from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import os
import shutil
import subprocess
import sys

import click
import openai
import typer

try:  # optional
    import yaml

    HAVE_YAML = True
except Exception:  # pragma: no cover
    yaml = None
    HAVE_YAML = False

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

CFG_PATH = Path(".squirrelfocus") / "config.yaml"
DEF_CFG = {
    "journals_dir": "journal_logs",
    "trailer_keys": ["fix", "why", "change", "proof", "ref"],
    "summary_format": (
        "### CI Triage\n"
        "- **Fix:** {{fix}}\n"
        "- **Why:** {{why}}\n"
        "- **Change:** {{change}}\n"
        "- **Proof:** {{proof}}\n"
    ),
}


def load_prompt() -> str:
    """Return the Codex work item prompt."""
    return PROMPT_FILE.read_text(encoding="utf-8")


def ensure_log_dir() -> None:
    """Create the log directory if it does not exist."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_cfg() -> dict:
    """Return configuration merged with defaults."""
    if HAVE_YAML and CFG_PATH.exists():
        try:
            with CFG_PATH.open("r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            out = dict(DEF_CFG)
            out.update({k: v for k, v in data.items() if v is not None})
            return out
        except Exception:
            pass
    return dict(DEF_CFG)


def parse_frontmatter(text: str) -> dict:
    """Return front matter dict parsed from TEXT."""
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm_text = parts[1]
    if HAVE_YAML:
        try:
            return yaml.safe_load(fm_text) or {}
        except Exception:
            return {}
    data: dict = {}
    section: str | None = None
    for ln in fm_text.splitlines():
        if ln.strip().endswith(":") and not ln.startswith(" "):
            section = ln.strip()[:-1]
            data[section] = {}
            continue
        if ":" in ln:
            k, v = ln.split(":", 1)
            if section:
                data[section][k.strip()] = v.strip().strip('"').strip("'")
            else:
                data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def slugify(text: str) -> str:
    """Return a filesystem-safe slug for TEXT."""
    chars = [ch.lower() if ch.isalnum() else " " for ch in text]
    return "-".join("".join(chars).split())


@app.command()
def init(
    with_workflows: bool = typer.Option(
        False, "--with-workflows", help="Copy CI summary workflow."
    ),
    with_hook: bool = typer.Option(
        False,
        "--with-hook",
        help="Install commit hook (.sh on Unix, .ps1 on Windows).",
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite existing files."
    ),
    journals_dir: str = typer.Option(
        "journal_logs", "--journals-dir", help="Journal directory."
    ),
) -> None:
    """Guided setup.

    Options:
      --with-workflows    Copy CI workflow.
      --with-hook         Run install_hooks.sh (Unix) or install_hooks.ps1
                          (Windows).
      --force             Allow overwrites.
      --journals-dir TEXT  Journal directory name.
    """
    created: list[Path] = []

    cfg_src = _BASE_PATH / ".squirrelfocus" / "config.yaml"
    cfg_dst = CFG_PATH
    if force or not cfg_dst.exists():
        cfg_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(cfg_src, cfg_dst)
        created.append(cfg_dst)

    cfg = load_cfg()
    cfg["journals_dir"] = journals_dir
    if HAVE_YAML:
        cfg_dst.write_text(
            yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8"
        )
    else:
        cfg_dst.write_text(f"journals_dir: {journals_dir}\n", encoding="utf-8")

    jdir = Path(journals_dir)
    if not jdir.exists():
        jdir.mkdir(parents=True)
        created.append(jdir)

    tpl_src = _BASE_PATH / "templates" / "sqf_fix.md"
    tpl_dst = Path("templates") / "sqf_fix.md"
    if force or not tpl_dst.exists():
        tpl_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(tpl_src, tpl_dst)
        created.append(tpl_dst)

    emit_src = _BASE_PATH / "scripts" / "sqf_emit.py"
    emit_dst = Path("scripts") / "sqf_emit.py"
    if force or not emit_dst.exists():
        emit_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(emit_src, emit_dst)
        created.append(emit_dst)

    if with_workflows:
        wf_src = _BASE_PATH / ".github" / "workflows" / "ci-summary.yml"
        wf_dst = Path(".github") / "workflows" / "ci-summary.yml"
        if force or not wf_dst.exists():
            wf_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(wf_src, wf_dst)
            created.append(wf_dst)

    if with_hook:
        sh_hook = Path("scripts/install_hooks.sh")
        ps1_hook = Path("scripts/install_hooks.ps1")
        if sh_hook.exists():
            subprocess.run(["bash", str(sh_hook)], check=False)
        elif ps1_hook.exists() and sys.platform.startswith("win"):
            subprocess.run(
                [
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ps1_hook),
                ],
                check=False,
            )

    for path in created:
        typer.echo(f"created {path}")


@app.command()
def new(
    fix: str = typer.Option("", "--fix", help="Fix trailer."),
    why: str = typer.Option("", "--why", help="Why trailer."),
    change: str = typer.Option("", "--change", help="Change trailer."),
    proof: str = typer.Option("", "--proof", help="Proof trailer."),
    ref: str = typer.Option("", "--ref", help="Reference trailer."),
) -> None:
    """Create a journal entry from template.

    Options map to commit trailers.
    """
    cfg = load_cfg()
    jdir = Path(cfg.get("journals_dir", "journal_logs"))
    jdir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().date().isoformat()
    slug = slugify(fix) or "entry"
    path = jdir / f"{today}-{slug}.md"

    tpl_path = Path("templates") / "sqf_fix.md"
    body = ""
    if tpl_path.exists():
        text = tpl_path.read_text(encoding="utf-8")
        if text.startswith("---"):
            body = text.split("---", 2)[2].lstrip()
        else:
            body = text

    fm = {"trailers": {}}
    for key, val in {
        "fix": fix,
        "why": why,
        "change": change,
        "proof": proof,
        "ref": ref,
    }.items():
        if val:
            fm["trailers"][key] = val

    if HAVE_YAML:
        fm_text = yaml.safe_dump(fm, sort_keys=False)
    else:
        lines = ["trailers:"]
        for k, v in fm["trailers"].items():
            lines.append(f'  {k}: "{v}"')
        fm_text = "\n".join(lines) + "\n"

    content = f"---\n{fm_text}---\n\n{body}"
    path.write_text(content, encoding="utf-8")
    typer.echo(str(path))


@app.command()
def preview() -> None:
    """Render the CI summary for the latest entry."""
    script = Path("scripts") / "sqf_emit.py"
    if not script.exists():
        typer.echo("No emitter script found.")
        raise typer.Exit()
    result = subprocess.run(
        [sys.executable, str(script), "summary"],
        capture_output=True,
        text=True,
    )
    msg = result.stdout.strip()
    if msg:
        typer.echo(msg)
    else:
        typer.echo("No journal entry found.")


@app.command()
def doctor() -> None:
    """Check installation health."""
    fail = False
    typer.echo(f"Python: {sys.version.split()[0]}")
    try:
        import click

        typer.echo(f"click {click.__version__}, typer {typer.__version__}")
    except Exception as exc:  # pragma: no cover
        typer.echo(f"click/typer error: {exc}")
        fail = True
    try:
        import yaml as _  # noqa: F401

        typer.echo("pyyaml: present")
    except Exception:
        typer.echo("pyyaml: missing (pip install pyyaml)")
    if CFG_PATH.exists():
        typer.echo("config: ok")
    else:
        typer.echo("config: missing (run 'sf init')")
        fail = True
    cfg = load_cfg()
    jdir = Path(cfg.get("journals_dir", "journal_logs"))
    if jdir.exists() and os.access(jdir, os.W_OK):
        typer.echo("journals_dir: ok")
    else:
        typer.echo(f"journals_dir: missing or not writable ({jdir})")
        fail = True
    emit = Path("scripts") / "sqf_emit.py"
    if emit.exists():
        typer.echo("sqf_emit.py: ok")
    else:
        typer.echo("sqf_emit.py: missing (run 'sf init')")
        fail = True
    hook = Path(".git/hooks/commit-msg")
    if hook.exists():
        typer.echo("commit hook: ok")
    else:
        typer.echo(
            "commit hook: missing (run 'scripts/install_hooks.sh' on Unix or "
            "'scripts/install_hooks.ps1' on Windows)"
        )
        fail = True
    raise typer.Exit(code=1 if fail else 0)


@app.command()
def report(
    since: int = typer.Option(
        30, "--since", min=0, help="Days back to include."
    ),
    fmt: str = typer.Option(
        "md",
        "--format",
        parser=lambda v: click.Choice(
            ["md", "txt"], case_sensitive=False
        ).convert(v, None, None),
        help="Output format: md or txt.",
    ),
) -> None:
    """Aggregate journal entries.

    Options:
      --since DAYS   Include entries from the last DAYS days.
      --format TEXT  Output format: md or txt.
    """
    cfg = load_cfg()
    jdir = Path(cfg.get("journals_dir", "journal_logs"))
    if not jdir.exists():
        typer.echo("No entries found.")
        raise typer.Exit(code=1)
    cutoff = datetime.now().date() - timedelta(days=since)
    entries: list[tuple[datetime, str, dict]] = []
    for path in sorted(jdir.glob("**/*.md")):
        fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        date_str = fm.get("created_at")
        if not date_str:
            continue
        try:
            dt = datetime.fromisoformat(str(date_str)).date()
        except Exception:
            continue
        if dt < cutoff:
            continue
        title = fm.get("title", path.stem)
        trailers = fm.get("trailers", {}) or {}
        entries.append((dt, title, trailers))
    if not entries:
        typer.echo("No entries found.")
        raise typer.Exit(code=1)
    lines: list[str] = []
    for dt, title, trailers in sorted(entries):
        header = f"{dt} {title}"
        lines.append(f"### {header}" if fmt == "md" else header)
        for k, v in trailers.items():
            prefix = "- " if fmt == "md" else ""
            lines.append(f"{prefix}{k}: {v}")
        lines.append("")
    typer.echo("\n".join(lines).rstrip())


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
def add(a: float, b: float) -> None:
    """Print the sum of A and B."""
    typer.echo(a + b)


@app.command()
def subtract(a: float, b: float) -> None:
    """Print the result of A minus B."""
    typer.echo(a - b)


@app.command()
def multiply(a: float, b: float) -> None:
    """Print the product of A and B."""
    typer.echo(a * b)


@app.command()
def divide(a: float, b: float) -> None:
    """Print the result of A divided by B."""
    if b == 0:
        typer.echo("Cannot divide by zero.")
        raise typer.Exit(code=1)
    typer.echo(a / b)


@app.command()
def hello(name: str = typer.Argument("world")):
    """Say hello to NAME."""
    typer.echo(f"Hello {name}!")


if __name__ == "__main__":
    app()
