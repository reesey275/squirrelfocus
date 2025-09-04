from pathlib import Path
import os
import subprocess
import sys
from typer.testing import CliRunner

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


def test_emit_multiple_entries_fallback():
    with runner.isolated_filesystem():
        make_basic()
        jdir = Path("journal_logs")
        jdir.mkdir()
        older = jdir / "old.md"
        older.write_text(
            "---\ntrailers:\n  fix: old\n  why: q\n---\n"
        )
        newer = jdir / "new.md"
        newer.write_text(
            "---\ntrailers:\n  fix: new\n  why: z\n---\n"
        )
        os.utime(older, (1, 1))
        os.utime(newer, (2, 2))
        fake = Path("fake")
        (fake / "yaml").mkdir(parents=True)
        Path(fake / "yaml/__init__.py").write_text(
            "raise RuntimeError('no yaml')\n"
        )
        env = dict(os.environ, PYTHONPATH=str(fake))
        result = subprocess.run(
            [sys.executable, "scripts/sqf_emit.py", "trailers"],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.stdout.strip() == "fix: new\nwhy: z"
