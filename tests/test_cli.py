from typer.testing import CliRunner
import cli

runner = CliRunner()


def setup_tmp_log(tmp_path, monkeypatch):
    log_dir = tmp_path / "log"
    log_file = log_dir / "acornlog.txt"
    monkeypatch.setattr(cli, "LOG_DIR", log_dir)
    monkeypatch.setattr(cli, "LOG_FILE", log_file)
    return log_dir, log_file


def test_sf_help_shows_usage():
    result = runner.invoke(cli.app, ["--help"], prog_name="sf")
    assert result.exit_code == 0
    assert "SquirrelFocus CLI" in result.output


def test_install_completion_creates_script(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("SHELL", "/bin/bash")
    result = runner.invoke(cli.app, ["--install-completion"], prog_name="sf")
    assert result.exit_code == 0
    assert "completion installed" in result.output.lower()
    script = tmp_path / ".bash_completions" / "sf.sh"
    assert script.exists()


def test_hello():
    result = runner.invoke(cli.app, ["hello", "squirrels"])
    assert result.exit_code == 0
    assert "Hello squirrels!" in result.output


def test_hello_default():
    result = runner.invoke(cli.app, ["hello"])
    assert result.exit_code == 0
    assert "Hello world!" in result.output


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


def test_show_no_log(tmp_path, monkeypatch):
    setup_tmp_log(tmp_path, monkeypatch)
    result = runner.invoke(cli.app, ["show", "1"])
    assert result.exit_code == 0
    assert "No log entries found." in result.output


def test_show_invalid_count(tmp_path, monkeypatch):
    setup_tmp_log(tmp_path, monkeypatch)
    result = runner.invoke(cli.app, ["show", "bad"])
    assert result.exit_code != 0
    assert "Invalid value for '[COUNT]'" in result.output


def test_show_non_positive_count(tmp_path, monkeypatch):
    setup_tmp_log(tmp_path, monkeypatch)
    result = runner.invoke(cli.app, ["show", "0"])
    assert result.exit_code != 0
    assert "range x>=1" in result.output


class DummyCompletions:
    def create(self, model, messages):
        class DummyMessage:
            content = "work item"

        class DummyChoice:
            message = DummyMessage()

        return type("R", (), {"choices": [DummyChoice()]})


class DummyClient:
    def __init__(self, api_key):
        self.chat = type("Chat", (), {"completions": DummyCompletions()})()


def test_ask_returns_work_item(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "token")
    monkeypatch.setattr(
        cli.openai,
        "OpenAI",
        lambda api_key: DummyClient(api_key),
    )
    result = runner.invoke(cli.app, ["ask", "question"])
    assert result.exit_code == 0
    assert "work item" in result.output


def test_ask_missing_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = runner.invoke(cli.app, ["ask", "anything"])
    assert result.exit_code != 0
    assert "OPENAI_API_KEY not set" in result.output


class ErrorCompletions:
    def create(self, model, messages):
        raise RuntimeError("boom")


class ErrorClient:
    def __init__(self, api_key):
        self.chat = type("Chat", (), {"completions": ErrorCompletions()})()


def test_ask_openai_error(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "token")
    monkeypatch.setattr(
        cli.openai,
        "OpenAI",
        lambda api_key: ErrorClient(api_key),
    )
    result = runner.invoke(cli.app, ["ask", "question"])
    assert result.exit_code != 0
    assert "OpenAI error: boom" in result.output


def test_drop_missing_text():
    result = runner.invoke(cli.app, ["drop"])
    assert result.exit_code != 0
    assert "Missing argument 'TEXT'" in result.output


def test_ask_missing_question():
    result = runner.invoke(cli.app, ["ask"])
    assert result.exit_code != 0
    assert "Missing argument 'QUESTION'" in result.output


class DummyFile:
    def open(self, mode="r", encoding="utf-8"):
        raise OSError("fail")


def test_drop_write_error(monkeypatch):
    monkeypatch.setattr(cli, "ensure_log_dir", lambda: None)
    monkeypatch.setattr(cli, "LOG_FILE", DummyFile())
    result = runner.invoke(cli.app, ["drop", "note"])
    assert result.exit_code != 0
    assert isinstance(result.exception, OSError)


class ReadFailFile:
    def exists(self):
        return True

    def open(self, mode="r", encoding="utf-8"):
        raise OSError("fail")


def test_show_read_error(monkeypatch):
    monkeypatch.setattr(cli, "ensure_log_dir", lambda: None)
    monkeypatch.setattr(cli, "LOG_FILE", ReadFailFile())
    result = runner.invoke(cli.app, ["show", "1"])
    assert result.exit_code != 0
    assert isinstance(result.exception, OSError)


def test_drop_log_dir_error(monkeypatch):
    def raiser():
        raise OSError("fail")

    monkeypatch.setattr(cli, "ensure_log_dir", raiser)
    result = runner.invoke(cli.app, ["drop", "note"])
    assert result.exit_code != 0
    assert isinstance(result.exception, OSError)


def test_ask_prompt_missing_file(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "token")
    monkeypatch.setattr(
        cli.openai,
        "OpenAI",
        lambda api_key: DummyClient(api_key),
    )
    monkeypatch.setattr(cli, "PROMPT_FILE", tmp_path / "missing")
    result = runner.invoke(cli.app, ["ask", "hi"])
    assert result.exit_code != 0
    assert isinstance(result.exception, FileNotFoundError)
