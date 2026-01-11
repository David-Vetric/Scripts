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

HEADERS = {"x-api-key": API_KEY}

VIDEO_IDS = [
    "ZfUk42ym1O8",
    "aJYS7ntR28M",
    "Ix6DbERRXZk",
    "8wL_o5dLQKo",
    "xo8FAwUOJkA",
    "6ubU3cZ0TQs",
    "1rU20-SKc8c"
]

TOTAL_ROUNDS = 10
SLEEP = 0.4


# =====================
# MAIN
# =====================
def main():
    print("\n🔍 Stress-testing YouTube transcript endpoint")
    print(f"➡️ Total rounds: {TOTAL_ROUNDS}")
    print(f"➡️ Videos per round: {len(VIDEO_IDS)}\n")

    for round_num in range(1, TOTAL_ROUNDS + 1):
        print("\n" + "=" * 70)
        print(f"🔁 ROUND {round_num}")
        print("=" * 70)

        for video_id in VIDEO_IDS:
            url = f"{base_url}/youtube/v1/video/{video_id}/transcript"
            params = {"languageCode": "en"}

            try:
                resp = requests.get(url, headers=HEADERS, params=params, timeout=20)
                status = resp.status_code

                print(f"🎬 {video_id} → Status: {status}")

                if status == 200:
                    try:
                        data = resp.json().get("data", [])
                    except ValueError:
                        data = []

                    print("   ✅ Transcript found (first 4 lines):")
                    for i, item in enumerate(data[:4], start=1):
                        text = item.get("text", "")
                        print(f"      🔹 Line {i}: {text}")
                else:
                    print("   ❌ No transcript")

            except requests.RequestException as e:
                print(f"   ⚠️ Request failed: {e}")

            time.sleep(SLEEP)

    print("\n🏁 Stress test completed.\n")


if __name__ == "__main__":
    main()

