from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

def send_post_recommendation_email(post, cd, post_url):
    """
    Sends a recommendation email for a given blog post, including the post title, a link to the post, and any additional comments.

    Args:
         post (Post): The blog post object being recommended.
         cd (dict): Cleaned form data containing the recommender's name, email, recipient's email, and optional comments.
         post_url (str): Absolute URL to the blog post.

    Returns:
        None
    """
    subject = f"{cd['name']} ({cd['email']}) recommends you read {post.title}"
    message = (
        f"Read {post.title} at {post_url}\n\n"
        f"{cd['name']}\'s comments: {cd['comments']}"
    )

    # Send email using Django's built-in send_email utility
    send_mail(
        subject=subject,
        message=message,
        from_email=None,    # Uses DEFAULT_FROM_EMAIL from settings.py
        recipient_list=[cd['to']]
    )

def paginate_queryset(request, queryset, per_page=5):
    """
    Paginate a given queryset based on the GET request's page parameter.
    Handles edge cases such as non-integer page numbers and out-of-range pages.

    Args:
        request (HttpRequest): The HTTP request object.
        queryset (QuerySet): The queryset of objects to paginate.
        per_page (int, optional): Number of items per page.

    Returns:
        Page: A Django Page object containing the objects for the current page.
    """

    # Create a Paginator instance with the specified number of items per page
    paginator = Paginator(queryset, per_page)
    # Get the current page number from the request query parameters, defaulting to 1 if absent
    page_number = request.GET.get('page', 1)

    try:
        # Fetch posts for the requested page
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer, return the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page number is out of range, deliver the last valid page
        posts = paginator.page(paginator.num_pages)

    return posts