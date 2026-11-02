#!/usr/bin/env python3
"""Draws the README's SVGs: GitHub strips scripts and CSS from a README, but an SVG in <img> keeps its animations.

Text becomes outlines, so the look doesn't depend on the viewer's fonts. Needs fontTools; run with the folder
holding Inter, Manrope and JetBrains Mono TTFs:
    python3 assets/make.py <fonts dir>
"""
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
FONTS = Path(sys.argv[1])
INK, MIST, FOG, FROST = "#ffffff", "#c7d3ea", "#9da7ba", "#d1e4fa"
VIOLET, TEAL, CANVAS, CARD = "#663af3", "#269684", "#05060f", "#0a0d1b"
EDGE, LINE = "#222938", "#34405a"
_fonts = {}


def font(name):
    if name not in _fonts:
        f = TTFont(FONTS / f"{name}.ttf")
        _fonts[name] = (f.getGlyphSet(), f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm)
    return _fonts[name]


def width(s, size, name, ls=0.0):
    _, cmap, hmtx, em = font(name)
    return sum(hmtx[cmap.get(ord(c), ".notdef")][0] * size / em + ls for c in s) - ls


def text(s, x, y, size, name="Inter-Regular", fill=FOG, anchor="start", ls=0.0):
    gs, cmap, hmtx, em = font(name)
    if anchor != "start":
        x -= width(s, size, name, ls) * (0.5 if anchor == "middle" else 1)
    k, d = size / em, ""
    for c in s:
        g = cmap.get(ord(c), ".notdef")
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        gs[g].draw(TransformPen(pen, (k, 0, 0, -k, x, y)))
        d += pen.getCommands()
        x += hmtx[g][0] * k + ls
    return f'<path d="{d}" fill="{fill}"/>'


def icon(x, y, s):
    k = s / 100
    return (f'<g transform="translate({x} {y}) scale({k})"><rect x="3" y="3" width="94" height="94" rx="24" fill="#0b0b0b" '
            'stroke="#2c2c2c" stroke-width="3"/><rect x="31" y="14" width="38" height="72" rx="9" fill="none" stroke="#eee" '
            'stroke-width="4"/><circle cx="50" cy="23" r="2.6" fill="#eee"/><rect x="43" y="74" width="14" height="3.6" '
            'rx="1.8" fill="#eee"/></g>')


def arrow(x, y, stroke=FROST, cls=""):
    return (f'<path class="{cls}" d="M{x} {y}h18m-6-6l6 6-6 6" fill="none" stroke="{stroke}" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round"/>')


def svg(w, h, alt, style, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="{alt}"><title>{alt}</title><style>{style}'
            '@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>'
            '<defs><linearGradient id="ice" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d8ecf8"/>'
            f'<stop offset="1" stop-color="#98c0ef"/></linearGradient>{defs}</defs>{body}</svg>\n')


def save(name, content):
    (HERE / name).write_text(content, encoding="utf-8")
    print(name, f"{len(content) // 1024} KiB")


BACKDROP = ('<radialGradient id="v" cx=".8" cy="0" r=".75"><stop offset="0" stop-color="#663af3" stop-opacity=".30"/>'
            '<stop offset="1" stop-color="#663af3" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="t" cx="0" cy="1" r=".65"><stop offset="0" stop-color="#269684" stop-opacity=".20"/>'
            '<stop offset="1" stop-color="#269684" stop-opacity="0"/></radialGradient>')

TEXT = {
    "en": {
        "alt": "SeamDroid: your Android phone on a Linux or Windows computer",
        "title": "SeamDroid — settings", "lead": "Your Android phone on your computer",
        "side": ["Screen", "Notifications", "Clipboard", "Webcam"],
        "s1": ("Phone screen in a window", "Mouse, keyboard, wheel scrolling"), "s2": ("Messages", "Are you coming today?", "Reply"),
        "s3": ("One clipboard", "Phone", "Computer"), "s4": ("Phone camera as a webcam", "Zoom, Telegram, Discord, OBS"),
    },
    "ru": {
        "alt": "SeamDroid: Android-смартфон на компьютере с Linux или Windows",
        "title": "SeamDroid — настройки", "lead": "Android-смартфон на вашем компьютере",
        "side": ["Экран", "Уведомления", "Буфер обмена", "Веб-камера"],
        "s1": ("Экран телефона в окне", "Мышь, клавиатура, листание колесом"), "s2": ("Сообщения", "Ты сегодня придёшь?", "Ответить"),
        "s3": ("Общий буфер обмена", "Телефон", "Компьютер"), "s4": ("Камера телефона как веб-камера", "Zoom, Telegram, Discord, OBS"),
    },
}


def hero(lang):
    t = TEXT[lang]
    W, H, SIDE, X, Y, CYCLE = 860, 370, 190, 226, 214, 16
    pct = lambda i: i * 25
    pills = "".join(f"{pct(i)}%,{pct(i) + 22}%{{transform:translateY({i * 42}px)}}" for i in range(4)) + "100%{transform:none}"
    # Slide i is on screen for a quarter of the loop.
    slides = "".join(f".s{i}{{animation:sl {CYCLE}s infinite both;animation-delay:{i * CYCLE / 4}s}}" for i in range(1, 4))
    side = "".join(text(n, 34, 96 + i * 42, 14, "Inter-Regular", MIST) for i, n in enumerate(t["side"]))
    BW, BH = W - X - 36, 112
    style = (f".pill{{animation:pill {CYCLE}s ease-in-out infinite}}@keyframes pill{{{pills}}}"
             f"{slides}.s0{{animation:sl {CYCLE}s infinite backwards}}"
             "@keyframes sl{0%{opacity:0;transform:translateY(8px)}2%,23%{opacity:1;transform:none}25%,100%{opacity:0;transform:translateY(-6px)}}"
             ".cur{animation:cur 4s ease-in-out infinite}@keyframes cur{0%,100%{transform:translate(0,0)}35%{transform:translate(26px,16px)}70%{transform:translate(8px,34px)}}"
             ".dot{animation:dot 1.8s ease-in-out infinite}@keyframes dot{50%{opacity:.2}}"
             f".fly{{animation:fly 1.8s ease-in-out infinite}}@keyframes fly{{0%{{transform:translateX(0);opacity:0}}15%,85%{{opacity:1}}100%{{transform:translateX(116px);opacity:0}}}}")
    x, y = X + 22, Y + 22
    s0 = (f'<g class="s0"><rect x="{x}" y="{y - 8}" width="42" height="84" rx="8" fill="#141927" stroke="{MIST}" stroke-width="1.6"/>'
          f'<rect x="{x + 6}" y="{y + 4}" width="30" height="8" rx="3" fill="{VIOLET}"/><rect x="{x + 6}" y="{y + 16}" width="30" height="4" rx="2" fill="{LINE}"/>'
          f'<rect x="{x + 6}" y="{y + 24}" width="22" height="4" rx="2" fill="{LINE}"/>'
          f'<path class="cur" d="M{x + 12} {y + 18}l0 15 4-4 3 7 3-1-3-7h6z" fill="{INK}" stroke="#05060f"/>'
          f'{text(t["s1"][0], x + 66, y + 28, 17, "Manrope-Medium", INK)}{text(t["s1"][1], x + 66, y + 52, 13.5, "Inter-Regular", FOG)}</g>')
    rw = width(t["s2"][2], 13, "Inter-Medium") + 28
    s1 = (f'<g class="s1">{icon(x, y + 4, 54)}{text(t["s2"][0], x + 70, y + 20, 14, "Inter-SemiBold", INK)}'
          f'{text(t["s2"][1], x + 70, y + 44, 14, "Inter-Regular", MIST)}<rect x="{X + BW - 22 - rw}" y="{y + 12}" width="{rw:.0f}" height="34" rx="17" fill="{VIOLET}"/>'
          f'{text(t["s2"][2], X + BW - 22 - rw / 2, y + 34, 13, "Inter-Medium", INK, "middle")}</g>')
    px = x + 150
    s2 = (f'<g class="s2">{text(t["s3"][0], x, y + 24, 17, "Manrope-Medium", INK)}'
          f'{text(t["s3"][1], x, y + 56, 13.5, "Inter-Medium", FROST)}<path d="M{px} {y + 51.5}h124" stroke="{LINE}" stroke-dasharray="3 5"/>'
          f'<circle class="fly" cx="{px + 4}" cy="{y + 51.5}" r="5" fill="#98c0ef"/>{text(t["s3"][2], px + 136, y + 56, 13.5, "Inter-Medium", FROST)}</g>')
    s3 = (f'<g class="s3"><rect x="{x}" y="{y + 2}" width="88" height="62" rx="9" fill="#141927" stroke="{MIST}" stroke-width="1.6"/>'
          f'<circle cx="{x + 44}" cy="{y + 33}" r="15" fill="none" stroke="{MIST}" stroke-width="1.6"/><circle cx="{x + 44}" cy="{y + 33}" r="6" fill="{MIST}"/>'
          f'<circle class="dot" cx="{x + 14}" cy="{y + 14}" r="4" fill="#ef5a6a"/>{text(t["s4"][0], x + 110, y + 28, 17, "Manrope-Medium", INK)}'
          f'{text(t["s4"][1], x + 110, y + 52, 13.5, "Inter-Regular", FOG)}</g>')
    body = f'''<clipPath id="w"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16"/></clipPath>
<g clip-path="url(#w)"><rect width="{W}" height="{H}" fill="{CANVAS}"/><rect width="{W}" height="{H}" fill="url(#v)"/><rect width="{W}" height="{H}" fill="url(#t)"/>
<path d="M0 50.5H{W}M{SIDE}.5 50V{H}" stroke="{EDGE}"/>
{text(t["title"], W / 2, 31, 14, "Inter-Medium", MIST, "middle")}
<circle cx="{W - 28}" cy="26" r="11" fill="#1a1f2d"/><path d="M{W - 32} 22l8 8m0-8l-8 8" stroke="{INK}" stroke-width="1.8" stroke-linecap="round"/>
<rect class="pill" x="12" y="74" width="{SIDE - 24}" height="36" rx="9" fill="#141927"/>{side}
{icon(18, H - 42, 22)}{text("SeamDroid", 48, H - 25, 14, "Manrope-Medium", FROST)}
{text("ANDROID · LINUX · WINDOWS", X, 88, 12, "JetBrainsMono-Regular", FOG, ls=2)}
{text("SeamDroid", X - 2, 152, 62, "Manrope-Medium", "url(#ice)", ls=-2)}
{text(t["lead"], X, 186, 19, "Manrope-Medium", INK)}
<rect x="{X}" y="{Y}" width="{BW}" height="{BH + 18}" rx="14" fill="{CARD}" fill-opacity=".88" stroke="{EDGE}"/>
{s0}{s1}{s2}{s3}</g><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="none" stroke="{TEAL}" stroke-width="1.5"/>'''
    save(f"hero-{lang}.svg", svg(W, H, t["alt"], style, body, BACKDROP))


def primary(lang):
    label = {"en": "Get SeamDroid", "ru": "Скачать SeamDroid"}[lang]
    w = round(width(label, 16, "Inter-Medium")) + 84
    h = 48
    defs = ('<linearGradient id="s" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" '
            f'stop-opacity=".28"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient><clipPath id="c"><rect width="{w}" height="{h}" rx="{h / 2}"/></clipPath>')
    style = (f".sh{{animation:sh 4s ease-in-out infinite}}@keyframes sh{{0%,55%{{transform:translateX(0)}}100%{{transform:translateX({w + 70}px)}}}}"
             ".ar{animation:ar 1.6s ease-in-out infinite}@keyframes ar{50%{transform:translateX(4px)}}")
    body = (f'<rect width="{w}" height="{h}" rx="{h / 2}" fill="{VIOLET}"/><g clip-path="url(#c)"><rect class="sh" x="-60" width="60" height="{h}" fill="url(#s)"/></g>'
            f'{text(label, 28, 30, 16, "Inter-Medium", INK)}{arrow(w - 46, 24, INK, "ar")}')
    save(f"get-{lang}.svg", svg(w, h, label, style, body, defs))


def package(file, name, kind):
    w, h = 196, 62
    body = (f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="13" fill="#0d1120" stroke="{LINE}"/>'
            f'{text(name, 16, 27, 14.5, "Inter-SemiBold", FROST)}{text(kind, 16, 46, 11.5, "JetBrainsMono-Regular", FOG)}'
            f'<path d="M{w - 30} 22v14m-6-6l6 6 6-6M{w - 38} 42h16" fill="none" stroke="#98c0ef" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
    save(file, svg(w, h, f"{name}: {kind}", "", body))


for lang in TEXT:
    hero(lang)
    primary(lang)
package("dl-arch.svg", "Arch Linux", ".pkg.tar.zst")
package("dl-fedora.svg", "Fedora", ".rpm")
package("dl-windows.svg", "Windows 10/11", "setup.exe")
package("dl-android.svg", "Android 11+", ".apk")
