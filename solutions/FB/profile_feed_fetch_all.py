# =====================
# SCRIPT TASK
# Fetch profile feed for specific profile
# Profile: 1013461997
# =====================

import requests
from dotenv import load_dotenv
import os
import time
import json

# =====================
# CONFIG
# =====================
load_dotenv("/Users/davidrajchenberg/Desktop/Vetric/Scripts/dev.env")

is_dev = True

if is_dev:
    print("Using DEV environment")
    API_KEY = os.getenv("API_KEY_S")
    base_url = os.getenv("URL_S")
else:
    print("Using PROD environment")
    API_KEY = os.getenv("API_KEY")
    base_url = os.getenv("URL")

PROFILE_ID = "1013461997"

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}
MAX_RETRIES = 5
SLEEP_BETWEEN_RETRIES = 2

# =====================
# FETCH PAGINATED FEED
# =====================

def fetch_feed(profile_id):
    url = f"{base_url}/facebook/v1/profiles/{profile_id}/feed"
    cursor = None
    total_requests = 0
    error_500_count = 0

    while True:
        total_requests += 1
        body = {} if cursor is None else {"cursor": cursor}

        print(f"[{total_requests}] Request body: {body}")

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(url, headers=HEADERS, json=body, timeout=20)
                status = response.status_code

                # Server side tantrum
                if status >= 500:
                    error_500_count += 1
                    print(f"[{total_requests}] 50X error (status {status}) on attempt {attempt}")
                    try:
                        err_msg = response.json()
                    except Exception:
                        err_msg = response.text
                    print(f"Error message: {err_msg}")
                    time.sleep(SLEEP_BETWEEN_RETRIES)
                    continue

                # Any other unhappy outcome
                if status != 200:
                    print(f"[{total_requests}] Non-200 response: {status}")
                    try:
                        err_msg = response.json()
                    except Exception:
                        err_msg = response.text
                    print(f"Error message: {err_msg}")
                    return

                # Parse response properly
                full_json = response.json()
                timeline = (
                    full_json
                    .get("data", {})
                    .get("node", {})
                    .get("timeline_feed_units", {})
                )
                page_info = timeline.get("page_info", {})

                cursor = page_info.get("end_cursor")
                has_next_page = page_info.get("has_next_page")

                print(f"[{total_requests}] Cursor: {cursor}")
                print(f"[{total_requests}] Has next page: {has_next_page}")

                break  # escape retry loop

            except requests.exceptions.RequestException as e:
                print(f"[{total_requests}] Request failed on attempt {attempt}: {e}")
                time.sleep(SLEEP_BETWEEN_RETRIES)
        else:
            print(f"[{total_requests}] Max retries reached. Moving on.")
            break

        # No next page? We're done here.
        if not cursor or not has_next_page:
            print("No more pages.")
            break

    print(f"\nCompleted. Total requests: {total_requests}, 50X errors: {error_500_count}")

# =====================
# RUN SCRIPT
# =====================

if __name__ == "__main__":
    fetch_feed(PROFILE_ID)
