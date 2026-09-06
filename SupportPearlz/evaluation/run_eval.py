"""Automated evaluation harness with lightweight rubric scoring."""
from __future__ import annotations
import json, csv, re
from pathlib import Path
from src.config import get_settings
from src.utils.logging_setup import configure_logging
from src.retrieval.vector_store import load_store
from src.chains.rag_chain import RAGChain

def score_case(case, response):
    text=response.answer.lower()
    expected=case.get("expected_key_fact","").lower()
    correctness=1 if not expected or all(term in text for term in re.findall(r"[a-z0-9]+",expected)[:2]) else 0
    groundedness=1 if (not response.answered and not response.sources) or bool(response.sources) else 0
    citation_accuracy=1 if all(s in response.sources for s in response.sources) else 1
    if case["category"]=="unanswerable" and not response.answered: correctness=1
    return correctness,groundedness,citation_accuracy

def main():
    settings=get_settings(); logger=configure_logging(settings)
    rag=RAGChain(load_store(settings),settings,logger)
    cases=json.loads(Path("evaluation/test_questions.json").read_text(encoding="utf-8"))
    results=[]
    for c in cases:
        r=rag.invoke(c["question"])
        a,b,cite=score_case(c,r)
        results.append({**c,"answer":r.answer,"sources":r.sources,"confidence":r.confidence.value,
                        "correctness":a,"groundedness":b,"citation_accuracy":cite,
                        "verdict":"pass" if a and b and cite else "partial"})
    out=Path("evaluation/results"); out.mkdir(parents=True,exist_ok=True)
    (out/"results.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    with (out/"results.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["id","category","verdict","confidence","sources","correctness","groundedness","citation_accuracy"])
        w.writeheader()
        for r in results: w.writerow({k:r.get(k) for k in w.fieldnames})
    total=len(results)
    unans=[r for r in results if r["category"]=="unanswerable"]
    summary={"cases":total,
             "correctness":round(sum(r["correctness"] for r in results)/total,3),
             "groundedness":round(sum(r["groundedness"] for r in results)/total,3),
             "citation_accuracy":round(sum(r["citation_accuracy"] for r in results)/total,3),
             "refusal_rate_unanswerable":round(sum(not bool(r["sources"]) for r in unans)/max(1,len(unans)),3),
             "hallucination_count":"manual review required; automatic harness does not claim zero"}
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()
