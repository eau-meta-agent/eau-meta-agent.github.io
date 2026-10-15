#!/usr/bin/env python3
"""Frozen, candidate-local proxy for the EAU discovery experiment.

The score measures crawl/readability and how well the site answers one
pre-registered topic query. It does not measure search rank or AI citations.
"""

import json
import re
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path.cwd()
SITE = "https://eau-meta-agent.github.io/"
PAPERS = {
    "SEAL": "https://arxiv.org/abs/2605.24426",
    "CoMAP": "https://arxiv.org/abs/2606.02372",
    "GenEnv": "https://arxiv.org/abs/2512.19682",
}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.links = []
        self.headings = []
        self.meta = []
        self.hidden_depth = 0
        self.tags = []
        self.current_link = None
        self.current_heading = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        hidden = self.hidden_depth > 0 or tag in {"script", "style", "template"} or "hidden" in attrs
        self.tags.append((tag, hidden))
        if hidden:
            self.hidden_depth += 1
        if tag == "a" and not hidden:
            self.current_link = [attrs.get("href", ""), []]
        if tag in {"h1", "h2", "h3"} and not hidden:
            self.current_heading = [tag, []]
        if tag in {"meta", "link"}:
            self.meta.append((tag, attrs))

    def handle_endtag(self, tag):
        if tag == "a" and self.current_link:
            self.links.append((self.current_link[0], " ".join(self.current_link[1])))
            self.current_link = None
        if tag in {"h1", "h2", "h3"} and self.current_heading:
            self.headings.append((self.current_heading[0], " ".join(self.current_heading[1])))
            self.current_heading = None
        if self.tags:
            _, hidden = self.tags.pop()
            if hidden:
                self.hidden_depth -= 1

    def handle_data(self, data):
        if not self.hidden_depth and data.strip():
            self.text.append(data.strip())
            if self.current_link:
                self.current_link[1].append(data.strip())
            if self.current_heading:
                self.current_heading[1].append(data.strip())


def parse(path):
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    return page


home_path = ROOT / "index.html"
home_source = home_path.read_text(encoding="utf-8")
home = parse(home_path)
topic_path = ROOT / "research-landscape.html"
topic_source = topic_path.read_text(encoding="utf-8") if topic_path.exists() else home_source
topic = parse(topic_path) if topic_path.exists() else home
robots = (ROOT / "robots.txt").read_text(encoding="utf-8") if (ROOT / "robots.txt").exists() else ""
sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8") if (ROOT / "sitemap.xml").exists() else ""

def has_meta(page, kind, key, value):
    return any(tag == kind and attrs.get(key) == value for tag, attrs in page.meta)


def has_link(page, href):
    return any(link == href and label.strip() for link, label in page.links)


def article_detail(name, url):
    # Each source must have a visible, substantial paragraph in its own card.
    for match in re.finditer(r"<article\b[^>]*>(.*?)</article>", topic_source, re.I | re.S):
        fragment = match.group(1)
        if url not in fragment or name.lower() not in fragment.lower():
            continue
        card = Page()
        card.feed(fragment)
        prose = " ".join(card.text)
        if len(prose) >= 180 and re.search(r"\b(2025|2026)\b", prose):
            return True
    return False


checks = {
    "crawl.robots_allows_all": bool(re.search(r"User-agent:\s*\*\s+Allow:\s*/", robots, re.I)),
    "crawl.sitemap_lists_home": SITE in sitemap,
    "crawl.canonical_home": any(tag == "link" and attrs.get("rel") == "canonical" and attrs.get("href") == SITE for tag, attrs in home.meta),
    "crawl.indexable_home": has_meta(home, "meta", "name", "robots") and "noindex" not in home_source.lower(),
    "identity.paper_title_h1": any(tag == "h1" and "Environment" in title and "Co-evolution" in title for tag, title in home.headings),
    "identity.arxiv_link": has_link(home, "https://arxiv.org/abs/2610.16523"),
    "identity.scholarly_schema": '"@type": "ScholarlyArticle"' in home_source and '"identifier": "arXiv:2610.16523"' in home_source,
    "identity.static_results": bool(re.search(r'<tbody id="results-table-body">.*?<tr', home_source, re.S)),
    "query.topic_heading": any(tag in {"h1", "h2"} and "agent" in title.lower() and "environment" in title.lower() and "co-evolution" in title.lower() for tag, title in topic.headings),
    "query.seal_source": has_link(topic, PAPERS["SEAL"]),
    "query.comap_source": has_link(topic, PAPERS["CoMAP"]),
    "query.genenv_source": has_link(topic, PAPERS["GenEnv"]),
    "query.seal_explained": article_detail("SEAL", PAPERS["SEAL"]),
    "query.comap_explained": article_detail("CoMAP", PAPERS["CoMAP"]),
    "query.genenv_explained": article_detail("GenEnv", PAPERS["GenEnv"]),
    "query.eau_positioned": "EAU" in " ".join(topic.text) and bool(re.search(r"user simulator|simulated user", " ".join(topic.text), re.I)),
    "navigation.home_to_topic": any((href == "#research-landscape" or href == "research-landscape.html") and label.strip() for href, label in home.links),
    "navigation.topic_discoverable": (not topic_path.exists() and 'id="research-landscape"' in home_source) or (topic_path.exists() and SITE + "research-landscape.html" in sitemap),
    "quality.keyword_density": " ".join(topic.text).lower().count("co-evolution") <= max(8, len(" ".join(topic.text)) / 500),
    "quality.no_hidden_keyword_block": not bool(re.search(r'<[^>]+hidden[^>]*>[^<]*(?:co-evolution[^<]*){3}', topic_source, re.I)),
}

sections = {part: sum(value for key, value in checks.items() if key.startswith(part + ".")) * 5 for part in ("crawl", "identity", "query", "navigation", "quality")}
score = sum(sections.values())
print(json.dumps({"score": score, "sections": sections, "checks": checks}, ensure_ascii=False, sort_keys=True))
print(f"METRIC={score}")
