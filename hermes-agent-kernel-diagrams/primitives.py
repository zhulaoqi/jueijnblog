#!/usr/bin/env python3
"""Editorial SVG primitives for the Hermes article diagrams."""

from __future__ import annotations

from html import escape
from typing import Iterable, Sequence
from unicodedata import east_asian_width

PAPER = "#f5f5f5"
WHITE = "#ffffff"
INK = "#2d3142"
MUTED = "#4f5d75"
SOFT = "#7a8399"
ACCENT = "#eb6c36"
ACCENT_TINT = "rgba(235,108,54,0.08)"
LINK = "#2e5aa8"
RULE = "rgba(45,49,66,0.12)"
WASH = "rgba(45,49,66,0.03)"

CSS = """
*,*::before,*::after{box-sizing:border-box}
html,body{margin:0;background:#f5f5f5;color:#2d3142}
body{font-family:'Geist',system-ui,sans-serif;padding:32px 20px}
.frame{width:min(1200px,100%);margin:0 auto}
.eyebrow{margin:0 0 8px;font:500 12px/1.3 'Geist Mono',monospace;
  letter-spacing:.16em;text-transform:uppercase;color:#4f5d75}
h1{margin:0 0 20px;font:400 32px/1.12 'Instrument Serif',serif;
  letter-spacing:-.02em}
.diagram-scroll{overflow-x:auto}
svg{display:block;width:100%;min-width:880px;height:auto}
@media(max-width:720px){body{padding:20px 12px}h1{font-size:28px}}
"""


def _grid(*values: int) -> None:
    invalid = [value for value in values if value % 4]
    if invalid:
        raise ValueError(f"geometry must use the 4px grid: {invalid}")


def marker_ids(slug: str) -> dict[str, str]:
    return {
        "default": f"{slug}-arrow",
        "accent": f"{slug}-arrow-accent",
        "link": f"{slug}-arrow-link",
    }


def markers(slug: str) -> str:
    ids = marker_ids(slug)
    return f"""
      <defs>
        <marker id="{ids['default']}" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/>
        </marker>
        <marker id="{ids['accent']}" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill="{ACCENT}"/>
        </marker>
        <marker id="{ids['link']}" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill="{LINK}"/>
        </marker>
      </defs>"""


def wrap(
    slug: str,
    eyebrow: str,
    title: str,
    desc: str,
    height: int,
    body: str,
    width: int = 1200,
) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-Hans">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{escape(title)}</title>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&amp;family=Geist:wght@400;500;600&amp;family=Geist+Mono:wght@400;500;600&amp;display=swap">
  <style>{CSS}</style>
</head>
<body>
  <main class="frame">
    <p class="eyebrow">{escape(eyebrow)}</p>
    <h1>{escape(title)}</h1>
    <div class="diagram-scroll">
      <svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg"
           role="img" aria-labelledby="{slug}-title {slug}-desc">
        <title id="{slug}-title">{escape(title)}</title>
        <desc id="{slug}-desc">{escape(desc)}</desc>
{markers(slug)}
        <rect width="{width}" height="{height}" fill="{PAPER}"/>
{body}
      </svg>
    </div>
  </main>
</body>
</html>
"""


def _text_lines(
    x: int,
    y: int,
    lines: Sequence[str],
    *,
    size: int = 16,
    weight: int = 600,
    fill: str = INK,
    family: str = "'Geist', sans-serif",
    anchor: str = "middle",
    line_height: int = 20,
) -> str:
    safe = [escape(line) for line in lines if line]
    if not safe:
        return ""
    tspans = "".join(
        f'<tspan x="{x}" dy="{"0" if index == 0 else line_height}">{line}</tspan>'
        for index, line in enumerate(safe)
    )
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
        f'font-weight="{weight}" font-family="{family}" text-anchor="{anchor}">{tspans}</text>'
    )


def validate_node_layout(
    w: int,
    h: int,
    tag_w: int,
    names: Sequence[str],
    subs: Sequence[str],
) -> tuple[int, int]:
    """Return baselines and reject approximate node text-box overflows."""
    def text_width(text: str, size: int, *, mono: bool = False) -> float:
        width = 0.0
        for char in text:
            if east_asian_width(char) in {"W", "F"}:
                width += size
            elif char.isspace():
                width += size * 0.35
            else:
                width += size * (0.60 if mono else 0.52)
        return width

    tag_box = (12, 8, 12 + tag_w, 20)
    if tag_box[2] > w - 8:
        raise ValueError(f"tag exceeds horizontal bounds in {w}x{h} node")
    content_top = 24 if h < 72 else 28
    content_bottom = h - 8
    block_h = len(names) * 20 + len(subs) * 16
    available = content_bottom - content_top
    if block_h > available:
        raise ValueError(
            f"node height {h}px cannot fit {len(names)} title and {len(subs)} subtitle lines"
        )
    block_top = content_top + ((available - block_h) // 8) * 4
    title_y = block_top + 16
    sub_y = title_y + len(names) * 20

    title_boxes = []
    for index, line in enumerate(names):
        baseline = title_y + index * 20
        approx_w = max(16, text_width(line, 16))
        title_boxes.append(((w - approx_w) / 2, baseline - 16, (w + approx_w) / 2, baseline + 4))
    for line, (left, top, right, bottom) in zip(names, title_boxes):
        if left < 8 or right > w - 8 or top < 4 or bottom > h - 4:
            raise ValueError(f"title exceeds {w}x{h} node: {line!r}")
    if any(
        left < tag_box[2]
        and right > tag_box[0]
        and top < tag_box[3]
        and bottom > tag_box[1]
        for left, top, right, bottom in title_boxes
    ):
        raise ValueError(f"tag/title overlap in {w}x{h} node: {names!r}")

    if subs:
        title_bottom = title_boxes[-1][3]
        first_sub_top = sub_y - 12
        if first_sub_top - title_bottom < 4:
            raise ValueError(f"title/subtitle gap below 4px in {w}x{h} node")
        last_sub_bottom = sub_y + (len(subs) - 1) * 16 + 4
        if last_sub_bottom > h - 4:
            raise ValueError(f"subtitle exceeds {w}x{h} node")
        subtitle_boxes = []
        for index, line in enumerate(subs):
            baseline = sub_y + index * 16
            approx_w = max(12, text_width(line, 12, mono=True))
            subtitle_boxes.append(
                ((w - approx_w) / 2, baseline - 12, (w + approx_w) / 2, baseline + 4)
            )
        for line, (left, top, right, bottom) in zip(subs, subtitle_boxes):
            if left < 8 or right > w - 8 or top < 4 or bottom > h - 4:
                raise ValueError(f"subtitle exceeds {w}x{h} node: {line!r}")
    return title_y, sub_y


def node(
    x: int,
    y: int,
    w: int,
    h: int,
    tag: str,
    name: str | Sequence[str],
    sub: str | Sequence[str] = "",
    *,
    kind: str = "default",
) -> str:
    _grid(x, y, w, h)
    styles = {
        "default": (WHITE, INK, INK),
        "focal": (ACCENT_TINT, ACCENT, ACCENT),
        "store": ("rgba(45,49,66,0.05)", MUTED, MUTED),
        "external": ("rgba(79,93,117,0.08)", SOFT, MUTED),
        "optional": ("rgba(45,49,66,0.02)", "rgba(45,49,66,0.30)", SOFT),
        "dark": (INK, INK, PAPER),
        "security": ("rgba(235,108,54,0.05)", "rgba(235,108,54,0.55)", ACCENT),
    }
    fill, stroke, tag_color = styles[kind]
    dash = ' stroke-dasharray="4,4"' if kind in {"optional", "security"} else ""
    names = [name] if isinstance(name, str) else list(name)
    subs = [sub] if isinstance(sub, str) else list(sub)
    subs = [line for line in subs if line]
    cx = round((x + w / 2) / 4) * 4
    tag_w = max(40, ((len(tag) + 1) // 2) * 16)
    name_offset, sub_offset = validate_node_layout(w, h, tag_w, names, subs)
    name_y = y + name_offset
    sub_y = y + sub_offset
    text_fill = PAPER if kind == "dark" else INK
    sub_fill = "rgba(245,245,245,0.74)" if kind == "dark" else MUTED
    return f"""
        <g>
          <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{PAPER}"/>
          <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}"
                stroke="{stroke}" stroke-width="1.2"{dash}/>
          <rect x="{x+12}" y="{y+8}" width="{tag_w}" height="12" rx="4"
                fill="transparent" stroke="{tag_color}" stroke-opacity=".48" stroke-width=".8"/>
          <text x="{x+12+tag_w//2}" y="{y+16}" fill="{tag_color}" font-size="8"
                font-weight="600" font-family="'Geist Mono',monospace"
                text-anchor="middle" letter-spacing=".08em">{escape(tag.upper())}</text>
          {_text_lines(cx, name_y, names, size=16, weight=600, fill=text_fill)}
          {_text_lines(cx, sub_y, subs, size=12, weight=400, fill=sub_fill, family="'Geist Mono',monospace", line_height=16)}
        </g>"""


def zone(x: int, y: int, w: int, h: int, label: str, *, security: bool = False) -> str:
    _grid(x, y, w, h)
    stroke = "rgba(235,108,54,0.50)" if security else RULE
    fill = "rgba(235,108,54,0.025)" if security else WASH
    label_w = max(96, ((len(label) + 1) // 2) * 16)
    return f"""
        <g>
          <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}"
                stroke="{stroke}" stroke-width=".8"{' stroke-dasharray="4,4"' if security else ''}/>
          <rect x="{x+16}" y="{y+8}" width="{label_w}" height="20" rx="4" fill="{PAPER}"/>
          <text x="{x+16+label_w//2}" y="{y+24}" fill="{ACCENT if security else MUTED}"
                font-size="12" font-weight="500" font-family="'Geist Mono',monospace"
                text-anchor="middle" letter-spacing=".10em">{escape(label.upper())}</text>
        </g>"""


def stage_header(x: int, y: int, number: str, title: str, *, focal: bool = False) -> str:
    _grid(x, y)
    color = ACCENT if focal else MUTED
    fill = "rgba(235,108,54,0.14)" if focal else "rgba(45,49,66,0.08)"
    return f"""
        <g>
          <rect x="{x}" y="{y}" width="32" height="24" rx="8" fill="{fill}"/>
          <text x="{x+16}" y="{y+16}" fill="{color}" font-size="12" font-weight="600"
                font-family="'Geist Mono',monospace" text-anchor="middle">{escape(number)}</text>
          <text x="{x+44}" y="{y+20}" fill="{color}" font-size="16" font-weight="600"
                font-family="'Geist',sans-serif">{escape(title)}</text>
        </g>"""


def layer_band(
    x: int,
    y: int,
    w: int,
    h: int,
    index: str,
    name: str,
    sub: str,
    *,
    focal: bool = False,
) -> str:
    _grid(x, y, w, h)
    fill = ACCENT_TINT if focal else (WHITE if (y // h) % 2 else "rgba(45,49,66,0.025)")
    stroke = ACCENT if focal else RULE
    return f"""
        <g>
          <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}"
                stroke="{stroke}" stroke-width="{1.2 if focal else 1}"/>
          <text x="{x+20}" y="{round((y+h/2+4)/4)*4}" fill="{ACCENT if focal else MUTED}"
                font-size="12" font-weight="600" font-family="'Geist Mono',monospace">{escape(index)}</text>
          <text x="{x+116}" y="{round((y+h/2+4)/4)*4}" fill="{INK}" font-size="16" font-weight="600"
                font-family="'Geist',sans-serif">{escape(name)}</text>
          <text x="{x+w-20}" y="{round((y+h/2+4)/4)*4}" fill="{MUTED}" font-size="12"
                font-family="'Geist Mono',monospace" text-anchor="end">{escape(sub)}</text>
        </g>"""


def diamond(cx: int, cy: int, w: int, h: int, text: str, *, focal: bool = False) -> str:
    _grid(cx, cy, w, h)
    points = f"{cx},{cy-h//2} {cx+w//2},{cy} {cx},{cy+h//2} {cx-w//2},{cy}"
    return f"""
        <g>
          <polygon points="{points}" fill="{ACCENT_TINT if focal else WHITE}"
                   stroke="{ACCENT if focal else INK}" stroke-width="1.2"/>
          <text x="{cx}" y="{cy+4}" fill="{INK}" font-size="16" font-weight="600"
                font-family="'Geist',sans-serif" text-anchor="middle">{escape(text)}</text>
        </g>"""


def _connector_style(slug: str, style: str) -> tuple[str, str, str]:
    ids = marker_ids(slug)
    if style == "accent":
        return ACCENT, f"url(#{ids['accent']})", "1.6"
    if style == "link":
        return LINK, f"url(#{ids['link']})", "1.4"
    return MUTED, f"url(#{ids['default']})", "1.4"


def connector(
    slug: str,
    points: Sequence[tuple[int, int]],
    *,
    style: str = "default",
    dashed: bool = False,
    radius: int = 8,
    arrow: bool = True,
) -> str:
    if len(points) < 2:
        raise ValueError("connector needs at least two points")
    for point in points:
        _grid(*point)
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        if x1 != x2 and y1 != y2:
            raise ValueError(f"non-orthogonal segment: {(x1, y1)} -> {(x2, y2)}")
    stroke, marker, width = _connector_style(slug, style)
    if len(points) == 2:
        (x1, y1), (x2, y2) = points
        d = f"M {x1},{y1} L {x2},{y2}"
    else:
        d = f"M {points[0][0]},{points[0][1]}"
        for index in range(1, len(points) - 1):
            px, py = points[index - 1]
            cx, cy = points[index]
            nx, ny = points[index + 1]
            in_len = abs(cx - px) + abs(cy - py)
            out_len = abs(nx - cx) + abs(ny - cy)
            r = min(radius, in_len // 2, out_len // 2)
            bx = cx - (r if cx > px else -r if cx < px else 0)
            by = cy - (r if cy > py else -r if cy < py else 0)
            ax = cx + (r if nx > cx else -r if nx < cx else 0)
            ay = cy + (r if ny > cy else -r if ny < cy else 0)
            d += f" L {bx},{by} Q {cx},{cy} {ax},{ay}"
        d += f" L {points[-1][0]},{points[-1][1]}"
    dash = ' stroke-dasharray="6,4"' if dashed else ""
    end = f' marker-end="{marker}"' if arrow else ""
    return (
        f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{width}"'
        f' stroke-linecap="round" stroke-linejoin="round"{dash}{end}/>'
    )


def arrow_label(x: int, y: int, text: str, *, anchor: str = "middle") -> str:
    _grid(x, y)
    width = max(48, ((len(text) + 1) // 2) * 16)
    if anchor == "middle":
        rect_x, text_x = x - width // 2, x
    elif anchor == "start":
        rect_x, text_x = x, x + 8
    elif anchor == "end":
        rect_x, text_x = x - width, x - 8
    else:
        raise ValueError(f"unsupported text anchor: {anchor}")
    return f"""
        <g>
          <rect x="{rect_x}" y="{y-16}" width="{width}" height="16" rx="4" fill="{PAPER}"/>
          <text x="{text_x}" y="{y-4}" fill="{MUTED}" font-size="12"
                font-family="'Geist Mono',monospace" text-anchor="{anchor}"
                letter-spacing=".04em">{escape(text.upper())}</text>
        </g>"""


def bus(x1: int, x2: int, y: int) -> str:
    _grid(x1, x2, y)
    return f'<path d="M {x1},{y} H {x2}" fill="none" stroke="{MUTED}" stroke-width="1.4"/>'


def caption(x: int, y: int, text: str, *, accent: bool = False, anchor: str = "start") -> str:
    _grid(x, y)
    return (
        f'<text x="{x}" y="{y}" fill="{ACCENT if accent else MUTED}" font-size="12" '
        f'font-family="\'Geist Mono\',monospace" text-anchor="{anchor}" '
        f'letter-spacing=".06em">{escape(text.upper())}</text>'
    )


def stack(parts: Iterable[str]) -> str:
    return "\n".join(part for part in parts if part)
