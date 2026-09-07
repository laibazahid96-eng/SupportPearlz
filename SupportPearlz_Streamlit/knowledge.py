"""
Knowledge base loading and lightweight keyword retrieval.

The knowledge file is plain text split into UPPERCASE section headers
(e.g. "WARRANTY:") followed by body text. Instead of sending the whole
file to the model on every question, we score each section against the
question by keyword overlap and only send the one or two most relevant
sections. This keeps prompts small and answers grounded, and scales to a
much bigger knowledge base later without changing the app.
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


class KnowledgeBase:
    def __init__(self, path: str | Path = "data/knowledge.txt"):
        file_path = Path(path)
        if not file_path.is_absolute():
            # If a relative path is passed, resolve it relative to this file's location
            file_path = (Path(__file__).resolve().parent / file_path).resolve()
            
        self._path = file_path
        self._sections: list[Section] = []
        self.reload()

    def reload(self) -> None:
        text = self._path.read_text(encoding="utf-8")
        matches = list(_SECTION_HEADER_RE.finditer(text))

        sections: list[Section] = []
        for i, match in enumerate(matches):
            title = match.group(1).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            if body:
                sections.append(Section(title=title, body=body))

        self._sections = sections or [Section(title="GENERAL", body=text.strip())]

    @property
    def sections(self) -> list[Section]:
        return list(self._sections)

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