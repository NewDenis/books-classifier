from fastapi import APIRouter, Depends
from books_classifier.app.schemas.classify import ClassifierResponse
from books_classifier.app.classifier.base_model import Classifier
from books_classifier.app.api.deps import get_ml_model_clf

router = APIRouter()


@router.get(
    "/predict",
    response_model=ClassifierResponse,
    response_model_exclude_none=True,
)
async def get_inference(
    query: str,
    model: Classifier = Depends(get_ml_model_clf),
) -> ClassifierResponse:
    prediction = model.predict(query)
    return ClassifierResponse(class_name=prediction)
