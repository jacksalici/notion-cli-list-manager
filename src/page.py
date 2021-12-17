import typer
import json
from utils import api_helper, file_helper


def add(title):
    api_helper.new_page(api_helper, title)

def all():
    r = api_helper.get_pages(api_helper)
    pages_dict = {}
    index = 0
    
    for page in r["results"]:
        path = page.get("properties").get("Name").get("title")
            
        if len(path) > 0:
            typer.echo("\t" + str(index) + "\t" + path[0].get("text").get("content"))
            index+=1
            pages_dict[str(index)] = page

    file_helper.set(file_helper.pages_file, pages_dict)

def remove(list_of_indexes):
    
    pages_dict = {"dict" : file_helper.get(file_helper.pages_file)}
    for index in list_of_indexes:
        p = pages_dict.get("dict").get(str(index))
        if type(p) == dict:
            api_helper.remove_page(api_helper, p.get("id"))

