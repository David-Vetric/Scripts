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

IDENTIFIER = "abbey-hurley-5b6a74135"
EXPECTED_PUBLIC_ID = IDENTIFIER

URL = f"{base_url}/linkedin/v1/profile/{IDENTIFIER}"
HEADERS = {"x-api-key": API_KEY}

TOTAL_RUNS = 1000
SLEEP = 0.5


# =====================
# MAIN
# =====================
def main():
    print("\n🔍 Stress-testing LinkedIn Profile public_identifier field")
    print(f"➡️ Endpoint: {URL}")
    print(f"➡️ Total runs: {TOTAL_RUNS}\n")

    total200 = 0
    totalErrors = 0
    missingPublicID = 0
    correctPublicID = 0

    for i in range(1, TOTAL_RUNS + 1):
        try:
            resp = requests.get(URL, headers=HEADERS, timeout=15)
            status = resp.status_code

            if status == 200:
                total200 += 1

                # parse JSON safely
                try:
                    data = resp.json()
                except ValueError:
                    data = None

                public_id = None
                if isinstance(data, dict):
                    public_id = data.get("public_identifier")

                # CASE 1: Correct public_identifier
                if public_id == EXPECTED_PUBLIC_ID:
                    print(f"#{i:04d} ✅ 200 OK — public_identifier correct: {public_id}")
                    correctPublicID += 1

                # CASE 2: Missing / null / undefined / incorrect
                else:
                    print(f"#{i:04d} ⚠️ 200 OK — public_identifier MISSING or WRONG → {public_id}")
                    missingPublicID += 1

            else:
                print(f"#{i:04d} ❌ {status} ERROR")
                totalErrors += 1

        except requests.RequestException as e:
            print(f"#{i:04d} ⚠️ FAILED → {e}")

        time.sleep(SLEEP)

    # SUMMARY
    print("\n🏁 Test complete.\n")
    print(f"Total 200 responses:        {total200}")
    print(f"Total error responses:      {totalErrors}")
    print(f"Correct public_identifier:  {correctPublicID}")
    print(f"Missing/invalid public_id:  {missingPublicID}")


if __name__ == "__main__":
    main()

