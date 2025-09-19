# Django 5 Blog Application

A fully-featured blog application built following the best practices for publishing platforms, including clickable tags to browse related posts, Markdown support for content formatting, RSS feeds, XML sitemap generation, SEO-friendly URLs, email sharing and full-text search to quickly find posts.

## ⚙️ Tech Stack

- **Backend:** Django 5.2, Python 3.12
- **Database:** SQLite, then migrated to PostgreSQL using a Docker container
- **Frontend:** Django Templates, HTML, CSS
- **Dependencies:**
  - `python-decouple` – manages environment variables
  - `django-taggit` – tagging system
  - `markdown` – supports content formatting
  - `psycopg2-binary` – PostgreSQL adapter

## 🎬 Demo
This video showcases the blog's main features, including creating posts, browsing tags, and managing content through the admin panel.

[Watch the demo](https://www.dropbox.com/scl/fi/mb7mvjzk04pd9wmxcsegy/blogapp-demo.mp4?rlkey=8250rovk8xapbbwclz6vhh743&st=myk87k6u&raw=1)

## Core Features

### Post Listing
- The homepage displays **all posts** in reverse chronological order, **with previews** showing the title, tags, publication date, author, and a short excerpt.
- **Pagination** ensures smooth navigation and prevents slow page loads.
- **Tags** are clickable, allowing readers to explore posts with the same tag.
- The **search bar** allows users to find posts by title or content, with typo-tolerant results.

### Individual Post View
- The page shows the **full content** of a post, allowing it to be shared via **email** with a custom message.
- A list of **recommended posts** is provided, ordered by the number of shared tags with the current post.
- **Comments** are displayed in chronological order, with the option to add new ones.

### Sidebar Navigation
The sidebar includes:
- The total **number of posts** on the blog.
- Links to the **latest posts** and the **most commented** ones to encourage further reading.
- An **RSS feed link** for readers to subscribe and stay updated with new content.

### Admin Panel
The administration interface is available to users with staff or superuser permissions. Depending on their role, they can:

#### Posts
- **Create** posts by specifying author, title, body (with Markdown rendering), publication date, status (draft or published), and tags.
- **View** all posts, ordered by publication date.
- **Filter** posts by author, status, or date, and **search** by title or body.
- **Edit** or **delete** posts as needed.

#### Comments
- **View** comments, displaying commenter name, email, related post, creation date, and visibility.
- **Hide** comments without deleting them.
- **Filter** by visibility or date, and **search** by commenter name, email, or content.

#### Users
- **View, filter, and search** the user list by account status (active, staff, or superuser), first and last name, username, or email.
- **Edit** user details, including username, email, account status.
- **Assign** permissions to staff users, selecting from available model-level permissions (e.g., Can add post, Can change comment, Can delete user).
- **Delete** users when necessary.

## Implementation Details

### Models
The application's data layer is built around `Post` and `Comment`, supported by Django's built-in authentication models, along with `Tag` and `TaggedItem` from `django-taggit`.
In addition to these models, Django automatically creates several internal tables (e.g., for migrations, sessions, content types, and sites).

#### Post
- **Custom manager:** `PublishedManager` returns only published posts, simplifying queries.
- **Status field with** `TextChoices`**:** restricts values to DRAFT or PUBLISHED, ensuring consistency.
- **Unique slug per publication date:** prevents URL collisions when posts share the same title.
- **Index on** `publication_date`**:** speeds up chronological queries, including listings, archives, and sorting by date.
- **Tagging via** `django-taggit`**:** enables flexible categorization and tag-based navigation.
- **Author relation:** `ForeignKey` to `settings.AUTH_USER_MODEL` with `on_delete=models.CASCADE`, ensuring posts are tied to user accounts.
- `get_absolute_url()`**:** generates canonical links to posts, keeping code that references post URLs accurate even if the URL structure changes.

#### Comment
- **Post relation:** `ForeignKey` with `related_name='comments'` for reverse lookups.
- **Soft moderation flag:** `is_visible` hides comments without deleting them.
- **Index on** `created_at`**:** optimizes filtering and sorting by creation date.

### Views and URL Mapping
- `post_list` **⟵** `/blog/`, `/blog/tag/<tag_slug>/`

  Retrieves all published posts, optionally filtered by a tag when its link is clicked.
  The view uses the `paginate_queryset` service to handle pagination and edge cases, then passes the results to the `list.html` template for rendering, where each post's title is displayed as a clickable link using `get_absolute_url`, directing the user to the corresponding `post_detail` view.

- `post_detail` **⟵** `/blog/<year>/<month>/<day>/<slug>/`

  Retrieves a single published post by slug and publication date, along with all visible comments.
  It initializes an empty `CommentForm` for new submissions and computes up to four similar posts based on the number of shared tags.
  All of this data is passed to the `detail.html` template, which also includes a link to the `post_share` URL, enabling users to share the post via email.
  
- `post_share` **⟵** `/blog/<post_id>/share/`
  
  Handles the sharing of a published post via email.
  The view retrieves the post by ID and uses `EmailPostForm` to validate the sender and recipient information, after it delegates the actual sending to the `send_post_recommendation_email` service.
  The view passes the post, form, and a status flag to the `share.html` template, which displays either the form or a confirmation message when the email has been successfully sent.
  
- `post_comment` **⟵** `/blog/<post_id>/comment/`

  Processes new comment submissions via `CommentForm`.
  Once the form is validated, the comment is associated with the corresponding post and saved to the database.
  The view then renders the `comment.html` template, which confirms the submission and provides a link back to the post detail page, or re-displays the form with validation errors if the submission is invalid.
  
- `post_search` **⟵** `/blog/search/`

  Handles search requests submitted via `SearchForm`.
  The input query is validated and passed to the appropriate search function (basic, ranked, weighted, or trigram), each implementing a different PostgreSQL full-text search strategy.
  Results are paginated through `paginate_queryset` and rendered in the `list.html` template, where the query and the number of matches are displayed above the results.
  Each matching post is listed with its title linked via `get_absolute_url` to the corresponding `post_detail` view.
  - Basic: full-text search on the post title and body without ranking.
  - Ranked: orders results by relevance score.
  - Weighted: prioritizes title matches and filters out results below a rank threshold.
  - Trigram: allows typo-tolerant fuzzy matching based on the post title.

### Services
- `paginate_queryset`**:** reusable pagination logic that handles invalid or out-of-range requests gracefully.
- `send_post_recommendation_email`**:** reusable email functionality that keeps mailing logic separate from the views.

### Forms
- `EmailPostForm`**:** validates recipient and sender information before sending emails.
- `CommentForm`**:** ensures comment submissions are valid before associating them with posts.
- `SearchForm`**:** sanitizes user search input before passing it to search functions.

### Admin Interface
**Django Admin** provides a web interface for staff users to manage blog content, including posts, tags, comments, and users.
- `@admin.register(Model)`**:** registers a model with the Django admin site.
- `ModelAdmin` **subclasses:** customize the admin interface for each model by defining filters, search fields, and ordering

### Templates and Styling
- **Frontend structure:** uses Django template inheritance to reduce duplication through `base.html` and reusable layouts.
- **Custom template tags:** generate dynamic content for templates, allowing reusable logic across multiple pages without changing views.
  - `total_posts` – shows blog size.
  - `show_latest_posts` – highlights recent content.
  - `get_most_commented_posts` – shows the most popular posts.
  - `markdown` – converts Markdown text to HTML for display in templates.
- **CSS styling:** `blog.css` defines layout, styles forms and search elements, and formats comment sections.

### RSS Feeds and Sitemap
- `LatestPostsFeed`**:** generates an RSS feed with truncated Markdown previews for feed readers.
- `PostSitemap`**:** creates an XML sitemap of all published posts, helping search engines discover content, track changes, and improve SEO.

### Database
- **SQLite (development):** chosen for its lightweight, file-based design, making it ideal for local testing and rapid prototyping.
- **PostgreSQL (production):** chosen for deployment due to its support for advanced full-text search, concurrent connections, and greater scalability compared to SQLite.
- **Django ORM:** manages database operations through Python objects, working seamlessly with both SQLite and PostgreSQL.
- `psycopg2-binary`**:** database adapter that connects Django's ORM to the PostgreSQL server, enabling queries and data manipulation.

#### Database Migration Steps
1. Run PostgreSQL with Docker:
   ```bash
   docker run --name=blog_db \
     -e POSTGRES_DB=blog \
     -e POSTGRES_USER=blog \
     -e POSTGRES_PASSWORD=xxx \
     -p 5432:5432 \
     -d postgres:16.3
   ```
2. Install database adapter:
   ```bash
   py -m pip install psycopg2-binary
   ```
3. Export SQLite data:
   ```bash
   cd mysite
   py -Xutf8 manage.py dumpdata \
     --exclude=contenttypes \
     --exclude=auth.permission \
     --indent=2 \
     --output=data.json
   ```
   Note: `contenttypes` and `auth.permission` are excluded because they are auto-managed by Django migrations.
   Including them could cause duplication and integrity errors when loading into PostgreSQL.
4. Update `DATABASES` settings:

   Modify the `DATABASES` configuration in `settings.py` to use `django.db.backends.postgresql`.
   Database credentials (name, user, password, host) are stored in the `.env` file and read via `python-decouple`.
5. Apply migrations:
   ```bash
   py manage.py migrate
   ```
6. Load data into PostgreSQL:
   ```bash
   py manage.py loaddata data.json
   ```

### Environment
- `.gitignore`**:** excludes DB files, logs, secrets, and build artifacts to keep the repository clean and secure.
- **Environment variables (**`.env`**),** `python-decouple`**, and** `settings.py`**:** configuration values such as database credentials and email settings are stored in a `.env` file and injected into Django's `settings.py` using `python-decouple`.
This prevents hard-coding sensitive data in the codebase and allows different configurations for development, testing, and production.

### Routing
- `mysite/urls.py`**:**
  - Redirects the root URL `/` to the blog homepage at `/blog/`.
  - Provides access to the Django admin interface at `/admin/`.
  - Includes all URL patterns from the blog app under `/blog/`.
  - Serves the XML sitemap at `/sitemap.xml` (powered by `PostSitemap`) to expose all blog post URLs to search engines.
- `blog/urls.py`**:**
  - Maps all blog-related URLs to their corresponding views.
  - Uses `app_name = 'blog'` for scoped URL reversing.

### Testing
- `pytest` **tests:** cover core application functionality to ensure the application works as expected and maintain code quality.
- `pytest.ini`**:** defines test discovery rules and sets `DJANGO_SETTINGS_MODULE` to `mysite.settings`.
- `settings.py` **test database:** configured a dedicated `TEST_DB_NAME` to isolate tests from development and production data.

<!--
### Future Enhancements
- JWT-based authentication for comment authors and send email
- RESTful API endpoints (Django REST Framework)
- Unit testing with pytest and coverage reports
- Image upload support in posts
- Rich text editor to write posts' bodies
- REST API for frontend decoupling
- CI/CD setup and deployment to cloud platform (e.g., Heroku, Railway, Fly.io)
-->