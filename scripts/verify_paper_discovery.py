#!/usr/bin/env python3
"""Capture citation baselines and check the paper-discovery update."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS = {
    "cot-chain-of-truth": ROOT / "papers" / "cot-chain-of-truth.json",
    "cognidir": ROOT / "papers" / "cognidir.json",
}
PROJECT_HTML = {
    "cot-chain-of-truth": ROOT / "projects" / "cot-chain-of-truth" / "index.html",
    "cognidir": ROOT / "projects" / "cognidir" / "index.html",
}
PAPER_BIB = {
    "cot-chain-of-truth": ROOT / "projects" / "cot-chain-of-truth" / "paper.bib",
    "cognidir": ROOT / "projects" / "cognidir" / "paper.bib",
}
PROTECTED = [
    "title",
    "shortTitle",
    "authors",
    "authorAffiliations",
    "venue",
    "venueId",
    "venueFull",
    "year",
    "volume",
    "pages",
    "links",
    "bibtex",
    "abstract",
]
EXTRA_ORDER = ["findings", "resources", "related", "faq", "history"]
GENERATED = [
    ROOT / "projects" / "index.html",
    ROOT / "projects" / "cot-chain-of-truth" / "index.html",
    ROOT / "projects" / "cognidir" / "index.html",
    ROOT / "research" / "reasoning-trace-safety" / "index.html",
    ROOT / "research" / "robust-fake-news-detection" / "index.html",
]
HOME = ROOT / "_pages" / "about.md"
COT_INTRO = (
    "We study reasoning-trace safety in language models through trace annotation, "
    "Jacobian-based layer and attention-head analysis, and targeted safety intervention. "
    "The experiments examine fake-news generation and HarmBench tasks."
)
COG_INTRO = (
    "CogniDir strengthens comment-aware fake news detection with mechanism-specific "
    "malicious comments and adaptive adversarial training mixtures. InfoDirichlet "
    "Resampling updates exposure across attack groups using vulnerability feedback."
)
COG_AUTHORS = (
    "Zhao Tong*, <strong>Chunlin Gong*</strong>, Yimeng Gu, Haichao Shi, "
    "Qiang Liu, Shu Wu, Xingcheng Xu, Xiao-Yu Zhang"
)
PAPER_LINKS = {
    "cot": "https://proceedings.mlr.press/v306/tong26e.html",
    "cognidir": "https://aclanthology.org/2026.emnlp-main.655/",
}
OLD_TITLE = (
    "Group-Adaptive Adversarial Learning for Robust Fake News Detection Against Malicious Comments"
)
CURRENT_TITLE = (
    "CogniDir: Combating Cognitive Malicious Comments via Adaptive Distributional "
    "Learning for Robust Fake News Detection"
)


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def bib_block(text: str) -> str:
    match = re.search(r"```bibtex\r?\n(.*?)```", text, re.S)
    if not match:
        raise SystemExit(f"missing bibtex block")
    return match.group(1)


def section_ids(page: str) -> list[str]:
    return re.findall(r'<section class="paper-section" id="([^"]+)"', page)


def section_html(page: str, section_id: str) -> str:
    match = re.search(
        rf'<section class="paper-section" id="{re.escape(section_id)}">(.*?)</section>',
        page,
        re.S,
    )
    return match.group(1) if match else ""


def text_bits(fragment: str) -> str:
    return norm(re.sub(r"<[^>]+>", " ", fragment))


def json_ld_blocks(page: str) -> list[dict]:
    blocks = []
    for raw in re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', page, re.S):
        blocks.append(json.loads(raw))
    return blocks


class Report:
    def __init__(self) -> None:
        self.failed = 0

    def check(self, number: int, name: str, ok: bool, detail: str = "") -> None:
        status = "PASS" if ok else "FAIL"
        if not ok:
            self.failed += 1
        line = f"{number:02d} {status} {name}"
        if detail and not ok:
            line += f" — {detail}"
        print(line)


def capture(cot_repo: Path, cog_repo: Path, dest: Path) -> None:
    papers = {}
    for slug, path in PAPERS.items():
        data = load_json(path)
        papers[slug] = {key: data[key] for key in PROTECTED}
    baseline = {
        "papers": papers,
        "citation_cff": {
            "cot": (cot_repo / "CITATION.cff").read_text(encoding="utf-8"),
            "cognidir": (cog_repo / "CITATION.cff").read_text(encoding="utf-8"),
        },
        "readme_bibtex": {
            "cot": bib_block((cot_repo / "README.md").read_text(encoding="utf-8")),
            "cognidir": bib_block((cog_repo / "README.md").read_text(encoding="utf-8")),
        },
        "paper_bib": {slug: path.read_text(encoding="utf-8") for slug, path in PAPER_BIB.items()},
    }
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(dest)
    return


def overview(readme: str) -> str:
    match = re.search(r"## Overview\r?\n(.*?)(?:\r?\n## |\Z)", readme, re.S)
    return match.group(1) if match else ""


def resource_paths(readme: str) -> list[str]:
    match = re.search(r"## Code and resources\r?\n(.*?)(?:\r?\n## |\Z)", readme, re.S)
    body = match.group(1) if match else ""
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", body)


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_link(href: str, source: Path) -> tuple[Path | None, str]:
    href = href.split("?", 1)[0]
    path_part, _, anchor = href.partition("#")
    if path_part.startswith(("http://", "https://", "mailto:", "javascript:")):
        return None, ""
    base = ROOT if source == HOME else source.parent
    if not path_part:
        return source, anchor
    if path_part == "/":
        return HOME, ""
    if path_part.startswith("/"):
        target = ROOT / path_part.lstrip("/")
    else:
        target = (base / path_part).resolve()
    if target.is_dir() or path_part.endswith("/"):
        target = Path(str(target).rstrip("/\\")) / "index.html"
    return target, anchor


def git_show(relative: str) -> str:
    git = r"C:\Program Files\Git\cmd\git.exe"
    result = subprocess.run(
        [git, "show", f"HEAD:{relative}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def verify(cot_repo: Path, cog_repo: Path, baseline_path: Path, targets_path: Path) -> int:
    report = Report()
    baseline = load_json(baseline_path)
    targets = load_json(targets_path)
    papers = {slug: load_json(path) for slug, path in PAPERS.items()}
    pages = {slug: path.read_text(encoding="utf-8") for slug, path in PROJECT_HTML.items()}
    home = HOME.read_text(encoding="utf-8")
    readmes = {
        "cot": (cot_repo / "README.md").read_text(encoding="utf-8"),
        "cognidir": (cog_repo / "README.md").read_text(encoding="utf-8"),
    }

    mismatched = []
    for slug, payload in targets.items():
        for key, value in payload.items():
            if papers[slug].get(key) != value:
                mismatched.append(f"{slug}.{key}")
    report.check(1, "JSON target fields match the plan payload", not mismatched, ", ".join(mismatched))

    context_ok = True
    context_detail = []
    for slug, page in pages.items():
        ids = section_ids(page)
        if (
            "tldr" not in ids
            or "resources" not in ids
            or "research-context" not in ids
            or ids[ids.index("resources") + 1] != "research-context"
        ):
            context_ok = False
            context_detail.append(slug)
    report.check(2, "Research context follows results and resources", context_ok, ", ".join(context_detail))

    order_ok = True
    order_detail = []
    for slug, page in pages.items():
        present = [item for item in EXTRA_ORDER if section_ids(page).count(item)]
        expected = []
        data = papers[slug]
        if data.get("findings"):
            expected.append("findings")
        if data.get("resources"):
            expected.append("resources")
        if data.get("relatedWork"):
            expected.append("related")
        if data.get("faqs"):
            expected.append("faq")
        if data.get("publicationHistory"):
            expected.append("history")
        if present != expected:
            order_ok = False
            order_detail.append(f"{slug}: {present} != {expected}")
    report.check(3, "Supplementary sections follow the specified order", order_ok, "; ".join(order_detail))

    faq_ok = True
    faq_detail = []
    for slug, page in pages.items():
        block = section_html(page, "faq")
        questions = [norm(item) for item in re.findall(r"<summary>(.*?)</summary>", block, re.S)]
        answers = [norm(item) for item in re.findall(r'<p class="section-text">(.*?)</p>', block, re.S)]
        expected_q = [norm(item["q"]) for item in papers[slug]["faqs"]]
        expected_a = [norm(item["a"]) for item in papers[slug]["faqs"]]
        if len(questions) != 6 or questions != expected_q or answers != expected_a:
            faq_ok = False
            faq_detail.append(slug)
    report.check(4, "Each project page has six FAQs matching the JSON", faq_ok, ", ".join(faq_detail))

    history = section_html(pages["cognidir"], "history")
    history_text = text_bits(history)
    history_ok = (
        OLD_TITLE in history_text
        and CURRENT_TITLE in history_text
        and "2510.09712" in history_text
        and 'href="https://arxiv.org/abs/2510.09712"' in history
        and "arXiv version history" in history_text
    )
    report.check(5, "CogniDir publication history includes titles, arXiv id, and version link", history_ok)

    scholarly = next(item for item in json_ld_blocks(pages["cognidir"]) if item.get("@type") == "ScholarlyArticle")
    report.check(
        6,
        "CogniDir alternateName matches formerTitles",
        scholarly.get("alternateName") == papers["cognidir"]["formerTitles"],
    )

    notes_ok = True
    notes_detail = []
    for slug, data in papers.items():
        note = data["researchNote"]
        page_path = ROOT / "research" / note["slug"] / "index.html"
        page = page_path.read_text(encoding="utf-8")
        title_ok = f"<title>{html.escape(note['title'])} | Chunlin Gong</title>" in page
        h1_ok = f"<h1>{html.escape(note['title'])}</h1>" in page
        byline_ok = "Research note by Chunlin Gong · Updated October 26, 2026" in page
        sections_ok = True
        for section in note["sections"]:
            block = section_html(page, section["id"])
            heading = re.search(r"<h2>(.*?)</h2>", block, re.S)
            paragraphs = [norm(item) for item in re.findall(r'<p class="section-text">(.*?)</p>', block, re.S)]
            if not heading or norm(heading.group(1)) != norm(section["title"]):
                sections_ok = False
            if paragraphs != [norm(item) for item in section["paragraphs"]]:
                sections_ok = False
        refs = section_html(page, "references")
        ref_names = [norm(item) for item in re.findall(r"<a [^>]*>(.*?)</a>", refs, re.S)]
        ref_urls = re.findall(r'<a href="([^"]+)"', refs)
        refs_ok = ref_names == [norm(item["name"]) for item in note["references"]] and ref_urls == [
            item["url"] for item in note["references"]
        ]
        if not (title_ok and h1_ok and byline_ok and sections_ok and refs_ok):
            notes_ok = False
            notes_detail.append(note["slug"])
    report.check(7, "Research notes match title, byline, sections, and references", notes_ok, ", ".join(notes_detail))

    canonical_ok = True
    canonical_detail = []
    for data in papers.values():
        note = data["researchNote"]
        page = (ROOT / "research" / note["slug"] / "index.html").read_text(encoding="utf-8")
        expected = f'{data["siteBase"]}{note["url"]}'
        if f'<link rel="canonical" href="{expected}">' not in page:
            canonical_ok = False
            canonical_detail.append(note["slug"])
    report.check(8, "Research-note canonicals use /research/ paths", canonical_ok, ", ".join(canonical_detail))

    hub = (ROOT / "projects" / "index.html").read_text(encoding="utf-8")
    hub_ok = True
    for data in papers.values():
        if data.get("cardSummary") not in hub:
            hub_ok = False
        if f'href="{data["links"]["code"]}"' not in hub:
            hub_ok = False
        note = data["researchNote"]
        if f'href="{note["url"]}">{html.escape(note["title"])}</a>' not in hub:
            hub_ok = False
        if data["researchQuestion"] not in pages[data["slug"]]:
            hub_ok = False
    report.check(9, "Project index includes summaries, code, and research notes", hub_ok)

    author_names = [author["name"] for author in papers["cognidir"]["authors"]]
    report.check(
        10,
        "Homepage CogniDir authors match JSON order",
        COG_AUTHORS in home and author_names == [
            "Zhao Tong",
            "Chunlin Gong",
            "Yimeng Gu",
            "Haichao Shi",
            "Qiang Liu",
            "Shu Wu",
            "Xingcheng Xu",
            "Xiao-Yu Zhang",
        ],
    )

    home_ok = (
        COT_INTRO in home
        and COG_INTRO in home
        and 'href="/research/reasoning-trace-safety/">Reasoning-Trace Safety: Evaluation, Mechanisms, and Intervention</a>' in home
        and 'href="/research/robust-fake-news-detection/">Robust Fake News Detection under Adversarial Social Context</a>' in home
        and 'alt="CoT is Not the Chain of Truth project figure"' in home
        and 'alt="CogniDir project figure"' in home
    )
    report.check(11, "Homepage introductions and research-note links match section 6", home_ok)

    overview_ok = True
    overview_detail = []
    for key, slug in (("cot", "cot-chain-of-truth"), ("cognidir", "cognidir")):
        body = norm(overview(readmes[key]))
        data = papers[slug]
        cursor = 0
        pieces = [data["tldr"], *data["researchContext"]]
        for piece in pieces:
            found = body.find(norm(piece), cursor)
            if found < 0:
                overview_ok = False
                overview_detail.append(slug)
                break
            cursor = found + len(norm(piece))
        note = data["researchNote"]
        if note["title"] not in body or f'{data["siteBase"]}{note["url"]}' not in readmes[key]:
            overview_ok = False
            overview_detail.append(slug)
    report.check(12, "README overviews match the JSON text", overview_ok, ", ".join(overview_detail))

    missing_paths = []
    for key, repo in (("cot", cot_repo), ("cognidir", cog_repo)):
        for rel in resource_paths(readmes[key]):
            if rel.startswith("http"):
                continue
            if not (repo / rel).exists():
                missing_paths.append(f"{key}:{rel}")
    report.check(13, "README resource paths exist", not missing_paths, ", ".join(missing_paths))

    cot_line = f'**Paper:** [ICML 2026 · PMLR]({PAPER_LINKS["cot"]})'
    cog_line = f'**Paper:** [EMNLP 2026 · ACL Anthology]({PAPER_LINKS["cognidir"]})'
    report.check(
        14,
        "README paper links point to PMLR and ACL",
        readmes["cot"].count(cot_line) == 1 and readmes["cognidir"].count(cog_line) == 1,
    )

    protected_ok = True
    protected_detail = []
    for slug, saved in baseline["papers"].items():
        for key in PROTECTED:
            if papers[slug][key] != saved[key]:
                protected_ok = False
                protected_detail.append(f"{slug}.{key}")
    current_bib = {
        "cot": bib_block(readmes["cot"]),
        "cognidir": bib_block(readmes["cognidir"]),
    }
    for key in ("cot", "cognidir"):
        if current_bib[key] != baseline["readme_bibtex"][key]:
            protected_ok = False
            protected_detail.append(f"readme:{key}")
    current_cff = {
        "cot": (cot_repo / "CITATION.cff").read_text(encoding="utf-8"),
        "cognidir": (cog_repo / "CITATION.cff").read_text(encoding="utf-8"),
    }
    for key in ("cot", "cognidir"):
        if current_cff[key] != baseline["citation_cff"][key]:
            protected_ok = False
            protected_detail.append(f"citation:{key}")
    for slug, saved in baseline["paper_bib"].items():
        if PAPER_BIB[slug].read_text(encoding="utf-8") != saved:
            protected_ok = False
            protected_detail.append(f"paper.bib:{slug}")
    report.check(15, "Protected citation fields and files match the baseline", protected_ok, ", ".join(protected_detail))

    broken = []
    for source in [HOME, *GENERATED]:
        if not source.exists():
            broken.append(str(source))
            continue
        text = source.read_text(encoding="utf-8")
        relative = source.relative_to(ROOT).as_posix()
        previous = set(re.findall(r'(?:href|src)="([^"]+)"', git_show(relative)))
        current = re.findall(r'(?:href|src)="([^"]+)"', text)
        hrefs = current if source not in PROJECT_HTML.values() and source != HOME else [
            href for href in current if href not in previous
        ]
        if source not in PROJECT_HTML.values() and source != HOME and source.name == "index.html" and "projects" in source.parts:
            hrefs = [href for href in current if href not in previous]
        for href in hrefs:
            target, anchor = resolve_link(html.unescape(href), source)
            if target is None:
                continue
            if not target.exists():
                broken.append(f"{source.name} -> {href}")
                continue
            if target.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".svg"}:
                if anchor:
                    broken.append(f"{source.name} -> {href}")
                continue
            page_text = target.read_text(encoding="utf-8")
            if anchor and f'id="{anchor}"' not in page_text and f"id='{anchor}'" not in page_text:
                broken.append(f"{source.name} -> {href}")
    report.check(16, "New internal links resolve to pages or anchors", not broken, "; ".join(broken[:8]))

    before = {path: file_sha(path) for path in GENERATED}
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_pages.py")], check=True, cwd=ROOT)
    after = {path: file_sha(path) for path in GENERATED}
    report.check(17, "A second build leaves generated files unchanged", before == after)

    return 1 if report.failed else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cot-repo", required=True, type=Path)
    parser.add_argument("--cognidir-repo", required=True, type=Path)
    parser.add_argument("--capture-baseline", type=Path)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--targets", type=Path)
    args = parser.parse_args()
    if args.capture_baseline:
        capture(args.cot_repo, args.cognidir_repo, args.capture_baseline)
        return 0
    if not args.baseline or not args.targets:
        parser.error("--baseline and --targets are required unless --capture-baseline is set")
    return verify(args.cot_repo, args.cognidir_repo, args.baseline, args.targets)


if __name__ == "__main__":
    sys.exit(main())
