import requests
import json
import os
import sys
from datetime import datetime

# === CONFIGURATION ===
# Credentials
BOT_ID = "d7c63fad-455b-48f2-b5a9-e1aa70b0a11e"
TOKEN = "bp_pat_3656eEvEX2jcOYqb6GahD31IgAa4jeyb5zzV"

# API Endpoints
BASE_API = "https://irres-listings-api.onrender.com/api"
LISTINGS_API = f"{BASE_API}/listings"
IMAGES_API = f"{BASE_API}/office-images"
LOCATIONS_API = f"{BASE_API}/locations"

# Botpress Headers
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "x-bot-id": BOT_ID,
    "Content-Type": "application/json"
}

def delete_table_rows(table_name):
    """
    Deletes all rows from a specified Botpress table.
    This ensures we don't have duplicate or stale data after a sync.
    """
    print(f"Emptying table: {table_name}...")
    url = f"https://api.botpress.cloud/v1/tables/{table_name}/rows/delete"
    try:
        res = requests.post(url, headers=HEADERS, json={"deleteAllRows": True})
        res.raise_for_status()
    except requests.exceptions.HTTPError as err:
        # If the table doesn't exist or other API error, print it but don't crash immediately
        print(f"Warning: Could not clear table {table_name}: {err}")
    except Exception as e:
        print(f"Error clearing table {table_name}: {e}")
        raise

def sync_listings():
    """
    Syncs Listings to ListingsTable.
    Maps API fields to Botpress columns.
    """
    print("Fetching listings...")
    try:
        res = requests.get(LISTINGS_API)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"Failed to fetch listings: {e}")
        return

    if not data.get('success') or not data.get('listings'):
        print("No listings found in API response.")
        return

    # Clear existing data
    delete_table_rows("ListingsTable")
    
    rows = []
    # Process each listing from the API
    for l in data['listings']:
        # We serialize 'details' to a JSON string because it's a nested object
        # and Botpress tables work best with flat structures or stringified JSON.
        details_json = json.dumps(l.get('details', {}), ensure_ascii=False)
        
        row = {
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
            "details": details_json,
            "last_updated": datetime.now().isoformat()
        }
        rows.append(row)

    # Insert rows in batch
    try:
        insert_url = f"https://api.botpress.cloud/v1/tables/ListingsTable/rows"
        res = requests.post(insert_url, headers=HEADERS, json={"rows": rows})
        res.raise_for_status()
        print(f"Inserted {len(rows)} listings.")
    except Exception as e:
        print(f"Failed to insert listings: {e}")

def sync_office_images():
    """
    Syncs Office Images to OfficeImagesTable.
    """
    print("Fetching office images...")
    try:
        res = requests.get(IMAGES_API)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"Failed to fetch office images: {e}")
        return
    
    delete_table_rows("OfficeImagesTable")
    
    image_rows = []
    # The API returns a dict: {"IrresLatemImage": "url", ...}
    if data.get('data'):
        for key, url in data['data'].items():
            name = key.replace("Irres", "").replace("Image", "")
            image_rows.append({"office_name": name, "image_url": url})
    
    if image_rows:
        try:
            insert_url = f"https://api.botpress.cloud/v1/tables/OfficeImagesTable/rows"
            requests.post(insert_url, headers=HEADERS, json={"rows": image_rows})
            print(f"Inserted {len(image_rows)} office images.")
        except Exception as e:
            print(f"Failed to insert office images: {e}")
    else:
        print("No office images found to insert.")

def sync_locations():
    """
    Syncs Locations to FilterLocationsTable into 1 row.
    Columns populated: 'all_locations' and 'location_groups'.
    Stores data as JSON strings for easy parsing inside the bot.
    """
    print("Fetching locations...")
    try:
        res = requests.get(LOCATIONS_API)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"Failed to fetch locations: {e}")
        return
    
    if not data.get('data'):
        print("No location data found in API.")
        return

    # Clear table
    delete_table_rows("FilterLocationsTable")
    
    # Extract data from the new API structure
    # 'all_locations' is a list of dicts: [{"label": "x", "value": "x"}, ...]
    # 'location_groups' is a dict: {"Group": ["sub", "sub"], ...}
    all_locations_data = data['data'].get('all_locations', [])
    location_groups_data = data['data'].get('location_groups', {})
    
    # Serialize to JSON strings (ensure_ascii=False preserves accents like 'é')
    all_locations_str = json.dumps(all_locations_data, ensure_ascii=False)
    location_groups_str = json.dumps(location_groups_data, ensure_ascii=False)
    
    # Create the single row payload
    row_payload = {
        "all_locations": all_locations_str,
        "location_groups": location_groups_str
    }
    
    try:
        insert_url = f"https://api.botpress.cloud/v1/tables/FilterLocationsTable/rows"
        res = requests.post(insert_url, headers=HEADERS, json={"rows": [row_payload]})
        res.raise_for_status()
        print("Inserted locations and location groups into 1 row.")
    except Exception as e:
        print(f"Failed to insert locations: {e}")

if __name__ == "__main__":
    print("--- Starting Sync Process ---")
    try:
        sync_listings()
        sync_office_images()
        sync_locations()
        print("✅ Sync complete!")
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        sys.exit(1)
