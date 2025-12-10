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

URL = f"{base_url}/facebook/v1/search/posts"
HEADERS = {
    "x-api-key": API_KEY,
    "x-version": "update",
    "Content-Type": "application/x-www-form-urlencoded"
}

KEYWORD = "real estate"
START_DATE = "2025-01-01"
END_DATE = "2025-06-01"
MAX_RETRIES = 4
SLEEP = 1


# =====================
# HELPERS
# =====================
def make_request(cursor=None):
    """POST request with retry logic."""
    data = {
        "typed_query": KEYWORD,
        "start_date": START_DATE,
        "end_date": END_DATE
    }

    # data = {
    #     "typed_query": KEYWORD,
    # }

    if cursor:
        data["end_cursor"] = cursor

    last_status = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(URL, headers=HEADERS, data=data, timeout=30)
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
    total_posts = 0
    all_posts = []

    print(f"\n🔍 Collecting Facebook posts for keyword '{KEYWORD}'\n")

    while True:
        data = make_request(cursor)

        results = data.get("results", []) or []
        page_info = data.get("page_info", {}) or {}

        count = len(results)
        total_posts += count
        all_posts.extend(results)

        print(f"📄 Page {page}: Retrieved {count} posts  (Total so far: {total_posts})")

        # Pagination
        cursor = page_info.get("end_cursor")
        has_more = page_info.get("has_next_page", False)

        if not cursor or not has_more:
            print("\n⛔ Pagination ended")
            break

        page += 1
        time.sleep(SLEEP)

    # ======== SUMMARY ======== #
    print("\n📊 === SUMMARY ===")
    print(f"Total pages fetched: {page}")
    print(f"Total posts collected: {total_posts}")

    if total_posts > 0:
        print("✨ Example post IDs:")
        for post in all_posts[:5]:
            print(f"   🔸 {post.get('id')}")

    print("\n🏁 Finished.\n")


if __name__ == "__main__":
    main()
