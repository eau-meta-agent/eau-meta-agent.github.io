#!/usr/bin/env python3
"""Render the audited EAU GEO decision trace as a standalone SVG."""

from __future__ import annotations

import csv
import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "geo"


def card(x: int, y: int, width: int, title: str, lines: list[str], color: str) -> str:
    height = 104
    parts = [f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="12" fill="{color}"/>',
             f'<text x="{x + 14}" y="{y + 28}" class="title">{escape(title)}</text>']
    for index, line in enumerate(lines):
        parts.append(f'<text x="{x + 14}" y="{y + 54 + index * 20}" class="body">{escape(line)}</text>')
    return "".join(parts)


def arrow(x1: int, y1: int, x2: int, y2: int, *, dashed: bool = False) -> str:
    dash = ' stroke-dasharray="7 6"' if dashed else ""
    return (f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="#80978b" '
            f'stroke-width="2.5" marker-end="url(#arrow)"{dash}/>')


def main() -> None:
    with (GEO / "henry-run-results.tsv").open(newline="", encoding="utf-8") as handle:
        rows = {row["candidate_id"]: row for row in csv.DictReader(handle, delimiter="\t")}
    evidence = json.loads((GEO / "gpt-web-search-observations.json").read_text(encoding="utf-8"))
    graph = json.loads((GEO / "baseline-graph.json").read_text(encoding="utf-8"))
    priorities = json.loads((GEO / "priorities.json").read_text(encoding="utf-8"))
    queries = evidence["observations"]
    project = "https://eau-meta-agent.github.io/"
    paper = "https://arxiv.org/abs/2610.16523"
    project_count = sum(any(url.rstrip("/") == project.rstrip("/") for url in q["result_urls"])
                        for q in queries)
    paper_count = sum(paper in q["result_urls"] for q in queries)
    paper_priority = next(item for item in priorities["interventions"]
                          if item["id"] == "paper_to_project_backlink")
    assert paper_priority["next_test_order"] == 1
    assert rows["candidate-001"]["status"] == "keep"
    assert rows["candidate-002"]["status"] == "discard"

    nodes = [
        card(390, 80, 300, "目标：项目页被检索与引用", ["目标 URL：eau-meta-agent.github.io", "论文与项目页分开计数"], "#254f3c"),
        card(390, 210, 300, f'依赖图：{len(graph["nodes"])} 节点 / {len(graph["edges"])} 边',
             ["定位 README、首页、论文入口", "边是结构关系，不是曝光证明"], "#3f7358"),
        card(390, 340, 300, "历史选择：先试 README", ["依据旧结构启发式与内容缺口", "发生在真实搜索排序上线之前"], "#687486"),
        card(390, 470, 300, f'基线：本地 {rows["seed"]["metric_value"]}/100',
             ["seed 工作树", "指标仅是本地 GEO readiness"], "#687486"),
        card(60, 610, 300, "candidate-001：保留", ["README 加项目页 / 论文链接", f'本地 {rows["candidate-001"]["metric_value"]}/100'], "#3f7358"),
        card(720, 610, 300, "candidate-002：舍弃", ["再加中文摘要", f'本地仍为 {rows["candidate-002"]["metric_value"]}/100'], "#806b61"),
        card(60, 740, 300, "PR #6 已合并", ["保留 candidate-001 改动", "不把本地分数当搜索收益"], "#3f7358"),
        card(390, 870, 300, "合并后：真实 GPT 工具搜索", [f"Q1–Q4 项目页 {project_count}/{len(queries)}",
                                                    f"论文 URL {paper_count}/{len(queries)}"], "#315e79"),
        card(60, 1010, 300, "已见入口：论文页", [f"返回 {paper_count}/{len(queries)}；下一测试 #1", "HTML 已有项目链接；复测搜索"], "#a06436"),
        card(390, 1010, 300, "项目页仍未出现", [f"本次返回 {project_count}/{len(queries)}", "已上线改动的曝光提升未证实"], "#a06436"),
        card(720, 1010, 300, "其他入口：本次未见", ["GitHub 仓库 / 项目页来源", "保持未排序，不等于无效"], "#806b61"),
        card(390, 1140, 300, "下一轮评测：尚未完成", ["需同平台、同查询、同指标前后配对", "跨平台覆盖率目前为 0"], "#806b61"),
    ]
    edges = [
        arrow(540, 184, 540, 210), arrow(540, 314, 540, 340),
        arrow(540, 444, 540, 470),
        arrow(490, 574, 210, 610), arrow(590, 574, 870, 610),
        arrow(210, 714, 210, 740),
        arrow(360, 792, 540, 870),
        arrow(490, 974, 210, 1010), arrow(540, 974, 540, 1010),
        arrow(590, 974, 870, 1010),
        arrow(210, 1114, 490, 1140, dashed=True),
        arrow(540, 1114, 540, 1140, dashed=True),
        arrow(870, 1114, 590, 1140, dashed=True),
    ]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1280" role="img" aria-label="EAU GEO 优化过程图">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#80978b"/></marker></defs>
<style>.title{{font:700 17px system-ui,sans-serif;fill:#fff}}.body{{font:14px system-ui,sans-serif;fill:#f3f6f2}}</style>
<rect width="1080" height="1280" fill="#f6f5f1"/>
<text x="60" y="43" style="font:700 27px system-ui,sans-serif;fill:#264b3a">EAU GEO：从依赖图到真实搜索复测</text>
<text x="60" y="1260" style="font:13px system-ui,sans-serif;fill:#5e6d62">实线：已经发生的流程　虚线：待完成的实验评测　来源：henry-run-results.tsv、gpt-web-search-observations.json</text>
{''.join(edges)}{''.join(nodes)}</svg>'''
    target = GEO / "figures" / "geo-optimization-process.svg"
    target.write_text(svg, encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
