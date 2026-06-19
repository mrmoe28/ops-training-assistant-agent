#!/usr/bin/env python3
"""Import private Eko Solar Ops data via direct PostgREST or the MCP connector."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path


MCP_URL = os.environ.get(
    "EKO_MCP_URL",
    "https://ajjntevpwmwyocooqkfv.supabase.co/functions/v1/mcp",
)
TOKEN_FILE = Path(os.environ.get("EKO_MCP_TOKEN_FILE", "/home/mrmoe28/eko-mcp-connector-values.txt"))
POSTGREST_URL = os.environ.get("EKO_POSTGREST_URL", "http://192.168.50.105:54321/rest/v1")
SCHEMA = os.environ.get("EKO_SUPABASE_SCHEMA", "proj_75ce0d135acd4740")
PUBLIC_BUNDLE = Path(os.environ.get("EKO_PUBLIC_BUNDLE", "/tmp/ops_lock28_bundle.js"))
KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge" / "private_ops"


def load_token() -> str:
    env_token = os.environ.get("EKO_MCP_TOKEN", "").strip()
    if env_token:
        return env_token

    if not TOKEN_FILE.exists():
        raise RuntimeError("EKO MCP token not found in env or token file")

    text = TOKEN_FILE.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"eko_live_[a-zA-Z0-9]+", text)
    if not match:
        raise RuntimeError("Could not extract MCP token from token file")
    return match.group(0)


def load_anon_key() -> str:
    env_key = os.environ.get("EKO_SUPABASE_ANON_KEY", "").strip()
    if env_key:
        return env_key

    if not PUBLIC_BUNDLE.exists():
        raise RuntimeError("Public bundle not found for anon key extraction")

    text = PUBLIC_BUNDLE.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"Ee\(`https://supabase\.ekodevops\.com`,`([^`]+)`", text)
    if not match:
        raise RuntimeError("Could not extract anon key from public bundle")
    return match.group(1)


def rpc_call(token: str, method: str, params: dict | None = None, request_id: int = 1) -> dict:
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params or {},
    }
    request = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from MCP endpoint: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach MCP endpoint: {exc}") from exc

    if "error" in body:
        raise RuntimeError(f"MCP error for {method}: {body['error']}")
    return body["result"]


def call_tool(token: str, tool_name: str, arguments: dict | None = None, request_id: int = 10) -> object:
    result = rpc_call(
        token,
        "tools/call",
        {"name": tool_name, "arguments": arguments or {}},
        request_id=request_id,
    )
    content = result.get("content", [])
    if not content:
        return None
    text = content[0].get("text", "")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def rest_get(path: str, anon_key: str, query: dict[str, str]) -> object:
    qs = urllib.parse.urlencode(query, doseq=True, safe="(),.*")
    request = urllib.request.Request(
        f"{POSTGREST_URL}/{path}?{qs}",
        headers={
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}",
            "Accept-Profile": SCHEMA,
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from PostgREST: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach PostgREST endpoint: {exc}") from exc


def import_via_rest() -> tuple[list[dict], list[dict], list[dict], dict]:
    anon_key = load_anon_key()
    jobs = rest_get(
        "jobs",
        anon_key,
        {
            "select": "id,client,email,phone,address,status,type,source,created_at,updated_at,notes",
            "order": "updated_at.desc",
            "limit": "25",
        },
    )
    clients = rest_get(
        "jobs",
        anon_key,
        {
            "select": "id,client,email,phone,address,company_name,status,created_at,updated_at",
            "order": "updated_at.desc",
            "limit": "25",
        },
    )
    invoices = rest_get(
        "invoices",
        anon_key,
        {
            "select": "id,job_id,status,amount_cents,created_at",
            "order": "created_at.desc",
            "limit": "25",
        },
    )

    jobs_by_status: dict[str, int] = {}
    for job in jobs:
        status = job.get("status") or "UNKNOWN"
        jobs_by_status[status] = jobs_by_status.get(status, 0) + 1

    total_cents = 0
    paid_cents = 0
    for invoice in invoices:
        amount = invoice.get("amount_cents") or 0
        total_cents += amount
        if invoice.get("status") == "PAID":
            paid_cents += amount

    stats = {
        "jobs_by_status": jobs_by_status,
        "total_jobs": len(jobs),
        "total_revenue_cents": total_cents,
        "paid_revenue_cents": paid_cents,
    }
    return jobs, clients, invoices, stats


def empty_payload() -> tuple[list[dict], list[dict], list[dict], dict]:
    return [], [], [], {
        "jobs_by_status": {},
        "total_jobs": 0,
        "total_revenue_cents": 0,
        "paid_revenue_cents": 0,
    }


def write_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def format_jobs(jobs: list[dict]) -> str:
    lines = [
        "# Private Ops Jobs Snapshot",
        "",
        f"Imported from MCP. Count: {len(jobs)}",
        "",
    ]
    for job in jobs:
        lines.extend(
            [
                f"## {job.get('client') or 'Unnamed client'}",
                "",
                f"- id: {job.get('id')}",
                f"- status: {job.get('status')}",
                f"- type: {job.get('type')}",
                f"- source: {job.get('source')}",
                f"- email: {job.get('email')}",
                f"- phone: {job.get('phone')}",
                f"- address: {job.get('address')}",
                f"- updated_at: {job.get('updated_at')}",
                "",
                "Notes:",
                "",
                (job.get("notes") or "").strip() or "None",
                "",
            ]
        )
    return "\n".join(lines)


def format_recent_jobs_summary(jobs: list[dict]) -> str:
    lines = [
        "# Recent Ops Jobs Summary",
        "",
        "This file is optimized for questions about recent jobs in ops, current statuses, and latest updates.",
        "",
    ]
    for index, job in enumerate(jobs[:10], start=1):
        lines.append(
            f"{index}. client={job.get('client') or 'Unnamed client'} | "
            f"status={job.get('status')} | type={job.get('type')} | "
            f"updated_at={job.get('updated_at')} | id={job.get('id')}"
        )
    lines.append("")
    return "\n".join(lines)


def format_completed_jobs_summary(jobs: list[dict]) -> str:
    completed_jobs = [job for job in jobs if (job.get("status") or "").upper() == "COMPLETE"]
    lines = [
        "# Recent Completed Jobs Summary",
        "",
        "This file is optimized for questions about the latest completed job or recently completed work.",
        "",
    ]
    for index, job in enumerate(completed_jobs[:15], start=1):
        lines.append(
            f"{index}. client={job.get('client') or 'Unnamed client'} | "
            f"status={job.get('status')} | type={job.get('type')} | "
            f"address={job.get('address')} | updated_at={job.get('updated_at')} | id={job.get('id')}"
        )
    lines.append("")
    if completed_jobs:
        latest = completed_jobs[0]
        lines.extend(
            [
                f"Latest completed job by updated_at: client={latest.get('client') or 'Unnamed client'} | "
                f"type={latest.get('type')} | address={latest.get('address')} | "
                f"updated_at={latest.get('updated_at')} | id={latest.get('id')}",
                "",
            ]
        )
    return "\n".join(lines)


def format_clients(clients: list[dict]) -> str:
    lines = [
        "# Private Ops Clients Snapshot",
        "",
        f"Imported from MCP. Count: {len(clients)}",
        "",
    ]
    for client in clients:
        lines.extend(
            [
                f"## {client.get('client') or 'Unnamed client'}",
                "",
                f"- id: {client.get('id')}",
                f"- company_name: {client.get('company_name')}",
                f"- status: {client.get('status')}",
                f"- email: {client.get('email')}",
                f"- phone: {client.get('phone')}",
                f"- address: {client.get('address')}",
                f"- created_at: {client.get('created_at')}",
                "",
            ]
        )
    return "\n".join(lines)


def format_recent_clients_summary(clients: list[dict]) -> str:
    lines = [
        "# Recent Ops Clients Summary",
        "",
        "This file is optimized for questions about recent clients, contact details, and CRM status.",
        "",
    ]
    for index, client in enumerate(clients[:15], start=1):
        lines.append(
            f"{index}. client={client.get('client') or 'Unnamed client'} | "
            f"status={client.get('status')} | email={client.get('email')} | "
            f"phone={client.get('phone')} | company_name={client.get('company_name')} | "
            f"id={client.get('id')}"
        )
    lines.append("")
    return "\n".join(lines)


def format_invoices(invoices: list[dict]) -> str:
    lines = [
        "# Private Ops Invoices Snapshot",
        "",
        f"Imported from MCP. Count: {len(invoices)}",
        "",
    ]
    for invoice in invoices:
        amount_cents = invoice.get("amount_cents") or 0
        lines.extend(
            [
                f"## Invoice {invoice.get('id')}",
                "",
                f"- job_id: {invoice.get('job_id')}",
                f"- status: {invoice.get('status')}",
                f"- amount_cents: {amount_cents}",
                f"- amount_usd: ${amount_cents / 100:.2f}",
                f"- created_at: {invoice.get('created_at')}",
                "",
            ]
        )
    return "\n".join(lines)


def format_recent_invoices_summary(invoices: list[dict]) -> str:
    lines = [
        "# Recent Ops Invoices Summary",
        "",
        "This file is optimized for questions about recent invoices, amounts, and payment status.",
        "",
    ]
    for index, invoice in enumerate(invoices[:15], start=1):
        amount_cents = invoice.get("amount_cents") or 0
        lines.append(
            f"{index}. invoice_id={invoice.get('id')} | job_id={invoice.get('job_id')} | "
            f"status={invoice.get('status')} | amount_usd=${amount_cents / 100:.2f} | "
            f"created_at={invoice.get('created_at')}"
        )
    lines.append("")
    return "\n".join(lines)


def format_stats(stats: dict) -> str:
    lines = [
        "# Private Ops Dashboard Stats",
        "",
        f"- total_jobs: {stats.get('total_jobs')}",
        f"- total_revenue_cents: {stats.get('total_revenue_cents')}",
        f"- paid_revenue_cents: {stats.get('paid_revenue_cents')}",
        "",
        "## Jobs by Status",
        "",
    ]
    for status, count in sorted((stats.get("jobs_by_status") or {}).items()):
        lines.append(f"- {status}: {count}")
    lines.append("")
    return "\n".join(lines)


def format_status_board_summary(jobs: list[dict]) -> str:
    buckets = {
        "Pending": [],
        "In Progress": [],
        "Complete": [],
    }
    for job in jobs:
        status = (job.get("status") or "").upper()
        if status == "COMPLETE":
            buckets["Complete"].append(job)
        elif status == "IN_PROGRESS":
            buckets["In Progress"].append(job)
        else:
            buckets["Pending"].append(job)

    lines = [
        "# Status Board Summary",
        "",
        "This file is optimized for company-board style questions grouped into Pending, In Progress, and Complete.",
        "",
    ]
    for label, bucket_jobs in buckets.items():
        lines.append(f"## {label}")
        lines.append("")
        lines.append(f"count={len(bucket_jobs)}")
        lines.append("")
        for index, job in enumerate(bucket_jobs[:10], start=1):
            lines.append(
                f"{index}. client={job.get('client') or 'Unnamed client'} | "
                f"type={job.get('type')} | status={job.get('status')} | "
                f"address={job.get('address')} | updated_at={job.get('updated_at')} | id={job.get('id')}"
            )
        lines.append("")
    return "\n".join(lines)


def format_ops_brief(jobs: list[dict], invoices: list[dict], stats: dict) -> str:
    completed_jobs = [job for job in jobs if (job.get("status") or "").upper() == "COMPLETE"]
    in_progress_jobs = [job for job in jobs if (job.get("status") or "").upper() == "IN_PROGRESS"]
    pending_jobs = [job for job in jobs if (job.get("status") or "").upper() != "COMPLETE" and (job.get("status") or "").upper() != "IN_PROGRESS"]
    lines = [
        "# Ops Brief",
        "",
        "High-signal summary for quick operational questions.",
        "",
        f"- total_jobs_snapshot: {stats.get('total_jobs')}",
        f"- pending_jobs_snapshot: {len(pending_jobs)}",
        f"- in_progress_jobs_snapshot: {len(in_progress_jobs)}",
        f"- complete_jobs_snapshot: {len(completed_jobs)}",
        f"- total_revenue_snapshot_usd: ${(stats.get('total_revenue_cents') or 0) / 100:.2f}",
        f"- paid_revenue_snapshot_usd: ${(stats.get('paid_revenue_cents') or 0) / 100:.2f}",
        "",
        "## Top Recent Jobs",
        "",
    ]
    for job in jobs[:5]:
        lines.append(
            f"- {job.get('client') or 'Unnamed client'} | {job.get('status')} | "
            f"{job.get('type')} | updated {job.get('updated_at')}"
        )
    if completed_jobs:
        latest_completed = completed_jobs[0]
        lines.extend(
            [
                "",
                "## Latest Completed Job",
                "",
                f"- {latest_completed.get('client') or 'Unnamed client'} | {latest_completed.get('type')} | "
                f"{latest_completed.get('address')} | updated {latest_completed.get('updated_at')}",
            ]
        )
    lines.extend(["", "## Top Recent Invoices", ""])
    for invoice in invoices[:5]:
        amount_cents = invoice.get("amount_cents") or 0
        lines.append(
            f"- invoice {invoice.get('id')} | {invoice.get('status')} | "
            f"${amount_cents / 100:.2f} | created {invoice.get('created_at')}"
        )
    lines.append("")
    return "\n".join(lines)


def parse_scope() -> str:
    if len(sys.argv) < 2:
        return "all"
    return sys.argv[1].strip().lower()


def main() -> int:
    scope = parse_scope()
    valid_scopes = {"all", "jobs", "clients", "invoices", "stats"}
    if scope not in valid_scopes:
        raise SystemExit(f"Unsupported scope '{scope}'. Use one of: {', '.join(sorted(valid_scopes))}")

    mode = os.environ.get("EKO_IMPORT_MODE", "rest").strip().lower()
    if mode == "mcp":
        token = load_token()
        rpc_call(token, "initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "ollama-local-poc", "version": "1.0.0"}}, request_id=1)
        rpc_call(token, "tools/list", {}, request_id=2)
        jobs, clients, invoices, stats = empty_payload()
        if scope in {"all", "jobs"}:
            jobs = call_tool(token, "list_jobs", {"limit": 25}, request_id=10) or []
        if scope in {"all", "clients"}:
            clients = call_tool(token, "list_clients", {"limit": 25}, request_id=11) or []
        if scope in {"all", "invoices"}:
            invoices = call_tool(token, "list_invoices", {"limit": 25}, request_id=12) or []
        if scope in {"all", "stats"}:
            stats = call_tool(token, "get_stats", {}, request_id=13) or {}
    else:
        jobs, clients, invoices, stats = import_via_rest()

    if scope in {"all", "jobs"}:
        write_markdown(KNOWLEDGE_DIR / "jobs.md", format_jobs(jobs))
        write_markdown(KNOWLEDGE_DIR / "recent_jobs_summary.md", format_recent_jobs_summary(jobs))
        write_markdown(KNOWLEDGE_DIR / "completed_jobs_summary.md", format_completed_jobs_summary(jobs))
        write_markdown(KNOWLEDGE_DIR / "status_board_summary.md", format_status_board_summary(jobs))
    if scope in {"all", "clients"}:
        write_markdown(KNOWLEDGE_DIR / "clients.md", format_clients(clients))
        write_markdown(KNOWLEDGE_DIR / "recent_clients_summary.md", format_recent_clients_summary(clients))
    if scope in {"all", "invoices"}:
        write_markdown(KNOWLEDGE_DIR / "invoices.md", format_invoices(invoices))
        write_markdown(KNOWLEDGE_DIR / "recent_invoices_summary.md", format_recent_invoices_summary(invoices))
    if scope in {"all", "stats"}:
        write_markdown(KNOWLEDGE_DIR / "stats.md", format_stats(stats))

    if scope == "all":
        write_markdown(KNOWLEDGE_DIR / "ops_brief.md", format_ops_brief(jobs, invoices, stats))
    elif scope in {"jobs", "invoices", "stats"}:
        # Keep the brief in sync for the most common ops questions.
        if mode == "mcp":
            token = load_token()
            if scope != "jobs":
                jobs = call_tool(token, "list_jobs", {"limit": 25}, request_id=20) or jobs
            if scope != "invoices":
                invoices = call_tool(token, "list_invoices", {"limit": 25}, request_id=21) or invoices
            if scope != "stats":
                stats = call_tool(token, "get_stats", {}, request_id=22) or stats
        else:
            all_jobs, _all_clients, all_invoices, all_stats = import_via_rest()
            jobs = all_jobs if scope != "jobs" else jobs
            invoices = all_invoices if scope != "invoices" else invoices
            stats = all_stats if scope != "stats" else stats
        write_markdown(KNOWLEDGE_DIR / "ops_brief.md", format_ops_brief(jobs, invoices, stats))

    print(f"Wrote private ops data to {KNOWLEDGE_DIR} for scope={scope}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
