# 2026-10-15 topic-query experiment

Question: “最近有什么 agent-environment co-evolution 的工作？”

The evaluator at `/workspace/eau-geo-eval/v2.py` was written and run on the merged homepage before any candidate edit. It was kept outside all wrapper candidate worktrees. The local score checks 20 pieces of crawlability, paper identity, question answerability, navigation, and keyword quality; it is not a ranking or citation measure.

`autoresearch-wrapper-cl` run `20261015T094550Z-script-js` created a seed and two isolated worktrees. The wrapper currently scans JavaScript files but does not list HTML as a part, so `script.js` was the administrative target. **No script.js optimization was claimed**: candidate edits were HTML/CSS content changes, and the external evaluator read the rendered source files. See `wrapper-results.tsv` for the recorded decisions.

| Candidate | Change | Local proxy | Decision |
| --- | --- | ---: | --- |
| Seed | Merged homepage | 60/100 | Baseline |
| 001 | Related research on the homepage, with links to SEAL, CoMAP, and GenEnv papers | 100/100 | Keep |
| 002 | Separate topic page linked from the homepage and sitemap | 100/100 | Discard; same score with an extra page to maintain |

The first live Codex web search for the question returned the EAU arXiv paper in position 3 and did not return the project URL among inspected results. The user also reported that the project was absent in their Doubao search, but without an exported result set this has not been added as a numerical observation. Search and citation rates require post-deployment repeat measurements.
