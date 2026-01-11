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

PROFILE_ID = "1541311211547000832"

TARGET_TWEET_IDS = {
    "1990076227084804323",
    "1990053625436033268",
    "1989822064983781703",
}

URL = f"{base_url}/twitter/v1/profile/{PROFILE_ID}/tweets"
HEADERS = {"x-api-key": API_KEY}

SLEEP = 1
MAX_RETRIES = 4


# =====================
# HELPERS
# =====================
def make_request(cursor=None):
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

    raise Exception(f"❌ Failed after retries. Last status: {last_status}")


# =====================
# MAIN
# =====================
def main():
    cursor = None
    page = 1

    found = {}  # tweet_id -> page number

    print(f"\n🔍 Searching tweets for profileId={PROFILE_ID}\n")

    while True:
        data = make_request(cursor)

        tweets = data.get("tweets", []) or []
        print(f"📄 Page {page} — {len(tweets)} tweets")

        for t in tweets:
            tweet_obj = t.get("tweet") or {}
            rest_id = tweet_obj.get("rest_id")

            if rest_id in TARGET_TWEET_IDS and rest_id not in found:
                found[rest_id] = page
                print(f"   ✅ Found tweet {rest_id} on page {page}")

        # Stop early if all targets found
        if len(found) == len(TARGET_TWEET_IDS):
            print("\n🎯 All target tweets found.")
            break

        cursor = data.get("cursor_bottom")
        if not cursor:
            print("\n⛔ Pagination ended — no cursor_bottom.")
            break

        print(f"➡️ Next cursor: {str(cursor)[:50]}...")
        page += 1
        time.sleep(SLEEP)

    # =====================
    # SUMMARY
    # =====================
    print("\n📊 === SUMMARY ===")

    for tid in TARGET_TWEET_IDS:
        if tid in found:
            print(f"✅ Tweet {tid} found on page {found[tid]}")
        else:
            print(f"❌ Tweet {tid} NOT found")

    print("\n🏁 Finished.\n")


if __name__ == "__main__":
    main()
