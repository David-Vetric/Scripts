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

PROFILE_ID = "100028659395603"
URL = f"{base_url}/facebook/v1/profiles/{PROFILE_ID}/uploaded-media"

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
    total_uploaded = 0
    end_cursor = None

    print(f"\n🔍 Collecting Facebook uploaded media for profileId={PROFILE_ID}\n")

    while True:
        data = make_request(end_cursor)

        uploaded_media = data.get("uploaded_media", []) or []
        count = len(uploaded_media)
        total_uploaded += count

        print(f"\n📄 Page {page} — {count} uploaded photos")

        for idx, media in enumerate(uploaded_media, start=1):
            photo_id = media.get("photo_id")
            print(f"   🔹 Uploaded Photo {idx}: photo_id={photo_id}")

        pagination = data.get("pagination", {}) or {}
        has_next_page = pagination.get("has_next_page")
        new_cursor = pagination.get("end_cursor")

        if not has_next_page or not new_cursor:
            print("\n⛔ Pagination ended — has_next_page is false or end_cursor is null.")
            break

        end_cursor = new_cursor
        print(f"➡️ Next end_cursor: {str(end_cursor)[:50]}...")
        page += 1
        time.sleep(SLEEP)

    # SUMMARY
    print("\n📊 === SUMMARY ===")
    print(f"Total pages fetched: {page}")
    print(f"Total uploaded photos collected: {total_uploaded}")
    print("\n🏁 Finished.\n")


if __name__ == "__main__":
    main()
