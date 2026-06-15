# LangGraph Workflow

## State

The workflow uses a shared `BookState` with project metadata, gathered inputs, generated artifacts, approval flags, chapter outputs, status, and errors.

Core fields:

- `project_id`
- `initial_user_idea`
- `raw_user_inputs`
- `input_questions`
- `user_answers`
- `book_requirements`
- `missing_information`
- `book_strategy`
- `book_structure`
- `chapter_template`
- `structure_approved`
- `structure_revision_requests`
- `current_chapter_number`
- `chapter_plans`
- `chapter_drafts`
- `chapter_reviews`
- `final_chapters`
- `user_feedback`
- `status`
- `errors`

## MVP Nodes

```text
gather_input
  -> understand_input
  -> create_strategy
  -> design_structure
  -> wait_for_human_approval
  -> plan_chapter
  -> write_chapter
  -> review_chapter
  -> edit_chapter
  -> done
```

## Conditional Edges

After `gather_input`:

- If missing information exists, return questions to the user and pause.
- If enough information exists, continue to `understand_input`.

After `design_structure`:

- If `structure_approved` is false, pause at `wait_for_human_approval`.
- If true, continue to chapter planning.

After `review_chapter`:

- If high-severity technical issues exist, return to `write_chapter` or request human feedback.
- If approved, continue to `edit_chapter`.

## Human-in-the-loop Contract

The workflow must not generate chapters until the structure is approved. Human review can:

- approve the structure;
- edit the structure;
- request regeneration;
- change tone or depth;
- remove or reorder chapters;
- focus or defocus topics.

## Implementation Notes

The service layer now runs the core creation phases through compiled LangGraph graphs. The node functions call Gemini through the shared LLM client when credentials are configured, while deterministic fallbacks keep tests and offline demos stable.

Every recorded run includes node-level observability metadata:

- `workflow_nodes`: the agents/services involved in that operation;
- `artifact_summary`: counts and readiness flags for generated outputs;
- `runtime_warnings`: provider fallback details, including quota or API failures.

The Streamlit UI renders this metadata in the sidebar, the structure "Agent trace" tab, and the chapter workspace "Trace" tab.
