import os

# 1. FIX VIEWS.PY
view_path = r'gamit_app/inventory/views.py'
with open(view_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'import re' not in content:
    content = content.replace('import json', 'import json\nimport re\nimport os')

view_code = """
# ==========================================
# 11. BULK MEDIA MANAGER (Surgical Execution)
# ==========================================
@login_required
def bulk_media_upload(request):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard')

    results = []
    if request.method == 'POST' and request.FILES.getlist('images'):
        images = request.FILES.getlist('images')
        upload_type = request.POST.get('upload_type', 'condition') # 'serials' or 'condition'
        
        for image in images:
            filename = image.name
            # Extract digits only (e.g. "315716.jpg" -> "315716")
            import re
            match = re.search(r'(\\d+)', filename)
            
            if not match:
                results.append({'file': filename, 'status': 'Error', 'msg': 'No numeric PAR found in name.'})
                continue
            
            par_digits = match.group(1)
            # Find asset where property_number contains these digits (e.g. "PAR-315716")
            from .models import Asset
            asset = Asset.objects.filter(property_number__icontains=par_digits).first()
            
            if asset:
                try:
                    if upload_type == 'serials':
                        asset.image_serial = image
                    else:
                        asset.image_condition = image
                    asset.save()
                    results.append({'file': filename, 'status': 'Success', 'asset': asset.property_number})
                except Exception as e:
                    results.append({'file': filename, 'status': 'Error', 'msg': str(e)})
            else:
                results.append({'file': filename, 'status': 'Not Found', 'msg': f'No Asset matches digits: {par_digits}'})

        messages.success(request, f"Processed {len(images)} images.")

    return render(request, 'inventory/bulk_media.html', {'results': results})
"""

if 'def bulk_media_upload' not in content:
    content += view_code

with open(view_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Surgically updated views.py")

# 2. FIX URLS.PY
url_path = r'gamit_app/inventory/urls.py'
with open(url_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'administration/bulk-upload' in line:
        continue
    # Strip bad formatting from previous attempts
    if ']' in line and 'path' not in line:
        line = ']\n'
    new_lines.append(line)

# Add the correct path before the final closing bracket
for i in range(len(new_lines)-1, -1, -1):
    if ']' in new_lines[i]:
        new_lines.insert(i, "    path('administration/bulk-upload/', views.bulk_media_upload, name='bulk_media_upload'),\n")
        break

with open(url_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Surgically updated urls.py")
