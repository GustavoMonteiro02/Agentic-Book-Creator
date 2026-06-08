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

The current scaffold implements the same node contract with deterministic Python functions. That keeps the app runnable before API keys are configured. The graph can be upgraded by replacing `SimpleBookWorkflow` with a LangGraph `StateGraph` whose node functions call the same agent modules.
