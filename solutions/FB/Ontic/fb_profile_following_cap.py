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

PROFILE_ID = "100014807225880"
URL = f"{base_url}/facebook/v1/profiles/{PROFILE_ID}/following"

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/x-www-form-urlencoded"
}

SLEEP = 1
MAX_RETRIES = 4


# =====================
# HELPERS
# =====================
def make_request(end_cursor=None):
    data = {}
    if end_cursor:
        data["end_cursor"] = end_cursor

    last_status = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(URL, headers=HEADERS, data=data, timeout=25)
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
    page = 1
    total_following = 0
    end_cursor = None

    print(f"\n🔍 Collecting Facebook following for profileId={PROFILE_ID}\n")

    while True:
        data = make_request(end_cursor)

        results = data.get("results", []) or []
        count = len(results)
        total_following += count

        print(f"\n📄 Page {page} — {count} following")

        for idx, item in enumerate(results, start=1):
            name = item.get("name")
            print(f"   🔹 Following {idx}: {name}")

        page_info = data.get("page_info", {}) or {}
        new_cursor = page_info.get("end_cursor")

        if not new_cursor:
            print("\n⛔ Pagination ended — end_cursor is null.")
            break

        end_cursor = new_cursor
        print(f"➡️ Next end_cursor: {str(end_cursor)[:50]}...")
        page += 1
        time.sleep(SLEEP)

    # SUMMARY
    print("\n📊 === SUMMARY ===")
    print(f"Total pages fetched: {page}")
    print(f"Total following collected: {total_following}")
    print("\n🏁 Finished.\n")


if __name__ == "__main__":
    main()
