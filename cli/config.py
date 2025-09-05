from __future__ import annotations

from pathlib import Path
from typing import Any  # for optional yaml support

import typer

try:  # optional
    import yaml as _yaml

    yaml: Any = _yaml
    HAVE_YAML = True
except Exception:  # pragma: no cover
    yaml = None
    HAVE_YAML = False

CFG_PATH = Path(".squirrelfocus") / "config.yaml"

DEFAULTS: dict[str, Any] = {
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

REQUIRED_TYPES: dict[str, type] = {
    "journals_dir": str,
}


def read_cfg() -> dict[str, Any] | None:
    """Return raw config or None if file missing."""
    if not HAVE_YAML or not CFG_PATH.exists():
        return None
    try:
        with CFG_PATH.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except yaml.YAMLError as err:
        typer.echo(f"Failed to parse config: {err}")
        raise typer.Exit(code=1)
    except OSError as err:
        typer.echo(f"Could not read config: {err}")
        raise typer.Exit(code=1)


def load_cfg(data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return configuration merged with defaults."""
    if data is None:
        data = read_cfg() or {}
    cfg: dict[str, Any] = dict(DEFAULTS)
    cfg.update({k: v for k, v in data.items() if v is not None})
    return cfg


def _example_line(key: str, value: Any) -> str:
    if isinstance(value, list):
        inner = ", ".join(str(v) for v in value)
        return f"{key}: [{inner}]"
    return f"{key}: {value}"


def validate(data: dict[str, Any] | None) -> None:
    """Validate raw config data."""
    if data is None:
        return
    for key, typ in REQUIRED_TYPES.items():
        if key not in data:
            typer.echo(f"Config missing '{key}'.")
            typer.echo(f"Example: {_example_line(key, DEFAULTS[key])}")
            raise typer.Exit(code=1)
        if not isinstance(data[key], typ):
            typer.echo(f"Config key '{key}' malformed.")
            defval = DEFAULTS.get(key, typ())
            typer.echo(f"Example: {_example_line(key, defval)}")
            raise typer.Exit(code=1)
    for key, defval in DEFAULTS.items():
        if key in data and key not in REQUIRED_TYPES:
            if not isinstance(data[key], type(defval)):
                typer.echo(f"Config key '{key}' malformed.")
                typer.echo(f"Example: {_example_line(key, defval)}")
                raise typer.Exit(code=1)
            if key == "trailer_keys" and not all(
                isinstance(v, str) for v in data[key]
            ):
                typer.echo("Config key 'trailer_keys' malformed.")
                typer.echo(f"Example: {_example_line(key, defval)}")
                raise typer.Exit(code=1)
