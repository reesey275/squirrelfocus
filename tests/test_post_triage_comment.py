from __future__ import annotations

import json
import subprocess
import textwrap
from pathlib import Path
from string import Template


def _run(
    labels: list[str], sum_path: Path, expect_called: bool, expect_result: bool
) -> None:
    root = Path(__file__).resolve().parents[1]
    mod = root / "scripts" / "post_triage_comment.js"
    tpl = Template(
        textwrap.dedent(
            """
            const fn = require($mod_path);
            const ctx = {
              payload: {pull_request: {number: 1, labels: $labels}},
              repo: {owner: 'o', repo: 'r'}
            };
            let called = false;
            const github = {
              rest: {issues: {createComment: () => {called = true;}}}
            };
            const core = {info: () => {}};
            fn({github, context: ctx, core}, $sum_path).then((r) => {
              if (called === $expect_called && !!r === $expect_result) {
                process.exit(0);
              }
              process.exit(1);
            });
            """
        )
    )
    js = tpl.substitute(
        mod_path=json.dumps(str(mod)),
        sum_path=json.dumps(str(sum_path)),
        labels=json.dumps([{"name": lab} for lab in labels]),
        expect_called=str(expect_called).lower(),
        expect_result=str(expect_result).lower(),
    )
    proc = subprocess.run(["node", "-e", js])
    assert proc.returncode == 0


def test_skip_without_label(tmp_path: Path) -> None:
    summ = tmp_path / "summary.md"
    summ.write_text("hi")
    _run([], summ, False, False)


def test_comment_with_label_and_summary(tmp_path: Path) -> None:
    summ = tmp_path / "summary.md"
    summ.write_text("hi")
    _run(["sqf:triage"], summ, True, True)


def test_skip_with_label_missing_summary(tmp_path: Path) -> None:
    # Use a path to a non-existent summary file to simulate the missing
    # summary case.
    sum_path = tmp_path / "nonexistent_summary.md"
    _run(["sqf:triage"], sum_path, False, False)


def test_skip_with_label_empty_summary(tmp_path: Path) -> None:
    summ = tmp_path / "summary.md"
    summ.write_text("")
    _run(["sqf:triage"], summ, False, False)
