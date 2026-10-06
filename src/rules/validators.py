"""Валидаторы и генераторы реквизитов РФ с контрольными суммами."""


def validate_inn(inn: str) -> bool:
    if not inn.isdigit() or len(inn) not in (10, 12):
        return False

    def _checksum(digits: list[int], weights: list[int]) -> int:
        return sum(d * w for d, w in zip(digits, weights)) % 11 % 10

    digits = [int(c) for c in inn]
    if len(inn) == 10:
        return digits[9] == _checksum(digits, [2, 4, 10, 3, 5, 9, 4, 6, 8])
    n11 = _checksum(digits, [7, 2, 4, 10, 3, 5, 9, 4, 6, 8])
    n12 = _checksum(digits, [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8])
    return digits[10] == n11 and digits[11] == n12


def validate_ogrn(ogrn: str) -> bool:
    if not ogrn.isdigit() or len(ogrn) not in (13, 15):
        return False
    div = 11 if len(ogrn) == 13 else 13
    body = int(ogrn[:-1])
    check = body % div % 10
    return check == int(ogrn[-1])


def validate_bik(bik: str) -> bool:
    return bik.isdigit() and len(bik) == 9 and bik[:2] == "04"


def validate_kpp(kpp: str) -> bool:
    return len(kpp) == 9 and kpp[0].isdigit() and kpp[1].isdigit()