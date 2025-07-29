from django.contrib.sitemaps import Sitemap
from .models import Post

class PostSitemap(Sitemap):
    # The change frequency of our post pages
    changefreq = 'weekly'
    # Their relevance in our website (the maximum value is 1)
    priority = 0.9

    # The QuerySet of objects to include in this sitemap
    def items(self):
        return Post.published.all()

    # For each post, return the date it was last updated
    # This helps search engines know when the content has changed
    def lastmod(self, obj):
        return obj.updated_at