# Feature Ideas From AI Engineering Interview Context

This project should evolve beyond book generation into a portfolio-grade agentic engineering case study. The best next features are the ones that show production thinking: versioning, observability, evaluation, fallback, cost control, and RAG quality.

## 1. Context Versioning Dashboard

Add a page that shows which versions were used for each generated artifact:

- `prompt_version`
- `llm_model_version`
- `embedding_model_version`
- `chunking_strategy_version`
- `retrieval_config_version`
- `index_version`

Why it matters: in real RAG systems, every answer should be traceable to the prompt, model, retrieval config, embedding model, index, and source documents used at the time.

## 2. Retrieval Evaluation Lab

Add golden datasets for source retrieval:

- query;
- expected document IDs;
- retrieved document IDs;
- Precision@K;
- Recall@K;
- Hit Rate@K;
- MRR;
- citation accuracy later.

Why it matters: if a generated answer is wrong, the system should help determine whether the root cause was retrieval, reranking, prompt assembly, or generation.

## 3. Source-Aware Chunking

Implement chunking modes:

- fixed-size chunks for baseline tests;
- heading/section-aware chunks for technical documents;
- semantic chunks later;
- overlap by token budget.

Why it matters: blind fixed-size chunking can split concepts and damage retrieval quality. Structure-aware chunking is more realistic for enterprise documents.

Current status: implemented a deterministic first pass in `app/rag/ingest.py` with fixed-size chunking, overlap, Markdown heading splitting, and chunk metadata.

## 4. Zero-Downtime Embedding Migration

Add an index migration workflow:

```text
index_v1 active
  -> create index_v2
  -> backfill documents
  -> run retrieval evals
  -> shadow compare
  -> switch active_index alias
  -> keep rollback
```

Why it matters: embeddings from different models should not be mixed. A strong portfolio project should show migration and rollback thinking.

## 5. Cost and Latency Budgeting

Add per-run diagnostics:

- estimated input tokens;
- estimated output tokens;
- estimated cost;
- model used;
- cache hit/miss;
- run latency;
- fallback used or not.

Why it matters: production AI systems need quality, cost, and latency tradeoff visibility.

## 6. Model Routing

Route simple tasks to cheaper deterministic or smaller-model paths:

- deterministic rules for workflow gates;
- small model for classification or extraction;
- stronger model for chapter generation or technical review.

Why it matters: a mature AI engineer does not use the largest model for every task.

## 7. Failure Checkpoint and Resume

Checkpoint every workflow step:

- gather input;
- generate brief;
- generate strategy;
- design structure;
- approve structure;
- plan chapter;
- draft chapter;
- review chapter;
- edit chapter.

If a step fails, retry only that step. If it fails repeatedly, request human review or use a fallback.

## 8. Memory Policy

Add project-level memory with rules:

- store stable preferences only;
- timestamp every memory item;
- support expiry;
- support deletion;
- avoid storing sensitive data;
- log memory updates.

Why it matters: memory should improve UX without becoming an uncontrolled data dump.

Current status: implemented a project memory MVP with explicit create/list/delete endpoints, timestamps, optional expiry, and diagnostics counts.

## 9. Prompt Regression Tests

Add tests for prompts and structured outputs:

- schema validation;
- required fields;
- refusal/fallback behavior;
- prompt injection resistance;
- deterministic examples with fixed inputs.

Why it matters: LLM CI/CD should test prompts, schemas, retrieval, cost, latency, and regressions.

## 10. Debugging Assistant

Add a diagnostics checklist for incorrect outputs:

1. Was the input clear?
2. Was the right document retrieved?
3. Was the chunk complete?
4. Did reranking remove the right chunk?
5. Was the prompt too vague?
6. Did the model ignore context?
7. Was temperature too high?
8. Did schema validation fail?
9. Was this case covered in evals?
10. Do we need a deterministic rule instead of an LLM?

Why it matters: this shows system design thinking, not just API usage.
