import requests
import json
import os
import sys
from datetime import datetime

# === CONFIGURATION ===
# These credentials are taken from your original JS file
BOT_ID = "d7c63fad-455b-48f2-b5a9-e1aa70b0a11e"
TOKEN = "bp_pat_3656eEvEX2jcOYqb6GahD31IgAa4jeyb5zzV"

# API Endpoints
BASE_API = "https://irres-listings-api.onrender.com/api"
LISTINGS_API = f"{BASE_API}/listings"
IMAGES_API = f"{BASE_API}/office-images"
LOCATIONS_API = f"{BASE_API}/locations"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "x-bot-id": BOT_ID,
    "Content-Type": "application/json"
}

def delete_table_rows(table_name):
    """Deletes all rows from a specified Botpress table."""
    print(f"Emptying table: {table_name}...")
    url = f"https://api.botpress.cloud/v1/tables/{table_name}/rows/delete"
    try:
        res = requests.post(url, headers=HEADERS, json={"deleteAllRows": True})
        res.raise_for_status()
    except Exception as e:
        print(f"Error clearing table {table_name}: {e}")
        raise

def sync_listings():
    """Syncs Listings to ListingsTable."""
    print("Fetching listings...")
    res = requests.get(LISTINGS_API)
    data = res.json()
    if not data.get('success') or not data.get('listings'):
        return

    delete_table_rows("ListingsTable")
    
    rows = []
    for l in data['listings']:
        rows.append({
            "listing_id": l.get('listing_id'),
            "listing_url": l.get('listing_url'),
            "photo_url": l.get('photo_url'),
            "price": l.get('price'),
            "location": l.get('location'),
            "description": l.get('description'),
            "listing_type": l.get('listing_type'),
            "Title": l.get('Title', ""),
            "Button1_Label": l.get('Button1_Label', "Bekijk het op onze website"),
            "Button2_Label": l.get('Button2_Label', ""),
            "Button2_email": l.get('Button2_email', ""),
            "Button3_Label": l.get('Button3_Label'),
            "Button3_Value": l.get('Button3_Value'),
            "details": json.dumps(l.get('details', {})),
            "last_updated": datetime.now().isoformat()
        })

    requests.post(f"https://api.botpress.cloud/v1/tables/ListingsTable/rows", headers=HEADERS, json={"rows": rows})
    print(f"Inserted {len(rows)} listings.")

def sync_office_images():
    """Syncs Office Images to OfficeImagesTable as separate rows."""
    print("Fetching office images...")
    res = requests.get(IMAGES_API)
    data = res.json()
    
    delete_table_rows("OfficeImagesTable")
    
    image_rows = []
    for key, url in data['data'].items():
        name = key.replace("Irres", "").replace("Image", "")
        image_rows.append({"office_name": name, "image_url": url})
    
    requests.post(f"https://api.botpress.cloud/v1/tables/OfficeImagesTable/rows", headers=HEADERS, json={"rows": image_rows})
    print(f"Inserted {len(image_rows)} office images.")

def sync_locations():
    """Syncs Locations to FilterLocationsTable into 1 row."""
    print("Fetching locations...")
    res = requests.get(LOCATIONS_API)
    data = res.json()
    
    delete_table_rows("FilterLocationsTable")
    
    location_string = ", ".join(data['data']['locations'])
    requests.post(f"https://api.botpress.cloud/v1/tables/FilterLocationsTable/rows", headers=HEADERS, json={
        "rows": [{"all_locations": location_string}]
    })
    print("Inserted locations into 1 row.")

if __name__ == "__main__":
    try:
        sync_listings()
        sync_office_images()
        sync_locations()
        print("✅ Sync complete!")
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        sys.exit(1)
