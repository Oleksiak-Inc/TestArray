from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AttachmentBase(BaseModel):
    resolution_id: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None

class AttachmentCreateInternal(BaseModel):
    uploaded_by: int
    filename: str
    relative_path: str
    resolution_id: Optional[int]
    settings: Optional[dict]
    presentmon_version: Optional[str]

class AttachmentOut(BaseModel):
    id: int
    uploaded_at: datetime
    uploaded_by: int
    filename: str
    
    class Config:
        from_attributes = True

