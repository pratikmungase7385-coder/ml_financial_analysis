# from flask import Flask, render_template, request, redirect, abort
# import pymysql

# app = Flask(__name__)

# db = pymysql.connect(
#     host="localhost",
#     user="root",
#     password="mysql",
#     database="ml",
#     cursorclass=pymysql.cursors.DictCursor,
#     autocommit=True
# )

# # ================= HOME =================
# @app.route("/")
# def home():
#     cur = db.cursor()
#     cur.execute("""
#         SELECT DISTINCT c.company_id, c.company_name
#         FROM analysis a
#         JOIN companies c ON a.company_id = c.company_id
#         ORDER BY c.company_name
#     """)
#     examples = cur.fetchall()
#     return render_template("home.html", examples=examples)

# # ================= SEARCH =================
# @app.route("/search")
# def search():
#     q = request.args.get("q")

#     if not q:
#         return redirect("/")

#     cur = db.cursor()
#     cur.execute("""
#         SELECT company_id
#         FROM companies
#         WHERE company_id=%s OR company_name LIKE %s
#         LIMIT 1
#     """, (q, "%" + q + "%"))

#     row = cur.fetchone()
#     if not row:
#         return "Company not found", 404

#     return redirect("/company/" + row["company_id"])

# # ================= ALL COMPANIES =================
# @app.route("/companies")
# def companies():
#     cur = db.cursor()
#     cur.execute("""
#         SELECT company_id, company_name, company_logo
#         FROM companies
#         ORDER BY company_name
#     """)
#     companies = cur.fetchall()
#     return render_template("list.html", companies=companies)

# # ================= COMPANY PAGE =================
# @app.route("/company/<cid>")
# def company(cid):
#     cur = db.cursor()

#     # Company info
#     cur.execute("SELECT * FROM companies WHERE company_id=%s", (cid,))
#     company = cur.fetchone()
#     if not company:
#         abort(404)

#     # Optional Analysis
#     cur.execute("SELECT * FROM analysis WHERE company_id=%s", (cid,))
#     analysis = cur.fetchall()

#     cur.execute("SELECT pros FROM prosandcons WHERE company_id=%s AND pros IS NOT NULL", (cid,))
#     pros = cur.fetchall()

#     cur.execute("SELECT cons FROM prosandcons WHERE company_id=%s AND cons IS NOT NULL", (cid,))
#     cons = cur.fetchall()

#     # Financials
#     cur.execute("SELECT * FROM balancesheet WHERE company_id=%s ORDER BY year", (cid,))
#     balancesheet = cur.fetchall()

#     cur.execute("SELECT * FROM profitandloss WHERE company_id=%s ORDER BY year", (cid,))
#     profitandloss = cur.fetchall()

#     cur.execute("SELECT * FROM cashflow WHERE company_id=%s ORDER BY year", (cid,))
#     cashflow = cur.fetchall()

#     cur.execute("SELECT * FROM documents WHERE company_id=%s ORDER BY year DESC", (cid,))
#     documents = cur.fetchall()

#     return render_template(
#         "company.html",
#         company=company,
#         analysis=analysis,
#         pros=pros,
#         cons=cons,
#         balancesheet=balancesheet,
#         profitandloss=profitandloss,
#         cashflow=cashflow,
#         documents=documents
#     )

# if __name__ == "__main__":
#     app.run(debug=True)


from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pymysql


from fastapi.responses import RedirectResponse

app = FastAPI()


from fastapi import Response

from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(SessionMiddleware, secret_key="super-secret")


@app.middleware("http")
async def no_cache(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# db = pymysql.connect(
#     host="localhost",
#     user="root",
#     password="mysql",
#     database="ml",
#     cursorclass=pymysql.cursors.DictCursor,
#     autocommit=True
# )


import os
import pymysql

db = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT", 3306)),
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)


# ---------------- HOME ----------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    cur = db.cursor()
    cur.execute("""
        SELECT DISTINCT c.company_id, c.company_name
        FROM analysis a
        JOIN companies c ON a.company_id = c.company_id
        ORDER BY c.company_name
    """)
    examples = cur.fetchall()

    # get error once and delete it from session
    error = request.session.pop("error", None)

    return templates.TemplateResponse("home.html", {
        "request": request,
        "examples": examples,
        "error": error
    })


@app.get("/search")
def search(q: str, request: Request):
    cur = db.cursor()

    cur.execute("""
        SELECT company_id
        FROM companies
        WHERE company_id LIKE %s OR company_name LIKE %s
        LIMIT 1
    """, (f"%{q}%", f"%{q}%"))

    row = cur.fetchone()

    if not row:
        # store error in session
        request.session["error"] = f"No company found for '{q}'"
        return RedirectResponse("/", status_code=302)

    return RedirectResponse(f"/company/{row['company_id']}", status_code=302)




# ---------------- COMPANY LIST ----------------
@app.get("/companies", response_class=HTMLResponse)
def companies(request: Request):
    cur = db.cursor()
    cur.execute("SELECT company_id, company_name, company_logo FROM companies ORDER BY company_name")
    companies = cur.fetchall()
    return templates.TemplateResponse("list.html", {
        "request": request,
        "companies": companies
    })

# ---------------- COMPANY PAGE ----------------
@app.get("/company/{cid}", response_class=HTMLResponse)
def company(cid: str, request: Request):
    cur = db.cursor()

    cur.execute("SELECT * FROM companies WHERE company_id=%s", (cid,))
    company = cur.fetchone()

    if not company:
        return HTMLResponse("Company not found", status_code=404)

    cur.execute("SELECT * FROM analysis WHERE company_id=%s", (cid,))
    analysis = cur.fetchall()

    cur.execute("SELECT pros FROM prosandcons WHERE company_id=%s AND pros IS NOT NULL", (cid,))
    pros = cur.fetchall()

    cur.execute("SELECT cons FROM prosandcons WHERE company_id=%s AND cons IS NOT NULL", (cid,))
    cons = cur.fetchall()

    cur.execute("SELECT * FROM balancesheet WHERE company_id=%s", (cid,))
    balancesheet = cur.fetchall()

    cur.execute("SELECT * FROM profitandloss WHERE company_id=%s", (cid,))
    profitandloss = cur.fetchall()

    cur.execute("SELECT * FROM cashflow WHERE company_id=%s", (cid,))
    cashflow = cur.fetchall()

    cur.execute("SELECT * FROM documents WHERE company_id=%s ORDER BY year DESC", (cid,))
    documents = cur.fetchall()

    return templates.TemplateResponse("company.html", {
        "request": request,
        "company": company,
        "analysis": analysis,
        "pros": pros,
        "cons": cons,
        "balancesheet": balancesheet,
        "profitandloss": profitandloss,
        "cashflow": cashflow,
        "documents": documents
    })
