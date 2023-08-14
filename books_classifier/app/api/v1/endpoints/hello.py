from fastapi import APIRouter
from books_classifier.app.schemas.hello import HelloWorld


router = APIRouter()


@router.get(
    "/hello",
    response_model=HelloWorld,
)
async def get_test() -> HelloWorld:
    return HelloWorld()
