# SquirrelFocus

[![CI][ci-badge]][ci-url]
[![CI Summary][ci-summary-badge]][ci-summary-url]

Developer productivity and reflection toolkit. The goal of this project is to
provide a minimal command line interface and supporting documents that help
developers stay focused and keep short personal notes during a work session.

## Workflow

Workflow: feature → development → main (release, tag).

## Branching and CI

All work starts on short-lived feature branches that merge into `development`.
Release branches target `main`. Commits use a commit-msg hook to append
SquirrelFocus trailers, enabling workflows to summarize the latest
`journal_logs` entry. CI runs on pushes and pull requests for `development`
and `main`, and merging to `main` appends a line to `MILESTONE_LOG.md`.
The `main` and `development` branches are protected. Merges require pull
requests and passing checks.
Run `bash scripts/install_hooks.sh` to install the hook on Unix-like
systems. Windows users can run `pwsh scripts/install_hooks.ps1` to set up
the hook.

## Prerequisites

- Python 3.10 or newer
- [Poetry](https://python-poetry.org/) for dependency management. The
  `setup.sh` helper will install it automatically if it is missing.

## Installation

Clone the repository and run the helper script. The script installs Poetry if
needed and then installs the project dependencies:

```bash
./setup.sh
```

After the script completes run a quick greeting to verify the setup:

```bash
poetry run sf hello
```

If the setup complains about lock-file changes run `poetry lock` and try
again. See [docs/troubleshooting.md](docs/troubleshooting.md) for details.

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

## Quick Start (CLI)

```bash
poetry run sf init --with-hook --with-workflows
poetry run sf new --fix "parser bug"
poetry run sf preview
poetry run sf doctor
```

Windows users can install the commit hook:

```powershell
pwsh scripts/install_hooks.ps1
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

GitHub Actions use this key as a secret. Add `OPENAI_API_KEY` to the
repository secrets so the automated workflows can run correctly.

## Running the CLI

After installing the project you can invoke the CLI using Poetry's `run`
command:

```bash
poetry run sf hello
```
See [docs/cli_reference.md](docs/cli_reference.md) for command details.

Shell completions are available with `--install-completion` and can be
inspected with `--show-completion`.

The default command prints a friendly greeting. Use `drop` to store a note and
`show` to display recent entries. The `ask` command requires an
`OPENAI_API_KEY` environment variable and turns a question into a work item:

```bash
poetry run sf drop "Fixed a tricky bug"
poetry run sf show 3
poetry run sf ask "How do I plan tomorrow?"
```

## Codex Journal

Daily reflections live in [codex/journal](codex/journal). Each entry lists
metadata such as date, tags and a short summary in a YAML header.

See the Codex goals document
[Codex goals](codex/goals/expected_codex_behavior.md)
for how `sf ask` converts prompts into tasks.

## Additional Documentation

- [Vision](docs/vision.md) outlines the goals and value of the project.
- [Security Overview](docs/security-overview.md) explains data handling.

## Development

Common development tasks can be run through Poetry:

```bash
# Format and lint the code
poetry run black .
poetry run ruff check .

# Run the test suite
poetry run pytest
```

## Reusable CI Summary

Use the reusable workflow to generate summaries in other workflows:

```yaml
jobs:
  summarize:
    uses: ./.github/workflows/sf-summary.yml
    with:
      title: "Example title"
    secrets: inherit
```

The job accepts a `title` describing the context for the summary.

## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md) for common errors.

## License

MIT License © 2024–2025. See [LICENSE](LICENSE) for full text.

[ci-badge]: https://img.shields.io/badge/CI-main-blue
[ci-url]: https://github.com/squirrelfocus/squirrelfocus/actions/workflows/ci.yml?query=branch%3Awork
[ci-summary-badge]: https://img.shields.io/badge/CI_summary-main-blue
[ci-summary-url]: https://github.com/squirrelfocus/squirrelfocus/actions/workflows/ci-summary.yml?query=branch%3Awork

