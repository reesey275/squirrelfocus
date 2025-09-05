from pathlib import Path
from typer.testing import CliRunner
import cli

runner = CliRunner()


def test_new_creates_entry():
    with runner.isolated_filesystem():
        Path(".squirrelfocus").mkdir()
        Path(".squirrelfocus/config.yaml").write_text(
            "journals_dir: journal_logs\n"
        )
        Path("templates").mkdir()
        Path("templates/sqf_fix.md").write_text("---\ntrailers:\n---\nbody\n")
        result = runner.invoke(
            cli.app, ["new", "--fix", "bug"], catch_exceptions=False
        )
        assert result.exit_code == 0
        path = Path(result.output.strip())
        assert path.exists()
        text = path.read_text()
        assert "fix" in text and "bug" in text


def test_new_missing_template(monkeypatch):
    with runner.isolated_filesystem():
        Path(".squirrelfocus").mkdir()
        Path(".squirrelfocus/config.yaml").write_text(
            "journals_dir: journal_logs\n"
        )

        orig_exists = Path.exists

        def fake_exists(self):
            if self.name == "sqf_fix.md":
                return False
            return orig_exists(self)

        monkeypatch.setattr(Path, "exists", fake_exists)

        result = runner.invoke(cli.app, ["new", "--fix", "bug"])
        assert result.exit_code != 0
        assert "template missing" in str(result.exception)


def test_new_journal_dir_failure(monkeypatch):
    with runner.isolated_filesystem():
        Path(".squirrelfocus").mkdir()
        Path(".squirrelfocus/config.yaml").write_text(
            "journals_dir: journal_logs\n"
        )
        Path("templates").mkdir()
        Path("templates/sqf_fix.md").write_text("---\ntrailers:\n---\nbody\n")

        orig_mkdir = Path.mkdir

        def fake_mkdir(self, *args, **kwargs):
            if self.name == "journal_logs":
                raise OSError("cannot create dir")
            return orig_mkdir(self, *args, **kwargs)

        monkeypatch.setattr(Path, "mkdir", fake_mkdir)

        result = runner.invoke(cli.app, ["new", "--fix", "bug"])
        assert result.exit_code != 0
        assert "cannot create dir" in str(result.exception)
