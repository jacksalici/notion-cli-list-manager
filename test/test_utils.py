import json
from unittest.mock import mock_open, patch, MagicMock
import pytest
import toml
from notion_cli_list_manager.utils import TomlHelper, NotionAPI


SAMPLE_CONFIG = toml.dumps({
    "token": "test_token",
    "databases": {
        "Default": {"id": "db_id_1", "properties": ["Name", "Date"]},
        "Work": {"id": "db_id_2", "properties": ["Title"]},
    },
})


class TestTomlHelper:
    def test_get_dict_success(self):
        with patch("builtins.open", mock_open(read_data=SAMPLE_CONFIG)):
            result = TomlHelper.get_dict("/fake/config.toml")
            assert result["token"] == "test_token"
            assert "Default" in result["databases"]

    def test_get_dict_file_not_found(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = TomlHelper.get_dict("/fake/missing.toml")
            assert result == {}

    def test_get_dict_decode_error(self):
        with patch("builtins.open", mock_open(read_data="invalid {{{ toml")):
            result = TomlHelper.get_dict("/fake/bad.toml")
            assert result == {}

    def test_set_dict_success(self):
        m_open = mock_open()
        with patch("builtins.open", m_open):
            result = TomlHelper.set_dict({"key": "value"}, "/fake/test.toml")
            assert result is True

    def test_set_dict_failure(self):
        with patch("builtins.open", side_effect=PermissionError("denied")):
            result = TomlHelper.set_dict({"key": "value"}, "/fake/test.toml")
            assert result is False

    def test_get_db_id_found(self):
        with patch.object(TomlHelper, "get_dict", return_value={
            "databases": {"Default": {"id": "abc123"}}
        }):
            result = TomlHelper.get_db_id("Default")
            assert result == "abc123"

    def test_get_db_id_not_found(self):
        with patch.object(TomlHelper, "get_dict", return_value={"databases": {}}):
            result = TomlHelper.get_db_id("NonExistent")
            assert result == ""

    def test_get_db_keys(self):
        with patch.object(TomlHelper, "get_dict", return_value={
            "databases": {"Default": {}, "Work": {}}
        }):
            result = TomlHelper.get_db_keys()
            assert set(result) == {"Default", "Work"}

    def test_get_db_keys_empty(self):
        with patch.object(TomlHelper, "get_dict", return_value={}):
            result = TomlHelper.get_db_keys()
            assert list(result) == []

    def test_get_db_prop_found(self):
        with patch.object(TomlHelper, "get_dict", return_value={
            "databases": {"Default": {"properties": ["Name", "Date"]}}
        }):
            result = TomlHelper.get_db_prop("Default")
            assert result == ["Name", "Date"]

    def test_get_db_prop_missing(self):
        with patch.object(TomlHelper, "get_dict", return_value={
            "databases": {"Default": {}}
        }):
            result = TomlHelper.get_db_prop("Default")
            assert result == []


class TestNotionAPI:
    def test_get_token(self):
        with patch.object(TomlHelper, "get_dict", return_value={"token": "abc123"}):
            token = NotionAPI.get_token()
            assert token == "abc123"

    def test_get_token_empty(self):
        with patch.object(TomlHelper, "get_dict", return_value={}):
            token = NotionAPI.get_token()
            assert token == ""

    def test_create_headers(self):
        with patch.object(TomlHelper, "get_dict", return_value={"token": "test_token"}):
            api = NotionAPI()
            headers = api.create_headers()
            assert headers["Authorization"] == "test_token"
            assert headers["Notion-Version"] == "2021-08-16"
            assert headers["Content-Type"] == "application/json"

    def test_get_db_props(self):
        mock_response = {
            "properties": {
                "Name": {"id": "title", "type": "title"},
                "Date": {"id": "date", "type": "date"},
            }
        }
        with patch.object(TomlHelper, "get_dict", return_value={"token": "test_token"}):
            api = NotionAPI()
            with patch.object(api, "get_database", return_value=mock_response):
                props = api.get_db_props("some_db_id")
                assert set(props) == {"Name", "Date"}

    def test_get_db_props_empty(self):
        with patch.object(TomlHelper, "get_dict", return_value={"token": "test_token"}):
            api = NotionAPI()
            with patch.object(api, "get_database", return_value={}):
                props = api.get_db_props("some_db_id")
                assert list(props) == []

    def _api(self):
        with patch.object(TomlHelper, "get_dict", return_value={"token": "t"}):
            return NotionAPI()

    @pytest.mark.parametrize("title", [
        "plain",
        'say "hi"',
        "back\\slash",
        "unicode àèì 🚀",
        '"}},"parent":{"database_id":"evil',  # injection attempt
    ])
    def test_new_page_payload_is_valid_json(self, title):
        api = self._api()
        with patch.object(api, "make_request") as mock_req:
            api.new_page(title, "db123")
            body = json.loads(mock_req.call_args[0][2])
            assert body["parent"] == {"database_id": "db123"}
            assert body["properties"]["Name"]["title"][0]["text"]["content"] == title

    def test_new_page_custom_dict_is_serialised(self):
        api = self._api()
        payload = NotionAPI.build_page_payload(
            "2024-02-29", "db123", {"Date": {"date": {"start": "2024-02-29"}}}
        )
        with patch.object(api, "make_request") as mock_req:
            api.new_page("ignored", "db123", payload)
            body = json.loads(mock_req.call_args[0][2])
            assert body["properties"]["Date"]["date"]["start"] == "2024-02-29"
            assert body["properties"]["Name"]["title"][0]["text"]["content"] == "2024-02-29"

    def test_new_page_custom_string_passthrough(self):
        api = self._api()
        with patch.object(api, "make_request") as mock_req:
            api.new_page("x", "db123", '{"raw": true}')
            assert mock_req.call_args[0][2] == '{"raw": true}'
