import json
import requests
import os

# Load JSON from local file
with open("tools/data/spoc/fb/fb_posts_media.json", "r", encoding="utf-8") as file:
    response = json.load(file)

# Create a download folder
os.makedirs("Tools/Data/Downloads", exist_ok=True)

for node in response["data"]["nodes"]:
    image_url = node.get("image", {}).get("uri")
    if not image_url:
        print(f"No image found for node {node.get('id')}")
        continue

    print(f"Downloading image for {node['id']}...")
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(image_url, headers=headers, stream=True)
    r.raise_for_status()

    filename = f"Tools/Data/Downloads/{node['id']}.jpg"
    with open(filename, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)

    print(f"Saved to {filename}")