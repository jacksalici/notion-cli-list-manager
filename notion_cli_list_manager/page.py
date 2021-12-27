import typer
from .utils import api_helper, toml_helper
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
        pages_dict = {}
        for key in toml_helper.get_db_keys():
            index, x, pages_dict = page.query(key, index, x, pages_dict)
        typer.echo(x)

        toml_helper.set_dict(pages_dict, toml_helper.pages_file)

    
    def all(database):
        x = PrettyTable()
        x.field_names = ["Index", "Title"]
        x.align["Index"] = "r"
        x.align["Title"] = "l"
        index, x, pages_dict = page.query(database, x = x)
        typer.echo(x)

        toml_helper.set_dict(pages_dict, toml_helper.pages_file)


    def query(database, index = 0, x = PrettyTable, pages_dict = {}):
        r = api_helper.get_pages(api_helper, database)

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
                

        return index, x, pages_dict


    def remove(list_of_indexes):
        pages_dict = toml_helper.get_dict(toml_helper.pages_file)
        for index in list_of_indexes:
            p = pages_dict.get(str(index))
            if type(p) == dict:
                api_helper.remove_page(api_helper, p.get("id"))

    def set_token(token):
        dict = toml_helper.get_dict(toml_helper.config_file)
        dict["token"] = token
        toml_helper.set_dict(dict, toml_helper.config_file)

    def set_database(key, id):
        db_dict = toml_helper.get_dict(toml_helper.config_file)
        
        if "databases" not in db_dict.keys():
            db_dict["databases"] = {}
        
        db_dict.get("databases")[key] = {"id": id} 
        
        toml_helper.set_dict(db_dict, toml_helper.config_file)

    def show_databases():
        list = toml_helper.get_db_keys()
        x = PrettyTable()
        x.field_names = ["Label"]
        for label in list:
            x.add_row([label])
        typer.echo(x)

    def rm_database(label):
        dict = toml_helper.get_dict(toml_helper.config_file)
        r = dict.get("databases").pop(label)
        toml_helper.set_dict(dict, toml_helper.config_file)

    
