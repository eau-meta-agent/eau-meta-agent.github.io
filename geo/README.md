# GEO experiment: EAU

Explore the evidence-linked [GEO experiment tree](figures/geo-exploration-tree.html), its [Chinese guide](EXPLORATION_TREE.zh-CN.md), and [machine-readable JSON](exploration-tree.json). The tree separates observed search entry points from untested interventions.

The target question is: **“最近有什么 agent-environment co-evolution 的工作？”**
The candidate-local proxy is run with `python3 tools/geo_score.py` from the repository root. It uses 20 binary checks worth 5 points each:

| Dimension | Points | What it checks |
| --- | ---: | --- |
| Crawl readiness | 20 | Robots rule, sitemap, canonical URL, index directive |
| Paper identity | 20 | Full paper title, arXiv link, scholarly metadata, static benchmark table |
| Answerability | 40 | Topic heading, source links and substantive dated descriptions of SEAL, CoMAP, and GenEnv, plus EAU's position |
| Navigation | 10 | Visible homepage link to the related-work content and a discoverable URL/section |
| Quality guardrails | 10 | Keyword density and no hidden repeated-keyword block |

This is a **local proxy**, not a search-engine score. A high value only says the page contains accessible, sourced material relevant to the target question. The experiment freezes the evaluator outside candidate worktrees at `/workspace/eau-geo-eval/v2.py`; this repository copy makes the criteria reviewable.

## Real exposure

Record repeated searches in `observations.csv` (one row per provider, phase, exact question, and date). Use `python3 tools/visibility_report.py geo/observations.csv` to calculate separate `retrieval@10`, EAU mention, final answer citation, and answer accuracy rates by provider and before/after phase. `project_rank=0` means the project URL was absent from the inspected top 10 results; an empty cell means unknown. The same applies to the paper URL. For mention/citation/accuracy, `1` means yes, `0` means no, and blank means unknown. Search result retrieval and final answer citation are separate observations. Keep the result URL or screenshot reference in `evidence_url` when available.

The full cross-agent protocol and current results are in [TEST_PLAN.zh-CN.md](TEST_PLAN.zh-CN.md).

The Henry autoresearch-wrapper dependency graph, node-edit loop, global priority analysis, and new observation template are documented in [HENRY_GEO_CASE_STUDY.zh-CN.md](HENRY_GEO_CASE_STUDY.zh-CN.md).

The [standalone dependency graph](figures/eau-dependency-graph-20261016.png) visualizes the key paths from external entry points and site files to project discovery, platform retrieval, and answer citation. The [post-merge Codex search observation](evidence/codex-web-postmerge-20261016.md) records the first immediate Q1–Q4 check after PR #6 merged; it does not establish search lift.

For all 39 nodes and 47 edges, open the [interactive full graph](figures/full-dependency-graph.html) or read the [Chinese viewing guide](GRAPH_VIEWER.zh-CN.md). The baseline and candidate graphs have the same topology; only the README content fingerprint changes.

Current next-test ordering uses only [actual GPT/Codex web-search source URLs](gpt-web-search-observations.json), with [raw responses](evidence/gpt-web-q1-20261016.txt) saved for audit. [Observed priorities](priorities.json) exclude modeled graph reachability, manually marked gaps, and estimated costs. The old structural score is preserved as [history](legacy-structural-priorities.json), not used for decisions.

Do not compare a deployed baseline with an unpublished candidate as if both had a live search result. Re-run the same query set after deployment and allow for indexing delay. The current sample size is too small to infer a stable exposure rate.
