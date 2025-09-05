from __future__ import annotations

import json
from pathlib import Path
import subprocess
import textwrap
from string import Template


def test_skip_without_label(tmp_path: Path):
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
              payload: {pull_request: {number: 1, labels: []}},
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
    summ = tmp_path / "summary.md"
    # Intentionally do not create the summary file to test the missing summary scenario.
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
