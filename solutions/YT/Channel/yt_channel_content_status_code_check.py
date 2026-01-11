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
    raise EnvironmentError("Missing API KEY or base_url in env")

CHANNEL_ID = "UCPvWHbIwTHbXX9Jo_Vephdg"
TYPE = "videos"

URL = f"{base_url}/youtube/v1/channel/{CHANNEL_ID}/content?type={TYPE}"
HEADERS = {"x-api-key": API_KEY}

TOTAL_RUNS = 100
SLEEP = 0.4  # avoid rate limit crying

# =====================
# MAIN
# =====================

def main():
    print("\n🔍 Stress-testing Youtube channel content")
    print(f"➡️ Channel: {CHANNEL_ID}")
    print(f"➡️ Endpoint: {URL}")
    print(f"➡️ Total runs: {TOTAL_RUNS}\n")

    count_200 = 0
    count_errors = 0

    for i in range(1, TOTAL_RUNS + 1):
        try:
            resp = requests.get(
                URL,
                headers=HEADERS,
                timeout=20
            )

            code = resp.status_code

            if code == 200:
                count_200 += 1
                try:
                    body = resp.text
                    snippet = body[:100].replace("\n", " ")
                except Exception:
                    snippet = "<unable to read body>"
                print(f"#{i:03d} ✅ 200 — Body snippet: {snippet}")
            else:
                count_errors += 1
                print(f"#{i:03d} ❌ {code}")

        except requests.RequestException as e:
            count_errors += 1
            print(f"#{i:03d} ⚠️ Request failed: {e}")

        time.sleep(SLEEP)

    # Summary
    print("\n🏁 Test complete.")
    print(f"✔️ 200 responses: {count_200}")
    print(f"❌ Error responses: {count_errors}")
    print("\n")


if __name__ == "__main__":
    main()