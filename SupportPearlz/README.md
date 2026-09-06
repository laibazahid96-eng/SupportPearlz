# SupportPearlz

A small, production-shaped Flask application that lets a customer sign in
with their own OpenAI API key and ask support questions about Pearlz Home
Systems products (warranty, returns, shipping, installation, and safety).

This is the professional rebuild of the original beginner prototype. The
customer-facing flow is unchanged — sign in, then chat — but the
implementation has been restructured for security, maintainability, and
testability.

## What changed from the beginner version

| Area | Beginner version | This version |
|---|---|---|
| Structure | One `app.py` file | Application factory + blueprint + service layer |
| API key storage | Flask session (client-side cookie) | Server-side session (`Flask-Session`, filesystem backend) |
| Forms | Raw HTML, no CSRF protection | `Flask-WTF` forms with CSRF tokens and validation |
| Prompting | Entire knowledge file sent on every request | Lightweight keyword retrieval sends only the relevant section(s) |
| Model | Placeholder model name that does not exist | Real, configurable model (`gpt-4o-mini` by default) via `OPENAI_MODEL` |
| Abuse protection | None | Rate limiting on the chat endpoint (`Flask-Limiter`) |
| Secrets | Hard-coded `secret_key` in source | Read from environment variables (`.env`) |
| Errors | Raw exception text shown to the user | Friendly messages; details go to server logs only |
| Tests | None | `pytest` suite covering routes and retrieval |
| Deployment | Dev server only | `Dockerfile` + `gunicorn` for production |

## Project structure

```
SupportPearlz/
├── app/
│   ├── __init__.py            # application factory
│   ├── config.py               # environment-driven configuration
│   ├── extensions.py           # shared Flask extension instances
│   ├── forms.py                 # CSRF-protected WTForms
│   ├── routes.py                 # login / chat / logout / health routes
│   ├── services/
│   │   ├── knowledge.py          # knowledge base loading + retrieval
│   │   └── openai_client.py      # OpenAI API wrapper
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/chat.js
│   └── templates/
│       ├── base.html
│       ├── login.html
│       └── chat.html
├── data/
│   └── knowledge.txt            # editable knowledge base
├── tests/
│   ├── test_app.py
│   └── test_knowledge.py
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── run.py
└── README.md
```

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create your local environment file:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and set a real `SECRET_KEY` (see the comment in the
   file for how to generate one). Do **not** put an OpenAI API key in
   `.env` — customers enter their own key in the browser at sign-in.
4. Run the app:
   ```bash
   python run.py
   ```
5. Open `http://127.0.0.1:5000`.

## Running tests

```bash
pip install -r requirements-dev.txt
pytest
```

Tests monkeypatch the OpenAI calls, so no real API key or network access
is required to run the suite.

## How it works

1. **Sign in** (`/`) — the visitor enters an OpenAI API key. The key is
   verified with a lightweight OpenAI call, then stored in a server-side
   session (not a browser cookie), so it never round-trips to the client.
2. **Ask a question** (`/chat`) — the question is matched against the
   knowledge base (`data/knowledge.txt`) using keyword overlap, and only
   the one or two most relevant sections are sent to the model. This keeps
   the prompt small and keeps the assistant grounded in the actual
   knowledge base instead of the whole document every time.
3. **Answer** — the model is instructed to answer only from the supplied
   knowledge and to say plainly when it doesn't have the answer, rather
   than guessing.
4. **Log out** (`/logout`) — clears the server-side session immediately.

## Updating the knowledge base

Edit `data/knowledge.txt`. Keep the `SECTION NAME:` header format (an
all-caps line ending in a colon) so the retrieval logic in
`app/services/knowledge.py` can split it into sections. No code changes
are needed to add, remove, or edit sections.

## Security notes

- The OpenAI API key is never written to disk, logged, or embedded in
  source code. It lives only in the signed, server-side session for the
  duration of the visitor's browser session.
- `SECRET_KEY` must be set to a long random value in any real deployment;
  the default in `config.py` is intentionally insecure and only meant for
  first-time local testing.
- Set `FLASK_ENV=production` in production so session cookies are marked
  `Secure` (HTTPS-only).
- The `/chat` endpoint is rate-limited per visitor to reduce the impact of
  accidental or malicious request floods against the customer's own
  OpenAI quota.

## Deployment

A `Dockerfile` is included, running the app under `gunicorn`:

```bash
docker build -t supportpearlz .
docker run -p 8000:8000 --env-file .env supportpearlz
```

Put a reverse proxy (e.g. nginx, or your platform's built-in one) in
front of it for TLS termination.
