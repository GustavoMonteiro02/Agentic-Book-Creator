# Agentic Book Creator

Agentic Book Creator is a portfolio project for AI Engineering and agentic automation. It is an editorial assistant that turns a rough book idea into a structured book plan, asks adaptive follow-up questions, keeps a human in the loop, and progressively generates reviewed chapters.

The goal is not to auto-generate a book in one opaque prompt. The system behaves like an intelligent coauthor: it gathers missing context, creates an editorial strategy, proposes an editable structure, waits for approval, then plans, drafts, reviews, and edits chapters.

## Core Capabilities

- Stateful multi-step workflows with LangGraph
- Human-in-the-loop approval before chapter generation
- Structured outputs with Pydantic schemas
- FastAPI backend with clean service boundaries
- PostgreSQL persistence model
- LangSmith observability hooks
- RAG-ready architecture with Pinecone
- Streamlit MVP interface
- pytest coverage for deterministic workflow behavior

## MVP Flow

```text
User Initial Idea
  -> Input Gathering Agent
  -> User Answers
  -> Input Understanding Agent
  -> Book Strategy Agent
  -> Structure Designer Agent
  -> Human Review / Approval
  -> Chapter Planning Agent
  -> Chapter Writer Agent
  -> Technical Reviewer Agent
  -> Editor Agent
  -> Final Chapter Output
```

## Repository Structure

```text
app/
  api/              FastAPI app and route modules
  agents/           Workflow state, graph orchestration, agent nodes
  database/         SQLAlchemy session, models, repositories
  prompts/          Prompt contracts for LLM-backed agents
  rag/              Pinecone/RAG integration placeholders
  schemas/          Pydantic request/response models
  services/         Application services used by API and UI
frontend/           Streamlit UI
tests/              pytest test suite
docs/               Architecture, workflow, and backlog
data/               Local source and output folders
```

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
make migrate
uvicorn app.api.main:app --reload
```

In another terminal:

```bash
streamlit run frontend/streamlit_app.py
```

The agents use real Gemini LLM calls when `GEMINI_API_KEY` or `GOOGLE_API_KEY` is configured. Without credentials, they fall back to deterministic local implementations so tests, CI, and offline demos remain stable.

```bash
export GEMINI_API_KEY=...
export LLM_PROVIDER=gemini
export LLM_MODEL=gemini-2.5-flash
```

Database migrations are managed with Alembic:

```bash
make migrate
```

## Docker

Create a local `.env` with your Gemini key:

```bash
cp .env.example .env
```

Set:

```env
GEMINI_API_KEY=your_key_here
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
LLM_ENABLED=true
```

Run the full stack:

```bash
docker compose up --build
```

Then open:

- API: `http://localhost:8000`
- UI: `http://localhost:8501`

The API container runs Alembic migrations before starting FastAPI.

## Portfolio Narrative

This project demonstrates the practical architecture behind agentic systems: stateful orchestration, structured intermediate artifacts, approval gates, persistence, observability, and evaluation-readiness. It is designed to grow from a runnable MVP into a complete AI Engineering portfolio case study.

See [docs/architecture.md](docs/architecture.md), [docs/langgraph_workflow.md](docs/langgraph_workflow.md), [docs/backlog.md](docs/backlog.md), and [docs/feature_ideas.md](docs/feature_ideas.md).

For a runnable API walkthrough, see [docs/api.md](docs/api.md).
