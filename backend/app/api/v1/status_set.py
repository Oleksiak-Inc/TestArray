from fastapi import APIRouter

router = APIRouter(
    prefix="/status-sets",
    tags=["status-sets"],
)