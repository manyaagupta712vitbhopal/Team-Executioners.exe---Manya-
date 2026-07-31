import os

import fitz

from app.core.config import settings
from app.models.document import Document


os.makedirs(settings.EXTRACTED_TEXT_DIR, exist_ok=True)


def extract_pdf_text(file_path: str) -> str:
    """
    Extract raw text from a PDF file on disk. Shared by document uploads
    and planner attachments alike.
    """
    try:
        pdf = fitz.open(file_path)
    except Exception as exc:
        raise ValueError("Failed to open PDF. The file may be corrupted.") from exc

    try:
        full_text = ""

        for page in pdf:
            text = page.get_text().strip()
            if text:
                full_text += text + "\n"

        if not full_text.strip():
            full_text = "No extractable text found in this PDF."

    finally:
        pdf.close()

    return full_text


def extract_text(document: Document) -> str:
    """
    Extract text from a PDF document and save it as a text file.
    """
    full_text = extract_pdf_text(document.file_path)

    text_filename = f"{document.id}.txt"
    text_path = os.path.join(
        settings.EXTRACTED_TEXT_DIR,
        text_filename,
    )

    with open(
        text_path,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(full_text)

    return text_path


def load_text(document: Document) -> str:
    """
    Load extracted text for a document.
    """
    if not document.text_path or not os.path.exists(document.text_path):
        raise FileNotFoundError("Extracted text file not found.")

    with open(
        document.text_path,
        "r",
        encoding="utf-8",
    ) as file:
        return file.read()
