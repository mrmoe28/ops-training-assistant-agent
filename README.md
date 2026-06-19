# Local Ollama PoC

Small local RAG proof of concept against a local Ollama endpoint.

## What it does

- uses a local chat model: `qwen3:8b`
- uses a local embedding model: `nomic-embed-text:latest`
- reads local documents from `knowledge/`
- retrieves the most relevant chunks with local embeddings
- asks the chat model to answer with citations

## Run it

```bash
cd /home/mrmoe28/ollama-local-poc
python3 ingest_local_sources.py
OLLAMA_URL=http://127.0.0.1:11434 python3 app.py "What services does Eko Solar offer?"
```

One-command refresh for both local docs and private ops data:

```bash
cd /home/mrmoe28/ollama-local-poc
./refresh_all.sh
```

Targeted refresh commands:

```bash
./refresh_all.sh local
./refresh_all.sh private
./refresh_all.sh jobs
./refresh_all.sh invoices
./refresh_all.sh clients
./refresh_all.sh stats
```

Interactive mode:

```bash
cd /home/mrmoe28/ollama-local-poc
OLLAMA_URL=http://127.0.0.1:11434 python3 app.py
```

## Swap in your real company data

Replace the files in `knowledge/` with:

- website copy
- FAQs
- internal SOPs
- pricing docs
- sales notes

Supported file types:

- `.md`
- `.txt`
- `.html`

You can also import the local Eko Solar source material already on this machine:

```bash
cd /home/mrmoe28/ollama-local-poc
python3 ingest_local_sources.py
```

To import private ops data through the existing MCP connector:

```bash
cd /home/mrmoe28/ollama-local-poc
python3 import_private_ops_data.py
python3 import_private_ops_data.py jobs
python3 import_private_ops_data.py invoices
```

This uses the existing Eko MCP bearer token already present on this machine unless you override it with `EKO_MCP_TOKEN`.

In this environment, the importer defaults to the reachable internal Supabase API:

- `http://192.168.50.105:54321/rest/v1`

You can override that with `EKO_POSTGREST_URL` if the internal host changes.

## Useful flags

```bash
OLLAMA_URL=http://127.0.0.1:11434 python3 app.py --chat-model llama3.1:8b
OLLAMA_URL=http://127.0.0.1:11434 python3 app.py --knowledge-dir /path/to/company-docs
OLLAMA_URL=http://127.0.0.1:11434 python3 app.py --top-k 6 "How do we handle support tickets?"
```

## Notes

- This is intentionally small and local-first.
- Retrieval is local embedding-based search with a small on-disk cache in `.cache/`.
- Nothing here depends on hosted APIs.
