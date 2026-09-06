"""Validated response models."""
from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field

class Confidence(str, Enum):
    high="high"
    partial="partial"
    none="none"

class GroundedResponse(BaseModel):
    answer: str = Field(min_length=1)
    sources: list[str] = Field(default_factory=list)
    confidence: Confidence
    answered: bool
    used_context_labels: list[str] = Field(default_factory=list)
