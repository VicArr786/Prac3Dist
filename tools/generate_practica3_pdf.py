import re
from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Spacer,
    Paragraph,
    ListFlowable,
    ListItem,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)


ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "PRACTICA3.md"
OUT_PATH = ROOT / "PRACTICA3.pdf"


def md_inline_to_rl(text: str) -> str:
    # very small subset: **bold**, `code`
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r'<font face="Courier">\1</font>', text)
    return text


def build_story(md: str):
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=10,
        alignment=1,  # center
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=12.5,
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.HexColor("#111827"),
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=10.8,
        leading=14,
        textColor=colors.HexColor("#111827"),
    )
    small = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontSize=9.8,
        leading=12.5,
        textColor=colors.HexColor("#374151"),
    )

    story = []

    # Cover / header block (cleaner than plain paragraphs)
    story.append(Paragraph("PRÁCTICA 3: Sockets – GRUPAL", title))
    story.append(Spacer(1, 0.15 * cm))

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    header_data = [
        [Paragraph("<b>Asignatura:</b>", small), Paragraph("Programación de Sistemas Distribuidos", small)],
        [Paragraph("<b>Curso:</b>", small), Paragraph("2023/2024", small)],
        [Paragraph("<b>Fecha:</b>", small), Paragraph("12-04-2024", small)],
        [Paragraph("<b>Semestre:</b>", small), Paragraph("2º", small)],
        [Paragraph("<b>Generado:</b>", small), Paragraph(generated_at, small)],
    ]
    header_tbl = Table(header_data, colWidths=[3.2 * cm, 12.5 * cm])
    header_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F9FAFB")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#E5E7EB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(header_tbl)
    story.append(Spacer(1, 0.25 * cm))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#E5E7EB")))
    story.append(Spacer(1, 0.35 * cm))

    pending_list: list[tuple[int, str]] = []

    def flush_list():
        nonlocal pending_list
        if not pending_list:
            return
        items = []
        for indent_level, text in pending_list:
            base_indent = 16 + indent_level * 14
            items.append(
                ListItem(
                    Paragraph(md_inline_to_rl(text), body),
                    leftIndent=base_indent,
                    bulletFontName="Helvetica",
                )
            )
        story.append(ListFlowable(items, bulletType="bullet", leftIndent=0))
        story.append(Spacer(1, 0.2 * cm))
        pending_list = []

    skipped_first_heading = False
    for raw in md.splitlines():
        line = raw.rstrip()

        if not line.strip():
            flush_list()
            story.append(Spacer(1, 0.18 * cm))
            continue

        # Remove "Alumno" section lines from the markdown content
        if line.lstrip().startswith("**Alumno") or line.lstrip().startswith("Alumno(") or line.lstrip().startswith("Alumno:") or line.lstrip().startswith("Alumno(s):"):
            continue

        if line.strip() == "---":
            flush_list()
            story.append(Spacer(1, 0.25 * cm))
            continue

        if line.startswith("## "):
            flush_list()
            # The markdown file already starts with a "PRÁCTICA 3..." heading,
            # but we render a nicer title block above; skip the first one.
            if not skipped_first_heading and line.upper().startswith("## PR"):
                skipped_first_heading = True
                continue
            # keep heading with a small spacer after it to avoid orphaning
            story.append(KeepTogether([Paragraph(md_inline_to_rl(line[3:]), h2), Spacer(1, 0.05 * cm)]))
            continue

        m = re.match(r"^(\s*)-\s+(.*)$", line)
        if m:
            indent_spaces = len(m.group(1).replace("\t", "    "))
            indent_level = min(indent_spaces // 2, 4)
            pending_list.append((indent_level, m.group(2)))
            continue

        flush_list()
        story.append(Paragraph(md_inline_to_rl(line), body))

    flush_list()
    return story


def main():
    md = MD_PATH.read_text(encoding="utf-8")
    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="PRÁCTICA 3: Sockets",
    )
    doc.build(build_story(md))
    print(f"Generated {OUT_PATH}")


if __name__ == "__main__":
    main()

