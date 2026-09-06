"""Central configuration for SupportPearlz."""
from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    llm_model: str
    embedding_model: str
    temperature: float
    vector_store_path: Path
    collection_name: str
    chunk_size: int
    chunk_overlap: int
    retrieval_k: int
    retrieval_threshold: float
    mmr_fetch_k: int
    max_context_chunks: int
    max_context_chars: int
    history_turns: int
    log_level: str
    log_file: Path

def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value or value == "your_api_key_here":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

def get_settings() -> Settings:
    return Settings(
        openai_api_key=_required("OPENAI_API_KEY"),
        llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        temperature=float(os.getenv("TEMPERATURE", "0")),
        vector_store_path=Path(os.getenv("VECTOR_STORE_PATH", "data/vector_store")),
        collection_name=os.getenv("COLLECTION_NAME", "supportpearlz"),
        chunk_size=int(os.getenv("CHUNK_SIZE", "800")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "120")),
        retrieval_k=int(os.getenv("RETRIEVAL_K", "4")),
        retrieval_threshold=float(os.getenv("RETRIEVAL_THRESHOLD", "0.55")),
        mmr_fetch_k=int(os.getenv("MMR_FETCH_K", "12")),
        max_context_chunks=int(os.getenv("MAX_CONTEXT_CHUNKS", "4")),
        max_context_chars=int(os.getenv("MAX_CONTEXT_CHARS", "12000")),
        history_turns=int(os.getenv("HISTORY_TURNS", "6")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=Path(os.getenv("LOG_FILE", "logs/supportpearlz.log")),
    )

if __name__ == "__main__":
    s = get_settings()
    print("SupportPearlz configuration")
    for k, v in s.__dict__.items():
        print(f"{k}: {'***masked***' if 'key' in k else v}")
