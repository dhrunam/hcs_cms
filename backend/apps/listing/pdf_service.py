from __future__ import annotations

import io
from dataclasses import dataclass
from datetime import date as date_type
from typing import Iterable, List, Optional, Sequence

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import os
import html
from typing import List, Dict, Any, Optional, Union, Tuple


@dataclass(frozen=True)
class CauseListRow:
    serial_no: int
    case_number: str
    ia_info: str
    main_parties: str
    petitioner_advocates: str
    respondent_advocates: str


BENCH_DISPLAY_LABELS: dict[str, str] = {
    "CJ": "HON'BLE THE CHIEF JUSTICE",
    "Judge1": "HON'BLE JUDGE - I",
    "Judge2": "HON'BLE JUDGE - II",
    "CJ+Judge1": "DIVISION BENCH -I",
    "CJ+Judge2": "DIVISION BENCH -II",
    "Judge1+Judge2": "DIVISION BENCH -III",
    "CJ+Judge1+Judge2": "FULL BENCH",
}


@dataclass(frozen=True)
class BenchPdfConfig:
    bench_label: str
    before_lines: Sequence[str]
    court_no: str = "2"
    sitting_time: str = "Time 10:30 A. M. to 01:00 P. M. and 02:00 P. M. to 04:00 P. M"
    at_time: str = "(At 10:30 A.M.)"
    vc_url: Optional[str] = None


BENCH_PDF_CONFIG: dict[str, BenchPdfConfig] = {
    "CJ": BenchPdfConfig(
        bench_label=BENCH_DISPLAY_LABELS["CJ"],
        before_lines=("Hon'ble Mr. Justice A. Muhamed Mustaque, Chief Justice",),
        court_no="1",
    ),
    "Judge1": BenchPdfConfig(
        bench_label=BENCH_DISPLAY_LABELS["Judge1"],
        before_lines=("Hon'ble Mrs. Justice Meenakshi Madan Rai, Judge",),
        court_no="2",
    ),
    "Judge2": BenchPdfConfig(
        bench_label=BENCH_DISPLAY_LABELS["Judge2"],
        before_lines=("Hon'ble Mr. Justice Bhaskar Raj Pradhan, Judge",),
        court_no="3",
    ),
    "CJ+Judge1": BenchPdfConfig(
        bench_label=BENCH_DISPLAY_LABELS["CJ+Judge1"],
        before_lines=(
            "Hon'ble Mr. Justice A. Muhamed Mustaque, Chief Justice",
            "Hon'ble Mrs. Justice Meenakshi Madan Rai, Judge",
        ),
        court_no="1",
    ),
    "CJ+Judge2": BenchPdfConfig(
        bench_label=BENCH_DISPLAY_LABELS["CJ+Judge2"],
        before_lines=(
            "Hon'ble Mr. Justice A. Muhamed Mustaque, Chief Justice",
            "Hon'ble Mr. Justice Bhaskar Raj Pradhan, Judge",
        ),
        court_no="1",
    ),
    "Judge1+Judge2": BenchPdfConfig(
        bench_label=BENCH_DISPLAY_LABELS["Judge1+Judge2"],
        before_lines=(
            "Hon'ble Mrs. Justice Meenakshi Madan Rai, Judge",
            "Hon'ble Mr. Justice Bhaskar Raj Pradhan, Judge",
        ),
        court_no="2",
    ),
    "CJ+Judge1+Judge2": BenchPdfConfig(
        bench_label=BENCH_DISPLAY_LABELS["CJ+Judge1+Judge2"],
        before_lines=(
            "Hon'ble Mr. Justice A. Muhamed Mustaque, Chief Justice",
            "Hon'ble Mrs. Justice Meenakshi Madan Rai, Judge",
            "Hon'ble Mr. Justice Bhaskar Raj Pradhan, Judge",
        ),
        court_no="1",
    ),
}


def _ordinal_suffix(day: int) -> str:
    if 11 <= (day % 100) <= 13:
        return "TH"
    last = day % 10
    if last == 1:
        return "ST"
    if last == 2:
        return "ND"
    if last == 3:
        return "RD"
    return "TH"


def _format_cause_list_date(d: date_type) -> str:
    weekday = d.strftime("%A").upper()
    month = d.strftime("%B").upper()
    return f"[FOR {weekday}, THE {d.day} {_ordinal_suffix(d.day)} DAY OF {month}, {d.year}]"


class _NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        super().showPage()

    def save(self):
        page_count = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page_number(page_count)
            super().showPage()
        super().save()

    def _draw_page_number(self, page_count: int) -> None:
        page = self._pageNumber
        w, h = letter
        self.setFont("Times-Roman", 10)
        self.drawString(0.75 * inch, h - 0.5 * inch, f"Page {page} of {page_count}")
        self.drawCentredString(w / 2, 0.55 * inch, f"-- {page} of {page_count} --")


def _logo_path() -> Optional[str]:
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(here, "assets", "sikkim_high_court_logo.png")
    return p if os.path.exists(p) else None


def generate_cause_list_pdf_bytes(
    *,
    cause_list_date,
    bench_key: str,
    rows: Iterable[CauseListRow],
) -> bytes:
    buf = io.BytesIO()
    cfg = BENCH_PDF_CONFIG.get(
        bench_key,
        BenchPdfConfig(bench_label=bench_key, before_lines=(bench_key,)),
    )

    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
        title="Daily Cause List",
    )

    styles = getSampleStyleSheet()
    header_center = ParagraphStyle(
        "header_center",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=12,
        leading=14,
        alignment=1,
    )
    header_center_bold = ParagraphStyle(
        "header_center_bold",
        parent=header_center,
        fontName="Times-Bold",
        fontSize=14,
        leading=16,
    )
    small_center = ParagraphStyle(
        "small_center",
        parent=header_center,
        fontSize=11,
        leading=13,
    )
    cell_style = ParagraphStyle(
        "cell",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=10,
        leading=12,
    )
    cell_style_bold = ParagraphStyle(
        "cell_bold",
        parent=cell_style,
        fontName="Times-Bold",
    )

    story: List = []

    # Logo (centered, like typical court causelists)
    logo = _logo_path()
    if logo:
        try:
            img = Image(logo)
            img.drawHeight = 0.85 * inch
            img.drawWidth = 0.85 * inch
            img.hAlign = "CENTER"
            story.append(img)
            story.append(Spacer(1, 6))
        except Exception:
            pass

    story.append(Paragraph("THE HIGH COURT OF SIKKIM", header_center_bold))
    story.append(Paragraph("GANGTOK", header_center_bold))
    story.append(Paragraph("DAILY CAUSELIST", header_center_bold))
    story.append(Paragraph(_format_cause_list_date(cause_list_date), small_center))
    story.append(
        Paragraph(
            "[ALL URGENT MATTERS MUST BE MENTIONED AT 10:30 A.M<br/>BEFORE HON'BLE THE CHIEF JUSTICE]",
            small_center,
        )
    )
    story.append(Paragraph(cfg.sitting_time, small_center))
    story.append(Spacer(1, 10))
    story.append(Paragraph(cfg.bench_label, header_center_bold))
    story.append(Spacer(1, 6))
    story.append(Paragraph("BEFORE", header_center_bold))
    for line in cfg.before_lines:
        story.append(Paragraph(str(line), header_center))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"COURT NO - {cfg.court_no}", header_center_bold))
    story.append(Paragraph(cfg.at_time, header_center))
    story.append(Spacer(1, 10))

    header_row = [
        Paragraph("Sr. No.", cell_style_bold),
        Paragraph("Case Number", cell_style_bold),
        Paragraph("Main Parties", cell_style_bold),
        Paragraph("Petitioner Advocate", cell_style_bold),
        Paragraph("Respondent Advocate", cell_style_bold),
    ]

    data = [header_row]
    def _ea(s: str) -> str:
        """Escape and Format: handle XML escaping then replace newlines with <br/>."""
        if not s:
            return "-"
        return html.escape(s).replace("\n", "<br/>")

    for r in list(rows):
        case_no_esc = html.escape(r.case_number or "-")
        case_cell_content = f"<b>{case_no_esc}</b>"
        if r.ia_info:
            formatted_ia = _ea(r.ia_info)
            case_cell_content += f"<br/>{formatted_ia}"

        data.append(
            [
                Paragraph(f"{r.serial_no})", cell_style),
                Paragraph(case_cell_content, cell_style),
                Paragraph(_ea(r.main_parties), cell_style),
                Paragraph(_ea(r.petitioner_advocates), cell_style),
                Paragraph(_ea(r.respondent_advocates), cell_style),
            ]
        )

    col_widths = [0.5 * inch, 1.0 * inch, 2.0 * inch, 1.75 * inch, 1.75 * inch]
    table = Table(data, colWidths=col_widths, hAlign="LEFT", repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), "Times-Roman", 10),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, 0), 0.75, colors.black),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 10))
    #story.append(Paragraph("VC / Hybrid Hearing Link", header_center))

    def _on_page(canv: canvas.Canvas, _doc):
        # Top-right VC hyperlink (placeholder until vc_url is provided)
        label = "VC / Hybrid Hearing Link"
        url = cfg.vc_url or "www.youtube.com"
        canv.setFont("Times-Roman", 10)
        w, h = letter
        x = w - doc.rightMargin
        y = h - 0.55 * inch
        canv.setFillColor(colors.blue)
        canv.drawRightString(x, y, label)
        canv.setFillColor(colors.black)
        if url:
            text_w = canv.stringWidth(label, "Times-Roman", 10)
            canv.linkURL(url, (x - text_w, y - 2, x, y + 10), relative=0)

    doc.build(story, canvasmaker=_NumberedCanvas, onFirstPage=_on_page, onLaterPages=_on_page)
    buf.seek(0)
    return buf.read()

