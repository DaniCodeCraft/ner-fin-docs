"""Проверка API на реалистичных финансовых документах.

⚠️ Модель обучена на шаблонных финансовых документах. На коротких
изолированных фразах (типа 'ИНН 7707083893' без контекста) может
быть неуверена — это ограничение синтетических данных.
"""
from pathlib import Path

import requests

API_URL = "http://localhost:8000/predict"

# Берём реальные документы из data/raw/
SAMPLES = [
    Path("data/raw/doc_00000.txt"),
    Path("data/raw/doc_00001.txt"),
    Path("data/raw/doc_00002.txt"),
]

for i, path in enumerate(SAMPLES, 1):
    if not path.exists():
        print(f"⚠️ {path} не найден, пропускаю")
        continue

    text = path.read_text(encoding="utf-8")
    print(f"\n=== Пример {i}: {path.name} ===")
    print(f"Текст (первые 200): {text[:200]!r}\n")

    try:
        resp = requests.post(API_URL, json={"text": text}, timeout=30)
        resp.raise_for_status()
    except requests.HTTPError as e:
        print(f"❌ Ошибка API: {e}")
        continue

    data = resp.json()
    for e in data["entities"]:
        print(f"  {e['label']:10} | {e['text']!r:35} | score={e['score']}")

    print(f"\nВсего: {data['n_entities']} сущностей")

    # Проверка порога
    low_score = [e for e in data["entities"] if e["score"] < 0.9]
    if low_score:
        print(f"⚠️ Есть сущности со score < 0.9: {len(low_score)}")
    else:
        print("✅ Все сущности со score >= 0.9")