from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class AttachmentUpdate(BaseModel):
    filename: Optional[str] = None
    parent_attachment_id: Optional[int] = None


class AttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    uploaded_at: datetime
    uploaded_by: int
    filename: str
    relative_path: Optional[str] = None
    edited_by: Optional[int] = None
    edited_at: Optional[datetime] = None
    parent_attachment_id: Optional[int] = None

