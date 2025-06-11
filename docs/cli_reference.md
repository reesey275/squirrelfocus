# CLI Reference

This file lists the available commands and examples.

## hello [NAME]

Print a friendly greeting. NAME defaults to "world".

```bash
poetry run sf hello
poetry run sf hello squirrels
```

## drop TEXT

Append TEXT to ~/.squirrelfocus/acornlog.txt with a timestamp.

```bash
poetry run sf drop "Fixed a tricky bug"
```

## show [COUNT]

Display the last COUNT entries from the log. COUNT defaults to 5.

```bash
poetry run sf show 3
```

## ask QUESTION

Create a work item from QUESTION using OpenAI.
The CLI help calls 'ask' to create tasks. Requires OPENAI_API_KEY.

```bash
poetry run sf ask "How do I plan tomorrow?"
```
