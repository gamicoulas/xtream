import requests
import urllib.parse
import csv
import time
from datetime import datetime

def get_account_info(m3u_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        parsed_url = urllib.parse.urlparse(m3u_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        params = urllib.parse.parse_qs(parsed_url.query)
        username = params.get('username', [None])[0]
        password = params.get('password', [None])[0]

        if not username or not password:
            return {"error": "Missing credentials"}

        api_url = f"{base_url}/player_api.php?username={username}&password={password}"
        
        response = requests.get(api_url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        user_info = data.get('user_info', {})
        
        exp_timestamp = user_info.get('exp_date')
        if exp_timestamp and str(exp_timestamp).isdigit():
            readable_date = datetime.fromtimestamp(int(exp_timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            readable_date = "Unlimited/Expired/Null"

        return {
            "URL": base_url,
            "Username": username,
            "Password": password,
            "Expiry": readable_date,
            "Active": user_info.get('active_cons', '0'),
            "Max": user_info.get('max_connections', '0'),
            "Status": user_info.get('status', 'Active'),
            "Error": ""
        }

    except Exception as e:
        return {"Error": str(e), "URL": m3u_url}

def main():
    input_file = "accounts_input.txt"
    output_file = "accounts_output.csv"
    
    results = []
    
    print(f"Reading {input_file}...")

    try:
        with open(input_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]

        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] Checking: {url[:40]}...")
            info = get_account_info(url)
            results.append(info)
            # Short pause to prevent IP blocking
            time.sleep(1)

        # Define the columns for the CSV
        fieldnames = ["URL", "Username", "Password", "Expiry", "Active", "Max", "Status", "Error"]

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"\nSuccess! Results saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: {input_file} not found.")

if __name__ == "__main__":
    main()