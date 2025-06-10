# SquirrelFocus

Developer productivity and reflection toolkit. The goal of this project is to
provide a minimal command line interface and supporting documents that help
developers stay focused and keep short personal notes during a work session.

## Prerequisites

- Python 3.10 or newer
- [Poetry](https://python-poetry.org/) for dependency management

## Installation

Clone the repository and install the dependencies using Poetry. Skipping the
project package keeps the environment lightweight:

```bash
poetry install --no-root
```

You can achieve the same behavior permanently by setting
`package-mode = false` in your Poetry configuration.

## Running the CLI

After installing the project you can invoke the CLI using Poetry's `run` command:

```bash
poetry run sf hello
```

The default command prints a friendly greeting. Additional subcommands will be
added over time.

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

This project is licensed under the [MIT License](LICENSE).
