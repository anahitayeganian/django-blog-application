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

def post_detail(request, year, month, day, post):
    """
    Retrieve a single published blog post by its slug and publication date, and render it in the post detail template.
    Args:
        request: The HTTP request object.
        year (int): The year the post was published.
        month (int): The month the post was published.
        day (int): The day the post was published.
        post (str): The slug of the post to retrieve.
    Returns:
        HttpResponse with the rendered 'blog/post/detail.html' template, containing the post in the context.
    Raises:
        Http404: If no published post with the given slug and date exists.
    """
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED, slug=post, publication_date__year=year,
                             publication_date__month=month, publication_date__day=day)
    return render(
        request,
        'blog/post/detail.html',
        {'post': post}
    )