from pathlib import Path
from datetime import datetime
import re
from typer.testing import CliRunner
import cli

runner = CliRunner()


class FixedDate(datetime):
    @classmethod
    def now(cls, tz=None):  # noqa: D401
        return cls(2024, 2, 1)


def make_entry(path: Path, date: str, fix: str) -> None:
    path.write_text(
        "---\n"
        f'created_at: "{date}"\n'
        "trailers:\n"
        f"  fix: {fix}\n"
        "---\n"
    )


def test_report_filters_and_format(monkeypatch):
    with runner.isolated_filesystem():
        Path(".squirrelfocus").mkdir()
        Path(".squirrelfocus/config.yaml").write_text(
            "journals_dir: journal_logs\n"
        )
        jdir = Path("journal_logs")
        jdir.mkdir()
        make_entry(jdir / "2024-01-15-recent.md", "2024-01-15", "bug1")
        make_entry(jdir / "2023-12-01-old.md", "2023-12-01", "bug2")
        monkeypatch.setattr(cli, "datetime", FixedDate)
        res = runner.invoke(cli.app, ["report"])
        assert res.exit_code == 0
        assert "bug1" in res.output
        assert "bug2" not in res.output
        res = runner.invoke(
            cli.app, ["report", "--since", "100", "--format", "txt"]
        )
        assert res.exit_code == 0
        assert "bug2" in res.output
        assert "###" not in res.output


def test_report_invalid_format(monkeypatch):
    with runner.isolated_filesystem():
        Path(".squirrelfocus").mkdir()
        Path(".squirrelfocus/config.yaml").write_text(
            "journals_dir: journal_logs\n"
        )
        Path("journal_logs").mkdir()
        monkeypatch.setattr(cli, "datetime", FixedDate)
        res = runner.invoke(cli.app, ["report", "--format", "html"])
        out = re.sub(r"\x1b\[[0-9;]*m", "", res.output)
        assert res.exit_code == 2
        assert "Invalid value for '--format'" in out


def test_report_negative_since():
    with runner.isolated_filesystem():
        res = runner.invoke(cli.app, ["report", "--since", "-1"])
        out = re.sub(r"\x1b\[[0-9;]*m", "", res.output)
        assert res.exit_code == 2
        assert "Invalid value for '--since'" in out


def test_report_format_case_insensitive(monkeypatch):
    with runner.isolated_filesystem():
        Path(".squirrelfocus").mkdir()
        Path(".squirrelfocus/config.yaml").write_text(
            "journals_dir: journal_logs\n"
        )
        jdir = Path("journal_logs")
        jdir.mkdir()
        make_entry(jdir / "2024-01-15.md", "2024-01-15", "bug1")
        monkeypatch.setattr(cli, "datetime", FixedDate)
        res = runner.invoke(cli.app, ["report", "--format", "TXT"])
        assert res.exit_code == 0
        assert "bug1" in res.output
        assert "###" not in res.output


def test_report_missing_journal_dir(monkeypatch):
    with runner.isolated_filesystem():
        Path(".squirrelfocus").mkdir()
        Path(".squirrelfocus/config.yaml").write_text(
            "journals_dir: journal_logs\n"
        )
        monkeypatch.setattr(cli, "datetime", FixedDate)
        res = runner.invoke(cli.app, ["report"])
        assert res.exit_code == 1
        assert "No entries found." in res.output


def test_report_empty_journal_dir(monkeypatch):
    with runner.isolated_filesystem():
        Path(".squirrelfocus").mkdir()
        Path(".squirrelfocus/config.yaml").write_text(
            "journals_dir: journal_logs\n"
        )
        Path("journal_logs").mkdir()
        monkeypatch.setattr(cli, "datetime", FixedDate)
        res = runner.invoke(cli.app, ["report"])
        assert res.exit_code == 1
        assert "No entries found." in res.output
