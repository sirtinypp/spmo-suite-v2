import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_supplies_project.settings')
django.setup()

from supplies.models import News

def create_sample_news():
    news_items = [
        {
            "title": "Welcome to the New Systems!",
            "content": "We are excited to launch the new integrated SPMO Suite. Experience faster transactions and real-time updates across all modules.",
            "date": timezone.now() - timezone.timedelta(days=1)
        },
        {
            "title": "Inventory Maintenance Schedule",
            "content": "Please be advised that system maintenance is scheduled for this coming Saturday from 8:00 AM to 12:00 PM. Access may be intermittent.",
            "date": timezone.now() - timezone.timedelta(days=5)
        },
        {
            "title": "New Paper Supplies Available",
            "content": "Fresh stocks of A4 and Legal size Bond Paper (Sub 20) have just arrived. Department requests are now being processed.",
            "date": timezone.now() - timezone.timedelta(days=10)
        }
    ]

    for item in news_items:
        News.objects.get_or_create(
            title=item["title"],
            defaults={
                "content": item["content"],
                "date_posted": item["date"],
                "is_active": True
            }
        )
    
    print(f"Successfully created {len(news_items)} news items.")

if __name__ == '__main__':
    create_sample_news()
