from pathlib import Path
from typer.testing import CliRunner
import cli

runner = CliRunner()


def make_basic_files():
    Path(".squirrelfocus").mkdir()
    Path(".squirrelfocus/config.yaml").write_text(
        "journals_dir: journal_logs\n"
    )
    Path("journal_logs").mkdir()
    scripts = Path("scripts")
    scripts.mkdir()
    src = Path(__file__).resolve().parents[1] / "scripts" / "sqf_emit.py"
    Path(scripts / "sqf_emit.py").write_text(src.read_text())
    hook = Path(".git/hooks")
    hook.mkdir(parents=True)
    Path(hook / "commit-msg").write_text("# hook")


def test_doctor_missing_config():
    with runner.isolated_filesystem():
        result = runner.invoke(cli.app, ["doctor"])
        assert result.exit_code == 1


def test_doctor_ok():
    with runner.isolated_filesystem():
        make_basic_files()
        result = runner.invoke(cli.app, ["doctor"])
        assert result.exit_code == 0
