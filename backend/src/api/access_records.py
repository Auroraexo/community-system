from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, Integer
import pandas as pd
from io import BytesIO

from ..database import get_db
from ..models.user import User
from ..models.device import AccessRecord, Device
from ..schemas.device import AccessRecord as AccessRecordSchema
from ..utils.auth import get_current_user, require_permissions
from ..utils.logger import log_operation

router = APIRouter()


@router.get("", response_model=dict)
async def get_access_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    device_id: Optional[int] = None,
    user_id: Optional[int] = None,
    card_id: Optional[str] = None,
    access_result: Optional[bool] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """获取门禁记录列表（分页）"""
    # 构建查询
    query = db.query(AccessRecord).options(joinedload(AccessRecord.device))
    
    # 应用过滤条件
    if device_id:
        query = query.filter(AccessRecord.device_id == device_id)
    if user_id:
        query = query.filter(AccessRecord.user_id == user_id)
    if card_id:
        query = query.filter(AccessRecord.card_id.like(f"%{card_id}%"))
    if access_result is not None:
        query = query.filter(AccessRecord.access_result == access_result)
    if start_time:
        query = query.filter(AccessRecord.access_time >= start_time)
    if end_time:
        query = query.filter(AccessRecord.access_time <= end_time)
    
    # 计算总数
    total = query.count()
    
    # 分页
    skip = (page - 1) * page_size
    records = query.order_by(AccessRecord.access_time.desc()).offset(skip).limit(page_size).all()
    
    # 记录查询日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="view",
        resource_type="access_record",
        details={
            "page": page,
            "page_size": page_size,
            "device_id": device_id,
            "user_id": user_id,
            "access_result": access_result,
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None
        },
        request=request,
        success=1
    )
    
    return {
        "items": [AccessRecordSchema.model_validate(record) for record in records],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@router.get("/{record_id}", response_model=AccessRecordSchema)
async def get_access_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("access:read")),
    request: Request = None
):
    """获取单条门禁记录详情"""
    record = db.query(AccessRecord).options(joinedload(AccessRecord.device)).filter(
        AccessRecord.id == record_id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="门禁记录不存在"
        )
    
    # 记录查询日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="view",
        resource_type="access_record",
        resource_id=str(record_id),
        details={"record_id": record_id},
        request=request,
        success=1
    )
    
    return AccessRecordSchema.model_validate(record)


@router.get("/export")
async def export_access_records(
    user_id: Optional[int] = None,
    device_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    access_result: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10000, ge=1, le=10000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """导出门禁记录"""
    # 构建查询
    query = db.query(AccessRecord).options(joinedload(AccessRecord.device))
    
    # 应用过滤条件
    if device_id:
        query = query.filter(AccessRecord.device_id == device_id)
    if user_id:
        query = query.filter(AccessRecord.user_id == user_id)
    if access_result is not None:
        query = query.filter(AccessRecord.access_result == access_result)
    if start_time:
        query = query.filter(AccessRecord.access_time >= start_time)
    if end_time:
        query = query.filter(AccessRecord.access_time <= end_time)
    
    # 限制导出数量
    records = query.order_by(AccessRecord.access_time.desc()).offset(skip).limit(limit).all()
    
    # 转换为DataFrame
    data = []
    for record in records:
        data.append({
            '记录ID': record.id,
            '通行时间': record.access_time.strftime('%Y-%m-%d %H:%M:%S'),
            '设备编号': record.device.device_code if record.device else '-',
            '设备名称': record.device.device_name if (record.device and record.device.device_name) else '-',
            '设备位置': record.device.location if (record.device and record.device.location) else '-',
            '用户ID': record.user_id or '',
            '卡号': record.card_id or '',
            '通行结果': '成功' if record.access_result else '失败',
            '失败原因': record.reason or ''
        })
    
    df = pd.DataFrame(data)
    
    # 创建Excel文件
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='门禁记录')
    
    output.seek(0)
    
    # 记录导出日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="export",
        resource_type="access_record",
        details={"count": len(records)},
        request=request,
        success=1
    )
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=门禁记录_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )


@router.get("/stats/summary")
async def get_access_stats_summary(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("access_record:read")),
    request: Request = None
):
    """获取门禁统计摘要"""
    # 设置默认时间范围（最近7天）
    if not end_time:
        end_time = datetime.now()
    if not start_time:
        start_time = end_time - timedelta(days=7)
    
    # 构建查询
    query = db.query(AccessRecord).filter(
        AccessRecord.access_time >= start_time,
        AccessRecord.access_time <= end_time
    )
    
    # 统计总记录数
    total_records = query.count()
    
    # 统计成功/失败次数
    success_count = query.filter(AccessRecord.access_result == True).count()
    failed_count = total_records - success_count
    
    # 统计设备分布
    device_stats = db.query(
        Device.device_name,
        Device.location,
        func.count(AccessRecord.id).label('total'),
        func.sum(func.cast(AccessRecord.access_result == True, Integer)).label('success'),
            func.sum(func.cast(AccessRecord.access_result == False, Integer)).label('failed')
    ).join(
        AccessRecord, AccessRecord.device_id == Device.id
    ).filter(
        AccessRecord.access_time >= start_time,
        AccessRecord.access_time <= end_time
    ).group_by(Device.id).order_by(func.count(AccessRecord.id).desc()).limit(10).all()
    
    # 统计每日通行量
    daily_stats = db.query(
        func.date(AccessRecord.access_time).label('date'),
        func.count(AccessRecord.id).label('total'),
        func.sum(func.cast(AccessRecord.access_result == True, Integer)).label('success')
    ).filter(
        AccessRecord.access_time >= start_time,
        AccessRecord.access_time <= end_time
    ).group_by(func.date(AccessRecord.access_time)).order_by(func.date(AccessRecord.access_time)).all()
    
    # 统计失败原因分布
    failure_reasons = db.query(
        AccessRecord.reason,
        func.count(AccessRecord.id).label('count')
    ).filter(
        AccessRecord.access_time >= start_time,
        AccessRecord.access_time <= end_time,
        AccessRecord.access_result == False,
        AccessRecord.reason.isnot(None)
    ).group_by(AccessRecord.reason).order_by(func.count(AccessRecord.id).desc()).all()
    
    result = {
        "time_range": {
            "start_time": start_time,
            "end_time": end_time
        },
        "total_records": total_records,
        "success_count": success_count,
        "failed_count": failed_count,
        "success_rate": round(success_count / total_records * 100, 2) if total_records > 0 else 0,
        "device_stats": [
            {
                "device_name": item.device_name,
                "location": item.location,
                "total": item.total or 0,
                "success": item.success or 0,
                "failed": item.failed or 0
            }
            for item in device_stats
        ],
        "daily_stats": [
            {
                "date": item.date.strftime('%Y-%m-%d'),
                "total": item.total or 0,
                "success": item.success or 0
            }
            for item in daily_stats
        ],
        "failure_reasons": [
            {
                "reason": item.reason or "未知",
                "count": item.count
            }
            for item in failure_reasons
        ]
    }
    
    # 记录统计查询日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="view_stats",
        resource_type="access_record",
        details={"stats_type": "summary"},
        request=request,
        success=1
    )
    
    return result


@router.get("/stats/device/{device_id}")
async def get_device_access_stats(
    device_id: int,
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """获取单个设备的门禁统计"""
    # 检查设备是否存在
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 计算时间范围
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    # 查询设备的门禁记录统计
    stats = db.query(
        func.date(AccessRecord.access_time).label('date'),
        func.count(AccessRecord.id).label('total'),
        func.sum(func.cast(AccessRecord.access_result == True, Integer)).label('success'),
            func.sum(func.cast(AccessRecord.access_result == False, Integer)).label('failed')
    ).filter(
        AccessRecord.device_id == device_id,
        AccessRecord.access_time >= start_time,
        AccessRecord.access_time <= end_time
    ).group_by(func.date(AccessRecord.access_time)).order_by(func.date(AccessRecord.access_time)).all()
    
    # 查询最活跃的用户/卡号
    top_accessors = db.query(
        AccessRecord.user_id,
        AccessRecord.card_id,
        func.count(AccessRecord.id).label('count')
    ).filter(
        AccessRecord.device_id == device_id,
        AccessRecord.access_time >= start_time,
        AccessRecord.access_time <= end_time,
        AccessRecord.access_result == True
    ).group_by(AccessRecord.user_id, AccessRecord.card_id).order_by(
        func.count(AccessRecord.id).desc()
    ).limit(10).all()
    
    result = {
        "device": {
            "id": device.id,
            "name": device.device_name,
            "location": device.location,
            "device_code": device.device_code
        },
        "time_range": {
            "start_time": start_time,
            "end_time": end_time,
            "days": days
        },
        "daily_stats": [
            {
                "date": item.date.strftime('%Y-%m-%d'),
                "total": item.total or 0,
                "success": item.success or 0,
                "failed": item.failed or 0
            }
            for item in stats
        ],
        "top_accessors": [
            {
                "user_id": item.user_id,
                "card_id": item.card_id,
                "count": item.count
            }
            for item in top_accessors
        ]
    }
    
    # 记录统计查询日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="view_stats",
        resource_type="access_record",
        resource_id=str(device_id),
        details={"device_id": device_id, "days": days},
        request=request,
        success=1
    )
    
    return result


@router.post("/batch-delete", status_code=status.HTTP_204_NO_CONTENT)
async def batch_delete_access_records(
    record_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("access:delete")),
    request: Request = None
):
    """批量删除门禁记录"""
    # 查询要删除的记录
    records = db.query(AccessRecord).filter(AccessRecord.id.in_(record_ids)).all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到要删除的门禁记录"
        )
    
    # 删除记录
    for record in records:
        db.delete(record)
    
    db.commit()
    
    # 记录删除日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="batch_delete",
        resource_type="access_record",
        details={"record_ids": record_ids, "count": len(records)},
        request=request,
        success=1
    )
    
    return None


@router.delete("/cleanup")
async def cleanup_old_access_records(
    days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("access:delete")),
    request: Request = None
):
    """清理指定天数之前的旧门禁记录"""
    # 计算截止日期
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # 查询并删除旧记录
    deleted_count = db.query(AccessRecord).filter(
        AccessRecord.access_time < cutoff_date
    ).delete()
    
    db.commit()
    
    # 记录清理日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="cleanup",
        resource_type="access_record",
        details={"days": days, "deleted_count": deleted_count},
        request=request,
        success=1
    )
    
    return {
        "message": f"已清理{days}天之前的{deleted_count}条门禁记录",
        "deleted_count": deleted_count,
        "cutoff_date": cutoff_date
    }


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_access_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("access:delete")),
    request: Request = None
):
    """删除单条门禁记录"""
    # 查询要删除的记录
    record = db.query(AccessRecord).filter(AccessRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="门禁记录不存在"
        )
    
    # 删除记录
    db.delete(record)
    db.commit()
    
    # 记录删除日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="delete",
        resource_type="access_record",
        resource_id=str(record_id),
        details={"record_id": record_id},
        request=request,
        success=1
    )
    
    return None