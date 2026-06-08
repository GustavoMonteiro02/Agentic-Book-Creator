from app.agents.state import BookState


def write_chapter(state: BookState) -> BookState:
    plan = state.get("chapter_plans", [{}])[-1]
    title = plan.get("title", "Chapter")

    markdown = f"""# {title}

## Introduction

Agentic systems become useful when they combine reasoning, state, tools, and human review into a workflow that can be inspected and improved.

## Core Concepts

This chapter focuses on {", ".join(plan.get("key_concepts", []))}. The central idea is that a reliable agent is not a single prompt. It is a controlled process with typed inputs, explicit state transitions, and review points.

## Analogy

{plan.get("analogies", ["Think of the workflow as a production pipeline."])[0]}

## Practical Example

{plan.get("examples", ["Build a simple workflow."])[0]}

## Code Sketch

```python
def node(state):
    return {{"status": "next_step_ready"}}
```

## Common Mistakes

- Generating final content before gathering enough context.
- Hiding intermediate decisions from the user.
- Treating human review as an afterthought.

## Summary

Agentic engineering is the discipline of making AI workflows explicit, observable, and safe to iterate.

## Exercises

{_format_exercises(plan.get("exercises", []))}
"""

    draft = {"chapter_number": plan.get("chapter_number", 1), "title": title, "markdown": markdown}
    return {**state, "chapter_drafts": [*state.get("chapter_drafts", []), draft], "status": "chapter_drafted"}


def _format_exercises(exercises: list[str]) -> str:
    if not exercises:
        return "- Design one approval gate for an agentic workflow."
    return "\n".join(f"- {exercise}" for exercise in exercises)
