# SquirrelFocus CI Trailers — Consumer Overlay

This overlay converts SquirrelFocus journal entries into commit trailers and
CI run summaries.

## Quick start
```bash
bash scripts/install_hooks.sh   # optional commit trailer auto-append

# create a journal entry using templates/sqf_fix.md under journal_logs/
git add -A && git commit -m "fix: example change" && git push
```

## CI

`.github/workflows/ci-summary.yml` writes a Run Summary from the newest
journal entry.
`merge-log.yml` (optional) appends a single-line record to
`MILESTONE_LOG.md` on pushes to main.

## Rollback

Remove `.github/workflows/ci-summary.yml` to stop posting summaries.
Delete `.git/hooks/commit-msg` to disable auto trailer insertion.
