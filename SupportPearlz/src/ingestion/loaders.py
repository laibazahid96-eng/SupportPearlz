"""Heterogeneous document loading with metadata normalisation."""
from __future__ import annotations
import csv
import hashlib
import re
from pathlib import Path
from typing import Iterable
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

SUPPORTED = {".pdf", ".docx", ".md", ".txt", ".csv"}

def _clean(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def _base_metadata(path: Path) -> dict:
    stem = path.stem.lower()
    if "warranty" in stem or "refund" in stem or "shipping" in stem or "privacy" in stem:
        doc_type = "policy"
    elif "manual" in stem:
        doc_type = "manual"
    elif "troubleshooting" in stem or "installation" in stem:
        doc_type = "guide"
    elif "faq" in stem:
        doc_type = "faq"
    elif "pricing" in stem:
        doc_type = "pricing"
    elif "service" in stem:
        doc_type = "agreement"
    elif "handbook" in stem:
        doc_type = "handbook"
    elif "changelog" in stem:
        doc_type = "release_notes"
    else:
        doc_type = "notes"
    product_line = ""
    for p in ["AquaPearl 500 Pro", "AquaPearl 300", "AeroPearl Mini", "AquaPearl 100", "AeroPearl Classic"]:
        if p.lower().replace(" ", "") in stem.replace("_", ""):
            product_line = p
    return {"source": path.name, "doc_type": doc_type, "product_line": product_line}

def _load_csv(path: Path) -> list[Document]:
    docs=[]
    with path.open(newline="", encoding="utf-8") as f:
        for row_number, row in enumerate(csv.DictReader(f), start=2):
            text = " | ".join(f"{k}: {v}" for k,v in row.items())
            md = _base_metadata(path) | {"row": row_number, "sku": row.get("sku", ""), "product_line": row.get("product_line","")}
            docs.append(Document(page_content=text, metadata=md))
    return docs

def load_file(path: Path) -> list[Document]:
    suffix=path.suffix.lower()
    md=_base_metadata(path)
    if suffix == ".csv":
        return _load_csv(path)
    if suffix == ".pdf":
        raw=PyPDFLoader(str(path)).load()
    elif suffix == ".docx":
        raw=Docx2txtLoader(str(path)).load()
    elif suffix in {".md",".txt"}:
        raw=TextLoader(str(path), encoding="utf-8").load()
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
    result=[]
    for i, doc in enumerate(raw):
        text=_clean(doc.page_content)
        if not text:
            continue
        merged=dict(md)
        merged.update(doc.metadata)
        merged["source"]=path.name
        merged["doc_type"]=md["doc_type"]
        merged.setdefault("page", i+1)
        merged.setdefault("section", "")
        result.append(Document(page_content=text, metadata=merged))
    return result

def content_hash(doc: Document) -> str:
    return hashlib.sha256(doc.page_content.encode("utf-8")).hexdigest()

def load_directory(directory: Path, logger) -> tuple[list[Document], list[dict]]:
    found=loaded=skipped=0
    reports=[]
    unique=set()
    docs=[]
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED:
            continue
        found += 1
        try:
            loaded_docs=load_file(path)
            new=[]
            for d in loaded_docs:
                h=content_hash(d)
                if h not in unique:
                    unique.add(h); new.append(d)
            if not new:
                raise ValueError("duplicate content")
            docs.extend(new)
            reports.append({"source": path.name, "type": path.suffix.lower(), "characters": sum(len(x.page_content) for x in new), "sections": len(new), "metadata_keys": sorted(new[0].metadata)})
            loaded += 1
        except Exception as exc:
            skipped += 1
            logger.warning("Skipped file %s: %s", path.name, exc)
            reports.append({"source": path.name, "type": path.suffix.lower(), "error": str(exc)})
    logger.info("Ingestion summary | found=%s loaded=%s skipped=%s chunks_before_split=%s", found, loaded, skipped, len(docs))
    return docs, reports
