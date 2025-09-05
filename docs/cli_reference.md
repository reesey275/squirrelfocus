# CLI Reference

This page lists the commands and options provided by the `sf` tool.
Run `sf COMMAND --help` for additional details.

## Global options

The CLI offers a few flags in addition to its subcommands:

- `--install-completion` installs shell completion for the current shell.
- `--show-completion` prints the completion script to standard output.
- `--help` displays usage information for the selected command.

## Configuration

Settings are read from `.squirrelfocus/config.yaml`.

Required keys:

- `journals_dir` (str): path for journal entries.

Optional keys:

- `trailer_keys` (list[str]): commit trailer names. Defaults to
  `[fix, why, change, proof, ref]`. Elements must be strings.
- `summary_format` (str): preview template. Defaults to a multi-line
  summary.

Unknown keys are ignored. Missing or malformed keys show an example
with the expected type.

## init

Set up the current directory for SquirrelFocus.

```bash
poetry run sf init
poetry run sf init --with-workflows --with-hook
```

Options:

- `--with-workflows` copy the CI summary workflow.
- `--with-hook` install commit hooks.
- `--force` overwrite existing files.
- `--journals-dir TEXT` name of the journals directory.

## new [OPTIONS]

Create a journal entry from the default template. Options map to commit
trailers.

```bash
poetry run sf new --fix bug --why "to reproduce"
```

Options:

- `--fix TEXT` Describe the bug or issue addressed.
- `--why TEXT` Explain the motivation for the change.
- `--change TEXT` Summarize what was modified.
- `--proof TEXT` Describe how the change was verified.
- `--ref TEXT` Link to related issues or resources.

## preview

Render the latest journal entry. The default format is `summary`. Supported
formats are listed in `PREVIEW_FORMATS`.

```bash
poetry run sf preview --format summary
poetry run sf preview --format trailers
```

Options:

- `--format FORMAT` choose output type (`PREVIEW_FORMATS`; default `summary`).

## doctor

Check installation health and return a non-zero exit code on problems.

```bash
poetry run sf doctor
```

## report

List journal entry paths prior to today.

```bash
poetry run sf report
```

## hello [NAME]

Print a friendly greeting. `NAME` defaults to `"world"`.

```bash
poetry run sf hello
poetry run sf hello squirrels
```

## drop TEXT

Append `TEXT` to `~/.squirrelfocus/acornlog.txt` with a timestamp.

```bash
poetry run sf drop "Fixed a tricky bug"
poetry run sf drop "Wrote tests"
```

## show [COUNT]

Display the last `COUNT` log entries. The default is `5`.
`COUNT` must be greater than `0`.

```bash
poetry run sf show      # uses default of 5
poetry run sf show 3
poetry run sf show -1   # fails with an error
```

## ask QUESTION

Create a work item from `QUESTION` using OpenAI.
Set the `OPENAI_API_KEY` environment variable first.

```bash
poetry run sf ask "How do I plan tomorrow?"
OPENAI_API_KEY= poetry run sf ask "anything"  # prints an error
```

## add A B

Print the sum of `A` and `B`.

```bash
poetry run sf add 2 3
poetry run sf add 1 2.5
```

## subtract A B

Print the result of `A - B`.

```bash
poetry run sf subtract 5 2
```

## multiply A B

Print the product of `A` and `B`.

```bash
poetry run sf multiply 3 4
```

## divide A B

Print the result of `A / B`. Fails if `B` is `0`.

```bash
poetry run sf divide 6 3
poetry run sf divide 1 0  # prints an error
```
