import requests
import toml
import json

class file_helper():
    token_file = "src/token.json"
    config_file = "src/token.json"
    pages_file = "src/pages.json"

    def get(file):
        with open(file, "r") as file_text:
            return file_text
    
    def set(file, text):
        with open(file, "a") as file_text:
            file_text.write(text)

class api_helper():
    api_url_pre = "https://api.notion.com/v1/"
    
 
    NOTION_API_KEY = json.load(file_helper.get(file_helper.stoken_file)).get("token")

    with open ("src/config.toml", "r") as config_file:
        DATABASE_ID = toml.load(config_file).get("databases").get("id")

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
        

    def api_post(self, api_url_post, data):
        return requests.post(self.api_url_pre + api_url_post, headers=self.payload, data=data).json() 


