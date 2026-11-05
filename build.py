#!/usr/bin/env python3
"""Build the whole site: python3 build.py

Reads tools/config.py and content/*.py, writes every page (English at /, Arabic at /ar/),
sitemap.xml, robots.txt, site.webmanifest and the social preview image, then checks the
result (titles, descriptions, internal links, hreflang pairs). Safe to run any number of times.
Never hand-edit the generated HTML: edit the content files and run this again.
"""
import json
import re
import shutil
import sys
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from tools import config as C  # noqa: E402
from tools.layout import (UI, ICONS, aside, abs_url, breadcrumb_schema, business_schema, business_ref,  # noqa: E402
                          cards, crumbs_html, faq_block, faq_schema, final_cta, page, quote_form, url,
                          wa_number, tel_number, WA_ICON, CALL_ICON)
from content.services import SERVICES  # noqa: E402
from content.locations import LOCATIONS  # noqa: E402
from content import pages as P  # noqa: E402

LANGS = ("en", "ar")
GENERATED_DIRS = ["ar", "services", "locations", "get-a-quote", "about", "contact", "faq", "privacy", "terms"]
SVC = {s["slug"]: s for s in SERVICES}
LOC = {l["slug"]: l for l in LOCATIONS}
assert list(SVC) == C.SERVICES and list(LOC) == C.LOCATIONS, "config.SERVICES/LOCATIONS must match content order"

T = {
    "en": {"included": "What's included", "available": "Available across the UAE", "areas": "Areas we cover in {}",
           "services_in": "Cleaning services in {}", "other_services": "Other services", "other_emirates": "Other emirates",
           "how_h": "How booking works", "emirates_line": "Dubai · Abu Dhabi · Sharjah · Ajman",
           "svc_in_loc": "{} in {}", "faq_h": "Questions about {}", "not_found": "Page not found"},
    "ar": {"included": "ماذا تشمل الخدمة", "available": "متوفرة في الإمارات", "areas": "المناطق التي نغطيها في {}",
           "services_in": "خدمات التنظيف في {}", "other_services": "خدمات أخرى", "other_emirates": "إمارات أخرى",
           "how_h": "طريقة الحجز", "emirates_line": "دبي · أبوظبي · الشارقة · عجمان",
           "svc_in_loc": "{} في {}", "faq_h": "أسئلة عن {}", "not_found": "الصفحة غير موجودة"},
}

PAGES = []  # (lang, path, html) collected for writing + checks


def emit(lang, path, html):
    PAGES.append((lang, path, html))


def hero_inner(lang, trail, eyebrow, h1, lead, buttons=True):
    t = UI[lang]
    btns = ""
    if buttons:
        btns = (f'<div class="btn-row"><a class="btn btn-gold" href="{url(lang, "get-a-quote/")}">{t["price"]}</a>'
                f'<a class="btn btn-ghost" href="https://wa.me/{wa_number()}" target="_blank" rel="noopener">{WA_ICON}<span>{t["wa"]}</span></a></div>')
    return (f'<section class="hero hero-inner"><div class="wrap">{crumbs_html(lang, trail)}'
            f'<p class="eyebrow">{eyebrow}</p><h1>{h1}</h1><p class="lead">{lead}</p>{btns}</div></section>')


def steps_band(lang, heading):
    h = P.HOME[lang]
    steps = "".join(f"<li><b>{escape(a)}</b><span>{escape(b)}</span></li>" for a, b in h["steps"])
    return (f'<section class="band band-deep"><div class="wrap"><div class="head"><p class="eyebrow">{h["how_eyebrow"]}</p>'
            f'<h2>{heading}</h2><p>{h["how_p"]}</p></div><ol class="steps">{steps}</ol></div></section>')


def home_trail(lang):
    return [(UI[lang]["home"], "")]


# ---------------------------------------------------------------- pages
def build_home(lang):
    h, t = P.HOME[lang], UI[lang]
    chips = "".join(f"<li>{escape(c)}</li>" for c in h["chips"])
    promise = "".join(f'<li>{ICONS[i]}<div><b>{escape(a)}</b><span>{escape(b)}</span></div></li>' for i, a, b in h["promise"])
    svc_cards = cards([(url(lang, f'services/{s["slug"]}/'), s["icon"], s[lang]["name"], s[lang]["card"], t["learn_more"]) for s in SERVICES])
    loc_cards = cards([(url(lang, f'locations/{l["slug"]}/'), "pin", l[lang]["name"], "، ".join(l[lang]["areas"][:4]) + "…" if lang == "ar" else ", ".join(l[lang]["areas"][:4]) + "…", t["price_arrow"]) for l in LOCATIONS], "four")
    body = f'''<section class="hero hero-home"><div class="wrap">
  <div><p class="eyebrow">{h["eyebrow"]}</p><h1>{h["h1"]}</h1><p class="lead">{h["lead"]}</p>
    <div class="btn-row"><a class="btn btn-gold" href="#quote">{t["price"]}</a><a class="btn btn-ghost" href="{url(lang, "services/")}">{t["see_services"]}</a></div>
    <ul class="chips">{chips}</ul></div>
  {quote_form(lang, SERVICES, LOCATIONS)}
</div></section>
<div class="promise band-surface"><ul class="wrap">{promise}</ul></div>
<section class="band"><div class="wrap"><div class="head"><p class="eyebrow">{h["svc_eyebrow"]}</p><h2>{h["svc_h"]}</h2><p>{h["svc_p"]}</p></div>{svc_cards}</div></section>
{steps_band(lang, h["how_h"])}
<section class="band"><div class="wrap"><div class="head"><p class="eyebrow">{h["loc_eyebrow"]}</p><h2>{h["loc_h"]}</h2><p>{h["loc_p"]}</p></div>{loc_cards}</div></section>
<section class="band band-surface"><div class="wrap faq-split">
  <div class="head"><p class="eyebrow">{h["why_eyebrow"]}</p><h2>{h["why_h"]}</h2></div>
  <div class="prose">{h["why_html"]}</div></div></section>
<section class="band"><div class="wrap faq-split"><div class="head"><p class="eyebrow">{t["nav_faq"]}</p><h2>{t["faq_title"]}</h2></div>{faq_block(h["faqs"])}</div></section>
{final_cta(lang)}'''
    website = {"@type": "WebSite", "@id": C.SITE_URL + "/#website", "url": abs_url(lang, ""), "name": C.BRAND[lang],
               "inLanguage": lang, "publisher": business_ref()}
    schema = [business_schema(lang, [l[lang]["name"] for l in LOCATIONS]), website, faq_schema(h["faqs"])]
    emit(lang, "", page(lang, "", h["title"], h["desc"], body, SERVICES, LOCATIONS, schema, current=""))


def build_service(lang, s):
    d, t, x = s[lang], UI[lang], T[lang]
    path = f'services/{s["slug"]}/'
    hub = P.SERVICES_HUB[lang]
    trail = home_trail(lang) + [(hub["crumb"], "services/"), (d["name"], path)]
    included = "".join(f"<li>{escape(i)}</li>" for i in d["included"])
    sections = "".join(f"<h2>{escape(h2)}</h2>{html}" for h2, html in d["body"])
    loc_links = "".join(
        f'<li><a href="{url(lang, "locations/" + l["slug"] + "/")}">{escape(x["svc_in_loc"].format(d["name"], l[lang]["name"]))}</a></li>'
        for l in LOCATIONS)
    related = [(url(lang, f'services/{o["slug"]}/'), o[lang]["name"]) for o in SERVICES if o is not s]
    body = (hero_inner(lang, trail, x["emirates_line"], escape(d["h1"]), escape(d["lead"])) +
            f'''<section class="band"><div class="wrap layout"><article class="prose">
  <h2>{x["included"]}</h2><ul class="check">{included}</ul>
  {sections}
  <h2>{x["available"]}</h2><ul>{loc_links}</ul>
  <h2>{escape(x["faq_h"].format(d["name"]))}</h2>{faq_block(d["faqs"])}
</article>
<div>{quote_form(lang, SERVICES, LOCATIONS, preset_service=s["slug"])}{aside(lang, related).replace('<aside class="aside">', '<aside class="aside" style="margin-top:16px;position:static">', 1)}</div>
</div></section>''' + steps_band(lang, x["how_h"]) + final_cta(lang))
    service = {"@type": "Service", "name": d["name"], "serviceType": SVC[s["slug"]]["en"]["name"], "description": d["desc"],
               "url": abs_url(lang, path), "provider": business_ref(),
               "areaServed": [{"@type": "City", "name": l[lang]["name"]} for l in LOCATIONS]}
    schema = [business_schema(lang, [l[lang]["name"] for l in LOCATIONS]), service, breadcrumb_schema(lang, trail), faq_schema(d["faqs"])]
    emit(lang, path, page(lang, path, d["title"], d["desc"], body, SERVICES, LOCATIONS, schema, current="services/"))


def build_location(lang, l):
    d, t, x = l[lang], UI[lang], T[lang]
    path = f'locations/{l["slug"]}/'
    hub = P.LOCATIONS_HUB[lang]
    trail = home_trail(lang) + [(hub["crumb"], "locations/"), (d["name"], path)]
    sections = "".join(f"<h2>{escape(h2)}</h2>{html}" for h2, html in d["body"])
    areas = "".join(f"<li>{escape(a)}</li>" for a in d["areas"])
    svc_cards = cards([(url(lang, f'services/{s["slug"]}/'), s["icon"], x["svc_in_loc"].format(s[lang]["name"], d["name"]), s[lang]["card"], t["learn_more"]) for s in SERVICES], "two")
    related = [(url(lang, f'locations/{o["slug"]}/'), o[lang]["h1_short"]) for o in LOCATIONS if o is not l]
    body = (hero_inner(lang, trail, escape(d["name"]), escape(d["h1"]), escape(d["lead"])) +
            f'''<section class="band"><div class="wrap layout"><article class="prose">
  {sections}
  <h2>{escape(x["areas"].format(d["name"]))}</h2><ul class="areas">{areas}</ul>
  <h2>{escape(x["services_in"].format(d["name"]))}</h2>{svc_cards}
  <h2>{escape(x["faq_h"].format(d["name"]))}</h2>{faq_block(d["faqs"])}
</article>
<div>{quote_form(lang, SERVICES, LOCATIONS, preset_location=l["slug"])}{aside(lang, related).replace('<aside class="aside">', '<aside class="aside" style="margin-top:16px;position:static">', 1)}</div>
</div></section>''' + final_cta(lang))
    biz = business_schema(lang, [d["name"]])
    biz["@id"] = abs_url(lang, path) + "#business"
    biz["parentOrganization"] = business_ref()
    schema = [biz, breadcrumb_schema(lang, trail), faq_schema(d["faqs"])]
    emit(lang, path, page(lang, path, d["title"], d["desc"], body, SERVICES, LOCATIONS, schema, current="locations/"))


def build_services_hub(lang):
    d, t = P.SERVICES_HUB[lang], UI[lang]
    path = "services/"
    trail = home_trail(lang) + [(d["crumb"], path)]
    svc_cards = cards([(url(lang, f'services/{s["slug"]}/'), s["icon"], s[lang]["name"], s[lang]["card"], t["learn_more"]) for s in SERVICES])
    rows = "".join(f'<tr><td>{escape(need)}</td><td><a href="{url(lang, "services/" + slug + "/")}">{escape(SVC[slug][lang]["name"])}</a></td></tr>' for need, slug in d["compare"])
    body = (hero_inner(lang, trail, T[lang]["emirates_line"], escape(d["h1"]), escape(d["lead"])) +
            f'''<section class="band"><div class="wrap">{svc_cards}</div></section>
<section class="band band-surface"><div class="wrap"><div class="head"><h2>{d["compare_h"]}</h2></div>
<div class="table-wrap"><table><thead><tr><th>{d["compare_cols"][0]}</th><th>{d["compare_cols"][1]}</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>''' + final_cta(lang))
    items = {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": abs_url(lang, f'services/{s["slug"]}/'), "name": s[lang]["name"]} for i, s in enumerate(SERVICES)]}
    emit(lang, path, page(lang, path, d["title"], d["desc"], body, SERVICES, LOCATIONS, [breadcrumb_schema(lang, trail), items], current=path))


def build_locations_hub(lang):
    d, t = P.LOCATIONS_HUB[lang], UI[lang]
    path = "locations/"
    trail = home_trail(lang) + [(d["crumb"], path)]
    sep = "، " if lang == "ar" else ", "
    loc_cards = cards([(url(lang, f'locations/{l["slug"]}/'), "pin", l[lang]["h1_short"], sep.join(l[lang]["areas"][:6]) + "…", t["learn_more"]) for l in LOCATIONS], "two")
    body = hero_inner(lang, trail, T[lang]["emirates_line"], escape(d["h1"]), escape(d["lead"])) + f'<section class="band"><div class="wrap">{loc_cards}</div></section>' + final_cta(lang)
    emit(lang, path, page(lang, path, d["title"], d["desc"], body, SERVICES, LOCATIONS, [breadcrumb_schema(lang, trail)], current=path))


def build_quote(lang):
    d = P.QUOTE[lang]
    path = "get-a-quote/"
    trail = home_trail(lang) + [(d["crumb"], path)]
    rows = "".join(f"<tr><td><b>{escape(a)}</b></td><td>{escape(b)}</td></tr>" for a, b in d["factors"])
    body = (hero_inner(lang, trail, T[lang]["emirates_line"], escape(d["h1"]), escape(d["lead"]), buttons=False) +
            f'''<section class="band"><div class="wrap layout form-first"><article class="prose">
  <h2>{d["factors_h"]}</h2><div class="table-wrap"><table><thead><tr><th>{d["factors_cols"][0]}</th><th>{d["factors_cols"][1]}</th></tr></thead><tbody>{rows}</tbody></table></div>
  <div class="note-box"><b>{d["photos_h"]}</b>{d["photos_p"]}</div>
</article><div class="aside">{quote_form(lang, SERVICES, LOCATIONS, heading="h2")}</div></div></section>''')
    emit(lang, path, page(lang, path, d["title"], d["desc"], body, SERVICES, LOCATIONS, [breadcrumb_schema(lang, trail)], current=path))


def build_prose_page(lang, data, path, extra_schema=(), current=None):
    d = data[lang]
    trail = home_trail(lang) + [(d["crumb"], path)]
    sections = "".join(f"<h2>{escape(h2)}</h2>{html}" for h2, html in d["body"])
    lead = d.get("lead", "")
    body = (hero_inner(lang, trail, escape(C.BRAND[lang]), escape(d["h1"]), escape(lead), buttons=bool(lead)) +
            f'<section class="band"><div class="wrap"><article class="prose">{sections}</article></div></section>' + (final_cta(lang) if lead else ""))
    emit(lang, path, page(lang, path, d["title"], d["desc"], body, SERVICES, LOCATIONS, [breadcrumb_schema(lang, trail), *extra_schema], current=current or path))


def build_contact(lang):
    d, t = P.CONTACT[lang], UI[lang]
    path = "contact/"
    trail = home_trail(lang) + [(d["crumb"], path)]
    wa = f'<a class="btn btn-wa" href="https://wa.me/{wa_number()}" target="_blank" rel="noopener">{WA_ICON}<span>{t["wa"]}</span></a>'
    phone_txt = ("+" + C.PHONE) if C.PHONE else d["tbc"]
    mail = f'<a href="mailto:{C.EMAIL}">{C.EMAIL}</a>' if C.EMAIL else d["tbc"]
    sep = "، " if lang == "ar" else ", "
    loc_cards = cards([(url(lang, f'locations/{l["slug"]}/'), "pin", l[lang]["h1_short"], sep.join(l[lang]["areas"][:4]) + "…", t["learn_more"]) for l in LOCATIONS], "four")
    body = (hero_inner(lang, trail, T[lang]["emirates_line"], escape(d["h1"]), escape(d["lead"]), buttons=False) +
            f'''<section class="band"><div class="wrap"><div class="cards">
  <div class="card"><h2 style="font-size:1.2rem">{d["wa_h"]}</h2><p>{d["wa_p"]}</p>{wa}</div>
  <div class="card"><h2 style="font-size:1.2rem">{d["call_h"]}</h2><p>{d["call_p"]}</p><p dir="ltr" style="color:var(--ink);font-weight:700;text-align:start">{phone_txt}</p><a class="btn btn-line" href="tel:+{tel_number()}">{CALL_ICON}<span>{t["call"]}</span></a></div>
  <div class="card"><h2 style="font-size:1.2rem">{d["mail_h"]}</h2><p>{d["mail_p"]}</p><p style="color:var(--ink);font-weight:700">{mail}</p></div>
</div></div></section>
<section class="band band-surface"><div class="wrap"><div class="head"><h2>{P.HOME[lang]["loc_h"]}</h2></div>{loc_cards}</div></section>''')
    schema = [breadcrumb_schema(lang, trail), business_schema(lang, [l[lang]["name"] for l in LOCATIONS])]
    emit(lang, path, page(lang, path, d["title"], d["desc"], body, SERVICES, LOCATIONS, schema, current=path))


def build_faq(lang):
    d = P.FAQ[lang]
    path = "faq/"
    trail = home_trail(lang) + [(d["crumb"], path)]
    per = "".join(
        f'<h3><a href="{url(lang, "services/" + s["slug"] + "/")}">{escape(s[lang]["name"])}</a></h3>{faq_block(s[lang]["faqs"][:2])}'
        for s in SERVICES)
    body = (hero_inner(lang, trail, T[lang]["emirates_line"], escape(d["h1"]), escape(d["lead"])) +
            f'''<section class="band"><div class="wrap"><article class="prose">
<h2>{d["general_h"]}</h2>{faq_block(d["general"])}
<h2>{d["by_service_h"]}</h2>{per}
</article></div></section>''' + final_cta(lang))
    emit(lang, path, page(lang, path, d["title"], d["desc"], body, SERVICES, LOCATIONS, [breadcrumb_schema(lang, trail), faq_schema(d["general"])], current=path))


def build_404():
    body = f'''<section class="hero hero-inner"><div class="wrap" style="padding-block:72px">
<p class="eyebrow">404</p><h1>{T["en"]["not_found"]}</h1>
<p class="lead">The page you were looking for has moved or doesn't exist. <span lang="ar" dir="rtl">الصفحة غير موجودة.</span></p>
<div class="btn-row"><a class="btn btn-gold" href="/">Home</a><a class="btn btn-ghost" href="/services/">Services</a><a class="btn btn-ghost" href="/ar/" lang="ar">الرئيسية</a></div>
</div></section>'''
    html = page("en", "", "Page not found | Naqaa Cleaning UAE", "This page doesn't exist.", body, SERVICES, LOCATIONS, (), has_alt=False, noindex=True)
    html = html.replace(f'<link rel="canonical" href="{abs_url("en", "")}">\n', "")
    (ROOT / "404.html").write_text(html, encoding="utf-8")


# ---------------------------------------------------------------- static files
def write_sitemap(paths):
    today = date.today().isoformat()
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for path in paths:
        prio = "1.0" if path == "" else ("0.9" if path.startswith(("services/", "locations/")) and path.count("/") == 2 else "0.7")
        for lang in LANGS:
            out.append(f"  <url><loc>{abs_url(lang, path)}</loc><lastmod>{today}</lastmod><priority>{prio}</priority>")
            out.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{abs_url("en", path)}"/>')
            out.append(f'    <xhtml:link rel="alternate" hreflang="ar" href="{abs_url("ar", path)}"/>')
            out.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{abs_url("en", path)}"/>')
            out.append("  </url>")
    out.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(out) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {C.SITE_URL}/sitemap.xml\n", encoding="utf-8")


def write_manifest():
    m = {"name": C.BRAND["en"] + " UAE", "short_name": C.BRAND_SHORT["en"], "start_url": "/", "display": "standalone",
         "background_color": "#0D1828", "theme_color": "#0D1828",
         "icons": [{"src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
                   {"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"}]}
    (ROOT / "site.webmanifest").write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8")


def write_images():
    """Social preview + app icons, drawn with Pillow (skipped if Pillow is missing)."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("  ! Pillow not installed: skipped og-default.png and icons (pip install pillow)")
        return
    navy, gold, cream = (13, 24, 40), (201, 168, 76), (243, 239, 228)

    def star(d, cx, cy, r, w):
        k = r * 0.25
        pts = [(cx, cy - r), (cx + k, cy - k), (cx + r, cy), (cx + k, cy + k), (cx, cy + r), (cx - k, cy + k), (cx - r, cy), (cx - k, cy - k)]
        d.line(pts + [pts[0]], fill=gold, width=w, joint="curve")
        d.ellipse((cx - r * .16, cy - r * .16, cx + r * .16, cy + r * .16), fill=gold)

    def font(size, bold=True):
        for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                  "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf", "Arial Bold.ttf"]:
            try:
                return ImageFont.truetype(f, size)
            except OSError:
                continue
        return ImageFont.load_default()

    for size, name in [(192, "icon-192.png"), (512, "icon-512.png"), (180, "apple-touch-icon.png")]:
        im = Image.new("RGB", (size, size), navy)
        star(ImageDraw.Draw(im), size / 2, size / 2, size * .36, max(3, size // 26))
        im.save(ROOT / "assets" / name)

    im = Image.new("RGB", (1200, 630), navy)
    d = ImageDraw.Draw(im)
    star(d, 170, 315, 95, 9)
    d.text((310, 205), "Naqaa Cleaning", font=font(84), fill=cream)
    d.text((314, 318), "Homes, villas and offices across the UAE", font=font(38, False), fill=(167, 177, 194))
    d.text((314, 392), "Dubai  ·  Abu Dhabi  ·  Sharjah  ·  Ajman", font=font(34), fill=gold)
    im.save(ROOT / "assets" / "og-default.png", optimize=True)


# ---------------------------------------------------------------- checks
def check():
    problems, titles = [], {}
    existing = {url(lang, path) for lang, path, _ in PAGES}
    static_ok = ("/assets/", "/favicon", "/site.webmanifest", "/sitemap.xml")
    for lang, path, html in PAGES:
        where = url(lang, path)
        title = re.search(r"<title>(.*?)</title>", html).group(1)
        desc = re.search(r'<meta name="description" content="(.*?)">', html).group(1)
        if len(title) > 70:
            problems.append(f"{where}: title is {len(title)} chars (aim for 60, max 70)")
        if not 70 <= len(desc) <= 160:
            problems.append(f"{where}: description is {len(desc)} chars (aim for 120-155)")
        if title in titles:
            problems.append(f"{where}: same title as {titles[title]}")
        titles[title] = where
        if html.count("<h1") != 1:
            problems.append(f"{where}: needs exactly one <h1>")
        if "TODO" in html:
            problems.append(f"{where}: contains TODO")
        for href in re.findall(r'href="(/[^"#?]*)', html):
            if href.startswith(static_ok) or href == "/":
                continue
            if href not in existing:
                problems.append(f"{where}: broken internal link {href}")
        for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            json.loads(m)
    return problems


def main():
    for d in GENERATED_DIRS:
        shutil.rmtree(ROOT / d, ignore_errors=True)
    for lang in LANGS:
        build_home(lang)
        build_services_hub(lang)
        for s in SERVICES:
            build_service(lang, s)
        build_locations_hub(lang)
        for l in LOCATIONS:
            build_location(lang, l)
        build_quote(lang)
        build_prose_page(lang, P.ABOUT, "about/", [business_schema(lang, [l[lang]["name"] for l in LOCATIONS])])
        build_contact(lang)
        build_faq(lang)
        build_prose_page(lang, P.PRIVACY, "privacy/")
        build_prose_page(lang, P.TERMS, "terms/")

    for lang, path, html in PAGES:
        out = ROOT / ("ar" if lang == "ar" else "") / path / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
    build_404()
    paths = sorted({p for _, p, _ in PAGES}, key=lambda p: (p.count("/"), p))
    write_sitemap(paths)
    write_manifest()
    write_images()

    print(f"✓ {len(PAGES)} pages written ({len(paths)} per language) + 404, sitemap.xml, robots.txt")
    warnings = []
    if "naqaa-uae.com" in C.SITE_URL:
        warnings.append("SITE_URL is still the placeholder domain (tools/config.py)")
    if not (C.WHATSAPP and C.PHONE):
        warnings.append("WHATSAPP / PHONE not set: contact links use a placeholder number and the preview banner is shown")
    if not C.TRADE_LICENCE:
        warnings.append("TRADE_LICENCE not set")
    if not (C.GA_ID or C.GTM_ID):
        warnings.append("No analytics IDs set")
    for w in warnings:
        print("  ! " + w)
    problems = check()
    if problems:
        print("✗ Fix these and run again:")
        for p in problems:
            print("  - " + p)
        sys.exit(1)
    print("✓ Checks passed: titles, descriptions, one h1 per page, internal links, structured data")


if __name__ == "__main__":
    main()
