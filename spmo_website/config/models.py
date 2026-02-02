from django.db import models
from django.conf import settings
from django.utils import timezone

class AuditableModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_created"
    )

    class Meta:
        abstract = True

class NewsPost(AuditableModel):
    # Category Options (Value, Readable Name)
    CATEGORY_CHOICES = [
        ('MEMO', 'Memorandum'),
        ('EVENT', 'Event'),
        ('ADVISORY', 'Advisory'),
        ('GFA', 'GFA Update'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='ADVISORY')
    summary = models.TextField(help_text="Short description for the card (Max 200 chars recommended)")
    content = models.TextField(help_text="The full article content for the popup", blank=True, null=True)
    
    # Uploads
    image = models.ImageField(upload_to='news_images/', help_text="Card thumbnail image", blank=True, null=True)
    attachment = models.FileField(upload_to='news_docs/', blank=True, null=True, help_text="Optional: Upload PDF Memo")
    
    date_posted = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_posted'] 

    def __str__(self):
        return self.title

    @property
    def color_theme(self):
        themes = {
            'MEMO': 'blue',
            'EVENT': 'amber',
            'ADVISORY': 'red',
            'GFA': 'emerald'
        }
        return themes.get(self.category, 'slate')

    @property
    def month_abbr(self):
        """Returns uppercase month abbreviation, e.g., 'JAN'"""
        return self.date_posted.strftime("%b").upper()

    @property
    def day_str(self):
        """Returns day string, e.g., '27'"""
        return self.date_posted.strftime("%d")

class InspectionSchedule(AuditableModel):
    unit_name = models.CharField(max_length=200, help_text="e.g., College of Engineering")
    activity = models.CharField(max_length=200, help_text="e.g., Physical Inventory Count")
    scheduled_date = models.DateField()
    status = models.CharField(
        max_length=20, 
        choices=[('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'), ('COMPLETED', 'Completed')], 
        default='PENDING'
    )
    
    class Meta:
        ordering = ['scheduled_date']

    def __str__(self):
        return f"{self.unit_name} - {self.scheduled_date}"