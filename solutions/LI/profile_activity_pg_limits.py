import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv("/Users/davidrajchenberg/Desktop/Vetric/Scripts/dev.env")

# Set the environment (Dev or Prod)
is_dev = True

if is_dev:
    print("Dev")
    API_KEY = os.getenv("API_KEY_S")
    base_url = os.getenv("URL_S")
else:
    print("Prod")
    API_KEY = os.getenv("API_KEY")
    base_url = os.getenv("URL")

URN = "urn:li:fsd_profile:ACoAAAAABL0B3SGhqeNX998wiOuk_8hYA6ojLwg"
BASE_URL = f'{base_url}/linkedin/v1/profile/{URN}/activity?type=posts'
HEADERS = {'x-api-key': API_KEY}
MAX_RETRIES = 5

def make_request_with_retries(url):
    """Make API requests with retries."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: Status code {response.status_code}, Attempt {attempt} of {MAX_RETRIES}")
        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt} of {MAX_RETRIES}: {e}")
    return None

def count_activity_types(activity, page_num, current_cursor):
    """Count and print activity types and main text."""
    activity_counts = {}
    for item in activity:
        activity_type = item.get('activity_type', 'Unknown')
        activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
        main_text = item.get('text', '')
        creation_date = item.get('created_at', '')
        print(f"[Page {page_num} | cursor={current_cursor!r}] Activity Type: {activity_type}")
        print(f"Main Text: {main_text}")
        print(f"Creation Date: {creation_date}")
        print("---")
    return activity_counts

def main():
    cursor = None
    total_counts = {}
    page = 1
    while True:
        # Build URL with cursor if available
        url = BASE_URL if cursor is None else f"{BASE_URL}&cursor={cursor}"
        print(f"\nFetching Page {page} | Using cursor={cursor!r}")
        data = make_request_with_retries(url)
        if data is None:
            print("Failed to retrieve data after maximum retries. Stopping.")
            break
        activity = data.get('activity', [])
        page_counts = count_activity_types(activity, page, cursor)
        # Aggregate counts
        for key, value in page_counts.items():
            total_counts[key] = total_counts.get(key, 0) + value
        # Get next cursor
        cursor = data.get('cursor')
        print(f"Next cursor: {cursor!r}")
        # Stop condition: when cursor is explicitly null
        if cursor is None:
            print("Cursor is null. Finished paginating.")
            break
        page += 1
    print("\n=== Final Activity Type Counts ===")
    for activity_type, count in total_counts.items():
        print(f"{activity_type}: {count}")

if __name__ == '__main__':
    main()