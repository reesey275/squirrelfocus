# CLI Reference

This page lists the commands and options provided by the `sf` tool.
Run `sf COMMAND --help` for additional details.

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
