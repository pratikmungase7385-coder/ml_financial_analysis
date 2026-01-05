import re
from sqlalchemy import text
from db import engine

def extract_number(s):
    if not s:
        return None
    m = re.search(r'([\d.]+)%', s)
    return float(m.group(1)) if m else None

def load_features():
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT company_id,
                   compounded_sales_growth,
                   compounded_profit_growth,
                   roe
            FROM analysis
        """)).fetchall()

    data = {}

    for r in rows:
        sales = extract_number(r.compounded_sales_growth)
        profit = extract_number(r.compounded_profit_growth)
        roe = extract_number(r.roe)

        if None in (sales, profit, roe):
            continue

        data[r.company_id] = (sales, profit, roe)

    return data
