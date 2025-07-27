from django import template
from ..models import Post

# Create a template library instance to register custom tags
register = template.Library()

@register.simple_tag
def total_posts():
    # Return the count of all posts using the custom published manager
    return Post.published.count()

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    # Get the latest 'count' published posts, ordered by descending publication_date
    latest_posts = Post.published.order_by('-publication_date')[:count]
    # Return the posts in a dictionary to render them in the latest_posts.html template
    return {'latest_posts': latest_posts}