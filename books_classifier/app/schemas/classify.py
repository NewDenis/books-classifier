from pydantic import BaseModel, Field


class ClassifierResponse(BaseModel):
    class_name: str = Field(..., description="Class name")
