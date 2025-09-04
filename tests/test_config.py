from pathlib import Path
from typer.testing import CliRunner
import cli

runner = CliRunner()


def _cfg_path() -> Path:
    path = Path(".squirrelfocus") / "config.yaml"
    cli.conf.CFG_PATH = path
    return path


def _write(text: str) -> None:
    path = _cfg_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_valid_config_allows_run():
    with runner.isolated_filesystem():
        cfg = (
            "journals_dir: logs\n"
            "trailer_keys: [fix, why]\n"
            "summary_format: 'x'\n"
        )
        _write(cfg)
        _write(cfg)
        result = runner.invoke(cli.app, ["hello"])
        assert result.exit_code == 0


def test_missing_key_shows_example():
    with runner.isolated_filesystem():
        _write("trailer_keys: [fix]\n" "summary_format: 'x'\n")
        result = runner.invoke(cli.app, ["hello"])
        assert result.exit_code != 0
        assert "journals_dir" in result.output
        assert "journals_dir: journal_logs" in result.output


def test_malformed_key_shows_example():
    with runner.isolated_filesystem():
        _write(
            "journals_dir: logs\n"
            "trailer_keys: bad\n"
            "summary_format: 'x'\n"
        )
        result = runner.invoke(cli.app, ["hello"])
        assert result.exit_code != 0
        assert "trailer_keys" in result.output
        assert "trailer_keys: [fix, why, change, proof, ref]" in result.output


def test_required_key_malformed_shows_example():
    with runner.isolated_filesystem():
        _write(
            "journals_dir: [logs]\n"
            "trailer_keys: [fix]\n"
            "summary_format: 'x'\n"
        )
        result = runner.invoke(cli.app, ["hello"])
        assert result.exit_code != 0
        assert "journals_dir" in result.output
        assert "journals_dir: journal_logs" in result.output


def test_trailer_keys_elements_must_be_strings():
    with runner.isolated_filesystem():
        _write(
            "journals_dir: logs\n"
            "trailer_keys: [fix, 1]\n"
            "summary_format: 'x'\n"
        )
        result = runner.invoke(cli.app, ["hello"])
        assert result.exit_code != 0
        assert "trailer_keys" in result.output
        assert "trailer_keys: [fix, why, change, proof, ref]" in result.output


def test_malformed_yaml_shows_error():
    with runner.isolated_filesystem():
        _write("journals_dir: [\n")
        result = runner.invoke(cli.app, ["hello"])
        assert result.exit_code != 0
        assert "Failed to parse config" in result.output


def test_unreadable_config_shows_error():
    with runner.isolated_filesystem():
        path = _cfg_path()
        path.parent.mkdir(exist_ok=True)
        path.mkdir()
        result = runner.invoke(cli.app, ["hello"])
        assert result.exit_code != 0
        assert "Could not read config" in result.output
