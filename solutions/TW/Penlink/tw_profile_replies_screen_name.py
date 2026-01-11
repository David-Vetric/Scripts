import requests
from dotenv import load_dotenv
import os
import time
from collections import defaultdict

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

SCREEN_NAME = "Wheresalexnyc"
URL = f"{base_url}/twitter/v1/profile/{SCREEN_NAME}/replies"
HEADERS = {"x-api-key": API_KEY}

TOTAL_RUNS = 50
MAX_RETRIES = 4
SLEEP = 0.5


# =====================
# HELPERS
# =====================
def make_request(cursor=None):
    params = {}
    if cursor:
        params["cursor"] = cursor

    last_status = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(URL, headers=HEADERS, params=params, timeout=25)
            last_status = resp.status_code

            if resp.status_code == 200:
                return resp.json()

            time.sleep(SLEEP)

        except requests.RequestException:
            time.sleep(SLEEP)

    raise Exception(f"Failed after {MAX_RETRIES} attempts. Last status={last_status}")


# =====================
# MAIN
# =====================
def main():
    unexpected_hits = defaultdict(list)

    print(f"\n🔍 Twitter replies consistency check for @{SCREEN_NAME}")
    print(f"🔁 Total runs: {TOTAL_RUNS}\n")

    for run in range(1, TOTAL_RUNS + 1):
        print(f"\n==============================")
        print(f"▶️ RUN {run}")
        print(f"==============================")

        cursor = None
        page = 1

        while True:
            data = make_request(cursor)

            tweets = data.get("tweets", []) or []
            count = len(tweets)

            print(f"\n📄 Run {run} — Page {page} — {count} tweets")

            # Stop condition: empty page
            if count == 0:
                print("⛔ Empty page returned. Ending pagination for this run.")
                break

            for idx, t in enumerate(tweets, start=1):
                tweet_obj = t.get("tweet") or {}
                user_details = tweet_obj.get("user_details") or {}

                sn = user_details.get("screen_name") or "<missing>"
                text = (tweet_obj.get("full_text") or "").replace("\n", " ").strip()

                print(f"   🔹 Tweet {idx}")
                print(f"      screen_name: {sn}")
                print(f"      full_text  : {text[:120]}")

                if sn.lower() != SCREEN_NAME.lower():
                    unexpected_hits[sn].append((run, page))

            cursor = data.get("cursor_bottom")
            if not cursor:
                print("⛔ No cursor_bottom found. Ending pagination for this run.")
                break

            print(f"➡️ Next cursor: {str(cursor)[:60]}...")
            page += 1
            time.sleep(SLEEP)

    # =====================
    # SUMMARY
    # =====================
    print("\n📊 === SUMMARY ===")

    if not unexpected_hits:
        print("✅ No unexpected screen_names detected across all runs.")
    else:
        print("❌ Unexpected screen_names detected:\n")
        for sn, occurrences in unexpected_hits.items():
            locations = ", ".join([f"(run {r}, page {p})" for r, p in occurrences])
            print(f"- {sn}: {locations}")

    print("\n🏁 Finished.\n")

if __name__ == "__main__":
    main()