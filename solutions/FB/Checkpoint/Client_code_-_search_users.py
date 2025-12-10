import requests
from collections import Counter

API_KEY = ""# Replace with your actual API key
def make_request(cursor=None):
    url = "https://api.vetric.io/facebook/v1/search/users"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "x-api-key": API_KEY,
    }
    data = {
        "typed_query": "HKTDC",
        "transform": "true",
    }
    if cursor:
        data["end_cursor"] = cursor

    last_status = None
    for attempt in range(4):
        try:
            print(f"end_cursor- {data}")
            resp = requests.post(url, headers=headers, data=data, timeout=30)
            last_status = resp.status_code
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException:
            pass

    raise Exception(f"Failed after 4 attempts. Last status code: {last_status}")

def main():
    has_more = True
    cursor = None
    requested_id = ""

    request_count = 0
    results_count = 0

    seen_ids = set()
    duplicate_count = 0
    id_counter = Counter()

    while has_more:
        result = make_request(cursor)
        request_count += 1

        results = result.get("results", []) or []
        results_count += len(results)

        for user in results:
            uid = str(user.get("id", ""))
            name = user.get("name", "")
            print(f"id-{uid} name-{name}")

            # count & detect duplicates
            id_counter[uid] += 1
            if uid in seen_ids:
                duplicate_count += 1  # this occurrence is a duplicate
            else:
                seen_ids.add(uid)

            # stop early if target found
            if uid == requested_id:
                print(f"Found the ID-{requested_id}")
                has_more = False
                break

        print(f"request_count: {request_count}")
        print(f"results_count (total seen this run): {results_count}")
        print(f"unique_ids_so_far: {len(seen_ids)}")
        print(f"duplicate_occurrences_so_far: {duplicate_count}")
        print("-" * 40)

        if has_more and result.get("page_info", {}).get("has_next_page", False):
            cursor = result["page_info"]["end_cursor"]
        else:
            has_more = False

    # Final summary
    # Build a small “top duplicates” list (ids that appeared >1 time)
    duplicates_detail = [(uid, cnt) for uid, cnt in id_counter.items() if cnt > 1]
    duplicates_detail.sort(key=lambda x: x[1], reverse=True)

    print("\n=== SUMMARY ===")
    print(f"Total requests: {request_count}")
    print(f"Total results processed: {results_count}")
    print(f"Unique IDs: {len(seen_ids)}")
    print(f"Duplicate occurrences: {duplicate_count}")
    if duplicates_detail:
        print("Most frequent duplicate IDs (uid -> count):")
        for uid, cnt in duplicates_detail[:10]:
            print(f"  {uid} -> {cnt}")
    else:
        print("No duplicates found.")

if __name__ == "__main__":
    main()
