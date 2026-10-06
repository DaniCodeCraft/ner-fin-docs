import random
import string
from datetime import date, timedelta

from faker import Faker

from src.rules.validators import validate_inn, validate_ogrn

fake = Faker("ru_RU")
Faker.seed(42)
random.seed(42)

COMPANY_FORMS = ["ООО", "АО", "ПАО", "ЗАО"]   # убрали ИП — теперь это отдельный тип
COMPANY_NAMES = [
    "Ромашка", "Вектор", "Гарант", "СтройИнвест", "АльфаТрейд",
    "ТехноСервис", "ФинЭксперт", "КапиталГрупп", "Меркурий",
    "Орион", "Дельта", "Прогресс", "Рубин", "Сатурн",
]


def gen_org() -> str:
    """Юридическое лицо: ООО/АО/ПАО/ЗАО «Название»."""
    form = random.choice(COMPANY_FORMS)
    name = random.choice(COMPANY_NAMES)
    return f'{form} "{name}"'


def gen_ip() -> str:
    """Индивидуальный предприниматель. Отдельный генератор — 
    при желании можно размечать как PERSON или как отдельный тип."""
    return f"ИП {fake.last_name()} {fake.first_name()[0]}.{fake.middle_name()[0]}."


def gen_person() -> str:
    return f"{fake.last_name()} {fake.first_name()} {fake.middle_name()}"


def gen_inn() -> str:
    for _ in range(1000):
        length = random.choice([10, 12])
        if length == 10:
            digits = [random.randint(0, 9) for _ in range(9)]
            weights = [2, 4, 10, 3, 5, 9, 4, 6, 8]
            check = sum(d * w for d, w in zip(digits, weights)) % 11 % 10
            inn = "".join(map(str, digits)) + str(check)
        else:
            digits = [random.randint(0, 9) for _ in range(11)]
            w11 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
            n11 = sum(d * w for d, w in zip(digits, w11)) % 11 % 10
            w12 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
            n12 = sum(d * w for d, w in zip(digits, w12)) % 11 % 10
            inn = "".join(map(str, digits)) + str(n11) + str(n12)
        if validate_inn(inn):
            return inn
    raise RuntimeError("Не удалось сгенерировать ИНН")


def gen_ogrn() -> str:
    for _ in range(1000):
        length = random.choice([13, 15])
        body_len = length - 1
        body = "".join(random.choices("0123456789", k=body_len))
        div = 11 if length == 13 else 13
        check = int(body) % div % 10
        ogrn = body + str(check)
        if validate_ogrn(ogrn):
            return ogrn
    raise RuntimeError("Не удалось сгенерировать ОГРН")


def gen_kpp() -> str:
    return "".join(random.choices("0123456789", k=9))


def gen_bik() -> str:
    return "04" + "".join(random.choices("0123456789", k=7))


def gen_account() -> str:
    return "".join(random.choices("0123456789", k=20))


def gen_contract() -> str:
    num = random.randint(1, 9999)
    year = random.randint(2020, 2025)
    sep = random.choice(["/", "-", "N"])
    return f"{num}{sep}{year}"


def gen_money() -> str:
    amount = random.choice([
        random.randint(100, 9999),
        random.randint(10_000, 999_999),
        random.randint(1_000_000, 100_000_000),
    ])
    formatted = f"{amount:,}".replace(",", " ")
    currency = random.choice(["руб.", "рублей", "₽", "RUB"])
    return f"{formatted} {currency}"


def gen_date() -> str:
    d = date.today() - timedelta(days=random.randint(0, 1500))
    fmt = random.choice(["%d.%m.%Y", "%d.%m.%y", "%Y-%m-%d"])
    return d.strftime(fmt)