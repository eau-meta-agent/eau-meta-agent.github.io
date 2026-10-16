# EAU GEO 实验探索树

打开 [交互树](figures/geo-exploration-tree.html)，点击分支逐层展开。机器可读版本为 [exploration-tree.json](exploration-tree.json)。它由 Henry wrapper 的 `geo-explore` 命令生成。

```text
目标项目页
└── GPT/Codex 网页搜索（真实返回的来源 URL）
    ├── Q1–Q4 查询
    │   └── arXiv 论文页（各查询均返回）
    │       └── 论文 → 项目页链接假设（下一测试 #1）
    │           └── external:paper-backlink（需论文作者操作）
    ├── 未观测到入口的候选（不能按本次搜索结果排效果次序）
    │   ├── GitHub README / About
    │   ├── 项目页元数据 / 相关工作
    │   └── robots / sitemap
    └── 其余依赖图节点（尚未连接到干预方案）
```

这棵树有两类分支：**搜索证据分支**和**待测改动分支**。Q1–Q4 每次都返回论文 URL，没有返回项目页 URL；因此论文页是当前可见的测试入口。论文页到项目页的链接状态尚未核实，不能从这棵树断言该链接有效，也不能断言添加链接会改变搜索结果。

每个干预分支显示改动类型（节点内部或节点之间的关系）、负责人、仓库内是否可操作、允许的操作，以及真实前后评测。当前所有干预的真实前后评测均为**未测**。README 的本地 90→100 分数不进入这棵树的曝光结论。未观测到的入口保持未排序；这不表示它们无效。

完整依赖图仍可在 [完整依赖图查看器](figures/full-dependency-graph.html) 中查看。探索树把其中的 39 个节点与具体查询、可见来源和实验假设相连；未映射的节点单列，避免把图上的假想检索结果当成真实返回。

重建命令：

```bash
python3 /path/to/autoresearch-wrapper/scripts/autoresearch_wrapper.py geo-explore \
  --repo . --config geo/config.json \
  --search-evidence geo/gpt-web-search-observations.json \
  --observations geo/pending_agent_observations.csv \
  --html-out geo/figures/geo-exploration-tree.html > geo/exploration-tree.json
```

后续只在取得同平台、同查询、同指标的候选前后观测后填写 CSV，并重新生成树。候选分支会显示 `geo-compare` 的覆盖率、全局增量区间和回退检查；没有数据时仍显示“未测”。
