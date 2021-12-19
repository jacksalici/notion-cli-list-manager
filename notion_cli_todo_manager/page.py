import typer
import json
from .utils import api_helper, file_helper

class page():
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
                pages_dict[str(index)] = page
                index+=1
                

        file_helper.set(file_helper.pages_file, pages_dict)

    def remove(list_of_indexes):
        
        pages_dict = {"dict" : file_helper.get_dict(file_helper.pages_file)}
        for index in list_of_indexes:
            p = pages_dict.get("dict").get(str(index))
            if type(p) == dict:
                api_helper.remove_page(api_helper, p.get("id"))

    def set_token(token):
        file_helper.set(file_helper.token_file, {"token": token})
    
    def set_database(db_id):
        file_helper.set(file_helper.config_file, {"database_id": db_id})


