from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from io import BytesIO

from ..database import get_db
from ..models.user import User
from ..models.device import Device, AccessRecord
from ..schemas.device import Device as DeviceSchema, DeviceCreate, DeviceUpdate, AccessRecord as AccessRecordSchema, AccessRecordCreate
from ..utils.auth import get_current_user, require_permissions
from ..utils.logger import log_operation

router = APIRouter()


@router.get("", response_model=dict)
async def get_devices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    device_code: Optional[str] = None,
    name: Optional[str] = None,
    device_type: Optional[str] = None,
    location: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """获取设备列表（分页）"""
    # 构建查询
    query = db.query(Device)
    
    # 应用过滤条件
    if device_code:
        query = query.filter(Device.device_code.contains(device_code))
    if name:
        query = query.filter(Device.name.contains(name))
    if device_type:
        query = query.filter(Device.device_type == device_type)
    if location:
        query = query.filter(Device.location.contains(location))
    if status:
        query = query.filter(Device.status == status)
    
    # 计算总数
    total = query.count()
    
    # 分页
    skip = (page - 1) * page_size
    devices = query.offset(skip).limit(page_size).all()
    
    # 记录查询日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="view",
        resource_type="device",
        details={"page": page, "page_size": page_size, "device_type": device_type, "status": status},
        request=request,
        success=1
    )
    
    # 转换为Pydantic模式
    device_schemas = [DeviceSchema.model_validate(device) for device in devices]
    
    return {
        "items": device_schemas,
        "total": total
    }


@router.post("/", response_model=DeviceSchema, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_data: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("device:create")),
    request: Request = None
):
    """创建设备"""
    # 检查设备编号是否已存在
    existing_device = db.query(Device).filter(Device.device_code == device_data.device_code).first()
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="设备编号已存在"
        )
    
    # 创建设备
    db_device = Device(**device_data.model_dump())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    # 记录创建设备日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="create",
        resource_type="device",
        resource_id=str(db_device.id),
        details=device_data.model_dump(),
        request=request,
        success=1
    )
    
    return db_device


@router.get("/{device_id}", response_model=DeviceSchema)
async def get_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("device:read")),
    request: Request = None
):
    """获取单个设备信息"""
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    return DeviceSchema.model_validate(device)


@router.put("/{device_id}", response_model=DeviceSchema)
async def update_device(
    device_id: int,
    device_update: DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("device:update")),
    request: Request = None
):
    """更新设备信息"""
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 更新设备信息
    update_data = device_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)
    
    db.commit()
    db.refresh(device)
    
    # 记录更新日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="update",
        resource_type="device",
        resource_id=str(device_id),
        details=update_data,
        request=request,
        success=1
    )
    
    return DeviceSchema.model_validate(device)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("device:delete")),
    request: Request = None
):
    """删除设备"""
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 检查是否有关联的门禁记录
    access_record_count = db.query(AccessRecord).filter(AccessRecord.device_id == device_id).count()
    if access_record_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该设备下有{access_record_count}条门禁记录，无法删除"
        )
    
    # 删除设备
    db.delete(device)
    db.commit()
    
    # 记录删除日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="delete",
        resource_type="device",
        resource_id=str(device_id),
        details={"device_code": device.device_code, "name": device.name},
        request=request,
        success=1
    )
    
    return None

@router.post("/batch-delete", status_code=status.HTTP_204_NO_CONTENT)
async def batch_delete_devices(
    device_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("device:delete")),
    request: Request = None
):
    """批量删除设备"""
    # 查询要删除的设备
    devices = db.query(Device).filter(Device.id.in_(device_ids)).all()
    
    if not devices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到要删除的设备"
        )
    
    # 检查是否有关联的门禁记录
    device_ids_with_records = db.query(AccessRecord.device_id).filter(
        AccessRecord.device_id.in_(device_ids)
    ).distinct().all()
    device_ids_with_records = [id[0] for id in device_ids_with_records]
    
    if device_ids_with_records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ID为{', '.join(map(str, device_ids_with_records))}的设备有关联的门禁记录，无法删除"
        )
    
    # 删除设备
    for device in devices:
        db.delete(device)
    
    db.commit()
    
    # 记录批量删除日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="batch_delete",
        resource_type="device",
        details={"device_ids": device_ids, "count": len(devices)},
        request=request,
        success=1
    )
    
    return None

@router.put("/{device_id}/status")
async def update_device_status(
    device_id: int,
    status_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("device:update")),
    request: Request = None
):
    """更新设备状态"""
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 验证状态值
    valid_statuses = ["online", "offline", "maintenance", "disabled"]
    new_status = status_data.get("status")
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的状态值，必须是以下之一: {', '.join(valid_statuses)}"
        )
    
    # 更新状态
    device.status = new_status
    db.commit()
    
    # 记录日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="update_status",
        resource_type="device",
        resource_id=str(device_id),
        details={"status": new_status},
        request=request,
        success=1
    )
    
    return {"message": "设备状态更新成功"}

@router.get("/types/list", response_model=List[Dict[str, Any]])
async def get_device_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("device:read"))
):
    """获取设备类型列表"""
    # 查询所有不重复的设备类型
    device_types = db.query(Device.device_type).distinct().all()
    
    # 转换为标准化格式
    types_list = [{"value": dt[0], "label": dt[0]} for dt in device_types if dt[0] is not None]
    
    return types_list

@router.get("/locations/list", response_model=List[Dict[str, Any]])
async def get_device_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("device:read"))
):
    """获取设备位置列表"""
    # 查询所有不重复的设备位置
    locations = db.query(Device.location).distinct().all()
    
    # 转换为标准化格式
    locations_list = [{"value": loc[0], "label": loc[0]} for loc in locations if loc[0] is not None]
    
    return locations_list

@router.post("/import")
async def import_devices(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("device:create")),
    request: Request = None
):
    """导入设备数据"""
    # 验证文件类型
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持Excel文件格式（.xlsx, .xls）"
        )
    
    try:
        # 读取Excel文件
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))
        
        # 验证必需的列
        required_columns = ['device_code', 'name', 'device_type', 'location']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Excel文件必须包含以下列: {', '.join(required_columns)}"
            )
        
        # 导入数据
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 检查设备编号是否已存在
                existing = db.query(Device).filter(
                    Device.device_code == str(row['device_code'])
                ).first()
                
                if existing:
                    error_count += 1
                    errors.append(f"第{index+2}行：设备编号 {row['device_code']} 已存在")
                    continue
                
                # 创建设备
                device = Device(
                    device_code=str(row['device_code']),
                    name=str(row['name']),
                    device_type=str(row['device_type']),
                    location=str(row['location']),
                    ip_address=row.get('ip_address', ''),
                    mac_address=row.get('mac_address', ''),
                    description=row.get('description', ''),
                    status='offline'  # 默认状态
                )
                
                db.add(device)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"第{index+2}行：{str(e)}")
        
        db.commit()
        
        # 记录日志
        log_operation(
            db=db,
            user_id=current_user.id,
            action="import",
            resource_type="device",
            details={"success_count": success_count, "error_count": error_count},
            request=request,
            success=1 if error_count == 0 else 0
        )
        
        return {
            "message": f"导入完成，成功{success_count}条，失败{error_count}条",
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入失败: {str(e)}"
        )

@router.get("/export")
async def export_devices(
    device_id: Optional[int] = None,
    name: Optional[str] = None,
    device_type: Optional[str] = None,
    status: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """导出设备数据"""
    from fastapi.responses import StreamingResponse
    
    # 查询设备
    query = db.query(Device)
    
    if device_id:
        query = query.filter(Device.id == device_id)
    if name:
        query = query.filter(Device.name.contains(name))
    if device_type:
        query = query.filter(Device.device_type == device_type)
    if location:
        query = query.filter(Device.location.contains(location))
    if status:
        query = query.filter(Device.status == status)
    
    devices = query.all()
    
    # 转换为DataFrame
    data = []
    for device in devices:
        data.append({
            '设备编号': device.device_code,
            '设备名称': device.name,
            '设备类型': device.device_type,
            '位置': device.location,
            'IP地址': device.ip_address,
            'MAC地址': device.mac_address,
            '状态': device.status,
            '描述': device.description,
            '创建时间': device.created_at.strftime('%Y-%m-%d %H:%M:%S') if device.created_at else ''
        })
    
    df = pd.DataFrame(data)
    
    # 创建Excel文件
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='设备列表')
    
    output.seek(0)
    
    # 记录日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="export",
        resource_type="device",
        details={"count": len(devices)},
        request=request,
        success=1
    )
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=设备列表_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )

@router.get("/stats/status")
async def get_device_status_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("device:read")),
    request: Request = None
):
    """获取设备状态统计"""
    # 统计各种状态的设备数量
    status_counts = db.query(
        Device.status,
        func.count(Device.id).label('count')
    ).group_by(
        Device.status
    ).all()
    
    # 转换为字典
    stats = {item.status: item.count for item in status_counts}
    
    # 确保所有状态都有统计
    all_statuses = ['online', 'offline', 'maintenance', 'disabled']
    for status in all_statuses:
        if status not in stats:
            stats[status] = 0
    
    # 计算总数
    total = sum(stats.values())
    stats['total'] = total
    
    # 记录日志
    log_operation(
        db=db,
        user_id=current_user.id,
        action="view_stats",
        resource_type="device",
        details={"stats": stats},
        request=request,
        success=1
    )
    
    return stats


@router.get("/{device_id}/access-records", response_model=List[AccessRecordSchema])
async def get_device_access_records(
    device_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions("device:read")),
    request: Request = None
):
    """获取设备的门禁记录"""
    # 检查设备是否存在
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 获取门禁记录
    records = db.query(AccessRecord).filter(
        AccessRecord.device_id == device_id
    ).order_by(AccessRecord.access_time.desc()).offset(skip).limit(limit).all()
    
    # 转换为Pydantic模式
    return [AccessRecordSchema.model_validate(record) for record in records]