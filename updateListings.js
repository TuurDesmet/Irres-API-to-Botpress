import fetch from "node-fetch";

const BOT_ID = "d7c63fad-455b-48f2-b5a9-e1aa70b0a11e";             
const TOKEN = "bp_pat_3656eEvEX2jcOYqb6GahD31IgAa4jeyb5zzV";        
const TABLE = "ListingsTable";                                      
const LISTINGS_API = "https://irres-listings-api.onrender.com/api/listings";

async function updateListings() {
  try {
    console.log("Fetching listings from API...");
    const res = await fetch(LISTINGS_API);
    const data = await res.json();
    
    if (!data.success || !data.listings?.length) {
      throw new Error("No listings found from API.");
    }
    
    // -------------------------------------------------------
    // STEP 1 — DELETE ALL EXISTING ROWS
    // -------------------------------------------------------
    console.log("Deleting all rows...");
    const deleteRes = await fetch(`https://api.botpress.cloud/v1/tables/${TABLE}/rows/delete`, {
      method: "POST",
      headers: {
        "x-bot-id": BOT_ID,
        "Authorization": `Bearer ${TOKEN}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ deleteAllRows: true })
    });

    const deleteData = await deleteRes.json();
    console.log(`Deleted rows:`, deleteData);
    
    // -------------------------------------------------------
    // STEP 2 — INSERT NEW ROWS
    // -------------------------------------------------------
    console.log(`Inserting ${data.listings.length} new rows...`);

    const rows = data.listings.map(l => ({
      listing_id: l.listing_id,
      listing_url: l.listing_url,
      photo_url: l.photo_url || "",
      price: l.price || "",
      location: l.location || "",
      description: l.description || "",
      listing_type: l.listing_type || "",

      // ----------------------------
      // New variables you added
      // ----------------------------
      Title: l.Title || "",
      Button1_Label: l.Button1_Label || "Bekijk het op onze website",
      Button2_Label: l.Button2_Label || `Contacteer ${l.firstname || ""} - Irres`,
      Button2_email: l.Button2_email || "",

      // ----------------------------
      // NEW: details object as JSON
      // ----------------------------
      details: JSON.stringify(l.details || {}),

      last_updated: new Date().toISOString()
    }));

    const insertRes = await fetch(`https://api.botpress.cloud/v1/tables/${TABLE}/rows`, {
      method: "POST",
      headers: {
        "x-bot-id": BOT_ID,
        "Authorization": `Bearer ${TOKEN}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ rows, waitComputed: true })
    });
    
    const insertData = await insertRes.json();
    console.log(`Inserted rows:`, insertData);
    console.log("✅ Listings table updated successfully!");
    
  } catch (err) {
    console.error("❌ Error updating listings:", err.message);
    process.exit(1); 
  }
}

updateListings();
