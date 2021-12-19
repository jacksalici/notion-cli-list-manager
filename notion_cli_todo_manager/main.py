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
def add(title: str):
    page.add(title)

@app.command()
def all():
    page.all()

@app.command()
def rm(string_of_index: str):
    page.remove(string_parser(string_of_index))

@app.command()
def set(
    token: str,
    db: str
):
    page.set_database(db)
    page.set_token(token)




if __name__=="__main__":
    app()







