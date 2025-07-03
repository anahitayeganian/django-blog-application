from django.core.paginator import EmptyPage, Paginator
from django.shortcuts import get_object_or_404, render
from .models import Post

def post_list(request):
    """
    Retrieve all published blog posts and render them with pagination support.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: HTML response with the rendered 'blog/post/list.html' template.
    """
    post_list = Post.published.all()
    # Paginate posts: 5 per page
    paginator = Paginator(post_list, 5)
    # Retrieve the current page number from the GET query parameters, defaulting to 1 if absent
    page_number = request.GET.get('page', 1)

    try:
        # Fetch posts for the requested page
        posts = paginator.page(page_number)
    except EmptyPage:
        # If page number is out of range, return the last valid page
        posts = paginator.page(paginator.num_pages)

    return render(
        request,
        'blog/post/list.html',
        {'posts': posts}
    )

def post_detail(request, year, month, day, post):
    """
    Retrieve a single published blog post by its slug and publication date, and render it in the post detail template.

    Args:
        request (HttpRequest): The HTTP request object.
        year (int): The year the post was published.
        month (int): The month the post was published.
        day (int): The day the post was published.
        post (str): The slug of the post to retrieve.

    Returns:
        HttpResponse: HTML response with the rendered 'blog/post/detail.html' template.

    Raises:
        Http404: If no published post with the given slug and date exists.
    """
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publication_date__year=year,
        publication_date__month=month,
        publication_date__day=day
    )

    return render(
        request,
        'blog/post/detail.html',
        {'post': post}
    )