import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from .models import Post

class LatestPostsFeed(Feed):
    """
    RSS feed for the latest published blog posts.
    Each feed entry includes the post title, a truncated HTML preview of the post body, and the publication date.
    """
    title = 'My blog'
    link = reverse_lazy('blog:post_list')
    description = 'New posts of my blog.'

    def items(self):
        """
        Retrieve the latest five published posts.

        Returns:
            QuerySet[Post]: Up to five most recent published Post instances.
        """
        return Post.published.all()[:5]

    def item_title(self, item):
        """
        Get the title of the given blog post.

        Args:
            item (Post): A blog post instance.

        Returns:
            str: The title of the blog post.
        """
        return item.title

    def item_description(self, item):
        """
        Convert the post body from Markdown to HTML and truncate it to 30 words.

        Args:
            item (Post): A blog post instance.

        Returns:
            str: An HTML string containing a truncated preview of the post's body.
        """
        return truncatewords_html(markdown.markdown(item.body), 30)

    def item_pubdate(self, item):
        """
        Get the publication date of the post.

        Args:
            item (Post): A blog post instance.

        Returns:
            datetime.datetime: The publication date.
        """
        return item.publication_date

    def item_link(self, item):
        """
        Get the absolute URL to the post's detail page.

        Args:
            item (Post): A blog post instance.

        Returns:
            str: The URL pointing to the post's detail page
        """
        return item.get_absolute_url()