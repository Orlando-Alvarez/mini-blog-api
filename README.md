# Mini Blog API

A Python backend for publishing blog posts with authors and tags. Readers can search titles, browse paginated results, and filter posts by tag. Writers sign in with a demo account and use a short-lived JWT to create, update, or delete posts.

## Project overview

Each post has a unique title, content, an optional author, and a list of tags. Posts can share authors and tags. The API reuses authors by email and looks up existing tags by name when creating a post.

The application is organized by responsibility. FastAPI routers handle HTTP requests, Pydantic schemas define request and response data, and a repository handles post queries through SQLAlchemy. SQLite provides a quick local setup. PostgreSQL is available through the same database configuration.

## Project goals

- Build a complete publishing workflow with persistent storage, input validation, search, and pagination.
- Keep public reading endpoints accessible while requiring authentication for writes.
- Make each stage of development reproducible, from the initial CRUD API through modularization, authentication, and future database migrations.

## Tech stack

| Technology | Role |
| --- | --- |
| Python 3.12 and FastAPI | Application runtime, HTTP routes, and interactive documentation |
| Pydantic | Request validation and response models |
| SQLAlchemy | Database sessions, relational models, and queries |
| SQLite or PostgreSQL | Post, author, and tag storage |
| Psycopg | PostgreSQL driver |
| PyJWT | Signing and verifying HS256 access tokens |

## Requirements and local installation

Use Python 3.12, pip, and Git. SQLite is included with Python. PostgreSQL is optional.

**1. Clone the repository.** While JWT authentication is on its feature branch, use:

```shell
git clone --branch feature/jwt-auth https://github.com/Orlando-Alvarez/mini-blog-api.git
cd mini-blog-api
```

**2. Create a virtual environment and install dependencies.** The root [requirements.txt](requirements.txt) lists the runtime dependencies, including PyJWT and the form parser used by the login endpoint.

Windows PowerShell:

```powershell
py -3.12 -m venv env
.\env\Scripts\python -m pip install -r requirements.txt
```

macOS or Linux:

```bash
python3.12 -m venv env
env/bin/python -m pip install -r requirements.txt
```

**3. Set a signing key and start the API.** Run these commands from the repository root. The default SQLite configuration creates `blog.db` in the working directory.

Windows PowerShell:

```powershell
$env:SECRET_KEY = .\env\Scripts\python -c "import secrets; print(secrets.token_urlsafe(32))"
.\env\Scripts\fastapi dev app/main.py
```

macOS or Linux:

```bash
export SECRET_KEY="$(env/bin/python -c 'import secrets; print(secrets.token_urlsafe(32))')"
env/bin/fastapi dev app/main.py
```

Open [Swagger UI](http://127.0.0.1:8000/docs) to try the API, or inspect the [OpenAPI schema](http://127.0.0.1:8000/openapi.json). Generating a new signing key invalidates tokens issued with the previous key.

### Use PostgreSQL instead of SQLite

Create a PostgreSQL database and login role, then set `DATABASE_URL` in the same terminal **before** starting FastAPI. For example, in PowerShell:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://blog_user:YOUR_PASSWORD@localhost:5432/mini_blog"
```

Replace the example values with your local credentials and URL-encode special characters in the password. On macOS or Linux, set the same variable with `export DATABASE_URL="..."`. With the current import order, setting database and signing variables in the shell makes them available when the database engine and security module initialize.

The app creates missing tables on startup. If PostgreSQL reports `permission denied for schema public`, connect to the **target database** as its schema owner or administrator and grant the application role access:

```sql
GRANT USAGE, CREATE ON SCHEMA public TO blog_user;
```

The database contains `posts`, `authors`, `tags`, and `post_tags`. The last table connects posts to tags.

## Try the publishing workflow

1. Open Swagger UI and select **Authorize**. Use a demo account from `FAKE_USERS` in [the authentication router](app/api/v1/auth/router.py). The login endpoint accepts `username` and `password` as form fields and issues a bearer token valid for 30 minutes.
2. Call **GET `/api/v1/auth/me`** to check which identity the token represents.
3. Open **POST `/posts`**, select **Try it out**, and submit the example below.

```json
{
  "title": "My first API post",
  "content": "Today I published a post through the API.",
  "author": {"name": "Alex", "email": "alex@example.com"},
  "tags": [{"name": "python"}, {"name": "fastapi"}]
}
```

A successful request returns **201** and the post ID. Use that ID with **GET `/posts/{post_id}`**. You can also [search for the title](http://127.0.0.1:8000/posts?Search=first) or [filter by tag](http://127.0.0.1:8000/posts/by-tags?tags=python). When using an HTTP client outside Swagger, send `Authorization: Bearer <access_token>` on protected requests.

## Endpoints

| Method | Path | Access | Purpose |
| --- | --- | --- | --- |
| POST | `/api/v1/auth/login` | Demo credentials | Issue an access token. |
| GET | `/api/v1/auth/me` | Bearer token | Return the current username and email. |
| GET | `/posts` | Public | Search, sort, and paginate posts. |
| GET | `/posts/by-tags` | Public | Match any supplied tag, e.g. `?tags=python&tags=fastapi`. |
| GET | `/posts/{post_id}` | Public | Read a post. Use `include_content=false` for an ID and title summary. |
| POST | `/posts` | Bearer token | Create a post with an optional author and a required tags array. |
| PUT | `/posts/{post_id}` | Bearer token | Update the supplied title or content. |
| DELETE | `/posts/{post_id}` | Bearer token | Delete a post and return **204**. |

**Search and pagination.** `Search` is case-sensitive as a parameter name and performs a case-insensitive title search. It accepts 3–50 characters. The older `text` parameter is deprecated. Pages start at 1, `per_page` defaults to 10 and accepts 1–50, and results can be sorted by `id` or `title` in `asc` or `desc` order.

**Post creation.** Titles must be unique and contain 3–100 characters. Supply 10–100 characters for content, or omit it to use the default. Use `tags: []` for an untagged post. Each tag name accepts 2–20 characters.

## Current structure

```text
app/
├── main.py                 # Creates the application and registers the routers
├── core/
│   ├── db.py               # Engine, shared model base, and database sessions
│   └── security.py         # Token creation, decoding, and current-user dependency
├── models/
│   ├── __init__.py
│   ├── author.py
│   ├── post.py             # Post model and post_tags association table
│   └── tag.py
└── api/v1/
    ├── auth/
    │   ├── router.py       # Login and current-user routes
    │   └── schemas.py
    └── posts/
        ├── router.py       # HTTP endpoints
        ├── repository.py   # Queries and persistence operations
        └── schemas.py      # Post, author, tag, and pagination schemas
requirements.txt            # Runtime dependencies and versions
README.md
```

## Current limitations

- Authentication uses in-memory demo accounts with plaintext passwords. Any authenticated demo user can modify any post. The author attached to a post is separate from the identity that signs in.
- Invalid or expired tokens can produce a server error because the current exception handlers raise helper functions instead of calling them. The experimental `/posts/secure` route is also shadowed by `/posts/{post_id}`. Use `/api/v1/auth/me` to check a token.
- Startup creates missing tables. Changes to existing database schemas still require a separate migration step.
- Requesting a page beyond the last page returns the last page’s items while the response echoes the requested page number.

## Development milestones

| Status | Milestone |
| --- | --- |
| Implemented | Persistent post CRUD, author and tag relationships, search, sorting, and pagination. |
| Implemented | Modular layout for database configuration, models, request schemas, and repository queries. |
| Implemented on `feature/jwt-auth` | Demo login, JWT access tokens, a current-user endpoint, and authenticated post writes. |
| Planned | Alembic migrations for versioned schema changes. |
| Planned | Docker setup for reproducible local development. |
