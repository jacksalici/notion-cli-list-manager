import requests
import json
import typer
import toml
from pathlib import Path


class toml_helper():
    script_location = Path(__file__).absolute().parent
    config_file = script_location / "config.toml"

    def get_dict():
        try:
            with open(toml_helper.config_file, "r+") as file_text:
                r = toml.load(file_text)
                return r
        except FileNotFoundError:
            typer.echo("Config file not found.")
        except toml.TomlDecodeError:
            typer.echo("Config file encoding error.")
        
        return {}
    
    def set_dict(dict):
        with open(toml_helper.config_file, "w") as file_text:
            return file_text.write(toml.dumps(dict))
    
    
    def get_db_id (database):
        try:
            dict = toml_helper.get_dict().get("databases")
            return str(dict.get(database).get("id"))
        except:
            return ""

   
    def get_db_keys():
        try:
            r = toml_helper.get_dict().get("databases")
            return r.keys()
        except:
            return []



class file_helper():
    script_location = Path(__file__).absolute().parent


    #token_file = script_location / "token.json" #[obsolete]
    #config_file = script_location / "config.json" #[obsolete]
    pages_file = script_location / "pages.json"

    
    def get_dict(file):
        try:
            with open(file, "r+") as file_text:
                r = json.load(file_text, object_hook=dict)
                return r
        except:
            return {}

    
    def set(file, text):
        with open(file, "w") as file_text:
            return file_text.write(text)
    

class api_helper():
    api_url_pre = "https://api.notion.com/v1/"
    NOTION_API_KEY = str(toml_helper.get_dict().get("token"))
    payload = {
        "Authorization": NOTION_API_KEY,
        "Notion-Version": "2021-08-16",
        "Content-Type": "application/json"
    }


   

    
    def new_page(self, title, database):
        data = '{"parent":{"database_id":"'+ toml_helper.get_db_id(database) + \
        '"},"properties":{"Name":{"title":[{"text":{"content":"'+title+'"}}]}}}'
        return self.api_post(self, "pages", data)


    def get_pages(self, database):
        return self.api_post(self, "databases/" + toml_helper.get_db_id(database) + "/query", "")
        
    

    def remove_page(self, page_id):
        return self.api_delete(self, "blocks/" + page_id, "")

        

    def api_post(self, api_url_post, data):
        return self.api(self, requests.post, api_url_post, data)


    def api_delete(self, api_url_post, data):
        return self.api(self, requests.delete, api_url_post, data)

    def api(self, function, api_url_post, data):
        try:
            r = function(self.api_url_pre + api_url_post, headers=self.payload, data=data)
            if (r.status_code == 200):
                return r.json()
            else:
                typer.echo("Request post error")
                return ""
        except:
            typer.echo("Request post error")
            return ""
