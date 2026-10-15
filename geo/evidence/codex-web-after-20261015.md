# Codex web search tool: deployed-site observations, 2026-10-15

Collection: 2026-10-15, approximately 13:16–13:23 UTC. PR #3 was merged at 12:35:43 UTC. Immediately before collection, `https://eau-meta-agent.github.io/`, `/robots.txt`, and `/sitemap.xml` each returned HTTP 200. The live homepage HTML contained the new related-work section and direct SEAL, CoMAP, and GenEnv paper links.

Environment: this Codex conversation's `web.run` `search_query` tool. One query per tool call, with no domain or recency filter. Model version, search index, location, account state, and query rewriting are not exposed by the tool. These are tool output observations, not a fresh ChatGPT Search App session or a measurement of this agent's final answer. The conversation already contained EAU context; even so, the exact query strings below did not contain the EAU name or site. Do not use these results as an unbiased estimate of final answer mentions or citations.

Rank below means *display position in the tool response*, including academic, PDF, and standard web results. It is not a search engine ranking score. Each list records the first ten displayed URL results. The project target is `https://eau-meta-agent.github.io/`; the paper target is `https://arxiv.org/abs/2610.16523`. Mirrors, paper review sites, and other arXiv URLs are not counted as those targets.

## Q1 · 最近有什么 agent-environment co-evolution 的工作？

| Position | URL |
| --- | --- |
| 1 | https://github.com/aaronlyt/awesome-agentic-environment-evolving |
| 2 | https://github.com/zongqing0068/awesome-co-evolution/blob/main/README.md |
| 3 | https://github.com/zongqing0068/awesome-co-evolution |
| 4 | https://github.com/yuema137/scientific-eval-environments/blob/main/zh/works/co-evolution-agentic-systems-survey.md |
| 5 | https://qgithub.com/XMUDeepLIT/Awesome-Self-Evolving-Agents |
| 6 | https://git.mitgai.net/yunfanye/awesome-environment-scaling/blob/main/surveys/2026-08/environment_scaling_survey_2026.md |
| 7 | https://paper.oopus.info/papers/2026-08-16-co-evolution-agentic-systems/ |
| 8 | https://arxiv.science/abs/2606.12191 |
| 9 | https://github.com/adongwanai/AgentGuide/blob/main/docs/06-research-frontiers/01-ai-research-directions-expanded.md |
| 10 | https://onlinelibrary.wiley.com/doi/10.1002/cpe.70974 |

Project: absent from first ten. EAU arXiv paper: absent from first ten.

## Q2 · What are recent papers on agent-environment co-evolution for LLM agents?

| Position | URL |
| --- | --- |
| 1 | https://aclanthology.org/2026.acl-long.1055/ |
| 2 | https://arxiv.org/abs/2605.24426 |
| 3 | https://arxiv.org/abs/2604.15840 |
| 4 | https://arxiv.org/abs/2608.10299 |
| 5 | https://arxiv.org/abs/2610.16523 |
| 6 | https://arxiv.science/abs/2606.12191 |
| 7 | https://aclanthology.org/2026.acl-long.1055.pdf |
| 8 | https://proceedings.mlr.press/v306/zhang26au.html |
| 9 | https://arxiv.deeppaper.ai/papers/2606.12191v1 |
| 10 | https://huggingface.co/papers/2604.15840 |

Project: absent from first ten. EAU arXiv paper: position 5.

## Q3 · Which recent methods co-evolve the training environment and agent policy, and how do they differ?

| Position | URL |
| --- | --- |
| 1 | https://arxiv.org/abs/2610.16523 |
| 2 | https://arxiv.org/abs/2609.04128 |
| 3 | https://github.com/ndqkhanh/agent-research-book/blob/main/docs/69-agent-world-self-evolving-training-arena.md |
| 4 | https://aclanthology.org/2026.acl-long.1055.pdf |
| 5 | https://arxiv.org/abs/2604.03098 |
| 6 | https://huggingface.co/papers/2605.24426 |
| 7 | https://jp.ibbac.eu.org/papers/2610.16523v1 |
| 8 | https://huggingface.co/papers/2604.15840 |
| 9 | https://www.preprints.org/manuscript/202607.1328 |
| 10 | https://github.com/aaronlyt/awesome-agentic-environment-evolving/blob/main/README.md |

Project: absent from first ten. EAU arXiv paper: position 1.

## Q4 · What work jointly adapts the environment, agent, and simulated user during multi-turn RL training?

| Position | URL |
| --- | --- |
| 1 | https://arxiv.org/abs/2610.16523 |
| 2 | https://jp.ibbac.eu.org/papers/2610.16523v1 |
| 3 | https://borowiecki.dev/abs/2610.16523 |
| 4 | https://arxiv-troller.com/paper/3340860/ |
| 5 | https://thelatestinai.com/papers/2610.16523 |
| 6 | https://arxiv.org/abs/2508.18669 |
| 7 | https://arxiv.org/abs/2509.19736 |
| 8 | https://pith.science/paper/2610.16523 |
| 9 | https://docs.aws.amazon.com/sagemaker/latest/dg/model-customize-mtrl.html |
| 10 | https://www.preprints.org/manuscript/202608.1575 |

Project: absent from first ten. EAU arXiv paper: position 1.

## Interpretation

This is one observation per query, collected shortly after deployment. Q1 has a predeployment observation in the same tool environment, but the query was executed at different times and the earlier list was not fully archived. Its paper result changed from position 3 before deployment to absent in this sample; this does not establish that the page change caused a decline. No before samples exist for Q2–Q4, so those rows are after-only. No final answers or citation panels were collected for these four runs, leaving mention, citation, and answer accuracy unknown. The project URL had 0/4 top-ten retrieval in this sample; the paper URL had 3/4.
