import os
import hashlib
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.colors import Color
from pypdf import PdfReader, PdfWriter
from .models import AssetBatch, ApprovalLog, UserSignature

class PARGenerator:
    """
    Handles PDF generation, signature overlay, and finalization for PARs.
    """
    
    # Path to the base template (must be a PDF)
    TEMPLATE_PATH = os.path.join(settings.BASE_DIR, 'gamit_app/inventory/static/inventory/pdf/par_template.pdf')
    
    # Signature Coordinates (x, y) - Hardcoded based on A4 Portrait
    # Adjust these based on the actual template layout
    COORDS = {
        'INSPECTOR': (100, 200),
        'SUPERVISOR': (250, 200),
        'CHIEF_PRE': (400, 200), # Not used for signature, maybe initials?
        'AO': (100, 100),
        'CHIEF_FINAL': (400, 100),
    }

    @staticmethod
    def generate_draft(batch: AssetBatch):
        """
        Generates a draft PAR with Inspector/Supervisor signatures and WATERMARK.
        Returns ContentFile or path.
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=portrait(A4))
        
        # 1. Draw Watermark
        c.saveState()
        c.translate(300, 400)
        c.rotate(45)
        c.setFillColor(Color(0.8, 0.8, 0.8, alpha=0.5))
        c.setFont("Helvetica-Bold", 100)
        c.drawCentredString(0, 0, "DRAFT - FOR REVIEW")
        c.restoreState()

        # 2. Draw Inspector/Supervisor Signatures
        # Fetch logs for these actions
        # This is a bit complex, we need the logs.
        logs = batch.approval_logs.filter(action__in=['Inspect and Approve', 'Supervisor Approval'])
        
        for log in logs:
            if log.role == 'INSPECTOR' and log.signature_snapshot:
                 PARGenerator._draw_signature(c, log.signature_snapshot.path, PARGenerator.COORDS['INSPECTOR'])
            elif log.role == 'SUPERVISOR' and log.signature_snapshot:
                 PARGenerator._draw_signature(c, log.signature_snapshot.path, PARGenerator.COORDS['SUPERVISOR'])

        c.showPage()
        c.save()
        
        # 3. Merge with Base Template
        overlay_pdf = PdfReader(buffer)
        
        # If template exists, merge. Else just return the overlay (for now)
        if os.path.exists(PARGenerator.TEMPLATE_PATH):
            base_pdf = PdfReader(PARGenerator.TEMPLATE_PATH)
            writer = PdfWriter()
            
            page = base_pdf.pages[0]
            page.merge_page(overlay_pdf.pages[0])
            writer.add_page(page)
            
            output_buffer = BytesIO()
            writer.write(output_buffer)
            return ContentFile(output_buffer.getvalue(), name=f"par_draft_{batch.transaction_id}.pdf")
        else:
             # Fallback if no template
             return ContentFile(buffer.getvalue(), name=f"par_draft_{batch.transaction_id}.pdf")

    @staticmethod
    def finalize_par(batch: AssetBatch):
        """
        Generates the FINAL PAR with ALL signatures, no watermark.
        Flattens and hashes.
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=portrait(A4))
        
        # 1. Draw ALL Signatures
        logs = batch.approval_logs.all()
        for log in logs:
             role_key = None
             if log.role == 'INSPECTOR': role_key = 'INSPECTOR'
             elif log.role == 'SUPERVISOR': role_key = 'SUPERVISOR'
             elif log.role == 'USER_AO': role_key = 'AO'
             elif log.role == 'CHIEF' and log.action == 'Finalize and Release': role_key = 'CHIEF_FINAL'
             
             if role_key and log.signature_snapshot:
                  PARGenerator._draw_signature(c, log.signature_snapshot.path, PARGenerator.COORDS[role_key])
        
        c.showPage()
        c.save()
        
        # 2. Merge
        overlay_pdf = PdfReader(buffer)
        if os.path.exists(PARGenerator.TEMPLATE_PATH):
            base_pdf = PdfReader(PARGenerator.TEMPLATE_PATH)
            writer = PdfWriter()
            page = base_pdf.pages[0]
            page.merge_page(overlay_pdf.pages[0])
            writer.add_page(page)
            output_buffer = BytesIO()
            writer.write(output_buffer)
            final_content = output_buffer.getvalue()
        else:
            final_content = buffer.getvalue()

        # 3. Hash
        sha256_hash = hashlib.sha256(final_content).hexdigest()
        
        # 4. Save to Batch
        batch.par_file.save(f"PAR_FINAL_{batch.transaction_id}.pdf", ContentFile(final_content))
        batch.par_hash = sha256_hash
        batch.save()
        
        return batch.par_file

    @staticmethod
    def _draw_signature(c, image_path, coords):
        try:
            # Draw image at coords width=100, height=50 (aspect ratio?)
            c.drawImage(image_path, coords[0], coords[1], width=100, height=50, mask='auto')
        except Exception as e:
            print(f"Error drawing signature: {e}")
            c.drawString(coords[0], coords[1], "[Signature Error]")
