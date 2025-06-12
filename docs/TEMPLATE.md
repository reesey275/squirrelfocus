---
project: "<project_name>"
module: "<module_or_subsystem>"
phase: "<phase_or_milestone>"
tags: ["ci", "poetry", "docs", "workflow", "config", "yaml"]
updated: "<DD Month YYYY HH:MM (TZ)>"
version: "v<major>.<minor>.<patch>"
-----------------------------------

# Codex Work Request – Documentation + CI Setup Task

## 🎯 Objective

Perform configuration and documentation-only updates that do not change
runtime logic or behavior. This includes LICENSE updates, GitHub
Actions YAML cleanup, adding `.github/FUNDING.yml`, or README
adjustments. Ensure formatting and CI validations are performed using
Poetry tools.

---

## 📦 Affected Repository

* `<repo_url>`

---

## ✅ Task Checklist

* [ ] Update `LICENSE` year (e.g., 2024 → 2024–2025)
* [ ] Add or update `.github/FUNDING.yml` with sponsor platform(s)
* [ ] Quote `run:` commands in GitHub Actions YAMLs
  (e.g., `ai-build.yml`, `codex.yml`)
* [ ] Open a PR to `main` with all of the above
* [ ] Ensure Poetry-based formatting tools are executed in CI

---

## 🔒 Merge Policy

* PR must be manually reviewed
* CI formatting checks must pass (`ruff`, `black`)
* Test failures are acceptable if unrelated to these non-functional
  changes

---

## 🦪 CI Testing Summary

| Command                      | Status | Notes                            |
| ---------------------------- | ------ | -------------------------------- |
| `poetry run ruff check .`    | ✅ | Formatting passed                |
| `poetry run black --check .` | ✅ | Formatting passed                |
| `poetry run pytest -q`       | ❌ | Failures acceptable if unrelated |

---

## ✅ Acceptance Criteria

* Non-code files updated as intended
* CI runs complete with formatting checks passing
* PR is clearly labeled as “documentation/config-only”
* No logic or core application files are modified

---

## 🚦 Priority

* `<P1 | P2 | P3 | P4>` — *Choose based on urgency*

---

## 🔭 Executor Notes

* Do not block PR if `pytest` fails due to unrelated missing packages
* This type of task is safe to fast-track for review
* Recommend tagging PR with: `type:maintenance`, `ci`, `docs`

---

Created by: <your_name>
Assigned to: Codex Executor
Date Created: <today’s date>
