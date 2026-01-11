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
    raise EnvironmentError("Missing API key or base URL")

SCREEN_NAME = "wawog_now"
URL = f"{base_url}/twitter/v1/profile/{SCREEN_NAME}/feed"
HEADERS = {"x-api-key": API_KEY}

BASE_PARAMS = {
    "include_replies": "true",
    "include_retweets": "true"
}

SLEEP = 1
MAX_RETRIES = 4


# =====================
# HELPERS
# =====================
def make_request(cursor=None):
    params = BASE_PARAMS.copy()
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

    raise Exception(f"❌ Failed after {MAX_RETRIES} attempts. Last status={last_status}")


# =====================
# MAIN
# =====================
def main():
    cursor = None
    page = 1
    total_tweets = 0

    seen_rest_ids = set()
    duplicate_rest_ids = set()

    print(f"\n🔍 Exhaustive feed fetch for @{SCREEN_NAME}\n")

    while True:
        data = make_request(cursor)

        tweets = data.get("tweets", []) or []
        page_count = len(tweets)
        total_tweets += page_count

        print(f"\n📄 Page {page}")
        print(f"   Tweets in this page: {page_count}")
        print(f"   Tweets collected so far: {total_tweets}")

        # Stop condition: empty page
        if page_count == 0:
            print("⛔ Empty page returned. Reached last page.")
            break

        for idx, t in enumerate(tweets, start=1):
            tweet_obj = t.get("tweet") or {}
            rest_id = tweet_obj.get("rest_id")

            print(f"   🔹 Tweet {idx} → rest_id: {rest_id}")

            if not rest_id:
                continue

            if rest_id in seen_rest_ids:
                duplicate_rest_ids.add(rest_id)
                print("      🔁 DUPLICATE DETECTED")
            else:
                seen_rest_ids.add(rest_id)

        cursor = data.get("cursor_bottom")

        if not cursor:
            print("\n⛔ cursor_bottom missing or empty. Reached last page.")
            break

        print(f"➡️ Next cursor: {str(cursor)[:60]}...")
        page += 1
        time.sleep(SLEEP)

    # =====================
    # SUMMARY
    # =====================
    print("\n📊 === SUMMARY ===")
    print(f"Total pages fetched: {page}")
    print(f"Total tweets fetched: {total_tweets}")
    print(f"Unique tweets (rest_id): {len(seen_rest_ids)}")
    print(f"Duplicate tweets detected: {len(duplicate_rest_ids)}")

    if duplicate_rest_ids:
        print("\n🔁 Duplicate rest_id values:")
        for rid in duplicate_rest_ids:
            print(f"- {rid}")

    print("\n🏁 Finished.\n")


if __name__ == "__main__":
    main()
