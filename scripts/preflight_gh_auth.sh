#!/usr/bin/env bash
set -euo pipefail

# Assign GH_TOKEN from CI_PROFILE_PUSH_TOKEN or CODEX_AGENT_AUTH if unset
if [ -z "${GH_TOKEN:-}" ]; then
  GH_TOKEN="${CI_PROFILE_PUSH_TOKEN:-${CODEX_AGENT_AUTH:-}}"
fi

