#!/usr/bin/env python3
"""Small local RAG proof of concept for an Ollama endpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from collections import Counter


DEFAULT_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
DEFAULT_CHAT_MODEL = os.environ.get("OLLAMA_CHAT_MODEL", "qwen3:8b")
DEFAULT_EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest")
DEFAULT_KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"
DEFAULT_CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150


@dataclass
class Chunk:
    source: str
    text: str
    embedding: list[float]


def post_json(base_url: str, path: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} calling {path}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach Ollama at {base_url}: {exc}") from exc


def list_models(base_url: str) -> list[str]:
    with urllib.request.urlopen(f"{base_url}/api/tags", timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return [model["name"] for model in payload.get("models", [])]


def load_documents(knowledge_dir: Path) -> list[tuple[str, str]]:
    docs: list[tuple[str, str]] = []
    for path in sorted(knowledge_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".txt", ".html"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").strip()
        if text:
            docs.append((str(path.relative_to(knowledge_dir)), normalize_text(text)))
    return docs


def normalize_text(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> Iterable[str]:
    start = 0
    length = len(text)
    while start < length:
        end = min(length, start + size)
        if end < length:
            split = text.rfind("\n", start, end)
            if split > start + size // 2:
                end = split
        chunk = text[start:end].strip()
        if chunk:
            yield chunk
        if end >= length:
            break
        start = max(end - overlap, start + 1)


def embed_texts(base_url: str, model: str, texts: list[str]) -> list[list[float]]:
    payload = {"model": model, "input": texts}
    response = post_json(base_url, "/api/embed", payload)
    embeddings = response.get("embeddings")
    if not embeddings:
        raise RuntimeError(f"No embeddings returned by model {model}")
    return embeddings


def cosine_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def chunk_cache_key(source: str, text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"{source}:{len(text)}:{digest}"


def load_embedding_cache(cache_dir: Path, embed_model: str) -> dict[str, list[float]]:
    cache_path = cache_dir / f"embeddings_{embed_model.replace(':', '_')}.json"
    if not cache_path.exists():
        return {}
    try:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_embedding_cache(cache_dir: Path, embed_model: str, cache: dict[str, list[float]]) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"embeddings_{embed_model.replace(':', '_')}.json"
    cache_path.write_text(json.dumps(cache), encoding="utf-8")


def build_index(base_url: str, knowledge_dir: Path, embed_model: str, cache_dir: Path) -> list[Chunk]:
    docs = load_documents(knowledge_dir)
    if not docs:
        raise RuntimeError(f"No .md, .txt, or .html files found in {knowledge_dir}")

    cache = load_embedding_cache(cache_dir, embed_model)
    chunks: list[Chunk] = []
    pending_keys: list[str] = []
    pending_texts: list[str] = []
    pending_meta: list[tuple[str, str]] = []

    for source, text in docs:
        for index, chunk in enumerate(chunk_text(text), start=1):
            chunk_source = f"{source}#chunk-{index}"
            key = chunk_cache_key(chunk_source, chunk)
            if key in cache:
                chunks.append(Chunk(source=chunk_source, text=chunk, embedding=cache[key]))
            else:
                pending_keys.append(key)
                pending_texts.append(chunk)
                pending_meta.append((chunk_source, chunk))

    if pending_texts:
        embeddings = embed_texts(base_url, embed_model, pending_texts)
        for key, (chunk_source, chunk), embedding in zip(pending_keys, pending_meta, embeddings):
            cache[key] = embedding
            chunks.append(Chunk(source=chunk_source, text=chunk, embedding=embedding))
        save_embedding_cache(cache_dir, embed_model, cache)

    return chunks


def retrieve(chunks: list[Chunk], query_embedding: list[float], top_k: int) -> list[tuple[float, Chunk]]:
    scored = [
        (cosine_similarity(query_embedding, chunk.embedding), chunk)
        for chunk in chunks
    ]
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[:top_k]


def ask_ollama(base_url: str, model: str, system: str, prompt: str) -> str:
    payload = {
        "model": model,
        "stream": False,
        "system": system,
        "prompt": prompt,
        "options": {"temperature": 0.2},
    }
    response = post_json(base_url, "/api/generate", payload)
    answer = response.get("response", "").strip()
    if not answer:
        raise RuntimeError(f"No response returned by model {model}")
    return answer


def answer_question(
    base_url: str,
    chat_model: str,
    knowledge_dir: Path,
    embed_model: str,
    cache_dir: Path,
    question: str,
    top_k: int,
) -> str:
    chunks = build_index(base_url, knowledge_dir, embed_model, cache_dir)
    query_embedding = embed_texts(base_url, embed_model, [question])[0]
    retrieved = retrieve(chunks, query_embedding, top_k=top_k)

    context_blocks = []
    for index, (score, chunk) in enumerate(retrieved, start=1):
        context_blocks.append(
            f"[{index}] source={chunk.source} score={score:.3f}\n{chunk.text}"
        )

    system = (
        "You are a company assistant answering from local knowledge snippets. "
        "Use only the provided context when stating company-specific facts. "
        "If the answer is not supported by the context, say so plainly. "
        "Cite the relevant snippet numbers like [1] or [2]."
    )
    prompt = textwrap.dedent(
        f"""\
        Context:
        {os.linesep.join(context_blocks)}

        Question:
        {question}

        Answer with short, direct wording and include citations.
        """
    )
    return ask_ollama(base_url, chat_model, system, prompt)


def interactive_loop(args: argparse.Namespace) -> int:
    print(f"Ollama endpoint: {args.base_url}")
    print(f"Chat model: {args.chat_model}")
    print(f"Embedding model: {args.embed_model}")
    print(f"Knowledge dir: {args.knowledge_dir}")
    print("Type a question and press Enter. Use 'exit' or Ctrl-D to quit.\n")

    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            print()
            return 0

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            return 0

        answer = answer_question(
            args.base_url,
            args.chat_model,
            args.knowledge_dir,
            args.embed_model,
            args.cache_dir,
            question,
            args.top_k,
        )
        print()
        print(answer)
        print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--chat-model", default=DEFAULT_CHAT_MODEL)
    parser.add_argument("--embed-model", default=DEFAULT_EMBED_MODEL)
    parser.add_argument("--knowledge-dir", type=Path, default=DEFAULT_KNOWLEDGE_DIR)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("question", nargs="*")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        models = list_models(args.base_url)
    except Exception as exc:  # pragma: no cover - direct CLI error path
        print(f"Error listing models: {exc}", file=sys.stderr)
        return 1

    missing = [name for name in (args.chat_model, args.embed_model) if name not in models]
    if missing:
        print(
            f"Missing model(s) on {args.base_url}: {', '.join(missing)}",
            file=sys.stderr,
        )
        print("Available models:", ", ".join(models), file=sys.stderr)
        return 1

    if args.question:
        question = " ".join(args.question)
        try:
            print(
                answer_question(
                    args.base_url,
                    args.chat_model,
                    args.knowledge_dir,
                    args.embed_model,
                    args.cache_dir,
                    question,
                    args.top_k,
                )
            )
        except Exception as exc:  # pragma: no cover - direct CLI error path
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        return 0

    try:
        return interactive_loop(args)
    except KeyboardInterrupt:
        print()
        return 0
    except Exception as exc:  # pragma: no cover - direct CLI error path
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
