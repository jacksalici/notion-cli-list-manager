import requests
import json
from config import *


def new_page(title):
    api_url_p = "https://api.notion.com/v1/pages"

    payload = {
        "Authorization": NOTION_API_KEY,
        "Notion-Version": "2021-08-16",
        "Content-Type": "application/json"

    }

    data = '{"parent":{"database_id":"'+DATABASE_ID + \
        '"},"properties":{"Name":{"title":[{"text":{"content":"'+title+'"}}]}}}'
    p = requests.post(api_url_p, headers=payload, data=data).json()
    #print(p)


def get_list():
    api_url_db = "https://api.notion.com/v1/databases/" + DATABASE_ID + "/query"
    payload = {
        "Authorization": NOTION_API_KEY,
        "Notion-Version": "2021-08-16",
        "Content-Type": "application/json"

    }

    

    r = requests.post(api_url_db, headers=payload).json()
    #print(json.dumps(r))#[0]["text"]["content"]
    for page in r["results"]:
        pathA = page.get("properties").get("Name").get("title")
        if len(pathA)>0:
            print(pathA[0].get("text").get("content"))
    
        #print(page)


#new_page("Hello World 2")
#new_page("Hey")
get_list()