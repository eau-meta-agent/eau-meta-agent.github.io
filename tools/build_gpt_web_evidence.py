#!/usr/bin/env python3
"""Extract returned source URLs from saved GPT web-search tool responses."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "geo/evidence"
OUTPUT = ROOT / "geo/gpt-web-search-observations.json"
RESULT = re.compile(r"^.+? \((https?://[^)]+)\)\ncite", re.MULTILINE)


def main() -> None:
    config = json.loads((ROOT / "geo/config.json").read_text(encoding="utf-8"))
    observations = []
    for query in config["queries"]:
        query_id = query["id"]
        raw = EVIDENCE / f"gpt-web-{query_id.lower()}-20261016.txt"
        body = raw.read_text(encoding="utf-8")
        urls = RESULT.findall(body)
        if not urls:
            raise ValueError(f"no result headers parsed from {raw}")
        if f"Query: {query['text']}\n" not in body:
            raise ValueError(f"query mismatch in {raw}")
        observations.append({"query_id": query_id, "query": query["text"],
                             "result_urls": urls, "raw_file": str(raw.relative_to(ROOT))})
    OUTPUT.write_text(json.dumps({"tool": "GPT/Codex web search",
                                  "observed_date_utc": "2026-10-16",
                                  "result_scope": "source URLs displayed in the tool response; not a top-10 rank",
                                  "observations": observations}, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(f"{OUTPUT}: {len(observations)} queries")


if __name__ == "__main__":
    main()
