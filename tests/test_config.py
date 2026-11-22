import pytest

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


def test_roundtrip(tmp_path):
    path = tmp_path / "nested" / "config.toml"
    config = Config(path)
    config.token = "t"
    config.databases["Work"] = {"id": "w", "properties": ["Name"]}
    config.save()
    reloaded = Config(path)
    assert reloaded.token == "t"
    assert reloaded.databases == {"Work": {"id": "w", "properties": ["Name"]}}


def test_reads_legacy_format(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text(LEGACY)
    assert Config(path).database("Default") == {"id": "abc", "properties": ["Name", "Date"]}


def test_invalid_file(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("not = [valid")
    with pytest.raises(ConfigError, match="Invalid config"):
        Config(path)


def test_unknown_database(tmp_path):
    with pytest.raises(ConfigError, match="'Nope' not found"):
        Config(tmp_path / "c.toml").database("Nope")


def test_page_index(tmp_path):
    index = PageIndex(tmp_path / "pages.json")
    assert index.load() == []
    index.save(["a", "b"])
    assert index.load() == ["a", "b"]
