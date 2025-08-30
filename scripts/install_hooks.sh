#!/usr/bin/env bash
set -euo pipefail
HOOK=".git/hooks/commit-msg"
cat > "$HOOK" <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
trailers="$(python3 "$root/scripts/sqf_emit.py" trailers || true)"
[ -z "$trailers" ] && exit 0
echo "" >> "$1"
echo "$trailers" >> "$1"
HOOK
chmod +x "$HOOK"
echo "Installed commit-msg hook."
