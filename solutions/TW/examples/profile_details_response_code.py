# =====================
# SCRIPT TASK
# TW - /profile/:screenName/replies stability test WITH transform toggle
# =====================

import requests
from dotenv import load_dotenv
import os
import time

# =====================
# CONFIG
# =====================
load_dotenv("/Users/davidrajchenberg/Desktop/Vetric/Scripts/dev.env")

is_dev = True          # toggle environment
TRANSFORM = False      # toggle transform=true/false
TOTAL_RUNS = 100       # number of test requests
DELAY = 0.5            # small delay to avoid rate limiting

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

# PLACE TWITTER HANDLE HERE
SCREEN_NAME = "KhalilErai39020"
TRANSFORM = "false"

URL = f"{base_url}/twitter/v1/profile/{SCREEN_NAME}/details?transform={TRANSFORM}"
HEADERS = {"x-api-key": API_KEY}

# =====================
# MAIN
# =====================
def main():

    count200 = 0
    countError = 0

    print("\n🔍 Testing Twitter Replies Endpoint Stability")
    print(f"➡️ Endpoint: {URL}")
    print(f"➡️ Total runs: {TOTAL_RUNS}\n")

    for i in range(1, TOTAL_RUNS + 1):
        try:
            resp = requests.get(URL, headers=HEADERS, timeout=20)
            status = resp.status_code

            if status == 200:
                print(f"#{i:03d} ✅ 200 OK")
                count200 += 1
            else:
                print(f"#{i:03d} ❌ {status} ERROR")
                countError += 1

        except requests.RequestException as e:
            print(f"#{i:03d} ⚠️ REQUEST FAILED: {e}")

        time.sleep(DELAY)

    print("\n🏁 Test completed.\n")
    print(f"200 reponses: {count200}")
    print(f"Error responses: {countError}")


if __name__ == "__main__":
    main()
