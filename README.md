# ComplyAU - Compliance Analyst for Australian Businesses

ComplyAU is an agentic RAG system that analyses uploaded business documents against Australian legislation and generates structured compliance reports. Upload a contract, agreement, or privacy policy and the system identifies gaps, compliant areas, and actionable recommendations across relevant Australian acts.

---

## Architecture

```
Frontend (Next.js)
      │
      ▼
Backend (FastAPI)
      │
      ├── Ingestion Pipeline
      │     PDF/DOCX → Parser → Chunker → Embedder → pgvector
      │
      ├── Retrieval Pipeline
      │     Query → Vector Search + BM25 → RRF → Cohere Rerank
      │
      ├── ReAct Agent (GPT-4o-mini)
      │     ├── static_retriever   — searches uploaded documents in pgvector
      │     ├── query_reformulator — rewrites queries for better retrieval
      │     ├── live_fetcher       — calls MCP server over SSE
      │     └── citation_validator — validates claims against retrieved chunks
      │
      └── MCP Server (Railway) ←── live_fetcher connects here via SSE
            ├── fetch_legislation_tool  — scrapes legislation.gov.au
            └── fetch_oaic_guidance     — scrapes oaic.gov.au
```

---

## Key Features

- **Hybrid Retrieval** - combines dense vector search (pgvector + sentence-transformers) with sparse BM25 retrieval, fused via Reciprocal Rank Fusion and reranked with Cohere
- **ReAct Agent** - reasons over retrieved document content and live legislation, calling tools iteratively until it has enough context to answer
- **MCP Tool Server** - a standalone deployed MCP server exposing Australian legislation fetching tools over SSE transport, following the official Model Context Protocol standard
- **Live Legislation Fetching** - fetches live guidance from oaic.gov.au for Privacy Act and OAIC topics; curated static summaries for Cloudflare-protected sites (Fair Work, WHS)
- **Compliance Scoring** - LLM classifies gaps as critical/major/minor; score = 100 − (20 × critical) − (10 × major) − (5 × minor)
- **PDF Report** - downloadable compliance report with score gauge, gap table, and recommendations
- **Observability** - full pipeline tracing with Langfuse (tool calls, LLM inputs/outputs)
- **PII Redaction** - Presidio strips personal information from documents before indexing

---

## Evaluation (Ragas)

Evaluated on a 10-question synthetic dataset against a privacy policy document using GPT-4o-mini as judge.

| Metric | Score |
|---|---|
| Faithfulness | **1.000** |
| Answer Relevancy | **0.970** |
| Context Precision | **0.967** |

Context Precision improved from 0.917 → 0.967 after increasing chunk overlap from 50 → 150 tokens, fixing chunk boundary fragmentation where section headings were split from their content.

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | GPT-4o-mini (OpenAI) |
| Agent Framework | LangChain ReAct |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Database | PostgreSQL + pgvector |
| Sparse Retrieval | BM25 (rank-bm25) |
| Reranking | Cohere Rerank |
| MCP Server | FastMCP (SSE transport) |
| Observability | Langfuse |
| PII Detection | Microsoft Presidio |
| Backend | FastAPI + Uvicorn |
| Frontend | Next.js 14 + Tailwind CSS |
| Deployment | Railway (backend + MCP server + PostgreSQL), Vercel (frontend) |

---

## Australian Legislation Covered

- Privacy Act 1988 (Australian Privacy Principles)
- Fair Work Act 2009 (National Employment Standards)
- Work Health and Safety Act 2011
- Corporations Act 2001
- Australian Consumer Law (Competition and Consumer Act 2010)
- Spam Act 2003
- Superannuation Guarantee Act 1992

---

## MCP Server

The legislation fetching tools are deployed as a standalone MCP server on a separate Railway service. Any MCP-compatible agent can connect to it and call the tools over SSE transport without any code sharing.

The MCP server lives in a separate repository: [au-legislation-mcp](https://github.com/Ro25v04/au-legislation-mcp)

Tools exposed:
- `fetch_legislation_tool(act_name)` — fetches Australian act summaries
- `fetch_oaic_guidance(topic)` — fetches OAIC privacy guidance

Note: most Australian government legislation sites are Cloudflare-protected or JavaScript-rendered, making automated scraping unreliable. Live scraping works for oaic.gov.au; other acts use curated static summaries based on the official act text.

---

## Project Structure

```
ComplyIQ/
├── backend/
│   ├── agent/
│   │   ├── react_agent.py          # ReAct agent loop (run + stream)
│   │   └── tools/
│   │       ├── static_retriever.py # hybrid retrieval tool
│   │       ├── live_fetcher.py     # MCP SSE client
│   │       ├── query_reformulator.py
│   │       └── citation_validator.py
│   ├── ingestion/
│   │   ├── parser.py               # PDF/DOCX extraction
│   │   ├── chunker.py              # recursive text splitting
│   │   ├── embedder.py             # sentence-transformers
│   │   └── indexer.py              # pgvector upsert
│   ├── retrieval/
│   │   ├── vector_search.py
│   │   ├── bm25_search.py
│   │   ├── rrf.py                  # Reciprocal Rank Fusion
│   │   └── reranker.py             # Cohere rerank
│   ├── api/routes/
│   │   ├── upload.py
│   │   ├── query.py                # streaming chat endpoint
│   │   └── report.py               # compliance report generation
│   └── monitoring/
│       └── langfuse_client.py
├── frontend/
│   └── app/
│       ├── page.tsx                # landing page
│       ├── app/page.tsx            # chat interface
│       └── report/page.tsx         # compliance report page
└── eval/
    ├── run_eval.py                 # Ragas evaluation script
    └── results.json                # evaluation results
```

---

## Limitations

- Live scraping works for oaic.gov.au; other government legislation sites (Fair Work, WHS) are Cloudflare-protected and fall back to curated static summaries
- Document analysis is limited to English-language Australian business documents
- Compliance analysis is AI-generated and should not be treated as legal advice
