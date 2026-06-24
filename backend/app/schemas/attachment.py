from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any
from datetime import datetime

'''
class AttachmentBase(BaseModel):
    resolution_id: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None
'''

'''
class AttachmentUploadForm(BaseModel):
    resolution_id: Optional[int] = Field(None, form=True)
    settings: Optional[str] = Field(None, form=True)
    presentmon_version: Optional[str] = Field(None, form=True)
'''

class AttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    uploaded_at: datetime
    uploaded_by: int
    filename: str

