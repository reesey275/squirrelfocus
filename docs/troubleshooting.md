# Troubleshooting

This page collects fixes for common issues.

## Poetry lock file mismatch

If `poetry install` fails with a message about a lock file mismatch run the
following commands:

```bash
poetry lock
poetry install
```

The first command regenerates the lock file. The second installs your
dependencies again.
