from app.services.knowledge import KnowledgeBase


def test_loads_all_sections():
    kb = KnowledgeBase("data/knowledge.txt")
    titles = {s.title for s in kb.sections}
    assert {"WARRANTY", "RETURNS", "SHIPPING", "INSTALLATION", "SUPPORT", "SAFETY"} <= titles


def test_search_returns_relevant_section():
    kb = KnowledgeBase("data/knowledge.txt")
    results = kb.search("How long is the warranty on my product?")
    assert results
    assert results[0].title == "WARRANTY"


def test_search_falls_back_when_no_keyword_match():
    kb = KnowledgeBase("data/knowledge.txt")
    results = kb.search("")
    assert results
