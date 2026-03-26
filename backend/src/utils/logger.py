import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request

from ..models.log import OperationLog


def log_operation(
    db: Session,
    user_id: Optional[int],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
    success: int = 1,
    error_message: Optional[str] = None
) -> None:
    """
    记录操作日志
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        action: 操作类型
        resource_type: 资源类型
        resource_id: 资源ID
        details: 操作详情
        request: FastAPI请求对象（用于获取IP和用户代理）
        success: 是否成功（1成功，0失败）
        error_message: 错误信息
    """
    # 获取IP地址和用户代理
    ip_address = None
    user_agent = None
    
    if request:
        # 尝试从X-Forwarded-For获取真实IP
        ip_address = request.headers.get("X-Forwarded-For")
        if not ip_address:
            # 否则使用客户端IP
            client_host = request.client.host if request.client else None
            ip_address = client_host
        
        # 获取用户代理
        user_agent = request.headers.get("User-Agent")
    
    # 将details转换为JSON字符串
    details_json = json.dumps(details, ensure_ascii=False) if details else None
    
    # 创建日志记录
    log_entry = OperationLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details_json,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        error_message=error_message
    )
    
    # 保存到数据库
    db.add(log_entry)
    db.commit()