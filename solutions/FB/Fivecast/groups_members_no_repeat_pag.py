# =====================
# SCRIPT TASK
# Check if new pages are different than previous ones.
# Includes new header x-version: update
# =====================

import requests
import os
import time
import json
from dotenv import load_dotenv

# =====================
# CONFIG
# =====================
load_dotenv("/Users/davidrajchenberg/Desktop/Vetric/Scripts/dev.env")

IS_DEV = True
MAX_RETRIES = 5
SLEEP_BETWEEN_RETRIES = 2
GROUP_ID = "1101220155491678"

if IS_DEV:
    print("Using DEV environment")
    API_KEY = os.getenv("API_KEY_S")
    BASE_URL = os.getenv("URL_S")
else:
    print("Using PROD environment")
    API_KEY = os.getenv("API_KEY")
    BASE_URL = os.getenv("URL")

HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "x-api-key": API_KEY,
    "x-version": "update"
}

# =====================
# FUNCTIONS
# =====================

def get_members_page(cursor=None):
    url = f"{BASE_URL}/facebook/v1/groups/{GROUP_ID}/members"
    payload = {}
    if cursor:
        payload["group_member_profiles_connection_after_cursor"] = cursor

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
            print(f"[DEBUG] Attempt {attempt+1} | Status: {response.status_code}")
            if response.status_code == 200:
                print(f"[DEBUG] Response Text: {response.text}")
                return response.json()
            else:
                print(f"[DEBUG] Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[DEBUG] Exception: {e}")
        time.sleep(SLEEP_BETWEEN_RETRIES)
    return None

def compare_pages(page1, page2):
    members_page1 = [m["user_id"] for m in page1.get("members", [])]
    members_page2 = [m["user_id"] for m in page2.get("members", [])]

    if members_page1 == members_page2:
        print("Pagination returned the same page. Cursor is a liar.")
    else:
        print("Pagination worked. Cursor moved forward.")
        print(f"Page 1 member IDs ({len(members_page1)}): {members_page1}")
        print(f"Page 2 member IDs ({len(members_page2)}): {members_page2}")

    has_next_page = page2.get("pagination", {}).get("has_next_page")
    print(f"Has next page? {has_next_page}")

# =====================
# MAIN
# =====================

def main():
    print("Fetching first page...")
    page1 = get_members_page()

    if not page1:
        print("No response from API. It died on us.")
        return

    members_page1 = [m["user_id"] for m in page1.get("members", [])]
    pagination1 = page1.get("pagination")

    if not pagination1 or not pagination1.get("cursor"):
        print("No pagination returned. Nothing to paginate.")
        print(f"First page member count: {len(members_page1)}")
        return

    next_cursor = pagination1.get("cursor")
    print(f"Cursor received: {next_cursor}")

    print("Fetching second page...")
    page2 = get_members_page(cursor=next_cursor)

    if not page2:
        print("Failed to fetch second page. API refused to cooperate.")
        return

    compare_pages(page1, page2)

if __name__ == "__main__":
    main()





