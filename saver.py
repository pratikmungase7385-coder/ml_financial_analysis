import json
import os
import pymysql

DB = pymysql.connect(
    host="localhost",
    user="root",
    password="mysql",   # change if needed
    database="ml",
    cursorclass=pymysql.cursors.DictCursor
)

RAW_DIR = "raw_data"

def to_int(x):
    try:
        return int(float(x))
    except:
        return None

def insert_company(cur, c):
    cur.execute("""
        INSERT INTO companies
        (company_id, company_logo, company_name, chart_link, about_company, website,
         nse_profile, bse_profile, face_value, book_value, roce_percentage, roe_percentage)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE company_name=VALUES(company_name)
    """, (
        c["id"], c["company_logo"], c["company_name"], c["chart_link"],
        c["about_company"], c["website"], c["nse_profile"], c["bse_profile"],
        to_int(c["face_value"]), to_int(c["book_value"]),
        float(c["roce_percentage"] or 0), float(c["roe_percentage"] or 0)
    ))

def insert_rows(cur, table, rows, cols):
    for r in rows:
        values = [r.get(c) for c in cols]
        cur.execute(
            f"REPLACE INTO {table} ({','.join(cols)}) VALUES ({','.join(['%s']*len(cols))})",
            values
        )

def main():
    cur = DB.cursor()

    for file in os.listdir(RAW_DIR):
        path = os.path.join(RAW_DIR, file)

        with open(path, "r", encoding="utf8") as f:
            data = json.load(f)

        company = data["company"]
        cid = company["id"]

        print("Saving", cid)

        insert_company(cur, company)

        d = data["data"]

        insert_rows(cur, "analysis", d.get("analysis", []),
            ["id","company_id","compounded_sales_growth","compounded_profit_growth","stock_price_cagr","roe"])

        insert_rows(cur, "prosandcons", d.get("prosandcons", []),
            ["id","company_id","pros","cons"])

        insert_rows(cur, "balancesheet", d.get("balancesheet", []),
            ["id","company_id","year","equity_capital","reserves","borrowings",
             "other_liabilities","total_liabilities","fixed_assets","cwip",
             "investments","other_asset","total_assets"])

        insert_rows(cur, "profitandloss", d.get("profitandloss", []),
            ["id","company_id","year","sales","expenses","operating_profit",
             "opm_percentage","other_income","interest","depreciation",
             "profit_before_tax","tax_percentage","net_profit","eps","dividend_payout"])

        insert_rows(cur, "cashflow", d.get("cashflow", []),
            ["id","company_id","year","operating_activity","investing_activity",
             "financing_activity","net_cash_flow"])

        insert_rows(cur, "documents", d.get("documents", []),
            ["id","company_id","Year","Annual_Report"])

    DB.commit()
    print("ALL DATA SAVED")

if __name__ == "__main__":
    main()
