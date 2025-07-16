from django.contrib import admin
from .models import Comment, Post

# Register the Post model with a custom admin interface for better content management
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Display these fields in the list view of the admin panel
    list_display = ['title', 'slug', 'author', 'publication_date', 'status']
    # Enable filters in the sidebar for quicker querying
    list_filter = ['status', 'created_at', 'publication_date', 'author']
    # Add search capability on title and body fields
    search_fields = ['title', 'body']
    # Auto-generate the slug from the title on model creation
    prepopulated_fields = {'slug': ('title',)}
    # Use raw ID input for the author field to improve performance with large user sets
    raw_id_fields = ['author']
    # Enables chronological navigation by publication date
    date_hierarchy = 'publication_date'
    # Default ordering of the list view
    ordering = ['status', 'publication_date']
    # Always show search facets
    show_facets = admin.ShowFacets.ALWAYS

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # Display these fields in the list view of the admin panel
    list_display = ['name', 'email', 'post', 'created_at', 'is_visible']
    # Enable filters in the sidebar for quicker querying
    list_filter = ['is_visible', 'created_at', 'updated_at']
    # Add search capability on name, email and body fields
    search_fields = ['name', 'email', 'body']