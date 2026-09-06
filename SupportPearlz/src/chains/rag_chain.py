"""Composable RAG chain with relevance gate and citation validation."""
from __future__ import annotations
import time
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from src.config import Settings
from src.retrieval.retriever import retrieve, apply_gate
from src.chains.schemas import GroundedResponse, Confidence
from src.chains.prompts import answer_prompt
from src.chains.memory import ConversationMemory

class RAGChain:
    def __init__(self, store, settings: Settings, logger):
        self.store=store; self.settings=settings; self.logger=logger
        self.memory=ConversationMemory(settings,logger)
        self.model=ChatOpenAI(model=settings.llm_model,temperature=settings.temperature,api_key=settings.openai_api_key)
        self.structured=self.model.with_structured_output(GroundedResponse)
        self.prompt=answer_prompt()
        self.generation_chain=self.prompt | self.structured
        self.pipeline=RunnableLambda(self._run)

    def _context(self, hits):
        labels=[]; blocks=[]; total=0
        for i,(doc,score) in enumerate(hits[:self.settings.max_context_chunks],1):
            label=f"S{i}"
            md=doc.metadata
            loc=f"page {md.get('page')}" if md.get('page') else (f"row {md.get('row')}" if md.get('row') else md.get('section',''))
            block=f"[{label}] source={md.get('source')} location={loc} score={score:.3f}\n{doc.page_content}"
            if total+len(block)>self.settings.max_context_chars:
                self.logger.warning("context truncated at %s chars",self.settings.max_context_chars)
                break
            blocks.append(block); labels.append(label); total+=len(block)
        return "\n\n---\n\n".join(blocks), labels

    def _run(self, inputs):
        start=time.perf_counter()
        question=inputs["question"]
        standalone=self.memory.condense(question)
        raw=retrieve(self.store,standalone,self.settings,inputs.get("strategy","similarity"))
        hits,passed=apply_gate(raw,self.settings.retrieval_threshold)
        self.logger.info("retrieval | query=%r | rewritten=%r | hits=%s | scores=%s | refusal=%s",
                         question,standalone,[d.metadata.get("chunk_id") for d,_ in hits],[round(s,4) for _,s in hits],not passed)
        if not passed:
            response=GroundedResponse(answer="I could not find supporting information for that in the Pearlz documentation. Please contact human support for confirmation.",
                                      sources=[],confidence=Confidence.none,answered=False,used_context_labels=[])
        else:
            context,labels=self._context(hits)
            try:
                response=self.generation_chain.invoke({"context":context,"question":standalone})
            except Exception as exc:
                self.logger.exception("generation failed")
                response=GroundedResponse(answer="I could not complete that request because the support model is temporarily unavailable. Please try again or contact human support.",
                                          sources=[],confidence=Confidence.none,answered=False,used_context_labels=[])
            valid=set(labels)
            claimed=[x for x in response.used_context_labels if x in valid]
            response.used_context_labels=claimed
            # Only render source labels that the model actually claimed.
            label_to_source={f"S{i+1}": d.metadata.get("source","unknown") for i,(d,_) in enumerate(hits[:len(labels)])}
            response.sources=[label_to_source[x] for x in claimed]
            if any(x not in valid for x in response.used_context_labels):
                response.confidence=Confidence.partial
        self.memory.add("user",question)
        self.memory.add("assistant",response.answer)
        latency=(time.perf_counter()-start)*1000
        self.logger.info("turn complete | latency_ms=%.1f | answered=%s | confidence=%s",latency,response.answered,response.confidence.value)
        return response

    def invoke(self, question:str, strategy:str="similarity")->GroundedResponse:
        return self.pipeline.invoke({"question":question,"strategy":strategy})
