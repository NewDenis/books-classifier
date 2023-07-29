from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/get_configs")
async def get_configs():
    return settings
