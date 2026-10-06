"""Быстрая проверка _collect: не должны попадать внешние запятые/точки в спаны."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.generation.templates import _collect  # noqa: E402


def _has_trailing_sentence_punct(text: str) -> bool:
    """True, если в конце — пунктуация конца предложения (не инициал/сокращение)."""
    if not text:
        return False
    if text.endswith((",", ";", ":", "!", "?", ")", "]", "}")):
        return True
    if text.endswith("."):
        # "И.И." — точка после буквы = инициал, ок
        if len(text) >= 2 and text[-2].isalpha():
            return False
        return True
    return False


def _has_leading_sentence_punct(text: str) -> bool:
    if not text:
        return False
    return text.startswith((",", ";", ":", "(", "[", "{"))


def main() -> None:
    cases = [
        (
            'ООО "Ромашка", в лице Иванова И.И., сумма 100 руб.',
            [('ООО "Ромашка"', "ORG"), ("Иванова И.И.", "PERSON"), ("100 руб.", "MONEY")],
            "Запятые после сущностей",
        ),
        (
            'Плательщик: ПАО "Сатурн". ИНН 1234567890.',
            [('ПАО "Сатурн"', "ORG"), ("1234567890", "INN")],
            "Точки — конец предложения",
        ),
        (
            "Сумма: (1 000 руб.); дата: 01.01.2024;",
            [("1 000 руб.", "MONEY"), ("01.01.2024", "DATE")],
            "Скобки, точки с запятой",
        ),
    ]

    ok = True
    for text, entities, desc in cases:
        print(f"\n{desc}")
        print(f"   {text!r}")
        spans = _collect(text, entities)
        for s in spans:
            print(f"   {s.label:8} | {s.text!r:25} | {s.start}-{s.end}")
            if _has_trailing_sentence_punct(s.text):
                print("      ❌ хвостовая пунктуация осталась!")
                ok = False
            if _has_leading_sentence_punct(s.text):
                print("      ❌ ведущая пунктуация осталась!")
                ok = False

    if ok:
        print("\n✅ Все проверки прошли — границы слов работают корректно")
    else:
        print("\n❌ Есть проблемы с разметкой")
        sys.exit(1)


if __name__ == "__main__":
    main()