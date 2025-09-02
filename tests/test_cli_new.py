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
