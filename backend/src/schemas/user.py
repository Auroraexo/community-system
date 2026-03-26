from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    phone: Optional[str] = None
    name: Optional[str] = None


class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role_name: str = Field(default="住户", description="用户角色")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)
    role_name: Optional[str] = None


class UserInDBBase(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class User(UserInDBBase):
    roles: List['Role'] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserInDBBase):
    password_hash: str


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    permissions: List['Permission'] = []


class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None


class Permission(PermissionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# 前向引用更新
User.model_rebuild()
Role.model_rebuild()