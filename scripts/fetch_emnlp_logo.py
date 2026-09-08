import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "static"
ROOT.mkdir(parents=True, exist_ok=True)

candidates = [
    "https://2026.emnlp.org/assets/img/logo.svg",
    "https://2026.emnlp.org/assets/images/logo.svg",
    "https://2026.emnlp.org/images/logo.png",
    "https://aclanthology.org/images/acl-logo.svg",
]

for url in candidates:
    name = url.rsplit("/", 1)[-1]
    try:
        data = urllib.request.urlopen(url, timeout=20).read()
        out = ROOT / f"emnlp-logo-{name}"
        out.write_bytes(data)
        print("OK", url, len(data))
    except Exception as exc:
        print("FAIL", url, exc)
