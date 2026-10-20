import pytest
from pydantic import ValidationError
from src.schema import Invoice


def test_valid_invoice():
    data = {
        "supplier_name": "Lanka Stationers (Pvt) Ltd",
        "invoice_number": "INV-2026-0042",
        "invoice_date": "2026-10-05",
        "line_items": [
            {"description": "A4 paper ream", "quantity": 10,
             "unit_price": 1500, "line_total": 15000}
        ],
        "subtotal": 15000,
        "vat_amount": 2700,
        "total_amount": 17700,
    }
    invoice = Invoice(**data)
    assert invoice.currency == "LKR"
    assert invoice.total_amount == 17700


def test_missing_fields_allowed():
    invoice = Invoice(supplier_name="Test Supplier")
    assert invoice.total_amount is None


def test_bad_date_rejected():
    with pytest.raises(ValidationError):
        Invoice(invoice_date="not-a-date")
