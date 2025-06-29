from django.shortcuts import get_object_or_404, render
from .models import Post

def post_list(request):
    """
    Retrieve all published blog posts and render them in the post list template.
    Args:
        request: The HTTP request object.
    Returns:
        HttpResponse with the rendered 'blog/post/list.html' template, containing the list of published posts in the context.
    """
    posts = Post.published.all()
    return render(
        request,
        'blog/post/list.html',
        {'posts': posts}
    )

def post_detail(request, id):
    """
    Retrieve a single published blog post by its ID and render it in the post detail template.
    Args:
        request: The HTTP request object.
        id (int): The primary key of the post to retrieve.
    Returns:
        HttpResponse with the rendered 'blog/post/detail.html' template, containing the post in the context.
    Raises:
        Http404: If no published post with the given ID exists.
    """
    post = get_object_or_404(Post, id=id, status=Post.Status.PUBLISHED)
    return render(
        request,
        'blog/post/detail.html',
        {'post': post}
    )