import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamit_core.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from inventory.views import create_batch_request
from inventory.models import AssetBatch, BatchItem

def test_batch_creation():
    print("--- Testing Batch Creation Logic ---")
    
    # Setup User
    user, _ = User.objects.get_or_create(username='test_ao_batch')
    
    # Mock Files
    pdf1 = SimpleUploadedFile("test1.pdf", b"dummy content 1", content_type="application/pdf")
    pdf2 = SimpleUploadedFile("test2.pdf", b"dummy content 2", content_type="application/pdf")
    
    # Mock POST Data (Form + Formset)
    data = {
        # AssetBatchForm fields
        'supplier_name': 'Test Supplier Inc.',
        'po_number': 'PO-999',
        'sales_invoice_number': 'SI-888',
        'remarks': 'Test Batch Creation',
        
        # BatchItemFormSet management form
        'items-TOTAL_FORMS': '1',
        'items-INITIAL_FORMS': '0',
        'items-MIN_NUM_FORMS': '0',
        'items-MAX_NUM_FORMS': '1000',
        
        # BatchItemFormSet Item 0
        'items-0-unit': 'Unit',
        'items-0-quantity': '5',
        'items-0-description': 'Test Laptop',
        'items-0-amount': '50000.00',
    }
    
    # Files
    files = {
        'doc_1_file': pdf1,
        'doc_2_file': pdf2,
        # doc_3 is optional
    }
    
    # Merge data and files
    post_data = {**data, **files}
    
    from django.test import Client
    c = Client()
    c.force_login(user)
    
    response = c.post('/transaction/batch/', data=post_data, HTTP_HOST='localhost')
    
    # Verify
    print(f"Response Status Code: {response.status_code}")
    
    if response.status_code == 302:
         print("Redirect detected (Success?)")
    
    # Check Database
    batch = AssetBatch.objects.filter(po_number='PO-999').last()
    if batch:
        print(f"Batch Created: {batch.transaction_id}")
        return True
    else:
        print("Batch NOT created.")
        if response.context:
            print("Context Keys:", response.context.keys())
            if 'form' in response.context:
                print(f"Form Errors: {response.context['form'].errors}")
            if 'formset' in response.context:
                print(f"Formset Errors: {response.context['formset'].errors}")
                print(f"Formset Non-Form Errors: {response.context['formset'].non_form_errors()}")
            # Check content for "error" string
            if b'error' in response.content.lower():
                print("Found 'error' in response content.")
        else:
            print("No context available in response.")
            # Print content to find errors manually
            content = response.content.decode('utf-8')
            if 'errorlist' in content:
                print("Found validation errors in HTML:")
                # Simple extraction of errors
                import re
                errors = re.findall(r'<ul class="errorlist">.*?</ul>', content, re.DOTALL)
                for err in errors:
                    print(err)
            else:
                 print("No errorlist class found in HTML. Printing first 1000 chars:")
                 print(content[:1000])
        return False

if __name__ == "__main__":
    if test_batch_creation():
        print("✅ Batch Creation Verification PASSED")
    else:
        print("❌ Batch Creation Verification FAILED")
