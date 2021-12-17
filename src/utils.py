import requests
import toml
import json



class api_helper():
    api_url_pre = "https://api.notion.com/v1/"
    
    with open ("src/token.json", "r") as token_file:
        NOTION_API_KEY = json.load(token_file).get("token")

    with open ("src/config.toml", "r") as config_file:
        DATABASE_ID = toml.load(config_file).get("databases").get("id")

    payload = {
        "Authorization": NOTION_API_KEY,
        "Notion-Version": "2021-08-16",
        "Content-Type": "application/json"
    }

    def __init__(self) -> None:
        pass
    
    def new_page(self, title):

        data = '{"parent":{"database_id":"'+self.DATABASE_ID + \
        '"},"properties":{"Name":{"title":[{"text":{"content":"'+title+'"}}]}}}'
        r = self.api_post(self, "pages", data)


    def get_pages(self):
       
        r = self.api_post(self, "databases/" + self.DATABASE_ID + "/query", "")
        i = 0
        for page in r["results"]:
            path = page.get("properties").get("Name").get("title")
            if len(path) > 0:
                print(str(i) + "\t" + path[0].get("text").get("content"))
                i+=1

    def api_post(self, api_url_post, data):
        return requests.post(self.api_url_pre + api_url_post, headers=self.payload, data=data).json() 


