import os
from pathlib import Path
from uuid import UUID
import uuid
import logging

from config import settings

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from database import SessionLocal
from models import Paper, ChatMessage, MessageSource, User

from services.pdf_service import extract_pages_from_pdf
from services.text_splitter import split_pages
from services.embedding_service import encode_texts
from services.vector_store import VectorStore
from services.rag_service import build_rag_prompt
from services.llm_service import generate_answer
from services.auth_service import hash_password, verify_password, create_access_token
from services.auth_dependency import get_current_user, get_owned_paper

app = FastAPI()

logger = logging.getLogger(__name__)

MAX_PDF_SIZE = settings.MAX_PDF_SIZE

UPLOAD_CHUNK_SIZE = 1024 * 1024  # 每次读取 1 MB

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = settings.UPLOAD_DIR
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

VECTOR_STORE_DIR = settings.VECTOR_STORE_DIR
VECTOR_STORE_DIR.mkdir(
    parents=True,
    exist_ok=True
)



# ============================================
# 1. 论文语义检索请求
# ============================================

class SearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=2000,
        description="检索问题，长度 1～2000 个字符"
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="返回的相关片段数量，范围 1～10"
    )


# ============================================
# 2. AI 论文问答请求
# ============================================

class AskRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
        description="向论文提出的问题"
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="用于构造 RAG 上下文的片段数量"
    )


# ============================================
# 3. 用户注册请求
# ============================================

class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9_]+$",
        description="3～50 位用户名，只允许字母、数字、下划线"
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        description="密码长度 8～128 个字符"
    )


# ============================================
# 4. 用户登录请求
# ============================================

class LoginRequest(BaseModel):
    username: str = Field(
        min_length=1,
        description="用户名"
    )

    password: str = Field(
        min_length=1,
        description="密码"
    )


@app.get("/")
def root():
    return {
        "message": "Welcome to PaperMind"
    }



@app.post("/papers/upload")
async def upload_paper(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    # =====================================
    # 1. 检查文件名
    # =====================================

    filename = file.filename or ""

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="只允许上传 PDF 文件"
        )

    # =====================================
    # 2. 创建本次上传使用的文件路径
    # =====================================

    paper_id = str(uuid.uuid4())

    file_path = UPLOAD_DIR / f"{paper_id}.pdf"

    index_path = (
        VECTOR_STORE_DIR / f"{paper_id}.index"
    )

    chunks_path = (
        VECTOR_STORE_DIR / f"{paper_id}_chunks.json"
    )

    created_paths = [
        file_path,
        index_path,
        chunks_path
    ]

    total_size = 0

    try:
        # =====================================
        # 3. 分块读取文件，限制最大 20 MB
        # =====================================

        with open(file_path, "wb") as output_file:

            while True:
                chunk = await file.read(
                    UPLOAD_CHUNK_SIZE
                )

                if not chunk:
                    break

                # 检查第一个数据块的 PDF 文件头
                if total_size == 0:

                    if not chunk.startswith(b"%PDF-"):
                        raise HTTPException(
                            status_code=400,
                            detail="文件内容不是有效的 PDF 格式"
                        )

                total_size += len(chunk)

                if total_size > MAX_PDF_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=("PDF 文件不能超过 ",f"{MAX_PDF_SIZE / (1024 * 1024):g}MB")
                    )

                output_file.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="上传的文件为空"
            )

        # =====================================
        # 4. 解析 PDF
        # =====================================

        try:
            pages = extract_pages_from_pdf(
                file_path
            )

        except Exception as error:
            logger.warning(
                "PDF 解析失败 paper_id=%s: %s",
                paper_id,
                error
            )

            raise HTTPException(
                status_code=422,
                detail="PDF 无法解析，文件可能损坏、加密或格式不受支持"
            ) from error

        if not pages:
            raise HTTPException(
                status_code=422,
                detail="PDF 未解析出任何页面"
            )

        # =====================================
        # 5. 文本分块
        # =====================================

        chunks = split_pages(pages)

        # 过滤空白文本块
        chunks = [
            chunk
            for chunk in chunks
            if chunk.get("text", "").strip()
        ]

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="PDF 没有可提取的文本，暂不支持纯扫描件"
            )

        chunk_texts = [
            chunk["text"]
            for chunk in chunks
        ]

        # =====================================
        # 6. 生成 Embedding
        # =====================================

        embeddings = encode_texts(
            chunk_texts
        )

        if (
            embeddings.ndim != 2
            or embeddings.shape[0] != len(chunks)
            or embeddings.shape[1] == 0
        ):
            raise RuntimeError(
                "Embedding 返回的向量维度不正确"
            )

        # =====================================
        # 7. 建立 FAISS 索引
        # =====================================

        dimension = embeddings.shape[1]

        vector_store = VectorStore(
            dimension
        )

        vector_store.add(
            embeddings,
            chunks
        )

        vector_store.save(
            str(index_path),
            str(chunks_path)
        )

        # =====================================
        # 8. 保存 MySQL 论文元数据
        # =====================================

        try:
            with SessionLocal() as db:

                paper = Paper(
                    id=paper_id,
                    user_id=current_user["id"],
                    filename=filename,
                    file_path=str(file_path),
                    index_path=str(index_path),
                    chunks_path=str(chunks_path)
                )

                db.add(paper)
                db.commit()

        except SQLAlchemyError as error:
            logger.exception(
                "MySQL 保存论文失败 paper_id=%s",
                paper_id
            )

            raise HTTPException(
                status_code=500,
                detail="论文索引已生成，但数据库保存失败"
            ) from error

        # =====================================
        # 9. 全部成功后返回
        # =====================================

        return {
            "message": "论文上传、索引建立及数据库保存成功",
            "paper_id": paper_id,
            "filename": filename,
            "chunk_count": len(chunks)
        }

    # =====================================
    # 10. 统一异常处理和文件清理
    # =====================================

    except Exception as error:

        # 无论在哪个处理阶段失败，
        # 都尝试删除本次创建的文件
        for path in created_paths:

            try:
                path.unlink(missing_ok=True)

            except OSError:
                logger.exception(
                    "清理上传文件失败：%s",
                    path
                )

        # 保留主动抛出的 HTTP 状态码
        if isinstance(error, HTTPException):
            raise

        # 未预料的异常记录在后端日志中
        logger.exception(
            "论文上传失败 paper_id=%s",
            paper_id
        )

        raise HTTPException(
            status_code=500,
            detail="论文处理失败，请检查服务器日志"
        ) from error

    finally:
        await file.close()


@app.get("/papers")
def list_papers(
    current_user: dict = Depends(get_current_user)
):
    with SessionLocal() as db:
        papers = db.scalars(
            select(Paper)
            .where(Paper.user_id == current_user["id"])
            .order_by(Paper.created_at.desc())
        ).all()

        return {
            "papers": [
                {
                    "id": paper.id,
                    "filename": paper.filename,
                    "created_at": paper.created_at.isoformat()
                }
                for paper in papers
            ]
        }

@app.delete("/papers/{paper_id}")
def delete_paper(
    paper_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    paper_id_str = str(paper_id)
    user_id = current_user["id"]

    # 1. 在同一个会话中检查所有权并删除记录
    try:
        with SessionLocal() as db:
            try:
                paper = db.scalar(
                    select(Paper).where(
                        Paper.id == paper_id_str,
                        Paper.user_id == user_id
                    )
                )

                if paper is None:
                    raise HTTPException(
                        status_code=404,
                        detail="论文不存在"
                    )

                # 使用 UUID 构造路径，不直接信任数据库路径
                paths = [
                    UPLOAD_DIR / f"{paper_id_str}.pdf",
                    VECTOR_STORE_DIR / f"{paper_id_str}.index",
                    VECTOR_STORE_DIR / f"{paper_id_str}_chunks.json"
                ]

                db.delete(paper)
                db.commit()

            except Exception:
                db.rollback()
                raise

    except SQLAlchemyError as error:
        logger.exception(
            "删除论文数据库记录失败 paper_id=%s",
            paper_id_str
        )

        raise HTTPException(
            status_code=500,
            detail="数据库删除失败，论文文件未进行清理"
        ) from error

    # 2. 数据库提交成功后再清理文件
    failed_files = []

    for path in paths:
        try:
            path.unlink(missing_ok=True)

        except OSError:
            logger.exception(
                "删除论文文件失败 paper_id=%s path=%s",
                paper_id_str,
                path
            )
            failed_files.append(str(path))

    # 3. 返回删除结果
    if failed_files:
        return {
            "message": "论文记录已删除，但部分文件清理失败",
            "paper_id": paper_id_str,
            "failed_files": failed_files
        }

    return {
        "message": "论文已成功删除",
        "paper_id": paper_id_str,
        "failed_files": []
    }

@app.post("/papers/{paper_id}/search")
def search_paper(
    paper_id: UUID,
    request: SearchRequest,
    current_user: dict = Depends(get_current_user)
):
    get_owned_paper(paper_id, current_user["id"])

    paper_id = str(paper_id)

    index_path = (
        VECTOR_STORE_DIR /
        f"{paper_id}.index"
    )

    chunks_path = (
        VECTOR_STORE_DIR /
        f"{paper_id}_chunks.json"
    )

    if not index_path.exists() or not chunks_path.exists():

        raise HTTPException(
            status_code=404,
            detail="论文索引不存在"
        )

    # 加载论文向量库
    vector_store = VectorStore.load(
        str(index_path),
        str(chunks_path)
    )

    # Query → Embedding
    query_embedding = encode_texts(
        [request.query]
    )[0]

    # FAISS Search
    results = vector_store.search(
        query_embedding,
        top_k=request.top_k
    )

    return {
        "paper_id": paper_id,
        "query": request.query,
        "results": results
    }


@app.post("/papers/{paper_id}/ask")
def ask_paper(paper_id: UUID, request: AskRequest, current_user: dict = Depends(get_current_user)):

    get_owned_paper(paper_id, current_user["id"])

    # 1. 构造索引路径
    paper_id_str = str(paper_id)

    index_path = (
        VECTOR_STORE_DIR / f"{paper_id_str}.index"
    )

    chunks_path = (
        VECTOR_STORE_DIR / f"{paper_id_str}_chunks.json"
    )

    # 2. 检查论文索引是否存在
    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        raise HTTPException(
            status_code=404,
            detail="论文不存在或尚未建立索引"
        )

    # 3. 加载向量数据库
    vector_store = VectorStore.load(
        index_path,
        chunks_path
    )

    # 4. 将问题转换为向量
    query_embedding = encode_texts([request.question])[0]

    # 5. FAISS 检索
    results = vector_store.search(
        query_embedding,
        top_k=request.top_k
    )

    if not results:
        raise HTTPException(
            status_code=422,
            detail="没有可用于回答的论文片段"
        )

    # 6. 构造 RAG Prompt
    prompt = build_rag_prompt(
        request.question,
        results
    )

    # 7. 调用 DeepSeek
    answer = generate_answer(prompt)

    if not answer.strip():
        raise HTTPException(
            status_code=502,
            detail="大模型未返回有效回答"
        )



    # 8. 保存聊天消息和引用来源
    try:
        with SessionLocal() as db:

            # 保存用户问题
            user_message = ChatMessage(
                paper_id=paper_id_str,
                role="user",
                content=request.question
            )

            # 保存 AI 回答
            assistant_message = ChatMessage(
                paper_id=paper_id_str,
                role="assistant",
                content=answer
            )

            db.add_all([
                user_message,
                assistant_message
            ])

            # 将消息写入当前事务，获取自增 ID
            db.flush()

            # 每个检索片段关联到 AI 回答
            for result in results:
                source = MessageSource(
                    message_id=assistant_message.id,
                    chunk_id=result["chunk_id"],
                    page=result["page"],
                    score=float(result["score"]),
                    text=result["text"]
                )

                db.add(source)

            # 统一提交三类数据
            db.commit()

    except SQLAlchemyError as error:
        print("保存聊天记录和引用来源失败：", error)

        raise HTTPException(
            status_code=500,
            detail="AI 回答已生成，但保存聊天记录或引用来源失败"
        )

    # 9. 组织检索来源
    sources = []

    for result in results:
        sources.append({
            "chunk_id": result["chunk_id"],
            "page": result["page"],
            "score": result["score"],
            "text": result["text"]
        })

    # 10. 返回结果
    return {
        "paper_id": paper_id_str,
        "question": request.question,
        "answer": answer,
        "sources": sources
    }

@app.get("/papers/{paper_id}/messages")
def get_paper_messages(
    paper_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    # =====================================
    # 1. 检查论文归属
    # =====================================

    get_owned_paper(
        paper_id,
        current_user["id"]
    )

    paper_id_str = str(paper_id)

    with SessionLocal() as db:

        # =====================================
        # 2. 一次查询所有聊天消息
        # =====================================

        messages = db.scalars(
            select(ChatMessage)
            .where(
                ChatMessage.paper_id == paper_id_str
            )
            .order_by(ChatMessage.id.asc())
        ).all()

        # 没有聊天记录时直接返回
        if not messages:
            return {
                "paper_id": paper_id_str,
                "messages": []
            }

        # =====================================
        # 3. 获取所有消息 ID
        # =====================================

        message_ids = [
            message.id
            for message in messages
        ]

        # =====================================
        # 4. 一次批量查询所有引用来源
        # =====================================

        all_sources = db.scalars(
            select(MessageSource)
            .where(
                MessageSource.message_id.in_(
                    message_ids
                )
            )
            .order_by(MessageSource.id.asc())
        ).all()

        # =====================================
        # 5. 按 message_id 对来源分组
        # =====================================

        source_map = {
            message_id: []
            for message_id in message_ids
        }

        for source in all_sources:

            source_map[source.message_id].append({
                "chunk_id": source.chunk_id,
                "page": source.page,
                "score": source.score,
                "text": source.text
            })

        # =====================================
        # 6. 组装聊天历史
        # =====================================

        message_list = []

        for message in messages:

            message_list.append({
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat(),

                "sources": source_map.get(
                    message.id,
                    []
                )
            })

        # =====================================
        # 7. 返回结果
        # =====================================

        return {
            "paper_id": paper_id_str,
            "messages": message_list
        }

@app.post("/auth/register", status_code=201)
def register(request: RegisterRequest):

    with SessionLocal() as db:

        existing_user = db.scalar(
            select(User).where(
                User.username == request.username
            )
        )

        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="用户名已存在"
            )

        user = User(
            username=request.username,
            password_hash=hash_password(
                request.password
            )
        )

        db.add(user)

        try:
            db.commit()
            db.refresh(user)

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=409,
                detail="用户名已存在"
            )

        return {
            "message": "注册成功",
            "user_id": user.id,
            "username": user.username
        }



@app.post("/auth/login")
def login(request: LoginRequest):

    with SessionLocal() as db:

        user = db.scalar(
            select(User).where(
                User.username == request.username
            )
        )

        if user is None or not verify_password(
            request.password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="用户名或密码错误"
            )

        access_token = create_access_token(user.id)

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

@app.get("/auth/me")
def get_my_profile(
    current_user: dict = Depends(get_current_user)
):
    return {
        "id": current_user["id"],
        "username": current_user["username"]
    }
