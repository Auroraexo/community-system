from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class OperationLog(Base):
    __tablename__ = "operation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    action = Column(String(100), nullable=False)  # 操作类型：login, create, update, delete, view等
    resource_type = Column(String(100), nullable=True)  # 资源类型：user, device, role等
    resource_id = Column(String(100), nullable=True)  # 资源ID
    details = Column(Text, nullable=True)  # 操作详情，JSON格式存储
    ip_address = Column(String(50), nullable=True)  # 客户端IP地址
    user_agent = Column(String(255), nullable=True)  # 客户端信息
    success = Column(Integer, default=1)  # 1表示成功，0表示失败
    error_message = Column(Text, nullable=True)  # 错误信息
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User")  # 移除back_populates避免循环引用