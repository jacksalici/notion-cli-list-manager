#!/usr/bin/env python3
import typer
from typing import Optional
from .page import page

app = typer.Typer(help="Notion CLI List Manager - manage Notion databases and pages from the command line.")

def parse_index_string(string: str) -> list[int]:
    """Parse a string of indices into a list of integers.
    
    Examples:
        "1,2,3" -> [1, 2, 3]
        "1:5" -> [1, 2, 3, 4]
        "1:10:2" -> [1, 3, 5, 7, 9]
    """
    indices = []
    
    for segment in string.split(','):
        parts = segment.split(':')
        
        if len(parts) == 1:
            # Single index
            indices.append(int(parts[0]))
        else:
            # Range with optional step
            start = int(parts[0])
            end = int(parts[1])
            step = int(parts[2]) if len(parts) >= 3 else 1
            
            indices.extend(range(start, end, step))
    
    return indices

def show_and_select_properties(properties: list, label: str) -> None:
    """Display properties and prompt user to select which ones to use."""
    try:
        # Show the available properties
        typer.echo(page.show_properties(properties))
        
        # Prompt user for selection
        typer.secho("Insert the ordered list of indexes of the properties you want to display.", bold=True)
        prompt_msg = "Eg: \"2,3,0\". Default:"
        default_val = f"0:{len(properties)}"
        indices_string = typer.prompt(prompt_msg, default=default_val, type=str)
        
        # Parse and validate selection
        indices = parse_index_string(indices_string)
        new_properties = []
        
        for index in indices:
            if index < 0 or index >= len(properties):
                typer.secho(f"Index {index} is out of bounds.", err=True, fg='yellow')
                continue
                
            property_name = properties[index]
            
            if property_name == "Index":
                typer.secho("Property cannot be named 'Index', please change it.", err=True, fg='yellow')
            elif property_name in new_properties:
                typer.secho("Property names must be unique.", err=True, fg='yellow')
            else:
                new_properties.append(property_name)
        
        # Save the selected properties
        if new_properties:
            page.set_properties(label, new_properties)
            typer.echo(f"Selected {len(new_properties)} properties for database '{label}'")
        else:
            typer.secho("No valid properties selected.", err=True, fg='yellow')
            
    except Exception as e:
        typer.secho(f"Error during property selection: {e}", err=True, fg='yellow')

@app.command()
def add(
    title: str = typer.Argument(..., help="The title of the page."),
    db: str = typer.Option("Default", help="Database to add the page to (default: Default)")
):
    """Add a new page to a Notion database."""
    page.add(title, db)
    typer.echo(f"Added page '{title}' to database '{db}'")

@app.command()
def gen(
    title: str = typer.Argument(..., help="Base title for generated pages"),
    db: str = typer.Option("Default", help="Database to add pages to (default: Default)"),
    year: str = typer.Option("2023", help="Year to generate pages for")
):
    """Generate pages for each day of a year."""
    typer.echo(f"Generating daily pages for {year} with title base '{title}'")
    page.generate_year_pages(title, db, year)

@app.command()
def rm(
    string_of_index: str = typer.Argument(..., metavar="INDEX", help="Index or range of indices to remove (e.g., '1,2,3' or '1:5')")
):
    """Remove pages by their index."""
    indices = parse_index_string(string_of_index)
    if indices:
        typer.echo(f"Removing pages with indices: {indices}")
        page.remove(indices)
    else:
        typer.secho("No valid indices provided.", err=True, fg='yellow')

@app.command()
def set(
    token: str = typer.Option("", help="Notion API token"),
    id: str = typer.Option("", help="Default database ID")
):
    """Set Notion API token and default database ID."""
    if token:
        page.set_token(token)
        typer.echo("API token has been set")
    
    if id:
        properties = page.set_database("Default", id)
        if properties:
            show_and_select_properties(properties, "Default")

@app.command()
def db(
    rm: str = typer.Option("", help="Remove a database by label"),
    label: str = typer.Option("", help="Label for adding a new database"),
    id: str = typer.Option("", help="ID for adding a new database"),
    prop: str = typer.Option("", help="Set properties for a database")
):
    """Manage databases in the configuration."""
    # Validate inputs to prevent conflicts
    options_count = sum(1 for opt in [rm, label, prop] if opt)
    
    if options_count > 1:
        typer.secho("Please use only one option at a time.", err=True, fg='yellow')
        return
    
    # Handle different operations
    if rm:
        page.rm_database(rm)
    elif label and id:
        properties = page.set_database(label, id)
        if properties:
            show_and_select_properties(properties, label)
    elif prop:
        properties = page.get_properties(prop)
        if properties:
            show_and_select_properties(properties, prop)
    else:
        # Default: show all databases
        page.show_databases()

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    db: str = typer.Option("Default", help="Display pages for a specific database"),
    all: bool = typer.Option(False, help="Display pages from all databases")
):
    """
    Notion CLI List Manager - manage your Notion databases and pages from the command line.
    
    Use the 'set' command to initialize with your API token and default database ID.
    """
    if ctx.invoked_subcommand is None:
        if all:
            page.all_by_all()
        else:
            page.all(db)

if __name__ == "__main__":
    app()