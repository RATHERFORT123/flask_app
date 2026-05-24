import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import re
from datetime import datetime, timedelta

# ================== PATH CONFIG ==================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
EXCEL_DIR = os.path.join(BASE_DIR, "data", "gem_excels")
os.makedirs(EXCEL_DIR, exist_ok=True)

# ================== CONSTANTS ==================
MAX_PAGES = 1000000000

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://gem.in",
    "Referer": "https://gem.in/view-contracts",
}

URL = "https://gem.gov.in/view_contracts/contract_details"

COLUMNS = [
    "Contract ID", "Status", "Organization Type", "Ministry", "Department",
    "Organization Name", "Office Zone", "Location", "Buyer Designation",
    "Buying Mode", "Bid Number", "Contract Date", "Total",
    "Service", "Category Name", "Product", "Brand", "Model", "HSN Code",
    "Ordered Quantity", "Price"
]

# ================== EXCEL SAFE CLEANER ==================
ILLEGAL_EXCEL_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")

def clean_excel_text(value):
    if isinstance(value, str):
        return ILLEGAL_EXCEL_RE.sub("", value)
    return value

# ================== NETWORK ==================
def robust_post(session, url, data, headers, max_retries=3):
    for attempt in range(max_retries):
        try:
            r = session.post(url, data=data, headers=headers, timeout=50)
            if r.status_code == 200:
                return r
            if 500 <= r.status_code < 600:
                time.sleep(2 ** attempt)
            else:
                r.raise_for_status()
        except requests.RequestException:
            time.sleep(2 ** attempt)
    raise Exception("Maximum retries exceeded")

# ================== PARSING HELPERS ==================
def safe_text(el):
    return el.get_text(strip=True) if el else ""

def extract_field_by_label(block, label):
    for p in block.find_all("p"):
        txt = p.get_text(" ", strip=True).lower()
        if label.lower() in txt:
            span = p.find("span")
            return span.get_text(strip=True) if span else txt.replace(label.lower(), "").replace(":", "").strip()
    return ""

def extract_bid_number(block):
    for p in block.find_all("p"):
        txt = p.get_text(" ", strip=True).lower()
        if "bid number" in txt:
            a = p.find("a")
            return a.get_text(strip=True) if a else txt.replace("bid number", "").replace(":", "").strip()
    return ""

def parse_items(table):
    rows = []
    headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
    idx = {h: i for i, h in enumerate(headers)}

    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")

        def get(key, cls=None):
            i = idx.get(key)
            if i is None or i >= len(tds):
                return ""
            if cls:
                el = tds[i].find(class_=cls)
                return el.get_text(strip=True) if el else tds[i].get_text(strip=True)
            return tds[i].get_text(strip=True)

        rows.append({
            "Service": get("service", "ajxtag_item_title"),
            "Category Name": get("category name", "ajxtag_item_title"),
            "Product": get("product", "ajxtag_item_title"),
            "Brand": get("brand", "ajxtag_item_title"),
            "Model": get("model", "ajxtag_item_title"),
            "HSN Code": get("hsn code"),
            "Ordered Quantity": get("ordered quantity", "ajxtag_quantity"),
            "Price": get("price", "ajxtag_totalvalue"),
        })
    return rows

def parse_contract(block):
    common = {
        "Contract ID": safe_text(block.select_one("span.ajxtag_order_number")),
        "Status": safe_text(block.select_one("span.ajxtag_order_status")),
        "Organization Type": extract_field_by_label(block, "Organization Type"),
        "Ministry": extract_field_by_label(block, "Ministry"),
        "Department": extract_field_by_label(block, "Department"),
        "Organization Name": extract_field_by_label(block, "Organization Name"),
        "Office Zone": extract_field_by_label(block, "Office Zone"),
        "Location": extract_field_by_label(block, "Location"),
        "Buyer Designation": extract_field_by_label(block, "Buyer Designation"),
        "Buying Mode": extract_field_by_label(block, "Buying Mode"),
        "Bid Number": extract_bid_number(block),
        "Contract Date": safe_text(block.select_one("span.ajxtag_contract_date")),
        "Total": safe_text(block.select_one("span.ajxtag_totalvalue")),
    }

    rows = []
    tables = block.select("table.table-striped")

    if tables:
        for table in tables:
            for item in parse_items(table):
                rows.append({**common, **item})
    else:
        rows.append({**common,
            "Service": "", "Category Name": "", "Product": "",
            "Brand": "", "Model": "", "HSN Code": "",
            "Ordered Quantity": "", "Price": ""
        })
    return rows

# ================== MAIN SERVICE FUNCTION ==================
def run_gem_scraper(start_date, category=""):
    session = requests.Session()
    current_date = datetime.strptime(start_date, "%d-%m-%Y")

    while True:
        date_str = current_date.strftime("%d-%m-%Y")
        output_file = os.path.join(EXCEL_DIR, f"{date_str}.xlsx")

        empty_pages = 0
        print(f"🔍 Scraping date: {date_str}")

        for page in range(MAX_PAGES):
            payload = {
                "fromDate": date_str,
                "toDate": date_str,
                "department": "",
                "bno": "",
                "buyer_category": category,
                "page": str(page),
            }

            try:
                response = robust_post(session, URL, payload, HEADERS)
            except Exception as e:
                print(f"❌ Page {page} failed: {e}")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            blocks = soup.select("div.border.block")

            if not blocks:
                empty_pages += 1
                if empty_pages >= 2:
                    break
                continue

            empty_pages = 0
            rows = []
            for block in blocks:
                rows.extend(parse_contract(block))

            df_page = pd.DataFrame(rows, columns=COLUMNS)
            df_page = df_page.map(clean_excel_text)

            if os.path.exists(output_file):
                df_existing = pd.read_excel(output_file, engine="openpyxl")
                combined = pd.concat([df_existing, df_page], ignore_index=True)
            else:
                combined = df_page

            combined.drop_duplicates(
                subset=["Contract ID", "Service", "Category Name", "Product"],
                inplace=True
            )

            combined.to_excel(output_file, index=False, engine="openpyxl")
            print(f"✅ Page {page} saved | Total rows: {len(combined)}")

        current_date += timedelta(days=1)

    return {
        "status": "completed",
        "excel_folder": EXCEL_DIR
    }
