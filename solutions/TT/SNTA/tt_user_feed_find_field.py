import requests
from dotenv import load_dotenv
import os
import time
import json

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

SEC_ID = "MS4wLjABAAAAxFxdfI_2kcjbIyupxUL8uD1B5zlYdQbDDx4vyfMk1Dbu0CrkLQZQ4AWn8Uv6Bd7r"
URL = f"{base_url}/tiktok/v1/user/{SEC_ID}/feed"

HEADERS = {"x-api-key": API_KEY}

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
    params = {}  # first call: no cursor
    page = 1

    print("\n🔍 Searching TikTok user feed for image_post_info\n")

    while True:
        data = make_request(params)

        posts = data.get("posts", []) or []
        pagination = data.get("pagination", {}) or {}
        cursor = pagination.get("cursor")

        print(f"\n📄 Page {page} — Posts found: {len(posts)}")

        # Process posts
        for idx, post in enumerate(posts, start=1):

            desc = post.get("desc")
            image_post_info = post.get("image_post_info")

            desc = post.get("desc", "")[:25]  # trim to 25 chars if you want
            print(f"   🔸 Post {idx} → image_post_info: desc: {desc} — {'HAS VALUE' if image_post_info else 'None'}")


            if image_post_info:
                print(json.dumps(image_post_info, indent=2))

        # Stop pagination
        if not cursor:
            print("\n⛔ Pagination ended — no cursor returned.")
            break

        params = {"cursor": cursor}

        print(f"➡️ Next cursor: {cursor}")

        page += 1
        time.sleep(SLEEP)

    print("\n🏁 Finished scanning user feed.\n")


if __name__ == "__main__":
    main()
