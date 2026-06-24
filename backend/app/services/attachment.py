from .utils.service import BaseService
from pathlib import Path
from uuid import uuid4
import aiofiles
from datetime import datetime
from core.config import settings
from db.models.attachments import Attachments
from fastapi import UploadFile
import json
from typing import Optional, Dict, Any

def get_date_subdir() -> Path:
    """Return the date-based subdirectory *relative to the upload root*."""
    now = datetime.now()
    return Path(str(now.year)) / f"{now.month:02}" / f"{now.day:02}"

class AttachmentService(BaseService):
    async def save_file(self, file: UploadFile, uploaded_by: int):

        ext = Path(file.filename).suffix
        if ext not in settings.ALLOWED_FILE_EXTENSIONS:
            return None

        contents = await file.read()
        if len(contents) > settings.MAX_FILE_SIZE:
            return None

        date_dir = get_date_subdir()
        full_dir = Path(settings.UPLOAD_DIR) / date_dir
        full_dir.mkdir(parents=True, exist_ok=True)

        stored_name = f"{uuid4()}{ext}"
        dest = full_dir / stored_name

        try:
            async with aiofiles.open(dest, "wb") as f:
                await f.write(contents)
        except Exception:
            return None

        attachment = Attachments(
            filename=file.filename,
            relative_path=str(date_dir / stored_name),
            uploaded_by=uploaded_by
        )
        self.db.add(attachment)
        self.commit_and_refresh(attachment)
        return attachment
    