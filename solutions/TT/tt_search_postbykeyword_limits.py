import requests
import os
import time
from dotenv import load_dotenv

# ======== ENV SETUP ======== #
load_dotenv("/Users/davidrajchenberg/Desktop/Vetric/Scripts/dev.env")

is_dev = True  # toggle False for prod

if is_dev:
    print("🌱 Environment: DEV")
    API_KEY = os.getenv("API_KEY_S")
    base_url = os.getenv("URL_S")
else:
    print("🚀 Environment: PROD")
    API_KEY = os.getenv("API_KEY")
    base_url = os.getenv("URL")

if not API_KEY or not base_url:
    raise EnvironmentError("Missing API_KEY or base_url in .env file")

# ======== CONFIG ======== #
KEYWORD = "cherry"
SORT_TYPE = "date"
HEADERS = {"x-api-key": API_KEY}
URL = f"{base_url}/tiktok/v1/search/posts-by-keyword"
MAX_PAGES = 50
DELAY = 1


def make_request(cursor=None):
    params = {"keyword": KEYWORD, "sort_type": SORT_TYPE}
    if cursor:
        params["cursor"] = cursor

    for attempt in range(3):
        try:
            resp = requests.get(URL, headers=HEADERS, params=params, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"⚠️ Unexpected status: {resp.status_code}")
        except requests.RequestException as e:
            print(f"⚠️ Request error: {e}")
        time.sleep(2)

    raise Exception(f"❌ Failed after 3 attempts for cursor={cursor}")


def main():
    cursor = None
    page = 1
    total_posts = 0
    all_posts = []

    print(f"\n🔍 Fetching TikTok posts for keyword '{KEYWORD}' sorted by {SORT_TYPE}\n")

    while page <= MAX_PAGES:
        data = make_request(cursor)
        posts = data.get("posts", []) or []
        pagination = data.get("pagination", {}) or {}

        if not posts:
            print(f"📄 Page {page}: ⚠️ No posts returned.")
        else:
            total_posts += len(posts)
            all_posts.extend(posts)

            print(f"📄 Page {page}: ✅ {len(posts)} posts")

            # === NEW: print all URLs per page ===
            for p in posts:
                post_url = p.get("post_url") or "(no url)"
                desc = (p.get("desc", "")[:25])
                author = p.get("author", {}).get("nickname", "")
                print(f"   🔗 {post_url}")
                print(f"Description: {desc}")
                print(f"Author: {author}")
                print("\n")

        cursor = pagination.get("cursor")
        has_more = pagination.get("has_more") or pagination.get("hasMore")

        if not has_more or not cursor:
            print(f"\n⛔ Pagination ended at page {page}. Cursor was {cursor}")
            break

        page += 1
        time.sleep(DELAY)

    # ======== SUMMARY ======== #
    print("\n📊 === SUMMARY ===")
    print(f"Total pages fetched: {page}")
    print(f"Total posts collected: {total_posts}")

    # if total_posts > 0:
    #     print(f"\n✨ Sample posts:")
    #     for post in all_posts[:5]:
    #         desc = post.get("desc", "")
    #         author = post.get("author", {}).get("nickname", "")
    #         post_url = post.get("post_url", "")
    #         print(f"      🔗 {post_url}")
    # else:
    #     print("❌ No posts were retrieved at all.")


if __name__ == "__main__":
    main()
