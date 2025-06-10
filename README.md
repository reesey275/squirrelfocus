# SquirrelFocus

Developer productivity and reflection toolkit. The goal of this project is to
provide a minimal command line interface and supporting documents that help
developers stay focused and keep short personal notes during a work session.

## Prerequisites

- Python 3.10 or newer
- [Poetry](https://python-poetry.org/) for dependency management. The
  `scripts/setup_poetry.sh` helper will install it automatically if it is
  missing.

## Installation

Clone the repository and run the helper script. The script installs Poetry if
needed and then installs the project dependencies:

```bash
./scripts/setup_poetry.sh
```

After the script completes run a quick greeting to verify the setup:

```bash
poetry run sf hello
```

If you prefer to manage Poetry yourself you can still run `poetry install`
manually. Skipping the project package keeps the environment lightweight:

```bash
poetry install --no-root
```

You can achieve the same behavior permanently by setting
`package-mode = false` in your Poetry configuration. When skipping the
package installation, the `sf` entry point is not available. Invoke the
CLI module directly instead:

```bash
poetry run python -m cli hello
```

If you do install the package (or enable package mode) the original
entry point will work as before:

```bash
poetry run sf hello
```

## Configuration

Some commands rely on external services such as the OpenAI API or a Discord
webhook. Copy `.env.example` to `.env` and supply your credentials before
running those features. The file includes placeholders for the following
variables:

```bash
OPENAI_API_KEY=your-api-key
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/... 
```

## Running the CLI

After installing the project you can invoke the CLI using Poetry's `run`
command:

```bash
poetry run sf hello
```

The default command prints a friendly greeting. Use `drop` to store a note and
`show` to display recent entries:

```bash
poetry run sf drop "Fixed a tricky bug"
poetry run sf show 3
```

## Development

Common development tasks can be run through Poetry:

```bash
# Format and lint the code
poetry run black .
poetry run ruff .

# Run the test suite
poetry run pytest
```

## License

MIT License © 2024. See [LICENSE](LICENSE) for full text.
