#!/usr/bin/env python3
"""Import local Eko Solar source material into the PoC knowledge folder."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("/home/mrmoe28")
POC_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = POC_DIR / "knowledge" / "imported"

QUOTE_PROMPT = ROOT / "eko-ops-claude-project-prompt.md"
TRAINING_README = ROOT / "solar-assistant-training" / "data" / "README.md"
TRAINING_JSONL = ROOT / "solar-assistant-training" / "data" / "solar_training_data.jsonl"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def import_quote_prompt() -> None:
    text = QUOTE_PROMPT.read_text(encoding="utf-8")
    write_text(KNOWLEDGE_DIR / "eko_ops_quote_prompt.md", text)


def import_training_readme() -> None:
    text = TRAINING_README.read_text(encoding="utf-8")
    write_text(KNOWLEDGE_DIR / "training_data_guide.md", text)


def import_training_examples(limit: int = 12) -> None:
    raw_lines = TRAINING_JSONL.read_text(encoding="utf-8").splitlines()
    sections: list[str] = [
        "# Eko Solar Training Examples",
        "",
        "These examples are imported from the local training dataset and reflect target workflows, outputs, and business conventions.",
        "",
    ]

    for index, line in enumerate(raw_lines[:limit], start=1):
        record = json.loads(line)
        output = record["output"]
        try:
            output = json.dumps(json.loads(output), indent=2)
        except json.JSONDecodeError:
            pass

        sections.extend(
            [
                f"## Example {index}: {record['instruction']}",
                "",
                "### Input",
                "",
                record["input"],
                "",
                "### Output",
                "",
                "```json",
                output,
                "```",
                "",
            ]
        )

    write_text(KNOWLEDGE_DIR / "training_examples.md", "\n".join(sections))


def main() -> int:
    import_quote_prompt()
    import_training_readme()
    import_training_examples()
    print(f"Wrote imported knowledge files to {KNOWLEDGE_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
