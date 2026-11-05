# Mini Blog API

A FastAPI service for publishing posts with authors and tags. Readers can search titles, browse paginated results, and find posts by tag. SQLAlchemy stores the data in SQLite for a quick local run or PostgreSQL for development.

## Project overview

A post can have one author and several tags. When two posts use the same author email or tag name, the API reuses the matching record. Readers can retrieve a full post, request just its ID and title, or find posts that share a tag.

## Project goals

- Build a complete publishing workflow from request validation through database storage to the HTTP response.
- Make the API easy to explore from a fresh checkout using SQLite and interactive documentation.
- Evolve the project in documented stages, starting with a modular layout and then adding database migrations and container support.

## Tech stack

| Technology | Role |
| --- | --- |
| Python 3.12 and FastAPI | Application runtime, HTTP routing, and interactive API documentation |
| Pydantic | Request validation and response schemas |
| SQLAlchemy | Relational models, queries, and database sessions |
| SQLite / PostgreSQL | Local file storage by default, or a PostgreSQL server using the Psycopg driver |
| python-dotenv | Load local database settings from an optional `.env` file |

## Requirements

Install Python 3.12 with pip and virtual environment support. Use Git to clone the repository, or download and extract its ZIP from GitHub. SQLite works out of the box with the standard Python distribution. For the PostgreSQL setup, you also need a running server, a database, and a role with access to its schema. Python dependency versions are listed in [requirements.txt](requirements.txt).

## Local installation

1. On the GitHub repository page, select **Code → HTTPS** and copy the clone URL.
2. Replace `YOUR_CLONE_URL` below with that URL. If you downloaded the ZIP, open a terminal in the extracted folder containing `main.py` and skip these two commands.

```shell
git clone YOUR_CLONE_URL mini-blog-api
cd mini-blog-api
```

3. Create a virtual environment, install the dependencies, and start the development server. On Windows, run:

```powershell
py -3.12 -m venv env
.\env\Scripts\python -m pip install -r requirements.txt
.\env\Scripts\fastapi dev main.py
```

On macOS or Linux, create the environment with `python3.12 -m venv env` and use `env/bin/python` and `env/bin/fastapi` for the next two commands.

With the default settings, the first startup creates `blog.db` in the working directory. Open [Swagger UI](http://127.0.0.1:8000/docs) to try the endpoints, or view the [OpenAPI schema](http://127.0.0.1:8000/openapi.json).

## Try it

In Swagger UI, expand **POST /posts**, select **Try it out**, paste the following body, and select **Execute**.

```json
{
  "title": "My first API post",
  "content": "Today I connected my blog to a database.",
  "author": {"name": "Alex", "email": "alex@example.com"},
  "tags": [{"name": "python"}, {"name": "fastapi"}]
}
```

A successful request returns **201** and the saved post, including its ID. Use that ID with **GET /posts/{post_id}**. Try [searching for the post](http://127.0.0.1:8000/posts?Search=first) or [filtering by tag](http://127.0.0.1:8000/post/by-tags?tags=python). Sending the example twice returns **409** because titles must be unique.

## Endpoints

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/` | Return the welcome message. |
| POST | `/posts` | Create a post. Authors are reused by email and tags by name. |
| GET | `/posts` | Search, sort, and paginate posts. The response includes `items`, totals, and previous/next page flags. |
| GET | `/posts/{post_id}` | Read one post. Set `include_content=false` to return only its ID and title. |
| PUT | `/posts/{post_id}` | Update the supplied title or content. Omitted fields keep their values. |
| DELETE | `/posts/{post_id}` | Delete a post and return **204**. |
| GET | `/post/by-tags` | Find posts matching any supplied tag. Repeat the parameter, e.g. `?tags=python&tags=fastapi`. |

**Listing posts.** Use `Search` (capital S, 3–50 characters) for a case-insensitive title search. The older `text` parameter is deprecated. Pages start at 1. The default page size is 10 and `per_page` accepts 1–50. Sort with `order_by=id|title` and `direction=asc|desc`; the default is ascending ID.

**Creating posts.** Supply a unique title of 3–100 characters and a `tags` array. Use `[]` for an untagged post. Each tag name is 2–20 characters. An author is optional and takes a name and email address. Supply 10–100 characters for content, or omit it to use the default. For updates, send a string for each field you want to change.

## Use PostgreSQL

Create a database and login role on your PostgreSQL server. In the repository root, create a local `.env` file using your own connection details:

```dotenv
DATABASE_URL=postgresql+psycopg://blog_user:your_password@localhost:5432/mini_blog
```

URL-encode special characters in the password. Restart the API after changing the connection. The application creates missing tables on startup, so the role needs permission to create tables in the target schema. If PostgreSQL reports “permission denied for schema public”, connect to **the target database** as the schema owner or administrator and grant the application role access:

```sql
GRANT USAGE, CREATE ON SCHEMA public TO blog_user;
```

The schema contains `posts`, `authors`, `tags`, and the `post_tags` association table. In DBeaver, connect to the database named in your URL and expand **Schemas → public → Tables** after starting the API. Local credentials, virtual environments, and SQLite database files are excluded by `.gitignore`.

## Current structure

```text
.
├── main.py            # Database setup, ORM models, validation, and HTTP routes
├── requirements.txt   # Python dependencies
├── .gitignore         # Local files excluded from version control
└── README.md          # Setup and API reference
```

## Current limitations

- The API is intended for local development. Anyone who can reach the server can create, update, or delete posts.
- Startup creates missing tables. Changing a model that maps to an existing table requires a separate schema change.
- Updates support title and content only. Authors and tags are assigned when creating a post.
- Requesting a page beyond the last page returns the last page's items, while the response echoes the requested page number.

## Next phase

The next milestone is to move database configuration, models, request schemas, and routes out of `main.py`. The refactor is complete when the existing post workflow still works through the documented endpoints and the installation instructions point to the new entry point.

| Status | Milestone |
| --- | --- |
| Implemented | Single-module API in `main.py` with persistent post CRUD, author and tag relationships, search, sorting, and pagination. |
| Planned | Split the application into modules for configuration, models, and API features. |
| Planned | Introduce Alembic migrations to track changes to existing database schemas. |
| Planned | Add Docker setup for running the project in containers. |

