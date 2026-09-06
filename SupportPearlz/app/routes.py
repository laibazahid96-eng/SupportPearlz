import logging

from flask import Blueprint, current_app, redirect, render_template, session, url_for

from app.extensions import limiter
from app.forms import LoginForm, QuestionForm
from app.services.openai_client import ApiKeyInvalidError, answer_question, verify_api_key

logger = logging.getLogger(__name__)

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET", "POST"])
def login():
    if session.get("authenticated"):
        return redirect(url_for("main.chat"))

    form = LoginForm()
    error = None

    if form.validate_on_submit():
        api_key = form.api_key.data.strip()
        try:
            verify_api_key(api_key)
        except ApiKeyInvalidError as exc:
            error = str(exc)
        else:
            # The key is stored server-side only (filesystem session
            # backend), never in the browser-visible cookie.
            session.clear()
            session["api_key"] = api_key
            session["authenticated"] = True
            return redirect(url_for("main.chat"))

    return render_template("login.html", form=form, error=error)


@bp.route("/chat", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config["RATELIMIT_CHAT"])
def chat():
    if not session.get("authenticated"):
        return redirect(url_for("main.login"))

    form = QuestionForm()
    answer = None

    if form.validate_on_submit():
        knowledge_base = current_app.extensions["knowledge_base"]
        answer = answer_question(
            api_key=session["api_key"],
            question=form.question.data.strip(),
            knowledge_base=knowledge_base,
            model=current_app.config["OPENAI_MODEL"],
            timeout=current_app.config["OPENAI_TIMEOUT_SECONDS"],
        )

    return render_template("chat.html", form=form, answer=answer)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.route("/healthz")
def healthz():
    """Lightweight endpoint for uptime checks / container orchestrators."""
    return {"status": "ok"}, 200
