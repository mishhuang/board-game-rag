# Board Game RAG

A self-hosted, local board game rules assistant that lets you ask natural language questions about board game rules and receive cited responses grounded in the actual rulebook.

## Overview

Looking up rules mid-game is slow and frustrating. This project provides a conversational interface powered by Retrieval-Augmented Generation (RAG) — upload a rulebook PDF once, then ask questions and get precise answers with page-level citations.

Each board game is configured as a separate Agent in LibreChat, so every game gets its own isolated chat session scoped to its rulebook.

## Tech Stack

- **Frontend:** [LibreChat](https://github.com/danny-avila/LibreChat) — open source AI chat UI
- **RAG Pipeline:** LibreChat RAG API (FastAPI + LangChain) with three-tier semantic chunking and PyMuPDF text extraction
- **Vector Database:** PostgreSQL + pgvector
- **Embeddings:** [nomic-embed-text](https://ollama.com/library/nomic-embed-text) via Ollama (local, zero cost)
- **LLM:** Claude (Anthropic API)
- **Orchestration:** Docker Compose

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) or Docker + Docker Compose (Linux)
- [Ollama](https://ollama.com/) installed and running locally
- An [Anthropic API key](https://console.anthropic.com/)

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/mishhuang/board-game-rag.git
cd board-game-rag
git submodule update --init
```

### 2. Pull the embedding model

```bash
ollama pull nomic-embed-text
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and add your Anthropic API key:
ANTHROPIC_API_KEY=your_key_here

### 4. Start the stack

```bash
docker compose up -d
```

Or using the Makefile:
```bash
make start
```

### 5. Open LibreChat

Go to [http://localhost:3080](http://localhost:3080), create an account, and log in.

### 6. Create a game agent

1. In the sidebar, click **Agents → Create New Agent**
2. Give it a name (e.g. "Catan Rules Assistant")
3. Set the instructions:
   > You are a rules assistant for [Game Name]. Answer questions strictly based on the uploaded rulebook. Always cite the page number where you found the answer. If the rulebook doesn't clearly address the question, say so rather than guessing.
4. Enable **File Search** under Capabilities
5. Click **Create**
6. Upload the game's rulebook PDF to the File Search section
7. Start chatting!

## Project Structure
board-game-rag/
├── docker-compose.yml          # Spins up LibreChat, RAG API, pgvector, MongoDB
├── librechat.yaml              # LibreChat configuration
├── Makefile                    # Shortcuts for common docker compose commands
├── .env.example                # Environment variable template
├── rag_api/                    # Forked RAG API with custom semantic chunking
├── scripts/                    # Planned: bulk rulebook ingestion scripts
├── prompts/                    # Planned: version-controlled system prompt templates per game
└── README.md

## How It Works

1. You upload a rulebook PDF to a game Agent in LibreChat
2. The RAG API chunks the PDF using a three-tier strategy: section-based (heading detection) → semantic (embedding-based) → fixed-size fallback — then embeds chunks using nomic-embed-text via Ollama
3. Embeddings are stored in pgvector (PostgreSQL)
4. When you ask a question, the RAG API retrieves the most relevant chunks
5. Those chunks are passed to Claude along with your question
6. Claude answers based on the rulebook and cites the source

## Chunking Strategy

PDFs are processed using a three-tier chunking pipeline implemented in the forked `rag_api`:

1. **Section-based (Tier 1)** — detects headings (short lines in ALL CAPS or Title Case) and splits at section boundaries. Used when more than 3 sections are detected. Preserves document structure for well-formatted rulebooks.
2. **Semantic (Tier 2)** — uses LangChain's SemanticChunker with nomic-embed-text embeddings to split at natural semantic boundaries. Fallback for PDFs without clear headings.
3. **Fixed-size (Tier 3)** — splits by token count (1000 tokens, 150 overlap). Last resort for unstructured PDFs and used for all non-PDF file types.

## Makefile Commands

```bash
make start        # Start all services
make stop         # Stop all services
make restart      # Restart all services
make logs         # Follow all logs
make logs-rag     # Follow RAG API logs
make status       # Show container status
make clean        # Stop and remove volumes
```

## Future Improvements

### Citations
- **Inline citation viewer** — a citation bar in the chat that lets you click on a source reference and see a pop-up of the exact lines retrieved from the rulebook

### Retrieval Quality
- **Reranking** — add a reranker model as a second pass after vector search to improve relevance before sending chunks to the LLM
- **Image and diagram extraction** — rulebooks contain setup diagrams and card layouts that are not yet extracted; PyMuPDF's `page.get_images()` provides the primitive, but a vision model is needed to describe diagram contents for RAG
- **Fully local/open source mode** — replace the Claude API with a locally running open source LLM via Ollama so the entire stack runs with zero API costs. Both Mistral 7B and Qwen3 8B were evaluated — tool calling works mechanically on Qwen3 8B but factual accuracy is insufficient for a rules assistant where wrong answers cause real problems mid-game. Requires a larger or more instruction-tuned model; a promising next candidate is Llama 3.1 8B Instruct.

### UI/UX
- **Game selector landing page** — a proper home screen where you pick your game before the chat loads, rather than manually switching agents
- **Mobile-friendly layout** — optimized for mid-game lookups on your phone
- **Custom PDF parser** — swap in PyMuPDF for better text extraction, especially for rulebooks with complex layouts and tables

### Cost & Infrastructure
- **Rulebook version management** — handle errata and updated editions without re-ingesting everything from scratch

### Features
- **Multi-game search** — query across all uploaded rulebooks at once (e.g. "which games have a worker placement mechanic?")
- **Pre-ingestion CLI script** — bulk upload all rulebooks at once instead of doing it manually through the UI per game
- **Offline mode** — fully air-gapped setup with no external API calls required

## Notes

- Images and diagrams in rulebooks are not currently extracted — text-only for v1
- Embeddings are generated locally via Ollama so there is no per-token embedding cost
- PDFs are chunked using a three-tier strategy: section-based → semantic → fixed-size fallback
- Local LLM support is a work in progress — Qwen3 8B via Ollama successfully calls the RAG API but hallucinates rule details; Claude remains the recommended model for accurate answers
- PDF text extraction uses PyMuPDF for improved handling of complex layouts, tables, and fonts

