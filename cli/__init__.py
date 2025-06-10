from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer

app = typer.Typer(
    help=(
        "SquirrelFocus command line interface. Use 'drop' to add notes and 'show'"
        " to view them. Entries are stored in ~/.squirrelfocus/acornlog.txt"
    )
)

LOG_DIR = Path.home() / ".squirrelfocus"
LOG_FILE = LOG_DIR / "acornlog.txt"


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
def show(count: int = 5) -> None:
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
def hello(name: str = "world"):
    """Say hello to NAME."""
    typer.echo(f"Hello {name}!")


if __name__ == "__main__":
    app()
