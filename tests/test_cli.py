from typer.testing import CliRunner
import cli

runner = CliRunner()


def setup_tmp_log(tmp_path, monkeypatch):
    log_dir = tmp_path / "log"
    log_file = log_dir / "acornlog.txt"
    monkeypatch.setattr(cli, "LOG_DIR", log_dir)
    monkeypatch.setattr(cli, "LOG_FILE", log_file)
    return log_dir, log_file


def test_hello():
    result = runner.invoke(cli.app, ["hello", "squirrels"])
    assert result.exit_code == 0
    assert "Hello squirrels!" in result.output


def test_drop_creates_entry(tmp_path, monkeypatch):
    _, log_file = setup_tmp_log(tmp_path, monkeypatch)
    result = runner.invoke(cli.app, ["drop", "first note"])
    assert result.exit_code == 0
    assert log_file.exists()
    with log_file.open() as fh:
        lines = fh.readlines()
    assert any("first note" in line for line in lines)


def test_show_outputs_recent_entries(tmp_path, monkeypatch):
    _, log_file = setup_tmp_log(tmp_path, monkeypatch)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text("entry1\nentry2\nentry3\n")
    result = runner.invoke(cli.app, ["show", "2"])
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    assert lines == ["entry2", "entry3"]
