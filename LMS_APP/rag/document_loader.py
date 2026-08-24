from pathlib import Path
from pypdf import PdfReader

def extract_text_from_pdf(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    reader = PdfReader(str(file_path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        text = text.strip()

        if text:
            pages.append({
                "text": text,
                "page": page_number,
                "source": file_path.name
            })

    return pages