"""Persistent Chroma vector store."""
from __future__ import annotations
from pathlib import Path
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from src.config import Settings

def embeddings(settings: Settings) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)

def create_store(chunks: list[Document], settings: Settings, logger) -> Chroma:
    settings.vector_store_path.mkdir(parents=True, exist_ok=True)
    store=Chroma(collection_name=settings.collection_name, persist_directory=str(settings.vector_store_path),
                 embedding_function=embeddings(settings))
    if chunks:
        store.add_documents(chunks, ids=[c.metadata["chunk_id"] for c in chunks])
    logger.info("Vector store built at %s with %s chunks", settings.vector_store_path, len(chunks))
    return store

def load_store(settings: Settings) -> Chroma:
    if not settings.vector_store_path.exists():
        raise FileNotFoundError(f"Vector store not found at {settings.vector_store_path}. Run the index build first.")
    return Chroma(collection_name=settings.collection_name, persist_directory=str(settings.vector_store_path),
                  embedding_function=embeddings(settings))

def similarity_search(store: Chroma, query: str, k: int) -> list[tuple[Document,float]]:
    return store.similarity_search_with_relevance_scores(query,k=k)
