import csv
from pathlib import Path

import pytest

from src.pdf_reader import extract_text

with open("data/ground_truth.csv", encoding="utf-8") as f:
    ROWS = list(csv.DictReader(f))


@pytest.mark.parametrize("row", ROWS, ids=[r["file_name"] for r in ROWS])
def test_text_contains_key_fields(row):
    text = extract_text(Path("data/sample_invoices") / row["file_name"])
    assert text, "no text extracted"

    if row["supplier_name"]:
        assert row["supplier_name"] in text
    if row["invoice_number"]:
        assert row["invoice_number"] in text
    assert f"{float(row['total_amount']):,.2f}" in text


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        extract_text("data/sample_invoices/does_not_exist.pdf")
