from dataclasses import dataclass


@dataclass(frozen=True)
class RoutingDecision:
    run_type: str
    route: str
    model_name: str
    reason: str
    estimated_cost_tier: str


ROUTING_TABLE = {
    "input_gathering": RoutingDecision(
        run_type="input_gathering",
        route="small_llm",
        model_name="fast-structured-extractor",
        reason="Clarification question generation is structured and low risk.",
        estimated_cost_tier="low",
    ),
    "book_plan": RoutingDecision(
        run_type="book_plan",
        route="strong_llm",
        model_name="reasoning-editorial-planner",
        reason="Book strategy and structure need stronger reasoning and coherence.",
        estimated_cost_tier="medium",
    ),
    "structure_approval": RoutingDecision(
        run_type="structure_approval",
        route="deterministic",
        model_name="rules-engine",
        reason="Human approval is a deterministic state transition.",
        estimated_cost_tier="none",
    ),
    "structure_revision": RoutingDecision(
        run_type="structure_revision",
        route="deterministic",
        model_name="rules-engine",
        reason="Revision request capture is persistence, not generation.",
        estimated_cost_tier="none",
    ),
    "chapter_planning": RoutingDecision(
        run_type="chapter_planning",
        route="strong_llm",
        model_name="reasoning-chapter-planner",
        reason="Chapter plans require pedagogy, sequencing, and technical judgment.",
        estimated_cost_tier="medium",
    ),
    "chapter_drafting": RoutingDecision(
        run_type="chapter_drafting",
        route="strong_llm",
        model_name="longform-writer",
        reason="Long-form generation benefits from the highest quality route.",
        estimated_cost_tier="high",
    ),
    "chapter_review": RoutingDecision(
        run_type="chapter_review",
        route="strong_llm",
        model_name="technical-reviewer",
        reason="Technical review is high impact and should prioritize quality.",
        estimated_cost_tier="medium",
    ),
    "chapter_edit": RoutingDecision(
        run_type="chapter_edit",
        route="small_llm",
        model_name="style-editor",
        reason="Editorial polishing is constrained by an existing draft.",
        estimated_cost_tier="low",
    ),
    "chapter_generation": RoutingDecision(
        run_type="chapter_generation",
        route="strong_llm",
        model_name="full-chapter-pipeline",
        reason="The full pipeline includes planning, writing, review, and editing.",
        estimated_cost_tier="high",
    ),
}


def choose_route(run_type: str) -> RoutingDecision:
    return ROUTING_TABLE.get(
        run_type,
        RoutingDecision(
            run_type=run_type,
            route="deterministic",
            model_name="rules-engine",
            reason="Unknown or administrative run types default to deterministic handling.",
            estimated_cost_tier="none",
        ),
    )


def routing_metadata(run_type: str) -> dict:
    decision = choose_route(run_type)
    return {
        "model_route": decision.route,
        "routed_model_name": decision.model_name,
        "routing_reason": decision.reason,
        "estimated_cost_tier": decision.estimated_cost_tier,
    }
