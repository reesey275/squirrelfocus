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

## PyYAML missing at runtime

`scripts/sqf_emit.py` uses PyYAML to parse config files.
If the library is not installed the script falls back to a basic parser.
Nested YAML structures are ignored, so install PyYAML to get full support.
