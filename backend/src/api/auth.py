from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models.user import User, Role
from ..schemas.user import UserCreate, User as UserSchema, Token, LoginRequest
from ..utils.auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from ..utils.logger import log_operation

router = APIRouter()


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db), request: Request = None):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        phone=user_data.phone,
        name=user_data.name,
        password_hash=hashed_password
    )
    
    # 为新用户分配默认角色（住户）
    default_role = db.query(Role).filter(Role.name == "住户").first()
    if default_role:
        db_user.roles.append(default_role)
    
    # 保存用户
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 记录注册日志
    log_operation(
        db=db,
        user_id=None,  # 注册时还没有用户ID
        action="register",
        resource_type="user",
        resource_id=str(db_user.id),
        details={"username": db_user.username, "email": db_user.email},
        request=request,
        success=1
    )
    
    return db_user


def _login_process(username: str, password: str, db: Session, request: Request):
    """登录处理的公共逻辑"""
    # 查找用户
    user = db.query(User).options(selectinload(User.roles).selectinload(Role.permissions)).filter(User.username == username).first()
    
    # 验证用户和密码
    if not user or not verify_password(password, user.password_hash):
        # 记录登录失败日志
        log_operation(
            db=db,
            user_id=None,
            action="login",
            resource_type="auth",
            details={"username": username},
            request=request,
            success=0,
            error_message="用户名或密码错误"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否激活
    if not user.is_active:
        # 记录登录失败日志
        log_operation(
            db=db,
            user_id=user.id,
            action="login",
            resource_type="auth",
            details={"username": username},
            request=request,
            success=0,
            error_message="用户已被禁用"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # 记录登录成功日志
    log_operation(
        db=db,
        user_id=user.id,
        action="login",
        resource_type="auth",
        details={"username": username},
        request=request,
        success=1
    )
    
    # 构建用户响应
    user_response = UserSchema.model_validate(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }


# JSON格式登录端点
@router.post("/login", response_model=Token)
def login_json(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
    request: Request = None
):
    """用户登录 - JSON格式"""
    return _login_process(login_data.username, login_data.password, db, request)


# OAuth2密码流格式登录端点（用于Swagger UI）
@router.post("/login/form", response_model=Token)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None
):
    """用户登录 - 表单格式（用于Swagger UI）"""
    return _login_process(form_data.username, form_data.password, db, request)


@router.post("/logout")
async def logout(db: Session = Depends(get_db), request: Request = None, current_user: User = Depends(get_current_user)):
    """用户登出"""
    # 记录登出日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="logout",
        resource_type="auth",
        details={"username": current_user.username},
        request=request,
        success=1
    )
    
    return {"message": "登出成功"}