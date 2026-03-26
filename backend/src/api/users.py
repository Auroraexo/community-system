from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User, Role
from ..schemas.user import User as UserSchema, UserUpdate, UserCreate
from ..utils.auth import get_current_user, require_permissions, get_password_hash, check_user_permissions, verify_password
from ..utils.logger import log_operation

router = APIRouter()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("user:create")),
    request: Request = None
):
    """创建新用户（需要权限）"""
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
        password_hash=hashed_password,
        is_active=True
    )
    
    # 为新用户分配角色
    if user_data.role_name:
        role = db.query(Role).filter(Role.name == user_data.role_name).first()
        if role:
            db_user.roles.append(role)
    else:
        # 默认分配住户角色
        default_role = db.query(Role).filter(Role.name == "住户").first()
        if default_role:
            db_user.roles.append(default_role)
    
    # 保存用户
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 记录创建日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="create",
        resource_type="user",
        resource_id=str(db_user.id),
        details={"username": db_user.username, "email": db_user.email},
        request=request,
        success=1
    )
    
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "phone": db_user.phone,
        "name": db_user.name,
        "is_active": db_user.is_active,
        "created_at": db_user.created_at,
        "updated_at": db_user.updated_at,
        "roles": [{"id": role.id, "name": role.name, "description": role.description} for role in db_user.roles]
    }


@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone,
        "name": current_user.name,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "roles": [{"id": role.id, "name": role.name, "description": role.description} for role in current_user.roles]
    }


@router.get("/", response_model=dict)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    username: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("user:read")),
    request: Request = None
):
    """获取用户列表（需要权限）"""
    query = db.query(User).filter(User.is_deleted == False)
    
    # 按用户名筛选
    if username:
        query = query.filter(User.username.contains(username))
    
    # 按角色筛选
    if role:
        query = query.join(User.roles).filter(Role.name == role)
    
    # 计算总数
    total = query.count()
    
    # 分页
    skip = (page - 1) * page_size
    users = query.offset(skip).limit(page_size).all()
    
    # 序列化用户数据
    user_schemas = []
    for user in users:
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "roles": [{"id": role.id, "name": role.name, "description": role.description} for role in user.roles]
        }
        user_schemas.append(user_data)
    
    return {"total": total, "items": user_schemas}


@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    # 额外检查权限：普通用户只能查看自己的信息
    if not check_user_permissions(current_user, "user:read", target_user_id=user_id):
        if not any(role.name in ['管理员', 'admin'] for role in current_user.roles) and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限查看其他用户的信息"
            )
    """获取单个用户信息"""
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查权限：只能查看自己的信息，或者有user:read权限
    if user_id != current_user.id:
        if not check_user_permissions(current_user, "user:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限查看其他用户信息"
            )
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "name": user.name,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "roles": [{"id": role.id, "name": role.name, "description": role.description} for role in user.roles]
    }


@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """更新用户信息"""
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查权限：只能更新自己的信息，或者有user:update权限
    if user_id != current_user.id:
        if not check_user_permissions(current_user, "user:update"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限更新其他用户信息"
            )
    
    # 更新用户信息
    update_data = user_update.model_dump(exclude_unset=True)
    
    # 如果有密码更新，需要加密
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    # 记录更新的字段和值（不包含密码）
    log_details = update_data.copy()
    if "password_hash" in log_details:
        log_details["password_hash"] = "[已更新]"
    
    db.commit()
    db.refresh(user)
    
    # 记录更新日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="update",
        resource_type="user",
        resource_id=str(user_id),
        details=log_details,
        request=request,
        success=1
    )
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "name": user.name,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "roles": [{"id": role.id, "name": role.name, "description": role.description} for role in user.roles]
    }


@router.post("/{user_id}/change-password", response_model=dict)
async def change_user_password(
    user_id: int,
    password_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """修改用户密码"""
    # 检查权限：只能修改自己的密码，或者有user:update权限
    if user_id != current_user.id:
        if not check_user_permissions(current_user, "user:update"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限修改其他用户密码"
            )
    
    # 获取用户
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 获取密码数据
    old_password = password_data.get("old_password")
    new_password = password_data.get("new_password")
    
    # 验证旧密码
    if not verify_password(old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码不正确"
        )
    
    # 更新密码
    user.password_hash = get_password_hash(new_password)
    db.commit()
    
    # 记录修改密码日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="change_password",
        resource_type="user",
        resource_id=str(user_id),
        details={"username": user.username},
        request=request,
        success=1
    )
    
    return {"message": "密码修改成功"}


@router.post("/{user_id}/reset-password", response_model=dict)
async def reset_user_password(
    user_id: int,
    password_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("user:update")),
    request: Request = None
):
    """重置用户密码（管理员功能）"""
    # 获取用户
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 获取新密码
    new_password = password_data.get("new_password")
    if not new_password or len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度不能少于6位"
        )
    
    # 更新密码
    user.password_hash = get_password_hash(new_password)
    db.commit()
    
    # 记录重置密码日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="reset_password",
        resource_type="user",
        resource_id=str(user_id),
        details={"username": user.username, "reset_by": current_user.username},
        request=request,
        success=1
    )
    
    return {"message": "密码重置成功"}


@router.put("/{user_id}/status", response_model=dict)
async def update_user_status(
    user_id: int,
    status_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("user:update")),
    request: Request = None
):
    """更新用户状态"""
    # 不允许用户修改自己的状态
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的状态"
        )
    
    # 获取用户
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 获取新状态
    is_active = status_data.get("is_active")
    if is_active is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须提供状态值"
        )
    
    # 更新状态
    user.is_active = is_active
    db.commit()
    
    # 记录更新状态日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="update_status",
        resource_type="user",
        resource_id=str(user_id),
        details={"username": user.username, "is_active": is_active, "updated_by": current_user.username},
        request=request,
        success=1
    )
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "name": user.name,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "roles": [{"id": role.id, "name": role.name, "description": role.description} for role in user.roles]
    }


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("user:delete")),
    request: Request = None
):
    # 不允许用户删除自己
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号"
        )
    """删除用户（软删除）"""
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 软删除
    user.is_deleted = True
    db.commit()
    
    # 记录删除日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="delete",
        resource_type="user",
        resource_id=str(user_id),
        details={"username": user.username},
        request=request,
        success=1
    )
    
    return None