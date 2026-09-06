# SupportPearlz (Streamlit edition)

The same SupportPearlz customer-support assistant, rebuilt as a single
Streamlit app. No Flask, no server config — one command runs it.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will open `http://localhost:8501` in your browser automatically.

## How it works

1. **Sign in** — enter your own OpenAI API key. It's verified once with a
   lightweight OpenAI call, then kept only in Streamlit's in-memory
   session state for your browser tab — never written to disk.
2. **Ask a question** — your question is matched against
   `data/knowledge.txt` using keyword overlap (`knowledge.py`), and only
   the most relevant section(s) are sent to the model, keeping answers
   grounded and prompts small.
3. **Answer** — the model answers only from the supplied knowledge, and
   says plainly when it doesn't know rather than guessing.
4. **Log out** — clears your key and chat history from the session.

A simple per-session rate limit (10 questions/minute) protects against
accidental floods against your own OpenAI quota.

## Project files

```
SupportPearlz_Streamlit/
├── app.py                 # Streamlit UI — run this
├── knowledge.py            # knowledge base loading + keyword retrieval
├── openai_helper.py         # OpenAI API wrapper (verify key, ask question)
├── data/knowledge.txt        # editable knowledge base
├── .streamlit/config.toml    # brand theme colors
└── requirements.txt
```

## Updating the knowledge base

Edit `data/knowledge.txt`. Keep the `SECTION NAME:` header format (an
all-caps line ending in a colon) — no code changes are needed to add,
remove, or edit sections.

## Notes

- This is a local/demo-friendly setup. If you deploy it (e.g. Streamlit
  Community Cloud), each visitor still enters their own OpenAI key —
  the app never bundles one.
- To change the model, edit `OPENAI_MODEL` near the top of `app.py`.
