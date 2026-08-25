#!/usr/bin/env python3
"""Export diagram HTML → PNG via local Google Chrome headless, then patch markdown."""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DIR = Path(__file__).parent
MD = DIR.parent / "hermes-agent-kernel-architecture-and-development-guide.md"
SCALE = 2
FONT_LINK = (
    "https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
    "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap"
)


def extract_svg(html: str) -> str:
    m = re.search(r"<svg\b[\s\S]*?</svg>", html, re.I)
    if not m:
        raise ValueError("no svg found")
    return m.group(0)


def viewbox_size(svg: str) -> tuple[int, int]:
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    if not m:
        raise ValueError("no viewBox")
    return int(m.group(1)), int(m.group(2))


def render_png(html_path: Path, png_path: Path) -> None:
    html = html_path.read_text(encoding="utf-8")
    svg = extract_svg(html)
    w, h = viewbox_size(svg)
    # viewport in CSS pixels; Chrome screenshot uses device scale via --force-device-scale-factor
    vw, vh = w, h
    page = f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<link href="{FONT_LINK}" rel="stylesheet">
<style>
  html, body {{ margin: 0; padding: 0; background: #f5f5f5; }}
  svg {{ display: block; width: {w}px; height: {h}px; }}
</style>
</head><body>{svg}</body></html>"""

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "diagram.html"
        tmp.write_text(page, encoding="utf-8")
        out = Path(td) / "shot.png"
        cmd = [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--no-sandbox",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=3000",
            f"--force-device-scale-factor={SCALE}",
            f"--window-size={vw},{vh}",
            f"--screenshot={out}",
            tmp.resolve().as_uri(),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if not out.exists():
            raise RuntimeError(
                f"Chrome screenshot failed for {html_path.name}:\n"
                f"stdout={r.stdout}\nstderr={r.stderr}"
            )
        png_path.write_bytes(out.read_bytes())
        print(f"PNG {png_path.name} ({w*SCALE}x{h*SCALE})")


def patch_markdown() -> None:
    text = MD.read_text(encoding="utf-8")
    # > **图：TITLE**
    # > [查看交互式架构图](./hermes-agent-kernel-diagrams/NAME.html)
    pattern = re.compile(
        r"> \*\*图：([^*]+)\*\*  \n"
        r"> \[查看交互式架构图\]\(\./hermes-agent-kernel-diagrams/([^)]+)\.html\)"
    )

    def repl(m: re.Match) -> str:
        title, name = m.group(1), m.group(2)
        return f"![{title}](./hermes-agent-kernel-diagrams/{name}.png)"

    new, n = pattern.subn(repl, text)
    MD.write_text(new, encoding="utf-8")
    print(f"Markdown: replaced {n} figure links with PNG images")


def main() -> None:
    htmls = sorted(DIR.glob("*.html"))
    if not htmls:
        raise SystemExit("no html diagrams")
    for html in htmls:
        render_png(html, html.with_suffix(".png"))
    patch_markdown()


if __name__ == "__main__":
    main()
