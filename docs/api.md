# API Guide

Start the backend:

```bash
make migrate
uvicorn app.api.main:app --reload
```

Base URL:

```text
http://127.0.0.1:8000
```

## 1. Create a Project

```bash
curl -X POST http://127.0.0.1:8000/projects \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Agentic AI for Automation Developers",
    "initial_idea": "Quero criar um livro sobre agentes de inteligência artificial para developers de automação e RPA. Quero que seja prático, com exemplos, código, analogias e mini projetos."
  }'
```

Copy the returned `project_id`.

## 2. Generate Adaptive Questions

```bash
curl -X POST http://127.0.0.1:8000/projects/{project_id}/questions
```

The response includes `input_questions`. The agent should only ask for missing information.

## 3. Submit Answers

```bash
curl -X POST http://127.0.0.1:8000/projects/{project_id}/answers \
  -H "Content-Type: application/json" \
  -d '{
    "answers": [
      {"field": "tone", "answer": "prático e conversacional"},
      {"field": "reader_level", "answer": "intermédio"},
      {"field": "preferred_structure", "answer": "do básico ao avançado por projetos"},
      {"field": "output_formats", "answer": "Markdown"}
    ]
  }'
```

This generates:

- structured requirements;
- editorial strategy;
- editable book structure.

## 4. Inspect Generated Artifacts

```bash
curl -X POST http://127.0.0.1:8000/projects/{project_id}/requirements
curl -X POST http://127.0.0.1:8000/projects/{project_id}/strategy
curl -X POST http://127.0.0.1:8000/projects/{project_id}/structure
```

## 5. Approve the Structure

```bash
curl -X POST http://127.0.0.1:8000/projects/{project_id}/approve-structure \
  -H "Content-Type: application/json" \
  -d '{"approved": true}'
```

Chapter generation is blocked until this approval exists.

## 6. Generate Chapter 1 Step by Step

```bash
curl -X POST http://127.0.0.1:8000/projects/{project_id}/chapters/1/plan
curl -X POST http://127.0.0.1:8000/projects/{project_id}/chapters/1/review
curl -X POST http://127.0.0.1:8000/projects/{project_id}/chapters/1/edit
```

Or run the full chapter pipeline:

```bash
curl -X POST http://127.0.0.1:8000/projects/{project_id}/chapters/1/generate
```

## 7. View Runs

```bash
curl http://127.0.0.1:8000/projects/{project_id}/runs
```

Runs are currently stored in memory and include a placeholder field for future `langsmith_trace_url` integration.

## 8. Export Markdown

```bash
curl -X POST http://127.0.0.1:8000/projects/{project_id}/export/markdown
```

## 9. Inspect Prompt Versions

```bash
curl http://127.0.0.1:8000/prompts
curl http://127.0.0.1:8000/prompts/chapter_writer
```

The prompt registry returns version, output contract, model route, and changelog metadata. Individual prompt lookups include the prompt template by default.

## Current MVP Limitation

The first implementation uses deterministic local agent functions and an in-memory repository so tests and demos can run without API keys. The database schema, LangGraph builder, prompt contracts, Pinecone placeholders, and LangSmith run fields are already prepared for the next integration pass.
