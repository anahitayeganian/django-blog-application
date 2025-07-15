from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from .forms import EmailPostForm
from .models import Post
from .services import send_post_recommendation_email

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
    except PageNotAnInteger:
        # If page_number is not an integer, return the first page
        posts = paginator.page(1)
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

def post_share(request, post_id):
    """
    Handle the logic for sharing a blog post via email.

    Args:
        request (HttpRequest): The HTTP request object.
        post_id (int): The ID of the post to be shared.

    Returns:
        HttpResponse: HTML response with the rendered 'blog/post/share.html' template.

    Raises:
        Http404: If no published post with the given ID exists.
    """
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Extract cleaned form data after validation
            cd = form.cleaned_data
            # Build the full absolute URL to the post for inclusion in the email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            # Delegate email sending to the service layer
            send_post_recommendation_email(post, cd, post_url)
            sent = True
    else:
        form = EmailPostForm()

    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent
        }
    )

class PostListView(ListView):
    """
    Displays a paginated list of published blog posts.
    Uses the blog/post/list.html template and shows 5 posts per page.
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 5
    template_name = 'blog/post/list.html'