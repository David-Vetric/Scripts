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
    raise EnvironmentError("Missing API key or base URL in env")

# Insert username here
USERNAME = "mangogirl2K"

URL = f"{base_url}/reddit/v1/user/{USERNAME}/comments"

HEADERS = {
    "x-api-key": API_KEY
}

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

    raise Exception(f"❌ Failed after {MAX_RETRIES} attempts. Last status = {last_status}")


# =====================
# MAIN
# =====================
def main():
    cursor = None
    page = 1
    total_comments = 0

    print(f"\n🔍 Collecting Reddit comments for user: {USERNAME}\n")

    while True:
        data = make_request(cursor)

        comments = data.get("comments", []) or []
        count = len(comments)
        total_comments += count

        print(f"\n📄 Page {page} — {count} comments")

        for idx, c in enumerate(comments, start=1):
            comment_text = (c.get("contentPreview") or "").strip()
            post_info = c.get("postInfo") or {}
            post_title = post_info.get("title") or ""
            subreddit = post_info.get("prefixedName") or ""

            print(f"\n   🔹 Comment {idx}")
            print(f"      💬 Comment: {comment_text[:200]}")
            print(f"      🧵 Post: {post_title}")
            print(f"      🏷 Subreddit: {subreddit}")

        page_info = data.get("pageInfo") or {}
        cursor = page_info.get("cursor")

        if not cursor:
            print("\n⛔ Pagination ended — cursor is null or empty.")
            break

        print(f"\n➡️ Next cursor: {str(cursor)[:50]}...")
        page += 1
        time.sleep(SLEEP)

    # SUMMARY
    print("\n📊 === SUMMARY ===")
    print(f"Total pages fetched: {page}")
    print(f"Total comments collected: {total_comments}")
    print("\n🏁 Finished.\n")


if __name__ == "__main__":
    main()
