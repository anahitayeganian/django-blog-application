# Django 5 Blog Application

A fully functional blog application built with Django 5.2 and Python 3.12 that demonstrates a range of practical features used in content publishing applications.

It includes PostgreSQL full-text search, tag-based navigation, Markdown rendering, RSS feed and sitemap support, a
customized admin interface, etc. The application was also migrated from SQLite to PostgreSQL using a Dockerized
container setup.

## ⚙️ Tech Stack

- **Backend:** Django 5.2, Python 3.12
- **Database:** SQLite, then migrated to PostgreSQL
- **ORM:** Django ORM
- **Frontend:** Django Templates, HTML, CSS
- **Admin Interface:** Django Admin (customized)
- **Dependencies:**
  - `python-decouple` – environment variable management
  - `django-taggit` – tag management
  - `markdown` – content formatting
  - `psycopg2-binary` – PostgreSQL adapter

<!--
## 📸 Screenshots

<Insert screenshots if available — e.g., admin interface, blog post list, post detail>
-->

## Core Features

### Blog Posts
- `Post` model with fields for title, slug, creation, publication, and modification timestamps, as well as publish/draft status
- Custom manager (`PublishedManager`) to separate published from draft content
- Unique slugs per date using unique_for_date to support clean, date-based URLs
- Pagination for post listings to improve navigability
- Post bodies written in Markdown, rendered as HTML using a custom template filter

### Tags and Related Content
- Integration with `django-taggit` for flexible tagging
- Tag-based filtering in post listings
- Similar posts recommendation based on tag overlap

### Comment System
- `Comment` model linked to posts via `ForeignKey`, ordered chronologically
- Moderation support via an `is_active` flag
- Admin filters and search on author name and content

### Admin Customization
- List filters, search fields, and slug prepopulation
- Date-based hierarchy for posts
- Filter sidebar customization

### Full-Text Search with PostgreSQL
- Basic full-text search with `SearchVector`
- Ranked results with `SearchRank`
- Weighted fields (e.g., title vs. body relevance)
- Fuzzy search using trigram similarity for typo-tolerant search

### SEO & Sharing
- Share posts via email with a dedicated form
- RSS feed for syndication
- Sitemap configuration for search engine indexing

### Database & Environment
- Initial development with SQLite
- Migrated to PostgreSQL running in a Docker container
- `.gitignore` configured to exclude SQLite DB, logs, secrets, IDE/project files, and compiled Python artifacts to protect sensitive data and avoid committing unnecessary files

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