# 0xbrain

Crypto knowledge engine — ask anything about protocols, get sourced answers from whitepapers and technical docs. Grounded answers from source documents.

## What is this?

A RAG (Retrieval-Augmented Generation) system built for crypto. Upload protocol whitepapers, and `0xbrain` chunks them, embeds them into a vector database, and uses them as context for AI-generated answers. Every answer comes with source references and relevance scores.

The system uses **Multi-Query RAG** — complex questions are automatically decomposed into sub-queries, each searching the knowledge base separately. This means cross-protocol questions like "How does Lido staking compare to Aave lending?" actually work, pulling relevant chunks from both protocols.

## How it works

```
User Question
      │
      ▼
┌─────────────────┐
│  Decompose into  │  ← Claude splits question into 2-4 sub-queries
│  sub-questions    │
└────────┬────────┘
         │
    ┌────▼────┐
    │ For each │
    │ sub-query│
    └────┬────┘
         │
┌────────▼────────┐
│  Embed question   │  ← sentence-transformers (local, free)
│  into vector      │
└────────┬────────┘
         │
┌────────▼────────┐
│  Search ChromaDB  │  ← cosine similarity, find closest chunks
│  for top-k chunks │
└────────┬────────┘
         │
┌────────▼────────┐
│  Deduplicate &    │  ← merge results from all sub-queries
│  combine chunks   │
└────────┬────────┘
         │
┌────────▼────────┐
│  Claude generates │  ← grounded answer from context only
│  sourced answer   │
└─────────────────┘
```

## Knowledge Base

Currently indexed with 400+ chunks from 10 protocol whitepapers:

| Protocol | Category | Chunks |
|----------|----------|--------|
| Bitcoin Whitepaper | btc | 12 |
| Ethereum Whitepaper | eth | 45 |
| Solana Whitepaper | solana | 25 |
| Uniswap V2 | defi | 16 |
| Uniswap V3 | defi | 22 |
| Aave V3 | defi | 22 |
| Compound | defi | 10 |
| Chainlink 2.0 | oracle | 196 |
| Lido V1 | staking | 12 |
| Lido V3 | staking | 44 |

New documents can be added via the `/ingest` endpoint or the batch ingestion script.

## Tech Stack

- **FastAPI** — async API
- **ChromaDB** — persistent vector database (local)
- **sentence-transformers** — local embeddings (all-MiniLM-L6-v2, 384 dims)
- **Anthropic SDK** — Claude for answer generation + query decomposition
- **pypdf** — PDF text extraction

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/ingest` | Upload a PDF to the knowledge base |
| `POST` | `/query` | Ask a question, get a sourced answer |
| `GET` | `/documents` | List all indexed documents |

## Query Example

**Request:**
```json
{
  "question": "How do automated market makers work?",
  "top_k": 5,
  "category_filter": "defi"
}
```

**Response:**
```json
{
  "question": "How do automated market makers work?",
  "answer": "Based on the Uniswap whitepapers, AMMs are agents that pool liquidity and make it available to traders according to an algorithm...",
  "sources": [
    {
      "title": "Uniswap V3 Whitepaper",
      "content_snippet": "Automated market makers (AMMs) are agents that pool liquidity...",
      "relevance_score": 0.58
    }
  ]
}
```

## Setup

```bash
# Clone
git clone https://github.com/Naakugod11/0xbrain.git
cd 0xbrain

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Install (CPU-only torch first to save space)
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# Environment
cp .env.example .env
# Edit .env with your Anthropic API key

# Ingest whitepapers
PYTHONPATH=. python ingestion/batch_ingest.py

# Run
uvicorn api.main:app --reload

# Frontend demo
# Open http://localhost:8000/demo

# Tests
PYTHONPATH=. python -m pytest tests/ -v
```

## Tests

```
tests/test_chunking.py   — chunk creation, overlap, indexing
tests/test_embedding.py  — vector dimensions, batch, semantic similarity
tests/test_models.py     — schema validation and defaults
```

All 11 tests passing.

## Project Structure

```
0xbrain/
├── api/
│   ├── main.py              # FastAPI app
│   └── routes.py            # Ingest, query, documents endpoints
├── core/
│   ├── config.py            # Settings (chunk size, embedding model, etc.)
│   └── models.py            # Pydantic schemas
├── services/
│   ├── chunking.py          # Text splitting with overlap + sentence boundaries
│   ├── embedding.py         # Local embeddings via sentence-transformers
│   ├── vector_store.py      # ChromaDB persistent storage
│   └── query.py             # Multi-query RAG pipeline
├── ingestion/
│   └── batch_ingest.py      # Auto-download and ingest protocol whitepapers
├── frontend/
│   └── index.html           # Demo UI
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## Key Features

**Multi-Query RAG** — questions are decomposed into sub-queries for broader, more accurate retrieval across multiple protocols.

**Grounded Answers** — the AI only answers from the provided context. If the docs don't have the answer, it says so honestly.

**Category Filtering** — search only in specific protocol categories (defi, btc, eth, oracle, staking).

**Batch Ingestion** — one script downloads and indexes all protocol whitepapers automatically.

**Local Embeddings** — no API costs for embeddings, runs on CPU with sentence-transformers.

## Part of a larger roadmap

This is Phase 2 of a Web3 + AI development track:

- Phase 1 — [web3-ai-agent](https://github.com/Naakugod11/web3-ai-agent) (SIWE auth + structured AI outputs) ✅
- Phase 2 — 0xbrain (RAG for crypto knowledge) ✅
- Phase 3 — Autonomous agent with tool use (separate repo)
- Phase 4 — Multi-agent adaptive trading bot (separate repo)
- Phase 5 — ZK proof integration (separate repo)

## Built by

[@naaku_builds](https://x.com/naaku_builds)