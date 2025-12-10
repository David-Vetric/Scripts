# =================================================================
# SCRIPT TASK
# Run specific query until you find results that don't match query
# =================================================================

import requests
from dotenv import load_dotenv
import os
import time
import json
from datetime import datetime

# =====================
# CONFIG
# =====================
load_dotenv("/Users/davidrajchenberg/Desktop/Vetric/Scripts/dev.env")

# Set environment
is_dev = True
if is_dev:
    print("⚙️  Using DEV environment")
    API_KEY = os.getenv("API_KEY_S")
    base_url = os.getenv("URL_S")
else:
    print("🚀  Using PROD environment")
    API_KEY = os.getenv("API_KEY")
    base_url = os.getenv("URL")

SEARCH_URL = f"{base_url}/twitter/v1/search/recent"
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}
TYPED_QUERY = "until_time:1760373658 (from:ClueWr OR from:MufasaEvey OR from:GeneralsUpdates OR from:_johnny_bgood OR from:salbiya92 OR from:3200INGLESIDEd OR from:B4dD3cisi0ns OR from:StarcadeMediaKC OR from:iknowball717 OR from:realLarryAkin OR from:danielmooch1021 OR from:CaptainCrutch2 OR from:avayahsDad1216 OR from:sTClairboiy OR from:soonernationx OR from:myateif OR from:DMNYC888 OR from:codynpr1964)"

# Number of iterations
RUNS = 20
SLEEP_BETWEEN_RUNS = 2

# Allowed handles
VALID_HANDLES = {
    "ClueWr", "MufasaEvey", "GeneralsUpdates", "_johnny_bgood", "salbiya92",
    "3200INGLESIDEd", "B4dD3cisi0ns", "StarcadeMediaKC", "iknowball717",
    "realLarryAkin", "danielmooch1021", "CaptainCrutch2", "avayahsDad1216",
    "sTClairboiy", "soonernationx", "myateif", "DMNYC888", "codynpr1964"
}

# until_time in epoch (provided by client)
UNTIL_TIMESTAMP = 1760373658

# =====================
# HELPERS
# =====================

def run_query():
    params = {"query": TYPED_QUERY}
    response = requests.get(SEARCH_URL, headers=HEADERS, params=params)
    try:
        return response.json()
    except Exception:
        print("💀 Invalid JSON response")
        return None

def validate_response(data):
    """Check user handles and timestamps"""
    if not data or "tweets" not in data:
        return False, [], False, []

    wrong_users = []
    bad_timestamps = []

    for item in data["tweets"]:
        tweet = item.get("tweet")
        created_at = tweet.get("created_at")
        user_details = tweet.get("user_details")
        handle = user_details.get("screen_name")
        # Example format: "Thu Nov 13 14:37:32 +0000 2025"
        try:
            dt_obj = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
            epoch_time = int(dt_obj.timestamp())
        except Exception:
            epoch_time = None

        if handle not in VALID_HANDLES:
            wrong_users.append(handle)
        if epoch_time and epoch_time > UNTIL_TIMESTAMP:
            bad_timestamps.append({
                "UserScreenName": handle,
                "CreatedAt": created_at
            })

    handle_ok = len(wrong_users) == 0
    time_ok = len(bad_timestamps) == 0
    return handle_ok, wrong_users, time_ok, bad_timestamps

# =====================
# MAIN
# =====================

def main():
    print(f"\n🔁 Running query {RUNS} times...\n")

    for i in range(1, RUNS + 1):
        print(f"▶️ Run {i}/{RUNS}")
        data = run_query()
        handle_ok, wrong_users, time_ok, bad_timestamps = validate_response(data)

        # print(json.dumps(data, indent=2))

        # Handles check
        if handle_ok:
            print("🧩 Handles check: ✅ All valid")
        else:
            unique_wrong = sorted(set(wrong_users))
            print(f"🧩 Handles check: ❌ Invalid handles found: {unique_wrong}")

        # Time check
        if time_ok:
            print("⏰ Time check: ✅ All within until_time")
        else:
            print("⏰ Time check: ❌ Tweets beyond until_time:")
            for bad in bad_timestamps:
                print(f"   - @{bad['UserScreenName']} → {bad['CreatedAt']}")

        print("-" * 50)
        time.sleep(SLEEP_BETWEEN_RUNS)

    print("\n🏁 Done.\n")

if __name__ == "__main__":
    main()

