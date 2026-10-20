import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

random.seed(42)  # same invoices every run

OUT_DIR = Path("data/sample_invoices")
OUT_DIR.mkdir(parents=True, exist_ok=True)

VAT_RATE = 0.18
PCT = int(VAT_RATE * 100)

# (name, address, invoice-number prefix) - all fictional
SUPPLIERS = [
    ("Lanka Stationers (Pvt) Ltd", "No. 45, Main Street, Kurunegala", "INV-2026"),
    ("Ceylon Fresh Foods", "12, Temple Road, Negombo", "CF"),
    ("Island Hardware & Tools", "88, Galle Road, Colombo 03", "IHT/26"),
    ("Green Valley Packaging", "5, Industrial Zone, Kandy", "GVP"),
    ("Serendib Office Solutions", "21, Station Road, Kurunegala", "SOS-26"),
    ("Royal Cleaning Supplies", "No. 9, Lake Drive, Matara", "RCS"),
    ("Lanka Tech Traders", "150, High Level Road, Nugegoda", "LTT-2026"),
    ("Coconut Grove Catering", "33, Beach Road, Negombo", "CGC"),
]

# (description, unit price in LKR)
ITEMS = [
    ("A4 paper ream", 1500), ("Ballpoint pens (box)", 650),
    ("Printer toner cartridge", 18500), ("Stapler", 1200),
    ("Cleaning liquid 5L", 2400), ("Hand soap 500ml", 480),
    ("Packing tape roll", 350), ("Cardboard boxes (bundle)", 4200),
    ("LED bulb 12W", 520), ("Extension cord 5m", 2100),
    ("Whiteboard markers (pack)", 900), ("File folders (pack)", 1100),
    ("Bottled water 500ml (case)", 1800), ("Rice 25kg bag", 9500),
]

DEFECTS = [
    "wrong_total", "wrong_total", "line_mismatch", "line_mismatch",
    "missing_invoice_number", "missing_supplier", "invalid_date",
    "duplicate_number",
]


def money(x):
    return f"{x:,.2f}"


def dtext(r, fmt):
    return r["printed_date"] or r["date"].strftime(fmt)


def make_record(used_numbers):
    name, address, prefix = random.choice(SUPPLIERS)
    while True:
        number = f"{prefix}-{random.randint(1000, 9999)}"
        if number not in used_numbers:
            used_numbers.add(number)
            break
    items = []
    for desc, price in random.sample(ITEMS, random.randint(2, 5)):
        qty = random.randint(1, 20)
        items.append({"description": desc, "quantity": qty,
                      "unit_price": price, "line_total": qty * price})
    subtotal = sum(i["line_total"] for i in items)
    vat = round(subtotal * VAT_RATE, 2)
    return {
        "supplier_name": name, "address": address, "invoice_number": number,
        "date": date(2026, 1, 1) + timedelta(days=random.randint(0, 287)),
        "printed_date": None, "items": items, "subtotal": subtotal,
        "vat": vat, "total": round(subtotal + vat, 2), "defect": "",
    }


# ---------- 4 layouts ----------

def layout_a(c, r):
    y = A4[1] - 60
    c.setFont("Helvetica-Bold", 16)
    if r["supplier_name"]:
        c.drawString(50, y, r["supplier_name"])
    c.setFont("Helvetica", 10)
    c.drawString(50, y - 16, r["address"])
    y -= 55
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "INVOICE")
    c.setFont("Helvetica", 10)
    y -= 20
    if r["invoice_number"]:
        c.drawString(50, y, f"Invoice No: {r['invoice_number']}")
        y -= 14
    c.drawString(50, y, f"Date: {dtext(r, '%Y-%m-%d')}")
    y -= 30
    c.setFont("Helvetica-Bold", 10)
    for x, t in [(50, "Description"), (300, "Qty"), (370, "Unit Price"), (480, "Amount")]:
        c.drawString(x, y, t)
    c.line(50, y - 4, 545, y - 4)
    c.setFont("Helvetica", 10)
    y -= 20
    for it in r["items"]:
        c.drawString(50, y, it["description"])
        c.drawString(300, y, str(it["quantity"]))
        c.drawRightString(440, y, money(it["unit_price"]))
        c.drawRightString(545, y, money(it["line_total"]))
        y -= 16
    y -= 10
    for label, val in [("Subtotal", r["subtotal"]), (f"VAT ({PCT}%)", r["vat"]),
                       ("Total (LKR)", r["total"])]:
        c.drawString(370, y, label)
        c.drawRightString(545, y, money(val))
        y -= 16


def layout_b(c, r):
    y = A4[1] - 60
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, y, "TAX INVOICE")
    c.setFont("Helvetica", 10)
    if r["supplier_name"]:
        c.drawRightString(545, y, r["supplier_name"])
    c.drawRightString(545, y - 14, r["address"])
    y -= 50
    if r["invoice_number"]:
        c.drawString(50, y, f"Invoice #: {r['invoice_number']}")
        y -= 14
    c.drawString(50, y, f"Date of issue: {dtext(r, '%d %b %Y')}")
    y -= 35
    for it in r["items"]:
        c.drawString(
            50, y, f"{it['quantity']} x {it['description']} @ {money(it['unit_price'])}")
        c.drawRightString(545, y, money(it["line_total"]))
        y -= 16
    y -= 15
    for label, val in [("Sub Total", r["subtotal"]), (f"VAT {PCT}%", r["vat"]),
                       ("Grand Total", r["total"])]:
        c.drawRightString(440, y, label)
        c.drawRightString(545, y, money(val))
        y -= 16


def layout_c(c, r):
    y = A4[1] - 60
    mid = 297
    c.setFont("Helvetica-Bold", 13)
    if r["supplier_name"]:
        c.drawCentredString(mid, y, r["supplier_name"])
        y -= 16
    c.setFont("Helvetica", 9)
    c.drawCentredString(mid, y, r["address"])
    y -= 24
    if r["invoice_number"]:
        c.drawCentredString(mid, y, f"Bill No. {r['invoice_number']}")
        y -= 14
    c.drawCentredString(mid, y, dtext(r, "%d/%m/%Y"))
    y -= 24
    for it in r["items"]:
        c.drawString(180, y, it["description"])
        y -= 12
        c.drawString(190, y, f"{it['quantity']} x {money(it['unit_price'])}")
        c.drawRightString(415, y, money(it["line_total"]))
        y -= 18
    c.line(180, y, 415, y)
    y -= 16
    c.drawString(180, y, "Subtotal")
    c.drawRightString(415, y, money(r["subtotal"]))
    y -= 14
    c.drawString(180, y, f"VAT {PCT}%")
    c.drawRightString(415, y, money(r["vat"]))
    y -= 18
    c.setFont("Helvetica-Bold", 11)
    c.drawString(180, y, "TOTAL DUE (LKR)")
    c.drawRightString(415, y, money(r["total"]))


def layout_d(c, r):
    y = A4[1] - 60
    c.rect(50, y - 30, 250, 50)
    c.setFont("Helvetica-Bold", 12)
    if r["supplier_name"]:
        c.drawString(58, y, r["supplier_name"])
    c.setFont("Helvetica", 9)
    c.drawString(58, y - 16, r["address"])
    c.setFont("Helvetica-Bold", 11)
    c.drawString(350, y, "SALES INVOICE")
    c.setFont("Helvetica", 10)
    if r["invoice_number"]:
        c.drawString(350, y - 16, f"Ref No: {r['invoice_number']}")
    c.drawString(350, y - 30, f"Dated: {dtext(r, '%B %d, %Y')}")
    y -= 85
    c.setFont("Helvetica-Bold", 10)
    for x, t in [(50, "Qty"), (100, "Item"), (390, "Rate"), (480, "Value")]:
        c.drawString(x, y, t)
    c.line(50, y - 4, 545, y - 4)
    c.setFont("Helvetica", 10)
    y -= 20
    for it in r["items"]:
        c.drawString(50, y, str(it["quantity"]))
        c.drawString(100, y, it["description"])
        c.drawRightString(450, y, f"Rs. {money(it['unit_price'])}")
        c.drawRightString(545, y, f"Rs. {money(it['line_total'])}")
        y -= 16
    y -= 10
    for label, val in [("Sub-total", r["subtotal"]), (f"VAT @ {PCT}%", r["vat"]),
                       ("Net Payable", r["total"])]:
        c.drawString(370, y, label)
        c.drawRightString(545, y, f"Rs. {money(val)}")
        y -= 16


LAYOUTS = [layout_a, layout_b, layout_c, layout_d]


def main():
    used = set()
    records = [make_record(used) for _ in range(36)]

    for defect in DEFECTS:
        r = make_record(used)
        r["defect"] = defect
        if defect == "wrong_total":
            r["total"] = round(
                r["total"] + random.choice([500, 1000, 2500]), 2)
        elif defect == "line_mismatch":
            r["items"][0]["line_total"] += 1000
        elif defect == "missing_invoice_number":
            r["invoice_number"] = None
        elif defect == "missing_supplier":
            r["supplier_name"] = None
        elif defect == "invalid_date":
            r["printed_date"] = "31/02/2026"
        elif defect == "duplicate_number":
            first = records[0]
            r["supplier_name"] = first["supplier_name"]
            r["address"] = first["address"]
            r["invoice_number"] = first["invoice_number"]
        records.append(r)

    rows, items_truth = [], {}
    for n, r in enumerate(records, start=1):
        fn = LAYOUTS[n % 4]
        file_name = f"invoice_{n:03d}.pdf"
        c = canvas.Canvas(str(OUT_DIR / file_name), pagesize=A4)
        fn(c, r)
        c.showPage()
        c.save()

        rows.append({
            "file_name": file_name,
            "layout": fn.__name__[-1].upper(),
            "supplier_name": r["supplier_name"] or "",
            "invoice_number": r["invoice_number"] or "",
            "invoice_date": "" if r["printed_date"] else r["date"].isoformat(),
            "subtotal": r["subtotal"],
            "vat_amount": r["vat"],
            "total_amount": r["total"],
            "num_items": len(r["items"]),
            "expected_flag": bool(r["defect"]),
            "defect": r["defect"],
        })
        items_truth[file_name] = r["items"]

    with open("data/ground_truth.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    with open("data/ground_truth_items.json", "w", encoding="utf-8") as f:
        json.dump(items_truth, f, indent=2)

    print(f"Created {len(records)} invoices in {OUT_DIR}")


if __name__ == "__main__":
    main()
