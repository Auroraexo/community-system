import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class DatabaseCrypto:
    """数据库连接加密工具类"""
    
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self):
        """获取或创建加密密钥"""
        # 从环境变量获取密钥，如果没有则生成新的
        key_str = os.getenv("DB_ENCRYPTION_KEY")
        if key_str:
            return key_str.encode()
        else:
            # 生成新的密钥
            key = Fernet.generate_key()
            logger.warning("⚠️  新生成数据库加密密钥，请设置 DB_ENCRYPTION_KEY 环境变量")
            logger.warning(f"🔑 密钥: {key.decode()}")
            return key
    
    def encrypt_password(self, password: str) -> str:
        """加密数据库密码"""
        encrypted = self.cipher.encrypt(password.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """解密数据库密码"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"解密失败: {e}")
            raise ValueError("数据库密码解密失败")
    
    def process_connection_string(self, connection_string: str) -> str:
        """处理连接字符串，解密其中的密码"""
        import re
        
        # 检查是否已经是明文密码格式（包含实际密码）
        if "://" in connection_string and "@" in connection_string:
            # 提取密码部分
            pattern = r"(://[^:]+:)([^@]+)(@)"
            match = re.search(pattern, connection_string)
            
            if match:
                password_part = match.group(2)
                
                # 检查密码是否像被加密的（base64编码且包含特定字符）
                try:
                    # 尝试解密
                    decrypted_password = self.decrypt_password(password_part)
                    # 替换为解密后的密码
                    new_connection_string = re.sub(
                        pattern, 
                        f"{match.group(1)}{decrypted_password}{match.group(3)}", 
                        connection_string
                    )
                    return new_connection_string
                except:
                    # 如果解密失败，假设是明文密码
                    logger.info("检测到明文数据库密码，建议加密处理")
                    return connection_string
        
        return connection_string

# 创建全局实例
db_crypto = DatabaseCrypto()