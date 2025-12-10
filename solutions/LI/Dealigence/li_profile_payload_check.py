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

IDENTIFIER = "georgy-zerkalov"

URL = f"{base_url}/linkedin/v1/profile/{IDENTIFIER}"
HEADERS = {"x-api-key": API_KEY}

TOTAL_RUNS = 1000
SLEEP = 0.5


# =====================
# MAIN
# =====================
def main():
    print("\n🔍 Stress-testing LinkedIn Profile endpoint")
    print(f"➡️ Endpoint: {URL}")
    print(f"➡️ Total runs: {TOTAL_RUNS}\n")

    total200 = 0
    totalErrors = 0
    emptyBodies = 0

    for i in range(1, TOTAL_RUNS + 1):
        try:
            resp = requests.get(URL, headers=HEADERS, timeout=15)
            status = resp.status_code

            if status == 200:
                total200 += 1

                # parse json safely
                try:
                    data = resp.json()
                except ValueError:
                    data = None

                if isinstance(data, dict) and len(data.keys()) > 0:
                    print(f"#{i:03d} ✅ 200 OK — Body has data")
                else:
                    print(f"#{i:03d} ⚠️ 200 OK — Body EMPTY")
                    emptyBodies += 1

            else:
                print(f"#{i:03d} ❌ {status} ERROR")
                totalErrors += 1

        except requests.RequestException as e:
            print(f"#{i:03d} ⚠️ FAILED → {e}")

        time.sleep(SLEEP)

    print("\n🏁 Test complete.\n")
    print(f"200 responses: {total200}")
    print(f"Error responses: {totalErrors}")
    print(f"Empty bodies: {emptyBodies}")


if __name__ == "__main__":
    main()

