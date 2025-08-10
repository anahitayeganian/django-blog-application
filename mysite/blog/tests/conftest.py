import pytest
from django.contrib.auth import get_user_model
from blog.models import Post

# Use the actual user model defined in AUTH_USER_MODEL instead of directly importing django.contrib.auth.models.User
# This keeps tests compatible if the project uses or switches to a custom user model
User = get_user_model()

@pytest.fixture
def user(db):
    """Fixture for creating a default test user."""
    return User.objects.create_user(username="testuser", password="pass")

@pytest.fixture
def published_post(user):
    """Fixture for creating a published blog post."""
    return Post.objects.create(
        title="Published Post",
        slug="published-post",
        author=user,
        body="Test published content",
        status=Post.Status.PUBLISHED
    )

@pytest.fixture
def draft_post(user):
    """Fixture for creating a draft blog post."""
    return Post.objects.create(
        title="Draft Post",
        slug="draft-post",
        author=user,
        body="Test draft content",
        status=Post.Status.DRAFT
    )

@pytest.fixture
def get_published_posts():
    """
    Callable fixture that returns the current list of published posts each time it is called.
    This fixture returns a function _get() which, when called, performs a fresh query on Post.published.all() and
    returns the results as a list.

    This allows tests to get an up-to-date list of published posts at any point, even if new posts are created or
    modified during the execution of the test.
    """
    def _get():
        return list(Post.published.all())
    return _get

@pytest.fixture
def multiple_published_posts(user):
    posts = [
        Post.objects.create(
            title=f"Post {i}",
            slug=f"post-{i}",
            author=user,
            body="Test multiple published posts",
            status=Post.Status.PUBLISHED,
        ) for i in range(3)
    ]
    return posts