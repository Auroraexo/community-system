from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from .utils.crypto import db_crypto

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 数据库配置 - 强制使用MySQL
DATABASE_URL_RAW = os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@localhost:3306/community_system")

# 处理可能加密的数据库连接密码
DATABASE_URL = db_crypto.process_connection_string(DATABASE_URL_RAW)

# 确保是MySQL连接
if "mysql" not in DATABASE_URL.lower():
    raise ValueError("错误: 数据库连接必须使用MySQL")

# 创建数据库引擎
def create_database_engine():
    """创建MySQL数据库引擎"""
    logger.info(f"尝试连接到MySQL数据库: {DATABASE_URL}")
    print("\n📊 数据库连接信息:")
    print(f"- 类型: MySQL")
    print(f"- 连接字符串: {DATABASE_URL}")
    print(f"- 正在尝试连接...")
    
    # 创建MySQL引擎
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
    
    # 测试连接
    with engine.connect() as conn:
        logger.info("✅ 成功连接到MySQL数据库")
        print("✅ MySQL连接成功!")
    
    print("\n🚀 数据库初始化完成 (当前使用: MySQL)")
    return engine

# 创建引擎
engine = create_database_engine()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """获取数据库会话的依赖项"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()