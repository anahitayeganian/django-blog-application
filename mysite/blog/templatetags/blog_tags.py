from django import template
from ..models import Post

# Create a template library instance to register custom tags
register = template.Library()

@register.simple_tag
def total_posts():
    # Return the count of all posts using the custom published manager
    return Post.published.count()