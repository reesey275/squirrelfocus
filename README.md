# SquirrelFocus

Developer productivity and reflection toolkit. The goal of this project is to
provide a minimal command line interface and supporting documents that help
developers stay focused and keep short personal notes during a work session.

## Prerequisites

- Python 3.10 or newer
- [Poetry](https://python-poetry.org/) for dependency management

## Installation

Clone the repository and install the dependencies using Poetry:

```bash
poetry install
```

## Running the CLI

After installing the project you can invoke the CLI directly:

```bash
poetry run squirrelfocus hello
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
pytest
```

## License

This project is licensed under the [MIT License](LICENSE).
