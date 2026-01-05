import pandas as pd
import requests
import time
import json
import os

API_KEY = "ghfkffu6378382826hhdjgk"
BASE_URL = "https://bluemutualfund.in/server/api/company.php"

EXCEL_FILE = "data/Nifty100Companies.xlsx"
RAW_DATA_DIR = "raw_data"

os.makedirs(RAW_DATA_DIR, exist_ok=True)


# ================= LOAD COMPANY IDS =================
def get_company_ids():
    df = pd.read_excel(EXCEL_FILE)

    print("Excel columns:", df.columns.tolist())

    # Screener / Nifty files usually use Symbol
    if "Symbol" in df.columns:
        ids = df["Symbol"]
    elif "company_id" in df.columns:
        ids = df["company_id"]
    else:
        raise Exception("No company id column found in Excel")

    ids = ids.dropna().astype(str).str.strip().unique().tolist()

    print("Total companies loaded:", len(ids))
    print("First 10:", ids[:10])

    return ids


# ================= FETCH SINGLE COMPANY =================
def fetch_company(company_id, retries=3):
    url = f"{BASE_URL}?id={company_id}&api_key={API_KEY}"

    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=15)

            if r.status_code != 200:
                raise Exception(f"HTTP {r.status_code}")

            data = r.json()

            # basic validation
            if "company" not in data or "data" not in data:
                raise Exception("Invalid API response structure")

            return data

        except Exception as e:
            print(f"❌ {company_id} failed (attempt {attempt+1}): {e}")
            time.sleep(2)

    print(f"🚨 {company_id} skipped after {retries} retries")
    return None


# ================= SAVE RAW JSON =================
def save_raw_json(company_id, data):
    path = os.path.join(RAW_DATA_DIR, f"{company_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"📁 Saved raw data → {path}")


# ================= MAIN PIPELINE =================
def run():
    company_ids = get_company_ids()

    success = 0
    failed = 0

    for cid in company_ids:
        print(f"\n🔄 Fetching {cid} ...")

        data = fetch_company(cid)

        if data:
            save_raw_json(cid, data)
            success += 1
        else:
            failed += 1

        time.sleep(1)   # avoid API blocking

    print("\n==============================")
    print(" Success:", success)
    print(" Failed:", failed)
    print("==============================")


if __name__ == "__main__":
    run()
