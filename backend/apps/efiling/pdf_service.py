"""
Merge multiple PDFs, prepend an index page with hyperlinks, and bookmarks.
Index page is created as text-only; link annotations are added with pypdf
after merge so destinations are valid (ReportLab would require bookmarkPage
for linkAbsolute, which we can't satisfy before merge).
"""
import io
import os
from typing import List, Optional, Tuple

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link

# Index page layout (must match _create_index_page_pdf and _index_row_rect_pdf_coords)
_PAGE_WIDTH, _PAGE_HEIGHT = letter
_MARGIN_X = 72
_MARGIN_TOP = 72
_INDEX_LEFT, _INDEX_RIGHT = _MARGIN_X, _PAGE_WIDTH - _MARGIN_X
_TITLE_Y = _PAGE_HEIGHT - _MARGIN_TOP
_TABLE_TOP_Y = _TITLE_Y - 40
_ROW_H = 22

_COL_NO_W = 48
_COL_PAGE_W = 72
_COL_NAME_W = (_INDEX_RIGHT - _INDEX_LEFT) - _COL_NO_W - _COL_PAGE_W


def _create_front_page_pdf(
    petitioner_name: str,
    respondent_name: str,
    case_no: str,
    case_type: str = "",
) -> bytes:
    """Create a single-page front/cover PDF in the court-style layout."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    left, right = _MARGIN_X, width - _MARGIN_X

    petitioner_name = (petitioner_name or "").strip()
    respondent_name = (respondent_name or "").strip()
    case_no = (case_no or "").strip()
    case_type = (case_type or "").strip()

    # Header (centered, serif, bold-ish)
    y = height - 90
    c.setFont("Times-Bold", 14)
    c.drawCentredString(width / 2.0, y, "IN THE HIGH COURT OF SIKKIM AT GANGTOK")
    y -= 22
    c.setFont("Times-Bold", 13)
    jurisdiction_line = f"({case_type})" if case_type else "(CIVIL EXTRAORDINARY JURISDICTION)"
    c.drawCentredString(width / 2.0, y, jurisdiction_line)
    y -= 28
    c.setFont("Times-Bold", 13)
    dotted = ".........." if not case_no else case_no
    c.drawCentredString(width / 2.0, y, f"{dotted}")

    # Matter of
    y -= 60
    c.setFont("Times-Bold", 13)
    c.drawString(left, y, "IN THE MATTER OF:")
    c.setLineWidth(1)
    c.line(left, y - 6, left + 160, y - 6)

    # Petitioner block
    y -= 55
    c.setFont("Times-Roman", 13)
    c.drawString(left, y, petitioner_name or "—")
    c.setFont("Times-Bold", 13)
    c.drawRightString(right, y, "..........PETITIONER")

    # Versus
    y -= 70
    c.setFont("Times-Bold", 14)
    c.drawCentredString(width / 2.0, y, "VERSUS")

    # Respondent block
    y -= 70
    c.setFont("Times-Roman", 13)
    c.drawString(left, y, respondent_name or "—")
    c.setFont("Times-Bold", 13)
    c.drawRightString(right, y, "..........RESPONDENT")

    c.save()
    buf.seek(0)
    return buf.read()


def _wrap_text(text: str, max_width: float, font_name: str, font_size: float) -> List[str]:
    """
    Wrap text into lines that fit max_width using the chosen font.
    Handles long tokens (e.g. underscores) by breaking them when needed.
    """
    s = (text or "").strip()
    if not s:
        return ["—"]

    # Prefer breaking on spaces; if no spaces, use underscores as soft breakpoints too.
    tokens: List[str]
    if " " in s:
        tokens = s.split(" ")
        joiner = " "
    elif "_" in s:
        tokens = s.split("_")
        joiner = "_"
    else:
        tokens = [s]
        joiner = ""

    lines: List[str] = []
    current = ""

    def w(t: str) -> float:
        return stringWidth(t, font_name, font_size)

    def flush() -> None:
        nonlocal current
        if current:
            lines.append(current)
            current = ""

    for tok in tokens:
        piece = tok if current == "" else current + joiner + tok
        if w(piece) <= max_width:
            current = piece
            continue

        # If we already have something on the line, flush it and retry token on new line.
        if current:
            flush()
            piece = tok
            if w(piece) <= max_width:
                current = piece
                continue

        # Token itself too long: hard-break by characters
        acc = ""
        for ch in tok:
            cand = acc + ch
            if w(cand) <= max_width or not acc:
                acc = cand
            else:
                lines.append(acc)
                acc = ch
        if acc:
            current = acc

    flush()
    return lines


def _create_index_pdf(
    document_names: List[str], page_numbers: List[int]
) -> Tuple[List[bytes], List[Tuple[int, Tuple[float, float, float, float]]]]:
    """
    Create one or more index pages as PDFs (table with wrapped Title).
    Returns (pdf_pages_bytes, link_rects) where link_rects entries are:
      (index_page_offset, rect) for each row, in the same order as document_names.
    """
    if len(document_names) != len(page_numbers):
        raise ValueError("document_names and page_numbers must be same length")

    header_font = "Helvetica-Bold"
    header_size = 12
    body_font = "Helvetica"
    body_size = 12
    line_h = 14  # for wrapped title lines

    x0, x3 = _INDEX_LEFT, _INDEX_RIGHT
    x1 = x0 + _COL_NO_W
    x2 = x3 - _COL_PAGE_W
    title_left = x1 + 6
    title_right = x2 - 6
    max_title_w = title_right - title_left

    # Page layout
    title_y = _TITLE_Y
    table_top = _TABLE_TOP_Y
    header_top = table_top
    header_bottom = header_top - _ROW_H
    bottom_margin = 72

    pdf_pages: List[bytes] = []
    link_rects: List[Tuple[int, Tuple[float, float, float, float]]] = []

    page_offset = -1
    c = None
    y = None
    table_bottom = None

    def start_page() -> None:
        nonlocal c, y, table_bottom, page_offset
        page_offset += 1
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        width, _height = letter
        # Title
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2.0, title_y, "Index")
        # Header text
        c.setFont(header_font, header_size)
        c.drawString(x0 + 6, header_bottom + 6, "No.")
        c.drawString(x1 + 6, header_bottom + 6, "Title")
        c.drawRightString(x3 - 6, header_bottom + 6, "Page")
        # Header lines (top & bottom)
        c.setLineWidth(1)
        c.line(x0, header_top, x3, header_top)
        c.line(x0, header_bottom, x3, header_bottom)
        c.setLineWidth(0.5)
        y = header_bottom
        table_bottom = header_bottom
        c._index_buf = buf  # type: ignore[attr-defined]

    def end_page() -> None:
        nonlocal c, table_bottom
        assert c is not None
        c.setLineWidth(0.5)
        c.line(x1, header_top, x1, table_bottom)
        c.line(x2, header_top, x2, table_bottom)
        c.line(x0, header_top, x0, table_bottom)
        c.line(x3, header_top, x3, table_bottom)
        c.save()
        buf = c._index_buf  # type: ignore[attr-defined]
        buf.seek(0)
        pdf_pages.append(buf.read())
        c = None

    start_page()

    for i, (name, page_no) in enumerate(zip(document_names, page_numbers)):
        assert c is not None and y is not None
        title_lines = _wrap_text(str(name), max_title_w, body_font, body_size)
        row_h = max(_ROW_H, 6 + (len(title_lines) * line_h) + 6)
        next_bottom = y - row_h

        # Page break if needed
        if next_bottom < bottom_margin:
            end_page()
            start_page()
            assert c is not None and y is not None
            next_bottom = y - row_h

        row_top = y
        row_bottom = next_bottom

        # Draw row contents
        c.setFont(body_font, body_size)
        c.drawString(x0 + 6, row_top - 16, str(i + 1))
        c.drawRightString(x3 - 6, row_top - 16, str(page_no))

        text_y = row_top - 16
        for line in title_lines:
            c.drawString(title_left, text_y, line)
            text_y -= line_h

        c.line(x0, row_bottom, x3, row_bottom)
        link_rects.append((page_offset, (x1, row_bottom, x2, row_top)))

        y = row_bottom
        table_bottom = row_bottom

    end_page()
    return pdf_pages, link_rects


def merge_pdfs_with_index(
    files: List[Tuple[str, bytes]],
    output_buffer: io.BytesIO,
    document_names: Optional[List[str]] = None,
    front_page: Optional[dict] = None,
) -> None:
    """
    Merge PDFs into one, optionally with a front page, then index page, then documents.

    :param files: List of (filename, pdf_bytes)
    :param output_buffer: Where to write the merged PDF
    :param document_names: Optional list of display names for index/bookmarks (one per file, same order).
    :param front_page: Optional dict with keys petitioner_name, respondent_name, case_no (strings).
        If provided, a front page is inserted as page 0.
    """
    if not files:
        raise ValueError("At least one PDF is required")

    if document_names and len(document_names) == len(files):
        names = [n.strip() or f"Document {i+1}" for i, n in enumerate(document_names)]
    else:
        names = [os.path.splitext(os.path.basename(n))[0] or f"Document {i+1}" for i, (n, _) in enumerate(files)]

    writer = PdfWriter()
    doc_start_base: List[int] = []
    for _fname, content in files:
        doc_start_base.append(len(writer.pages))
        reader = PdfReader(io.BytesIO(content))
        # Ignore source PDF outlines/bookmarks; we add a fresh bookmark tree below.
        writer.append(reader, import_outline=False)

    use_front = True
    front_pages = 1
    index_pages = 1
    index_pdf_pages: List[bytes] = []
    index_link_rects: List[Tuple[int, Tuple[float, float, float, float]]] = []
    for _ in range(5):
        n_prefix = front_pages + index_pages
        doc_start_pages = [p + n_prefix for p in doc_start_base]
        page_numbers_display = [p + 1 for p in doc_start_pages]
        index_pdf_pages, index_link_rects = _create_index_pdf(names, page_numbers_display)
        if len(index_pdf_pages) == index_pages:
            break
        index_pages = len(index_pdf_pages)

    fp = front_page or {}
    front_page_pdf = _create_front_page_pdf(
        fp.get("petitioner_name") or "",
        fp.get("respondent_name") or "",
        fp.get("case_no") or "",
        fp.get("case_type") or "",
    )
    writer.insert_page(PdfReader(io.BytesIO(front_page_pdf)).pages[0], 0)

    index_at = 1
    for page_bytes in reversed(index_pdf_pages):
        idx_page = PdfReader(io.BytesIO(page_bytes)).pages[0]
        writer.insert_page(idx_page, index_at)

    writer.add_outline_item(title="Front Page", page_number=0)
    writer.add_outline_item(title="Index", page_number=index_at)
    for i, title in enumerate(names):
        writer.add_outline_item(title=title, page_number=doc_start_pages[i])

    for i, (page_offset, rect) in enumerate(index_link_rects):
        link = Link(rect=rect, target_page_index=doc_start_pages[i])
        writer.add_annotation(index_at + page_offset, link)

    writer.write(output_buffer)
    output_buffer.seek(0)
