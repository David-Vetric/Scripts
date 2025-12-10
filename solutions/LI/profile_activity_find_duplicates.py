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

IDENTIFIER = "rubendominguezibar"
URL = f"{base_url}/linkedin/v1/profile/{IDENTIFIER}/activity"
HEADERS = {"x-api-key": API_KEY}
TYPE = "posts"
SLEEP = 1


# =====================
# HELPERS
# =====================
def extract_text(post):
    """Return post.text or shared_post.text (fallback)."""
    main = (post.get("text") or "").strip()

    shared_post = post.get("shared_post") or {}
    shared = (shared_post.get("text") or "").strip()

    return main if main else shared


def make_request(cursor=None):
    params = {"type": TYPE}
    if cursor:
        params["cursor"] = cursor

    resp = requests.get(URL, headers=HEADERS, params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


# =====================
# MAIN
# =====================
def main():
    cursor = None
    page = 1

    seen_posts = {}  # text → {id, text}
    duplicates = []

    print(f"\n🔍 Checking LinkedIn posts for duplicates (user: {IDENTIFIER})\n")

    while True:
        data = make_request(cursor)

        posts = data.get("activity", []) or []
        print(f"\n📄 Page {page} — {len(posts)} posts")

        for post in posts:
            txt = extract_text(post)
            if not txt:
                continue  # ignore empty text

            post_id = post.get("urn") or post.get("id") or "<no-id>"

            if txt in seen_posts:
                # Duplicate found — print both clearly
                orig = seen_posts[txt]

                print("-----------------------------------")
                print("\n⚠️ DUPLICATE FOUND")
                print("Original:")
                print(f"   id:   {orig['id']}")
                print(f"   text: {orig['text'][:200]}")

                print("Duplicate:")
                print(f"   id:   {post_id}")
                print(f"   text: {txt[:200]}")
                print("-----------------------------------")

                duplicates.append((orig, {"id": post_id, "text": txt}))
            else:
                seen_posts[txt] = {
                    "id": post_id,
                    "text": txt
                }

        # Pagination
        cursor = data.get("cursor")
        if not cursor:
            print("\n⛔ No more pages.")
            break

        print(f"➡️ Next cursor: {cursor[:6]}...")
        page += 1
        time.sleep(SLEEP)

    # SUMMARY
    print("\n📊 === SUMMARY ===")
    print(f"Total unique posts: {len(seen_posts)}")
    print(f"Total duplicate pairs: {len(duplicates)}")

    print("\n🏁 Finished.\n")


if __name__ == "__main__":
    main()


