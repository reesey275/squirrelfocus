from pathlib import Path
from typer.testing import CliRunner
import cli

runner = CliRunner()


def test_preview_outputs_summary():
    with runner.isolated_filesystem():
        Path(".squirrelfocus").mkdir()
        Path(".squirrelfocus/config.yaml").write_text(
            "journals_dir: journal_logs\n"
        )
        scripts = Path("scripts")
        scripts.mkdir()
        src = Path(__file__).resolve().parents[1] / "scripts" / "sqf_emit.py"
        Path(scripts / "sqf_emit.py").write_text(src.read_text())
        jdir = Path("journal_logs")
        jdir.mkdir()
        entry = jdir / "2024-01-01-test.md"
        entry.write_text(
            "---\ntrailers:\n  fix: bug\n  why: x\n  change: y\n  proof: z\n---\n"
        )
        result = runner.invoke(cli.app, ["preview"])
        assert result.exit_code == 0
        assert "CI Triage" in result.output
