import requests
import json
import time
from dotenv import load_dotenv
import os

# ======== ENV SETUP ======== #
load_dotenv("/Users/davidrajchenberg/Desktop/Vetric/Scripts/dev.env")

is_dev = True  # toggle for prod if needed

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

# ======== CONFIG ======== #
PROFILE_ID = "paulius-taraskevicius"
URL = f"{base_url}/linkedin/v1/profile/{PROFILE_ID}"
HEADERS = {"x-api-key": API_KEY}
NUM_CALLS = 50
DELAY_SECONDS = 1  # optional delay between calls

# ======== MAIN LOOP ======== #
def main():
    print(f"\n🔍 Testing {NUM_CALLS} calls to {URL}\n")

    for i in range(1, NUM_CALLS + 1):
        try:
            resp = requests.get(URL, headers=HEADERS, timeout=30)
            status = resp.status_code

            try:
                body = resp.json()
            except ValueError:
                body = resp.text or ""

            print(f"\n📦 Request #{i}: Result {status}")

            # Empty-body detection
            if not body or (isinstance(body, dict) and not body):
                print("❌ Body is empty:")
                print(body)
            else:
                if isinstance(body, dict) and "first_name" in body:
                    print("✅ Body has data:")
                    print(
                        json.dumps(
                            {
                                "first_name": body.get("first_name"),
                                "middle_name": body.get("middle_name"),
                                "last_name": body.get("last_name"),
                                "public_identifier": body.get("public_identifier"),
                            },
                            ensure_ascii=False,
                            indent=4,
                        )
                    )
                    print("...and so on...")
                else:
                    print("✅ Body has data (non-empty structure):")
                    print(json.dumps(body, ensure_ascii=False, indent=4))

        except requests.RequestException as e:
            print(f"⚠️ Request #{i} failed: {e}")

        time.sleep(DELAY_SECONDS)

    print("\n🏁 Test completed.")


if __name__ == "__main__":
    main()