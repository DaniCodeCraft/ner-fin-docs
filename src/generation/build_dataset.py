"""Генерирует синтетические финансовые документы с BIO-разметкой."""
import json
import random
import re
from pathlib import Path

from loguru import logger
from tqdm import tqdm

from src.config import load_config, ROOT
from src.generation import generators as G
from src.generation.templates import Document, _collect

random.seed(42)


def make_payment_order() -> Document:
    """Платёжное поручение."""
    payer = G.gen_org()
    receiver = G.gen_org()
    inn1, inn2 = G.gen_inn(), G.gen_inn()
    kpp1, kpp2 = G.gen_kpp(), G.gen_kpp()
    ogrn1 = G.gen_ogrn()
    bik = G.gen_bik()
    acc1, acc2 = G.gen_account(), G.gen_account()
    amount = G.gen_money()
    date = G.gen_date()
    contract = G.gen_contract()
    person = G.gen_person()

    text = (
        f"ПЛАТЁЖНОЕ ПОРУЧЕНИЕ № {contract} от {date}\n"
        f"Плательщик: {payer}\n"
        f"ИНН {inn1}, КПП {kpp1}, ОГРН {ogrn1}\n"
        f"Р/с {acc1} в банке, БИК {bik}\n"
        f"Получатель: {receiver}\n"
        f"ИНН {inn2}, КПП {kpp2}\n"
        f"Р/с {acc2}\n"
        f"Сумма: {amount}\n"
        f"Назначение платежа: оплата по договору № {contract}.\n"
        f"Главный бухгалтер: {person}\n"
    )
    ents = [
        (contract, "CONTRACT"), (date, "DATE"),
        (payer, "ORG"), (inn1, "INN"), (kpp1, "KPP"), (ogrn1, "OGRN"),
        (acc1, "ACCOUNT"), (bik, "BIK"),
        (receiver, "ORG"), (inn2, "INN"), (kpp2, "KPP"),
        (acc2, "ACCOUNT"),
        (amount, "MONEY"), (person, "PERSON"),
    ]
    return Document(text=text, spans=_collect(text, ents))


def make_contract() -> Document:
    """Договор оказания услуг."""
    org1 = G.gen_org()
    org2 = G.gen_org()
    person1 = G.gen_person()
    person2 = G.gen_person()
    date = G.gen_date()
    contract = G.gen_contract()
    amount = G.gen_money()
    inn = G.gen_inn()
    acc = G.gen_account()
    bik = G.gen_bik()

    text = (
        f"ДОГОВОР № {contract}\n"
        f"г. Москва                                {date}\n\n"
        f"{org1}, в лице {person1}, именуемое «Исполнитель», "
        f"и {org2}, в лице {person2}, именуемое «Заказчик», "
        f"заключили настоящий договор о нижеследующем:\n"
        f"1. Стоимость услуг составляет {amount}.\n"
        f"2. Оплата производится на р/с {acc}, БИК {bik}.\n"
        f"3. ИНН Исполнителя: {inn}.\n"
    )
    ents = [
        (contract, "CONTRACT"), (date, "DATE"),
        (org1, "ORG"), (person1, "PERSON"),
        (org2, "ORG"), (person2, "PERSON"),
        (amount, "MONEY"), (acc, "ACCOUNT"),
        (bik, "BIK"), (inn, "INN"),
    ]
    return Document(text=text, spans=_collect(text, ents))


def make_invoice() -> Document:
    """Счёт на оплату."""
    supplier = G.gen_org()
    buyer = G.gen_org()
    inn1, inn2 = G.gen_inn(), G.gen_inn()
    kpp = G.gen_kpp()
    acc = G.gen_account()
    bik = G.gen_bik()
    date = G.gen_date()
    amount = G.gen_money()
    person = G.gen_person()

    text = (
        f"СЧЁТ НА ОПЛАТУ № {G.gen_contract()} от {date}\n"
        f"Поставщик: {supplier}\n"
        f"ИНН/КПП: {inn1}/{kpp}\n"
        f"Банк: ПАО Сбербанк, БИК {bik}\n"
        f"Р/с: {acc}\n"
        f"Покупатель: {buyer}\n"
        f"ИНН покупателя: {inn2}\n"
        f"Итого к оплате: {amount}\n"
        f"Руководитель: {person}\n"
    )
    ents = [
        (date, "DATE"), (supplier, "ORG"), (inn1, "INN"),
        (kpp, "KPP"), (bik, "BIK"), (acc, "ACCOUNT"),
        (buyer, "ORG"), (inn2, "INN"),
        (amount, "MONEY"), (person, "PERSON"),
    ]
    return Document(text=text, spans=_collect(text, ents))


GENERATORS = [make_payment_order, make_contract, make_invoice]


# Регулярка токенизации: числа с пробелами, отдельные числа, слова,
# отдельные знаки пунктуации. ДОЛЖНА совпадать с src/models/predict.py.
_TOKEN_RE = re.compile(
    r"\d[\d\s]*\d"           # числа с пробелами внутри: "1 269", "29 317 637"
    r"|\d"                    # одно число
    r"|[A-Za-zА-Яа-яЁё]+"     # слова (буквы, включая Ё)
    r"|[₽$€£¥]"               # валютные символы
    r"|[/\-.,;:!?\"'«»()«»]"  # пунктуация
)


def _tokenize(text: str) -> list[tuple[str, int, int]]:
    """Разбивает текст на токены: слова, числа и отдельная пунктуация.

    Возвращает [(token, start, end), ...].
    Пробелы внутри чисел (1 000 000) схлопываются в одно число.

    Отличия от split по whitespace:
      - 'АО "Дельта",' → ['АО', '"', 'Дельта', '"', ',']
      - '1 269 рублей' → ['1269', 'рублей']
    """
    tokens: list[tuple[str, int, int]] = []
    for m in _TOKEN_RE.finditer(text):
        tok = m.group()
        if " " in tok:
            tok_clean = tok.replace(" ", "")
            tokens.append((tok_clean, m.start(), m.end()))
        else:
            tokens.append((tok, m.start(), m.end()))
    return tokens


def doc_to_bio(doc: Document) -> list[tuple[str, str, int, int]]:
    """Превращает спаны в BIO-разметку по токенам с offset-ами.

    Возвращает [(token, label, start, end), ...], где start/end —
    позиции токена в исходном тексте.
    """
    tokens = _tokenize(doc.text)

    bio: list[tuple[str, str, int, int]] = []
    for tok, tstart, tend in tokens:
        label = "O"
        for span in doc.spans:
            if not (tend <= span.start or tstart >= span.end):
                prefix = "B-" if tstart <= span.start < tend else "I-"
                label = prefix + span.label
                break
        bio.append((tok, label, tstart, tend))
    return bio


def build_dataset(n_docs: int, raw_dir: Path, out_dir: Path) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    records = []
    logger.info(f"Генерируем {n_docs} документов...")
    for i in tqdm(range(n_docs)):
        gen = random.choice(GENERATORS)
        doc = gen()
        (raw_dir / f"doc_{i:05d}.txt").write_text(doc.text, encoding="utf-8")
        bio = doc_to_bio(doc)
        records.append({"id": i, "text": doc.text, "tokens": bio})

    out_path = out_dir / "dataset.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    logger.success(f"Готово: {out_path} ({len(records)} записей)")


if __name__ == "__main__":
    cfg = load_config()
    build_dataset(
        n_docs=cfg.data.n_documents,
        raw_dir=ROOT / cfg.data.raw_dir,
        out_dir=ROOT / cfg.data.output_dir,
    )
