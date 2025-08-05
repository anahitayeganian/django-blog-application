from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from taggit.models import Tag
from .forms import CommentForm, EmailPostForm, SearchForm
from .models import Post
from .services import paginate_queryset, send_post_recommendation_email

def post_list(request, tag_slug=None):
    """
    Display a list of published blog posts, optionally filtered by tag.
    If a tag_slug is provided, the view filters posts to only include those tagged accordingly.
    The result is paginated.

    Args:
        request (HttpRequest): The HTTP request object.
        tag_slug (str, optional): The slug identifying the tag to filter posts by. Defaults to None.

    Returns:
        HttpResponse: Rendered HTML page displaying the list of posts.
    """
    post_list = Post.published.all()
    tag = None

    if tag_slug:
        # Retrieve the tag object by its slug or return 404 if not found
        tag = get_object_or_404(Tag, slug=tag_slug)
        # Filter posts by the specified tag
        post_list = post_list.filter(tags__in=[tag])

    paginated_posts = paginate_queryset(request, post_list, per_page=5)

    return render(
        request,
        'blog/post/list.html',
        {
            'posts': paginated_posts,
            'tag': tag,
        }
    )

def post_detail(request, year, month, day, post):
    """
    Display the details of a single published post, retrieved based on its slug and publication date.

    Args:
        request (HttpRequest): The HTTP request object.
        year (int): The year the post was published.
        month (int): The month the post was published.
        day (int): The day the post was published.
        post (str): The slug identifying the post.

    Returns:
        HttpResponse: Rendered HTML page with the post, comments, an empty comment submission form, and a list of up
        to four similar posts based on shared tags.

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
    Allow users to share a blog post via email.

    Args:
        request (HttpRequest): The HTTP request object.
        post_id (int): The ID of the post to be shared.

    Returns:
        HttpResponse: Rendered HTML page containing the share form.

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
    If the form is valid, it associates and saves the comment with the corresponding published post, then renders a confirmation message.
    If the form is invalid, the same template is rendered again with the form and validation errors.

    Args:
        request (HttpRequest): The HTTP request object containing the form data.
        post_id (int): The ID of the blog post being commented on.

    Returns:
        HttpResponse: Rendered HTML page.

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
    Search published posts based on a user-provided string using PostgreSQL.
    If a valid query parameter is provided, performs a full-text search on the title and body fields, ranks the results
    by relevance, and paginates them.

    Args:
        request (HttpRequest): The HTTP request object, containing the user's search query.

    Returns:
        HttpResponse: Rendered HTML page with the paginated list of matched posts.
    """
    search_form = SearchForm()
    query = None
    results = Post.published.none()

    if 'query' in request.GET:
        # Populate the form with submitted data from the GET request
        form = SearchForm(request.GET)
        if form.is_valid():
            # Extract the cleaned query string from the form data
            query = form.cleaned_data['query']

            # Combine title and body fields into a single search vector
            search_vector = SearchVector('title', 'body')
            # Convert the user’s query into a format suitable for PostgreSQL full-text search
            search_query = SearchQuery(query)

            # Annotate the posts queryset with (search) the combined search vector used for full-text search and
            # (rank) a relevance score calculated by comparing the search vector to the search query
            # Then filter posts matching the query and order by descending relevance (highest rank first)
            results = (
                Post.published.annotate(
                    search=search_vector,
                    rank=SearchRank(search_vector, search_query)
                )
                .filter(search=search_query)
                .order_by('-rank')
            )

    paginated_posts = paginate_queryset(request, results, per_page=5)

    # Render the search page template, passing the form, original query, and any search results
    return render(
        request,
        'blog/post/list.html',
        {
            'search_form': search_form,
            'query': query,
            'posts': paginated_posts,
        }
    )

class PostListView(ListView):
    """
    Class-based view to display a paginated list of published posts.
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 5
    template_name = 'blog/post/list.html'