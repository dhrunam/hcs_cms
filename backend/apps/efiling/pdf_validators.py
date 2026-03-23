"""
PDF upload validation: file size and OCR (extractable text) checks.
"""
import io

from django.conf import settings
from pypdf import PdfReader
from rest_framework.exceptions import ValidationError

MAX_PDF_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
MIN_OCR_TEXT_LENGTH = 20  # Minimum extractable chars from first page to consider OCR'd


def _is_validation_enabled() -> bool:
    return getattr(settings, "EFILING_VALIDATE_PDF_UPLOAD", True)


def validate_pdf_file(uploaded_file, field_name: str = "file") -> None:
    """
    Validate an uploaded PDF file:
    1. Size must be less than 25 MB
    2. PDF must have extractable text (OCR-converted / searchable)

    Raises ValidationError if invalid.
    """
    if not uploaded_file:
        return
    if not _is_validation_enabled():
        return

    # 1. Size check
    size = getattr(uploaded_file, "size", None)
    if size is not None and size > MAX_PDF_SIZE_BYTES:
        raise ValidationError(
            {
                field_name: f"PDF file size must be less than 25 MB. Current size: {size / (1024 * 1024):.1f} MB."
            }
        )

    # 2. OCR check - must have extractable text
    try:
        content = uploaded_file.read()
        uploaded_file.seek(0)  # Reset for later use
    except (AttributeError, IOError) as e:
        raise ValidationError({field_name: f"Could not read file: {e}"}) from e

    if not content or len(content) < 100:
        raise ValidationError({field_name: "File is not a valid PDF or is too small."})

    try:
        reader = PdfReader(io.BytesIO(content))
        if len(reader.pages) == 0:
            raise ValidationError({field_name: "PDF has no pages."})

        # Extract text from first page
        first_page = reader.pages[0]
        text = first_page.extract_text() or ""
        # Count non-whitespace characters
        text_chars = "".join(c for c in text if not c.isspace())

        if len(text_chars) < MIN_OCR_TEXT_LENGTH:
            raise ValidationError(
                {
                    field_name: "PDF must be OCR-converted (searchable). This file appears to be a scanned image without text layer. Please use OCR software to make the PDF searchable before uploading."
                }
            )
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(
            {field_name: f"Invalid or corrupted PDF. Please ensure the file is a valid, OCR-converted PDF. ({e})"}
        ) from e
