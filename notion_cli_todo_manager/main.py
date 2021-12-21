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
def add(title: str, database: str = typer.Option("Default")):
    page.add(title, database)

@app.command()
def all(database: str = typer.Option("Default"), verbose: bool = typer.Option(False)):
    if(verbose):
        page.all_by_all()    
    else:
        page.all(database)

@app.command()
def rm(string_of_index: str):
    page.remove(string_parser(string_of_index))

@app.command()
def set(
    token: str = typer.Option(""),
    key: str = typer.Option("Default"),
    id: str = typer.Option(""),
):
    if token != "":
        page.set_token(token)
    
    if id != "":
        page.set_database(key, id)

        



if __name__=="__main__":
    app()







