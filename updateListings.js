import fetch from "node-fetch";

const BOT_ID = "d7c63fad-455b-48f2-b5a9-e1aa70b0a11e"; // <-- jouw bot id
const TOKEN = "bp_pat_3656eEvEX2jcOYqb6GahD31IgAa4jeyb5zzV";        // <-- jouw token
const TABLE = "ListingsTable";                                      // <-- exacte tabelnaam
const LISTINGS_API = "https://irres-listings-api.onrender.com/api/listings";

async function updateListings() {
  try {
    console.log("Fetching listings from API...");
    const res = await fetch(LISTINGS_API);
    const data = await res.json();

    if (!data.success || !Array.isArray(data.listings) || !data.listings.length) {
      throw new Error("No listings found from API.");
    }

    // -------------------------------------------------------
    // STEP 1 — DELETE ALL EXISTING ROWS
    // -------------------------------------------------------
    console.log("Deleting all rows...");
    const deleteRes = await fetch(
      `https://api.botpress.cloud/v1/tables/${TABLE}/rows/delete`,
      {
        method: "POST",
        headers: {
          "x-bot-id": BOT_ID,
          Authorization: `Bearer ${TOKEN}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ deleteAllRows: true }),
      }
    );

    const deleteData = await deleteRes.json();
    console.log(`Deleted rows:`, deleteData);

    // -------------------------------------------------------
    // STEP 2 — INSERT NEW ROWS
    // -------------------------------------------------------
    console.log(`Inserting ${data.listings.length} new rows...`);

    const rows = data.listings.map((l = {}) => ({
      // basisvelden
      listing_id: String(l.listing_id ?? ""),
      listing_url: String(l.listing_url ?? ""),
      photo_url: String(l.photo_url ?? ""),
      price: String(l.price ?? ""),
      location: String(l.location ?? ""),
      description: String(l.description ?? ""),
      listing_type: String(l.listing_type ?? ""),

      // knoppen en title
      Title: String(l.Title ?? ""),
      Button1_Label: String(l.Button1_Label ?? ""),
      Button2_Label: String(l.Button2_Label ?? ""),
      Button2_email: String(l.Button2_email ?? ""),
      Button3_Label: String(l.Button3_Label ?? ""),
      Button3_Value: String(l.Button3_Value ?? ""),

      // details als JSON-string (kolomtype in Botpress: string)
      details: JSON.stringify(l.details ?? {}),

      // optionele extra kolom in jouw tabel (als je die hebt)
      last_updated: new Date().toISOString(),
    }));

    console.log("Example row being sent:", rows[0]);

    const insertRes = await fetch(
      `https://api.botpress.cloud/v1/tables/${TABLE}/rows`,
      {
        method: "POST",
        headers: {
          "x-bot-id": BOT_ID,
          Authorization: `Bearer ${TOKEN}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ rows, waitComputed: true }),
      }
    );

    const insertData = await insertRes.json();
    console.log(`Inserted rows:`, JSON.stringify(insertData, null, 2));
    console.log("✅ Listings table updated successfully!");
  } catch (err) {
    console.error("❌ Error updating listings:", err.message);
    process.exit(1);
  }
}

updateListings();
