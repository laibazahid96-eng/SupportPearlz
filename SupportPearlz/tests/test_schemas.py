from src.chains.schemas import GroundedResponse, Confidence
def test_response_schema():
    r=GroundedResponse(answer="ok",sources=["warranty_policy.md"],confidence=Confidence.high,answered=True,used_context_labels=["S1"])
    assert r.answered and r.confidence=="high"
