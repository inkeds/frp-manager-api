from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from urllib.parse import urlparse

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/frp_manager.db")

# 根据数据库类型配置连接参数
parsed_url = urlparse(DATABASE_URL)
if parsed_url.scheme == "sqlite":
    connect_args = {"check_same_thread": False}
    pool_size = None
    max_overflow = None
elif parsed_url.scheme in ["mysql+pymysql", "postgresql"]:
    connect_args = {}
    pool_size = 5
    max_overflow = 10
else:
    raise ValueError(f"Unsupported database type: {parsed_url.scheme}")

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_size=pool_size,
    max_overflow=max_overflow,
    pool_pre_ping=True,  # 自动检测断开的连接
    pool_recycle=3600,   # 每小时回收连接
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
