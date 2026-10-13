# PaperMind — AI 文献智能助手

基于 **FastAPI + Vue 3 + FAISS + DeepSeek** 构建的 AI 科研文献助手，支持 PDF 论文管理、语义检索、检索增强生成（RAG）问答和多用户数据隔离。

PaperMind 旨在帮助科研人员和学生更高效地阅读论文，通过自然语言提问快速理解论文内容，并查看回答所依据的原文片段。

## 核心功能

- **PDF 论文上传与解析**：上传 PDF，自动提取文本并进行分块。
- **语义向量检索**：利用 Sentence Transformers 生成文本向量，使用 FAISS 检索相关内容。
- **RAG 智能问答**：将论文检索结果作为上下文，调用 DeepSeek 生成回答。
- **引用来源展示**：展示与 AI 回答相关的论文原文片段、页码及检索分数。
- **多用户管理**：支持注册、登录、JWT 认证和论文访问权限隔离。
- **数据持久化**：使用 MySQL 保存用户、论文元数据、聊天记录和引用信息。
- **异常处理**：支持上传文件大小校验、API 错误处理、文件清理和前端请求状态隔离。
- **自动化测试**：使用 pytest 验证认证、权限、文件上传和大模型异常处理。

## 技术栈

| 模块 | 使用技术 |
|---|---|
| 前端 | Vue 3、Vite、Axios |
| 后端 | Python、FastAPI |
| 数据库 | MySQL、SQLAlchemy |
| PDF 解析 | PyMuPDF |
| 文本向量化 | Sentence Transformers |
| 向量检索 | FAISS |
| 大模型 | DeepSeek API |
| 身份认证 | JWT、Argon2 |
| 自动化测试 | pytest、HTTPX |

## 系统工作流程

```text
用户上传 PDF
      |
      v
PyMuPDF 提取论文文本
      |
      v
文本清理与分块
      |
      v
Sentence Transformers 生成 Embedding
      |
      v
FAISS 构建并保存向量索引
      |
      v
用户输入自然语言问题
      |
      v
向量相似度检索相关论文片段
      |
      v
构建 RAG Prompt
      |
      v
调用 DeepSeek API
      |
      v
返回 AI 回答与引用来源
```

## 项目结构

```text
PaperMind/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── auth_dependency.py
│   │   ├── pdf_service.py
│   │   ├── text_splitter.py
│   │   ├── embedding_service.py
│   │   ├── vector_store.py
│   │   ├── retrieval_service.py
│   │   ├── rag_service.py
│   │   └── llm_service.py
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── components/
│   │   │   ├── LoginForm.vue
│   │   │   ├── RegisterForm.vue
│   │   │   ├── PaperSidebar.vue
│   │   │   └── ChatPanel.vue
│   │   ├── services/api.js
│   │   └── utils/apiError.js
│   └── package.json
├── .gitignore
└── README.md
```

## 本地运行

### 1. 环境要求

- Python 3.11
- Node.js 和 npm
- MySQL 8.x
- 可用的 DeepSeek API Key

首次使用文本向量化模型时，可能需要从 Hugging Face 下载模型文件。

### 2. 获取项目

```bash
git clone <YOUR_REPOSITORY_URL>
cd PaperMind
```

请将 `<YOUR_REPOSITORY_URL>` 替换为实际 GitHub 仓库地址。

### 3. 安装后端依赖

```bash
cd backend
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

然后安装依赖：

```bash
python -m pip install -r requirements.txt
```

PyTorch 的 CPU/CUDA 版本可根据实际硬件环境单独配置。

### 4. 配置环境变量

参考 `backend/.env.example` 设置数据库连接、JWT 密钥和 DeepSeek API Key。

主要配置项：

```dotenv
DB_USER=root
DB_PASSWORD=your_database_password
DB_NAME=papermind

JWT_SECRET_KEY=your_random_secret_key
JWT_EXPIRE_MINUTES=120

DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=your_available_model
```

请使用实际有效的模型名称和独立生成的随机 JWT 密钥。

**不要将包含真实凭据的 `.env` 上传到 GitHub。**

启动前需要在 MySQL 中创建对应数据库并初始化数据库表结构。当前项目使用 SQLAlchemy ORM，数据库迁移管理将后续引入 Alembic。

### 5. 启动后端

在 `backend` 目录执行：

```bash
uvicorn main:app --reload
```

访问：

- API 地址：`http://127.0.0.1:8000`
- Swagger API 文档：`http://127.0.0.1:8000/docs`

### 6. 启动前端

打开另一个终端：

```bash
cd frontend
npm install
npm run dev
```

使用终端输出的本地地址访问 PaperMind。

## 自动化测试

后端测试涵盖：

- 用户注册与登录
- JWT 身份认证
- 跨用户论文权限隔离
- 数据库级联删除
- PDF 上传异常处理及文件清理
- 上传成功和数据库失败回滚
- DeepSeek API 超时、限流和异常响应
- 请求参数校验

当前测试套件共 **26 项测试**，已在本地开发环境中通过。

```bash
cd backend
python -m pytest -q
```

数据库集成测试需要独立的测试数据库 `papermind_pytest_db`、测试账号 `papermind_tester`，以及 `PAPERMIND_TEST_DB_PASSWORD` 环境变量。

请勿使用正式数据库运行集成测试。

## 当前开发状态

目前已实现 PaperMind 的主要端到端功能，包括 PDF 上传、向量检索、RAG 问答、用户管理以及前后端交互。

后续计划：

- [ ] 统一后端配置管理
- [ ] 完善应用日志
- [ ] 引入 Alembic 数据库迁移
- [ ] 增加前端自动化测试
- [ ] 整理项目截图与部署文档
- [ ] Docker 容器化部署
- [ ] Redis 缓存优化

## 项目说明

PaperMind 是一个持续迭代中的学习和工程实践项目，重点在于实现完整的 AI 应用开发流程，包括文档处理、向量检索、大模型集成、API 服务、权限管理及自动化测试。

当前以本地开发和测试为主，尚未提供公开在线服务。
