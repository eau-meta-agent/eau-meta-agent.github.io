# GEO experiment: EAU

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

Do not compare a deployed baseline with an unpublished candidate as if both had a live search result. Re-run the same query set after deployment and allow for indexing delay. The current sample size is too small to infer a stable exposure rate.
