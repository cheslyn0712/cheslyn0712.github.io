"""Export CogniDir figure PDFs from latex/figs/ to PNG for web display.

Exports the full source figure PDF (vector → raster at high DPI).
Does NOT crop from paper.pdf or take page screenshots.
Also keeps verbatim PDF copies for download links.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import fitz

SRC = Path(r"D:\桌面\PhD_Reseach\EMNLP_2026\EMNLP2026\latex\figs")
OUT = Path(__file__).resolve().parents[1] / "data" / "figures" / "cognidir"

FIGURES = (
    "Teaser0120_clean_noborder.pdf",
    "Method1833_clean_notext_0826.pdf",
    "ASR_ori_grid.pdf",
    "ASR_com_grid.pdf",
    "VAL_grid.pdf",
)

SCALE = 3.0


def export_pdf(pdf_path: Path, png_path: Path) -> None:
    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(SCALE, SCALE), alpha=False)
    pix.save(png_path)
    print(f"exported {png_path.name} ({pix.width}x{pix.height})")


def main() -> None:
    if not SRC.is_dir():
        raise SystemExit(f"Missing figure source directory: {SRC}")
    OUT.mkdir(parents=True, exist_ok=True)
    for name in FIGURES:
        src = SRC / name
        if not src.is_file():
            raise SystemExit(f"Missing source figure: {src}")
        shutil.copy2(src, OUT / name)
        export_pdf(src, OUT / f"{src.stem}.png")


if __name__ == "__main__":
    main()
