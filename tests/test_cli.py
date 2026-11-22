import pytest
import typer
from conftest import make_page

from notion_cli_list_manager import cli
from notion_cli_list_manager.client import NotionError
from notion_cli_list_manager.config import Config, ConfigError

DONE = {"type": "checkbox", "checkbox": True}


@pytest.mark.parametrize(
    "text, expected",
    [
        ("5", [5]),
        ("1,2,3", [1, 2, 3]),
        ("1:4", [1, 2, 3]),
        ("1:10:3", [1, 4, 7]),
        ("0,2:4,9", [0, 2, 3, 9]),
        ("5:1:-2", [5, 3]),
        (" 1, 2 ", [1, 2]),
    ],
)
def test_parse_indices(text, expected):
    assert cli.parse_indices(text) == expected


@pytest.mark.parametrize("text", ["", "a", "1:2:3:4", "1:5:0"])
def test_parse_indices_invalid(text):
    with pytest.raises(typer.BadParameter):
        cli.parse_indices(text)


def test_list_default_uses_configured_columns(invoke, client, state):
    client.pages["db1"] = [make_page("p0", "Buy milk", Done=DONE), make_page("p1", "Call")]
    result = invoke()
    assert result.exit_code == 0
    lines = result.output.splitlines()
    assert lines[1].split("|")[1:-1] == [" # ", " Name     ", " Done "]
    assert "| 0 | Buy milk | [x]  |" in lines
    assert "| 1 | Call     |      |" in lines
    assert state.index.load() == ["p0", "p1"]


def test_list_all_numbers_pages_across_databases(invoke, client, state):
    client.pages = {"db1": [make_page("a", "A")], "db2": [make_page("b", "B")]}
    assert invoke("--all").exit_code == 0
    assert state.index.load() == ["a", "b"]


def test_list_unknown_database(invoke):
    assert isinstance(invoke("--db", "Nope").exception, ConfigError)


def test_add(invoke, client):
    assert invoke("add", "Task", "--db", "Work").exit_code == 0
    assert client.created == [("db2", "Task", {})]


def test_rm_uses_last_listing_and_skips_out_of_range(invoke, client, state):
    state.index.save(["p0", "p1", "p2"])
    result = invoke("rm", "0,2,7")
    assert result.exit_code == 0
    assert client.deleted == ["p0", "p2"]
    assert "Index 7 out of range" in result.output


def test_rm_invalid_indices(invoke):
    assert invoke("rm", "x").exit_code == 2


def test_set_token_persists(invoke, state):
    assert invoke("set", "--token", "new").exit_code == 0
    assert Config(state.config.path).token == "new"


def test_set_id_prompts_for_properties(invoke, client, state):
    client.props = ["Name", "Date", "Tags"]
    assert invoke("set", "--id", "db9", input="2,0,2\n").exit_code == 0
    saved = Config(state.config.path).database("Default")
    assert saved == {"id": "db9", "properties": ["Tags", "Name"]}


def test_db_prop_reprompts_on_invalid_input(invoke, client, state):
    client.props = ["Name", "Date"]
    assert invoke("db", "--prop", "Work", input="oops\n1\n").exit_code == 0
    assert Config(state.config.path).database("Work")["properties"] == ["Date"]


def test_db_lists_labels(invoke):
    result = invoke("db")
    assert result.output.split() == ["Default", "Work"]


def test_db_rm(invoke, state):
    assert invoke("db", "--rm", "Work").exit_code == 0
    assert list(Config(state.config.path).databases) == ["Default"]


@pytest.mark.parametrize("args", [["--label", "X"], ["--rm", "Work", "--prop", "Work"]])
def test_db_rejects_bad_option_combinations(invoke, args):
    assert invoke("db", *args).exit_code == 2


@pytest.mark.parametrize("year, days", [(2024, 366), (2023, 365), (1900, 365), (2000, 366)])
def test_gen_creates_one_page_per_day(invoke, client, year, days):
    assert invoke("gen", "--year", str(year), "--delay", "0").exit_code == 0
    assert len(client.created) == days
    db_id, title, props = client.created[-1]
    assert (db_id, title) == ("db1", f"{year}-12-31")
    assert props == {"Date": {"date": {"start": f"{year}-12-31"}}}


def test_gen_custom_title(invoke, client):
    invoke("gen", "Journal", "--year", "2024", "--delay", "0")
    assert {title for _, title, _ in client.created} == {"Journal"}


@pytest.mark.parametrize("error", [NotionError("boom"), ConfigError("boom")])
def test_run_reports_errors(monkeypatch, capsys, error):
    def fail():
        raise error

    monkeypatch.setattr(cli, "app", fail)
    with pytest.raises(SystemExit) as exit_info:
        cli.run()
    assert exit_info.value.code == 1
    assert "Error: boom" in capsys.readouterr().err
