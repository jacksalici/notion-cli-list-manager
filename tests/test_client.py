import pytest
import requests

from notion_cli_list_manager.client import NotionClient, NotionError


class FakeResponse:
    def __init__(self, status=200, body=None, text=""):
        self.status_code, self.ok, self.body, self.text = status, status < 400, body, text

    def json(self):
        if self.body is None:
            raise ValueError("not json")
        return self.body


class FakeSession:
    def __init__(self, *responses):
        self.headers = {}
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def make_client(*responses, token="secret"):
    session = FakeSession(*responses)
    return NotionClient(token, session), session


URL = "https://api.notion.com/v1/"


def sources(*ids):
    return FakeResponse(body={"data_sources": [{"id": i, "name": i} for i in ids]})


@pytest.mark.parametrize("token", ["secret", "Bearer secret"])
def test_headers(token):
    _, session = make_client(token=token)
    assert session.headers == {"Authorization": "Bearer secret", "Notion-Version": "2026-03-11"}


def test_missing_token():
    with pytest.raises(NotionError, match="No token"):
        NotionClient("")


def test_data_source_is_resolved_once_per_database():
    client, session = make_client(sources("ds1"), sources("ds2"))
    assert [client.data_source(d) for d in ("db1", "db1", "db2")] == ["ds1", "ds1", "ds2"]
    assert [url for _, url, _ in session.calls] == [URL + "databases/db1", URL + "databases/db2"]


@pytest.mark.parametrize("ids", [(), ("a", "b")])
def test_data_source_requires_exactly_one(ids):
    client, _ = make_client(sources(*ids))
    with pytest.raises(NotionError, match=f"has {len(ids)} data sources"):
        client.data_source("db")


def test_properties():
    client, session = make_client(
        sources("ds"), FakeResponse(body={"properties": {"Name": {}, "Date": {}}})
    )
    assert client.properties("db") == ["Name", "Date"]
    assert session.calls[1][:2] == ("GET", URL + "data_sources/ds")


def test_query_follows_pagination():
    client, session = make_client(
        sources("ds"),
        FakeResponse(body={"results": [{"id": 1}], "has_more": True, "next_cursor": "c"}),
        FakeResponse(body={"results": [{"id": 2}], "has_more": False}),
    )
    assert client.query("db") == [{"id": 1}, {"id": 2}]
    queries = session.calls[1:]
    assert {(m, u) for m, u, _ in queries} == {("POST", URL + "data_sources/ds/query")}
    assert [kw["json"] for _, _, kw in queries] == [{}, {"start_cursor": "c"}]


def test_create_page_body():
    client, session = make_client(sources("ds"), FakeResponse(body={"id": "p"}))
    title = 'say "hi" \\ 🚀'
    client.create_page("db", title, Date={"date": {"start": "2024-01-01"}})
    method, url, kwargs = session.calls[1]
    assert (method, url) == ("POST", URL + "pages")
    assert kwargs["json"] == {
        "parent": {"type": "data_source_id", "data_source_id": "ds"},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "Date": {"date": {"start": "2024-01-01"}},
        },
    }


def test_delete_page_moves_it_to_trash():
    client, session = make_client(FakeResponse(body={}))
    client.delete_page("p1")
    assert session.calls == [
        ("PATCH", URL + "pages/p1", {"timeout": 30, "json": {"in_trash": True}})
    ]


@pytest.mark.parametrize(
    "response, message",
    [
        (FakeResponse(401, {"message": "unauthorized"}), "HTTP 401: unauthorized"),
        (FakeResponse(502, text="Bad Gateway"), "HTTP 502: Bad Gateway"),
        (requests.ConnectionError("offline"), "offline"),
    ],
)
def test_errors(response, message):
    client, _ = make_client(response)
    with pytest.raises(NotionError, match=message):
        client.properties("db")


def test_query_sends_filter_on_every_page():
    flt = {"property": "Name", "title": {"equals": "T"}}
    client, session = make_client(
        sources("ds"),
        FakeResponse(body={"results": [], "has_more": True, "next_cursor": "c"}),
        FakeResponse(body={"results": [], "has_more": False}),
    )
    client.query("db", filter=flt)
    assert [kw["json"] for _, _, kw in session.calls[1:]] == [
        {"filter": flt},
        {"filter": flt, "start_cursor": "c"},
    ]


def page_markdown(text, truncated=False, **extra):
    body = {"object": "page_markdown", "markdown": text, "truncated": truncated}
    return FakeResponse(body={**body, "unknown_block_ids": [], **extra})


def test_markdown():
    client, session = make_client(page_markdown("# Hi"))
    assert client.markdown("p1") == "# Hi"
    assert session.calls[0] == (
        "GET",
        URL + "pages/p1/markdown",
        {"timeout": 30, "params": {"markdown_version": "v2"}},
    )


def test_markdown_refuses_truncated_pages():
    client, _ = make_client(page_markdown("partial", truncated=True))
    with pytest.raises(NotionError, match="too large"):
        client.markdown("p1")


@pytest.mark.parametrize("warnings", [[], [{"code": "unsupported_tag", "message": "x"}]])
def test_set_markdown(warnings):
    extra = {"warnings": warnings} if warnings else {}
    client, session = make_client(page_markdown("new", **extra))
    assert client.set_markdown("p1", "new") == warnings
    method, url, kwargs = session.calls[0]
    assert (method, url) == ("PATCH", URL + "pages/p1/markdown")
    assert kwargs["json"] == {
        "markdown_version": "v2",
        "type": "replace_content",
        "replace_content": {"new_str": "new"},
    }
