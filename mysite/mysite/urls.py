from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic.base import RedirectView
from blog.sitemaps import PostSitemap

# Define the sitemap dictionary
# The key posts is used in '/sitemap.xml' to reference '/sitemap-posts.xml', which lists all blog post URLs
sitemaps = {
    'posts': PostSitemap,
}

# Main URL configuration for the entire Django project
urlpatterns = [
    # Redirect the root URL '/' to the blog homepage at '/blog/'
    path('', RedirectView.as_view(url='/blog/', permanent=True)),

    # URL route for the Django admin interface
    path('admin/', admin.site.urls),

    # Include URL patterns defined in the blog app and assign a namespace for reverse URL matching
    path('blog/', include('blog.urls', namespace='blog')),

    # Serve the sitemap at '/sitemap.xml' using Django's built-in sitemap view
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
]
