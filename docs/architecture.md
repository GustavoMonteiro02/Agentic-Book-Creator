# Architecture

## Product Architecture

Agentic Book Creator is split into four layers:

```text
Streamlit or React UI
        |
FastAPI Backend
        |
Application Services
        |
LangGraph Workflow + Agent Nodes
        |
LLM Providers, Pinecone, PostgreSQL, LangSmith
```

## Backend Responsibilities

FastAPI exposes project, input, structure, chapter, and export endpoints. Route modules should stay thin: validate input, call services, and return structured schemas.

Services coordinate persistence and workflow execution. They are the main boundary between API/UI concerns and the agent workflow.

Agent nodes transform the shared `BookState`. Each node accepts the current state and returns a partial update, making workflow behavior testable and observable.

## Persistence Model

PostgreSQL stores durable project artifacts:

- `book_projects`: project metadata and status
- `user_inputs`: initial ideas, answers, and feedback
- `input_questions`: adaptive clarification questions
- `book_requirements`: structured requirements JSON
- `book_strategies`: editorial strategy JSON
- `book_structures`: editable structure JSON and approval state
- `book_chapters`: chapter plans, drafts, final markdown, and status
- `chapter_reviews`: technical and editorial review data
- `execution_runs`: workflow runs and LangSmith trace links

The MVP can use SQLite locally through the same SQLAlchemy models, while Docker Compose provides PostgreSQL for portfolio/demo use. Alembic migrations define the durable schema and should be run before serving a shared environment.

## Agent Design

The agent layer is intentionally modular:

- Input Gathering Agent identifies known and missing information.
- Input Understanding Agent converts all user input into a typed brief.
- Book Strategy Agent creates an editorial strategy.
- Structure Designer Agent proposes parts, chapters, sections, examples, exercises, and mini projects.
- Human Review Node blocks chapter generation until approval.
- Chapter Planning Agent builds a chapter-specific plan.
- Chapter Writer Agent drafts the chapter.
- Technical Reviewer Agent scores and flags technical issues.
- Editor Agent improves clarity and style.
- Consistency and Export Agents are planned after the MVP.

Each agent first prepares a deterministic fallback artifact, then delegates to the shared LLM client. If `OPENAI_API_KEY` is present, the client calls the configured OpenAI model. If not, it returns the fallback. This keeps production behavior LLM-backed while preserving stable offline tests.

## RAG Strategy

RAG enters in v0.3, after the core workflow is stable. Source upload and indexing should produce project-scoped document chunks in Pinecone. Chapter planning and writing can then retrieve relevant context and include source-grounded examples.

## Observability

The agent layer uses an optional LLM client. When `OPENAI_API_KEY` is configured, agents call the configured OpenAI model; otherwise, deterministic fallbacks are used for tests and offline demos. LangSmith tracing should wrap each workflow execution and key LLM call. The `execution_runs` table stores status, run type, timing, and trace URLs so the UI can connect generated artifacts to execution traces.

## Design Principles

- Keep human approval explicit before expensive generation steps.
- Store every important intermediate artifact.
- Prefer typed schemas over loosely shaped dictionaries at API boundaries.
- Make deterministic tests possible without LLM calls.
- Introduce RAG, evaluation, and export only after the MVP workflow is reliable.
