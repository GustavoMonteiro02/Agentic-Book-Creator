from app.services.model_routing_service import choose_route, routing_metadata


def test_choose_route_uses_deterministic_rules_for_approval():
    decision = choose_route("structure_approval")

    assert decision.route == "deterministic"
    assert decision.model_name == "rules-engine"
    assert decision.estimated_cost_tier == "none"


def test_choose_route_uses_stronger_model_for_chapter_drafting():
    decision = choose_route("chapter_drafting")

    assert decision.route == "strong_llm"
    assert decision.estimated_cost_tier == "high"


def test_routing_metadata_includes_reason():
    metadata = routing_metadata("chapter_edit")

    assert metadata["model_route"] == "small_llm"
    assert metadata["routing_reason"]
