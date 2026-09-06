from app.services import openai_client


def test_login_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Sign in" in response.data


def test_chat_redirects_when_not_authenticated(client):
    response = client.get("/chat", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_success_redirects_to_chat(client, monkeypatch):
    monkeypatch.setattr(openai_client, "verify_api_key", lambda api_key: None)

    response = client.post(
        "/", data={"api_key": "sk-test-123"}, follow_redirects=False
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/chat")


def test_login_failure_shows_error(client, monkeypatch):
    def _raise(api_key):
        raise openai_client.ApiKeyInvalidError("The API key was rejected by OpenAI.")

    monkeypatch.setattr(openai_client, "verify_api_key", _raise)

    response = client.post("/", data={"api_key": "sk-bad"})
    assert response.status_code == 200
    assert b"rejected" in response.data


def test_chat_returns_answer_when_authenticated(client, monkeypatch):
    monkeypatch.setattr(openai_client, "verify_api_key", lambda api_key: None)
    monkeypatch.setattr(
        "app.routes.answer_question",
        lambda **kwargs: "The warranty lasts 2 years.\nSource: WARRANTY",
    )

    client.post("/", data={"api_key": "sk-test-123"})
    response = client.post("/chat", data={"question": "How long is the warranty?"})

    assert response.status_code == 200
    assert b"The warranty lasts 2 years." in response.data


def test_logout_clears_session(client, monkeypatch):
    monkeypatch.setattr(openai_client, "verify_api_key", lambda api_key: None)
    client.post("/", data={"api_key": "sk-test-123"})

    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302

    chat_response = client.get("/chat", follow_redirects=False)
    assert chat_response.status_code == 302


def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
