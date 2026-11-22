import os
import shutil
import time
from datetime import date, timedelta
from typing import Annotated

import click
import typer
from prettytable import PrettyTable

from .client import NotionClient, NotionError
from .config import Config, ConfigError, PageIndex
from .properties import row

app = typer.Typer(
    help="Manage Notion databases from the command line.",
    pretty_exceptions_show_locals=False,
)

show_app = typer.Typer(help="Open files in the editor.")
app.add_typer(show_app, name="show")

Db = Annotated[str | None, typer.Option(help="Database label (default: Default, else the first).")]


class State:
    def __init__(
        self,
        config: Config | None = None,
        index: PageIndex | None = None,
        client: NotionClient | None = None,
    ):
        self.config = config or Config()  # parsed lazily, so a broken file can still be edited
        self.index = index or PageIndex()
        self._client = client

    @property
    def client(self) -> NotionClient:
        if self._client is None:
            self._client = NotionClient(self.config.token)
        return self._client


def edit_text(text: str, extension: str) -> str | None:
    """Open TEXT in $EDITOR (default nano); None if not saved or unchanged."""
    edited = click.edit(text, editor=os.environ.get("EDITOR", "nano"), extension=extension)
    return None if edited is None or edited == text else edited


def parse_indices(text: str) -> list[int]:
    """'1,3:6,9:5:-2' -> [1, 3, 4, 5, 9, 7]"""
    try:
        indices = []
        for part in text.split(","):
            bounds = [int(b) for b in part.split(":")]
            indices += bounds if len(bounds) == 1 else range(*bounds)
        return indices
    except (ValueError, TypeError) as e:
        raise typer.BadParameter(f"invalid index list {text!r}") from e


def pick_properties(available: list[str]) -> list[str]:
    for i, name in enumerate(available):
        typer.echo(f"{i:>3}  {name}")
    indices = typer.prompt(
        "Ordered indices of the properties to show",
        default=f"0:{len(available)}",
        value_proc=parse_indices,
    )
    return list(dict.fromkeys(available[i] for i in indices if 0 <= i < len(available)))


def save_database(state: State, label: str, database_id: str) -> None:
    properties = pick_properties(state.client.properties(database_id))
    state.config.databases[label] = {"id": database_id, "properties": properties}
    state.config.save()
    typer.echo(f"Saved database '{label}'.")


def show(state: State, labels: list[str], columns: list[str]) -> None:
    table = PrettyTable(["#", *columns], align="l")
    table.max_table_width = shutil.get_terminal_size().columns
    ids = []
    for label in labels:
        for page in state.client.query(state.config.database(label)["id"]):
            table.add_row([len(ids), *row(page, columns)])
            ids.append(page["id"])
    state.index.save(ids)
    typer.echo(table)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    db: Db = None,
    all_: Annotated[bool, typer.Option("--all", help="Show every database.")] = False,
):
    """Manage Notion databases from the command line."""
    state = ctx.obj = ctx.obj or State()
    if ctx.invoked_subcommand:
        return
    if all_:
        show(state, list(state.config.databases), ["Name"])
    else:
        label = state.config.resolve(db)
        show(state, [label], state.config.databases[label].get("properties") or ["Name"])


@app.command()
def add(ctx: typer.Context, title: str, db: Db = None):
    """Add a page."""
    label = ctx.obj.config.resolve(db)
    ctx.obj.client.create_page(ctx.obj.config.databases[label]["id"], title)
    typer.echo(f"Added '{title}' to '{label}'.")


@app.command()
def edit(ctx: typer.Context, title: str, db: Db = None):
    """Edit a page's content as markdown; saving the file updates the page."""
    state = ctx.obj
    label = state.config.resolve(db)
    title_filter = {"property": "Name", "title": {"equals": title}}
    pages = state.client.query(state.config.databases[label]["id"], filter=title_filter)
    if len(pages) != 1:
        raise typer.BadParameter(f"{len(pages)} pages titled {title!r} in '{label}', expected 1.")
    page_id = pages[0]["id"]
    edited = edit_text(state.client.markdown(page_id), ".md")
    if edited is None:
        typer.echo("No changes.")
        return
    for warning in state.client.set_markdown(page_id, edited):
        typer.secho(f"Warning: {warning['message']}", err=True, fg="yellow")
    typer.echo(f"Saved '{title}'.")


@show_app.command("configs")
def show_configs(ctx: typer.Context):
    """Edit the config file; it is saved only if it is valid TOML."""
    config = ctx.obj.config
    text = config.text
    while (edited := edit_text(text, ".toml")) is not None:
        try:
            config.data = config.parse(edited)
        except ConfigError as e:
            typer.secho(str(e), err=True, fg="yellow")
            if not typer.confirm("Edit again?", default=True):
                break
            text = edited
            continue
        config.save()
        typer.echo(f"Saved {config.path}.")
        return
    typer.echo("No changes.")


@app.command()
def rm(
    ctx: typer.Context,
    indices: Annotated[str, typer.Argument(metavar="INDEX", help="e.g. 3, 1,4 or 2:6.")],
):
    """Remove pages by their index in the last listing."""
    ids = ctx.obj.index.load()
    for i in parse_indices(indices):
        if not 0 <= i < len(ids):
            typer.secho(f"Index {i} out of range, skipped.", err=True, fg="yellow")
            continue
        ctx.obj.client.delete_page(ids[i])
        typer.echo(f"Removed {i}.")


@app.command("set")
def set_(
    ctx: typer.Context,
    token: Annotated[str, typer.Option(help="Notion integration token.")] = "",
    id: Annotated[str, typer.Option(help="Default database id.")] = "",
):
    """Set the token and the default database."""
    if token:
        ctx.obj.config.token = token
        typer.echo("Token saved to the system keyring.")
    if id:
        save_database(ctx.obj, "Default", id)


@app.command()
def db(
    ctx: typer.Context,
    rm: Annotated[str, typer.Option(help="Label of the database to remove.")] = "",
    label: Annotated[str, typer.Option(help="Label of the database to add (needs --id).")] = "",
    id: Annotated[str, typer.Option(help="Id of the database to add.")] = "",
    prop: Annotated[str, typer.Option(help="Label of the database whose columns to edit.")] = "",
):
    """List, add or remove databases, or edit their columns."""
    state = ctx.obj
    if sum(map(bool, (rm, label, prop))) > 1:
        raise typer.BadParameter("use only one of --rm, --label, --prop")
    if label and not id:
        raise typer.BadParameter("--label requires --id")
    if rm:
        state.config.database(rm)
        del state.config.databases[rm]
        state.config.save()
        typer.echo(f"Removed database '{rm}'.")
    elif label:
        save_database(state, label, id)
    elif prop:
        save_database(state, prop, state.config.database(prop)["id"])
    else:
        typer.echo("\n".join(state.config.databases) or "No databases configured.")


@app.command()
def gen(
    ctx: typer.Context,
    title: Annotated[str | None, typer.Argument(help="Page title (default: the date).")] = None,
    db: Db = None,
    year: int = date.today().year,
    delay: Annotated[float, typer.Option(help="Seconds between requests.")] = 0.4,
):
    """Create one page per day of YEAR."""
    database_id = ctx.obj.config.database(db)["id"]
    first = date(year, 1, 1)
    days = [first + timedelta(d) for d in range((date(year + 1, 1, 1) - first).days)]
    with typer.progressbar(days, label=f"Generating {year}") as bar:
        for day in bar:
            ctx.obj.client.create_page(
                database_id, title or day.isoformat(), Date={"date": {"start": day.isoformat()}}
            )
            time.sleep(delay)


def run() -> None:
    try:
        app()
    except (NotionError, ConfigError) as e:
        typer.secho(f"Error: {e}", err=True, fg="red")
        raise SystemExit(1) from None
