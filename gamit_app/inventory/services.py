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
        # This now pulls from the Official Movement Logs (Signature-Lock)
        logs = batch.movement_logs.filter(persona__role__code__in=['INSPECTION_OFFICER', 'SPMO_SUPERVISOR'])
        
        for log in logs:
            if log.persona.role.code == 'INSPECTION_OFFICER' and log.signature_snapshot:
                 PARGenerator._draw_signature(c, log.signature_snapshot.path, PARGenerator.COORDS['INSPECTOR'])
            elif log.persona.role.code == 'SPMO_SUPERVISOR' and log.signature_snapshot:
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
        
        # 1. Draw ALL Signatures from the Official Workflow Movement Logs
        logs = batch.movement_logs.all()
        for log in logs:
             role_key = None
             role_code = log.persona.role.code if log.persona and log.persona.role else ''
             
             if role_code == 'INSPECTION_OFFICER': role_key = 'INSPECTOR'
             elif role_code == 'SPMO_SUPERVISOR': role_key = 'SUPERVISOR'
             elif role_code == 'UNIT_AO': role_key = 'AO'
             elif role_code == 'SPMO_CHIEF' and log.status_label == 'FINALIZED': role_key = 'CHIEF_FINAL'
             
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


class ICSGenerator:
    """
    Handles PDF generation and finalization for Inventory Custodian Slips (ICS).
    ICS is used for items under P50,000 threshold.
    """
    
    # Path to the base template
    TEMPLATE_PATH = os.path.join(settings.BASE_DIR, 'gamit_app/inventory/static/inventory/pdf/ics_template.pdf')
    
    # Signature Coordinates (x, y) - A4 Portrait estimation
    COORDS = {
        'RECEIVED_BY': (100, 150),
        'ISSUED_BY': (400, 150),
    }

    @staticmethod
    def generate_draft(batch: AssetBatch):
        """Generates a draft ICS with watermark."""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=portrait(A4))
        
        c.saveState()
        c.translate(300, 400)
        c.rotate(45)
        c.setFillColor(Color(0.8, 0.8, 0.8, alpha=0.5))
        c.setFont("Helvetica-Bold", 100)
        c.drawCentredString(0, 0, "ICS DRAFT")
        c.restoreState()

        # Try mapping available signatures
        logs = getattr(batch, 'movement_logs', None)
        if logs:
             for log in logs.all():
                 # Match logic depending on how signatures are captured in movement_logs 
                 # Or use ApprovalLogs if still heavily relying on the old module.
                 pass

        c.showPage()
        c.save()
        
        return ICSGenerator._merge(buffer, batch, "draft")

    @staticmethod
    def finalize_ics(batch: AssetBatch):
        """Generates the FINAL ICS with ALL signatures."""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=portrait(A4))
        
        # Overlay signatures... (logic relies heavily on tracking the signature_snapshot in the log)
        # We will keep it generalized for the baseline.
        c.showPage()
        c.save()

        # Generate Hash
        batch.par_hash = hashlib.sha256(buffer.getvalue()).hexdigest()
        
        # Note: Saving field should probably be abstracted since it's an ICS, not a PAR
        # We save it to par_file for now as the model field is generic.
        final_file = ICSGenerator._merge(buffer, batch, "final")
        batch.par_file.save(f"ICS_{batch.transaction_id}_Final.pdf", final_file, save=True)
        return final_file

    @staticmethod
    def _merge(overlay_buffer, batch, type_str):
        if os.path.exists(ICSGenerator.TEMPLATE_PATH):
            base_pdf = PdfReader(ICSGenerator.TEMPLATE_PATH)
            overlay_pdf = PdfReader(overlay_buffer)
            writer = PdfWriter()
            page = base_pdf.pages[0]
            page.merge_page(overlay_pdf.pages[0])
            writer.add_page(page)
            out = BytesIO()
            writer.write(out)
            return ContentFile(out.getvalue(), name=f"ics_{type_str}_{batch.transaction_id}.pdf")
        return ContentFile(overlay_buffer.getvalue(), name=f"ics_{type_str}_{batch.transaction_id}.pdf")


class PTRGenerator:
    """
    Handles PDF generation for Property Transfer Reports (PTR).
    Used during AssetTransfer requests.
    """
    
    TEMPLATE_PATH = os.path.join(settings.BASE_DIR, 'gamit_app/inventory/static/inventory/pdf/ptr_template.pdf')
    
    COORDS = {
        'APPROVED_BY': (100, 150),
        'RELEASED_BY': (300, 150),
        'RECEIVED_BY': (450, 150)
    }

    @staticmethod
    def generate_draft(transfer):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=portrait(A4))
        c.saveState()
        c.translate(300, 400)
        c.rotate(45)
        c.setFillColor(Color(0.8, 0.8, 0.8, alpha=0.5))
        c.setFont("Helvetica-Bold", 100)
        c.drawCentredString(0, 0, "PTR DRAFT")
        c.restoreState()
        c.showPage()
        c.save()
        return PTRGenerator._merge(buffer, transfer, "draft")

    @staticmethod
    def finalize_ptr(transfer):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=portrait(A4))
        # Draw final signatures logic here
        c.showPage()
        c.save()
        
        # Assuming AssetTransferRequest gets a generic `document_file` or `ptr_file` field eventually
        # Currently, returning ContentFile to be saved by the view.
        final_file = PTRGenerator._merge(buffer, transfer, "final")
        if hasattr(transfer, 'par_file'): # Using if it exists
            transfer.par_file.save(f"PTR_{transfer.transaction_id}_Final.pdf", final_file, save=True)
        return final_file

    @staticmethod
    def _merge(overlay_buffer, transfer, type_str):
        if os.path.exists(PTRGenerator.TEMPLATE_PATH):
            base_pdf = PdfReader(PTRGenerator.TEMPLATE_PATH)
            overlay_pdf = PdfReader(overlay_buffer)
            writer = PdfWriter()
            page = base_pdf.pages[0]
            page.merge_page(overlay_pdf.pages[0])
            writer.add_page(page)
            out = BytesIO()
            writer.write(out)
            return ContentFile(out.getvalue(), name=f"ptr_{type_str}_{transfer.transaction_id}.pdf")
        return ContentFile(overlay_buffer.getvalue(), name=f"ptr_{type_str}_{transfer.transaction_id}.pdf")
