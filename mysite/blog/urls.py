from django.urls import path
from . import views

# Define the application namespace for URL reversing
app_name = 'blog'

# URL patterns for the blog app
urlpatterns = [
    # Displays a list of blog posts
    path('', views.post_list, name='post_list'),
    # Displays details of a specific blog post
    path('<int:id>/', views.post_detail, name='post_detail'),
]