from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class OperationLogBase(BaseModel):
    action: str = Field(..., min_length=1, max_length=100)
    resource_type: Optional[str] = Field(None, max_length=100)
    resource_id: Optional[str] = Field(None, max_length=100)
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: int = 1
    error_message: Optional[str] = None


class OperationLogCreate(OperationLogBase):
    user_id: Optional[int] = None


class OperationLog(OperationLogBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None  # 添加用户名字段
    target_type: Optional[str] = None  # 添加目标类型字段（与resource_type相同）
    target_id: Optional[str] = None  # 添加目标ID字段（与resource_id相同）
    created_at: datetime


class LogQuery(BaseModel):
    user_id: Optional[int] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    success: Optional[int] = None
    page: int = 1
    page_size: int = 20