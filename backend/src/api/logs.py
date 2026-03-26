from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, Integer
import pandas as pd
from io import BytesIO

from ..database import get_db
from ..models.user import User
from ..models.log import OperationLog
from ..schemas.log import OperationLog as OperationLogSchema, LogQuery
from ..utils.auth import get_current_user, require_permissions
from ..utils.logger import log_operation

router = APIRouter()


@router.get("", response_model=dict)
async def get_operation_logs(
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    target_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    success: Optional[int] = None,
    ip_address: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """获取操作日志列表（带分页）"""
    # 构建查询
    query = db.query(OperationLog)
    
    # 应用过滤条件
    if username:
        # 通过用户名查找用户ID
        user = db.query(User).filter(User.username.contains(username)).first()
        if user:
            query = query.filter(OperationLog.user_id == user.id)
    elif user_id:
        query = query.filter(OperationLog.user_id == user_id)
    if action:
        query = query.filter(OperationLog.action.contains(action))
    if resource_type:
        query = query.filter(OperationLog.resource_type == resource_type)
    elif target_type:
        query = query.filter(OperationLog.resource_type == target_type)
    if start_time:
        query = query.filter(OperationLog.created_at >= start_time)
    if end_time:
        query = query.filter(OperationLog.created_at <= end_time)
    if success is not None:
        query = query.filter(OperationLog.success == success)
    if ip_address:
        query = query.filter(OperationLog.ip_address.contains(ip_address))
    
    # 计算总数
    total = query.count()
    
    # 分页
    skip = (page - 1) * page_size
    logs = query.order_by(OperationLog.created_at.desc()).offset(skip).limit(page_size).all()
    
    # 记录查询日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="view",
        resource_type="log",
        details={
            "user_id": user_id,
            "username": username,
            "action": action,
            "resource_type": resource_type or target_type,
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None,
            "success": success,
            "ip_address": ip_address,
            "page": page,
            "page_size": page_size
        },
        request=request,
        success=1
    )
    
    # 转换为Pydantic模式
    log_schemas = []
    for log in logs:
        # 处理details字段 - 如果是字符串则尝试解析为字典
        details_data = log.details
        if isinstance(details_data, str):
            try:
                import json
                details_data = json.loads(details_data)
            except json.JSONDecodeError:
                # 如果解析失败，保持原样或设置为空字典
                details_data = {}
        
        # 创建日志字典
        log_dict = {
            "id": log.id,
            "user_id": log.user_id,
            "username": log.user.username if log.user else None,
            "action": log.action,
            "resource_type": log.resource_type,
            "target_type": log.resource_type,  # 添加target_type字段
            "resource_id": log.resource_id,
            "target_id": log.resource_id,  # 添加target_id字段
            "details": details_data,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "success": log.success,
            "error_message": log.error_message,
            "created_at": log.created_at
        }
        
        # 转换为Pydantic模式
        log_schemas.append(OperationLogSchema.model_validate(log_dict))
    
    return {
        "items": log_schemas,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@router.get("/{log_id}", response_model=OperationLogSchema)
async def get_operation_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("log:read")),
    request: Request = None
):
    """获取单条操作日志"""
    log = db.query(OperationLog).filter(OperationLog.id == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日志不存在"
        )
    
    # 处理details字段 - 如果是字符串则尝试解析为字典
    details_data = log.details
    if isinstance(details_data, str):
        try:
            import json
            details_data = json.loads(details_data)
        except json.JSONDecodeError:
            # 如果解析失败，保持原样或设置为空字典
            details_data = {}
    
    # 创建日志字典
    log_dict = {
        "id": log.id,
        "user_id": log.user_id,
        "username": log.user.username if log.user else None,
        "action": log.action,
        "resource_type": log.resource_type,
        "target_type": log.resource_type,  # 添加target_type字段
        "resource_id": log.resource_id,
        "target_id": log.resource_id,  # 添加target_id字段
        "details": details_data,
        "ip_address": log.ip_address,
        "user_agent": log.user_agent,
        "success": log.success,
        "error_message": log.error_message,
        "created_at": log.created_at
    }
    
    return OperationLogSchema.model_validate(log_dict)


@router.get("/user/me", response_model=dict)
async def get_my_operation_logs(
    action: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    success: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """获取当前用户的操作日志（带分页）"""
    # 构建查询
    query = db.query(OperationLog).filter(OperationLog.user_id == current_user.id)
    
    # 应用过滤条件
    if action:
        query = query.filter(OperationLog.action.contains(action))
    if start_time:
        query = query.filter(OperationLog.created_at >= start_time)
    if end_time:
        query = query.filter(OperationLog.created_at <= end_time)
    if success is not None:
        query = query.filter(OperationLog.success == success)
    
    # 计算总数
    total = query.count()
    
    # 分页
    skip = (page - 1) * page_size
    logs = query.order_by(OperationLog.created_at.desc()).offset(skip).limit(page_size).all()
    
    # 转换为Pydantic模式
    log_schemas = []
    for log in logs:
        # 处理details字段 - 如果是字符串则尝试解析为字典
        details_data = log.details
        if isinstance(details_data, str):
            try:
                import json
                details_data = json.loads(details_data)
            except json.JSONDecodeError:
                # 如果解析失败，保持原样或设置为空字典
                details_data = {}
        
        # 创建日志字典
        log_dict = {
            "id": log.id,
            "user_id": log.user_id,
            "username": log.user.username if log.user else None,
            "action": log.action,
            "resource_type": log.resource_type,
            "target_type": log.resource_type,  # 添加target_type字段
            "resource_id": log.resource_id,
            "target_id": log.resource_id,  # 添加target_id字段
            "details": details_data,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "success": log.success,
            "error_message": log.error_message,
            "created_at": log.created_at
        }
        
        # 转换为Pydantic模式
        log_schemas.append(OperationLogSchema.model_validate(log_dict))
    
    return {
        "items": log_schemas,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }

@router.post("/batch-delete", status_code=status.HTTP_204_NO_CONTENT)
async def batch_delete_logs(
    log_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("log:delete")),
    request: Request = None
):
    """批量删除操作日志"""
    # 查询要删除的日志
    logs = db.query(OperationLog).filter(OperationLog.id.in_(log_ids)).all()
    
    if not logs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到要删除的日志"
        )
    
    # 删除日志
    for log in logs:
        db.delete(log)
    
    db.commit()
    
    # 记录删除日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="batch_delete",
        resource_type="log",
        details={"log_ids": log_ids, "count": len(logs)},
        request=request,
        success=1
    )
    
    return None

@router.delete("/cleanup")
async def cleanup_old_logs(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("log:delete")),
    request: Request = None
):
    """清理指定天数之前的旧日志"""
    # 计算截止日期
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # 查询并删除旧日志
    deleted_count = db.query(OperationLog).filter(
        OperationLog.created_at < cutoff_date
    ).delete()
    
    db.commit()
    
    # 记录清理日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="cleanup",
        resource_type="log",
        details={"days": days, "deleted_count": deleted_count},
        request=request,
        success=1
    )
    
    return {
        "message": f"已清理{days}天之前的{deleted_count}条日志",
        "deleted_count": deleted_count,
        "cutoff_date": cutoff_date
    }

@router.get("/export")
async def export_logs(
    username: Optional[str] = None,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    target_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    success: Optional[int] = None,
    limit: Optional[int] = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """导出操作日志"""
    # 构建查询
    query = db.query(OperationLog)
    
    # 应用过滤条件
    if username:
        # 通过用户名查找用户ID
        user = db.query(User).filter(User.username.contains(username)).first()
        if user:
            query = query.filter(OperationLog.user_id == user.id)
    elif user_id:
        query = query.filter(OperationLog.user_id == user_id)
    if action:
        query = query.filter(OperationLog.action.contains(action))
    if resource_type:
        query = query.filter(OperationLog.resource_type == resource_type)
    elif target_type:
        query = query.filter(OperationLog.resource_type == target_type)
    if start_time:
        query = query.filter(OperationLog.created_at >= start_time)
    if end_time:
        query = query.filter(OperationLog.created_at <= end_time)
    if success is not None:
        query = query.filter(OperationLog.success == success)
    
    # 限制导出数量
    logs = query.order_by(OperationLog.created_at.desc()).limit(limit).all()
    
    # 转换为DataFrame
    data = []
    for log in logs:
        # 尝试解析details字段（如果是字符串）
        details_str = log.details
        if isinstance(details_str, str):
            try:
                import json
                details = json.loads(details_str)
            except:
                details = {"raw": details_str}
        else:
            details = details_str or {}
        
        data.append({
            '操作时间': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            '用户ID': log.user_id,
            '操作类型': log.action,
            '资源类型': log.resource_type,
            '资源ID': log.resource_id,
            'IP地址': log.ip_address,
            '操作状态': '成功' if log.success == 1 else '失败',
            '详细信息': str(details)
        })
    
    df = pd.DataFrame(data)
    
    # 创建Excel文件
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='操作日志')
    
    output.seek(0)
    
    # 记录导出日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="export",
        resource_type="log",
        details={"count": len(logs)},
        request=request,
        success=1
    )
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=操作日志_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )

@router.get("/stats/summary")
async def get_log_stats_summary(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """获取日志统计摘要"""
    # 构建查询
    query = db.query(OperationLog)
    
    # 应用时间过滤
    if start_time:
        query = query.filter(OperationLog.created_at >= start_time)
    if end_time:
        query = query.filter(OperationLog.created_at <= end_time)
    
    # 统计总日志数
    total_logs = query.count()
    
    # 统计成功/失败次数
    success_count = query.filter(OperationLog.success == 1).count()
    failed_count = total_logs - success_count
    
    # 统计操作类型分布
    action_stats = db.query(
        OperationLog.action,
        func.count(OperationLog.id).label('count')
    ).filter(
        OperationLog.created_at >= (start_time or datetime.min),
        OperationLog.created_at <= (end_time or datetime.max)
    ).group_by(OperationLog.action).all()
    
    # 统计资源类型分布
    resource_stats = db.query(
        OperationLog.resource_type,
        func.count(OperationLog.id).label('count')
    ).filter(
        OperationLog.created_at >= (start_time or datetime.min),
        OperationLog.created_at <= (end_time or datetime.max)
    ).group_by(OperationLog.resource_type).all()
    
    # 统计活跃用户
    active_users = db.query(
        OperationLog.user_id,
        func.count(OperationLog.id).label('count')
    ).filter(
        OperationLog.created_at >= (start_time or datetime.min),
        OperationLog.created_at <= (end_time or datetime.max)
    ).group_by(OperationLog.user_id).order_by(func.count(OperationLog.id).desc()).limit(10).all()
    
    # 最近的失败记录
    recent_failures = query.filter(
        OperationLog.success == 0
    ).order_by(OperationLog.created_at.desc()).limit(10).all()
    
    result = {
        "total_logs": total_logs,
        "success_count": success_count,
        "failed_count": failed_count,
        "success_rate": round(success_count / total_logs * 100, 2) if total_logs > 0 else 0,
        "action_distribution": {item.action: item.count for item in action_stats},
        "resource_distribution": {item.resource_type: item.count for item in resource_stats},
        "active_users": [
            {"user_id": item.user_id, "count": item.count}
            for item in active_users
        ],
        "recent_failures": recent_failures[:5]  # 只返回最近5条失败记录
    }
    
    # 记录统计查询日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="view_stats",
        resource_type="log",
        details={"stats_type": "summary"},
        request=request,
        success=1
    )
    
    return result

@router.get("/stats/activity")
async def get_activity_stats(
    days: int = Query(7, ge=1, le=30),
    interval: str = Query("day", regex="^(day|hour)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """获取活动统计数据（按天/小时）"""
    # 计算开始时间
    start_date = datetime.now() - timedelta(days=days)
    
    # 构建查询
    if interval == "day":
        # 按天统计
        stats = db.query(
            func.date(OperationLog.created_at).label('date'),
            func.count(OperationLog.id).label('total'),
            func.sum(func.cast(OperationLog.success == 1, Integer)).label('success'),
            func.sum(func.cast(OperationLog.success == 0, Integer)).label('failed')
        ).filter(
            OperationLog.created_at >= start_date
        ).group_by(func.date(OperationLog.created_at)).all()
        
        # 格式化数据
        data = []
        for stat in stats:
            data.append({
                "date": stat.date.strftime('%Y-%m-%d'),
                "total": stat.total or 0,
                "success": stat.success or 0,
                "failed": stat.failed or 0
            })
    else:
        # 按小时统计
        stats = db.query(
            func.strftime('%Y-%m-%d %H:00', OperationLog.created_at).label('hour'),
            func.count(OperationLog.id).label('total'),
            func.sum(func.cast(OperationLog.success == 1, Integer)).label('success'),
            func.sum(func.cast(OperationLog.success == 0, Integer)).label('failed')
        ).filter(
            OperationLog.created_at >= start_date
        ).group_by(func.strftime('%Y-%m-%d %H:00', OperationLog.created_at)).all()
        
        # 格式化数据
        data = []
        for stat in stats:
            data.append({
                "hour": stat.hour,
                "total": stat.total or 0,
                "success": stat.success or 0,
                "failed": stat.failed or 0
            })
    
    # 记录统计查询日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="view_stats",
        resource_type="log",
        details={"stats_type": "activity", "days": days, "interval": interval},
        request=request,
        success=1
    )
    
    return {
        "days": days,
        "interval": interval,
        "data": data
    }