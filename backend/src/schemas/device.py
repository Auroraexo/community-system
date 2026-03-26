from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class DeviceBase(BaseModel):
    device_code: str = Field(..., min_length=1, max_length=50)
    device_name: str = Field(..., min_length=1, max_length=100)
    device_type: str = Field(..., min_length=1, max_length=50)
    location: str = Field(..., min_length=1, max_length=200)
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    device_name: Optional[str] = Field(None, min_length=1, max_length=100)
    device_type: Optional[str] = Field(None, min_length=1, max_length=50)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None


class Device(DeviceBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: str
    last_online_time: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class AccessRecordBase(BaseModel):
    device_id: int
    user_id: Optional[int] = None
    card_id: Optional[str] = None
    access_result: bool
    reason: Optional[str] = None


class AccessRecordCreate(AccessRecordBase):
    pass


class AccessRecord(AccessRecordBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    access_time: datetime
    device: Optional['Device'] = None