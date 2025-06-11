# CLI Reference

This file lists the available commands, their options and examples.

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
```

## show [COUNT]

Display the last `COUNT` entries from the log. The default is `5`.

```bash
poetry run sf show 3
poetry run sf show -1  # fails, COUNT must be greater than 0
```

## ask QUESTION

Create a work item from `QUESTION` using OpenAI. The CLI help calls
`ask` to create tasks. Set the `OPENAI_API_KEY` environment variable
before running this command.

```bash
poetry run sf ask "How do I plan tomorrow?"
OPENAI_API_KEY= poetry run sf ask "anything"  # prints an error
```
