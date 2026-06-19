#!/usr/bin/env python3
"""Small local HTTP wrapper for the Ollama PoC assistant."""

from __future__ import annotations

import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from app import (
    DEFAULT_CACHE_DIR,
    DEFAULT_CHAT_MODEL,
    DEFAULT_EMBED_MODEL,
    DEFAULT_KNOWLEDGE_DIR,
    DEFAULT_OLLAMA_URL,
    ask_ollama,
    build_index,
    embed_texts,
    retrieve,
)


HOST = os.environ.get("ASSISTANT_HOST", "127.0.0.1")
PORT = int(os.environ.get("ASSISTANT_PORT", "8008"))
ALLOWED_ORIGIN = os.environ.get("ASSISTANT_ALLOWED_ORIGIN", "*")


class AssistantService:
    def __init__(self) -> None:
        self.base_url = os.environ.get("OLLAMA_URL", DEFAULT_OLLAMA_URL)
        self.chat_model = os.environ.get("OLLAMA_CHAT_MODEL", DEFAULT_CHAT_MODEL)
        self.embed_model = os.environ.get("OLLAMA_EMBED_MODEL", DEFAULT_EMBED_MODEL)
        self.knowledge_dir = Path(os.environ.get("ASSISTANT_KNOWLEDGE_DIR", str(DEFAULT_KNOWLEDGE_DIR)))
        self.cache_dir = Path(os.environ.get("ASSISTANT_CACHE_DIR", str(DEFAULT_CACHE_DIR)))
        self.top_k = int(os.environ.get("ASSISTANT_TOP_K", "4"))
        self._chunks = []
        self._documents: dict[str, str] = {}
        self.refresh()

    def refresh(self) -> None:
        self._chunks = build_index(
            self.base_url,
            self.knowledge_dir,
            self.embed_model,
            self.cache_dir,
        )
        self._documents = self._load_documents()

    def _load_documents(self) -> dict[str, str]:
        docs: dict[str, str] = {}
        for path in sorted(self.knowledge_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".md", ".txt", ".html"}:
                continue
            try:
                docs[str(path.relative_to(self.knowledge_dir))] = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
        return docs

    def _latest_completed_job(self) -> dict[str, str] | None:
        text = self._documents.get("private_ops/completed_jobs_summary.md", "")
        for line in text.splitlines():
            if not re.match(r"^\d+\.\s", line):
                continue
            fields: dict[str, str] = {}
            for part in re.split(r"\s+\|\s+", re.sub(r"^\d+\.\s*", "", line)):
                if "=" in part:
                    key, value = part.split("=", 1)
                    fields[key.strip()] = value.strip()
            if fields:
                return fields
        return None

    def _shortcut_answer(self, question: str, context: dict[str, object] | None = None) -> dict[str, object] | None:
        normalized = " ".join(question.lower().split())
        if any(phrase in normalized for phrase in ("last completed job", "latest completed job", "most recent completed job")):
            latest = self._latest_completed_job()
            if latest:
                current_job = context.get("current_job") if isinstance(context, dict) else None
                if isinstance(current_job, dict) and str(current_job.get("status", "")).upper() == "COMPLETE":
                    reply = (
                        f"Globally, the latest completed job is {latest.get('type', 'Unknown type')} for "
                        f"{latest.get('client', 'Unknown client')} at {latest.get('address', 'Unknown address')} "
                        f"(updated {latest.get('updated_at', 'unknown time')}) [1]. "
                        f"If you mean the job open on screen, that one is {current_job.get('type', 'Unknown type')} for "
                        f"{current_job.get('client', 'Unknown client')} at {current_job.get('address', 'Unknown address')} "
                        f"(updated {current_job.get('updated_at', 'unknown time')})."
                    )
                else:
                    reply = (
                        f"The latest completed job is {latest.get('type', 'Unknown type')} for "
                        f"{latest.get('client', 'Unknown client')} at {latest.get('address', 'Unknown address')} "
                        f"(updated {latest.get('updated_at', 'unknown time')}) [1]."
                    )
                return {
                    "reply": reply,
                    "sources": [{"source": "private_ops/completed_jobs_summary.md#chunk-1", "score": 1.0}],
                }
        return None

    def answer(
        self,
        question: str,
        history: list[dict[str, str]] | None = None,
        context: dict[str, object] | None = None,
        top_k: int | None = None,
    ) -> dict[str, object]:
        shortcut = self._shortcut_answer(question, context)
        if shortcut:
            return shortcut

        query_embedding = embed_texts(self.base_url, self.embed_model, [question])[0]
        retrieved = retrieve(self._chunks, query_embedding, top_k=top_k or self.top_k)

        context_blocks = []
        sources = []
        for index, (score, chunk) in enumerate(retrieved, start=1):
            context_blocks.append(
                f"[{index}] source={chunk.source} score={score:.3f}\n{chunk.text}"
            )
            sources.append({"source": chunk.source, "score": round(score, 3)})

        system = (
            "You are a company assistant answering from local knowledge snippets. "
            "Use only the provided context when stating company-specific facts. "
            "Prefer organizing operational answers using the company-board buckets Pending, In Progress, and Complete when that fits the question. "
            "For time-based job questions like latest, last, or most recent, prefer explicit summary lines that mention updated_at. "
            "If the answer is not supported by the context, say so plainly. "
            "Cite the relevant snippet numbers like [1] or [2]."
        )
        history_lines: list[str] = []
        for item in (history or [])[-8:]:
            role = item.get("role", "").strip().lower()
            content = item.get("content", "").strip()
            if role in {"user", "assistant"} and content:
                history_lines.append(f"{role.title()}: {content}")
        context_lines: list[str] = []
        current_job = context.get("current_job") if isinstance(context, dict) else None
        if isinstance(current_job, dict):
            context_lines.append(
                "Current job on screen: "
                f"client={current_job.get('client')} | "
                f"status={current_job.get('status')} | "
                f"type={current_job.get('type')} | "
                f"address={current_job.get('address')} | "
                f"updated_at={current_job.get('updated_at')}"
            )
        prompt = (
            "Context:\n"
            + os.linesep.join(context_blocks)
            + ("\n\nCurrent app context:\n" + os.linesep.join(context_lines) if context_lines else "")
            + ("\n\nConversation so far:\n" + os.linesep.join(history_lines) if history_lines else "")
            + "\n\nQuestion:\n"
            + question
            + "\n\nAnswer with short, direct wording and include citations."
        )
        reply = ask_ollama(self.base_url, self.chat_model, system, prompt)
        return {"reply": reply, "sources": sources}


SERVICE = AssistantService()


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send(
                200,
                {
                    "ok": True,
                    "chat_model": SERVICE.chat_model,
                    "embed_model": SERVICE.embed_model,
                    "knowledge_dir": str(SERVICE.knowledge_dir),
                },
            )
            return
        self._send(404, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send(400, {"error": "Invalid JSON"})
            return

        if self.path == "/chat":
            question = str(payload.get("question", "")).strip()
            if not question:
                self._send(400, {"error": "question is required"})
                return
            top_k = payload.get("top_k")
            history = payload.get("history")
            context = payload.get("context")
            result = SERVICE.answer(
                question,
                history if isinstance(history, list) else None,
                context if isinstance(context, dict) else None,
                int(top_k) if top_k is not None else None,
            )
            self._send(200, result)
            return

        if self.path == "/refresh":
            SERVICE.refresh()
            self._send(200, {"ok": True})
            return

        self._send(404, {"error": "Not found"})


def main() -> int:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Assistant server listening on http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
