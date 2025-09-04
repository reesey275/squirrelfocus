from __future__ import annotations

from pathlib import Path
from typing import Any

try:  # optional
    import yaml
    HAVE_YAML = True
except Exception:  # pragma: no cover
    yaml = None
    HAVE_YAML = False

CFG_PATH = Path('.squirrelfocus') / 'config.yaml'

DEFAULTS = {
    'journals_dir': 'journal_logs',
    'entry_glob': '**/*.md',
    'prefer_frontmatter': True,
    'trailer_keys': ['fix', 'why', 'change', 'proof', 'ref'],
    'summary_format': (
        '### CI Triage\n'
        '- **Fix:** {{fix}}\n'
        '- **Why:** {{why}}\n'
        '- **Change:** {{change}}\n'
        '- **Proof:** {{proof}}\n'
    ),
}

REQUIRED_KEYS: dict[str, type[Any]] = {
    'journals_dir': str,
    'entry_glob': str,
    'prefer_frontmatter': bool,
    'trailer_keys': list,
    'summary_format': str,
}


def load() -> tuple[dict[str, Any], list[str]]:
    """Return merged config and a list of problems."""
    data: dict[str, Any] = {}
    problems: list[str] = []
    if HAVE_YAML and CFG_PATH.exists():
        try:
            with CFG_PATH.open('r', encoding='utf-8') as fh:
                data = yaml.safe_load(fh) or {}
        except Exception as exc:
            problems.append(f'invalid YAML: {exc}')
            data = {}
    else:
        data = {}
    if not problems:
        for key, typ in REQUIRED_KEYS.items():
            if key not in data:
                problems.append(f"missing '{key}'")
            elif not isinstance(data[key], typ):
                problems.append(
                    f"'{key}' should be {typ.__name__}"
                )
    cfg = dict(DEFAULTS)
    cfg.update({k: v for k, v in data.items() if v is not None})
    return cfg, problems
