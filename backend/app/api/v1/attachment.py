from typing import List
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.attachment import AttachmentService
from app.schemas.attachment import AttachmentOut, AttachmentUpdate
from db.session import get_db
from app.api.utils.auth_dependencies import permission_required
from db.models.users import Users


router = APIRouter(
    prefix="/attachments",
    tags=["attachments"],
)

@router.post("/upload", response_model=AttachmentOut, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("attachments.write")),
):
    service = AttachmentService(db)
    attachment = await service.save_file(file, current_user.id)
    if not attachment:
        raise HTTPException(status_code=400, detail="File could not be saved")
    return attachment


@router.get("/", response_model=List[AttachmentOut])
def list_attachments(
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("attachments.read")),
):
    return AttachmentService(db).list_attachments()


@router.get("/{attachment_id}", response_model=AttachmentOut)
def get_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("attachments.read")),
):
    attachment = AttachmentService(db).get_attachment(attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return attachment


@router.patch("/{attachment_id}", response_model=AttachmentOut)
async def update_attachment(
    attachment_id: int,
    attachment_in: AttachmentUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("attachments.write")),
):
    service = AttachmentService(db)
    data = attachment_in.model_dump(exclude_unset=True)
    if not data:
        attachment = service.get_attachment(attachment_id)
        if not attachment:
            raise HTTPException(status_code=404, detail="Attachment not found")
        return attachment

    attachment = await service.update_file_metadata(attachment_id, current_user.id, **data)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return attachment


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file_by_id(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("attachments.write")),
):
    service = AttachmentService(db)
    attachment = await service.delete_file(attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")