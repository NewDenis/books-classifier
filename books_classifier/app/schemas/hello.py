from pydantic import BaseModel, Field


class HelloWorld(BaseModel):
    message: str = Field(
        "Hello world!",
        description="Приветственное сообщение от сервера",
        example="Multihead-classifier v 0.1.0",
    )
