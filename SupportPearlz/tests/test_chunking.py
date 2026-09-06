from langchain_core.documents import Document
from src.ingestion.chunking import recursive_chunks
def test_metadata_survives():
    docs=[Document(page_content="a "*500,metadata={"source":"x.md","doc_type":"policy"})]
    chunks=recursive_chunks(docs,100,10)
    assert chunks and all(c.metadata["source"]=="x.md" for c in chunks)
