import requests
import json
import argparse
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
    # print(p)


def get_pages():
    api_url_db = "https://api.notion.com/v1/databases/" + DATABASE_ID + "/query"
    payload = {
        "Authorization": NOTION_API_KEY,
        "Notion-Version": "2021-08-16",
        "Content-Type": "application/json"

    }

    r = requests.post(api_url_db, headers=payload).json()

    for page in r["results"]:
        path = page.get("properties").get("Name").get("title")
        if len(path) > 0:
            print(path[0].get("text").get("content"))




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "function", help="Insert the fuction of the ToDo.\nUse [get] or [add]")
    args = parser.parse_args()

    if args.function == "add":
        new_page("Hey")
    elif args.function == "get":
        get_pages()
    else:
        pass
