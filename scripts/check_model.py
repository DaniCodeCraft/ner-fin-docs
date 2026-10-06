"""Проверка, что модель на диске — та, что была обучена."""
from pathlib import Path
from transformers import AutoConfig, AutoModelForTokenClassification, AutoTokenizer

model_dir = Path("models/ner-fin")

print("=== Файлы в models/ner-fin ===")
for f in sorted(model_dir.iterdir()):
    size = f.stat().st_size if f.is_file() else "-"
    mtime = f.stat().st_mtime
    import datetime
    dt = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
    print(f"  {f.name:30} {str(size):>12} {dt}")

print("\n=== Config ===")
cfg = AutoConfig.from_pretrained(model_dir)
print(f"  num_labels: {cfg.num_labels}")
print(f"  id2label:   {cfg.id2label}")

print("\n=== Токенизатор ===")
tok = AutoTokenizer.from_pretrained(model_dir)
print(f"  vocab_size: {tok.vocab_size}")

print("\n=== Загрузка модели ===")
model = AutoModelForTokenClassification.from_pretrained(model_dir)
print(f"  classifier.weight shape: {model.classifier.weight.shape}")
print(f"  classifier.bias shape:   {model.classifier.bias.shape}")

# Проверка: загружаются ли веса classifier из чекпоинта?
# Если да — они НЕ «случайные», а обученные
import numpy as np
w = model.classifier.weight.detach().numpy()
print(f"  classifier.weight mean:  {w.mean():.6f}")
print(f"  classifier.weight std:   {w.std():.6f}")