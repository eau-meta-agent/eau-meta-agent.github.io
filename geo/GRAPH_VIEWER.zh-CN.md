# 如何查看 EAU 完整依赖图

打开 [交互式完整图](figures/full-dependency-graph.html)。它是一个**自包含 HTML 文件**，不用安装包，也不用联网；可直接双击打开。画布支持滚轮缩放、拖动平移、搜索节点、点击查看节点属性和所有相邻边，并可切换 `baseline` 与 `candidate`。右上角可导出当前视图为 SVG。

如果本地浏览器限制直接打开文件，也可以在仓库根目录运行：

```bash
python3 -m http.server 8000
```

然后打开 `http://localhost:8000/geo/figures/full-dependency-graph.html`。

也提供两张可直接在浏览器查看、放大或打印的全量矢量图：[改动前 SVG](figures/full-baseline-graph.svg) · [候选 SVG](figures/full-candidate-graph.svg)。它们都包含 **39 个节点和 47 条有向边**。之前的[简化图片](figures/eau-dependency-graph-20261016.png)只展示关键路径，不是全量图。

## 两份 JSON 是什么

| 文件 | 对应状态 | 用途 |
| --- | --- | --- |
| [baseline-graph.json](baseline-graph.json) | README 改动前，实验 seed `6fdd5e7` | 固定起点；保存节点、边和可编辑位置 |
| [candidate-graph.json](candidate-graph.json) | README 链接改动后的候选，已随 PR #6 合并 | 比较候选与起点 |
| [graph-diff.json](graph-diff.json) | 两者的机器计算差异 | 明确列出增删节点、改动节点、增删边 |

这次实验的**拓扑没有变化**：两图都是 39 个节点、47 条边。只改了 `file:README.md` 节点的文本，因此它的 `content_sha256` 不同，`graph-diff.json` 只列出这一处内容变化。旧版 JSON 只记录拓扑，导致两份文件完全相同；现已补上内容指纹并重生成。内容指纹只用于识别变化，不是搜索排名指标。

## 字段怎么读

- `nodes`: `id` 是节点标识；`kind` 区分仓库文件、HTML 分节、元数据、资源、外部入口和观测结果；`path` 指向本地文件；`operations` 是允许的编辑方式；本地节点的 `content_sha256` 是内容指纹。
- `edges`: `from` → `to` 是**原始有向边**，`kind` 表示 `contains`、`references`、`links-to`、`depends-on` 或 `may-retrieve`。例如 `答案 → 检索` 的 `depends-on` 边表示答案依赖检索，并非搜索结果已被观测。
- `outcome:*` 节点只是待观测位置。图显示可能的依赖路径，**不证明**项目页已被平台召回或引用；真实结果看[测试计划](TEST_PLAN.zh-CN.md)与[合并后记录](evidence/codex-web-postmerge-20261016.md)。

当前实验决策已改用[实际 GPT 网页搜索返回的 URL](gpt-web-search-observations.json)和[观测优先级](priorities.json)。图中的 `outcome:*` 占位节点与 11 个“可达结果”**不参与当前排序**；其他平台暂不计入。

图和差异可用 `python3 tools/render_geo_graph.py` 从两份 JSON 重新生成。
