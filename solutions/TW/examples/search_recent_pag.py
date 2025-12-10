# =====================
# SCRIPT TASK
# TW - search/latest script to find specific tweet
# =====================

import requests
from dotenv import load_dotenv
import os
import time

# =====================
# CONFIG
# =====================
# Load environment variables
load_dotenv("/Users/davidrajchenberg/Desktop/Vetric/Scripts/dev.env")

# Set environment (dev or prod)
is_dev = True

if is_dev:
    print("Using DEV environment")
    API_KEY = os.getenv("API_KEY_S")
    base_url = os.getenv("URL_S")
else:
    print("Using PROD environment")
    API_KEY = os.getenv("API_KEY")
    base_url = os.getenv("URL")

QUERY = "cleptogirls"
TARGET_REST_ID = "1879228541239443931"  # Tweet ID we're searching for
MAX_RETRIES = 5
SLEEP_BETWEEN_RETRIES = 2

# =====================
# HELPERS
# =====================
def make_request(url, headers, retries=MAX_RETRIES):
    """Make GET request with retry logic."""
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(SLEEP_BETWEEN_RETRIES)
            else:
                raise

def find_tweet_in_page(data, target_rest_id):
    """Look inside 'tweets' array for the tweet with matching rest_id."""
    tweets = data.get("tweets", [])
    for entry in tweets:
        tweet = entry.get("tweet", {})
        if tweet.get("rest_id") == target_rest_id:
            return entry  # return the full tweet object (entryId + tweet)
    return None

def get_cursor_bottom(data):
    """Extract cursor_bottom from root level."""
    return data.get("cursor_bottom")

# =====================
# MAIN LOGIC
# =====================
def main():
    headers = {'x-api-key': API_KEY}
    cursor = None
    page = 1
    total_tweets_checked = 0

    try:
        while True:
            # Construct URL
            if cursor:
                url = f"{base_url}/twitter/v1/search/latest?query={QUERY}&cursor={cursor}"
            else:
                url = f"{base_url}/twitter/v1/search/latest?query={QUERY}"

            print(f"\nFetching page {page} → {url}")
            data = make_request(url, headers)

            # Count tweets in this page
            tweets_in_page = len(data.get("tweets", []))
            total_tweets_checked += tweets_in_page
            print(f"→ Tweets in this page: {tweets_in_page} (Total checked so far: {total_tweets_checked})")

            # Search for target tweet
            tweet_entry = find_tweet_in_page(data, TARGET_REST_ID)
            if tweet_entry:
                print("\n✅ FOUND TWEET IN THIS PAGE!")
                print(tweet_entry)
                print(f"\nTotal tweets checked before finding it: {total_tweets_checked}")
                break
            else:
                print("Tweet not found in this page. Moving to next page...")

            # Move to next page
            cursor = get_cursor_bottom(data)
            if not cursor:
                print(f"\nReached end of results — tweet not found after {total_tweets_checked} tweets.")
                break

            print(f"→ Next cursor: {cursor}")
            page += 1
            time.sleep(1)  # Prevent rate limits

    except KeyboardInterrupt:
        print(f"\n🛑 Stopped by user at page {page}. Total tweets checked: {total_tweets_checked}")

if __name__ == '__main__':
    main()