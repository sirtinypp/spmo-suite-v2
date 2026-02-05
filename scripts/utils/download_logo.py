import os

# Official UP Seal SVG (Simplified for reliability)
svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
<circle cx="50" cy="50" r="48" fill="#7b1113" stroke="#00563f" stroke-width="2"/>
<text x="50" y="50" font-family="serif" font-size="40" fill="#fff" text-anchor="middle" dy=".3em">UP</text>
</svg>"""

# Using a simplified placeholder if official one fails, but I will try to write a proper one or successful download.
# Actually, let's try to download from a different mirror or just write a placeholder for now to fix the layout errors.
# Better yet, I will use the Base64 of the actual seal if I had it.
# Since I don't, I will write the URL that is known to work: 
# https://upload.wikimedia.org/wikipedia/commons/3/3a/University_of_the_Philippines_Seal.svg (Commons vs En)
# Let's try Commons.

import urllib.request

url = "https://upload.wikimedia.org/wikipedia/commons/3/3a/University_of_the_Philippines_Seal.svg"
path = "gfa_app/travel/static/travel/img"
file_path = f"{path}/up_seal.svg"

headers = {'User-Agent': 'Mozilla/5.0'}

try:
    os.makedirs(path, exist_ok=True)
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response, open(file_path, 'wb') as out_file:
        out_file.write(response.read())
    print("Success: Downloaded from Commons")
except Exception as e:
    print(f"Error downloading: {e}")
    # Fallback to creating a placeholder SVG
    with open(file_path, "w") as f:
        f.write(svg_content)
    print("Fallback: Created placeholder SVG")
