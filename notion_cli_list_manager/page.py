import typer
import json
from .utils import api_helper, file_helper

class page():


    def add(title, database):
        api_helper.new_page(api_helper, title, database)

    def all_by_all():
        index = 0
        for key in api_helper.get_dbs_keys():
            index = page.all(key, index)

    def all(database, index = 0):
        r = api_helper.get_pages(api_helper, database)
        pages_dict = {}

        if type(r) is dict:
            if r["object"] == "list":
                for page in r["results"]:
                        path = page.get("properties").get("Name").get("title")
                            
                        if len(path) > 0:
                            typer.echo("\t" + str(index) + "\t" + path[0].get("text").get("content"))
                            pages_dict[str(index)] = page
                            index+=1

            elif r["object"] == "error":
                typer.echo("Error:\t" + str(r["message"]))
                

        file_helper.set(file_helper.pages_file, pages_dict)

        return index


    def remove(list_of_indexes):
        
        pages_dict = {"dict" : file_helper.get_dict(file_helper.pages_file)}
        for index in list_of_indexes:
            p = pages_dict.get("dict").get(str(index))
            if type(p) == dict:
                api_helper.remove_page(api_helper, p.get("id"))

    def set_token(token):
        file_helper.set(file_helper.token_file, {"token": token})
    
    def set_database(key, id):
        db_dict = file_helper.get_dict(file_helper.config_file)
        db_dict.get("database_ids")[key] = id

        print(file_helper.set(file_helper.config_file, db_dict))

    def show_databases():
        list = api_helper.get_dbs_keys()
        for db in list:
            typer.echo("\t" + str(db))

    def rm_database(db):
        dict = file_helper.get_dict(file_helper.config_file)
        r = dict.get("database_ids").pop(db)
        file_helper.set(file_helper.config_file, dict)

    def add_database(label, id):
        dict = file_helper.get_dict(file_helper.config_file)
        dict.get("database_ids")[label] = id
        file_helper.set(file_helper.config_file, dict)
