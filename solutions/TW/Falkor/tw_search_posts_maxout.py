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

KEYWORD = "trump"
URL = f"{base_url}/twitter/v1/search/top"
HEADERS = {"x-api-key": API_KEY}

SLEEP = 1
MAX_RETRIES = 4


# =====================
# HELPERS
# =====================
def make_request(cursor=None):
    """GET request with retry logic."""
    params = {"query": KEYWORD}

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
            print(f"⚠️ Error: {e}")
            time.sleep(SLEEP)

    raise Exception(f"❌ Failed after {MAX_RETRIES} attempts. Last status: {last_status}")


# =====================
# MAIN
# =====================
def main():
    cursor = None
    page = 1
    total_tweets = 0
    all_tweets = []

    print(f"\n🔍 Collecting Twitter TOP tweets for keyword '{KEYWORD}'\n")

    while True:
        data = make_request(cursor)

        tweets = data.get("tweets", []) or []
        count = len(tweets)

        total_tweets += count
        all_tweets.extend(tweets)

        print(f"📄 Page {page}: Retrieved {count} tweets (Total so far: {total_tweets})")

        # Pagination
        cursor = data.get("cursor_bottom")
        if not cursor:
            print("\n⛔ Pagination ended — no cursor_bottom found.")
            break

        page += 1
        time.sleep(SLEEP)

    # =====================
    # SUMMARY
    # =====================
    print("\n📊 === SUMMARY ===")
    print(f"Total pages fetched: {page}")
    print(f"Total tweets collected: {total_tweets}")

    if total_tweets > 0:
        print("✨ Example tweet rest_id values:")
        for tweet in all_tweets[:5]:
            tweet_obj = tweet.get("tweet", {})
            print(f"   🔸 {tweet_obj.get('rest_id')}")

    print("\n🏁 Finished.\n")


if __name__ == "__main__":
    main()
