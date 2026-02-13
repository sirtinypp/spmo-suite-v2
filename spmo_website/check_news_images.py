from website.models import News
import os

print("--- Checking News Images ---")
for news in News.objects.all():
    print(f"Title: {news.title}")
    if news.image:
        print(f"Image Field: {news.image}")
        print(f"Image URL: {news.image.url}")
        print(f"File Exists: {os.path.exists(news.image.path)}")
    else:
        print("Image Field: None")
    print("-" * 20)
