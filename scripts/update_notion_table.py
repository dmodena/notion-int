import os
import pandas as pd
import requests

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
EN_NOTION_DATABASE_ID = os.environ["EN_NOTION_DATABASE_ID"]
NO_NOTION_DATABASE_ID = os.environ["NO_NOTION_DATABASE_ID"]
EN_CSV_PATH = "../tmp/en-system-notifications.csv"
NO_CSV_PATH = "../tmp/no-system-notifications.csv"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def clear_database(db_id):
    query_url = f"https://api.notion.com/v1/databases/{db_id}/query"
    pages = []

    while True:
        res = requests.post(query_url, headers=headers, json={})
        if not res.ok:
            print("Failed to query Notion database:")
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

def add_row(row, db_id):
    create_url = "https://api.notion.com/v1/pages"
    new_page = {
        "parent": {"database_id": db_id},
        "properties": {
            "Type": {"title": [{"text": {"content": str(row["Type"])}}]},
            "Code": {"rich_text": [{"text": {"content": str(row["Code"])}}]},
            "Summary": {"rich_text": [{"text": {"content": str(row["Summary"])}}]},
            "Detail": {"rich_text": [{"text": {"content": str(row["Detail"])}}]}
        }
    }
    res = requests.post(create_url, headers=headers, json=new_page)
    return res.ok

def process_file(file_path, db_id):
    df = pd.read_csv(file_path)
    clear_database(db_id)
    for _, row in df.iterrows():
        add_row(row, db_id)

def main():
    process_file(EN_CSV_PATH, EN_NOTION_DATABASE_ID)
    process_file(NO_CSV_PATH, NO_NOTION_DATABASE_ID)

if __name__ == "__main__":
    main()
