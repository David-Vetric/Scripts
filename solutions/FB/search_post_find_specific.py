# =====================
# SCRIPT TASK
# Find specific posts from Facebook's posts search.
# Find the posts by the ID
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

SEARCH_URL = f"{base_url}/facebook/v1/search/pages"
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}
TYPED_QUERY = "BDO Binary"
TARGET_IDS = {"61578674683929", "61578190053160"}
MAX_RETRIES = 5
SLEEP_BETWEEN_RETRIES = 2

# =====================
# HELPERS
# =====================
def make_post_request(url, headers, body, retries=MAX_RETRIES):
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(url, headers=headers, json=body, timeout=20)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(SLEEP_BETWEEN_RETRIES)
            else:
                raise

def extract_end_cursor(data):
    # end_cursor might be at different nesting levels depending on the API
    page_info = data.get("page_info", {})
    return page_info.get("end_cursor")

def extract_items(data):
    return data.get("results", [])

# =====================
# MAIN
# =====================
def main():
    end_cursor = None
    found_ids = set()
    page = 1

    print("\n🚀 Starting Facebook post search...\n")

    try:
        while True:
            body = {"typed_query": TYPED_QUERY}
            if end_cursor:
                body["end_cursor"] = end_cursor

            print(f"🔎 Fetching page {page}")
            data = make_post_request(SEARCH_URL, HEADERS, body)

            items = extract_items(data)
            if not items:
                print("\n❌ No items returned — probably hit the end.")
                break

            for item in items:
                post_id = item.get("id")
                if post_id in TARGET_IDS and post_id not in found_ids:
                    print(f"✅ Found post ID: {post_id}")
                    found_ids.add(post_id)

            if found_ids == TARGET_IDS:
                print("\n🎯 All target IDs found. Mission accomplished.")
                break

            end_cursor = extract_end_cursor(data)
            if not end_cursor:
                print("\n✅ No more end_cursor — reached natural end of pagination.")
                break

            page += 1
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n🛑 Script manually stopped at page {page}. Found IDs: {found_ids}")

    except Exception as e:
        print(f"\n⚠️ Script crashed after page {page}: {e}")

    finally:
        print("\n📊 Summary:")
        print(f"   • Total pages fetched: {page}")
        print(f"   • IDs found: {found_ids}")
        print("\n✅ Done.")

if __name__ == "__main__":
    main()


