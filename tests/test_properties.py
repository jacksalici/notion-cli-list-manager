import pytest

from notion_cli_list_manager.properties import format_property, row


def prop(kind, value):
    return {"type": kind, kind: value}


@pytest.mark.parametrize(
    "p, expected",
    [
        (prop("title", [{"plain_text": "Hello "}, {"plain_text": "world"}]), "Hello world"),
        (prop("title", [{"text": {"content": "fallback"}}]), "fallback"),
        (prop("rich_text", [{"plain_text": "a"}, {"plain_text": "b"}]), "ab"),
        (prop("rich_text", []), ""),
        (prop("select", {"name": "Done"}), "Done"),
        (prop("select", None), ""),
        (prop("status", {"name": "In progress"}), "In progress"),
        (prop("multi_select", [{"name": "work"}, {"name": "urgent"}]), "work urgent"),
        (prop("people", [{"name": "Alice"}, {"name": "Bob"}]), "Alice Bob"),
        (prop("files", [{"name": "doc.pdf"}]), "doc.pdf"),
        (prop("created_by", {"name": "John"}), "John"),
        (prop("checkbox", True), "[x]"),
        (prop("checkbox", False), "[ ]"),
        (prop("date", {"start": "2024-01-15", "end": "2024-01-20"}), "2024-01-15 -> 2024-01-20"),
        (prop("date", {"start": "2024-01-15", "end": None}), "2024-01-15"),
        (prop("date", None), ""),
        (prop("formula", prop("string", "result")), "result"),
        (prop("formula", prop("number", 3)), "3"),
        (prop("formula", prop("date", {"start": "2024-01-01"})), "2024-01-01"),
        (prop("formula", None), ""),
        (prop("number", 42), "42"),
        (prop("number", None), ""),
        (prop("url", "https://example.com"), "https://example.com"),
        (prop("email", "a@b.c"), "a@b.c"),
        (prop("phone_number", "+1-555"), "+1-555"),
        (prop("created_time", "2024-01-01T00:00:00.000Z"), "2024-01-01T00:00:00.000Z"),
        (prop("relation", [{"id": "x"}]), ""),
        (prop("rollup", {"type": "array", "array": []}), ""),
    ],
)
def test_format_property(p, expected):
    assert format_property(p) == expected


def test_row_keeps_column_order_and_fills_missing():
    page = {"properties": {"Name": prop("title", [{"plain_text": "T"}]), "N": prop("number", 1)}}
    assert row(page, ["N", "Missing", "Name"]) == ["1", "", "T"]
