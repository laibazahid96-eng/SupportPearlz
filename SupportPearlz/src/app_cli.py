"""Interactive SupportPearlz CLI."""
from __future__ import annotations
from src.config import get_settings
from src.utils.logging_setup import configure_logging
from src.retrieval.vector_store import load_store
from src.chains.rag_chain import RAGChain

def main():
    settings=get_settings(); logger=configure_logging(settings)
    store=load_store(settings)
    rag=RAGChain(store,settings,logger)
    print(f"SupportPearlz | model={settings.llm_model} | collection={settings.collection_name}")
    print("Commands: /reset, /quit")
    while True:
        try: q=input("\nYou > ").strip()
        except (EOFError,KeyboardInterrupt): print("\nGoodbye."); break
        if not q: continue
        if q.lower() in {"/quit","/exit"}: break
        if q.lower()=="/reset":
            rag.memory.reset(); print("Session reset."); continue
        try:
            r=rag.invoke(q)
            print(f"Bot > {r.answer}")
            if r.sources:
                print("Sources:")
                for s in dict.fromkeys(r.sources): print(f"  - {s}")
            print(f"Confidence: {r.confidence.value}")
        except Exception as exc:
            logger.exception("CLI error")
            print(f"SupportPearlz could not complete that request: {exc}")
if __name__=="__main__":
    main()
