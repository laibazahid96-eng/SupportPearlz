"""
Knowledge base loading and lightweight retrieval.

The knowledge file is a plain-text document split into UPPERCASE section
headers (e.g. "WARRANTY:") followed by their body text. Rather than
stuffing the entire file into every prompt -- which wastes tokens and
makes it easier for the model to wander off-topic -- we score each
section against the customer's question with simple keyword overlap and
only send the most relevant section(s) to the model. This keeps answers
grounded and keeps the project easy to scale to a much larger knowledge
base later without changing the prompting strategy.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_SECTION_HEADER_RE = re.compile(r"^([A-Z][A-Z \-]{2,}):\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Section:
    title: str
    body: str
    source: str


class KnowledgeBase:
    """In-memory, file-backed knowledge base with keyword retrieval."""

    def __init__(self, path: str):
        self._path = Path(path)
        self._sections: list[Section] = []
        self.reload()

    def reload(self) -> None:
        text = self._path.read_text(encoding="utf-8")
        source = self._path.name
        matches = list(_SECTION_HEADER_RE.finditer(text))

        sections: list[Section] = []
        for i, match in enumerate(matches):
            title = match.group(1).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            if body:
                sections.append(Section(title=title, body=body, source=source))

        if not sections:
            # Fall back to treating the whole file as one section so the
            # app still works even if the knowledge file has no headers.
            sections = [Section(title="GENERAL", body=text.strip(), source=source)]

        self._sections = sections

    @property
    def sections(self) -> list[Section]:
        return list(self._sections)

    def full_text(self) -> str:
        return "\n\n".join(f"{s.title}:\n{s.body}" for s in self._sections)

    def search(self, question: str, top_k: int = 2) -> list[Section]:
        """Return the sections most relevant to `question` by keyword overlap."""
        words = {w for w in re.findall(r"[a-z0-9]+", question.lower()) if len(w) > 2}
        if not words:
            return self._sections[:top_k]

        scored = []
        for section in self._sections:
            haystack = f"{section.title} {section.body}".lower()
            score = sum(1 for w in words if w in haystack)
            scored.append((score, section))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        top = [section for score, section in scored if score > 0][:top_k]
        return top or self._sections[:top_k]
