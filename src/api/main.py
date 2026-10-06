"""FastAPI-приложение для NER финансовых документов.

Запуск:
    uvicorn src.api.main:app --reload --port 8000

Swagger UI: http://localhost:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from loguru import logger

from src.api.schemas import (
    PredictRequest,
    PredictResponse,
    BatchPredictRequest,
    BatchPredictResponse,
    HealthResponse,
)
from src.models.predict import NERPredictor


# Глобальный предиктор — загружается один раз при старте
_predictor: NERPredictor | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _predictor
    logger.info("Загружаю NER-модель...")
    try:
        _predictor = NERPredictor()
        logger.success(f"Модель загружена: {_predictor.model_dir}")
    except FileNotFoundError as e:
        logger.error(f"Модель не найдена: {e}. Обучи сначала: python -m src.models.train")
        _predictor = None
    yield
    logger.info("Остановка сервера.")


app = FastAPI(
    title="NER финансовых документов",
    description="Извлечение сущностей из финансовых документов на русском языке",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Проверка состояния сервиса."""
    if _predictor is None:
        raise HTTPException(status_code=503, detail="Модель не загружена")
    return HealthResponse(
        status="ok",
        model_dir=str(_predictor.model_dir),
        device=str(_predictor.device),
        labels=list(_predictor.model.config.id2label.values()),
    )


@app.post("/predict", response_model=PredictResponse, tags=["predict"])
def predict(req: PredictRequest) -> PredictResponse:
    """Извлечь сущности из одного документа."""
    if _predictor is None:
        raise HTTPException(status_code=503, detail="Модель не загружена")
    entities = _predictor.predict(req.text)
    return PredictResponse(
        entities=[e.__dict__ for e in entities],
        n_entities=len(entities),
    )


@app.post("/predict/batch", response_model=BatchPredictResponse, tags=["predict"])
def predict_batch(req: BatchPredictRequest) -> BatchPredictResponse:
    """Пакетная обработка нескольких документов (до 100 за раз)."""
    if _predictor is None:
        raise HTTPException(status_code=503, detail="Модель не загружена")
    results = []
    for text in req.texts:
        ents = _predictor.predict(text)
        results.append(PredictResponse(
            entities=[e.__dict__ for e in ents],
            n_entities=len(ents),
        ))
    return BatchPredictResponse(results=results)