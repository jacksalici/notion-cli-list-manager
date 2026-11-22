import pytest
from notion_cli_list_manager.main import parse_index_string


class TestParseIndexString:
    def test_single_index(self):
        assert parse_index_string("5") == [5]

    def test_multiple_indices(self):
        assert parse_index_string("1,2,3") == [1, 2, 3]

    def test_range(self):
        assert parse_index_string("1:5") == [1, 2, 3, 4]

    def test_range_with_step(self):
        assert parse_index_string("1:10:2") == [1, 3, 5, 7, 9]

    def test_mixed_single_and_ranges(self):
        assert parse_index_string("0,2:5,9") == [0, 2, 3, 4, 9]

    def test_single_element_range(self):
        assert parse_index_string("3:4") == [3]

    def test_negative_step(self):
        assert parse_index_string("5:1:-1") == [5, 4, 3, 2]

    def test_empty_string(self):
        with pytest.raises(ValueError):
            parse_index_string("")

    def test_whitespace_stripped_by_int(self):
        assert parse_index_string("1, 2, 3") == [1, 2, 3]

    def test_invalid_input(self):
        with pytest.raises(ValueError):
            parse_index_string("abc")
