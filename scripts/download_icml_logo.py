import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "static"
ROOT.mkdir(parents=True, exist_ok=True)

urls = {
    "icml-logo.svg": "https://icml.cc/media/Press/ICML-logo.svg",
    "icml-logo.png": "https://icml.cc/media/Press/ICML-logo.png",
    "icml-navbar-logo.svg": "https://icml.cc/static/core/img/icml-navbar-logo.svg",
}

for name in ["icml-logo.svg", "icml-logo.png", "icml-navbar-logo.svg"]:
    try:
        data = urllib.request.urlopen(urls[name], timeout=30).read()
        out = ROOT / name
        out.write_bytes(data)
        print(f"OK {name} ({len(data)} bytes)")
    except Exception as e:
        print(f"FAIL {name}: {e}")

try:
    from PIL import Image

    src = ROOT / "icml-logo.png"
    out = ROOT / "icml-logo-white-bg.png"
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    pad_x, pad_y = 20, 14
    bg = Image.new("RGBA", (w + pad_x * 2, h + pad_y * 2), (255, 255, 255, 255))
    bg.paste(img, (pad_x, pad_y), img)
    bg.save(out)
    print(f"OK icml-logo-white-bg.png ({out.stat().st_size} bytes)")
except Exception as e:
    print(f"SKIP icml-logo-white-bg.png: {e}")
