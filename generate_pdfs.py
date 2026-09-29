"""Build visually distinct, clearly synthetic patient summary PDFs for the demo."""

import json
from pathlib import Path

import reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas


DATA = Path(__file__).resolve().parent / "data"
NAVY = colors.HexColor("#15314E")
BLUE = colors.HexColor("#1867A7")
GRAY = colors.HexColor("#4B6075")
PALE = colors.HexColor("#EDF4FA")
FONTS = Path(reportlab.__file__).resolve().parent / "fonts"
pdfmetrics.registerFont(TTFont("DejaVu", str(FONTS / "Vera.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(FONTS / "VeraBd.ttf")))


def lines(text: str, width: int, font_size: int = 11) -> list[str]:
    output, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if stringWidth(candidate, "DejaVu", font_size) > width and current:
            output.append(current)
            current = word
        else:
            current = candidate
    return output + ([current] if current else [])


def generate():
    patients = json.loads((DATA / "patients.json").read_text(encoding="utf-8"))
    for patient_id, patient in patients.items():
        target = DATA / f"{patient_id}_synthetic_patient.pdf"
        c = Canvas(str(target), pagesize=letter)
        c.setTitle(f"Synthetic patient summary - {patient_id}")
        c.setFillColor(NAVY)
        c.rect(0, 672, 612, 120, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("DejaVu-Bold", 13)
        c.drawString(48, 739, "FICTIONAL CASE FILE")
        c.setFont("DejaVu-Bold", 24)
        c.drawString(48, 703, "MRI prior authorization")
        c.setFillColor(PALE)
        c.roundRect(48, 562, 516, 80, 10, fill=1, stroke=0)
        c.setFillColor(GRAY)
        c.setFont("DejaVu-Bold", 10)
        c.drawString(65, 617, "PATIENT ID")
        c.drawString(275, 617, "PLAN STATUS")
        c.setFillColor(NAVY)
        c.setFont("DejaVu-Bold", 16)
        c.drawString(65, 588, patient_id)
        c.drawString(275, 588, "Active" if patient["plan_active"] else "Inactive")
        c.setFillColor(BLUE)
        c.setFont("DejaVu-Bold", 11)
        c.drawString(48, 520, "PATIENT")
        c.setFillColor(NAVY)
        c.setFont("DejaVu", 15)
        c.drawString(48, 495, patient["name"])
        c.setFillColor(BLUE)
        c.setFont("DejaVu-Bold", 11)
        c.drawString(48, 450, "CLINICAL NOTE (PLAIN-TEXT INPUT ALSO PROVIDED)")
        note = (DATA / f"{patient_id}.txt").read_text(encoding="utf-8")
        c.setFillColor(NAVY)
        c.setFont("DejaVu", 11)
        y = 421
        for line in lines(note, 490):
            c.drawString(48, y, line)
            y -= 18
        c.setStrokeColor(colors.HexColor("#D7E2EC"))
        c.line(48, 93, 564, 93)
        c.setFillColor(GRAY)
        c.setFont("DejaVu", 9)
        c.drawString(48, 76, "Entirely synthetic. Created for a coding exercise; not a real medical record.")
        c.showPage()
        c.save()
        print(target)


if __name__ == "__main__":
    generate()
