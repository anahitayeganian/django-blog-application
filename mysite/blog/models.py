from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

# Define a custom manager to handle queries specific to published posts
class PublishedManager(models.Manager):
    def get_queryset(self):
        # Override the default queryset to return only posts with PUBLISHED status
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)

class Post(models.Model):
    # Enum-style choices for post status used in the status field
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    # URL-friendly version of the title
    # The slug field is required to be unique for the date stored in the publication_date field
    # Although publication_date is a DateTimeField, uniqueness is checked using just the date portion
    slug = models.SlugField(max_length=250, unique_for_date='publication_date')
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

    #The default manager
    objects = models.Manager()
    # Custom manager
    published = PublishedManager()

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

    # Returns the absolute URL to access the detail view of this post instance
    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.id])