"""PyTorch Dataset для NER: word-level BIO → subword-разметка."""
from pathlib import Path

import torch
from torch.utils.data import Dataset
from transformers import PreTrainedTokenizerFast


def load_jsonl(path: str | Path) -> list[dict]:
    import json
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    return records


class NERDataset(Dataset):
    """
    Каждый пример: {"tokens": [(token, label), ...], "text": str}
    Токенизируем слова по отдельности и склеиваем с [CLS]/[SEP],
    сохраняя выравнивание меток.
    """

    def __init__(
        self,
        records: list[dict],
        tokenizer: PreTrainedTokenizerFast,
        label2id: dict[str, int],
        max_length: int = 256,
    ):
        self.records = records
        self.tokenizer = tokenizer
        self.label2id = label2id
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> dict:
        rec = self.records[idx]
        words = [t[0] for t in rec["tokens"]]
        word_labels = [self.label2id[t[1]] for t in rec["tokens"]]

        input_ids = [self.tokenizer.cls_token_id]
        label_ids = [-100]  # [CLS]
        attention_mask = [1]
        token_type_ids = [0]

        for word, label in zip(words, word_labels):
            sub_ids = self.tokenizer.encode(word, add_special_tokens=False)
            if not sub_ids:
                continue
            # Первый subword — реальная метка, остальные — -100
            input_ids.extend(sub_ids)
            label_ids.append(label)
            label_ids.extend([-100] * (len(sub_ids) - 1))
            attention_mask.extend([1] * len(sub_ids))
            token_type_ids.extend([0] * len(sub_ids))

        input_ids.append(self.tokenizer.sep_token_id)
        label_ids.append(-100)
        attention_mask.append(1)
        token_type_ids.append(0)

        # Обрезка / паддинг
        if len(input_ids) > self.max_length:
            input_ids = input_ids[: self.max_length]
            label_ids = label_ids[: self.max_length]
            attention_mask = attention_mask[: self.max_length]
            token_type_ids = token_type_ids[: self.max_length]

        pad_len = self.max_length - len(input_ids)
        input_ids += [self.tokenizer.pad_token_id] * pad_len
        label_ids += [-100] * pad_len
        attention_mask += [0] * pad_len
        token_type_ids += [0] * pad_len

        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
            "token_type_ids": torch.tensor(token_type_ids, dtype=torch.long),
            "labels": torch.tensor(label_ids, dtype=torch.long),
        }


def train_val_test_split(records: list[dict], val: float, test: float, seed: int = 42):
    import random
    random.seed(seed)
    random.shuffle(records)
    n = len(records)
    n_test = int(n * test)
    n_val = int(n * val)
    return (
        records[n_test + n_val:],
        records[n_test: n_test + n_val],
        records[:n_test],
    )