# Board Game RAG

A self-hosted, local board game rules assistant that lets you ask natural language questions about board game rules and receive cited responses grounded in the actual rulebook.

## Overview

Looking up rules mid-game is slow and frustrating. This project provides a conversational interface powered by Retrieval-Augmented Generation (RAG) — upload a rulebook PDF once, then ask questions and get precise answers with page-level citations.

Each board game is configured as a separate Agent in LibreChat, so every game gets its own isolated chat session scoped to its rulebook.

## Tech Stack

- **Frontend:** [LibreChat](https://github.com/danny-avila/LibreChat) — open source AI chat UI
- **RAG Pipeline:** LibreChat RAG API (FastAPI + LangChain)
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
git clone https://github.com/yourusername/board-game-rag.git
cd board-game-rag
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
├── .env.example                # Environment variable template
├── scripts/                    # Utility scripts (ingestion, etc.)
├── prompts/                    # System prompt templates per game
└── README.md

## How It Works

1. You upload a rulebook PDF to a game Agent in LibreChat
2. The RAG API chunks and embeds the PDF using nomic-embed-text via Ollama
3. Embeddings are stored in pgvector (PostgreSQL)
4. When you ask a question, the RAG API retrieves the most relevant chunks
5. Those chunks are passed to Claude along with your question
6. Claude answers based on the rulebook and cites the source

## Future Improvements

### Citations
- **Inline citation viewer** — a citation bar in the chat that lets you click on a source reference and see a pop-up of the exact lines retrieved from the rulebook, so you can verify answers against the original text

### Retrieval Quality
- **Semantic chunking** — replace the current fixed-size chunking (1000 token chunks with 150 token overlap) with heading/section-based chunking so chunks align with actual rule boundaries rather than arbitrary token counts
- **Reranking** — add a reranker model as a second pass after vector search to improve relevance before sending chunks to the LLM
- **Image and diagram extraction** — rulebooks contain setup diagrams and card layouts that the current text-only parser skips entirely; extract and reference these visually

### UI/UX
- **Game selector landing page** — a proper home screen where you pick your game before the chat loads, rather than manually switching agents
- **Mobile-friendly layout** — optimized for mid-game lookups on your phone
- **Custom PDF parser** — swap in PyMuPDF for better text extraction, especially for rulebooks with complex layouts and tables

### Cost & Infrastructure
- **Fully local/open source mode** — replace the Claude API with a locally running open source LLM via Ollama (Llama 3, Mistral, etc.) so the entire stack runs with zero API costs
- **Rulebook version management** — handle errata and updated editions without re-ingesting everything from scratch

### Features
- **Multi-game search** — query across all uploaded rulebooks at once (e.g. "which games have a worker placement mechanic?")
- **Pre-ingestion CLI script** — bulk upload all rulebooks at once instead of doing it manually through the UI per game
- **Offline mode** — fully air-gapped setup with no external API calls required

## Notes

- Images and diagrams in rulebooks are not currently extracted — text-only for v1
- Embeddings are generated locally via Ollama so there is no per-token embedding cost
- Only Claude API calls cost money (per query)