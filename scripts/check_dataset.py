"""Проверка, что датасет содержит правильную разметку.

Использует offset-ы из dataset.jsonl, чтобы показать ровно тот текст,
что был в исходном документе — без эвристик склейки.
"""
import json
from collections import Counter
from pathlib import Path


path = Path("data/processed/dataset.jsonl")
lines = path.read_text(encoding="utf-8").splitlines()
print(f"Всего записей: {len(lines)}")


for i, line in enumerate(lines[:3]):
    rec = json.loads(line)
    text = rec["text"]
    print(f"\n=== Запись {i} ===")
    print(f"Текст (первые 200): {text[:200]!r}")

    # Определяем, сколько полей в каждом токене (2 или 4)
    sample = rec["tokens"][0]
    has_offsets = len(sample) >= 4

    if not has_offsets:
        print("⚠️ В датасете нет offset-ов! Перегенерируй: python -m src.generation.build_dataset")
        continue

    # Собираем сущности через offsets
    ents = []
    current = None
    for tok, lab, start, end in rec["tokens"]:
        if lab.startswith("B-"):
            if current:
                ents.append(current)
            current = {"label": lab[2:], "start": start, "end": end}
        elif lab.startswith("I-") and current and current["label"] == lab[2:]:
            current["end"] = end  # расширяем до конца текущего токена
        else:
            if current:
                ents.append(current)
            current = None
    if current:
        ents.append(current)

    print(f"Сущности ({len(ents)}):")
    for e in ents:
        # Берём текст НАПРЯМУЮ из исходного — никакой склейки!
        snippet = text[e["start"]:e["end"]]
        print(f"  {e['label']:10} | {snippet!r}")


# Статистика по меткам
labels = Counter()
for line in lines:
    rec = json.loads(line)
    for t in rec["tokens"]:
        labels[t[1]] += 1

print("\n=== Распределение меток ===")
for lab, cnt in sorted(labels.items()):
    print(f"  {lab:15} {cnt}")