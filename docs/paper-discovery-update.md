# Paper discovery update

Date: 2026-10-26

## Repositories

| Role | Repository | Start commit | Completion commit |
|---|---|---|---|
| SITE | cheslyn0712/cheslyn0712.github.io | 0de49d671604942b4ee82929f1ffe9f6202f7143 | recorded after the site commit |
| COT | cheslyn0712/CoT_is_Not_the_Chain_of_Truth | 43ef607c612c73aef628500b3e4d7e5f374940c1 | recorded after the code commit |
| COG | cheslyn0712/CogniDir | c8bd54cd7d49dc57c35b08851d15dd24bd765d8a | recorded after the code commit |

No repository contains an AGENTS.md. All three were on `main`. The recorded start commits match the plan. COT had unrelated local code edits; this update commits only `README.md` there.

## Files

SITE:

- `papers/cot-chain-of-truth.json`
- `papers/cognidir.json`
- `scripts/build_pages.py`
- `scripts/verify_paper_discovery.py`
- `_pages/about.md`
- `_config.yml` (research pages use `layout: null` so the existing Jekyll sitemap can include them)
- `projects/index.html`
- `projects/cot-chain-of-truth/index.html`
- `projects/cognidir/index.html`
- `research/reasoning-trace-safety/index.html`
- `research/robust-fake-news-detection/index.html`
- `docs/paper-discovery-update.md`

COT: `README.md`

COG: `README.md`

Protected citation files were compared with the pre-edit baseline and left unchanged: both `CITATION.cff` files, both README BibTeX blocks, both `paper.bib` files, and the paper JSON fields `title`, `shortTitle`, `authors`, `authorAffiliations`, `venue`, `venueId`, `venueFull`, `year`, `volume`, `pages`, `links`, `bibtex`, and `abstract`.

## Build and checks

```text
python scripts/verify_paper_discovery.py --cot-repo COT_PATH --cognidir-repo COG_PATH --capture-baseline BASELINE_PATH
python scripts/build_pages.py
python scripts/verify_paper_discovery.py --cot-repo COT_PATH --cognidir-repo COG_PATH --baseline BASELINE_PATH --targets TARGETS_PATH
git diff --check
```

Result: exit 0. Checks 01–17 all PASS. `git diff --check` produced no whitespace errors.

## GitHub About

Status: pending_access.

`gh` is not installed, and Git Credential Manager did not return a GitHub token for the API. The request bodies to apply are:

CoT description: `ICML 2026: reasoning-trace safety, Jacobian-based layer and attention-head analysis, and targeted safety intervention.`

CoT homepage: `https://chunlingong.me/projects/cot-chain-of-truth/`

CoT topics: `llm-safety`, `chain-of-thought`, `reasoning-models`, `mechanistic-interpretability`, `attention-heads`, `jacobian-analysis`, `fake-news-generation`

CogniDir description: `EMNLP 2026: robust fake news detection with LLM-generated cognitive comments and adaptive adversarial data mixtures.`

CogniDir homepage: `https://chunlingong.me/projects/cognidir/`

CogniDir topics: `fake-news-detection`, `adversarial-robustness`, `malicious-comments`, `llm-generated-content`, `adaptive-sampling`, `adversarial-training`

## Page review

Reviewed locally at desktop width 1280 and phone width 390.

| Page | Result |
|---|---|
| `/projects/` | verified. Title, both research questions, Paper/Preprint/PDF/Code, and both research notes are present. No page-level horizontal overflow. |
| `/projects/cognidir/` | verified. Research context follows TL;DR. Related research, findings, resources, six questions, publication history, and the arXiv version link are present. Wide tables scroll inside their wrappers. |
| `/projects/cot-chain-of-truth/` | verified. Research context, related research, findings, resources, and six questions are present. No publication-history section. |
| `/research/reasoning-trace-safety/` | verified. Title, byline, four sections, references, and related project link are present. Phone width does not overflow the page. |
| `/research/robust-fake-news-detection/` | verified. Title, byline, four sections, references, and related project link are present. Phone width does not overflow the page. |

The research-note source files include Jekyll front matter so GitHub Pages can publish them and add them to the sitemap. A plain static server shows that front matter; the Jekyll build removes it.

## Release and indexing

Status after the local checks: pending push and live confirmation.

Search Console and Bing Webmaster Tools: pending_access. No site-verification credentials are configured in `_config.yml`. URLs to submit after publication:

- `https://chunlingong.me/projects/cot-chain-of-truth/`
- `https://chunlingong.me/projects/cognidir/`
- `https://chunlingong.me/research/reasoning-trace-safety/`
- `https://chunlingong.me/research/robust-fake-news-detection/`
- `https://chunlingong.me/sitemap.xml`

Search observation across independent ChatGPT and Claude sessions: pending. The 32 questions are listed in section 11 of the execution plan. This environment cannot open those separate sessions, so no observation rows were recorded.
