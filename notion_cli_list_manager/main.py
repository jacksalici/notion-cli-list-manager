#!/usr/bin/env python3
import typer
from .page import page

def string_parser(string: str):

    pars_raw = string.split(',')

    indexes = []

    for pars_temp in pars_raw:
        pars = pars_temp.split(':')

        if len(pars) == 1:
            indexes.append(int(pars[0]))
        else:
  
            if len(pars) == 2:
                pars.append('1')
        
            pars = [int(i) for i in pars]
            for i in range(pars[0], pars[1], pars[2]):
                indexes.append(i)

    return indexes

app = typer.Typer()
 
@app.command()
def add(title: str = typer.Argument(..., help="The title of the page."),
        db: str = typer.Option("Default", help="To add the page to a custom database (Leave the option blank and the default database will be used.)", show_default=False)):
    """
    Add an entry to your database.
    """
    page.add(title, db)

@app.command()
def rm(string_of_index: str = typer.Argument(..., metavar="INDEX", help="The index of the page to remove.")):
    """
    Remove a database entry. Use this after the "list" command.
    """
    page.remove(string_parser(string_of_index))

@app.command()
def set(
        token: str = typer.Option("", help="The API token"),
        id: str = typer.Option("", help="The database id")
    ):
    """
    Set the personal Notion API Token and the default Database id.  
    """

    
    if token != "":
        page.set_token(token)
    
    if id != "":
        page.set_database("Default", id)

@app.command()
def db(
    rm: str = typer.Option("", help="Remove a database from the manager.", metavar="LABEL"),
    label: str = typer.Option("", help="Add a database from the manager.", metavar="LABEL"),
    id: str = typer.Option("", help="The database id.") 
    ):
    """
    Display the databases saved on the manager. To add or to remove a database here does not cause the actual creation or deletion on Notion. 
    """
    if rm == "" and label == "" and id == "":
        page.show_databases()
    elif rm != "" and (label != "" or id != ""):
        typer.echo("You cannot remove and add a databese at the same time.")
    elif rm != "":
        page.rm_database(rm)
    else:
        page.set_database(label, id)
    
      

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context,
        db: str = typer.Option("Default", help="Display the list for a specific database"),
        all: bool = typer.Option(False, help="Display all the lists.")):
    """
    The Notion Cli List Manager allows you to manage - as you can imagine - Notion Lists.
    Use the set command to initialize the token and the default database id.
    """
    if ctx.invoked_subcommand is None:
        if(all):
            page.all_by_all()    
        else:
            page.all(db)


if __name__=="__main__":
    app()







