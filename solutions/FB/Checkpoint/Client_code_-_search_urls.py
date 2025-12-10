import requests
from collections import Counter
from dotenv import load_dotenv
import os

# ======== ENV SETUP ======== #
load_dotenv("/Users/davidrajchenberg/Desktop/Vetric/Scripts/dev.env")

is_dev = True  # toggle to False for production

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

# ======== TARGETS ======== #
TARGETS = {
    "https://www.facebook.com/profile.php?id=100056201291051",
    "https://www.facebook.com/HKTDC.MOBILE",
    "https://www.facebook.com/hktdc.courier",
    "https://www.facebook.com/profile.php?id=100008415902335",
    "https://www.facebook.com/profile.php?id=100091846726232",
    "https://www.facebook.com/profile.php?id=61567567797567",
    "100056201291051",
    "HKTDC.MOBILE",
    "hktdc.courier",
    "100008415902335",
    "100091846726232",
    "61567567797567",
}

# ======== API REQUEST ======== #
def make_request(cursor=None):
    url = f"{base_url}/facebook/v1/search/users"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "x-api-key": API_KEY,
    }
    data = {"typed_query": "HKTDC", "transform": "true"}
    if cursor:
        data["end_cursor"] = cursor

    last_status = None
    for attempt in range(4):
        try:
            resp = requests.post(url, headers=headers, data=data, timeout=30)
            last_status = resp.status_code
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 403:
                print("🚫 403 Forbidden – check your API key permissions.")
                break
        except requests.RequestException as e:
            print(f"⚠️ Request error: {e}")
    raise Exception(f"Failed after 4 attempts. Last status code: {last_status}")

# ======== MAIN LOOP ======== #
def main():
    has_more = True
    cursor = None
    page_number = 1
    request_count = 0
    results_count = 0

    seen_ids = set()
    id_counter = Counter()
    duplicate_count = 0
    found_targets = []

    while has_more:
        result = make_request(cursor)
        request_count += 1

        results = result.get("results", []) or []
        results_count += len(results)

        # Find any matches in this page
        matches = []
        for user in results:
            uid = str(user.get("id", ""))
            url = user.get("url", "")
            name = user.get("name", "")

            id_counter[uid] += 1
            if uid in seen_ids:
                duplicate_count += 1
            else:
                seen_ids.add(uid)

            if uid in TARGETS or url in TARGETS:
                matches.append((uid, url, name))
                found_targets.append((uid, url, name))

        # Print results for this page
        if matches:
            print(f"\n📄 Page {page_number}: 🎯 Found target(s)!")
            for uid, url, name in matches:
                print(f"   ✅ {name} → {url} (id: {uid})")
        else:
            print(f"📄 Page {page_number}: target URLs/IDs not found in this page ❌")

        # Pagination control
        if result.get("page_info", {}).get("has_next_page", False):
            cursor = result["page_info"]["end_cursor"]
            page_number += 1
        else:
            has_more = False

    # ======== SUMMARY ======== #
    print("\n📊 === SUMMARY ===")
    print(f"Total pages fetched: {page_number}")
    print(f"Total requests: {request_count}")
    print(f"Total results processed: {results_count}")
    print(f"Unique IDs: {len(seen_ids)}")
    print(f"Duplicate occurrences: {duplicate_count}")

    if found_targets:
        print("\n🏁 Matched targets overall:")
        for uid, url, name in found_targets:
            print(f"   ⭐ {name} ({uid}) -> {url}")
    else:
        print("\n🚫 No target URLs or IDs were found across all pages.")


if __name__ == "__main__":
    main()


