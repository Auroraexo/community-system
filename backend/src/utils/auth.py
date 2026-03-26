from datetime import datetime, timedelta
from typing import Optional, Union, List
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from ..database import get_db
from ..models.user import User, Permission

# 加载环境变量
load_dotenv()

# OAuth2密码承载令牌 - 指向表单登录端点，用于Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login/form")

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 7天 = 60分钟 × 24小时 × 7天


import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    # 使用bcrypt验证密码哈希
    try:
        # 确保密码长度不超过72字节限制
        if len(plain_password) > 72:
            plain_password = plain_password[:72]
        # 检查密码是否已经是bcrypt格式
        if hashed_password.startswith('$2'):
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        else:
            # 如果验证失败，检查是否是旧系统的明文密码（临时兼容）
            return plain_password == hashed_password
    except Exception:
        # 如果验证失败，检查是否是旧系统的明文密码（临时兼容）
        return plain_password == hashed_password

def get_password_hash(password: str) -> str:
    """获取密码哈希值"""
    # 使用bcrypt生成密码哈希，确保密码长度不超过72字节限制
    if len(password) > 72:
        password = password[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def is_self_or_admin(current_user: User, target_user_id: int) -> bool:
    """检查当前用户是否为目标用户本人或管理员
    
    Args:
        current_user: 当前登录用户
        target_user_id: 目标用户ID
        
    Returns:
        bool: 如果是本人或管理员返回True，否则返回False
    """
    # 检查是否是本人
    if current_user.id == target_user_id:
        return True
    
    # 检查是否是管理员（拥有所有权限）
    admin_roles = ['管理员', 'admin']
    for role in current_user.roles:
        if role.name in admin_roles:
            return True
    
    return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """解码令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    
    return user


def check_user_permissions(current_user: User, required_permissions: Union[str, List[str]], target_user_id: int = None) -> bool:
    """检查用户权限，支持用户只能操作自己信息的控制
    
    Args:
        current_user: 当前登录用户
        required_permissions: 所需权限列表或单个权限
        target_user_id: 目标用户ID（可选，用于检查是否操作自己的信息）
        
    Returns:
        bool: 如果有权限返回True，否则返回False
    """
    # 管理员角色（"管理员"或"admin"）拥有所有权限
    if any(role.name in ['管理员', 'admin'] for role in current_user.roles):
        return True
    
    # 转换为列表
    if isinstance(required_permissions, str):
        required_permissions = [required_permissions]
    
    # 获取用户所有权限
    user_permissions = set()
    for role in current_user.roles:
        for permission in role.permissions:
            user_permissions.add(permission.name)
    
    # 检查是否有所需权限
    has_all_permissions = all(perm in user_permissions for perm in required_permissions)
    
    # 如果有权限，且操作的是用户相关资源，需要额外检查
    if has_all_permissions and target_user_id is not None:
        # 对于user相关操作，非管理员只能操作自己的信息
        if any(perm.startswith('user:') for perm in required_permissions):
            return current_user.id == target_user_id
    
    return has_all_permissions


def require_permissions(required_permissions: Union[str, List[str]], target_user_id: Optional[int] = None):
    """权限装饰器依赖，支持针对特定用户的权限控制
    
    Args:
        required_permissions: 所需权限列表或单个权限
        target_user_id: 目标用户ID（可选，用于检查是否操作自己的信息）
        
    Returns:
        权限检查装饰器
    """
    async def permission_checker(current_user: User = Depends(get_current_user)):
        # 管理员角色（"管理员"或"admin"）拥有所有权限，直接返回当前用户
        if any(role.name in ['管理员', 'admin'] for role in current_user.roles):
            return current_user
            
        if not check_user_permissions(current_user, required_permissions, target_user_id):
            # 根据不同的原因返回更具体的错误信息
            if target_user_id is not None and any(perm.startswith('user:') for perm in 
                                               (required_permissions if isinstance(required_permissions, list) else [required_permissions])):
                if not is_self_or_admin(current_user, target_user_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="没有权限操作其他用户的信息"
                    )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return permission_checker