#!/usr/bin/env python3
import typer
import page
from utils import api_helper

pages = []

app = typer.Typer()
 
@app.command()
def add(title: str):
    api_helper.new_page(api_helper, title)

@app.command()
def get():
    api_helper.get_pages(api_helper)

if __name__ == "__main__":
    app()