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
    raise EnvironmentError("Missing API key or base URL in env")

URL = f"{base_url}/facebook/v1/marketplace/search"
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/x-www-form-urlencoded"
}

SLEEP = 1
MAX_RETRIES = 4


# =====================
# HELPERS
# =====================
def make_request(end_cursor=None):

    data = {
        "query": "ps5",
        "filter_location_latitude": 25.7700,
        "filter_location_longitude": -80.1900,
        "virtual_category_id": 139967891347278,
        "filter_radius_km": 200,
        "filter_price_lower_bound": 20000,
        "commerce_search_sort_by": "PRICE_ASCEND",
    }

    # data = {
    #     "query": "ps5",
    #     "filter_location_latitude": 25.7700,
    #     "filter_location_longitude": -80.1900
    # }

    if end_cursor:
        data["end_cursor"] = end_cursor

    last_status = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(URL, headers=HEADERS, data=data, timeout=30)
            last_status = resp.status_code

            if resp.status_code == 200:
                return resp.json()

            print(f"⚠️ Attempt {attempt} returned {resp.status_code}")
            time.sleep(SLEEP)

        except requests.RequestException as e:
            print(f"⚠️ Error on attempt {attempt}: {e}")
            time.sleep(SLEEP)

    raise Exception(f"❌ Failed after {MAX_RETRIES} attempts. Last status = {last_status}")


# =====================
# MAIN
# =====================
def main():
    page = 1
    end_cursor = None

    # product_id -> { "title": str, "pages": [int, ...] }
    product_occurrences = defaultdict(lambda: {"title": None, "pages": []})
    total_items_seen = 0

    print("\n🔍 Searching Facebook Marketplace for duplicated products\n")

    while True:
        data = make_request(end_cursor)

        products = data.get("products", []) or []
        pagination = data.get("pagination") or {}

        print(f"\n📄 Page {page} — {len(products)} products")

        total_items_seen += len(products)

        for idx, p in enumerate(products, start=1):
            product_id = p.get("product_id")
            title = p.get("title")

            print(f"   🔹 Product {idx}: {product_id} — {title}")

            entry = product_occurrences[product_id]
            entry["title"] = title
            entry["pages"].append(page)

        end_cursor = pagination.get("end_cursor")
        has_next = pagination.get("has_next_page")

        if not end_cursor or not has_next:
            print("\n⛔ Pagination ended — no more pages.")
            break

        print(f"➡️ Next end_cursor: {str(end_cursor)[:50]}...")
        page += 1
        time.sleep(SLEEP)

    # =====================
    # SUMMARY
    # =====================
    total_unique_ids = len(product_occurrences)
    duplicated_ids = {
        pid: info for pid, info in product_occurrences.items()
        if len(info["pages"]) > 1
    }

    total_duplicated_ids = len(duplicated_ids)
    total_non_duplicated_ids = total_unique_ids - total_duplicated_ids

    duplicated_pct = (total_duplicated_ids / total_unique_ids * 100) if total_unique_ids else 0
    unique_pct = (total_non_duplicated_ids / total_unique_ids * 100) if total_unique_ids else 0

    print("\n📊 === DUPLICATED PRODUCTS SUMMARY ===")

    for product_id, info in duplicated_ids.items():
        print(f"\n🔁 Product ID: {product_id}")
        print(f"   Title: {info['title']}")
        print(f"   Appeared on pages: {info['pages']}")

    print("\n📈 === AGGREGATE STATS ===")
    print(f"Total items seen (incl. duplicates): {total_items_seen}")
    print(f"Total unique item IDs: {total_unique_ids}")
    print(f"Total duplicated item IDs: {total_duplicated_ids}")
    print(f"% duplicated item IDs: {duplicated_pct:.2f}%")
    print(f"% unique item IDs: {unique_pct:.2f}%")

    print("\n🏁 Finished.\n")


if __name__ == "__main__":
    main()


