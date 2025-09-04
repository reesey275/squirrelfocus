from pathlib import Path
from typer.testing import CliRunner
import cli

runner = CliRunner()

VALID_CFG = (
    "journals_dir: journal_logs\n"
    "entry_glob: '**/*.md'\n"
    "prefer_frontmatter: true\n"
    "trailer_keys: [fix]\n"
    "summary_format: hi\n"
)


def write_cfg(text: str) -> None:
    Path('.squirrelfocus').mkdir(parents=True, exist_ok=True)
    Path('.squirrelfocus/config.yaml').write_text(text)


def test_startup_valid_config():
    with runner.isolated_filesystem():
        write_cfg(VALID_CFG)
        result = runner.invoke(cli.app, ['hello'])
        assert result.exit_code == 0
        assert 'config:' not in result.output


def test_startup_missing_key():
    with runner.isolated_filesystem():
        bad = VALID_CFG.replace("entry_glob: '**/*.md'\n", '')
        write_cfg(bad)
        result = runner.invoke(cli.app, ['hello'])
        assert result.exit_code == 0
        assert "missing 'entry_glob'" in result.output


def test_startup_malformed_config():
    with runner.isolated_filesystem():
        write_cfg('journals_dir: x\nentry_glob: **/*.md\n')
        result = runner.invoke(cli.app, ['hello'])
        assert result.exit_code == 0
        assert 'invalid YAML' in result.output
