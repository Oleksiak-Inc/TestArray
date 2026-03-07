from fastapi import APIRouter

router = APIRouter(
    prefix="/test-cases",
    tags=["test-cases"],
)