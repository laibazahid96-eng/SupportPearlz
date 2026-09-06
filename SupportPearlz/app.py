"""SupportPearlz application entry point.

The application uses the user's own OpenAI API key from a local .env file.
The key is never hard-coded in this source file and is never printed.

Run:
    python app.py

First build the local vector index:
    python -m src.ingestion.build_index --rebuild
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Make imports work when this file is launched directly with `python app.py`.
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv


def main() -> None:
    """Start the interactive SupportPearlz customer-support agent."""
    load_dotenv(ROOT / ".env")

    # Never put a real key in source code. The customer supplies their own key
    # in .env as OPENAI_API_KEY=sk-....
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or api_key == "your_api_key_here":
        print("\nSupportPearlz - OpenAI API key required")
        print("------------------------------------------------")
        print("1. Copy .env.example to .env")
        print("2. Open .env")
        print("3. Put YOUR OpenAI API key in OPENAI_API_KEY")
        print("   Example: OPENAI_API_KEY=sk-...   (do not share it with anyone)\n")
        raise SystemExit(1)

    from src.app_cli import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()
