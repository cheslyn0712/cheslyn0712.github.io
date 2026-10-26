#!/usr/bin/env python3
"""Build static paper project pages from papers/*.json metadata."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS_DIR = ROOT / "papers"
PROJECTS_DIR = ROOT / "projects"
FIGURES_DIR = ROOT / "data" / "figures"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def author_citation_name(full_name: str) -> str:
    parts = full_name.strip().split()
    if len(parts) < 2:
        return full_name
    return f"{parts[-1]}, {' '.join(parts[:-1])}"


PDF_ICON = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7z"></path><path d="M14 2v5h5"></path><path d="M9 13h6M9 17h4"></path></svg>"""

GITHUB_ICON = """<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 1.2A6.8 6.8 0 0 0 5.85 14.45c.34.06.47-.14.47-.33v-1.17c-1.9.42-2.3-.81-2.3-.81-.3-.77-.76-.97-.76-.97-.62-.42.05-.41.05-.41.69.05 1.05.7 1.05.7.6 1.04 1.59.74 1.98.56.06-.45.24-.75.44-.92-1.52-.18-3.13-.76-3.13-3.4 0-.75.27-1.36.7-1.84-.07-.17-.3-.88.07-1.84 0 0 .57-.18 1.86.7A6.36 6.36 0 0 1 8 4.4c.58 0 1.16.08 1.7.23 1.29-.88 1.86-.7 1.86-.7.37.96.14 1.67.07 1.84.44.48.7 1.1.7 1.84 0 2.64-1.61 3.21-3.14 3.39.25.22.47.64.47 1.29v1.9c0 .19.13.39.47.33A6.8 6.8 0 0 0 8 1.2z"></path></svg>"""


VENUE_LOGOS = {
    "icml": {
        "file": "icml-logo.svg",
        "alt": "ICML — International Conference on Machine Learning",
        "label": "ICML",
        "css": "venue-badge-icml",
    },
    "emnlp": {
        "file": "emnlp-2026-main.png",
        "alt": "EMNLP 2026 Main Conference, Budapest",
        "label": "Main",
        "css": "venue-badge-emnlp",
    },
}


def conference_poster(links: dict) -> str | None:
    return links.get("conferencePoster") or links.get("icmlPoster")


def venue_link(links: dict) -> str | None:
    return conference_poster(links) or links.get("venueUrl")


def venue_id(p: dict) -> str:
    return p.get("venueId") or "icml"


def venue_logo(p: dict, asset_root: str, css_class: str = "venue-logo-official") -> str:
    cfg = VENUE_LOGOS.get(venue_id(p), VENUE_LOGOS["icml"])
    src = f'{asset_root.rstrip("/")}/static/{cfg["file"]}'
    return f'<img class="{css_class}" src="{esc(src)}" alt="{esc(cfg["alt"])}" loading="lazy">'


def venue_badge_html(p: dict, asset_root: str) -> str:
    link = venue_link(p.get("links", {}))
    if venue_id(p) in VENUE_LOGOS:
        cfg = VENUE_LOGOS[venue_id(p)]
        logo = venue_logo(p, asset_root)
        label = f'<span class="venue-label">{esc(cfg["label"])}</span>'
        year = esc(p.get("year", ""))
        inner = f'{logo}{label}<span class="venue-year">{year}</span>'
        if link:
            return (
                f'<a class="venue-badge {cfg["css"]}" href="{esc(link)}" '
                f'target="_blank" rel="noopener noreferrer">{inner}</a>'
            )
        return f'<span class="venue-badge {cfg["css"]}">{inner}</span>'
    return f'<p class="venue-badge"><span>{esc(p["venue"])}</span></p>'


def hub_venue_line(p: dict, asset_root: str) -> str:
    link = venue_link(p.get("links", {}))
    year = esc(p["year"])
    if venue_id(p) in VENUE_LOGOS:
        cfg = VENUE_LOGOS[venue_id(p)]
        logo = venue_logo(p, asset_root, "hub-logo-official")
        label = f'<span class="hub-venue-label">{esc(cfg["label"])}</span>'
        tail = (
            f'<span class="hub-venue-text"><span class="hub-venue-sep">·</span>'
            f'{label}<span class="hub-venue-sep">·</span>'
            f'<span class="hub-venue-year">{year}</span></span>'
        )
        if link:
            return (
                f'<p class="hub-venue">'
                f'<a class="hub-venue-logo" href="{esc(link)}" target="_blank" rel="noopener noreferrer">{logo}</a>'
                f'{tail}</p>'
            )
        return f'<p class="hub-venue">{logo}{tail}</p>'
    return f'<p class="hub-venue"><span>{esc(p["venue"])}</span><span class="hub-venue-sep">·</span><span>{year}</span></p>'


def render_authors(authors: list[dict]) -> str:
    chunks = []
    for author in authors:
        tag_chars = []
        if author.get("equal"):
            tag_chars.append("*")
        if author.get("corresponding"):
            tag_chars.append("†")
        tag_suffix = f'<sup class="author-tag">{"".join(tag_chars)}</sup>' if tag_chars else ""
        affs = author.get("affs", [])
        aff_suffix = f'<sup class="author-aff">{",".join(str(i) for i in affs)}</sup>' if affs else ""
        chunks.append(f'<span class="author-name">{esc(author["name"])}{tag_suffix}{aff_suffix}</span>')
    return '<span class="author-sep">, </span>'.join(chunks)


def render_head(p: dict, canonical: str) -> str:
    desc = p["tldr"][:300]
    keywords = ", ".join(p.get("keywords", []))
    authors_json = []
    for a in p["authors"]:
        authors_json.append(
            {
                "@type": "Person",
                "name": a["name"],
            }
        )

    citation_authors = "\n".join(
        f'  <meta name="citation_author" content="{esc(author_citation_name(a["name"]))}">' for a in p["authors"]
    )

    teaser_key = p.get("ogFigureKey", "teaser")
    teaser_file = p["figures"].get(teaser_key, "")
    if teaser_file and not teaser_file.lower().endswith(".pdf"):
        if p.get("figureDir"):
            og_image = f'{p["siteBase"]}/data/figures/{p["figureDir"]}/{teaser_file}'
        else:
            og_image = f'{p["siteBase"]}/data/figures/{teaser_file}'
        social_meta = f"""  <meta property="og:image" content="{esc(og_image)}">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(p["shortTitle"])}">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{esc(og_image)}">"""
    else:
        social_meta = f"""  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{esc(p["shortTitle"])}">
  <meta name="twitter:description" content="{esc(desc)}">"""
    links = p["links"]

    venue_full = p.get("venueFull") or p["venue"]
    same_as = []
    for key in ("paper", "arxiv"):
        value = links.get(key)
        if value and value not in same_as:
            same_as.append(value)
    json_ld = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "headline": p["title"],
        "description": p["abstract"],
        "author": authors_json,
        "datePublished": str(p["year"]),
        "url": canonical,
        "keywords": p.get("keywords", []),
        "isPartOf": {"@type": "PublicationEvent", "name": venue_full},
        "sameAs": same_as,
    }
    if links.get("code"):
        json_ld["mentions"] = {
            "@type": "SoftwareSourceCode",
            "name": f'{p["shortTitle"]} code',
            "codeRepository": links["code"],
        }
    if links.get("pdf"):
        json_ld["encoding"] = {"@type": "MediaObject", "contentUrl": links["pdf"]}
    former_titles = [title for title in (p.get("formerTitles") or []) if title]
    if former_titles:
        json_ld["alternateName"] = former_titles

    doi_meta = ""
    if links.get("doi"):
        doi_meta = f'  <meta name="citation_doi" content="{esc(links["doi"])}">\n'
    pages = p.get("pages") or {}
    page_meta = ""
    if pages.get("first"):
        page_meta += f'  <meta name="citation_firstpage" content="{esc(pages["first"])}">\n'
    if pages.get("last"):
        page_meta += f'  <meta name="citation_lastpage" content="{esc(pages["last"])}">\n'
    if p.get("volume"):
        page_meta += f'  <meta name="citation_volume" content="{esc(p["volume"])}">\n'

    return f"""  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(p["title"])}</title>
  <meta name="description" content="{esc(desc)}">
  <meta name="keywords" content="{esc(keywords)}">
  <meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">
  <link rel="canonical" href="{esc(canonical)}">

  <meta property="og:type" content="article">
  <meta property="og:title" content="{esc(p["title"])}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{esc(canonical)}">
{social_meta}

  <meta name="citation_title" content="{esc(p["title"])}">
{citation_authors}
  <meta name="citation_publication_date" content="{esc(p["year"])}">
  <meta name="citation_conference_title" content="{esc(venue_full)}">
  <meta name="citation_pdf_url" content="{esc(links["pdf"])}">
  <meta name="citation_abstract_html_url" content="{esc(canonical)}">
{page_meta}{doi_meta}
  <script type="application/ld+json">
{json.dumps(json_ld, indent=2)}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{esc(p["_assetRoot"])}/styles.css">
  <link rel="stylesheet" href="{esc(p["_assetRoot"])}/site-overrides.css">
  <link rel="stylesheet" href="{esc(p["_assetRoot"])}/static/paper.css?v=20261026l">"""


def figure_src(p: dict, filename: str) -> str:
    base = f'{p["_assetRoot"]}/data/figures'
    if p.get("figureDir"):
        return f"{base}/{p['figureDir']}/{filename}"
    return f"{base}/{filename}"


def figure_pdf_link(p: dict, png_filename: str) -> str:
    pdf_name = Path(png_filename).stem + ".pdf"
    if p.get("figureDir"):
        rel = Path("data") / "figures" / p["figureDir"] / pdf_name
        href = f'{p["_assetRoot"]}/data/figures/{p["figureDir"]}/{pdf_name}'
    else:
        rel = Path("data") / "figures" / pdf_name
        href = f'{p["_assetRoot"]}/data/figures/{pdf_name}'
    if not (ROOT / rel).is_file():
        return ""
    return href


def fig(p: dict, key: str, alt: str, caption: str, css_class: str = "figure-medium") -> str:
    filename = p["figures"][key]
    src = figure_src(p, filename)
    pdf_href = figure_pdf_link(p, filename)
    vector = (
        f' · <a href="{esc(pdf_href)}" target="_blank" rel="noopener">Vector PDF</a>'
        if pdf_href
        else ""
    )
    cap = f"<figcaption>{caption}{vector}</figcaption>" if caption else ""
    return f"""<figure class="paper-figure {css_class}">
  <img src="{esc(src)}" alt="{esc(alt)}" loading="lazy">
  {cap}
</figure>"""


def fig_file(p: dict, filename: str, alt: str, caption: str, css_class: str = "figure-medium") -> str:
    if p.get("figureDir"):
        src = f'{p["_assetRoot"]}/data/figures/{p["figureDir"]}/{filename}'
    else:
        src = f'{p["_assetRoot"]}/data/figures/{filename}'
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return f"""<figure class="paper-figure {css_class}">
  <img src="{esc(src)}" alt="{esc(alt)}" loading="lazy">
  {cap}
</figure>"""


def build_action_buttons(links: dict) -> list[str]:
    buttons = []
    if links.get("paper"):
        buttons.append(
            f'<a class="button primary" href="{esc(links["paper"])}" target="_blank" rel="noopener noreferrer">Paper</a>'
        )
    if links.get("pdf"):
        buttons.append(
            f'<a class="button" href="{esc(links["pdf"])}" target="_blank" rel="noopener noreferrer"><span class="button-icon">{PDF_ICON}</span><span>PDF</span></a>'
        )
    if links.get("arxiv"):
        buttons.append(
            f'<a class="button" href="{esc(links["arxiv"])}" target="_blank" rel="noopener noreferrer">Preprint</a>'
        )
    if links.get("code"):
        buttons.append(
            f'<a class="button code-link" href="{esc(links["code"])}" target="_blank" rel="noopener noreferrer"><span class="button-icon github-icon">{GITHUB_ICON}</span><span>Code</span></a>'
        )
    if links.get("dataset"):
        buttons.append(f'<a class="button" href="{esc(links["dataset"])}" target="_blank" rel="noopener noreferrer">Data</a>')
    if links.get("poster"):
        buttons.append(f'<a class="button" href="{esc(links["poster"])}" target="_blank" rel="noopener noreferrer">Poster</a>')
    return buttons


def render_research_context(p: dict) -> str:
    paragraphs = [
        f'<p class="section-text">{esc(text)}</p>' for text in (p.get("researchContext") or [])
    ]
    note = p.get("researchNote") or {}
    if note.get("title") and note.get("url"):
        paragraphs.append(
            '<p class="note-row"><span class="note-row-label">Research note</span>'
            f'<a href="{esc(note["url"])}">{esc(note["title"])}</a></p>'
        )
    if not paragraphs:
        return ""
    return (
        '<section class="paper-section" id="research-context"><h2>Research context</h2>'
        + "".join(paragraphs)
        + "</section>"
    )


def render_extra_sections(p: dict) -> str:
    parts: list[str] = []
    rows = p.get("relatedWork") or []
    if rows:
        body = []
        for row in rows:
            name = esc(row["name"])
            if row.get("url"):
                name = (
                    f'<a href="{esc(row["url"])}" target="_blank" rel="noopener noreferrer">{name}</a>'
                )
            body.append(f'<tr><td>{name}</td><td>{esc(row["relation"])}</td></tr>')
        parts.append(
            '<section class="paper-section" id="related"><h2>Related research</h2>'
            '<div class="table-wrap full-width-table scroll-x"><table class="data-table compact">'
            '<thead><tr><th>Work</th><th>Connection</th></tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div></section>'
        )
    findings = p.get("findings") or []
    if findings:
        items = "".join(
            f'<li><strong>{esc(item["title"])}.</strong> {esc(item["text"])}</li>' for item in findings
        )
        parts.append(
            '<section class="paper-section" id="findings"><h2>Research findings</h2>'
            f'<ul class="section-list">{items}</ul></section>'
        )
    resources = p.get("resources") or []
    if resources:
        items = "".join(
            f'<li><a href="{esc(item["url"])}" target="_blank" rel="noopener noreferrer">{esc(item["name"])}</a>'
            f' — {esc(item["description"])}</li>'
            for item in resources
        )
        parts.append(
            '<section class="paper-section" id="resources"><h2>Code and resources</h2>'
            f'<ul class="section-list">{items}</ul></section>'
        )
    faqs = p.get("faqs") or []
    if faqs:
        blocks = "".join(
            f'<h3>{esc(item["q"])}</h3><p class="section-text">{esc(item["a"])}</p>' for item in faqs
        )
        parts.append(f'<section class="paper-section" id="faq"><h2>Questions</h2>{blocks}</section>')
    if p.get("publicationHistory"):
        history_link = ""
        if p.get("slug") == "cognidir":
            history_link = (
                '<p class="section-text"><a href="https://arxiv.org/abs/2510.09712">'
                "arXiv version history</a></p>"
            )
        parts.append(
            '<section class="paper-section" id="history"><h2>Publication history</h2>'
            f'<p class="section-text">{esc(p["publicationHistory"])}</p>{history_link}</section>'
        )
    return "".join(parts)


def author_notes_html(p: dict) -> str:
    equal_names = ", ".join(a["name"] for a in p["authors"] if a.get("equal"))
    corr_names = ", ".join(a["name"] for a in p["authors"] if a.get("corresponding"))
    return (
        f'<p class="paper-notes"><sup>*</sup>Equal contribution: {esc(equal_names)} · '
        f'<sup>†</sup>Corresponding author: {esc(corr_names)}</p>'
    )


def render_paper_page(p: dict) -> str:
    template = p.get("template", "cot")
    if template == "cognidir":
        return render_cognidir_paper_page(p)
    return render_cot_paper_page(p)


def render_metric_cells(values: list[str], highlight: bool = False) -> str:
    tag_open = "<strong>" if highlight else ""
    tag_close = "</strong>" if highlight else ""
    return "".join(f"<td>{tag_open}{esc(v)}{tag_close}</td>" for v in values)


def render_cognidir_main_table(table: dict) -> str:
    body_rows = []
    for group in table["groups"]:
        rows = group["rows"]
        for index, row in enumerate(rows):
            highlight = bool(row.get("highlight"))
            model = f"<strong>{esc(row['model'])}</strong>" if highlight else esc(row["model"])
            type_cell = ""
            if index == 0:
                type_cell = f'<td rowspan="{len(rows)}"><strong>{esc(group["type"])}</strong></td>'
            body_rows.append(
                f"<tr>{type_cell}<td>{model}</td>"
                f"{render_metric_cells(row['weibo16'], highlight)}"
                f"{render_metric_cells(row['weibo20'], highlight)}"
                f"{render_metric_cells(row['rumour'], highlight)}</tr>"
            )

    improvements = table["improvements"]
    improve_row = (
        f'<tr class="table-highlight-row"><td colspan="2"><strong>Δ Improve</strong></td>'
        f"{render_metric_cells(improvements[:3], True)}"
        f"{render_metric_cells(improvements[3:6], True)}"
        f"{render_metric_cells(improvements[6:9], True)}</tr>"
    )
    return f"""<div class="table-wrap full-width-table scroll-x">
  <table class="data-table compact results-matrix">
    <thead>
      <tr>
        <th>Type</th><th>Model</th>
        <th colspan="3">Weibo16</th>
        <th colspan="3">Weibo20</th>
        <th colspan="3">RumourEval-19</th>
      </tr>
      <tr>
        <th colspan="2"></th>
        <th>O</th><th>A</th><th>R</th>
        <th>O</th><th>A</th><th>R</th>
        <th>O</th><th>A</th><th>R</th>
      </tr>
    </thead>
    <tbody>
      {''.join(body_rows)}
      {improve_row}
    </tbody>
  </table>
</div>"""


def render_cognidir_ablation_table(table: dict) -> str:
    rows_html = []
    dataset_counts: dict[str, int] = {}
    for row in table["rows"]:
        dataset_counts[row["dataset"]] = dataset_counts.get(row["dataset"], 0) + 1

    seen: dict[str, int] = {}
    for row in table["rows"]:
        dataset = row["dataset"]
        seen[dataset] = seen.get(dataset, 0) + 1
        dataset_cell = ""
        if seen[dataset] == 1:
            dataset_cell = f'<td rowspan="{dataset_counts[dataset]}"><strong>{esc(dataset)}</strong></td>'

        highlight = bool(row.get("highlight"))
        method = f"<strong>{esc(row['method'])}</strong>" if highlight else esc(row["method"])
        value = lambda key: f"<strong>{esc(row[key])}</strong>" if highlight else esc(row[key])
        rows_html.append(
            f"<tr>{dataset_cell}<td>{method}</td>"
            f"<td>{value('macroF1')}</td><td>{value('acc')}</td>"
            f"<td>{value('f1Real')}</td><td>{value('f1Fake')}</td></tr>"
        )

    return f"""<div class="table-wrap full-width-table scroll-x">
  <table class="data-table compact">
    <thead>
      <tr><th>Dataset</th><th>Method</th><th>Macro-F1</th><th>Acc.</th><th>F1-real</th><th>F1-fake</th></tr>
    </thead>
    <tbody>{''.join(rows_html)}</tbody>
  </table>
</div>"""


def render_cognidir_paper_page(p: dict) -> str:
    asset = p["_assetRoot"]
    canonical = f'{p["siteBase"]}/projects/{p["slug"]}/'
    links = p["links"]

    aff_list = "".join(
        f"<li><sup>{i + 1}</sup>{esc(a)}</li>" for i, a in enumerate(p["authorAffiliations"])
    )
    stats = "".join(
        f'<div class="paper-stat"><strong>{esc(s["value"])}</strong><span>{esc(s["label"])}</span></div>'
        for s in p.get("stats", [])
    )
    contributions = "".join(f"<li>{esc(c)}</li>" for c in p["contributions"])
    main_results = "".join(f"<li>{esc(r)}</li>" for r in p["mainResults"])

    taxonomy = "".join(
        f"""<article class="taxonomy-card">
  <span class="taxonomy-tag">{esc(c["tag"])}</span>
  <h3>{esc(c["name"])}</h3>
  <p>{esc(c["description"])}</p>
</article>"""
        for c in p["attackCategories"]
    )

    result_rows = render_cognidir_main_table(p["mainResultsTable"])
    ablation_table = render_cognidir_ablation_table(p["ablationTable"])
    main_table_caption = esc(p["mainResultsTable"]["caption"])
    ablation_caption = esc(p["ablationTable"]["caption"])

    nav = """
      <a href="#teaser">Overview</a>
      <a href="#framework">Framework</a>
      <a href="#results">Results</a>
      <a href="#bibtex">BibTeX</a>"""

    bib = esc(p["bibtex"])

    return f"""<!doctype html>
<html lang="en">
<head>
{render_head(p, canonical)}
</head>
<body>
  <div class="site-shell">
    <header class="site-header site-header-nav-only">
      <nav class="site-nav">{nav}
        <a href="{esc(links['pdf'])}" target="_blank" rel="noopener noreferrer">PDF</a>
      </nav>
    </header>

    <main class="paper-page" id="top">
      <header class="paper-hero">
        {venue_badge_html(p, asset)}
        <h1>{esc(p["title"])}</h1>
        <p class="paper-authors">{render_authors(p["authors"])}</p>
        <ol class="paper-affiliations">{aff_list}</ol>
        {author_notes_html(p)}
        <div class="paper-hero-actions">{''.join(build_action_buttons(links))}</div>
        <div class="paper-hero-stats">{stats}</div>
      </header>

      <section class="paper-section" id="tldr">
        <h2>TL;DR</h2>
        <p class="lead-text">{esc(p["tldr"])}</p>
      </section>

      {render_research_context(p)}

      <section class="paper-section" id="teaser">
        <h2>Cognitive Attacks Break Static Defenses</h2>
        <p class="section-text">{esc(p.get("teaserText", ""))}</p>
        {fig(p, "teaser", "Group-wise F1 comparison under cognitive malicious comments", "<strong>Figure 1.</strong> Group-wise F1 on Weibo16: prior methods drop sharply under diverse malicious comments; CogniDir maintains high robust F1.", "figure-teaser")}
      </section>

      <section class="paper-section" id="framework">
        <h2>Framework</h2>
        <p class="section-text">{esc(p["methodOverview"])}</p>
        {fig(p, "framework", "CogniDir framework overview", "<strong>Figure 2.</strong> Cognitive malicious comment synthesis, InfoDirichlet Resampling (IDR), and robust evaluation under mixed attack settings.", "figure-full")}
      </section>

      <section class="paper-section" id="contributions">
        <h2>Key Contributions</h2>
        <ul class="section-list">{contributions}</ul>
      </section>

      <section class="paper-section" id="attacks">
        <h2>Cognitive Attack Taxonomy</h2>
        <p class="section-text">Grounded in cognitive psychology, we categorize adversarial comments into three complementary mechanisms and synthesize mechanism-labeled training data with multiple LLMs.</p>
        <div class="taxonomy-grid">{taxonomy}</div>
      </section>

      <section class="paper-section" id="results">
        <h2>Main Results</h2>
        <ul class="section-list">{main_results}</ul>

        <h3 class="subsection-title">Performance vs. Baselines</h3>
        <p class="section-text">{main_table_caption}</p>
        {result_rows}

        <h3 class="subsection-title">Attack Success Rate (ASR)</h3>
        <p class="section-text">{esc(p.get("asrText", ""))}</p>
        <div class="asr-grid">
          {fig(p, "asrBefore", "ASR before robust training", "<strong>Figure 3a.</strong> ASR before robust training under varying attack types and comment counts.", "figure-asr")}
          {fig(p, "asrAfter", "ASR after CogniDir training", "<strong>Figure 3b.</strong> ASR after robust training — substantial reduction across attack types.", "figure-asr")}
        </div>

        <h3 class="subsection-title">Adaptive Robustness During Training</h3>
        <p class="section-text">Validation accuracy rises for all attack groups and the inter-group gap shrinks from 0.23 to 0.08, showing IDR reallocates learning toward weaker mechanisms.</p>
        {fig(p, "convergence", "Validation accuracy convergence across attack groups", "<strong>Figure 4.</strong> Group-wise validation accuracy during training — Fact Distortion, Logical Confusion, and Emotional Manipulation.", "figure-large")}

        <h3 class="subsection-title">Ablation Study</h3>
        <p class="section-text">{ablation_caption}</p>
        {ablation_table}
      </section>

      <section class="paper-section" id="method">
        <h2>Allocation</h2>
        <p class="section-text">{esc(p["priorWorkDiff"])}</p>
      </section>

      {render_extra_sections(p)}

      <section class="paper-section" id="bibtex">
        <h2>BibTeX</h2>
        <p class="section-text">Official EMNLP BibTeX. Download: <a href="./paper.bib" download="cognidir.bib">paper.bib</a></p>
        <pre class="codeblock bibtex-block"><code id="bibtex-content">{bib}</code></pre>
        <button class="button" type="button" id="copy-bibtex">Copy BibTeX</button>
      </section>
    </main>
  </div>
  <script src="{esc(asset)}/static/copy-bibtex.js" defer></script>
</body>
</html>
"""


def render_cot_paper_page(p: dict) -> str:
    asset = p["_assetRoot"]
    canonical = f'{p["siteBase"]}/projects/{p["slug"]}/'
    links = p["links"]

    action_buttons = build_action_buttons(links)

    aff_list = "".join(
        f"<li><sup>{i + 1}</sup>{esc(a)}</li>" for i, a in enumerate(p["authorAffiliations"])
    )

    stats = "".join(
        f'<div class="paper-stat"><strong>{esc(s["value"])}</strong><span>{esc(s["label"])}</span></div>'
        for s in p.get("stats", [])
    )

    contributions = "".join(f"<li>{esc(c)}</li>" for c in p["contributions"])
    main_results = "".join(f"<li>{esc(r)}</li>" for r in p["mainResults"])

    taxonomy = "".join(
        f"""<article class="taxonomy-card">
  <span class="taxonomy-tag">{esc(c["tag"])}</span>
  <h3>{esc(c["name"])}</h3>
  <p>{esc(c["description"])}</p>
  <div class="taxonomy-meta"><span>CoT: {esc(c["cot"])}</span><span>Response: {esc(c["response"])}</span></div>
</article>"""
        for c in p["cotCategories"]
    )

    distributions = ""
    for d in p["distributions"]:
        distributions += f"""
<article class="distribution-block">
  <h3>{esc(d["title"])}</h3>
  <p class="distribution-lead">{esc(d["description"])}</p>
  {fig_file(p, d["figure"], d["title"], f"<strong>{esc(d['caption'])}</strong>", "figure-pie")}
</article>"""

    layer_rows = "".join(
        f"<tr><td><strong>{esc(r['model'])}</strong></td><td>{esc(r['direct'])}</td><td>{esc(r['indirect'])}</td></tr>"
        for r in p["criticalLayers"]
    )

    layer_figs = "".join(
        f"""<figure class="paper-figure figure-compact-inline">
  <img src="{esc(asset)}/data/figures/{esc(p['figures'][k])}" alt="{esc(alt)}" loading="lazy">
  <figcaption>{esc(alt)}</figcaption>
</figure>"""
        for k, alt in [
            ("layerLlama", "Llama3-8B layer separation"),
            ("layerQwen4B", "Qwen3-4B layer separation"),
            ("layerQwen8B", "Qwen3-8B layer separation"),
        ]
    )

    metrics = "".join(
        f"""<article class="metric-panel">
  <header class="metric-panel-head"><span class="metric-id">{esc(m["id"])}</span><h3>{esc(m["name"])}</h3><p>{esc(m["summary"])}</p></header>
  <figure class="paper-figure figure-metric">
    <img src="{esc(asset)}/data/figures/{esc(m["figure"])}" alt="{esc(m["name"])} metric plot" loading="lazy">
    <figcaption>{esc(m["caption"])}</figcaption>
  </figure>
</article>"""
        for m in p["metrics"]
    )

    mitigation_rows = "".join(
        f"<tr><td><strong>{esc(r['model'])}</strong></td><td>{esc(r['ftRatio'])}</td><td>{esc(r['news'])}</td><td>{esc(r['harmbench'])}</td></tr>"
        for r in p["mitigation"]
    )

    correlation_rows = "".join(
        f"<tr><td>{esc(r['model'])}</td><td>{esc(r['b1'])}</td><td>{esc(r['b2'])}</td><td>{esc(r['b3'])}</td></tr>"
        for r in p.get("correlationData", [])
    )

    nav = """
      <a href="#framework">Framework</a>
      <a href="#results">Results</a>
      <a href="#method">Method</a>
      <a href="#bibtex">BibTeX</a>"""

    venue_html = venue_badge_html(p, asset)

    author_notes = author_notes_html(p)

    bib = esc(p["bibtex"])

    return f"""<!doctype html>
<html lang="en">
<head>
{render_head(p, canonical)}
</head>
<body>
  <div class="site-shell">
    <header class="site-header site-header-nav-only">
      <nav class="site-nav">{nav}
        <a href="{esc(links['pdf'])}" target="_blank" rel="noopener noreferrer">PDF</a>
      </nav>
    </header>

    <main class="paper-page" id="top">
      <header class="paper-hero">
        {venue_html}
        <h1>{esc(p["title"])}</h1>
        <p class="paper-authors">{render_authors(p["authors"])}</p>
        <ol class="paper-affiliations">{aff_list}</ol>
        {author_notes}
        <div class="paper-hero-actions">{''.join(action_buttons)}</div>
        <div class="paper-hero-stats">{stats}</div>
      </header>

      <section class="paper-section" id="tldr">
        <h2>TL;DR</h2>
        <p class="lead-text">{esc(p["tldr"])}</p>
      </section>

      {render_research_context(p)}

      <section class="paper-section" id="framework">
        <h2>Framework</h2>
        <p class="section-text">{esc(p["methodOverview"])}</p>
        {fig(p, "framework", "Unified safety-analysis framework overview", "<strong>Framework overview.</strong> CoT generation and annotation, critical-layer localization, Jacobian head metrics (B1–B3), and perturbation analysis.", "figure-full")}
      </section>

      <section class="paper-section" id="contributions">
        <h2>Key Contributions</h2>
        <ul class="section-list">{contributions}</ul>
      </section>

      <section class="paper-section" id="introduction">
        <h2>Unsafe CoT Persists Despite Refusal</h2>
        <p class="section-text">{esc(p.get("introText", ""))}</p>
        {fig(p, "teaser", "Unsafe CoT generation across reasoning LLMs", "<strong>Figure 1.</strong> Unsafe CoT traces persist despite final refusal; thinking mode increases unsafe rates to nearly 80%.", "figure-teaser")}
      </section>

      <section class="paper-section" id="dataset">
        <h2>CoT Safety Taxonomy &amp; Distribution</h2>
        <p class="section-text">We annotate each CoT as Safe, Potential Unsafe, or Unsafe under direct and indirect prompting. Each stylistic setting is reported separately below.</p>
        <div class="taxonomy-grid">{taxonomy}</div>
        <div class="distribution-grid">{distributions}</div>
      </section>

      <section class="paper-section" id="results">
        <h2>Main Results</h2>
        <ul class="section-list">{main_results}</ul>

        <h3 class="subsection-title">Safety-Critical Layer Localization</h3>
        <p class="section-text">{esc(p.get("layerText", ""))}</p>
        <div class="table-wrap full-width-table">
          <table class="data-table compact">
            <thead><tr><th>Model</th><th>Direct Prompting</th><th>Indirect Prompting</th></tr></thead>
            <tbody>{layer_rows}</tbody>
          </table>
        </div>
        <div class="layer-grid">{layer_figs}</div>

        <h3 class="subsection-title">Perturbation Sensitivity</h3>
        {fig(p, "perturbation", "Layer perturbation sensitivity in Llama3-8B", "<strong>Figure 4.</strong> Critical layers exhibit greater sensitivity under perturbation (Llama3-8B, indirect prompting).", "figure-large")}

        <h3 class="subsection-title">Jacobian Spectral Metrics (B1, B2, B3)</h3>
        <p class="section-text">Safe reasoning shows lower B1/B2 and higher B3, indicating stronger stability and broader spectral participation.</p>
        <div class="metrics-grid">{metrics}</div>

        <h3 class="subsection-title">Metric Correlation</h3>
        <div class="correlation-block">
          <p class="correlation-lead">{esc(p["correlationSummary"])}</p>
          <div class="table-wrap correlation-table-wrap">
            <table class="data-table compact correlation-table">
              <thead><tr><th>Model</th><th>B1</th><th>B2</th><th>B3</th></tr></thead>
              <tbody>{correlation_rows}</tbody>
            </table>
          </div>
          {fig(p, "correlation", "Correlation between Jacobian metrics and safety routing", "<strong>Figure 5.</strong> Correlation between Jacobian-based metrics and safety-relevant routing.", "figure-correlation-inline")}
        </div>

        <h3 class="subsection-title">Generalization Beyond Fake News</h3>
        <p class="section-text">{esc(p.get("generalizationSummary", ""))}</p>

        <h3 class="subsection-title">Critical-Head Mitigation</h3>
        <div class="table-wrap full-width-table">
          <table class="data-table compact">
            <thead><tr><th>Model</th><th>FT Ratio</th><th>News Before / After</th><th>HarmBench Before / After</th></tr></thead>
            <tbody>
              {mitigation_rows}
              <tr><td colspan="2"><strong>Average improvement</strong></td><td><strong>+67.1</strong></td><td><strong>+55.0</strong></td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="paper-section" id="method">
        <h2>What this analysis adds</h2>
        <p class="section-text">{esc(p["priorWorkDiff"])}</p>
      </section>

      {render_extra_sections(p)}

      <section class="paper-section" id="bibtex">
        <h2>BibTeX</h2>
        <p class="section-text">Official PMLR BibTeX. Download: <a href="./paper.bib" download="cot-chain-of-truth.bib">paper.bib</a></p>
        <pre class="codeblock bibtex-block"><code id="bibtex-content">{bib}</code></pre>
        <button class="button" type="button" id="copy-bibtex">Copy BibTeX</button>
      </section>
    </main>
  </div>
  <script src="{esc(asset)}/static/copy-bibtex.js" defer></script>
</body>
</html>
"""


def render_hub(papers: list[dict], *, asset_root: str, paper_href_prefix: str, canonical: str) -> str:
    description = (
        "Research on reasoning-model safety and robust misinformation detection, "
        "with methods, empirical findings, and code."
    )
    cards = []
    notes = []
    for p in papers:
        url = f'{paper_href_prefix}{p["slug"]}/'
        links = p["links"]
        note = p.get("researchNote") or {}
        note_link = ""
        if note.get("title") and note.get("url"):
            note_link = (
                f'<p class="note-row"><span class="note-row-label">Research note</span>'
                f'<a href="{esc(note["url"])}">{esc(note["title"])}</a></p>'
            )
            notes.append(
                '<article class="hub-note-card">'
                '<span class="note-row-label">Research note</span>'
                '<div class="hub-note-copy">'
                f'<h3><a href="{esc(note["url"])}">{esc(note["title"])}</a></h3>'
                f'<p>{esc(note.get("description", ""))}</p>'
                '</div></article>'
            )
        cards.append(
            f"""<article class="hub-card">
  <h2><a href="{esc(url)}">{esc(p["shortTitle"])}</a></h2>
  {hub_venue_line(p, asset_root)}
  <p class="hub-kicker">Research area: {esc(p.get("researchTheme", ""))}</p>
  <p class="hub-question">{esc(p.get("researchQuestion", ""))}</p>
  <p class="hub-summary">{esc(p["tldr"])}</p>
  <p class="hub-links"><a href="{esc(url)}">Project</a><span>·</span><a href="{esc(links.get("paper") or links["arxiv"])}" target="_blank" rel="noopener noreferrer">Paper</a><span>·</span><a href="{esc(links["arxiv"])}" target="_blank" rel="noopener noreferrer">Preprint</a><span>·</span><a href="{esc(links["pdf"])}" target="_blank" rel="noopener noreferrer">PDF</a><span>·</span><a href="{esc(links["code"])}" target="_blank" rel="noopener noreferrer">Code</a></p>
  {note_link}
</article>"""
        )

    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Research projects",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "url": f'{p["siteBase"]}/projects/{p["slug"]}/',
                "name": p["shortTitle"],
            }
            for i, p in enumerate(papers)
        ],
    }

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Research Projects | Chunlin Gong</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="{esc(canonical)}">
  <script type="application/ld+json">
{json.dumps(item_list, indent=2)}
  </script>
  <link rel="stylesheet" href="{esc(asset_root)}/styles.css">
  <link rel="stylesheet" href="{esc(asset_root)}/site-overrides.css">
  <link rel="stylesheet" href="{esc(asset_root)}/static/paper.css?v=20261026l">
</head>
<body>
  <div class="site-shell">
    <header class="site-header site-header-nav-only">
      <nav class="site-nav">
        <a href="/">Home</a>
        <a href="#research-notes">Research notes</a>
      </nav>
    </header>
    <main class="hub-page">
    <h1>Research projects</h1>
    <p class="hub-intro">{esc(description)}</p>
    <div class="hub-grid">{''.join(cards)}</div>
    <section class="paper-section" id="research-notes">
      <h2>Research notes</h2>
      <p class="section-text">Research perspectives on reasoning-trace safety and robust fake news detection.</p>
      <div class="hub-note-grid">{''.join(notes)}</div>
    </section>
  </main>
  </div>
</body>
</html>"""


def render_research_note(p: dict) -> str:
    note = p["researchNote"]
    canonical = f'{p["siteBase"]}{note["url"]}'
    links = p["links"]
    sections = []
    for section in note["sections"]:
        paragraphs = "".join(
            f'<p class="section-text">{esc(paragraph)}</p>' for paragraph in section["paragraphs"]
        )
        sections.append(
            f'<section class="paper-section" id="{esc(section["id"])}">'
            f'<h2>{esc(section["title"])}</h2>{paragraphs}</section>'
        )
    references = "".join(
        f'<li><a href="{esc(item["url"])}">{esc(item["name"])}</a></li>' for item in note["references"]
    )
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": note["title"],
        "description": note["description"],
        "author": {"@type": "Person", "name": note["author"]},
        "dateModified": note["updated"],
        "url": canonical,
        "mainEntityOfPage": canonical,
        "about": {
            "@type": "ScholarlyArticle",
            "name": p["title"],
            "url": links["paper"],
        },
        "citation": [item["url"] for item in note["references"]],
    }
    return f"""---
layout: null
sitemap: true
---
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(note["title"])} | Chunlin Gong</title>
  <meta name="description" content="{esc(note["description"])}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="{esc(canonical)}">
  <script type="application/ld+json">
{json.dumps(article, indent=2)}
  </script>
  <link rel="stylesheet" href="../../styles.css">
  <link rel="stylesheet" href="../../site-overrides.css">
  <link rel="stylesheet" href="../../static/paper.css?v=20261026l">
</head>
<body>
  <div class="site-shell">
    <header class="site-header site-header-nav-only">
      <nav class="site-nav">
        <a href="/projects/">Projects</a>
        <a href="/projects/{esc(p["slug"])}/">Project</a>
        <a href="{esc(links["paper"])}" target="_blank" rel="noopener noreferrer">Paper</a>
        <a href="{esc(links["code"])}" target="_blank" rel="noopener noreferrer">Code</a>
      </nav>
    </header>
    <main class="paper-page">
      <header class="paper-hero">
        <h1>{esc(note["title"])}</h1>
        <p class="paper-byline">Research note by Chunlin Gong · Updated October 26, 2026</p>
        <p class="lead-text">{esc(note["lead"])}</p>
      </header>
      {''.join(sections)}
      <section class="paper-section" id="references">
        <h2>References</h2>
        <ul class="section-list">{references}</ul>
      </section>
      <section class="paper-section" id="project">
        <h2>Related project</h2>
        <p class="note-row"><span class="note-row-label">Project</span><a href="/projects/{esc(p["slug"])}/">{esc(p["title"])}</a></p>
        <div class="paper-hero-actions note-actions">
          <a class="button primary" href="/projects/{esc(p["slug"])}/">Project</a>
          <a class="button" href="{esc(links["paper"])}" target="_blank" rel="noopener noreferrer">Paper</a>
          <a class="button code-link" href="{esc(links["code"])}" target="_blank" rel="noopener noreferrer"><span class="button-icon github-icon">{GITHUB_ICON}</span><span>Code</span></a>
        </div>
      </section>
    </main>
  </div>
</body>
</html>
"""


def render_root_redirect(site_base: str) -> str:
    canonical = f"{site_base}/projects/"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Research Project Pages</title>
  <meta http-equiv="refresh" content="0; url=./projects/">
  <link rel="canonical" href="{esc(canonical)}">
</head>
<body>
  <p><a href="./projects/">Research Project Pages</a></p>
</body>
</html>"""


def build() -> None:
    papers: list[dict] = []
    for json_path in sorted(PAPERS_DIR.glob("*.json")):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        if not data.get("published", False):
            continue
        slug = data["slug"]
        out_dir = PROJECTS_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)

        depth = len(out_dir.relative_to(ROOT).parts)
        data["_assetRoot"] = "/".join([".."] * depth)

        page_html = render_paper_page(data)
        (out_dir / "index.html").write_text(page_html, encoding="utf-8")
        (out_dir / "paper.bib").write_text(data["bibtex"], encoding="utf-8")
        note = data.get("researchNote") or {}
        if note.get("slug"):
            note_dir = ROOT / "research" / note["slug"]
            note_dir.mkdir(parents=True, exist_ok=True)
            note_html = render_research_note(data)
            (note_dir / "index.html").write_text(note_html, encoding="utf-8")
            print(f"Built {note_dir / 'index.html'}")
        papers.append(data)
        print(f"Built {out_dir / 'index.html'}")

    site_base = papers[0]["siteBase"] if papers else "https://example.com"
    projects_hub = render_hub(
        papers,
        asset_root="..",
        paper_href_prefix="./",
        canonical=f"{site_base}/projects/",
    )
    (PROJECTS_DIR / "index.html").write_text(projects_hub, encoding="utf-8")
    # The Jekyll homepage, robots.txt, and sitemap stay under _config.yml.
    # A static index.html or a project-only sitemap would replace them.
    if not (ROOT / "_config.yml").exists():
        (ROOT / "index.html").write_text(render_root_redirect(site_base), encoding="utf-8")
        sitemap_entries = [
            f"  <url><loc>{esc(site_base)}/projects/</loc></url>",
            *[
                f"  <url><loc>{esc(p['siteBase'])}/projects/{esc(p['slug'])}/</loc></url>"
                for p in papers
            ],
        ]
        (ROOT / "sitemap.xml").write_text(
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
            + "\n".join(sitemap_entries)
            + "\n</urlset>\n",
            encoding="utf-8",
        )
        (ROOT / "robots.txt").write_text(
            f"User-agent: *\nAllow: /\n\nSitemap: {site_base}/sitemap.xml\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    build()
