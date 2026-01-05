import re
import json
import os


# ==============================
# Universal value cleaner
# ==============================

def to_float(val):
    """
    Converts API values into float.
    Handles:
      1234
      "1,234"
      "12.5"
      "12%"
      "10 Years: 11%"
      None
      "NULL"
    """

    if val is None:
        return None

    if isinstance(val, (int, float)):
        return float(val)

    if isinstance(val, str):
        val = val.strip().replace(",", "")

        if val.upper() in ["NULL", "NA", "N/A", ""]:
            return None

        # extract first number from string
        match = re.search(r"-?\d+\.?\d*", val)
        if match:
            return float(match.group())

    return None


# ==============================
# Clean financial tables
# (P&L, Balance Sheet, Cashflow)
# ==============================

def clean_financial_rows(rows):
    """
    Converts all numeric columns to float.
    Leaves id, company_id, year untouched.
    """

    cleaned = []

    for r in rows:
        row = {}

        for k, v in r.items():
            if k.lower() in ["id", "company_id", "year"]:
                row[k] = v
            else:
                row[k] = to_float(v)

        cleaned.append(row)

    return cleaned


# ==============================
# Clean Analysis table
# ==============================

def clean_analysis(rows):
    """
    Converts API 'analysis' block into numeric format.
    """

    output = []

    for r in rows:
        output.append({
            "company_id": r["company_id"],
            "period": r["compounded_sales_growth"].split(":")[0].strip(),

            "sales_growth": to_float(r["compounded_sales_growth"]),
            "profit_growth": to_float(r["compounded_profit_growth"]),
            "roe": to_float(r["roe"]),
            "stock_cagr": to_float(r["stock_price_cagr"])
        })

    return output


# ==============================
# Validate API response
# ==============================

def validate_api_data(api_json):
    """
    Ensures required sections exist.
    """
    if "data" not in api_json:
        return False

    required = ["profitandloss", "balancesheet", "cashflow"]

    for key in required:
        if key not in api_json["data"]:
            return False

    return True


# ==============================
# Log cleaned data for debugging
# ==============================

def log_cleaned(company_id, data):
    os.makedirs("logs", exist_ok=True)

    with open(f"logs/{company_id}.json", "w") as f:
        json.dump(data, f, indent=2, default=str)
