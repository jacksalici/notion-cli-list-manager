import requests
import json
import typer
from pathlib import Path

class file_helper():
    script_location = Path(__file__).absolute().parent


    token_file = script_location / "token.json"
    config_file = script_location / "config.json"
    pages_file = script_location / "pages.json"

    def get_dict(file):
        try:
            with open(file, "r") as file_text:
                return json.loads(file_text.read())
        except OSError:
            if file == file_helper.pages_file:
                typer.echo("Config file not found. Be sure to call the to-do with 'all'.")
            else:
                typer.echo("File not found. Be sure to set the token and the db id with 'set'.")
            
            return json.loads("{}")

    
    def set(file, text):
        with open(file, "w") as file_text:
            return file_text.write(json.dumps(text))

class api_helper():
    api_url_pre = "https://api.notion.com/v1/"
    
 
    NOTION_API_KEY = str(file_helper.get_dict(file_helper.token_file).get("token"))

    DATABASE_ID = str(file_helper.get_dict(file_helper.config_file).get("database_id"))

    payload = {
        "Authorization": NOTION_API_KEY,
        "Notion-Version": "2021-08-16",
        "Content-Type": "application/json"

    }
    
    def new_page(self, title):

        data = '{"parent":{"database_id":"'+self.DATABASE_ID + \
        '"},"properties":{"Name":{"title":[{"text":{"content":"'+title+'"}}]}}}'
        return self.api_post(self, "pages", data)


    def get_pages(self):
        return self.api_post(self, "databases/" + self.DATABASE_ID + "/query", "")
    

    def remove_page(self, page_id):
        return self.api_delete(self, "blocks/" + page_id, "")

        

    def api_post(self, api_url_post, data):
        return requests.post(self.api_url_pre + api_url_post, headers=self.payload, data=data).json() 

    def api_delete(self, api_url_post, data):
        return requests.delete(self.api_url_pre + api_url_post, headers=self.payload, data=data).json() 


