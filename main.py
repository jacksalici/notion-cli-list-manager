import requests
import json
from config import *

def get_list():
    api_url="https://api.notion.com/v1/databases/" + DATABASE_ID + "/query"
    payload = {
        "Authorization":NOTION_API_KEY,
        "Notion-Version":"2021-08-16",
        "Content-Type": "application/json"

        }
    r = requests.post(api_url, headers=payload)
    print(r.json())

    pages=[]
    page=[]
    pages.__add__()



get_list()