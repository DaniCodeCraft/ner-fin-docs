"""Проверка токенизации: обе должны совпадать."""
from src.generation.build_dataset import _tokenize as tok_train
from src.models.predict import _tokenize as tok_infer

text = 'АО "Дельта", в лице Селезнева Кир Демьянович, сумма 1 269 рублей.'

print("=== build_dataset ===")
for t, s, e in tok_train(text):
    print(f"  {t!r:15} {s}-{e}")

print("\n=== predict ===")
for t, s, e in tok_infer(text):
    print(f"  {t!r:15} {s}-{e}")

t1 = [t for t, _, _ in tok_train(text)]
t2 = [t for t, _, _ in tok_infer(text)]
assert t1 == t2, f"Токенизации различаются!\n{t1}\n{t2}"
print("\n✅ Обе токенизации идентичны")