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
    raise EnvironmentError("Missing API key or base URL")

SCREEN_NAME = "iamsrk"
URL = f"{base_url}/twitter/v1/profile/{SCREEN_NAME}/feed"

HEADERS = {"x-api-key": API_KEY}

PARAMS = {
    "include_replies": "true",
    "include_retweets": "true"
}

RUNS = 100
SLEEP = 1
TIMEOUT = 25

# =====================
# MAIN
# =====================
def main():
    count_200 = 0
    count_404 = 0
    other_statuses = {}

    print(f"\n🔁 Running first-page request {RUNS} times for @{SCREEN_NAME}\n")

    for i in range(1, RUNS + 1):
        try:
            resp = requests.get(URL, headers=HEADERS, params=PARAMS, timeout=TIMEOUT)
            status = resp.status_code

            print(f"▶️ Run {i}/{RUNS} → HTTP {status}")

            if status == 200:
                count_200 += 1
            elif status == 404:
                count_404 += 1
            else:
                other_statuses[status] = other_statuses.get(status, 0) + 1

        except requests.RequestException as e:
            print(f"⚠️ Run {i}/{RUNS} → Request error: {e}")
            other_statuses["exception"] = other_statuses.get("exception", 0) + 1

        time.sleep(SLEEP)

    # =====================
    # SUMMARY
    # =====================
    print("\n📊 === SUMMARY ===")
    print(f"Total runs: {RUNS}")
    print(f"HTTP 200 responses: {count_200}")
    print(f"HTTP 404 responses: {count_404}")

    if other_statuses:
        print("\n⚠️ Other responses:")
        for k, v in other_statuses.items():
            print(f"  {k}: {v}")

    print("\n🏁 Finished.\n")


if __name__ == "__main__":
    main()
