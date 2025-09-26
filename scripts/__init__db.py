# python
# 文件：scripts/init_db.py
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

database_url="mysql+pymysql://root:123456@127.0.0.1:3306/rag_agent"
from src.api.db import Base
import src.api.models  # 确保模型被导入到 Base.metadata

def main() -> None:
    url = make_url(database_url)
    db_name = url.database

    # 连接到不带数据库名的服务器
    server_url = url.set(database=None)
    server_engine = create_engine(server_url, isolation_level="AUTOCOMMIT")

    # 创建数据库（如不存在）
    with server_engine.connect() as conn:
        conn.execute(text(
            f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
            "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        ))

    # 创建所有表
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    print(f"Database `{db_name}` is ready.")

if __name__ == "__main__":
    main()