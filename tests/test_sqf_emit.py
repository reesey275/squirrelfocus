from pathlib import Path
import os
import subprocess
import sys
import runpy

import pytest

typer_testing = pytest.importorskip("typer.testing")
yaml = pytest.importorskip("yaml")
CliRunner = typer_testing.CliRunner

runner = CliRunner()


def make_basic():
    Path(".squirrelfocus").mkdir()
    Path(".squirrelfocus/config.yaml").write_text(
        "journals_dir: journal_logs\n"
    )
    scripts = Path("scripts")
    scripts.mkdir()
    src = Path(__file__).resolve().parents[1] / "scripts" / "sqf_emit.py"
    Path(scripts / "sqf_emit.py").write_text(src.read_text())


def test_emit_no_journal_file():
    with runner.isolated_filesystem():
        make_basic()
        result = subprocess.run(
            [sys.executable, "scripts/sqf_emit.py", "trailers"],
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.stdout.strip() == ""


def test_emit_malformed_frontmatter():
    with runner.isolated_filesystem():
        make_basic()
        jdir = Path("journal_logs")
        jdir.mkdir()
        entry = jdir / "bad.md"
        entry.write_text("---\ntrailers:\n  fix: [\n---\n")
        result = subprocess.run(
            [sys.executable, "scripts/sqf_emit.py", "trailers"],
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.stdout.strip() == ""


def test_emit_multiple_entries_fallback(monkeypatch, capsys):
    with runner.isolated_filesystem():
        make_basic()
        jdir = Path("journal_logs")
        jdir.mkdir()
        older = jdir / "old.md"
        older.write_text("---\ntrailers:\n  fix: old\n  why: q\n---\n")
        newer = jdir / "new.md"
        newer.write_text("---\ntrailers:\n  fix: new\n  why: z\n---\n")
        os.utime(older, (1, 1))
        os.utime(newer, (2, 2))

        import builtins

        orig_import = builtins.__import__

        def fake_import(name, *a, **k):
            if name == "yaml":
                raise ImportError("no yaml")
            return orig_import(name, *a, **k)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        monkeypatch.setattr(sys, "argv", ["sqf_emit.py", "trailers"])
        runpy.run_path("scripts/sqf_emit.py", run_name="__main__")
        out = capsys.readouterr().out
        assert out.strip() == "fix: new\nwhy: z"
