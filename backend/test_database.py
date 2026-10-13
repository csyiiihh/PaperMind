
from sqlalchemy import text

from database import engine


with engine.connect() as connection:

    result = connection.execute(
        text("SELECT DATABASE(), VERSION()")
    )

    database_name, mysql_version = result.fetchone()

    print("数据库连接成功！")
    print("当前数据库：", database_name)
    print("MySQL 版本：", mysql_version)
