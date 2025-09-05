from __future__ import annotations

import json
import subprocess
import textwrap
from pathlib import Path
from string import Template

import pytest


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


@pytest.mark.parametrize(
    "summary_text, expect_called, expect_result",
    [
        ("hi", True, True),
        (None, False, False),
        ("", False, False),
    ],
)
def test_triage_label_summary_cases(
    tmp_path: Path,
    summary_text: str | None,
    expect_called: bool,
    expect_result: bool,
) -> None:
    if summary_text is None:
        # Intentionally use a path to a nonexistent summary file to simulate
        # the missing summary case.
        sum_path = tmp_path / "nonexistent_summary.md"
    else:
        sum_path = tmp_path / "summary.md"
        sum_path.write_text(summary_text)
    _run(["sqf:triage"], sum_path, expect_called, expect_result)

def test_comment_with_label_and_summary(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    mod = root / "scripts" / "post_triage_comment.js"
    summ = tmp_path / "summary.md"
    summ.write_text("hi")
    mod_path = json.dumps(str(mod))
    sum_path = json.dumps(str(summ))
    tpl = Template(
        textwrap.dedent(
            """
            const fn = require($mod_path);
            const ctx = {
              payload: {
                pull_request: {
                  number: 1, labels: [{name: 'sqf:triage'}]
                }
              },
              repo: {owner: 'o', repo: 'r'}
            };
            let called = false;
            const github = {
              rest: {issues: {createComment: () => {called = true;}}}
            };
            const core = {info: () => {}};
            fn({github, context: ctx, core}, $sum_path).then((r) => {
              if (called && r) process.exit(0);
              process.exit(1);
            });
            """
        )
    )
    js = tpl.substitute(mod_path=mod_path, sum_path=sum_path)
    proc = subprocess.run(["node", "-e", js])
    assert proc.returncode == 0


def test_skip_with_label_missing_summary(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    mod = root / "scripts" / "post_triage_comment.js"
    mod_path = json.dumps(str(mod))
    # Pass a non-existent summary file to simulate the missing summary case.
    sum_path = json.dumps(str(tmp_path / "summary.md"))
    tpl = Template(
        textwrap.dedent(
            """
            const fn = require($mod_path);
            const ctx = {
              payload: {
                pull_request: {
                  number: 1, labels: [{name: 'sqf:triage'}]
                }
              },
              repo: {owner: 'o', repo: 'r'}
            };
            let called = false;
            const github = {
              rest: {issues: {createComment: () => {called = true;}}}
            };
            const core = {info: () => {}};
            fn({github, context: ctx, core}, $sum_path).then((r) => {
              if (!called && !r) process.exit(0);
              process.exit(1);
            });
            """
        )
    )
    js = tpl.substitute(mod_path=mod_path, sum_path=sum_path)
    proc = subprocess.run(["node", "-e", js])
    assert proc.returncode == 0


def test_skip_with_label_empty_summary(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    mod = root / "scripts" / "post_triage_comment.js"
    summ = tmp_path / "summary.md"
    summ.write_text("")
    mod_path = json.dumps(str(mod))
    sum_path = json.dumps(str(summ))
    tpl = Template(
        textwrap.dedent(
            """
            const fn = require($mod_path);
            const ctx = {
              payload: {
                pull_request: {
                  number: 1, labels: [{name: 'sqf:triage'}]
                }
              },
              repo: {owner: 'o', repo: 'r'}
            };
            let called = false;
            const github = {
              rest: {issues: {createComment: () => {called = true;}}}
            };
            const core = {info: () => {}};
            fn({github, context: ctx, core}, $sum_path).then((r) => {
              if (!called && !r) process.exit(0);
              process.exit(1);
            });
            """
        )
    )
    js = tpl.substitute(mod_path=mod_path, sum_path=sum_path)
    proc = subprocess.run(["node", "-e", js])
    assert proc.returncode == 0