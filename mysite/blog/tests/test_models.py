from django.urls import reverse
import pytest
from blog.models import Post

def assert_all_posts_published(posts):
    assert all(post.status == Post.Status.PUBLISHED for post in posts), "All posts must have status PUBLISHED"

@pytest.mark.django_db
def test_returns_empty_list_when_no_posts(get_published_posts):
    """
    When no posts exist, PublishedManager should return an empty list.
    This tests the edge case of an empty database.
    """
    assert get_published_posts() == []

@pytest.mark.django_db
def test_draft_post_is_excluded(get_published_posts, draft_post):
    """
    Draft posts should not appear in the PublishedManager results.
    Verify that draft posts are explicitly excluded.
    """
    posts = get_published_posts()
    assert draft_post not in posts, "Draft posts should be excluded from published posts"

@pytest.mark.django_db
def test_published_post_is_included(get_published_posts, published_post):
    """
    Verify that published posts are included in the PublishedManager results.
    """
    posts = get_published_posts()
    assert published_post in posts, "Published posts should be included in the published posts list"

@pytest.mark.django_db
def test_published_manager_only_returns_published_status(get_published_posts, published_post, draft_post):
    """PublishedManager returns only published posts when both types exist."""
    posts = get_published_posts()
    assert len(posts) == 1, "There should be one published post"
    assert_all_posts_published(posts)

@pytest.mark.django_db
def test_published_manager_returns_multiple_posts(get_published_posts, multiple_published_posts):
    """
    Verify that the PublishedManager returns all published posts when multiple exist.

    This test ensures that when multiple published posts are present,
    the manager returns exactly those posts and that all have the status 'PUBLISHED'.
    """
    posts = get_published_posts()
    assert len(posts) == 3, "There should be exactly 3 published posts"
    assert_all_posts_published(posts)

@pytest.mark.django_db
def test_get_absolute_url_matches_reverse_pattern(published_post):
    """
    Verify that the Post model's get_absolute_url method returns the correct URL for the post detail view.

    The test builds the expected URL using Django's reverse with the year, month, day, and slug extracted from the post,
    and compares it to the URL returned by the method.

    This ensures the method generates the URL according to the 'blog:post_detail' named URL pattern.
    """
    expected_url = reverse(
        'blog:post_detail',
        args=[
            published_post.publication_date.year,
            published_post.publication_date.month,
            published_post.publication_date.day,
            published_post.slug,
        ]
    )
    assert published_post.get_absolute_url() == expected_url

@pytest.mark.django_db
def test_get_absolute_url_builds_correct_path(published_post):
    """
    Verify that get_absolute_url() correctly constructs the URL path from the post's publication date and slug,
    without relying on Django's reverse() function.
    This test ensures the method passes the correct parameters in the expected order to reverse(), guarding
    against regressions where argument order or values might be changed incorrectly.
    """
    expected_url = f"/blog/{published_post.publication_date.year}/{published_post.publication_date.month}/{published_post.publication_date.day}/{published_post.slug}/"
    assert published_post.get_absolute_url() == expected_url