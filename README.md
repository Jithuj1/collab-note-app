# CollabNotes

## Overview
- This is a simple collaborative note-taking application built with Django and Django REST Framework.
- It allows users to create, edit, and delete notes.
- It allows users to collaborate on notes with other users.
- It allows users to view history, search, filter, and sort notes.
- Frontend is not implemented using the django templates and is built using vanilla JavaScript.
- Some APIs build using the DRF
- For real-time collaboration, channels and websockets are used.
- Redis used to handle caching and message broker.
- Custom pagination is used to paginate the API responses.
  - check `utils/paginator.py` for more details.
- Custom Abstract Base Model is used to inherit the common fields and methods for the models.
  - check `utils/models.py` for more details.
  

## Project structure
- `collabnotes/` - root directory
- `collabnotes/collabnotes/` - django project
- `collabnotes/iam/` - authentication and authorization
- `collabnotes/note/` - note management
- `collabnotes/templates/` - templates

## Environment variables
- `ENVIRONMENT` - environment variable to set the environment (development or production)
- `SECRET_KEY` - secret key for the project
- `DEBUG` - debug mode for the project
- `ALLOWED_ORIGINS` - allowed origins for the project
- `ALLOWED_HOSTS` - allowed hosts for the project
- `CACHE_TIMEOUT` - cache timeout for the project
- `ACCESS_TOKEN_LIFETIME` - access token lifetime for the project
- `REFRESH_TOKEN_LIFETIME` - refresh token lifetime for the project
- `PAGINATION_PAGE_SIZE` - pagination page size for the project

## User Management
- Django default user model is not used.
- Custom user model is used with email as the username.
- Created custom management command to create users from the CLI.
- Use admin panel to manage users.

## Authentication

- Authentication is handled using JWT (JSON Web Tokens).
- Users authenticate using their email and password to obtain JWT tokens.
- The authentication endpoint returns an access token and a refresh token.
- Both tokens should be stored securely on the client side and used as required.
- The tokens are not compatible with the default djangorestframework-simplejwt; a custom implementation is used.
- The payload of the tokens includes only strictly necessary user information, typically the user ID.

### Obtain Token

Example request to obtain access and refresh tokens:

```bash
curl --location 'http://127.0.0.1:8000/api/v1/iam/auth/login/' \
  --header 'Content-Type: application/json' \
  --data-raw '{
    "email": "user@example.com",
    "password": "yourpassword"
}'
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xyz...",
  "user": {
    "id": "a008ea88-ae63-4ca3-ac0b-5cb586ffe232",
    "email": "user@example.com",
    "first_name": "User",
    "last_name": "Example"
  }
}
```

### Refresh Token

Example request to obtain a new access token using a refresh token:

```bash
curl --location 'http://127.0.0.1:8000/api/v1/iam/auth/refresh/' \
  --header 'Content-Type: application/json' \
  --data-raw '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xyz..."
}'
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc..."
}
```

**Notes:**
- Tokens use `access_token` and `refresh_token` as JSON keys.
- Endpoints use `/auth/login/` and `/auth/refresh/` instead of the default `/token/` and `/token/refresh/`.
- Always send tokens in the `Authorization: Bearer <access_token>` header for authenticated endpoints.

## Caching
- caching is implemented using redis
- caching is implemented for the following endpoints:
  - `api/v1/iam/users/`
  - `api/v1/note/collab-notes/<note_id>/`
- cache timeout is based on the environment variable `CACHE_TIMEOUT` in the `.env` file.
- every view cache key is based on the endpoint and the query parameters.

## Real-time collaboration
- real-time collaboration is implemented using channels and websockets.
- channels are used to send messages to the clients.
- websockets are used to send messages to the clients.
- channels are used to send messages to the clients.
- redis is used to handle the message broker.