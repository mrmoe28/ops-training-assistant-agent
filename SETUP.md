# Setup & Run Guide

## 1. Clone

```bash
git clone https://github.com/mrmoe28/ops-training-assistant-agent.git
cd ops-training-assistant-agent
```

## 2. Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) running locally (default: `http://127.0.0.1:11434`)
- Models pulled:
  ```bash
  ollama pull qwen3:8b
  ollama pull nomic-embed-text:latest
  ```

## 3. Environment (optional)

Copy the example and edit:

```bash
cp deploy/lock28-assistant.env.example .env
```

Key overrides:

| Var | Default | Purpose |
|-----|---------|---------|
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Ollama endpoint |
| `OLLAMA_CHAT_MODEL` | `qwen3:8b` | Chat model |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text:latest` | Embedding model |
| `ASSISTANT_HOST` | `127.0.0.1` | HTTP server bind address |
| `ASSISTANT_PORT` | `8008` | HTTP server port |
| `EKO_POSTGREST_URL` | — | Internal PostgREST for ops data |
| `EKO_SUPABASE_SCHEMA` | — | Schema name |
| `EKO_SUPABASE_ANON_KEY` | — | Anon key for PostgREST |

## 4. Quick Start

```bash
# Refresh knowledge (local + private ops data)
./refresh_all.sh

# Start the HTTP server
./start_assistant.sh
```

Server listens on `http://127.0.0.1:8008` by default.

## 5. API Endpoints

| Endpoint | Method | Payload | Response |
|----------|--------|---------|----------|
| `/health` | GET | — | `{ok, chat_model, embed_model, knowledge_dir}` |
| `/chat` | POST | `{"question": "...", "history": [...], "context": {...}, "top_k": 4}` | `{reply, sources}` |
| `/refresh` | POST | — | `{ok}` |

## 6. Targeted Refresh

```bash
./refresh_all.sh local       # public site + training docs only
./refresh_all.sh private     # ops jobs/clients/invoices/stats
./refresh_all.sh jobs        # jobs only
./refresh_all.sh clients     # clients only
./refresh_all.sh invoices    # invoices only
./refresh_all.sh stats       # stats only
```

## 7. CLI Mode (no server)

```bash
python3 app.py "What services does Eko Solar offer?"
```

Interactive:

```bash
python3 app.py
```

## 8. Systemd Install (Linux)

```bash
sudo mkdir -p /opt/lock28-assistant
sudo cp -r . /opt/lock28-assistant/
sudo cp deploy/lock28-ops-assistant.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now lock28-ops-assistant
```

Ensure `/opt/lock28-assistant/.env` exists with production values.

## 9. Troubleshooting

| Symptom | Fix |
|---------|-----|
| "No embeddings returned" | Pull the embedding model: `ollama pull nomic-embed-text:latest` |
| "Could not reach Ollama" | Verify Ollama is running: `curl http://127.0.0.1:11434/api/tags` |
| Missing ops data | Check `EKO_POSTGREST_URL` and `EKO_SUPABASE_ANON_KEY` |
| Port 8008 in use | `ASSISTANT_PORT=9000 ./start_assistant.sh` |
