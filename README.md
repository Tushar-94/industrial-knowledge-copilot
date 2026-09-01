
# Industrial Knowledge Copilot

An evaluation-driven Retrieval-Augmented Generation and agentic AI system for technical operations knowledge.

The project uses a realistic, fully synthetic manufacturing environment to demonstrate how technical manuals, standard operating procedures, troubleshooting guides, and structured operational data can be combined into a grounded AI assistant with source-level traceability.

## Project status

Currently in the foundation and system-design phase.

## Planned capabilities

- Technical-document ingestion and metadata preservation

- Chunking and embedding pipelines

- Dense, lexical, and hybrid retrieval

- Retrieval and answer evaluation

- Grounded answers with citations

- Structured operational tools

- Controlled agentic workflows

- FastAPI service

- Automated testing

- Docker and CI/CD

- Public demo deployment

## Data and intellectual-property policy

All public project data and documents will be independently created synthetic content. No employer source code, internal documents, confidential data, or proprietary business logic will be published.

## System Architecture

The current retrieval pipeline follows a modular Retrieval-Augmented Generation (RAG) architecture.

```text
Canonical YAML Knowledge Base

        │

        ▼

Synthetic Document Generation

        │

        ▼

Markdown Technical Documents

        │

        ▼

Markdown Chunking

        │

        ▼

Embedding Generation

        │

        ▼

Retrieval Layer

   ├── Dense Retrieval

   ├── BM25 Retrieval

   ├── Hybrid Retrieval

   └── Query-Aware Routing

        │

        ▼

Relevant Context
```

## Current Features

- Canonical industrial knowledge stored in YAML

- Automatic generation of synthetic manuals, SOPs, and troubleshooting guides

- Markdown parser with section-aware chunking

- Rich metadata attached to every chunk

- SentenceTransformer embeddings (all-MiniLM-L6-v2)

- Dense semantic retrieval

- BM25 lexical retrieval

- Hybrid retrieval using Reciprocal Rank Fusion (RRF)

- Query-aware retrieval routing

- Exact identifier boosting for alarm codes, procedures, and part numbers

- Automated retrieval evaluation framework

## Retrieval Evaluation

The retrieval system is evaluated using two independent benchmark suites.

### Development Benchmark

25 manually curated retrieval cases used during iterative system development.

| Metric | Score |
|--------|------:|
| Hit@1 | 0.800 |
| Hit@3 | 0.960 |
| Hit@5 | **1.000** |
| MRR | 0.883 |

### Held-Out Benchmark

12 previously unseen retrieval cases used to estimate generalization.

| Metric | Score |
|--------|------:|
| Hit@1 | 0.750 |
| Hit@3 | 0.750 |
| Hit@5 | 0.833 |
| MRR | 0.771 |

The held-out benchmark is intentionally kept separate from the development benchmark to reduce evaluation bias during retrieval-system development.

## Retrieval Pipeline

The retrieval system dynamically selects the retrieval strategy based on query characteristics.

- General semantic questions → Dense retrieval

- Identifier-heavy questions (alarm codes, SOP IDs, part numbers) → Hybrid retrieval

- Exact identifier boosting is applied after candidate generation to prioritize exact industrial identifiers.

## Project Status

### Completed

- Canonical knowledge base

- Synthetic document generation

- Markdown chunking

- Embedding generation

- Dense retrieval

- BM25 retrieval

- Hybrid retrieval

- Query-aware routing

- Evaluation framework

### Next

- Persistent vector database (Qdrant)

- Metadata filtering

- Retrieval service

- LLM integration

- End-to-end RAG pipeline