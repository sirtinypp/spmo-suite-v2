
import os
import django
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from pypdf import PdfReader, PdfWriter

def generate_calibration_grid():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=portrait(A4))
    
    # Draw Grid
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.setFont("Helvetica", 6)
    
    # Verticals
    for x in range(0, 600, 50):
        c.line(x, 0, x, 850)
        c.drawString(x + 2, 10, str(x))
        
    # Horizontals
    for y in range(0, 850, 50):
        c.line(0, y, 600, y)
        c.drawString(10, y + 2, str(y))
        
    # Sub-grid (10s)
    c.setStrokeColorRGB(0.9, 0.9, 0.9)
    for x in range(0, 600, 10):
        if x % 50 != 0:
            c.line(x, 0, x, 850)
    for y in range(0, 850, 10):
        if y % 50 != 0:
            c.line(0, y, 600, y)

    c.showPage()
    c.save()
    
    template_path = 'static/templates/par_template_official.pdf'
    
    base_pdf = PdfReader(template_path)
    buffer.seek(0)
    overlay_pdf = PdfReader(buffer)
    
    writer = PdfWriter()
    page = base_pdf.pages[0]
    page.merge_page(overlay_pdf.pages[0])
    writer.add_page(page)
    
    output_path = "par_calibration_grid.pdf"
    with open(output_path, "wb") as f:
        writer.write(f)
    
    print(f"Calibration grid generated at: {output_path}")

if __name__ == "__main__":
    generate_calibration_grid()
