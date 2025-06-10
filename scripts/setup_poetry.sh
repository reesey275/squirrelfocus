#!/usr/bin/env bash
set -e

# Ensure we're in repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

# Create a minimal pyproject if one does not exist
if [ ! -f pyproject.toml ]; then
    cat > pyproject.toml <<'PYEOF'
[tool.poetry]
name = "squirrelfocus"
version = "0.1.0"
description = ""
authors = []

[tool.poetry.dependencies]
python = "^3.10"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
PYEOF
fi

# Install Poetry if it is not already available
if ! command -v poetry >/dev/null 2>&1; then
    echo "Poetry not found. Installing..." >&2
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

poetry install

