import requests
import csv
import time
from datetime import datetime

def get_account_info(base_url, username, password):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Ensure URL doesn't have trailing slashes and points to the API
    base_url = base_url.strip().rstrip('/')
    api_url = f"{base_url}/player_api.php?username={username.strip()}&password={password.strip()}"
    
    try:
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
        return {
            "URL": base_url, 
            "Username": username, 
            "Password": password, 
            "Expiry": "N/A", 
            "Active": "N/A", 
            "Max": "N/A", 
            "Status": "Failed", 
            "Error": str(e)
        }

def main():
    input_file = "accounts_input.csv"
    output_file = "accounts_output.csv"
    results = []

    try:
        with open(input_file, mode='r', encoding='utf-8') as infile:
            # DictReader automatically uses the first row as keys
            reader = csv.DictReader(infile)
            
            # Convert to list to get total count
            rows = list(reader)
            total = len(rows)
            
            print(f"Starting check for {total} accounts...")

            for i, row in enumerate(rows, 1):
                # Using .get() to avoid errors if columns are missing
                u = row.get('url')
                un = row.get('username')
                pw = row.get('password')

                if not all([u, un, pw]):
                    print(f"[{i}/{total}] Skipping: Missing data in row.")
                    continue

                print(f"[{i}/{total}] Checking: {un} @ {u[:30]}...")
                
                info = get_account_info(u, un, pw)
                results.append(info)
                
                # Politeness delay
                time.sleep(1)

        # Write results to output CSV
        fieldnames = ["URL", "Username", "Password", "Expiry", "Active", "Max", "Status", "Error"]
        with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"\nDone! Results saved to: {output_file}")

    except FileNotFoundError:
        print(f"Error: {input_file} not found. Please create it with url,username,password columns.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()