from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.attachment import AttachmentService
from app.schemas.attachment import AttachmentOut
from db.session import get_db
from app.api.utils.users import get_current_user
from db.models.users import Users


router = APIRouter(
    prefix="/attachments",
    tags=["attachments"],
)

@router.post("/upload", response_model=AttachmentOut, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = AttachmentService(db)
    attachment = await service.save_file(file, current_user.id)
    if not attachment:
        raise HTTPException(status_code=400, detail="File could not be saved")
    return attachment