# =====================
# SCRIPT TASK
# Find specific users from Facebook's users search.
# Query: ตลาดหลักทรัพย์แห่งประเทศไทย
# =====================

import requests
from dotenv import load_dotenv
import os
import time
import json

# =====================
# CONFIG
# =====================
# Load environment variables
load_dotenv("/Users/davidrajchenberg/Desktop/Vetric/Scripts/dev.env")

# Set environment (dev or prod)
is_dev = True

if is_dev:
    print("Using DEV environment")
    API_KEY = os.getenv("API_KEY_S")
    base_url = os.getenv("URL_S")
else:
    print("Using PROD environment")
    API_KEY = os.getenv("API_KEY")
    base_url = os.getenv("URL")

SEARCH_URL = f"{base_url}/facebook/v1/search/users"
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}
TYPED_QUERY = "ตลาดหลักทรัพย์แห่งประเทศไทย"
MAX_RETRIES = 5
SLEEP_BETWEEN_RETRIES = 2

# =====================
# HELPERS
# =====================

def make_request(cursor=None):
    """Handle API request with retries and optional cursor"""
    for attempt in range(1, MAX_RETRIES + 1):
        payload = {"typed_query": TYPED_QUERY}
        if cursor:
            payload["cursor"] = cursor

        try:
            resp = requests.post(SEARCH_URL, headers=HEADERS, json=payload, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"Request failed with status {resp.status_code}, attempt {attempt}/{MAX_RETRIES}")
        except requests.RequestException as e:
            print(f"Request error on attempt {attempt}/{MAX_RETRIES}: {e}")

        time.sleep(SLEEP_BETWEEN_RETRIES)

    print("Max retries reached. Moving on...")
    return None

# =====================
# MAIN
# =====================

def main():
    all_users = []
    unique_users = {}
    page = 1
    cursor = None
    prev_cursor = None  # Track previous cursor for comparison

    while page < 10:
        print(f"\nFetching page {page}...")
        data = make_request(cursor)

        if not data or "results" not in data:
            print("No data or 'results' missing in response. Exiting.")
            break

        results = data.get("results", [])
        if not results:
            print("No more users found. Exiting.")
            break

        # Collect users
        page_users = []
        page_names = []
        for user in results:
            user_id = user.get("id")
            user_name = user.get("name")
            all_users.append(user)
            page_users.append(user_id)
            page_names.append(user_name)
            if user_id not in unique_users:
                unique_users[user_id] = user

        print(f"Page {page} users ({len(page_users)} found): {page_users}")
        print(f"usernames: {page_names}")

        # Check for next page
        next_cursor = (data.get("page_info", {}).get("end_cursor") or "").strip()

        if not next_cursor:
            print("No more cursor. End of results.")
            break

        # Detect repeated cursor
        if next_cursor == prev_cursor:
            print(f"Cursor hasn't changed ({next_cursor[-30:]}). Pagination might be stuck.")
            break
        else:
            print("Cursors are different")

        print(f"Next cursor (last 30): ...{next_cursor[-30:]}")
        prev_cursor = next_cursor
        cursor = next_cursor
        page += 1

    # =====================
    # SUMMARY
    # =====================
    total_users = len(all_users)
    unique_user_count = len(unique_users)
    repeated = total_users - unique_user_count

    print("\n")
    print("=====================")
    print("SUMMARY")
    print("=====================")
    print(f"Total users (including duplicates): {total_users}")
    print(f"Unique users: {unique_user_count}")
    print(f"Repeated instances: {repeated}")

    print("\nList of ALL user IDs:")
    print([u.get("id") for u in all_users])

    print("\nList of UNIQUE user IDs:")
    print(list(unique_users.keys()))


if __name__ == "__main__":
    main()