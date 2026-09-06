"""
Local development entry point.

Usage:
    python run.py

For production, use a WSGI server instead, e.g.:
    gunicorn "app:create_app()"
"""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    debug = os.environ.get("FLASK_ENV", "development") != "production"
    # use_reloader=False avoids "signal only works in main thread" errors,
    # which some Windows terminals/IDEs trigger because Werkzeug's
    # auto-reload feature registers a SIGTERM handler that requires
    # running in the interpreter's main thread. You lose auto-restart on
    # code changes, but the app still runs fine -- just restart it
    # manually after editing code.
    app.run(
        debug=debug,
        use_reloader=False,
        host="127.0.0.1",
        port=int(os.environ.get("PORT", 5000)),
    )
