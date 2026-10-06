"""CLI: ner-fin predict <file>|--stdin  |  train  |  gen-data  |  evaluate."""
import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.models.predict import NERPredictor

app = typer.Typer(help="NER для финансовых документов", no_args_is_help=True)
console = Console()


def _read_stdin() -> str:
    """Читает stdin как UTF-8, кроссплатформенно (PS, CMD, bash)."""
    data = sys.stdin.buffer.read()
    if not data:
        return ""
    for enc in ("utf-8", "utf-8-sig", "cp1251", "cp866"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


@app.command()
def predict(
    file: Path = typer.Argument(None, help="Путь к TXT. Не указывай, если используешь --stdin."),
    model_dir: Path = typer.Option(None, "--model", "-m"),
    json_out: bool = typer.Option(False, "--json", help="Вывод в JSON"),
    stdin: bool = typer.Option(False, "--stdin", help="Читать текст из stdin"),
):
    """Извлечь сущности из документа."""
    if stdin:
        text = _read_stdin()
    elif file and str(file) == "-":
        text = _read_stdin()
    elif file:
        if not file.exists():
            console.print(f"[red]Файл не найден: {file}[/red]")
            raise typer.Exit(code=1)
        text = file.read_text(encoding="utf-8")
    else:
        console.print("[red]Укажи файл или --stdin[/red]")
        raise typer.Exit(code=1)

    if not text.strip():
        console.print("[yellow]Пустой ввод — нечего обрабатывать.[/yellow]")
        if json_out:
            print("[]")
        raise typer.Exit(code=1)

    predictor = NERPredictor(model_dir=model_dir)
    entities = predictor.predict(text)

    if json_out:
        print(json.dumps([e.__dict__ for e in entities], ensure_ascii=False, indent=2))
        return

    console.print(Panel(text[:500] + ("..." if len(text) > 500 else ""), title="Документ"))
    table = Table(title=f"Найдено сущностей: {len(entities)}")
    table.add_column("Тип", style="cyan")
    table.add_column("Значение", style="green")
    table.add_column("Позиция", style="dim")
    table.add_column("Score", style="yellow")
    for e in entities:
        table.add_row(e.label, e.text, f"{e.start}-{e.end}", f"{e.score:.3f}")
    console.print(table)


@app.command()
def gen_data():
    """Сгенерировать датасет."""
    from src.generation.build_dataset import build_dataset
    from src.config import load_config, ROOT
    cfg = load_config()
    build_dataset(cfg.data.n_documents, ROOT / cfg.data.raw_dir, ROOT / cfg.data.output_dir)


@app.command()
def train():
    """Обучить модель."""
    from src.models.train import main as train_main
    train_main()


@app.command()
def evaluate():
    """Оценить модель на тесте."""
    from src.models.evaluate import main as eval_main
    eval_main()


if __name__ == "__main__":
    app()