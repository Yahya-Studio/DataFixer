"""PDF Report Generator for DataFixer with full Unicode and Arabic font support."""

import contextlib
from pathlib import Path
from typing import Any

from fpdf import FPDF
from fpdf.enums import XPos, YPos


def _get_font_paths() -> tuple[Path | None, Path | None]:
    """Locate Unicode TrueType fonts supporting Arabic and English."""
    candidates_reg = [
        Path("assets/fonts/NotoSansArabic-Regular.ttf"),
        Path("/usr/share/fonts/noto/NotoSansArabic-Regular.ttf"),
        Path("/usr/share/fonts/noto/NotoNaskhArabic-Regular.ttf"),
    ]
    candidates_bold = [
        Path("assets/fonts/NotoSansArabic-Bold.ttf"),
        Path("/usr/share/fonts/noto/NotoSansArabic-Bold.ttf"),
        Path("/usr/share/fonts/noto/NotoNaskhArabic-Bold.ttf"),
    ]

    reg_path = next((p.resolve() for p in candidates_reg if p.exists()), None)
    bold_path = next((p.resolve() for p in candidates_bold if p.exists()), None)
    return reg_path, bold_path


class DataFixerPDF(FPDF):
    """Custom PDF document supporting Arabic shaping and clean SaaS styling."""

    def __init__(self, font_family: str = "NotoArabic"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.custom_font = font_family

    def header(self):
        self.set_font(self.custom_font, "B", 15)
        self.set_text_color(30, 27, 75)
        self.cell(0, 9, "DataFixer — تقرير جودة وتنظيف البيانات", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
        self.set_font(self.custom_font, "", 9)
        self.set_text_color(100, 116, 139)
        self.cell(
            0,
            6,
            "ملخص التدقيق الشامل للبيانات والعمليات المنفذة | Data Quality & Audit Report",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="R",
        )
        self.line(10, 26, 200, 26)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.custom_font, "", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f"صفحة {self.page_no()}/{{nb}} | تم الإنشاء بواسطة منصة DataFixer", align="C")


def generate_pdf_report(data: dict[str, Any]) -> bytes:
    """Generate professional PDF report bytes with full Arabic Unicode support."""
    reg_font, bold_font = _get_font_paths()

    pdf = DataFixerPDF(font_family="NotoArabic" if reg_font else "Helvetica")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Enable text shaping for Arabic glyphs if font is available
    if reg_font:
        with contextlib.suppress(Exception):
            pdf.set_text_shaping(True)
        pdf.add_font("NotoArabic", "", str(reg_font))
        if bold_font:
            pdf.add_font("NotoArabic", "B", str(bold_font))
        else:
            pdf.add_font("NotoArabic", "B", str(reg_font))
        font_name = "NotoArabic"
    else:
        font_name = "Helvetica"

    pdf.add_page()

    # Section 1: Dataset Overview
    pdf.set_font(font_name, "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "نظرة عامة على البيانات | Dataset Overview", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

    pdf.set_font(font_name, "", 9)
    pdf.set_text_color(51, 65, 85)

    # 2-column info layout
    pdf.cell(95, 6, f"اسم الملف: {data.get('filename', '-')}", new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
    pdf.cell(
        95,
        6,
        f"الصيغة والحجم: {data.get('file_type', '')} ({data.get('file_size', '')})",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
        align="R",
    )
    pdf.cell(95, 6, f"تاريخ التوليد: {data.get('generated_at', '-')}", new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
    pdf.cell(
        95, 6, f"معرف التقرير: {str(data.get('report_id', '-'))[:10]}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R"
    )
    pdf.ln(3)

    # Key Metrics Box
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(10, pdf.get_y(), 190, 22, "FD")

    pdf.set_y(pdf.get_y() + 2)
    pdf.set_font(font_name, "B", 10)

    score_orig = data.get("initial_score", 0.0)
    score_curr = data.get("final_score", 0.0)
    diff_score = data.get("score_improvement", 0.0)

    pdf.cell(47, 5, "الخلايا المعدلة", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(47, 5, "الصفوف (قبل -> بعد)", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(47, 5, "الجودة النهائية", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(47, 5, "الجودة الابتدائية", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font(font_name, "B", 10)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(47, 6, str(data.get("cells_modified", 0)), align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(
        47, 6, f"{data.get('rows_before')} -> {data.get('rows_after')}", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP
    )
    pdf.set_text_color(16, 185, 129)
    pdf.cell(47, 6, f"{score_curr:.1f} (+{diff_score:.1f})", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(47, 6, f"{score_orig:.1f} / 100", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)

    # Section 2: Detected Issues
    issues = data.get("detected_issues", [])
    pdf.set_font(font_name, "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, f"المشكلات المكتشفة ({len(issues)})", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

    pdf.set_font(font_name, "B", 8)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(60, 6, "التفاصيل / الإجراء", border=1, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
    pdf.cell(30, 6, "العدد والنسبة", border=1, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP, align="C")
    pdf.cell(40, 6, "العمود المتأثر", border=1, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
    pdf.cell(20, 6, "الخطورة", border=1, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP, align="C")
    pdf.cell(40, 6, "نوع المشكلة", border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

    pdf.set_font(font_name, "", 7)
    for issue in issues[:25]:  # limit to top 25 issues to keep PDF clean
        title = str(issue.title)[:35]
        sev = str(issue.severity).upper()
        col = (str(issue.affected_column) if issue.affected_column else "الجدول بالكامل")[:25]
        cnt = f"{issue.affected_count:,} ({issue.affected_ratio * 100:.1f}%)"
        rec = (str(issue.recommendation) if issue.recommendation else str(issue.description))[:45]

        pdf.cell(60, 5, rec, border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
        pdf.cell(30, 5, cnt, border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align="C")
        pdf.cell(40, 5, col, border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
        pdf.cell(20, 5, sev, border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align="C")
        pdf.cell(40, 5, title, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

    if not issues:
        pdf.cell(
            190,
            6,
            "لم يتم العثور على أي مشكلات جودة في البيانات.",
            border=1,
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

    pdf.ln(5)

    # Section 3: Cleaning Operations Log
    actions = data.get("actions_log", [])
    pdf.set_font(font_name, "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, f"سجل العمليات المنفذة ({len(actions)})", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

    pdf.set_font(font_name, "B", 8)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(30, 6, "الخلايا المعدلة", border=1, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP, align="C")
    pdf.cell(40, 6, "تأثير الصفوف", border=1, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP, align="C")
    pdf.cell(45, 6, "الأعمدة المستهدفة", border=1, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
    pdf.cell(50, 6, "العملية", border=1, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
    pdf.cell(25, 6, "الوقت", border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    pdf.set_font(font_name, "", 7)
    for act in actions:
        t_str = act.timestamp.strftime("%H:%M:%S") if hasattr(act.timestamp, "strftime") else str(act.timestamp)[:8]
        op_name = str(act.name)[:35]
        tgt = (", ".join(act.target_columns) if act.target_columns else "كل الجدول")[:28]
        r_trans = f"{act.rows_before} -> {act.rows_after}"
        c_mod = str(act.cells_modified)

        pdf.cell(30, 5, c_mod, border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align="C")
        pdf.cell(40, 5, r_trans, border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align="C")
        pdf.cell(45, 5, tgt, border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
        pdf.cell(50, 5, op_name, border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
        pdf.cell(25, 5, t_str, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    if not actions:
        pdf.cell(190, 6, "لم يتم تنفيذ أي عمليات تنظيف بعد.", border=1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    return bytes(pdf.output())
