from __future__ import annotations

from datetime import datetime
from pathlib import Path
import os

import openai
import typer

app = typer.Typer(
    help=(
        "SquirrelFocus CLI. Use 'drop' to add notes, "
        "'show' to view them, 'ask' to create tasks. "
        "Entries are stored in ~/.squirrelfocus/acornlog.txt"
    )
)

LOG_DIR = Path.home() / ".squirrelfocus"
LOG_FILE = LOG_DIR / "acornlog.txt"
_BASE_PATH = Path(__file__).resolve().parents[1]
PROMPT_FILE = _BASE_PATH / "codex" / "prompts" / "work_item_generator.md"


def load_prompt() -> str:
    """Return the Codex work item prompt."""
    return PROMPT_FILE.read_text(encoding="utf-8")


def ensure_log_dir() -> None:
    """Create the log directory if it does not exist."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)


@app.command()
def drop(text: str) -> None:
    """Append TEXT with a timestamp to ~/.squirrelfocus/acornlog.txt."""
    ensure_log_dir()
    timestamp = datetime.now().isoformat()
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(f"{timestamp} {text}\n")


@app.command()
def show(
    count: int = typer.Argument(
        5, min=1, help="Number of log lines to display"
    )
) -> None:
    """Print the last COUNT lines from ~/.squirrelfocus/acornlog.txt."""
    ensure_log_dir()
    if not LOG_FILE.exists():
        typer.echo("No log entries found.")
        raise typer.Exit()

    with LOG_FILE.open("r", encoding="utf-8") as fh:
        lines = fh.readlines()

    for line in lines[-count:]:
        typer.echo(line.rstrip())


@app.command()
def ask(question: str) -> None:
    """Send QUESTION to Codex and print the work item."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        typer.echo("OPENAI_API_KEY not set")
        raise typer.Exit(code=1)
    client = openai.OpenAI(api_key=api_key)
    prompt = load_prompt()
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": question},
    ]
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
    except Exception as exc:  # pragma: no cover - network issues
        typer.echo(f"OpenAI error: {exc}")
        raise typer.Exit(code=1)
    item = resp.choices[0].message.content.strip()
    typer.echo(item)


@app.command()
def hello(name: str = typer.Argument("world")):
    """Say hello to NAME."""
    typer.echo(f"Hello {name}!")


if __name__ == "__main__":
    app()
