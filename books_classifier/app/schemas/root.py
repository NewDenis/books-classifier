from pydantic import BaseModel, Field
from books_classifier.app.config import settings


class Root(BaseModel):
    message: str = Field(
        f"books_classifier v {settings.SERVICE_VERSION}",
        description="Приветственное сообщение от сервера",
        example="books_classifier v 0.1.0",
    )
