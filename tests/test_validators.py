"""Тесты валидаторов ИНН/ОГРН/БИК с контрольными суммами."""
from src.generation import generators as G
from src.rules.validators import validate_bik, validate_inn, validate_ogrn


def test_inn_length():
    for _ in range(50):
        inn = G.gen_inn()
        assert len(inn) in (10, 12)
        assert inn.isdigit()


def test_inn_checksum():
    for _ in range(50):
        assert validate_inn(G.gen_inn()), "Сгенерированный ИНН должен быть валидным"


def test_inn_reject_bad():
    assert not validate_inn("1234567890")
    assert not validate_inn("abc")
    assert not validate_inn("123")


def test_ogrn_checksum():
    for _ in range(50):
        assert validate_ogrn(G.gen_ogrn())


def test_bik_prefix():
    for _ in range(20):
        bik = G.gen_bik()
        assert bik.startswith("04")
        assert len(bik) == 9
        assert validate_bik(bik)


def test_org_format():
    for _ in range(20):
        org = G.gen_org()
        assert '"' in org  # ООО "Название"


def test_money_currency():
    for _ in range(20):
        money = G.gen_money()
        assert any(c in money for c in ("руб", "₽", "RUB"))