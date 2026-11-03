import sys

from src.pdf_reader import extract_text

file_name = sys.argv[1] if len(sys.argv) > 1 else "invoice_001.pdf"
text = extract_text(f"data/sample_invoices/{file_name}")
print(text)
