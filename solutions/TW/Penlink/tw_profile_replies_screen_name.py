import requests
from dotenv import load_dotenv
import os
import time

# =====================
# CONFIG
# =====================
load_dotenv("/Users/davidrajchenberg/Desktop/Vetric/Scripts/dev.env")

is_dev = True

if is_dev:
    print("🌱 Using DEV environment")
    API_KEY = os.getenv("API_KEY_S")
    base_url = os.getenv("URL_S")
else:
    print("🚀 Using PROD environment")
    API_KEY = os.getenv("API_KEY")
    base_url = os.getenv("URL")

if not API_KEY or not base_url:
    raise EnvironmentError("Missing API key or base URL in .env file")

SCREEN_NAME = "Wheresalexnyc"

URL = f"{base_url}/twitter/v1/profile/{SCREEN_NAME}/replies"
HEADERS = {"x-api-key": API_KEY}

SLEEP = 1
MAX_RETRIES = 4


# =====================
# HELPERS
# =====================
def make_request(cursor=None):
    """GET request with retry logic."""
    params = {}

    if cursor:
        params["cursor"] = cursor

    last_status = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(URL, headers=HEADERS, params=params, timeout=25)
            last_status = resp.status_code

            if resp.status_code == 200:
                return resp.json()

            print(f"⚠️ Attempt {attempt} returned {resp.status_code}")
            time.sleep(SLEEP)

        except requests.RequestException as e:
            print(f"⚠️ Error on attempt {attempt}: {e}")
            time.sleep(SLEEP)

    raise Exception(f"❌ Failed after {MAX_RETRIES} attempts. Last status = {last_status}")


# =====================
# MAIN
# =====================
def main():
    cursor = None
    page = 1
    total_tweets = 0

    print(f"\n🔍 Collecting ALL replies for @{SCREEN_NAME}\n")

    while True:
        data = make_request(cursor)

        tweets = data.get("tweets", []) or []
        count = len(tweets)
        total_tweets += count

        print(f"\n📄 Page {page} — {count} tweets")

        # Extract created_at
        for idx, t in enumerate(tweets, start=1):
            tweet_obj = t.get("tweet", {}) or {}
            full_text = tweet_obj.get("full_text" or "empty")
            user_details = tweet_obj.get("user_details") or {}
            screen_name = user_details.get("screen_name" or "empty")
            print(f"🔸 Tweet {idx}: screen_name = {screen_name}")
            print(f"🔸 Tweet {idx}: full_text = {full_text[:30]}")

        # Pagination
        cursor = data.get("cursor_bottom")
        if not cursor:
            print("\n⛔ Pagination ended — no cursor_bottom found.")
            break

        print(f"➡️ Next cursor: {cursor[:50]}...")

        page += 1
        time.sleep(SLEEP)

    # SUMMARY
    print("\n📊 === SUMMARY ===")
    print(f"Total pages fetched: {page}")
    print(f"Total tweets collected: {total_tweets}")
    print("\n🏁 Finished.\n")


if __name__ == "__main__":
    main()
