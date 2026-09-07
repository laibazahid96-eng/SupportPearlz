"""
Thin wrapper around the OpenAI SDK, kept separate from app.py so the
Streamlit UI code stays readable and this part is easy to unit test.
"""
from __future__ import annotations

from openai import APIConnectionError, APIStatusError, AuthenticationError, OpenAI

from knowledge import KnowledgeBase

SYSTEM_PROMPT = (
    "You are SupportPearlz, a customer support assistant for Pearlz Home "
    "Systems. Answer ONLY using the knowledge provided below. Keep answers "
    "short, friendly, and specific. If the knowledge does not contain the "
    "answer, say exactly: \"I don't have that information in my knowledge "
    "base. Please contact our support team directly.\" Always end your "
    "answer with a line formatted as: Source: <section name(s)>."
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
    model: str = "gpt-4o-mini",
    timeout: float = 20.0,
) -> str:
    """Ask the model to answer `question` grounded in the knowledge base."""
    relevant = knowledge_base.search(question, top_k=2)
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
        return (
            "Your API key was rejected by OpenAI. Please log out and sign "
            "in again with a valid key."
        )
    except (APIConnectionError, APIStatusError) as exc:
        return f"Sorry, I couldn't reach the support assistant right now. ({exc})"
