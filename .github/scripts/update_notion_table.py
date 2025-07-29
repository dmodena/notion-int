import os
import pandas as pd
import requests

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
CSV_PATH = "tmp/en-system-notifications.csv"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def clear_database():
    query_url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    pages = []

    while True:
        res = requests.post(query_url, headers=headers, json={})
        if not res.ok:
            print("❌ Failed to query Notion database:")
            print("Status:", res.status_code)
            print("Response:", res.text)
            res.raise_for_status()

        data = res.json()
        pages.extend(data.get("results", []))

        if not data.get("has_more"):
            break

    for page in pages:
        del_url = f"https://api.notion.com/v1/pages/{page['id']}"
        requests.patch(del_url, headers=headers, json={"archived": True})

def add_row(row):
    create_url = "https://api.notion.com/v1/pages"
    new_page = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Type": {"title": [{"text": {"content": str(row["Type"])}}]},
            "Code": {"text": [{"text": {"content": str(row["Code"])}}]},
            "Summary": {"text": [{"text": {"content": str(row["Summary"])}}]},
            "Detail": {"text": [{"text": {"content": str(row["Detail"])}}]}
        }
    }
    res = requests.post(create_url, headers=headers, json=new_page)
    return res.ok

def main():
    df = pd.read_csv(CSV_PATH)
    clear_database()
    for _, row in df.iterrows():
        add_row(row)

if __name__ == "__main__":
    main()
