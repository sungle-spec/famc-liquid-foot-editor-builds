"""
Generate the app-icon assets the installers embed, from one programmatic source.

Renders a 256x256 FAMC-styled icon with Qt (no external art), then emits:
  * packaging/icons/app.png   — always (Linux / AppImage)
  * packaging/icons/app.ico   — if Pillow is installed (Windows EXE)
  * packaging/icons/app.icns  — if `iconutil` is available (macOS .app, i.e. on a mac)

Run:  QT_QPA_PLATFORM=offscreen python packaging/make_icons.py
The PyInstaller spec embeds whichever files exist; missing ones are simply skipped, so a build
never fails just because an icon couldn't be produced on a given OS.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QGuiApplication, QPainter, QPen, QPixmap

OUT = Path(__file__).resolve().parent / "icons"

# Match the editor theme (lfeditor/ui/theme.py): dark panel + FAMC cyan.
BG = "#0e1620"
PANEL = "#16212e"
ACCENT = "#36c9d4"
TEXT = "#eaf2f5"


def render(size: int) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setRenderHint(QPainter.TextAntialiasing, True)

    # rounded dark tile with a cyan rim
    inset = size * 0.06
    tile = QRectF(inset, inset, size - 2 * inset, size - 2 * inset)
    radius = size * 0.20
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(BG))
    p.drawRoundedRect(tile, radius, radius)
    p.setBrush(QColor(PANEL))
    p.drawRoundedRect(tile.adjusted(size * 0.05, size * 0.05, -size * 0.05, -size * 0.05),
                      radius * 0.7, radius * 0.7)
    pen = QPen(QColor(ACCENT))
    pen.setWidthF(size * 0.035)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    p.drawRoundedRect(tile, radius, radius)

    # "LF+" wordmark
    f = QFont("Menlo")
    f.setBold(True)
    f.setPixelSize(int(size * 0.40))
    p.setFont(f)
    p.setPen(QColor(TEXT))
    p.drawText(tile, Qt.AlignCenter, "LF+")
    p.end()
    return pm


def main() -> int:
    QGuiApplication.instance() or QGuiApplication(sys.argv)
    OUT.mkdir(parents=True, exist_ok=True)
    sizes = [16, 32, 64, 128, 256, 512]
    pixmaps = {s: render(s) for s in sizes}

    png = OUT / "app.png"
    pixmaps[256].save(str(png), "PNG")
    print(f"wrote {png}")

    # Windows .ico via Pillow (multi-resolution). Build the PIL images in memory — writing PNGs to
    # a temp dir and reopening them leaks file handles, which makes the temp cleanup fail on
    # Windows (WinError 32: file in use).
    try:
        from io import BytesIO
        from PIL import Image
        from PySide6.QtCore import QBuffer, QByteArray

        def _to_pil(pm):
            ba = QByteArray()
            buf = QBuffer(ba)
            buf.open(QBuffer.WriteOnly)
            pm.save(buf, "PNG")
            buf.close()
            return Image.open(BytesIO(bytes(ba.data()))).copy()   # .copy() detaches from the buffer

        imgs = [_to_pil(render(s)) for s in (16, 32, 48, 64, 128, 256)]
        ico = OUT / "app.ico"
        imgs[0].save(str(ico), format="ICO", sizes=[(im.width, im.height) for im in imgs])
        print(f"wrote {ico}")
    except ImportError:
        print("Pillow not installed — skipping app.ico (Windows icon)")

    # macOS .icns via iconutil (mac only)
    if sys.platform == "darwin" and shutil.which("iconutil"):
        with tempfile.TemporaryDirectory() as d:
            iconset = Path(d) / "app.iconset"
            iconset.mkdir()
            spec = {16: "16x16", 32: "16x16@2x", 64: "32x32@2x", 128: "128x128",
                    256: "128x128@2x", 512: "256x256@2x"}
            for s, label in spec.items():
                render(s).save(str(iconset / f"icon_{label}.png"), "PNG")
            icns = OUT / "app.icns"
            subprocess.run(["iconutil", "-c", "icns", "-o", str(icns), str(iconset)], check=True)
            print(f"wrote {icns}")
    else:
        print("iconutil unavailable (not macOS) — skipping app.icns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
