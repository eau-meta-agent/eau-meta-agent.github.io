#!/usr/bin/env python3
"""Render the visible top-level EAU GEO exploration branches as a static SVG."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "geo"


def main() -> None:
    data = json.loads((GEO / "exploration-tree.json").read_text(encoding="utf-8"))
    # Static overview shows the actual visible path. The HTML expands every intervention and node.
    root = {"label": "EAU 项目页曝光", "detail": "项目 URL 0/4", "type": "root", "children": []}
    observed = {"label": data["tool"], "detail": "真实返回的来源 URL", "type": "tool", "children": []}
    for query in data["queries"]:
        q = {"label": query["id"], "detail": query["text"], "type": "query", "children": []}
        for source in query["sources"]:
            s = {"label": "arXiv 论文页" if "arxiv.org" in source["url"] else source["url"],
                 "detail": source["url"], "type": "source", "children": []}
            for intervention in source["interventions"]:
                s["children"].append({"label": "论文 → 项目页链接" if intervention["id"] == "paper_to_project_backlink"
                                      else intervention["id"],
                                      "detail": "下一测试 #1 · 效果未测" if intervention["next_test_order"] == 1
                                      else "效果未测", "type": "candidate", "children": []})
            q["children"].append(s)
        observed["children"].append(q)
    root["children"] = [
        observed,
        {"label": f'未观测入口 ({len(data["unobserved_entry_points"])})',
         "detail": "保持未排序", "type": "dormant", "children": []},
        {"label": f'其余依赖图节点 ({len(data["unmapped_nodes"])})',
         "detail": "可在 HTML 中展开", "type": "group", "children": []},
    ]
    box_w, box_h, dx, dy = 200, 56, 238, 82
    leaf = 0
    nodes: list[dict] = []
    edges: list[tuple[dict, dict]] = []

    def place(node: dict, depth: int) -> None:
        nonlocal leaf
        node["x"] = 24 + depth * dx
        nodes.append(node)
        if not node["children"]:
            node["y"] = 92 + leaf * dy
            leaf += 1
        else:
            for child in node["children"]:
                place(child, depth + 1)
                edges.append((node, child))
            node["y"] = (node["children"][0]["y"] + node["children"][-1]["y"]) / 2

    place(root, 0)
    width = max(n["x"] for n in nodes) + box_w + 28
    height = 160 + leaf * dy
    colors = {"root": "#264b3a", "tool": "#39745a", "query": "#4a6579",
              "source": "#4c7f74", "candidate": "#a0582d", "dormant": "#886b51",
              "group": "#6c7282"}
    pieces = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
              'role="img" aria-label="EAU GEO 搜索证据与实验树">',
              '<rect width="100%" height="100%" fill="#f6f5f1"/>',
              '<text x="24" y="42" style="font:700 25px system-ui,sans-serif;fill:#264b3a">EAU GEO：真实搜索证据树</text>',
              '<text x="24" y="66" style="font:13px system-ui,sans-serif;fill:#5e6d62">橙色是待测干预；灰色分支没有真实入口证据。节点与连线不代表曝光因果关系。</text>']
    for parent, child in edges:
        x1, y1 = parent["x"] + box_w, parent["y"] + box_h / 2
        x2, y2 = child["x"], child["y"] + box_h / 2
        mid = (x1 + x2) / 2
        pieces.append(f'<path d="M{x1} {y1} H{mid} V{y2} H{x2}" fill="none" '
                      'stroke="#a4b5a7" stroke-width="2"/>')
    for node in nodes:
        x, y = node["x"], node["y"]
        label = node["label"][:23] + ("…" if len(node["label"]) > 23 else "")
        detail = node["detail"][:29] + ("…" if len(node["detail"]) > 29 else "")
        pieces.extend([
            f'<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="9" fill="{colors[node["type"]]}"/>',
            f'<text x="{x + 12}" y="{y + 23}" style="font:700 14px system-ui,sans-serif;fill:white">{escape(label)}</text>',
            f'<text x="{x + 12}" y="{y + 42}" style="font:11px system-ui,sans-serif;fill:#edf4ef">{escape(detail)}</text>',
        ])
    pieces.append("</svg>")
    target = GEO / "figures" / "geo-exploration-overview.svg"
    target.write_text("".join(pieces), encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
