from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_code = Column(String(50), unique=True, nullable=False, index=True)  # 设备编号
    device_name = Column(String(100), nullable=False)  # 设备名称
    device_type = Column(String(50), nullable=False)  # 设备类型：门禁、道闸、电梯等
    location = Column(String(255), nullable=False)  # 安装位置
    status = Column(String(20), default="正常")  # 状态：正常、故障、维护
    ip_address = Column(String(50), nullable=True)  # 设备IP地址
    mac_address = Column(String(50), nullable=True)  # MAC地址
    last_online_time = Column(DateTime(timezone=True), nullable=True)  # 最后在线时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    access_records = relationship("AccessRecord", back_populates="device")


class AccessRecord(Base):
    __tablename__ = "access_records"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    card_id = Column(String(50), nullable=True)  # 卡号，可选
    access_time = Column(DateTime(timezone=True), server_default=func.now())
    access_result = Column(Boolean, default=False)  # 通行结果
    reason = Column(String(255), nullable=True)  # 失败原因
    
    # 关系
    device = relationship("Device", back_populates="access_records")