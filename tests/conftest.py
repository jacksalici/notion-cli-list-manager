import click
import keyring
import pytest
from keyring.backend import KeyringBackend
from typer.testing import CliRunner

from notion_cli_list_manager.cli import State, app
from notion_cli_list_manager.config import Config, PageIndex


class FakeClient:
    def __init__(self):
        self.pages: dict[str, list[dict]] = {}
        self.props: list[str] = []
        self.created: list[tuple] = []
        self.deleted: list[str] = []
        self.markdowns: dict[str, str] = {}
        self.warnings: list[dict] = []

    def query(self, database_id, filter=None):
        pages = self.pages.get(database_id, [])
        if filter:
            title = filter["title"]["equals"]
            pages = [p for p in pages if p["properties"]["Name"]["title"][0]["plain_text"] == title]
        return pages

    def markdown(self, page_id):
        return self.markdowns[page_id]

    def set_markdown(self, page_id, markdown):
        self.markdowns[page_id] = markdown
        return self.warnings

    def properties(self, database_id):
        return self.props

    def create_page(self, database_id, title, **properties):
        self.created.append((database_id, title, properties))

    def delete_page(self, page_id):
        self.deleted.append(page_id)


class MemoryKeyring(KeyringBackend):
    priority = 1

    def __init__(self):
        self.store = {}

    def get_password(self, service, username):
        return self.store.get((service, username))

    def set_password(self, service, username, password):
        self.store[(service, username)] = password

    def delete_password(self, service, username):
        del self.store[(service, username)]


@pytest.fixture(autouse=True)
def memory_keyring():
    previous = keyring.get_keyring()
    backend = MemoryKeyring()
    keyring.set_keyring(backend)
    yield backend
    keyring.set_keyring(previous)


class FakeEditor:
    """Stands in for click.edit: returns queued results and records each call."""

    def __init__(self):
        self.results: list[str | None] = []
        self.calls: list[tuple] = []

    def __call__(self, text, editor, extension):
        self.calls.append((text, editor, extension))
        return self.results.pop(0)


@pytest.fixture
def editor(monkeypatch):
    fake = FakeEditor()
    monkeypatch.setattr(click, "edit", fake)
    monkeypatch.delenv("EDITOR", raising=False)
    return fake


def make_page(page_id: str, title: str, **props: dict) -> dict:
    return {
        "id": page_id,
        "properties": {"Name": {"type": "title", "title": [{"plain_text": title}]}, **props},
    }


@pytest.fixture
def client():
    return FakeClient()


@pytest.fixture
def state(tmp_path, client):
    config = Config(tmp_path / "config.toml")
    config.token = "secret"
    config.databases["Default"] = {"id": "db1", "properties": ["Name", "Done"]}
    config.databases["Work"] = {"id": "db2"}
    config.save()
    return State(config, PageIndex(tmp_path / "pages.json"), client)


@pytest.fixture
def invoke(state):
    runner = CliRunner()
    return lambda *args, input=None: runner.invoke(app, list(args), obj=state, input=input)
