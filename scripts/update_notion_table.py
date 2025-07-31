import os
import pandas as pd
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_NOTIF_DB_ID = os.environ["NOTION_NOTIF_DB_ID"]
NOTION_PARAMS_DB_ID = os.environ["NOTION_PARAMS_DB_ID"]
NOTIF_CSV_PATH = os.path.join(SCRIPT_DIR, "../tmp/system-notifications.csv")
PARAMS_CSV_PATH = os.path.join(SCRIPT_DIR, "../tmp/system-notifications-parameters.csv")

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
            print(f"Failed to query Notion database {db_id}: {res.status_code} {res.text}")
            res.raise_for_status()
        data = res.json()
        pages.extend(data.get("results", []))
        if not data.get("has_more"):
            break
    # Cleaning up db
    for page in pages:
        del_url = f"https://api.notion.com/v1/pages/{page['id']}"
        resp = requests.patch(del_url, headers=headers, json={"archived": True})
        if not resp.ok:
            print(f"Failed to archive page {page['id']}: {resp.status_code} {resp.text}")

def add_row(row, db_id, columns):
    create_url = "https://api.notion.com/v1/pages"
    properties = {}
    # First column is always title
    first_col = columns[0]
    properties[first_col] = {"title": [{"text": {"content": str(row[first_col])}}]}
    # Remaining columns are rich_text
    for col in columns[1:]:
        properties[col] = {"rich_text": [{"text": {"content": str(row[col])}}]}
    new_page = {
        "parent": {"database_id": db_id},
        "properties": properties
    }
    res = requests.post(create_url, headers=headers, json=new_page)
    if not res.ok:
        print(f"Failed to add row to database {db_id}: {res.status_code} {res.text}")
    return res.ok

def process_file(file_path, db_id):
    print(f"Processing file '{file_path}'...")
    df = pd.read_csv(file_path)
    columns = df.columns.tolist()
    clear_database(db_id)
    for _, row in df.iterrows():
        add_row(row, db_id, columns)
    print(f"File '{file_path}' processing complete.")

def main():
    print("Uploading notifications to Notion...")
    process_file(NOTIF_CSV_PATH, NOTION_NOTIF_DB_ID)
    process_file(PARAMS_CSV_PATH, NOTION_PARAMS_DB_ID)
    print("All uploads complete.")

if __name__ == "__main__":
    main()
