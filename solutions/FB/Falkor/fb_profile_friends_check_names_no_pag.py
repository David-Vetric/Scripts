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

PROFILE_ID = "100001750658349"
URL = f"{base_url}/facebook/v1/profiles/{PROFILE_ID}/friends"

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/x-www-form-urlencoded"
}

TOTAL_RUNS = 20
SLEEP = 1
MAX_RETRIES = 4


# =====================
# HELPERS
# =====================
def fetch_first_page():
    """POST request for the first page only."""
    last_status = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(URL, headers=HEADERS, timeout=20)
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
    print(f"\n🔍 Running FIRST PAGE of Facebook friends {TOTAL_RUNS} times")
    print(f"➡️ Profile ID: {PROFILE_ID}\n")

    success = 0
    failures = 0

    for i in range(1, TOTAL_RUNS + 1):
        print(f"\n===== Run {i}/{TOTAL_RUNS} =====")

        try:
            data = fetch_first_page()
            results = data.get("results", []) or []
            success += 1

            print(f"🟩 200 OK — Found {len(results)} friends")

            # Print names
            for idx, friend in enumerate(results, start=1):
                name = friend.get("name") or "<no-name>"
                print(f"   🔹 Friend {idx}: {name}")

        except Exception as e:
            failures += 1
            print(f"🟥 ERROR → {e}")

        time.sleep(SLEEP)

    print("\n🏁 Test complete.")
    print(f"✔️ Successful runs: {success}")
    print(f"❌ Failed runs: {failures}\n")


if __name__ == "__main__":
    main()
