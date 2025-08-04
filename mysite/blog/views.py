from django.contrib.postgres.search import SearchVector
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from taggit.models import Tag
from .forms import CommentForm, EmailPostForm, SearchForm
from .models import Post
from .services import send_post_recommendation_email

def post_list(request, tag_slug=None):
    """
    Display a list of published blog posts with pagination. If a tag is specified, only posts with that tag are shown.

    Args:
        request (HttpRequest): The incoming HTTP request, potentially containing a page GET parameter.
        tag_slug (str, optional): The slug of the tag used to filter the posts. Defaults to None.

    Returns:
        HttpResponse: HTML response with the rendered 'blog/post/list.html' template.
    """
    post_list = Post.published.all()
    tag = None

    if tag_slug:
        # Retrieve the tag object by its slug or return 404 if not found
        tag = get_object_or_404(Tag, slug=tag_slug)
        # Filter posts by the specified tag
        post_list = post_list.filter(tags__in=[tag])

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
        {
            'posts': posts,
            'tag': tag,
        }
    )

def post_detail(request, year, month, day, post):
    """
    Retrieve and render a published blog post based on its slug and publication date.

    Args:
        request (HttpRequest): The HTTP request object.
        year (int): The year the post was published.
        month (int): The month the post was published.
        day (int): The day the post was published.
        post (str): The slug identifying the post.

    Returns:
        HttpResponse: HTML response with the rendered 'blog/post/detail.html' template, including the post, its
        comments, an empty comment submission form, and a list of up to four similar posts based on shared tags.

    Raises:
        Http404: If no matching published post is found for the given slug and date.
    """
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publication_date__year=year,
        publication_date__month=month,
        publication_date__day=day
    )

    # Retrieve visible comments related to the post
    comments = post.comments.filter(is_visible=True)
    # Initialize an empty form for user submissions
    form = CommentForm()

    # Retrieve the IDs of tags associated with the current post
    post_tags_ids = post.tags.values_list('id', flat=True)
    # Find up to 4 published posts that share the most tags with the current post
    # Use a Q object to filter only tags that match those of the current post, and ensure the count
    # is distinct to avoid duplicates
    # Order the results by the number of shared tags (descending), then by publication date (most recent first)
    similar_posts = (
        Post.published
        .filter(tags__in=post_tags_ids)
        .exclude(id=post.id)
        .annotate(
            same_tags=Count('tags', filter=Q(tags__in=post_tags_ids), distinct=True)
        ).order_by('-same_tags', '-publication_date')[:4]
    )

    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
            'similar_posts': similar_posts,
        }
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
    post = Post.published.get_by_id_or_404(post_id)
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

@require_POST
def post_comment(request, post_id):
    """
    Handle the submission of a comment on a specific blog post.
    This view processes a POST request containing comment data submitted via a form.
    If the form is valid, it associates the comment with the corresponding published post,
    saves the comment to the database, and renders a confirmation message using the 'comment.html' template.
    If the form is invalid, the same template is rendered again with the form and validation errors. The comment form
    itself is included via the 'includes/comment_form.html' template.

    Args:
        request (HttpRequest): The HTTP request object containing the submitted form data.
        post_id (int): The ID of the blog post being commented on.

    Returns:
        HttpResponse: HTML response with the rendered 'blog/post/comment.html' template.

    Raises:
        Http404: If no published post with the given ID exists.
    """
    post = Post.published.get_by_id_or_404(post_id)
    comment = None

    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a new unsaved Comment instance from the validated form data
        comment = form.save(commit=False)
        # Associate the comment with the current post
        comment.post = post
        # Save the fully initialized comment instance to the database
        comment.save()

    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,
            'form': form,
            'comment': comment
        }
    )

def post_search(request):
    """
    Handle the logic for searching published blog posts based on a user-provided string.
    This view checks for a query parameter in the GET request. If present and valid, it performs a full-text search
    using PostgreSQL to retrieve published posts that match the search string within their title or body.

    Args:
        request (HttpRequest): The incoming HTTP request potentially containing a search query.

    Returns:
        HttpResponse: HTML response rendering 'blog/post/search.html' with the search form, the query string, and the list of matched posts.
    """
    search_form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        # Populate the form with submitted data from the GET request
        form = SearchForm(request.GET)
        if form.is_valid():
            # Extract the cleaned query string from the form data
            query = form.cleaned_data['query']
            # Perform a full-text search on published posts by creating a search vector from the title and body fields,
            # then filter posts that match the user's query
            results = Post.published.annotate(search=SearchVector('title','body'),).filter(search=query)

    # Render the search page template, passing the form, original query, and any search results
    return render(
        request,
        'blog/post/list.html',
        {
            'search_form': search_form,
            'query': query,
            'posts': results
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