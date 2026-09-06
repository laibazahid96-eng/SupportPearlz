"""CLI for offline index building."""
from __future__ import annotations
import argparse, json, shutil
from pathlib import Path
from src.config import get_settings
from src.utils.logging_setup import configure_logging
from src.ingestion.loaders import load_directory
from src.ingestion.chunking import recursive_chunks, structure_aware_markdown

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--rebuild",action="store_true")
    parser.add_argument("--knowledge-base",default="data/knowledge_base")
    args=parser.parse_args()
    settings=get_settings(); logger=configure_logging(settings)
    if args.rebuild and settings.vector_store_path.exists():
        shutil.rmtree(settings.vector_store_path)
        logger.info("Removed existing vector store for rebuild")
    from src.retrieval.vector_store import create_store
    documents,reports=load_directory(Path(args.knowledge_base),logger)
    chunks=recursive_chunks(documents,settings.chunk_size,settings.chunk_overlap)
    # CSV rows are already row-wise; markdown remains recursively chunked for consistent indexing.
    create_store(chunks,settings,logger)
    Path("evaluation/results").mkdir(parents=True,exist_ok=True)
    Path("evaluation/results/ingestion_report.json").write_text(json.dumps(reports,indent=2),encoding="utf-8")
    logger.info("Index build complete | documents=%s chunks=%s",len(documents),len(chunks))
if __name__=="__main__":
    main()
