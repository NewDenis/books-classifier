from fastapi import APIRouter
from app.schemas.hello import HelloWorld


router = APIRouter()


@router.get(
    "/hello",
    response_model=HelloWorld,
)
async def get_test(
) -> HelloWorld:
    return HelloWorld()
