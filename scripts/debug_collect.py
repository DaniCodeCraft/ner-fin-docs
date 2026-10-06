"""Отладка: что реально возвращает _collect прямо сейчас."""
import inspect

from src.generation.templates import _collect


def show_version() -> None:
    """Смотрим, какая версия _collect импортируется."""
    code = inspect.getsource(_collect)
    print("=== Версия _collect ===")
    print(f"  Файл:                         {_collect.__module__}")
    print(f"  Содержит '_is_word_boundary': {'_is_word_boundary' in code}")
    print(f"  Содержит 'used_ranges':       {'used_ranges' in code}")
    print(f"  Содержит 'overlaps':          {'overlaps' in code}")
    print()


def show_spans() -> None:
    """Генерируем примеры и смотрим, что возвращает _collect."""
    cases = [
        (
            'АО "Дельта", в лице Селезнева Кир Демьянович, именуемое Исполнитель',
            [('АО "Дельта"', "ORG"), ("Селезнева Кир Демьянович", "PERSON")],
            "ORG и PERSON с запятыми после",
        ),
        (
            "Р/с 25832950016740395980, БИК 047652614.",
            [("25832950016740395980", "ACCOUNT"), ("047652614", "BIK")],
            "ACCOUNT и BIK с пунктуацией",
        ),
        (
            "Итого к оплате: 29 317 637 ₽.",
            [("29 317 637 ₽", "MONEY")],
            "MONEY с точкой",
        ),
    ]

    print("=== Спаны ===")
    bad = 0
    for text, ents, desc in cases:
        print(f"\n[{desc}]")
        print(f"  Текст: {text!r}")
        for s in _collect(text, ents):
            warn = ""
            if s.text.endswith((",", ".", ";")):
                warn = "  ⚠️ ПУНКТУАЦИЯ В КОНЦЕ"
                bad += 1
            print(f"  {s.label:8} | {s.text!r:30} | {s.start}-{s.end}{warn}")

    print()
    if bad == 0:
        print("✅ Все спаны чистые — _collect работает правильно")
    else:
        print(f"❌ {bad} спанов с пунктуацией — _collect возвращает старое поведение")


def main() -> None:
    show_version()
    show_spans()


if __name__ == "__main__":
    main()