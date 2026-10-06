"""Создаёт все три файла в docs/ одним разом.

Не редактируй этот файл — просто запусти:
    python scripts/create_docs.py
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DOCS = HERE / "docs"
DOCS.mkdir(exist_ok=True)

# Минимальные заглушки — потом наполнишь сам
FILES = {
    "ARCHITECTURE.md": "# Архитектура\n\nTODO: описание пайплайна.\n",
    "DATA.md": "# Данные\n\nTODO: описание датасета.\n",
    "LIMITATIONS.md": "# Ограничения\n\nTODO: честные ограничения.\n",
}

for name, content in FILES.items():
    path = DOCS / name
    path.write_text(content, encoding="utf-8")
    print(f"OK  {path}")

print("\nГотово. Открой каждый файл в VS Code и заполни содержимым.")