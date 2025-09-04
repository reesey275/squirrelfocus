from __future__ import annotations

from pathlib import Path
import importlib.util
import os
import sys


def load_emit(tmp_path: Path):
    src = Path(__file__).resolve().parents[1] / "scripts" / "sqf_emit.py"
    dst = tmp_path / "scripts" / "sqf_emit.py"
    dst.parent.mkdir()
    dst.write_text(src.read_text())
    spec = importlib.util.spec_from_file_location("sqf_emit", dst)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load sqf_emit from {dst}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_missing_journal_file(tmp_path, capsys, monkeypatch):
    emit = load_emit(tmp_path)
    monkeypatch.setattr(sys, "argv", ["sqf_emit.py", "trailers"])
    emit.main()
    out = capsys.readouterr().out
    assert out == ""


def test_malformed_yaml_frontmatter(tmp_path, capsys, monkeypatch):
    emit = load_emit(tmp_path)

    class Dummy:
        @staticmethod
        def safe_load(text: str):
            raise ValueError("bad")

    monkeypatch.setattr(emit, "yaml", Dummy())
    monkeypatch.setattr(emit, "HAVE_YAML", True)
    jdir = tmp_path / "journal_logs"
    jdir.mkdir()
    entry = jdir / "2024-01-01.md"
    entry.write_text("---\ntrailers: [oops\n---\n")
    monkeypatch.setattr(sys, "argv", ["sqf_emit.py", "trailers"])
    emit.main()
    out = capsys.readouterr().out.strip()
    assert out == ""


def test_multiple_entries_fallback_parser(tmp_path, capsys, monkeypatch):
    emit = load_emit(tmp_path)
    monkeypatch.setattr(emit, "yaml", None)
    monkeypatch.setattr(emit, "HAVE_YAML", False)
    jdir = tmp_path / "journal_logs"
    jdir.mkdir()
    old = jdir / "2024-01-01-old.md"
    old.write_text("---\ntrailers:\n  fix: old\n---\n")
    new = jdir / "2024-01-02-new.md"
    new.write_text("---\ntrailers:\n  fix: new\n---\n")
    older_ts = (1, 1)
    newer_ts = (2, 2)
    os.utime(old, older_ts)
    os.utime(new, newer_ts)
    monkeypatch.setattr(sys, "argv", ["sqf_emit.py", "trailers"])
    emit.main()
    out = capsys.readouterr().out.strip()
    assert out == "fix: new"
