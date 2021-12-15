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

    for page in r["results"]:
        print("- " + page["properties"]["Name"]["title"][0]["text"]["content"])
        # print(page)


#new_page("Hello World")
get_list()
