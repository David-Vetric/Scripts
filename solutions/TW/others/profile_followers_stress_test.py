# =====================
# SCRIPT TASK
# Are there known limitations for X followers collection. Today, we limit our customers by up to several Ks, usually ~5K.
#  What if we would like to increase it? is there a maximum number from Vetric's end that we can't pass? 10k? 20k? 100k?
# I'm not saying we will reach to 100k but I'd like to know the boundries more or less.
# TW - 
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

MAX_RETRIES = 5
SLEEP_BETWEEN_RETRIES = 2
IDENTIFIER = "44196397"  # Jordan Peterson (6.1M followers)

# =====================
# HELPERS
# =====================
def make_request(url, headers, retries=MAX_RETRIES):
    """Perform GET request with retries."""
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(SLEEP_BETWEEN_RETRIES)
            else:
                raise

def get_cursor_bottom(data):
    """Extract and safely encode cursor_bottom from response."""
    cursor = None

    # Some APIs return it at root, others under 'data'
    if "cursor_bottom" in data:
        cursor = data["cursor_bottom"]
    elif "data" in data and "cursor_bottom" in data["data"]:
        cursor = data["data"]["cursor_bottom"]

    # Encode only the pipe character (|) if it exists
    if cursor and "|" in cursor:
        cursor = cursor.replace("|", "%7C")

    print(f"→ Encoded cursor: {cursor}")
    return cursor

def get_followers_in_page(data):
    """Return list of followers for current page."""
    return data.get("users", [])

# =====================
# MAIN
# =====================
def main():
    headers = {'x-api-key': API_KEY}
    cursor = None
    page = 1
    total_followers = 0

    print("\n🚀 Starting follower collection test...\n")

    try:
        while True:
            # Construct URL (first call without cursor)
            if cursor:
                url = f"{base_url}/twitter/v1/profile/{IDENTIFIER}/followers?cursor={cursor}"
            else:
                url = f"{base_url}/twitter/v1/profile/{IDENTIFIER}/followers"

            print(f"\nFetching page {page} → {url}")
            data = make_request(url, headers)

            # 👇 Print raw JSON early, before checking follower count
            # if page == 1:
            #     print("\n--- RAW RESPONSE (page 1) ---")
            #     print(json.dumps(data, indent=2)[:3000])
            #     print("-----------------------------\n")

            # Extract followers
            followers = get_followers_in_page(data)
            count = len(followers)
            total_followers += count

            print(f"→ Page {page}: {count} followers (Total so far: {total_followers})")

            # Stop conditions
            if count == 0:
                print("\n❌ No more followers returned — likely reached API limit or end of list.")
                break

            cursor = get_cursor_bottom(data)
            if not cursor:
                print(f"\n✅ No cursor_bottom found — reached the natural end of pagination.")
                break

            print(f"→ Next cursor: {cursor[:40]}...")
            print(f"📄 Pages processed so far: {page}")

            page += 1
            time.sleep(1)  # avoid hitting rate limits

    except KeyboardInterrupt:
        print(f"\n🛑 Script manually stopped at page {page}. Total followers collected: {total_followers}")

    except Exception as e:
        print(f"\n⚠️ Script stopped due to error after {total_followers} followers (page {page}): {e}")

    finally:
        print("\n📊 Summary:")
        print(f"   • Total pages fetched: {page}")
        print(f"   • Total followers collected: {total_followers}")
        print("\n✅ Test completed.")


if __name__ == '__main__':
    main()


