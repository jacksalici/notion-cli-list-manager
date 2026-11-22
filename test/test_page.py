from unittest.mock import patch, MagicMock
import pytest
from notion_cli_list_manager.page import NotionPage


class TestNotionPage:
    @pytest.fixture
    def page(self):
        with patch("notion_cli_list_manager.page.NotionAPI") as mock_api_cls:
            mock_api = MagicMock()
            mock_api_cls.return_value = mock_api
            p = NotionPage()
            assert p.api is mock_api
            yield p

    @pytest.fixture
    def sample_page_data(self):
        return {
            "properties": {
                "Name": {
                    "type": "title",
                    "title": [{"text": {"content": "Test Page"}}],
                },
                "Description": {
                    "type": "rich_text",
                    "rich_text": [{"plain_text": "A description"}],
                },
                "Status": {
                    "type": "select",
                    "select": {"name": "Done"},
                },
                "Tags": {
                    "type": "multi_select",
                    "multi_select": [{"name": "work"}, {"name": "urgent"}],
                },
                "Created": {
                    "type": "created_time",
                    "created_time": "2024-01-01T00:00:00.000Z",
                },
                "Done": {
                    "type": "checkbox",
                    "checkbox": True,
                },
                "Score": {
                    "type": "number",
                    "number": 42,
                },
            }
        }

    def test_extract_title(self, page, sample_page_data):
        props = ["Index", "Name"]
        row = page._extract_property_values(sample_page_data, props, 0)
        assert row["Name"] == "Test Page"
        assert row["Index"] == 0

    def test_extract_rich_text(self, page, sample_page_data):
        props = ["Index", "Description"]
        row = page._extract_property_values(sample_page_data, props, 0)
        assert row["Description"] == "A description"

    def test_extract_select(self, page, sample_page_data):
        props = ["Index", "Status"]
        row = page._extract_property_values(sample_page_data, props, 0)
        assert row["Status"] == "Done"

    def test_extract_multi_select(self, page, sample_page_data):
        props = ["Index", "Tags"]
        row = page._extract_property_values(sample_page_data, props, 0)
        assert row["Tags"] == "work urgent"

    def test_extract_checkbox_true(self, page, sample_page_data):
        props = ["Index", "Done"]
        row = page._extract_property_values(sample_page_data, props, 0)
        assert row["Done"] == "[x]"

    def test_extract_checkbox_false(self, page):
        page_data = {
            "properties": {"Active": {"type": "checkbox", "checkbox": False}}
        }
        props = ["Index", "Active"]
        row = page._extract_property_values(page_data, props, 0)
        assert row["Active"] == "[ ]"

    def test_extract_number(self, page, sample_page_data):
        props = ["Index", "Score"]
        row = page._extract_property_values(sample_page_data, props, 0)
        assert row["Score"] == "42"

    def test_extract_missing_property(self, page, sample_page_data):
        props = ["Index", "NonExistent"]
        row = page._extract_property_values(sample_page_data, props, 0)
        assert row["NonExistent"] == ""

    def test_extract_date(self, page):
        page_data = {
            "properties": {
                "Date": {
                    "type": "date",
                    "date": {"start": "2024-01-15", "end": "2024-01-20"},
                }
            }
        }
        props = ["Index", "Date"]
        row = page._extract_property_values(page_data, props, 0)
        assert "2024-01-15" in row["Date"]
        assert "2024-01-20" in row["Date"]
        assert "->" in row["Date"]

    def test_extract_date_no_end(self, page):
        page_data = {
            "properties": {
                "Date": {
                    "type": "date",
                    "date": {"start": "2024-01-15"},
                }
            }
        }
        props = ["Index", "Date"]
        row = page._extract_property_values(page_data, props, 0)
        assert row["Date"] == "2024-01-15"

    def test_extract_date_none(self, page):
        page_data = {"properties": {"Date": {"type": "date", "date": None}}}
        props = ["Index", "Date"]
        row = page._extract_property_values(page_data, props, 0)
        assert row["Date"] == ""

    def test_extract_formula(self, page):
        page_data = {
            "properties": {
                "Calc": {
                    "type": "formula",
                    "formula": {"string": "result"},
                }
            }
        }
        props = ["Index", "Calc"]
        row = page._extract_property_values(page_data, props, 0)
        assert row["Calc"] == "result"

    def test_extract_formula_empty(self, page):
        page_data = {
            "properties": {
                "Calc": {"type": "formula", "formula": None}
            }
        }
        props = ["Index", "Calc"]
        row = page._extract_property_values(page_data, props, 0)
        assert row["Calc"] == ""

    def test_extract_people(self, page):
        page_data = {
            "properties": {
                "Assign": {
                    "type": "people",
                    "people": [{"name": "Alice"}, {"name": "Bob"}],
                }
            }
        }
        props = ["Index", "Assign"]
        row = page._extract_property_values(page_data, props, 0)
        assert row["Assign"] == "Alice Bob"

    def test_extract_files(self, page):
        page_data = {
            "properties": {
                "Attach": {
                    "type": "files",
                    "files": [{"name": "doc.pdf"}, {"name": "img.png"}],
                }
            }
        }
        props = ["Index", "Attach"]
        row = page._extract_property_values(page_data, props, 0)
        assert row["Attach"] == "doc.pdf img.png"

    def test_extract_created_by(self, page):
        page_data = {
            "properties": {
                "Author": {
                    "type": "created_by",
                    "created_by": {"name": "John"},
                }
            }
        }
        props = ["Index", "Author"]
        row = page._extract_property_values(page_data, props, 0)
        assert row["Author"] == "John"

    def test_extract_url(self, page):
        page_data = {
            "properties": {
                "Link": {
                    "type": "url",
                    "url": "https://example.com",
                }
            }
        }
        props = ["Index", "Link"]
        row = page._extract_property_values(page_data, props, 0)
        assert row["Link"] == "https://example.com"

    def test_extract_phone(self, page):
        page_data = {
            "properties": {
                "Phone": {
                    "type": "phone_number",
                    "phone_number": "+1-555-1234",
                }
            }
        }
        props = ["Index", "Phone"]
        row = page._extract_property_values(page_data, props, 0)
        assert row["Phone"] == "+1-555-1234"

    def test_extract_email(self, page):
        page_data = {
            "properties": {
                "Email": {
                    "type": "email",
                    "email": "test@example.com",
                }
            }
        }
        props = ["Index", "Email"]
        row = page._extract_property_values(page_data, props, 0)
        assert row["Email"] == "test@example.com"

    def test_show_properties(self, page):
        table = page.show_properties(["Name", "Date", "Tag"])
        assert "Name" in str(table)
        assert "Date" in str(table)
        assert "Tag" in str(table)

    def test_add_page(self, page):
        with patch("notion_cli_list_manager.page.TomlHelper.get_db_id", return_value="db123"):
            page.add("Test Title", "Default")
            page.api.new_page.assert_called_once_with("Test Title", "db123")

    def test_add_page_db_not_found(self, page):
        with patch("notion_cli_list_manager.page.TomlHelper.get_db_id", return_value=""):
            page.add("Test Title", "MissingDB")
            page.api.new_page.assert_not_called()

    def test_remove_page(self, page):
        pages_dict = {"0": {"id": "page_id_1"}, "1": {"id": "page_id_2"}}
        with patch("notion_cli_list_manager.page.TomlHelper.get_dict", return_value=pages_dict):
            page.remove([0, 1])
            assert page.api.remove_page.call_count == 2
            page.api.remove_page.assert_any_call("page_id_1")
            page.api.remove_page.assert_any_call("page_id_2")

    def test_set_token(self, page):
        with patch("notion_cli_list_manager.page.TomlHelper.get_dict", return_value={}):
            with patch("notion_cli_list_manager.page.TomlHelper.set_dict", return_value=True) as mock_set:
                page.set_token("new_token")
                mock_set.assert_called_once()
                args = mock_set.call_args[0]
                assert args[0]["token"] == "new_token"

    def test_set_database(self, page):
        with patch("notion_cli_list_manager.page.TomlHelper.get_dict", return_value={"databases": {}}):
            with patch("notion_cli_list_manager.page.TomlHelper.set_dict", return_value=True):
                page.api.get_db_props.return_value = {"Name": {}, "Date": {}}
                props = page.set_database("TestDB", "test_id_123")
                assert "Name" in props
                assert "Date" in props

    def test_set_properties(self, page):
        with patch("notion_cli_list_manager.page.TomlHelper.get_dict", return_value={
            "databases": {"Default": {"id": "db123"}}
        }):
            with patch("notion_cli_list_manager.page.TomlHelper.set_dict", return_value=True) as mock_set:
                page.set_properties("Default", ["Name", "Date"])
                args = mock_set.call_args[0]
                assert args[0]["databases"]["Default"]["properties"] == ["Name", "Date"]

    def test_rm_database(self, page):
        with patch("notion_cli_list_manager.page.TomlHelper.get_dict", return_value={
            "databases": {"Default": {}, "Work": {}}
        }):
            with patch("notion_cli_list_manager.page.TomlHelper.set_dict", return_value=True) as mock_set:
                page.rm_database("Work")
                args = mock_set.call_args[0]
                assert "Work" not in args[0]["databases"]
                assert "Default" in args[0]["databases"]

    def test_rm_database_not_found(self, page):
        with patch("notion_cli_list_manager.page.TomlHelper.get_dict", return_value={
            "databases": {"Default": {}}
        }):
            with patch("notion_cli_list_manager.page.TomlHelper.set_dict") as mock_set:
                page.rm_database("Missing")
                mock_set.assert_not_called()
