#!/usr/bin/env python3
import typer
import page


app = typer.Typer()
 
@app.command()
def add(title: str):
    page.add(title)

@app.command()
def all():
    page.all()



if __name__ == "__main__":
    app()