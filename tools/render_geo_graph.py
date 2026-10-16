#!/usr/bin/env python3
"""Render the complete EAU GEO graph as a standalone, dependency-free HTML file."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "geo/baseline-graph.json"
CANDIDATE = ROOT / "geo/candidate-graph.json"
OUTPUT = ROOT / "geo/figures/full-dependency-graph.html"
DIFF = ROOT / "geo/graph-diff.json"
SVG_NS = "http://www.w3.org/2000/svg"


def write_svg(graph: dict, changed: set[str], output: Path) -> None:
    """A static, vector, full-node export for viewing and printing without JavaScript."""
    ET.register_namespace("", SVG_NS)
    tag = lambda name: f"{{{SVG_NS}}}{name}"
    root = ET.Element(tag("svg"), {"viewBox": "0 0 2370 1650", "width": "2370", "height": "1650",
                                    "role": "img", "aria-label": "EAU complete dependency graph"})
    ET.SubElement(root, tag("rect"), {"width": "2370", "height": "1650", "fill": "#f7f9fb"})
    defs = ET.SubElement(root, tag("defs"))
    marker = ET.SubElement(defs, tag("marker"), {"id": "arrow", "viewBox": "0 0 10 10", "refX": "8",
                                                 "refY": "5", "markerWidth": "5", "markerHeight": "5",
                                                 "orient": "auto-start-reverse"})
    ET.SubElement(marker, tag("path"), {"d": "M0 0 L10 5 L0 10 Z", "fill": "#91a1b0"})
    def txt(x: int, y: int, value: str, size: int = 15, weight: int = 500, fill: str = "#243445") -> None:
        element = ET.SubElement(root, tag("text"), {"x": str(x), "y": str(y), "font-size": str(size),
                                                   "font-weight": str(weight), "fill": fill,
                                                   "font-family": "Inter, Noto Sans SC, Microsoft YaHei, sans-serif"})
        element.text = value

    txt(45, 42, "EAU GEO 完整依赖图", 27, 750)
    txt(45, 67, f"{len(graph['nodes'])} 个节点 · {len(graph['edges'])} 条有向边 · 箭头方向与 JSON 一致", 14, 500, "#617184")
    groups = [("外部来源 / 入口", 40, 280), ("仓库与站点文件", 350, 280),
              ("首页分节与元数据", 660, 280), ("引用的静态资源", 975, 280),
              ("发现环节", 1290, 280), ("各平台检索", 1605, 290), ("答案阶段", 1925, 290)]
    for name, x, width in groups:
        ET.SubElement(root, tag("rect"), {"x": str(x), "y": "87", "width": str(width),
                                          "height": "1500", "rx": "14", "fill": "#ffffff", "stroke": "#e3e9ef"})
        txt(x + 13, 119, name, 16, 700, "#5b6d7f")
    nodes = {node["id"]: node for node in graph["nodes"]}
    ext = sorted(n["id"] for n in graph["nodes"] if n["kind"] in {"external-source", "external-owned"})
    files = sorted(n["id"] for n in graph["nodes"] if n["kind"] == "file")
    internal = sorted(n["id"] for n in graph["nodes"] if n["kind"] in {"html-section", "html-metadata"})
    assets = sorted(n["id"] for n in graph["nodes"] if n["kind"] == "asset")
    retrieval = sorted(n["id"] for n in graph["nodes"] if n["id"].endswith(":retrieval"))
    answer = sorted(n["id"] for n in graph["nodes"] if n["id"].endswith(":answer"))
    positions: dict[str, tuple[int, int]] = {}
    for ids, x, start, step in [(ext, 55, 200, 184), (files, 365, 200, 184),
                                (internal, 675, 148, 135), (assets, 990, 360, 226),
                                (retrieval, 1620, 278, 247), (answer, 1940, 278, 247)]:
        positions.update({node_id: (x, start + i * step) for i, node_id in enumerate(ids)})
    positions["outcome:site-discovery"] = (1305, 789)
    width, height = 232, 57
    for edge in graph["edges"]:
        a = positions[edge["from"]]
        b = positions[edge["to"]]
        ax, ay = a[0] + width / 2, a[1] + height / 2
        bx, by = b[0] + width / 2, b[1] + height / 2
        if abs(bx - ax) > abs(by - ay) * .62:
            x1, y1 = (a[0] + width if bx > ax else a[0]), ay
            x2, y2 = (b[0] if bx > ax else b[0] + width), by
        else:
            x1, y1 = ax, (a[1] + height if by > ay else a[1])
            x2, y2 = bx, (b[1] if by > ay else b[1] + height)
        dx, dy = x2 - x1, y2 - y1
        attrs = {"d": f"M{x1:.1f},{y1:.1f} C{x1 + dx*.45:.1f},{y1 + dy*.1:.1f} "
                      f"{x2 - dx*.45:.1f},{y2 - dy*.1:.1f} {x2:.1f},{y2:.1f}",
                 "fill": "none", "stroke": "#9daab6", "stroke-width": "1.8", "opacity": ".47",
                 "marker-end": "url(#arrow)"}
        if edge["kind"] == "may-retrieve" or edge["to"] == "external:paper-backlink":
            attrs["stroke-dasharray"] = "7 5"
        path = ET.SubElement(root, tag("path"), attrs)
        ET.SubElement(path, tag("title")).text = f"{edge['from']} → {edge['to']} ({edge['kind']})"
    special = {"file:index.html": "index.html 项目首页", "file:README.md": "README.md 仓库说明",
               "external:paper": "EAU 论文 arXiv:2610.16523", "external:repository-metadata": "GitHub About 元数据",
               "external:paper-backlink": "论文 → 项目页（未核实）", "outcome:site-discovery": "项目页发现 / 抓取"}
    colors = {"file": "#e8f1f9", "html-section": "#e8f6ef", "html-metadata": "#fff3d5",
              "asset": "#eef0f2", "external-source": "#f0edf8", "external-owned": "#f0edf8",
              "unobserved-outcome": "#fae6df", "observed-outcome": "#f9ece8"}
    for node_id, (x, y) in positions.items():
        node = nodes[node_id]
        if node_id in special:
            label = special[node_id]
        elif node["kind"] == "external-source":
            label = "项目首页 URL" if node["url"] == graph["site_url"] else node["url"].replace("https://arxiv.org/abs/", "arXiv:")
        elif node["kind"] == "observed-outcome":
            label = node["platform"] + (" · 答案" if node_id.endswith(":answer") else " · 检索")
        else:
            label = node.get("path") or node_id
        box = ET.SubElement(root, tag("rect"), {"x": str(x), "y": str(y), "width": str(width),
                                                "height": str(height), "rx": "8", "fill": colors[node["kind"]],
                                                "stroke": "#c78218" if node_id in changed else "#c7d1db",
                                                "stroke-width": "3" if node_id in changed else "1.3"})
        ET.SubElement(box, tag("title")).text = node_id
        if len(label) <= 25:
            txt(x + 10, y + 35, label, 14, 700 if node_id in changed else 500)
        else:
            txt(x + 10, y + 25, label[:24], 13, 700 if node_id in changed else 500)
            txt(x + 10, y + 45, label[24:48], 12)
    txt(45, 1620, "橙色边框：候选中内容变化的节点；虚线：未核实或可能路径。完整节点属性、相邻边和前后切换见 HTML 版。", 13, 500, "#68788a")
    output.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))


def main() -> None:
    before = json.loads(BASELINE.read_text(encoding="utf-8"))
    after = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    for graph in (before, after):
        ids = {node["id"] for node in graph["nodes"]}
        if len(ids) != len(graph["nodes"]):
            raise ValueError("duplicate node IDs")
        if any(edge["from"] not in ids or edge["to"] not in ids for edge in graph["edges"]):
            raise ValueError("edge references a missing node")
    html = TEMPLATE.replace("__BASELINE_JSON__", json.dumps(before, ensure_ascii=False).replace("<", "\\u003c"))
    html = html.replace("__CANDIDATE_JSON__", json.dumps(after, ensure_ascii=False).replace("<", "\\u003c"))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    before_nodes = {node["id"]: node for node in before["nodes"]}
    after_nodes = {node["id"]: node for node in after["nodes"]}
    before_edges = {(edge["from"], edge["to"], edge["kind"]) for edge in before["edges"]}
    after_edges = {(edge["from"], edge["to"], edge["kind"]) for edge in after["edges"]}
    diff = {
        "added_nodes": sorted(after_nodes.keys() - before_nodes.keys()),
        "removed_nodes": sorted(before_nodes.keys() - after_nodes.keys()),
        "changed_nodes": [{"id": node_id,
                           "before_content_sha256": before_nodes[node_id].get("content_sha256"),
                           "after_content_sha256": after_nodes[node_id].get("content_sha256")}
                          for node_id in sorted(before_nodes.keys() & after_nodes.keys())
                          if before_nodes[node_id] != after_nodes[node_id]],
        "added_edges": [dict(zip(("from", "to", "kind"), edge)) for edge in sorted(after_edges - before_edges)],
        "removed_edges": [dict(zip(("from", "to", "kind"), edge)) for edge in sorted(before_edges - after_edges)],
    }
    DIFF.write_text(json.dumps(diff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    changed_ids = {node["id"] for node in diff["changed_nodes"]}
    write_svg(before, changed_ids, OUTPUT.parent / "full-baseline-graph.svg")
    write_svg(after, changed_ids, OUTPUT.parent / "full-candidate-graph.svg")
    print(f"{OUTPUT}: {len(before['nodes'])} nodes, {len(before['edges'])} edges")


TEMPLATE = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EAU GEO 完整依赖图 — 基线与候选</title>
<style>
:root{font-family:Inter,"Noto Sans SC","Microsoft YaHei",system-ui,sans-serif;color:#202b38;background:#f7f8fa}
*{box-sizing:border-box}body{margin:0}.top{padding:20px 24px 16px;background:#fff;border-bottom:1px solid #dfe4ea;display:flex;gap:20px;align-items:end;justify-content:space-between;flex-wrap:wrap}
h1{font-size:24px;margin:0 0 5px;font-weight:750;letter-spacing:-.02em}.sub{font-size:13px;color:#627285}.toolbar{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
button,input{font:inherit}button{border:1px solid #cbd5df;background:#fff;color:#233143;border-radius:7px;padding:8px 11px;cursor:pointer}button:hover{background:#f1f5f9}button.active{background:#183954;color:#fff;border-color:#183954}
input{border:1px solid #cbd5df;border-radius:7px;padding:8px 10px;width:200px}.layout{display:grid;grid-template-columns:minmax(0,1fr) 335px;height:calc(100vh - 105px);min-height:650px}
.canvas{position:relative;overflow:hidden;background:#fbfcfd}.canvas svg{display:block;width:100%;height:100%;touch-action:none;cursor:grab}.canvas svg.dragging{cursor:grabbing}.sidebar{overflow:auto;background:#fff;border-left:1px solid #dfe4ea;padding:19px}
.sidebar h2{font-size:17px;margin:0 0 8px}.sidebar p,.sidebar li{font-size:13px;line-height:1.5;color:#4a5b6d}.stat{display:flex;gap:7px;flex-wrap:wrap;margin:14px 0}.pill{font-size:12px;border-radius:20px;padding:4px 9px;background:#edf3f7;color:#32536b}.pill.changed{background:#fff1d6;color:#7b4b00}
.legend{display:grid;gap:6px;margin:16px 0;font-size:12px;color:#4a5b6d}.sample{display:inline-block;width:18px;height:9px;border-radius:2px;margin-right:6px;vertical-align:middle}.node-list{display:grid;gap:4px;margin-top:12px}.node-row{display:block;text-align:left;width:100%;font-size:12px;padding:7px 8px;white-space:normal}.node-row.hidden{display:none}
.detail{background:#f6f8fa;border:1px solid #e1e7ec;border-radius:8px;padding:10px;overflow-wrap:anywhere}.detail code{font-size:11px}.muted{color:#7a8795}.note{position:absolute;left:18px;bottom:14px;background:rgba(255,255,255,.92);border:1px solid #e0e5ea;border-radius:6px;padding:8px 10px;font-size:11px;color:#59697a;max-width:540px;pointer-events:none}
@media(max-width:850px){.layout{display:block;height:auto}.canvas{height:65vh;min-height:450px}.sidebar{height:auto;border-left:0;border-top:1px solid #dfe4ea}}
</style>
</head>
<body>
<header class="top"><div><h1>EAU GEO 完整依赖图</h1><div class="sub">全量节点与边 · 基线和 README 候选 · 箭头方向与 JSON 一致</div></div>
<div class="toolbar"><button id="before" class="active">改动前 baseline</button><button id="after">改动后 candidate</button><input id="search" type="search" placeholder="搜索节点 / URL"><button id="fit">适配画布</button><button id="zoomIn">＋</button><button id="zoomOut">－</button><button id="download">下载 SVG</button></div></header>
<main class="layout"><section class="canvas"><svg id="graph" role="img" aria-label="EAU 完整依赖图，39 个节点和 47 条有向边" xmlns="http://www.w3.org/2000/svg"></svg><div class="note">滚轮缩放 · 拖动画布平移 · 点击节点看详情。灰色箭头：原始依赖方向；虚线：未验证或可能路径。</div></section>
<aside class="sidebar"><h2 id="phaseTitle">改动前 baseline</h2><div class="stat"><span class="pill" id="counts"></span><span class="pill changed" id="delta"></span></div><p>节点分组按内容来源排列。<strong>箭头方向保持原始 JSON</strong>：例如“答案 → 检索”表示答案依赖检索；网站文件指向内部内容表示包含或引用。</p><div class="legend"><span><i class="sample" style="background:#e8f1f9"></i>仓库文件</span><span><i class="sample" style="background:#e8f6ef"></i>HTML 分节</span><span><i class="sample" style="background:#fff3d5"></i>HTML 元数据</span><span><i class="sample" style="background:#f0edf8"></i>外部入口/论文</span><span><i class="sample" style="background:#f9ece8"></i>检索与答案结果（需实测）</span></div><h2>选中节点</h2><div id="detail" class="detail"><span class="muted">点击图中节点或下方列表。</span></div><h2 style="margin-top:22px">全部节点</h2><div id="list" class="node-list"></div></aside></main>
<script id="baseline-data" type="application/json">__BASELINE_JSON__</script>
<script id="candidate-data" type="application/json">__CANDIDATE_JSON__</script>
<script>
const G={before:JSON.parse(document.getElementById('baseline-data').textContent),after:JSON.parse(document.getElementById('candidate-data').textContent)};
const NS='http://www.w3.org/2000/svg',svg=document.getElementById('graph'),W=2450,H=1660,NW=232,NH=57;
let phase='before',selected=null,query='',vb={x:0,y:0,w:W,h:H},drag=null;
const beforeNodes=new Map(G.before.nodes.map(n=>[n.id,n])), afterNodes=new Map(G.after.nodes.map(n=>[n.id,n]));
const changed=new Set([...beforeNodes.keys()].filter(id=>JSON.stringify(beforeNodes.get(id))!==JSON.stringify(afterNodes.get(id))));
const labels={
 'file:index.html':'index.html 项目首页','file:README.md':'README.md 仓库说明','file:robots.txt':'robots.txt','file:sitemap.xml':'sitemap.xml','file:styles.css':'styles.css','file:script.js':'script.js','file:site-config.js':'site-config.js',
 'external:paper':'EAU 论文 arXiv:2610.16523','external:repository-metadata':'GitHub About 元数据','external:paper-backlink':'论文 → 项目页（未核实）','outcome:site-discovery':'项目页发现 / 抓取'
};
const ext=G.before.nodes.filter(n=>n.kind==='external-source'||n.kind==='external-owned').map(n=>n.id).sort();
const files=G.before.nodes.filter(n=>n.kind==='file').map(n=>n.id).sort();
const internal=G.before.nodes.filter(n=>n.kind==='html-section'||n.kind==='html-metadata').map(n=>n.id).sort();
const assets=G.before.nodes.filter(n=>n.kind==='asset').map(n=>n.id).sort();
const retrieval=G.before.nodes.filter(n=>n.id.endsWith(':retrieval')).map(n=>n.id).sort();
const answer=G.before.nodes.filter(n=>n.id.endsWith(':answer')).map(n=>n.id).sort();
const pos=new Map();
ext.forEach((id,i)=>pos.set(id,{x:55,y:190+i*184}));
files.forEach((id,i)=>pos.set(id,{x:365,y:190+i*184}));
internal.forEach((id,i)=>pos.set(id,{x:675,y:138+i*135}));
assets.forEach((id,i)=>pos.set(id,{x:990,y:350+i*226}));
pos.set('outcome:site-discovery',{x:1305,y:779});
retrieval.forEach((id,i)=>pos.set(id,{x:1620,y:268+i*247}));
answer.forEach((id,i)=>pos.set(id,{x:1940,y:268+i*247}));
function label(n){if(labels[n.id])return labels[n.id];if(n.kind==='external-source')return n.url===G.before.site_url?'项目首页 URL':n.url.replace('https://arxiv.org/abs/','arXiv:');if(n.kind==='html-section')return 'section: '+n.id.split(':')[1];if(n.kind==='html-metadata')return 'meta: '+n.id.split(':')[1];if(n.kind==='asset')return n.path.replace('assets/','assets/');if(n.kind==='observed-outcome')return n.platform+(n.id.endsWith(':answer')?' · 答案':' · 检索');return n.id}
function kindColor(n){return {'file':'#e8f1f9','html-section':'#e8f6ef','html-metadata':'#fff3d5','asset':'#eef0f2','external-source':'#f0edf8','external-owned':'#f0edf8','unobserved-outcome':'#fae6df','observed-outcome':'#f9ece8'}[n.kind]||'#eee'}
function S(tag,attrs={}){const e=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);return e}
function addText(parent,x,y,value,size=15,weight=500,fill='#243445'){const t=S('text',{x,y,'font-size':size,'font-weight':weight,fill,'font-family':'Inter, Noto Sans SC, Microsoft YaHei, sans-serif'});t.textContent=value;parent.appendChild(t);return t}
function wrap(value,max=23){if(value.length<=max)return [value];const p=value.lastIndexOf(' ',max);return p>8?[value.slice(0,p),value.slice(p+1)]:[value.slice(0,max-1)+'…',value.slice(max-1,max+17)]}
function endpoints(a,b){const ax=a.x+NW/2,ay=a.y+NH/2,bx=b.x+NW/2,by=b.y+NH/2;if(Math.abs(bx-ax)>Math.abs(by-ay)*.62){return {x1:bx>ax?a.x+NW:a.x,y1:ay,x2:bx>ax?b.x:b.x+NW,y2:by}}return {x1:ax,y1:by>ay?a.y+NH:a.y,x2:bx,y2:by>ay?b.y:b.y+NH}}
function edgePath(a,b){let e=endpoints(a,b),dx=e.x2-e.x1,dy=e.y2-e.y1;return `M${e.x1},${e.y1} C${e.x1+dx*.45},${e.y1+dy*.1} ${e.x2-dx*.45},${e.y2-dy*.1} ${e.x2},${e.y2}`}
function updateView(){svg.setAttribute('viewBox',`${vb.x} ${vb.y} ${vb.w} ${vb.h}`)}
function draw(){const graph=G[phase],nodes=new Map(graph.nodes.map(n=>[n.id,n]));svg.replaceChildren();
 const defs=S('defs'),marker=S('marker',{id:'arrow','viewBox':'0 0 10 10',refX:'8',refY:'5',markerWidth:'5',markerHeight:'5',orient:'auto-start-reverse'});marker.appendChild(S('path',{d:'M0 0L10 5L0 10Z',fill:'#98a6b4'}));defs.appendChild(marker);svg.appendChild(defs);
 const groups=[['外部来源 / 入口',40,280],['仓库与站点文件',350,280],['首页分节与元数据',660,280],['引用的静态资源',975,280],['发现环节',1290,280],['各平台检索',1605,290],['答案阶段',1925,290]];
 groups.forEach(([name,x,w])=>{svg.appendChild(S('rect',{x,y:66,width:w,height:1515,rx:15,fill:'#ffffff',stroke:'#e8edf1'}));addText(svg,x+13,101,name,16,700,'#5f7081')});
 const edges=S('g',{id:'edges'});graph.edges.forEach((e,i)=>{const a=pos.get(e.from),b=pos.get(e.to);if(!a||!b)return;const path=S('path',{d:edgePath(a,b),fill:'none',stroke:'#a4b0bb','stroke-width':e.kind==='contains'?1.7:2,opacity:.5,'marker-end':'url(#arrow)','data-from':e.from,'data-to':e.to,'data-kind':e.kind});if(e.kind==='may-retrieve'||e.from==='outcome:site-discovery'&&e.to==='external:paper-backlink')path.setAttribute('stroke-dasharray','7 5');const title=S('title');title.textContent=`${e.from} → ${e.to} (${e.kind})`;path.appendChild(title);edges.appendChild(path)});svg.appendChild(edges);
 const nodeLayer=S('g',{id:'nodes'});graph.nodes.forEach(n=>{const p=pos.get(n.id);if(!p)return;const g=S('g',{'class':'graph-node','data-id':n.id,tabindex:'0',role:'button','aria-label':label(n)});let rect=S('rect',{x:p.x,y:p.y,width:NW,height:NH,rx:8,fill:kindColor(n),stroke:changed.has(n.id)?'#d48b22':'#cbd5df','stroke-width':changed.has(n.id)?3:1.4});g.appendChild(rect);const lines=wrap(label(n));if(lines.length===1)addText(g,p.x+11,p.y+35,lines[0],15,changed.has(n.id)?700:550);else {addText(g,p.x+11,p.y+25,lines[0],14,changed.has(n.id)?700:550);addText(g,p.x+11,p.y+44,lines[1],13,500)}if(changed.has(n.id))addText(g,p.x+NW-19,p.y+17,'●',12,700,'#c78218');g.addEventListener('click',()=>select(n.id));g.addEventListener('keydown',ev=>{if(ev.key==='Enter')select(n.id)});g.addEventListener('mouseenter',()=>highlight(n.id));g.addEventListener('mouseleave',()=>highlight(selected));nodeLayer.appendChild(g)});svg.appendChild(nodeLayer);updateView();
 document.getElementById('phaseTitle').textContent=phase==='before'?'改动前 baseline':'改动后 candidate';document.getElementById('counts').textContent=`${graph.nodes.length} 节点 · ${graph.edges.length} 条边`;document.getElementById('delta').textContent=`${changed.size} 个内容变化节点 · 0 条边变化`;
 document.getElementById('before').classList.toggle('active',phase==='before');document.getElementById('after').classList.toggle('active',phase==='after');renderList();highlight(selected);if(selected)showDetail(selected)}
function highlight(id){const needle=(query||'').toLowerCase();const graph=G[phase];for(const el of svg.querySelectorAll('.graph-node')){const nid=el.dataset.id,matches=!needle||nid.toLowerCase().includes(needle)||label(graph.nodes.find(n=>n.id===nid)).toLowerCase().includes(needle);const related=!id||nid===id||graph.edges.some(e=>e.from===id&&e.to===nid||e.to===id&&e.from===nid);el.setAttribute('opacity',matches&&related?'1':'.18')}for(const el of svg.querySelectorAll('#edges path')){const related=!id||el.dataset.from===id||el.dataset.to===id;const matches=!needle||el.dataset.from.toLowerCase().includes(needle)||el.dataset.to.toLowerCase().includes(needle);el.setAttribute('opacity',related&&matches?(id?'.9':'.42'):'.07');el.setAttribute('stroke-width',related&&id?'3':'1.7')}}
function showDetail(id){const n=G[phase].nodes.find(x=>x.id===id),d=document.getElementById('detail');if(!n){d.textContent='请选择节点';return}const neighbors=G[phase].edges.filter(e=>e.from===id||e.to===id);d.replaceChildren();const title=document.createElement('strong');title.textContent=label(n);d.appendChild(title);const p=document.createElement('p');p.textContent=`${n.id} · ${n.kind} · ${neighbors.length} 条相邻边`;d.appendChild(p);const pre=document.createElement('pre');pre.style.cssText='white-space:pre-wrap;font-size:11px;line-height:1.4';pre.textContent=JSON.stringify(n,null,2);d.appendChild(pre);const h=document.createElement('strong');h.textContent='相邻边（方向按 JSON）';d.appendChild(h);for(const e of neighbors){const line=document.createElement('p');line.style.margin='6px 0';line.textContent=`${e.from} → ${e.to} · ${e.kind}`;d.appendChild(line)}if(changed.has(id)){const b=beforeNodes.get(id),a=afterNodes.get(id),x=document.createElement('p');x.style.fontWeight='700';x.textContent=`内容变化：${b.content_sha256?.slice(0,12)} → ${a.content_sha256?.slice(0,12)}；拓扑未变。`;d.appendChild(x)}}
function select(id){selected=id;showDetail(id);highlight(id);const p=pos.get(id);if(p){vb.x=Math.max(0,p.x-vb.w*.45);vb.y=Math.max(0,p.y-vb.h*.45);updateView()}}
function renderList(){const list=document.getElementById('list');list.replaceChildren();for(const n of G[phase].nodes){const b=document.createElement('button');b.className='node-row';b.textContent=(changed.has(n.id)?'● ':'')+label(n);b.title=n.id;b.addEventListener('click',()=>select(n.id));list.appendChild(b)}filterList()}
function filterList(){const q=query.toLowerCase();for(const b of document.querySelectorAll('.node-row'))b.classList.toggle('hidden',q&&!b.textContent.toLowerCase().includes(q)&&!b.title.toLowerCase().includes(q))}
function zoom(f){const cx=vb.x+vb.w/2,cy=vb.y+vb.h/2;vb.w=Math.max(350,Math.min(W*1.3,vb.w*f));vb.h=Math.max(260,Math.min(H*1.3,vb.h*f));vb.x=cx-vb.w/2;vb.y=cy-vb.h/2;updateView()}
document.getElementById('before').onclick=()=>{phase='before';draw()};document.getElementById('after').onclick=()=>{phase='after';draw()};document.getElementById('fit').onclick=()=>{vb={x:0,y:0,w:W,h:H};selected=null;draw()};document.getElementById('zoomIn').onclick=()=>zoom(.78);document.getElementById('zoomOut').onclick=()=>zoom(1.28);document.getElementById('search').oninput=e=>{query=e.target.value;filterList();highlight(selected)};
svg.addEventListener('wheel',e=>{e.preventDefault();zoom(e.deltaY>0?1.14:.88)},{passive:false});svg.addEventListener('pointerdown',e=>{if(e.target.closest('.graph-node'))return;drag={x:e.clientX,y:e.clientY,ox:vb.x,oy:vb.y};svg.classList.add('dragging');svg.setPointerCapture(e.pointerId)});svg.addEventListener('pointermove',e=>{if(!drag)return;const r=svg.getBoundingClientRect();vb.x=drag.ox-(e.clientX-drag.x)*vb.w/r.width;vb.y=drag.oy-(e.clientY-drag.y)*vb.h/r.height;updateView()});svg.addEventListener('pointerup',()=>{drag=null;svg.classList.remove('dragging')});
document.getElementById('download').onclick=()=>{const clone=svg.cloneNode(true),style=S('style');style.textContent='text{font-family:Inter,Noto Sans SC,Microsoft YaHei,sans-serif}';clone.insertBefore(style,clone.firstChild);clone.setAttribute('width',W);clone.setAttribute('height',H);const blob=new Blob([new XMLSerializer().serializeToString(clone)],{type:'image/svg+xml'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`eau-full-dependency-${phase}.svg`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};
draw();
</script>
</body>
</html>'''


if __name__ == "__main__":
    main()
