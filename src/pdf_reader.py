from pathlib import Path

import pdfplumber


def extract_text(pdf_path) -> str:
    """Return all text from a PDF as one string."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")

    return "\n".join(pages).strip()
