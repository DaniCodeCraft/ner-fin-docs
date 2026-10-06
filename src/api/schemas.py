"""Pydantic-схемы для REST API."""

from pydantic import BaseModel, ConfigDict, Field
class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Текст финансового документа")


class EntityOut(BaseModel):
    text: str
    label: str
    start: int
    end: int
    score: float


class PredictResponse(BaseModel):
    entities: list[EntityOut]
    n_entities: int


class BatchPredictRequest(BaseModel):
    texts: list[str] = Field(..., min_items=1, max_items=100)


class BatchPredictResponse(BaseModel):
    results: list[PredictResponse]


class HealthResponse(BaseModel):
    # Отключаем проверку protected namespace для поля model_dir
    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_dir: str
    device: str
    labels: list[str]