"""Home page in the naqaa-cleaning.com (Riyadh) layout, re-coloured light, with UAE content.

Sources (all in templates/home/):
  styles.<lang>.html   the Riyadh home styles, copied as-is
  light.css            UAE light palette layered on top of those styles
  intro.html           opening animation
  body.<lang>.html     header, sections, footer and contact bar ({{TOKENS}} filled below)
  scripts.<lang>.html  the Riyadh home scripts (null-safe for the sections we don't use)
  icons.json           shared inline SVG icons
"""
import json
from html import escape
from pathlib import Path
from urllib.parse import quote

from tools import config as C
from tools.layout import seo_head, tel_number, wa_number

T = Path(__file__).resolve().parent.parent / "templates" / "home"

STRIPS = {
    "ar": [["نظافة", "ثقة", "دبي", "أبوظبي", "الشارقة", "عجمان"],
           ["فلل", "شقق", "كنب", "سجاد", "خزانات", "مكاتب"],
           ["المعدات علينا", "سعر بالدرهم", "قائمة مهام", "جولة مراجعة"]],
    "en": [["Clean", "Trusted", "Dubai", "Abu Dhabi", "Sharjah", "Ajman"],
           ["Villas", "Apartments", "Sofas", "Carpets", "Water tanks", "Offices"],
           ["Equipment included", "Price in AED", "Service checklist", "Final walkthrough"]],
}
WA_MSG = {"ar": "السلام عليكم، أريد الاستفسار عن خدمات التنظيف في الإمارات",
          "en": "Hello, I'd like to ask about your cleaning services in the UAE"}


def _read(name):
    return (T / name).read_text(encoding="utf-8")


def _strip(words):
    one = "".join(f"<span>{escape(w)}</span><span>✦</span>" for w in words)
    return one * 4  # the scroller moves by a quarter of the track


def _faq(items):
    return "\n".join(f'      <details class="rv-in"><summary>{escape(q)}<i></i></summary><div class="ans">{escape(a)}</div></details>'
                     for q, a in items)


def _tel_display():
    n = C.PHONE or C.WHATSAPP
    if not n:
        return "+971 XX XXX XXXX"
    return "+" + n[:3] + " " + n[3:5] + " " + n[5:8] + " " + n[8:]


def render(lang, title, description, schema, faqs):
    icons = json.loads(_read("icons.json"))
    licence = ""
    if C.TRADE_LICENCE:
        licence = (" · رقم الرخصة التجارية " if lang == "ar" else " · Trade licence no. ") + escape(C.TRADE_LICENCE)
    tokens = {
        "WA": wa_number(), "TEL": tel_number(), "TEL_DISPLAY": _tel_display(),
        "WA_MSG": quote(WA_MSG[lang]), "LICENCE": licence, "FAQ": _faq(faqs),
        "STRIP1": _strip(STRIPS[lang][0]), "STRIP2": _strip(STRIPS[lang][1]), "STRIP3": _strip(STRIPS[lang][2]),
        **icons,
    }
    body = _read(f"body.{lang}.html")
    scripts = _read(f"scripts.{lang}.html")
    for k, v in tokens.items():
        body = body.replace("{{" + k + "}}", v)
        scripts = scripts.replace("{{" + k + "}}", v)
    assert "{{" not in body and "{{" not in scripts, "unfilled token in home template"
    dir_ = "rtl" if lang == "ar" else "ltr"
    return f'''<!doctype html>
<html lang="{lang}" dir="{dir_}">
<head>
{seo_head(lang, "", title, description, schema)}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" href="/images/hero/hero-sofa.webp" as="image" type="image/webp" fetchpriority="high">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cairo:wght@300..900&display=swap">
{_read(f"styles.{lang}.html")}<style id="uae-light">
{_read("light.css")}</style>
</head>
<body>
{_read("intro.html")}{body}
{scripts}</body>
</html>
'''
