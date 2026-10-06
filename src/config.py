from pathlib import Path
import yaml
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent


class ModelConfig(BaseModel):
    name: str
    max_length: int
    num_labels: int


class TrainingConfig(BaseModel):
    batch_size: int
    epochs: int
    lr: float
    weight_decay: float
    warmup_ratio: float
    eval_split: float
    test_split: float


class DataConfig(BaseModel):
    n_documents: int
    output_dir: str
    raw_dir: str


class Config(BaseModel):
    seed: int
    model: ModelConfig
    labels: list[str]
    training: TrainingConfig
    data: DataConfig


def load_config(path: str | Path = "configs/config.yaml") -> Config:
    with open(ROOT / path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return Config(**raw)