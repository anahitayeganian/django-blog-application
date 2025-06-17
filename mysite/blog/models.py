from django.conf import settings
from django.db import models
from django.utils import timezone

class Post(models.Model):
    # Enum-style choices for post status used in the 'status' field
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    # URL-friendly version of the title
    slug = models.SlugField(max_length=250)
    # ForeignKey to the author (user); enables reverse access via blog_posts
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,   # Deleting the user also deletes all related posts
        related_name='blog_posts'
    )
    body = models.TextField()
    publication_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Status field using choices defined above
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT
    )

    class Meta:
        # Order posts by most recent publication date first
        ordering = ['-publication_date']
        # Database index on publication date for faster queries
        indexes = [
            models.Index(fields=['-publication_date']),
        ]

    # Human-readable representation of a post instance
    def __str__(self):
        return self.title