"""
Thin wrapper around the OpenAI SDK so the rest of the app never touches
the SDK directly. This keeps routes.py simple and makes the OpenAI calls
easy to unit test (see tests/test_app.py, which monkeypatches
`answer_question`).
"""
from __future__ import annotations

import logging

from openai import APIConnectionError, APIStatusError, AuthenticationError, OpenAI

from app.services.knowledge import KnowledgeBase, Section

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are SupportPearlz, a customer support assistant for Pearlz Home "
    "Systems. Answer ONLY using the knowledge provided below. Keep answers "
    "short, friendly, and specific. If the knowledge does not contain the "
    "answer, say exactly: \"I don't have that information in my knowledge "
    "base. Please contact our support team directly.\" Always end your "
    "answer with a line listing which knowledge section(s) you used, "
    "formatted as: Source: <section name(s)>."
)


class ApiKeyInvalidError(Exception):
    """Raised when the supplied OpenAI API key fails validation."""


def verify_api_key(api_key: str) -> None:
    """Raise ApiKeyInvalidError if the key is not usable."""
    try:
        client = OpenAI(api_key=api_key)
        client.models.list()
    except AuthenticationError as exc:
        raise ApiKeyInvalidError("The API key was rejected by OpenAI.") from exc
    except (APIConnectionError, APIStatusError) as exc:
        raise ApiKeyInvalidError(
            "Could not reach OpenAI to verify the key. Please try again."
        ) from exc


def answer_question(
    api_key: str,
    question: str,
    knowledge_base: KnowledgeBase,
    model: str,
    timeout: float = 20.0,
) -> str:
    """Ask the model to answer `question` grounded in the knowledge base."""
    relevant: list[Section] = knowledge_base.search(question, top_k=2)
    context = "\n\n".join(f"[{s.title}]\n{s.body}" for s in relevant)

    client = OpenAI(api_key=api_key, timeout=timeout)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Knowledge:\n{context}\n\nCustomer question:\n{question}",
                },
            ],
            temperature=0.2,
            max_tokens=400,
        )
        return response.choices[0].message.content.strip()
    except AuthenticationError:
        logger.warning("OpenAI rejected the API key during a chat request.")
        return (
            "Your API key was rejected by OpenAI. Please log out and sign "
            "in again with a valid key."
        )
    except (APIConnectionError, APIStatusError) as exc:
        logger.error("OpenAI request failed: %s", exc)
        return (
            "Sorry, I couldn't reach the support assistant right now. "
            "Please try again in a moment."
        )
