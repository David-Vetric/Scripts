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

URL = f"{base_url}/linkedin/v1/search/posts"
HEADERS = {"x-api-key": API_KEY}

KEYWORD = "trump"
SLEEP = 1
MAX_RETRIES = 4


# =====================
# HELPERS
# =====================
def make_request(params):
    """GET request with retry logic."""
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
    params = {"keywords": KEYWORD}

    page = 1
    total_posts = 0
    all_posts = []

    print(f"\n🔍 Collecting LinkedIn posts for keyword '{KEYWORD}'\n")

    while True:
        data = make_request(params)

        posts = data.get("posts", []) or []
        count = len(posts)
        total_posts += count
        all_posts.extend(posts)

        print(f"📄 Page {page}: Retrieved {count} posts (Total so far: {total_posts})")

        cursor = data.get("cursor")

        if not cursor:
            print("\n⛔ Pagination ended — 'cursor' missing or empty.")
            break

        params = {
            "keywords": KEYWORD,
            "cursor": cursor
        }

        # print(f"➡️ Next cursor: {cursor}")

        page += 1
        time.sleep(SLEEP)

    # =====================
    # SUMMARY
    # =====================
    print("\n📊 === SUMMARY ===")
    print(f"Total pages fetched: {page}")
    print(f"Total posts collected: {total_posts}")

    if total_posts > 0:
        print("✨ First few post IDs (if they exist):")
        for p in all_posts[:5]:
            print(f"   🔸 {p.get('id')}")

    print("\n🏁 Finished.\n")


if __name__ == "__main__":
    main()
