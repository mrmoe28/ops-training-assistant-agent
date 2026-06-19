# Local Ollama RAG Assistant

Small local RAG proof of concept against a local Ollama endpoint.

## What it does

- Uses a local chat model: `qwen3:8b`
- Uses a local embedding model: `nomic-embed-text:latest`
- Reads local documents from `knowledge/`
- Retrieves the most relevant chunks with local embeddings
- Asks the chat model to answer with citations

## Quick Start

```bash
# 1. Ensure Ollama is running and models are pulled
ollama pull qwen3:8b
ollama pull nomic-embed-text:latest

# 2. Refresh knowledge base
./refresh_all.sh

# 3. Start the assistant server
./start_assistant.sh
```

The server listens on `http://127.0.0.1:8008` by default.

## One-off CLI query

```bash
OLLAMA_URL=http://127.0.0.1:11434 python3 app.py "What services does Eko Solar offer?"
```

Interactive mode:

```bash
OLLAMA_URL=http://127.0.0.1:11434 python3 app.py
```

## Targeted refresh commands

```bash
./refresh_all.sh local       # public site + training docs only
./refresh_all.sh private     # ops jobs/clients/invoices/stats
./refresh_all.sh jobs
./refresh_all.sh invoices
./refresh_all.sh clients
./refresh_all.sh stats
```

## API Endpoints

- `GET /health` — service status + model info
- `POST /chat` — ask a question with optional history/context
- `POST /refresh` — rebuild the knowledge index

Example `POST /chat`:

```bash
curl -X POST http://127.0.0.1:8008/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the latest completed job?"}'
```

## Useful flags

```bash
python3 app.py --chat-model llama3.1:8b
python3 app.py --knowledge-dir /path/to/company-docs
python3 app.py --top-k 6 "How do we handle support tickets?"
```

## Architecture

| File | Role |
|------|------|
| `app.py` | Core RAG engine (chunking, embeddings, retrieval, chat) |
| `server.py` | HTTP wrapper with CORS (`/health`, `/chat`, `/refresh`) |
| `ingest_local_sources.py` | Imports local Eko material into `knowledge/imported/` |
| `import_private_ops_data.py` | Pulls jobs/clients/invoices/stats via PostgREST or MCP |
| `refresh_all.sh` | Orchestrates refresh (`all \| local \| private \| jobs \| clients \| invoices \| stats`) |
| `start_assistant.sh` | Runs refresh then starts `server.py` |
| `deploy/lock28-ops-assistant.service` | systemd unit for production install |

## Environment Variables

See `deploy/lock28-assistant.env.example` and `SETUP.md` for full configuration.

Key overrides:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Ollama API endpoint |
| `OLLAMA_CHAT_MODEL` | `qwen3:8b` | Chat generation model |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text:latest` | Embedding model |
| `ASSISTANT_HOST` | `127.0.0.1` | HTTP bind address |
| `ASSISTANT_PORT` | `8008` | HTTP port |
| `EKO_POSTGREST_URL` | — | Internal PostgREST base URL |
| `EKO_SUPABASE_SCHEMA` | — | Database schema |
| `EKO_SUPABASE_ANON_KEY` | — | Anon key for PostgREST auth |

## Systemd Install

```bash
sudo mkdir -p /opt/lock28-assistant
sudo cp -r . /opt/lock28-assistant/
sudo cp deploy/lock28-ops-assistant.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now lock28-ops-assistant
```

Ensure `/opt/lock28-assistant/.env` exists with production values.

## Notes

- Intentionally small and local-first.
- Retrieval is local embedding-based search with a small on-disk cache in `.cache/`.
- Nothing here depends on hosted APIs for chat or embeddings.
- Private ops data refresh requires network access to your internal PostgREST or MCP endpoint.
