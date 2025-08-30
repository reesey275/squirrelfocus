# ADOPTERS

Projects adopting SquirrelFocus should copy these files and directories:

- `.squirrelfocus/config.yaml`
- `scripts/*`
- `templates/*`

To use the reusable summary workflow, reference `sf-summary.yml`:

```yaml
jobs:
  summarize:
    uses: owner/squirrelfocus/.github/workflows/sf-summary.yml@main
    with:
      title: Example title
```

Verify the integration with a smoke test:

```bash
python scripts/sqf_emit.py summary
```
