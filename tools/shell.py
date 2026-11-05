"""naqaa-cleaning.com header, mobile menu, footer and contact bar, filled with UAE links and data.
Used by every page except the home page (which carries the same design in templates/home/)."""
import json
from html import escape
from pathlib import Path
from urllib.parse import quote

from tools import config as C
from tools import layout

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "templates" / "article"
WA_MSG = {"ar": "السلام عليكم، أريد الاستفسار عن خدمات التنظيف في الإمارات",
          "en": "Hello, I'd like to ask about your cleaning services in the UAE"}


def icons():
    return json.loads((ROOT / "templates" / "home" / "icons.json").read_text(encoding="utf-8"))


def tel_display():
    n = C.PHONE or C.WHATSAPP
    if not n:
        return "+971 XX XXX XXXX"
    return "+" + n[:3] + " " + n[3:5] + " " + n[5:8] + " " + n[8:]


def head_assets():
    """Fonts + shared header/footer styles (put inside <head>)."""
    menu = (ROOT / "templates" / "shell" / "menu-styles.html").read_text(encoding="utf-8")
    return ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cairo:wght@300..900&display=swap">\n'
            '<link rel="stylesheet" href="/assets/nq/nq-ui.css">\n' + menu)


def _fill(text, lang, alt_url, wa_msg=None):
    blog = ""
    if layout.BLOG_LIVE[lang]:
        blog = f'<a href="{layout.url(lang, "blog/")}">{"المدونة" if lang == "ar" else "Blog"}</a>'
    licence = ""
    if C.TRADE_LICENCE:
        licence = (" · رقم الرخصة التجارية " if lang == "ar" else " · Trade licence no. ") + escape(C.TRADE_LICENCE)
    tokens = {"TEL": layout.tel_number(), "TEL_DISPLAY": tel_display(), "WA": layout.wa_number(),
              "WA_MSG": quote(wa_msg or WA_MSG[lang]), "ALT_URL": alt_url, "LICENCE": licence, "BLOG_LINK": blog, **icons()}
    for k, v in tokens.items():
        text = text.replace("{{" + k + "}}", v)
    assert "{{" not in text, "unfilled token in shell template"
    return text


def header(lang, alt_url):
    return _fill((TPL / f"header.{lang}.html").read_text(encoding="utf-8"), lang, alt_url)


def footer(lang, wa_msg=None):
    return _fill((TPL / f"footer.{lang}.html").read_text(encoding="utf-8"), lang, "", wa_msg)
