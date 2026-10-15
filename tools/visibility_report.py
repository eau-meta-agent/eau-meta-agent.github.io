#!/usr/bin/env python3
"""Report real search retrieval and citation observations by provider.

Blank values mean unknown; do not count them as a negative result.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def boolean(value):
    value = value.strip().lower()
    if value in {"1", "true", "yes"}:
        return True
    if value in {"0", "false", "no"}:
        return False
    if not value:
        return None
    raise ValueError(f"Invalid boolean: {value}")


def rank(value):
    value = value.strip()
    if not value:
        return None
    result = int(value)
    if result < 0:
        raise ValueError("Rank must be 0 (absent) or a positive result position")
    return result


def rate(values):
    known = [v for v in values if v is not None]
    return {"numerator": sum(known), "denominator": len(known),
            "rate": round(sum(known) / len(known), 3) if known else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("observations", type=Path)
    args = parser.parse_args()
    with args.observations.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    required = {"date", "phase", "provider", "query", "project_rank", "paper_rank", "eau_mentioned", "project_cited", "paper_cited", "answer_accurate"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"CSV needs at least one row and columns: {', '.join(sorted(required))}")
    grouped = defaultdict(list)
    for row in rows:
        if row["phase"] not in {"before", "after"}:
            raise ValueError("phase must be before or after")
        grouped[(row["provider"], row["phase"])].append(row)
    report = {}
    for (provider, phase), samples in grouped.items():
        project_rank = [rank(row["project_rank"]) for row in samples]
        paper_rank = [rank(row["paper_rank"]) for row in samples]
        report.setdefault(provider, {})[phase] = {
            "queries": len(samples),
            "project_retrieval_at_10": rate([None if r is None else 0 < r <= 10 for r in project_rank]),
            "paper_retrieval_at_10": rate([None if r is None else 0 < r <= 10 for r in paper_rank]),
            "eau_mention": rate([boolean(row["eau_mentioned"]) for row in samples]),
            "project_citation": rate([boolean(row["project_cited"]) for row in samples]),
            "paper_citation": rate([boolean(row["paper_cited"]) for row in samples]),
            "answer_accuracy": rate([boolean(row["answer_accurate"]) for row in samples]),
        }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
