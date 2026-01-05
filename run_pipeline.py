from fetch import get_company_ids, fetch_company, save_raw_json
import os
import json
import pymysql
import time

RAW_DIR = "raw_data"

DB = pymysql.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="ml",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

cur = DB.cursor()


def insert_company(c):
    cur.execute("""
        INSERT INTO companies
        (company_id, company_logo, company_name, chart_link, about_company, website,
         nse_profile, bse_profile, face_value, book_value, roce_percentage, roe_percentage)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
        company_name=VALUES(company_name),
        company_logo=VALUES(company_logo)
    """, (
        c["id"], c["company_logo"], c["company_name"], c["chart_link"],
        c["about_company"], c["website"], c["nse_profile"], c["bse_profile"],
        c["face_value"], c["book_value"], c["roce_percentage"], c["roe_percentage"]
    ))


def insert_rows(table, rows, cols):
    for r in rows:
        values = [r.get(c) for c in cols]
        cur.execute(
            f"REPLACE INTO {table} ({','.join(cols)}) VALUES ({','.join(['%s']*len(cols))})",
            values
        )


def main():
    company_ids = get_company_ids()

    print("Processing", len(company_ids), "companies")

    for cid in company_ids:
        print("\n Fetching", cid)

        data = fetch_company(cid)
        if not data:
            print(" Failed:", cid)
            continue

        save_raw_json(cid, data)

        company = data["company"]
        d = data["data"]

        insert_company(company)

        insert_rows("analysis", d.get("analysis", []),
            ["id","company_id","compounded_sales_growth","compounded_profit_growth","stock_price_cagr","roe"])

        insert_rows("prosandcons", d.get("prosandcons", []),
            ["id","company_id","pros","cons"])

        insert_rows("balancesheet", d.get("balancesheet", []),
            ["id","company_id","year","equity_capital","reserves","borrowings",
             "other_liabilities","total_liabilities","fixed_assets","cwip",
             "investments","other_asset","total_assets"])

        insert_rows("profitandloss", d.get("profitandloss", []),
            ["id","company_id","year","sales","expenses","operating_profit",
             "opm_percentage","other_income","interest","depreciation",
             "profit_before_tax","tax_percentage","net_profit","eps","dividend_payout"])

        insert_rows("cashflow", d.get("cashflow", []),
            ["id","company_id","year","operating_activity","investing_activity",
             "financing_activity","net_cash_flow"])

        insert_rows("documents", d.get("documents", []),
            ["id","company_id","Year","Annual_Report"])

        print(cid, " saved")
        time.sleep(1)

    print("\nALL COMPANIES PROCESSED")


if __name__ == "__main__":
    main()
