"""Chunking strategies and experiment helpers."""
from __future__ import annotations
from pathlib import Path
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def recursive_chunks(documents: list[Document], chunk_size: int, chunk_overlap: int) -> list[Document]:
    splitter=RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=["\n\n","\n",". "," ",""])
    chunks=splitter.split_documents(documents)
    for i,c in enumerate(chunks):
        c.metadata["chunk_id"]=f"chunk-{i:05d}"
    return chunks

def structure_aware_markdown(documents: list[Document]) -> list[Document]:
    out=[]
    for doc in documents:
        if not doc.metadata["source"].lower().endswith(".md"):
            out.append(doc); continue
        sections=doc.page_content.split("\n## ")
        for idx, section in enumerate(sections):
            if section.strip():
                text=section if idx == 0 else "## "+section
                md=dict(doc.metadata); md["section"]=text.splitlines()[0][:120]
                out.append(Document(page_content=text.strip(), metadata=md))
    for i,c in enumerate(out): c.metadata["chunk_id"]=f"struct-{i:05d}"
    return out

def run_chunking_experiment(documents: list[Document], sample_questions: list[dict], output_path: Path) -> list[dict]:
    # Retrieval-independent experiment: answer-bearing source presence is approximated by source labels.
    configs=[(300,0),(300,60),(800,0),(800,120),(1500,0),(1500,225)]
    rows=[]
    expected=[q.get("ground_truth_source","").lower() for q in sample_questions]
    for size,overlap in configs:
        chunks=recursive_chunks(documents,size,overlap)
        hits=sum(any(e and e in c.metadata.get("source","").lower() for c in chunks) for e in expected)
        lengths=[len(c.page_content) for c in chunks]
        rows.append({"chunk_size":size,"overlap":overlap,"chunk_count":len(chunks),
                     "mean_length":round(sum(lengths)/len(lengths),1) if lengths else 0,
                     "max_length":max(lengths) if lengths else 0,
                     "sample_source_coverage":round(hits/max(len(expected),1),3)})
    output_path.parent.mkdir(parents=True,exist_ok=True)
    output_path.write_text(json.dumps(rows,indent=2),encoding="utf-8")
    return rows
