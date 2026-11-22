from collections.abc import Callable
from typing import Any


def _text(value: list | None) -> str:
    return "".join(t.get("plain_text") or t.get("text", {}).get("content", "") for t in value or [])


def _name(value: dict | None) -> str:
    return (value or {}).get("name", "")


def _names(value: list | None) -> str:
    return " ".join(_name(v) for v in value or [])


def _date(value: dict | None) -> str:
    return " -> ".join(filter(None, (value.get("start"), value.get("end")))) if value else ""


FORMATTERS: dict[str, Callable[[Any], str]] = {
    "title": _text,
    "rich_text": _text,
    "select": _name,
    "status": _name,
    "created_by": _name,
    "last_edited_by": _name,
    "multi_select": _names,
    "people": _names,
    "files": _names,
    "date": _date,
    "checkbox": lambda v: "[x]" if v else "[ ]",
    "formula": lambda v: format_property(v) if v else "",
}


def format_property(prop: dict) -> str:
    kind = prop.get("type")
    value = prop.get(kind)
    if kind in FORMATTERS:
        return FORMATTERS[kind](value)
    return "" if value is None or isinstance(value, dict | list) else str(value)


def row(page: dict, columns: list[str]) -> list[str]:
    props = page.get("properties", {})
    return [format_property(props[c]) if c in props else "" for c in columns]
