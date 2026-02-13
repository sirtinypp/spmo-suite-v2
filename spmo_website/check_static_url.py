import urllib.request
import urllib.error

url = "http://localhost:8000/static/images/test_image.png"

try:
    with urllib.request.urlopen(url) as response:
        print(f"Status: {response.status}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print("Success! Static serving works.")
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code} {e.reason}")
except urllib.error.URLError as e:
    print(f"URLError: {e.reason}")
except Exception as e:
    print(f"Error: {e}")
