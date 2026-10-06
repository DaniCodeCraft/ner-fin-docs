"""Шаблоны финансовых документов.

Возвращают (текст, spans), где spans — список Span {start, end, label, text}.
Гарантируется, что границы спана — на границах слов (не внутри токена).
"""
from dataclasses import dataclass, field


@dataclass
class Span:
    start: int
    end: int
    label: str
    text: str


@dataclass
class Document:
    text: str
    spans: list[Span] = field(default_factory=list)


def _is_word_boundary(text: str, pos: int) -> bool:
    """True, если позиция pos — начало или конец слова.
    
    Позиция считается границей, если выходит за пределы текста,
    либо символ в этой позиции НЕ буква/цифра/подчёркивание.
    """
    if pos < 0 or pos >= len(text):
        return True
    ch = text[pos]
    return not (ch.isalnum() or ch == "_")


def _collect(text: str, entities: list[tuple[str, str]]) -> list[Span]:
    """Находит позиции сущностей в тексте.
    
    Сущность должна занимать целые слова: границы проверяются по
    не-алфанумерическим символам с обеих сторон. Это предотвращает
    случай, когда 'Ромашка' матчится внутри 'Ромашка",'.
    
    Поиск идёт слева направо, без пересечений; длинные сущности
    матчатся первыми, чтобы избежать вложенности.
    """
    spans: list[Span] = []
    used_ranges: list[tuple[int, int]] = []
    entities_sorted = sorted(entities, key=lambda x: -len(x[0]))

    for value, label in entities_sorted:
        start = 0
        while True:
            idx = text.find(value, start)
            if idx == -1:
                break
            end = idx + len(value)

            # Проверяем, что сущность — целые слова, а не часть токена
            if not _is_word_boundary(text, idx - 1):
                start = idx + 1
                continue
            if not _is_word_boundary(text, end):
                start = idx + 1
                continue

            # Проверяем отсутствие пересечений с уже найденными спанами
            overlaps = any(not (end <= s or idx >= e) for s, e in used_ranges)
            if overlaps:
                start = idx + 1
                continue

            used_ranges.append((idx, end))
            spans.append(Span(idx, end, label, value))
            break

    spans.sort(key=lambda s: s.start)
    return spans