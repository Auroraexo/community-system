#!/usr/bin/env python3
"""
数据库密码加密工具
用于加密数据库连接密码
"""

import sys
import os
import logging
from pathlib import Path

# 添加后端目录到Python路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from src.utils.crypto import db_crypto

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def encrypt_db_password():
    """加密数据库密码"""
    print("🔐 数据库密码加密工具")
    print("=" * 50)
    
    # 获取当前数据库连接信息
    current_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@localhost:3306/community_system")
    print(f"当前连接字符串: {current_url}")
    
    # 提取密码部分
    import re
    pattern = r"(://[^:]+:)([^@]+)(@)"
    match = re.search(pattern, current_url)
    
    if not match:
        print("❌ 无法解析数据库连接字符串")
        return
    
    password = match.group(2)
    print(f"检测到密码: {password}")
    
    # 加密密码
    try:
        encrypted_password = db_crypto.encrypt_password(password)
        print(f"加密后的密码: {encrypted_password}")
        
        # 生成新的连接字符串
        new_url = re.sub(pattern, f"{match.group(1)}{encrypted_password}{match.group(3)}", current_url)
        print(f"新的连接字符串: {new_url}")
        
        print("\n✅ 加密完成！")
        print("请执行以下步骤：")
        print("1. 备份您的 .env 文件")
        print("2. 将 DATABASE_URL 更新为上面的新连接字符串")
        print("3. 设置环境变量 DB_ENCRYPTION_KEY 为提供的密钥")
        print("\n🔑 重要：请安全保存加密密钥！")
        
    except Exception as e:
        print(f"❌ 加密失败: {e}")

if __name__ == "__main__":
    encrypt_db_password()