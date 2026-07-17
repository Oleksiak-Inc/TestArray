from .utils.service import BaseService
from pathlib import Path
from uuid import uuid4
import aiofiles
from datetime import datetime
from core.config import settings
from db.models.attachments import Attachments
from fastapi import UploadFile
from typing import List, Union

def get_date_subdir() -> Path:
    now = datetime.now()
    return Path(str(now.year)) / f"{now.month:02}" / f"{now.day:02}"

class AttachmentService(BaseService):
    def get_attachment(self, attachment_id: int):
        return self.db.query(Attachments).filter(Attachments.id == attachment_id).first()

    def list_attachments(self):
        return self.db.query(Attachments).order_by(Attachments.uploaded_at.desc()).all()

    async def save_file(self, file: UploadFile, uploaded_by: int, **kwargs) -> Union[Attachments, None]:
        ext = Path(file.filename).suffix
        if ext not in settings.ALLOWED_FILE_EXTENSIONS:
            return None

        date_dir = get_date_subdir()
        full_dir = Path(settings.UPLOAD_DIR) / date_dir
        full_dir.mkdir(parents=True, exist_ok=True)

        stored_name = f"{uuid4()}{ext}"
        dest = full_dir / stored_name

        total_bytes = 0
        try:
            async with aiofiles.open(dest, "wb") as f:
                while chunk := await file.read(settings.CHUNK_SIZE):
                    total_bytes += len(chunk)
                    if total_bytes > settings.MAX_FILE_SIZE:
                        await f.close()
                        dest.unlink(missing_ok=True)
                        return None
                    await f.write(chunk)
        except Exception:
            if dest.exists():
                dest.unlink(missing_ok=True)
            return None

        attachment = Attachments(
            filename=file.filename,
            relative_path=str(date_dir / stored_name),
            uploaded_by=uploaded_by,
            uploaded_at=datetime.now(),
            **kwargs
        )
        return self.save(attachment)

    async def delete_file(self, attachment_id: int) -> Union[Attachments, None]:
        attachment = self.db.query(Attachments).filter(Attachments.id == attachment_id).first()
        if not attachment:
            return None

        file_path = Path(settings.UPLOAD_DIR) / attachment.relative_path
        if file_path.exists():
            file_path.unlink()
        return self.delete(attachment)

    async def bulk_save_files(self, files: List[UploadFile], uploaded_by: int) -> List[dict]:
        results = []
        for file in files:
            attachment = await self.save_file(file, uploaded_by)
            status = "fail"
            if attachment:
                status = "success"
                
            results.append({"attachment": attachment, "status": status})
        return results

    async def replace_file(self, attachment_id: int, edited_by: int, new_file: UploadFile) -> Union[Attachments, None]:
        attachment = self.db.query(Attachments).filter(Attachments.id == attachment_id).first()
        if not attachment:
            return None
        # delete old file from disk
        old_path = Path(settings.UPLOAD_DIR) / attachment.relative_path
        if old_path.exists():
            old_path.unlink()
        # save new file to disk (reuse save_file logic but without DB insert)
        ext = Path(new_file.filename).suffix
        if ext not in settings.ALLOWED_FILE_EXTENSIONS:
            return None
        date_dir = get_date_subdir()
        full_dir = Path(settings.UPLOAD_DIR) / date_dir
        full_dir.mkdir(parents=True, exist_ok=True)
        stored_name = f"{uuid4()}{ext}"
        dest = full_dir / stored_name
        total_bytes = 0
        async with aiofiles.open(dest, "wb") as f:
            while chunk := await new_file.read(settings.CHUNK_SIZE):
                total_bytes += len(chunk)
                if total_bytes > settings.MAX_FILE_SIZE:
                    await f.close()
                    dest.unlink(missing_ok=True)
                    return None
                await f.write(chunk)
        # update the existing DB record
        attachment.filename = new_file.filename
        attachment.relative_path = str(date_dir / stored_name)
        attachment.edited_by = edited_by
        attachment.edited_at = datetime.now()
        return self.commit_and_refresh(attachment)

    async def update_file_metadata(self, attachment_id: int, edited_by: int, **kwargs) -> Union[Attachments, None]:
        attachment = self.db.query(Attachments).filter(Attachments.id == attachment_id).first()
        if not attachment:
            return None

        # Update the metadata fields provided in kwargs
        for key, value in kwargs.items():
            setattr(attachment, key, value)

        attachment.edited_by = edited_by
        attachment.edited_at = datetime.now()
        return self.commit_and_refresh(attachment)