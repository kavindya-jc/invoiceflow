from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    line_total: Optional[float] = None


class Invoice(BaseModel):
    supplier_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    currency: str = "LKR"
    line_items: list[LineItem] = Field(default_factory=list)
    subtotal: Optional[float] = None
    vat_amount: Optional[float] = None
    total_amount: Optional[float] = None
