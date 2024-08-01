import requests
import time
import json
from datetime import datetime, timedelta
import sys
import urllib.parse
import re  # Import module re for regex operations

def load_account_data(filename):
    accounts = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 2):
            authorization = lines[i].strip()
            x_app_init_data = lines[i + 1].strip()
            accounts.append((authorization, x_app_init_data))
    return accounts

def extract_telegram_info(x_app_init_data):
    # Mendecode URL-encoded string
    decoded_data = urllib.parse.unquote(x_app_init_data)
    # Menemukan bagian JSON dari data yang sudah didecode
    json_data = re.search(r'user=({.*?})', decoded_data)
    if json_data:
        user_info = json.loads(json_data.group(1))
        telegram_user_id = str(user_info.get('id', ''))
        telegram_username = user_info.get('username', '')
        return telegram_user_id, telegram_username
    else:
        raise ValueError("Data tidak sesuai format yang diharapkan")

def login(account):
    authorization, x_app_init_data = account
    url = 'https://cms-tg.nomis.cc/api/ton-twa-users/auth/'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': authorization,
        'Content-Type': 'application/json',
        'X-App-Init-Data': x_app_init_data,
    }
    
    # Mengextract informasi dari x_app_init_data
    try:
        telegram_user_id, telegram_username = extract_telegram_info(x_app_init_data)
    except ValueError as e:
        print(f"Error extracting data for account with Authorization: {authorization}. {e}")
        return None
    
    payload = {
        "telegram_user_id": telegram_user_id,
        "telegram_username": telegram_username,
        "referrer": ""
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        user_id = data.get('id')
        return user_id
    else:
        print(f"Login failed for account with Authorization: {authorization}")
        return None

def claim(user_id):
    url = 'https://cms-tg.nomis.cc/api/ton-twa-users/claim/'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json'
    }
    payload = {
        "user_id": user_id
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Claim successful for user_id: {user_id}")
    else:
        print(f"Claim failed for user_id: {user_id}")

def countdown_timer(duration):
    end_time = datetime.now() + timedelta(seconds=duration)
    while datetime.now() < end_time:
        remaining = end_time - datetime.now()
        sys.stdout.write(f"\rTime remaining: {str(remaining).split('.')[0]}")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\n")

def main():
    accounts = load_account_data('data.txt')
    num_accounts = len(accounts)
    print(f"Number of accounts: {num_accounts}")

    for index, account in enumerate(accounts):
        print(f"Processing account {index + 1}/{num_accounts}")
        user_id = login(account)
        if user_id:
            claim(user_id)
        time.sleep(5)  # wait for 5 seconds before processing the next account

    print("All accounts processed. Starting 8-hour countdown...")
    countdown_timer(8 * 60 * 60)  # 8 hours in seconds

    print("Restarting process...")
    main()  # Restart the process after the countdown

if __name__ == '__main__':
    main()
