from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

def decode_token(token: str) -> dict:
    """解码令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"JWT Error: {e}")
        return None

# 测试token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2MjMxOTY3M30.jnxp0MrMIeqx3wlvAtC58cSFZVo3FUaDTM-43F953K0"
print(f"Token: {token}")
print(f"SECRET_KEY: {SECRET_KEY}")

payload = decode_token(token)
print(f"Payload: {payload}")

if payload:
    username = payload.get("sub")
    print(f"Username: {username}")
    
    # 检查过期时间
    exp = payload.get("exp")
    if exp:
        exp_datetime = datetime.fromtimestamp(exp)
        now = datetime.utcnow()
        print(f"Expiration time: {exp_datetime}")
        print(f"Current time: {now}")
        print(f"Token is expired: {exp_datetime < now}")
else:
    print("Failed to decode token")