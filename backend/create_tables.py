from database import Base, engine
from models import Paper, ChatMessage, MessageSource, User

Base.metadata.create_all(bind=engine)

print("数据库表创建完成！")