import requests
import time
import json
from datetime import datetime, timedelta
import sys
import re
from urllib.parse import unquote

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
    decoded_data = unquote(x_app_init_data)
    match = re.search(r'user=({.*?})', decoded_data)
    if match:
        user_data = json.loads(match.group(1))
        telegram_user_id = user_data.get('id')
        telegram_username = user_data.get('username')
        return telegram_user_id, telegram_username
    return None, None

def login(account):
    authorization, x_app_init_data = account
    url = 'https://cms-tg.nomis.cc/api/ton-twa-users/auth/'
    headers = {
        ':authority': 'cms-tg.nomis.cc',
        ':method': 'POST',
        ':path': '/api/ton-twa-users/auth/',
        ':scheme': 'https',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8',
        'Authorization': authorization,
        'Cache-Control': 'no-cache',
        'Content-Length': '82',
        'Content-Type': 'application/json',
        'Origin': 'https://telegram.nomis.cc',
        'Pragma': 'no-cache',
        'Priority': 'u=1, i',
        'Referer': 'https://telegram.nomis.cc/',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126", "Microsoft Edge WebView2";v="126"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        'X-App-Init-Data': x_app_init_data
    }
    telegram_user_id, telegram_username = extract_telegram_info(x_app_init_data)
    payload = {
        "telegram_user_id": telegram_user_id,
        "telegram_username": telegram_username,
        "referrer": ""
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        user_id = data.get('id')
        print(f"Login successful for {telegram_username}.")
        print(f"Response details:")
        print(f"Telegram Username: {data.get('telegramUsername')}")
        print(f"Next Farm Claim At: {data.get('nextFarmClaimAt')}")
        print(f"Day Streak: {data.get('dayStreak')}")
        print(f"Wallet: {data.get('wallet')}")
        print(f"Points: {data.get('points')}")
        return user_id
    else:
        print(f"Login failed for account with Authorization: {authorization}")
        print(f"Response: {response.text}")
        return None

def claim(user_id, authorization, x_app_init_data):
    url = 'https://cms-tg.nomis.cc/api/ton-twa-users/start-farm'
    headers = {
        ':authority': 'cms-tg.nomis.cc',
        ':method': 'POST',
        ':path': '/api/ton-twa-users/start-farm',
        ':scheme': 'https',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8',
        'Authorization': authorization,
        'Cache-Control': 'no-cache',
        'Content-Length': '19',
        'Content-Type': 'application/json',
        'Origin': 'https://telegram.nomis.cc',
        'Pragma': 'no-cache',
        'Priority': 'u=1, i',
        'Referer': 'https://telegram.nomis.cc/',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126", "Microsoft Edge WebView2";v="126"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        'X-App-Init-Data': x_app_init_data
    }
    payload = {
        "user_id": user_id
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Claim successful for user_id: {user_id}")
    else:
        print(f"Claim failed for user_id: {user_id}")
        print(f"Response: {response.text}")

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
            claim(user_id, account[0], account[1])
        time.sleep(5)  # wait for 5 seconds before processing the next account

    print("All accounts processed. Starting 8-hour countdown...")
    countdown_timer(8 * 60 * 60)  # 8 hours in seconds

    print("Restarting process...")
    main()  # Restart the process after the countdown

if __name__ == '__main__':
    main()
