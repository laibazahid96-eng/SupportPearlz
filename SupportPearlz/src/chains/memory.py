"""Bounded conversational history and query condensation."""
from __future__ import annotations
from langchain_openai import ChatOpenAI
from src.config import Settings
from src.chains.prompts import condensation_prompt

class ConversationMemory:
    def __init__(self, settings: Settings, logger):
        self.settings=settings
        self.logger=logger
        self.messages:list[tuple[str,str]]=[]

    def reset(self) -> None:
        self.messages=[]

    def add(self, role:str, content:str) -> None:
        self.messages.append((role,content))
        max_messages=self.settings.history_turns*2
        self.messages=self.messages[-max_messages:]

    def history_text(self)->str:
        return "\n".join(f"{r}: {c}" for r,c in self.messages)

    def condense(self, question:str)->str:
        if not self.messages:
            return question
        model=ChatOpenAI(model=self.settings.llm_model,temperature=0,api_key=self.settings.openai_api_key)
        chain=condensation_prompt() | model
        rewritten=chain.invoke({"history":self.history_text(),"question":question}).content.strip()
        self.logger.info("query rewrite | original=%r | rewritten=%r",question,rewritten)
        return rewritten or question
