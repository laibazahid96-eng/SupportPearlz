"""Retriever policies and relevance gate."""
from __future__ import annotations
from langchain_chroma import Chroma
from langchain_core.documents import Document
from src.config import Settings

def retrieve(store: Chroma, query: str, settings: Settings, strategy: str="similarity") -> list[tuple[Document,float]]:
    if strategy=="mmr":
        docs=store.max_marginal_relevance_search(query,k=settings.retrieval_k,fetch_k=settings.mmr_fetch_k)
        # Chroma MMR does not expose relevance scores; use a neutral display score.
        return [(d, 0.5) for d in docs]
    return store.similarity_search_with_relevance_scores(query,k=settings.retrieval_k)

def apply_gate(hits: list[tuple[Document,float]], threshold: float) -> tuple[list[tuple[Document,float]], bool]:
    relevant=[h for h in hits if h[1] >= threshold]
    return relevant, bool(relevant)

def format_hit(doc: Document, score: float) -> str:
    md=doc.metadata
    location=f"page={md.get('page')}" if md.get("page") else f"section={md.get('section','')}"
    if md.get("row"): location=f"row={md['row']} sku={md.get('sku','')}"
    return f"{md.get('source','unknown')} | {location} | score={score:.3f}\n{doc.page_content[:200]}"

def debug_search(store: Chroma, query: str, k: int, logger) -> None:
    for doc,score in similarity_search(store,query,k):
        print(format_hit(doc,score))
        logger.info("debug retrieval | source=%s score=%.4f chunk=%s",doc.metadata.get("source"),score,doc.metadata.get("chunk_id"))
