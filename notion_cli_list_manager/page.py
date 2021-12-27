import typer
import json
from .utils import api_helper, file_helper, toml_helper
from prettytable import PrettyTable

class page():

    def add(title, database):
        api_helper.new_page(api_helper, title, database)

    def all_by_all():
        index = 0
        x = PrettyTable()
        x.field_names = ["Index", "Title"]
        x.align["Index"] = "r"
        x.align["Title"] = "l"
        
        for key in toml_helper.get_db_keys():
            index, x = page.query(key, index, x)
        typer.echo(x)
    
    def all(database):
        x = PrettyTable()
        x.field_names = ["Index", "Title"]
        x.align["Index"] = "r"
        x.align["Title"] = "l"
        index, x = page.query(database, x = x)
        typer.echo(x)

    def query(database, index = 0, x = PrettyTable):
        r = api_helper.get_pages(api_helper, database)
        pages_dict = {}

        if type(r) is dict:
            if r["object"] == "list":
                for page in r["results"]:
                        path = page.get("properties").get("Name").get("title")
                            
                        if len(path) > 0:
                            x.add_row([ str(index), path[0].get("text").get("content")])
                            pages_dict[str(index)] = page
                            index+=1

            elif r["object"] == "error":
                typer.echo("Error:\t" + str(r["message"]))
                

        file_helper.set(file_helper.pages_file, json.dumps(pages_dict))

        return index, x


    def remove(list_of_indexes):
        pages_dict = file_helper.get_dict(file_helper.pages_file)
        for index in list_of_indexes:
            p = pages_dict.get(str(index))
            if type(p) == dict:
                api_helper.remove_page(api_helper, p.get("id"))

    def set_token(token):
        dict = toml_helper.get_dict()
        dict["token"] = token
        toml_helper.set_dict(dict)

    def set_database(key, id):
        db_dict = toml_helper.get_dict()
        
        if "databases" not in db_dict.keys():
            db_dict["databases"] = {}
        
        db_dict.get("databases")[key] = {"id": id} 
        
        toml_helper.set_dict(db_dict)

    def show_databases():
        list = toml_helper.get_db_keys()
        for label in list:
            typer.echo("\t" + label)

    def rm_database(label):
        dict = toml_helper.get_dict()
        r = dict.get("databases").pop(label)
        toml_helper.set_dict(dict)

    
