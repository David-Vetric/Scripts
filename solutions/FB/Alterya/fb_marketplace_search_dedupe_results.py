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
    API_KEY = os.getenv("API_KEY_S")
    base_url = os.getenv("URL_S")
else:
    API_KEY = os.getenv("API_KEY")
    base_url = os.getenv("URL")

if not API_KEY or not base_url:
    raise EnvironmentError("Missing API key or base URL")

URL = f"{base_url}/facebook/v1/marketplace/search"

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/x-www-form-urlencoded",
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

    if end_cursor:
        data["end_cursor"] = end_cursor

    last_status = None

    for _ in range(MAX_RETRIES):
        resp = requests.post(URL, headers=HEADERS, data=data, timeout=30)
        last_status = resp.status_code

        if resp.status_code == 200:
            return resp.json()

        time.sleep(SLEEP)

    raise Exception(f"Request failed after retries (last status {last_status})")


# =====================
# MAIN
# =====================
def main():
    end_cursor = None
    page = 1

    seen_product_ids = set()
    unique_products = []

    while True:
        data = make_request(end_cursor)

        products = data.get("products", []) or []
        pagination = data.get("pagination") or {}

        print(f"📄 Page {page} — received {len(products)} products")

        for p in products:
            product_id = p.get("product_id")
            if not product_id:
                continue

            if product_id in seen_product_ids:
                continue

            seen_product_ids.add(product_id)
            unique_products.append(p)

            title = p.get("title")
            print(f"   ✅ {product_id} — {title}")

        end_cursor = pagination.get("end_cursor")
        has_next = pagination.get("has_next_page")

        if not end_cursor or not has_next:
            break

        page += 1
        time.sleep(SLEEP)

    # =====================
    # SUMMARY
    # =====================
    print("\n📊 SUMMARY")
    print(f"Total pages fetched: {page}")
    print(f"Total unique products returned: {len(unique_products)}")
    print("\n🏁 Finished.")


if __name__ == "__main__":
    main()

