from pydantic import BaseModel, Field
from app.config import settings


class Root(BaseModel):
    message: str = Field(
        f"books_classifier v {settings.SERVICE_VERSION} Команды навыков",
        description="Приветственное сообщение от сервера",
        example="Multihead-classifier v 0.1.0",
    )
