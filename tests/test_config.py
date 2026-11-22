import pytest
from keyring.errors import KeyringError

from notion_cli_list_manager.config import Config, ConfigError, PageIndex

LEGACY = """
token = "secret"

[databases]
    [databases.Default]
        id = "abc"
        properties = ["Name", "Date"]
"""


def test_missing_file_is_empty(tmp_path):
    config = Config(tmp_path / "none.toml")
    assert config.token == "" and config.databases == {}


def test_token_lives_in_keyring(tmp_path, memory_keyring):
    path = tmp_path / "config.toml"
    config = Config(path)
    config.token = "t"
    config.save()
    assert Config(path).token == "t"
    assert memory_keyring.store == {("notion-cli-list-manager", "token"): "t"}
    assert "token" not in path.read_text()


def test_legacy_plaintext_token_is_ignored_and_dropped_on_save(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text(LEGACY)
    config = Config(path)
    assert config.token == ""
    config.save()
    assert "secret" not in path.read_text()


def locked(*args):
    raise KeyringError("locked")


def test_keyring_read_failure(tmp_path, monkeypatch, memory_keyring):
    monkeypatch.setattr(memory_keyring, "get_password", locked)
    with pytest.raises(ConfigError, match="read the token from the system keyring: locked"):
        _ = Config(tmp_path / "c.toml").token


def test_keyring_write_failure(tmp_path, monkeypatch, memory_keyring):
    monkeypatch.setattr(memory_keyring, "set_password", locked)
    with pytest.raises(ConfigError, match="save the token to the system keyring: locked"):
        Config(tmp_path / "c.toml").token = "t"


def test_roundtrip(tmp_path):
    path = tmp_path / "nested" / "config.toml"
    config = Config(path)
    config.databases["Work"] = {"id": "w", "properties": ["Name"]}
    config.save()
    reloaded = Config(path)
    assert reloaded.databases == {"Work": {"id": "w", "properties": ["Name"]}}


def test_reads_legacy_format(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text(LEGACY)
    assert Config(path).database("Default") == {"id": "abc", "properties": ["Name", "Date"]}


def test_invalid_file(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("not = [valid")
    config = Config(path)
    assert config.text == "not = [valid"
    with pytest.raises(ConfigError, match="Invalid config"):
        _ = config.databases


def test_unknown_database(tmp_path):
    with pytest.raises(ConfigError, match="'Nope' not found"):
        Config(tmp_path / "c.toml").database("Nope")


def test_page_index(tmp_path):
    index = PageIndex(tmp_path / "pages.json")
    assert index.load() == []
    index.save(["a", "b"])
    assert index.load() == ["a", "b"]


@pytest.mark.parametrize(
    "labels, given, expected",
    [
        (["Work", "Default"], None, "Default"),
        (["Work", "Home"], None, "Work"),
        (["Work", "Default"], "Work", "Work"),
    ],
)
def test_resolve(tmp_path, labels, given, expected):
    config = Config(tmp_path / "c.toml")
    config.databases.update({label: {"id": label} for label in labels})
    assert config.resolve(given) == expected
    assert config.database(given) == {"id": expected}


@pytest.mark.parametrize(
    "labels, given, message",
    [([], None, "No databases configured"), (["Work"], "Default", "'Default' not found")],
)
def test_resolve_errors(tmp_path, labels, given, message):
    config = Config(tmp_path / "c.toml")
    config.databases.update({label: {"id": label} for label in labels})
    with pytest.raises(ConfigError, match=message):
        config.resolve(given)


def test_parse_drops_token():
    assert Config.parse('token = "x"\n[databases.A]\nid = "a"') == {"databases": {"A": {"id": "a"}}}
