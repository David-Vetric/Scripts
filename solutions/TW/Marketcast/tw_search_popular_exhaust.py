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


# *** IMPORTANT FIX ***
# Use UNENCODED query string. Let "requests" encode it correctly.
QUERY = (
    "%28wolfman%20OR%20wolfmanmovie%20OR%20wolfmanfilm%20OR%20wolfmandarkuniverse%20OR%20%22wolf%20man%22%20OR%20%23wolfman%20OR%20%23wolfmanmovie%20OR%20%23wolfmanfilm%20OR%20%23wolfmandarkuniverse%20OR%20thewolfman%20OR%20%23thewolfman%20OR%20thewolfmanmovie%20OR%20%23thewolfmanmovie%20OR%20thewolfmanfilm%20OR%20%23thewolfmanfilm%29%20-furry%20-furries%20-onlyfans%20-onlyfan%20-cock%20-tits%20-ass%20-porn%20-nsfw%20-sex%20-svengoolie%20-cum%20-outcum%20-cumming%20-%22Wolfman%20Matt%22%20since_time%3A1734393600%20until_time%3A1734998400"
)

URL = f"{base_url}/twitter/v1/search/popular"
HEADERS = {"x-api-key": API_KEY}

SLEEP = 1
MAX_RETRIES = 4


# =====================
# HELPERS
# =====================
def make_request(cursor=None):
    """GET request with retry logic."""
    params = {"query": QUERY}
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
            print(f"URL requested: {resp.url}")      # so you see EXACTLY what's sent
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

    print(f"\n🔍 Exhaustive search for query: {QUERY[:60]}\n")

    while True:
        data = make_request(cursor)

        tweets = data.get("tweets", []) or []
        count = len(tweets)
        total_tweets += count

        print(f"\n📄 Page {page} — {count} tweets")

        for idx, t in enumerate(tweets, start=1):
            tweet_obj = t.get("tweet") or {}
            full_text = (tweet_obj.get("full_text") or "").strip()
            print(f"   🔹 Tweet 'full_text' {idx}: {full_text[:80].replace(chr(10), ' / ')}")

        # Pagination
        cursor = data.get("cursor_bottom")
        if not cursor:
            print("\n⛔ Pagination ended — no cursor_bottom found.")
            break

        print(f"➡️ Next cursor: {str(cursor)[:50]}...")
        page += 1
        time.sleep(SLEEP)

    # SUMMARY
    print("\n📊 === SUMMARY ===")
    print(f"Total pages fetched: {page}")
    print(f"Total tweets collected: {total_tweets}")
    print("\n🏁 Finished.\n")


if __name__ == "__main__":
    main()

