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


@pytest.mark.parametrize("token", ["secret", "Bearer secret"])
def test_headers(token):
    _, session = make_client(token=token)
    assert session.headers == {"Authorization": "Bearer secret", "Notion-Version": "2021-08-16"}


def test_missing_token():
    with pytest.raises(NotionError, match="No token"):
        NotionClient("")


def test_create_page_body():
    client, session = make_client(FakeResponse(body={"id": "p"}))
    title = 'say "hi" \\ 🚀'
    client.create_page("db", title, Date={"date": {"start": "2024-01-01"}})
    method, url, kwargs = session.calls[0]
    assert (method, url) == ("POST", "https://api.notion.com/v1/pages")
    assert kwargs["json"] == {
        "parent": {"database_id": "db"},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "Date": {"date": {"start": "2024-01-01"}},
        },
    }


def test_query_follows_pagination():
    client, session = make_client(
        FakeResponse(body={"results": [{"id": 1}], "has_more": True, "next_cursor": "c"}),
        FakeResponse(body={"results": [{"id": 2}], "has_more": False}),
    )
    assert client.query("db") == [{"id": 1}, {"id": 2}]
    assert [kw["json"] for _, _, kw in session.calls] == [{}, {"start_cursor": "c"}]


def test_properties():
    client, _ = make_client(FakeResponse(body={"properties": {"Name": {}, "Date": {}}}))
    assert client.properties("db") == ["Name", "Date"]


def test_delete_page():
    client, session = make_client(FakeResponse(body={}))
    client.delete_page("p1")
    assert session.calls[0][:2] == ("DELETE", "https://api.notion.com/v1/blocks/p1")


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
