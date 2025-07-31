import os
import json
import pandas as pd
import csv
from typing import Any, Dict, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EN_INPUT_FILE = os.path.join(SCRIPT_DIR, '../src/assets/i18n/en.json')
NO_INPUT_FILE = os.path.join(SCRIPT_DIR, '../src/assets/i18n/no.json')
OUTPUT_FILE = os.path.join(SCRIPT_DIR, '../tmp/system-notifications.csv')
PARAMS_OUTPUT_FILE = os.path.join(SCRIPT_DIR, '../tmp/system-notifications-parameters.csv')

os.makedirs(os.path.join(SCRIPT_DIR, '../tmp'), exist_ok=True)

class SystemNotification:
    def __init__(self, summary: str = '', detail: str = ''):
        self.summary = summary
        self.detail = detail

    @classmethod
    def from_dict(cls, data: Any) -> Optional['SystemNotification']:
        if isinstance(data, dict):
            summary = data.get('Summary', '')
            detail = data.get('Detail', '')
            return cls(summary, detail)
        return None

class NotificationParameter:
    def __init__(self, value: str = ''):
        self.value = value

    @classmethod
    def from_any(cls, data: Any) -> 'NotificationParameter':
        if isinstance(data, dict):
            value = data.get('')
            return cls(str(value))
        return cls(str(data))

def load_json(filepath: str) -> Dict[str, Any]:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_notifications(data: Dict[str, Any]) -> Dict[tuple, SystemNotification]:
    notifications = data.get('SystemNotifications', {})
    result = {}
    for notif_type, notif_dict in notifications.items():
        if isinstance(notif_dict, dict):
            for code, value in notif_dict.items():
                if code == 'Parameters':
                    continue
                notif = SystemNotification.from_dict(value)
                if notif:
                    result[(notif_type, code)] = notif
    return result

def extract_parameters(data: Dict[str, Any]) -> Dict[str, NotificationParameter]:
    params = data.get('SystemNotifications', {}).get('Parameters', {})
    result = {}
    for param_key, param_value in params.items():
        param = NotificationParameter.from_any(param_value)
        result[param_key] = param
    return result

def write_notifications_csv(en_notifications, no_notifications, output_file):
    all_keys = set(en_notifications.keys()) | set(no_notifications.keys())
    rows = []
    for notif_type, code in sorted(all_keys):
        en_notif = en_notifications.get((notif_type, code), SystemNotification())
        no_notif = no_notifications.get((notif_type, code), SystemNotification())
        rows.append({
            'Type': notif_type,
            'Code': code,
            'SummaryNO': no_notif.summary,
            'SummaryEN': en_notif.summary,
            'DetailNO': no_notif.detail,
            'DetailEN': en_notif.detail
        })
    df = pd.DataFrame(rows, columns=['Type', 'Code', 'SummaryNO', 'SummaryEN', 'DetailNO', 'DetailEN'])
    df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL)
    print(f"SystemNotifications extracted to '{output_file}'")

def write_parameters_csv(en_params, no_params, output_file):
    all_param_keys = set(en_params.keys()) | set(no_params.keys())
    param_rows = []
    for param_key in sorted(all_param_keys):
        value_no = no_params.get(param_key, NotificationParameter()).value
        value_en = en_params.get(param_key, NotificationParameter()).value
        param_rows.append({
            'Key': param_key,
            'Norwegian': value_no,
            'English': value_en
        })
    param_df = pd.DataFrame(param_rows, columns=['Key', 'Norwegian', 'English'])
    param_df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL)
    print(f"SystemNotifications.Parameters extracted to '{output_file}'")

def main():
    print("Loading English and Norwegian files...")
    en_data = load_json(EN_INPUT_FILE)
    no_data = load_json(NO_INPUT_FILE)

    en_notifications = extract_notifications(en_data)
    no_notifications = extract_notifications(no_data)
    write_notifications_csv(en_notifications, no_notifications, OUTPUT_FILE)

    en_params = extract_parameters(en_data)
    no_params = extract_parameters(no_data)
    write_parameters_csv(en_params, no_params, PARAMS_OUTPUT_FILE)

    print("Processing complete.")

if __name__ == "__main__":
    main()
