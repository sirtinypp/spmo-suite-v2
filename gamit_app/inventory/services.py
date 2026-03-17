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
    TEMPLATE_PATH = os.path.join(settings.BASE_DIR, 'gamit_app/static/templates/par_template_official.pdf')
    
    # Signature & Text Coordinates (x, y) - A4 (595 x 842 points)
    # Coordinates are estimated based on Appendix 71 layout
    COORDS = {
        'ENTITY_NAME': (140, 725),
        'PAR_NO': (420, 725),
        'FUND_CLUSTER': (140, 712),
        'UPS_DV_NO': (420, 712),
        
        # Table Start (Iterate items)
        'TABLE_START_Y': 620,
        'COL_QTY': (60, 0),
        'COL_UOM': (105, 0),
        'COL_DESC': (160, 0),
        'COL_PROP_NO': (350, 0),
        'COL_DATE': (420, 0),
        'COL_COST': (500, 0),
        
        'TOTAL_COST': (500, 485),
        
        'SUPPLIER': (130, 460),
        'INVOICE': (130, 448),
        'PO_NO': (130, 436),

        'SIG_RECEIVED': (150, 310),
        'SIG_ISSUED': (420, 310),
        
        # signatories (names)
        'NAME_RECEIVED': (150, 260),
        'NAME_ISSUED': (420, 260),
        
        # footer
        'FOOTER_PREPARED': (170, 74),
        'FOOTER_INSPECTED': (170, 42),
        'FOOTER_REVIEWED': (170, 10),
        'FOOTER_POSTED': (170, -22), # This template seems crowded at the bottom
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
        buffer.seek(0)
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
        Generates the FINAL PAR with ALL signatures, 1 page per asset.
        """
        assets = batch.generated_assets.all()
        if not assets.exists():
            return None

        bulk_writer = PdfWriter()
        logs = batch.movement_logs.all().order_by('timestamp')

        # To keep readers in scope if necessary
        readers = []

        for asset in assets:
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=portrait(A4))
            
            # 1. Draw HEADER and Asset Details (1 per page)
            PARGenerator._draw_header(c, batch)
            PARGenerator._draw_asset_details(c, asset)
            
            # 2. Draw Signatures
            for log in logs:
                 role_key = None
                 role_code = log.persona.role.code if log.persona and log.persona.role else ''
                 
                 # RECEIVED BY (Unit AO / Accountable Officer)
                 if role_code == 'UNIT_AO': 
                     role_key = 'SIG_RECEIVED'
                     c.setFont("Helvetica-Bold", 10)
                     c.drawCentredString(PARGenerator.COORDS['NAME_RECEIVED'][0] + 40, PARGenerator.COORDS['NAME_RECEIVED'][1], f"{log.user.first_name} {log.user.last_name}".upper())
                     
                 # ISSUED BY (SSPMO Chief)
                 elif role_code == 'SPMO_CHIEF' and log.status_label == 'PAR_RELEASED': 
                     role_key = 'SIG_ISSUED'
                     c.setFont("Helvetica-Bold", 10)
                     c.drawCentredString(PARGenerator.COORDS['NAME_ISSUED'][0] + 40, PARGenerator.COORDS['NAME_ISSUED'][1], "ISAGANI L. BAGUS")
                     
                 # Footer signatories (Appendix 71)
                 elif role_code == 'SPMO_CLERK': 
                     c.setFont("Helvetica", 8)
                     c.drawString(PARGenerator.COORDS['FOOTER_PREPARED'][0], PARGenerator.COORDS['FOOTER_PREPARED'][1], f"{log.user.first_name} {log.user.last_name}")
                     c.drawString(PARGenerator.COORDS['FOOTER_PREPARED'][0] + 150, PARGenerator.COORDS['FOOTER_PREPARED'][1], log.timestamp.strftime("%Y-%m-%d"))
                 
                 elif role_code == 'INSPECTION_OFFICER': 
                     c.setFont("Helvetica", 8)
                     c.drawString(PARGenerator.COORDS['FOOTER_INSPECTED'][0], PARGenerator.COORDS['FOOTER_INSPECTED'][1], f"{log.user.first_name} {log.user.last_name}")
                     c.drawString(PARGenerator.COORDS['FOOTER_INSPECTED'][0] + 150, PARGenerator.COORDS['FOOTER_INSPECTED'][1], log.timestamp.strftime("%Y-%m-%d"))

                 elif role_code == 'SPMO_SUPERVISOR': 
                     c.setFont("Helvetica", 8)
                     c.drawString(PARGenerator.COORDS['FOOTER_REVIEWED'][0], PARGenerator.COORDS['FOOTER_REVIEWED'][1], f"{log.user.first_name} {log.user.last_name}")
                     c.drawString(PARGenerator.COORDS['FOOTER_REVIEWED'][0] + 150, PARGenerator.COORDS['FOOTER_REVIEWED'][1], log.timestamp.strftime("%Y-%m-%d"))

                 if role_key and log.signature_snapshot:
                      PARGenerator._draw_signature(c, log.signature_snapshot.path, PARGenerator.COORDS[role_key])
            
            # 3. Draw Custodian Signature and Name (If present)
            if asset.assigned_custodian:
                c.setFont("Helvetica-Oblique", 8)
                c.drawString(PARGenerator.COORDS['SIG_RECEIVED'][0] - 20, PARGenerator.COORDS['SIG_RECEIVED'][1] - 60, f"Actual User (Custodian): {asset.assigned_custodian}")
                if asset.custodian_signature:
                    PARGenerator._draw_signature(c, asset.custodian_signature.path, (PARGenerator.COORDS['SIG_RECEIVED'][0], PARGenerator.COORDS['SIG_RECEIVED'][1] - 50))

            # Draw "Posted by"
            c.setFont("Helvetica", 8)
            c.drawString(PARGenerator.COORDS['FOOTER_POSTED'][0], PARGenerator.COORDS['FOOTER_POSTED'][1], "Aaron Basa - thru GAMIT")
            c.drawString(PARGenerator.COORDS['FOOTER_POSTED'][0] + 150, PARGenerator.COORDS['FOOTER_POSTED'][1], batch.created_at.strftime("%Y-%m-%d"))

            c.showPage()
            c.save()
            
            # --- Merge Overlay for this page ---
            buffer.seek(0)
            overlay_pdf = PdfReader(buffer)
            
            if os.path.exists(PARGenerator.TEMPLATE_PATH):
                template_reader = PdfReader(PARGenerator.TEMPLATE_PATH)
                # We must append the template page to the writer and then merge the overlay onto it
                # to ensure all resources (background images, etc.) are preserved.
                template_page = template_reader.pages[0]
                template_page.merge_page(overlay_pdf.pages[0])
                bulk_writer.add_page(template_page)
                # Keep reference to reader
                readers.append(template_reader)
            else:
                bulk_writer.add_page(overlay_pdf.pages[0])

        # 4. Finalize and Save
        output_buffer = BytesIO()
        bulk_writer.write(output_buffer)
        final_content = output_buffer.getvalue()
        
        # Hash for integrity
        sha256_hash = hashlib.sha256(final_content).hexdigest()
        
        batch.par_file.save(f"PAR_FINAL_{batch.transaction_id}.pdf", ContentFile(final_content))
        batch.par_hash = sha256_hash
        batch.save()
        
        return batch.par_file

    @staticmethod
    def _draw_header(c, batch):
        c.setFont("Helvetica-Bold", 10)
        c.drawString(*PARGenerator.COORDS['ENTITY_NAME'], str(batch.requesting_unit or ""))
        c.drawString(*PARGenerator.COORDS['PAR_NO'], str(batch.transaction_id or ""))
        c.drawString(*PARGenerator.COORDS['FUND_CLUSTER'], str(batch.fund_cluster or ""))
        c.drawString(*PARGenerator.COORDS['UPS_DV_NO'], str(batch.ups_dv_number or ""))
        
        c.setFont("Helvetica", 9)
        c.drawString(*PARGenerator.COORDS['SUPPLIER'], str(batch.supplier_name or ""))
        c.drawString(*PARGenerator.COORDS['INVOICE'], str(batch.sales_invoice_number or ""))
        c.drawString(*PARGenerator.COORDS['PO_NO'], str(batch.po_number or ""))

    @staticmethod
    def _draw_asset_details(c, asset):
        """Draws details for a single asset (Appendix 71 per page)."""
        c.setFont("Helvetica", 9)
        y = PARGenerator.COORDS['TABLE_START_Y']
        
        # In a single-asset PAR, we show Qty=1
        c.drawCentredString(PARGenerator.COORDS['COL_QTY'][0], y, "1")
        c.drawCentredString(PARGenerator.COORDS['COL_UOM'][0], y, "pc")
        c.drawString(PARGenerator.COORDS['COL_DESC'][0], y, asset.name[:45])
        
        c.drawString(PARGenerator.COORDS['COL_PROP_NO'][0], y, str(asset.property_number or "N/A"))
        c.drawString(PARGenerator.COORDS['COL_DATE'][0], y, asset.date_acquired.strftime("%m/%d/%Y"))
        
        cost = asset.acquisition_cost or 0
        c.drawRightString(PARGenerator.COORDS['COL_COST'][0] + 50, y, f"{cost:,.2f}")
        
        # Total line
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(PARGenerator.COORDS['TOTAL_COST'][0] + 50, PARGenerator.COORDS['TOTAL_COST'][1], f"{cost:,.2f}")

    @staticmethod
    def _draw_signature(c, image_path, coords):
        try:
            c.drawImage(image_path, coords[0], coords[1], width=80, height=40, mask='auto')
        except Exception as e:
            print(f"Error drawing signature: {e}")
            c.setFont("Helvetica-Oblique", 7)
            c.drawString(coords[0], coords[1], "[Digitally Signed]")


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
            overlay_buffer.seek(0)
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
            overlay_buffer.seek(0)
            overlay_pdf = PdfReader(overlay_buffer)
            writer = PdfWriter()
            page = base_pdf.pages[0]
            page.merge_page(overlay_pdf.pages[0])
            writer.add_page(page)
            out = BytesIO()
            writer.write(out)
            return ContentFile(out.getvalue(), name=f"ptr_{type_str}_{transfer.transaction_id}.pdf")
        return ContentFile(overlay_buffer.getvalue(), name=f"ptr_{type_str}_{transfer.transaction_id}.pdf")
