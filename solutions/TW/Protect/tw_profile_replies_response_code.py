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

HANDLE = "SimAIGeen"

URL = f"{base_url}/twitter/v1/profile/{HANDLE}/replies"
HEADERS = {"x-api-key": API_KEY}

TOTAL_RUNS = 50
SLEEP = 0.5  # tiny delay to keep the API from crying


# =====================
# MAIN
# =====================
def main():
    print("\n🔍 Stress-testing Twitter Replies endpoint")
    print(f"➡️ Endpoint: {URL}")
    print(f"➡️ Total runs: {TOTAL_RUNS}\n")

    total200 = 0
    totalErrors = 0

    for i in range(1, TOTAL_RUNS + 1):
        try:
            resp = requests.get(URL, headers=HEADERS, timeout=15)
            status = resp.status_code

            if status == 200:
                print(f"#{i:03d} ✅ 200 OK")
                total200 += 1
            else:
                print(f"#{i:03d} ❌ {status} ERROR")
                totalErrors += 1

        except requests.RequestException as e:
            print(f"#{i:03d} ⚠️ FAILED → {e}")

        time.sleep(SLEEP)

    print("\n🏁 Test complete.\n")
    print(f"200 responses: {total200}")
    print(f"Error responses: {totalErrors}")


if __name__ == "__main__":
    main()
