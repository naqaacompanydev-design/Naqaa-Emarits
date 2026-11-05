"""Blog: /blog/ (English) and /ar/blog/ (Arabic).

Source
  content/blog/articles.json      one entry per article (newest first), see tools/new_article.py
  content/blog/<slug>/body.<lang>.html   the article content for each language it is written in
  content/blog/<slug>/*.jpg|png|webp     cover and inline images (WebP copies are made automatically)

An article is published in every language that has an entry block AND a body file, unless it is
marked "draft": true. The blog (menu link, index, sitemap) only appears once something is published.
"""
import json
import re
import shutil
from datetime import date
from html import escape, unescape
from pathlib import Path

from tools import config as C
from tools.layout import (UI, seo_head, tel_number, wa_number, abs_url, breadcrumb_schema, business_ref, crumbs_html, final_cta, page, quote_form, url)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "content" / "blog"
PER_PAGE = 12

# Sections (category pages). "service" is the related service for the booking box.
SECTIONS = {
    "homes":       {"service": "home-cleaning", "en": "Home cleaning", "ar": "تنظيف المنازل"},
    "moving":      {"service": "move-in-move-out-cleaning", "en": "Moving in & out", "ar": "الانتقال والإخلاء"},
    "water-tanks": {"service": "water-tank-cleaning", "en": "Water tanks", "ar": "خزانات المياه"},
    "upholstery":  {"service": "sofa-carpet-cleaning", "en": "Sofas & carpets", "ar": "الكنب والسجاد"},
    "offices":     {"service": "office-cleaning", "en": "Offices", "ar": "المكاتب"},
    "guides":      {"service": "deep-cleaning", "en": "Prices & guides", "ar": "الأسعار والنصائح"},
}

S = {
    "en": {"blog": "Blog", "title": "Cleaning Tips & Guides for UAE Homes | Naqaa Blog",
           "desc": "Practical cleaning guides for homes, villas and offices in Dubai, Abu Dhabi, Sharjah and Ajman, from the Naqaa cleaning team.",
           "h1": "Naqaa blog", "lead": "Practical cleaning guides for homes, villas and offices across the UAE.",
           "all": "All", "read": "Read article →", "min": "min read", "toc": "In this article",
           "related": "Related articles", "page": "Page", "prev": "← Newer", "next": "Older →",
           "sec_title": "{} Tips & Guides | Naqaa Blog", "sec_desc": "Naqaa articles about {} in the UAE: practical tips for homes, villas and offices in Dubai, Abu Dhabi, Sharjah and Ajman.",
           "updated": "Updated", "service_box": "Related service"},
    "ar": {"blog": "المدونة", "title": "نصائح وأدلة التنظيف لبيوت الإمارات | مدونة نقاء",
           "desc": "أدلة تنظيف عملية للمنازل والفلل والمكاتب في دبي وأبوظبي والشارقة وعجمان، من فريق نقاء للتنظيف.",
           "h1": "مدونة نقاء", "lead": "أدلة تنظيف عملية للمنازل والفلل والمكاتب في الإمارات.",
           "all": "الكل", "read": "اقرأ المقال ←", "min": "دقائق قراءة", "toc": "محتويات المقال",
           "related": "مقالات ذات صلة", "page": "صفحة", "prev": "→ الأحدث", "next": "الأقدم ←",
           "sec_title": "مقالات {} | مدونة نقاء", "sec_desc": "مقالات نقاء عن {} في الإمارات: نصائح عملية للمنازل والفلل والمكاتب في دبي وأبوظبي والشارقة وعجمان.",
           "updated": "آخر تحديث", "service_box": "الخدمة المرتبطة"},
}

AR_MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
EN_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def fmt_date(iso, lang):
    d = date.fromisoformat(iso)
    return f"{d.day} {(AR_MONTHS if lang == 'ar' else EN_MONTHS)[d.month - 1]} {d.year}"


def load():
    """Return {lang: [article dicts]} for published articles, newest first, plus a list of problems."""
    problems, out = [], {"en": [], "ar": []}
    path = SRC / "articles.json"
    if not path.exists():
        return out, problems
    entries = json.loads(path.read_text(encoding="utf-8"))
    seen = set()
    for e in entries:
        slug = e.get("slug", "")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
            problems.append(f"blog: bad slug '{slug}' (lowercase English words joined by -)")
            continue
        if slug in seen:
            problems.append(f"blog: duplicate slug {slug}")
        seen.add(slug)
        if e.get("draft"):
            continue
        if e.get("section") not in SECTIONS:
            problems.append(f"blog/{slug}: section must be one of {', '.join(SECTIONS)}")
            continue
        try:
            date.fromisoformat(e.get("date", ""))
        except ValueError:
            problems.append(f"blog/{slug}: date must be YYYY-MM-DD")
            continue
        langs = [l for l in ("en", "ar") if l in e and (SRC / slug / f"body.{l}.html").exists()]
        if not langs:
            problems.append(f"blog/{slug}: no body.en.html / body.ar.html found")
        for l in langs:
            meta = e[l]
            for k in ("title", "desc", "excerpt"):
                if not meta.get(k) or "TODO" in meta.get(k, ""):
                    problems.append(f"blog/{slug} ({l}): fill in {k} in articles.json")
            body = (SRC / slug / f"body.{l}.html").read_text(encoding="utf-8")
            if "TODO" in body:
                problems.append(f"blog/{slug}/body.{l}.html still contains TODO")
            if "<h1" in body:
                problems.append(f"blog/{slug}/body.{l}.html: remove the <h1> (the page adds it)")
            out[l].append({**e, "lang": l, "meta": meta, "body": body, "langs": langs})
    for l in out:
        out[l].sort(key=lambda a: a["date"], reverse=True)
    return out, problems


# ---------------------------------------------------------------- helpers
def _text(html):
    return unescape(re.sub(r"<[^>]+>", " ", html))


def reading_minutes(html, lang):
    words = len(_text(html).split())
    return max(1, round(words / (180 if lang == "ar" else 220)))


def add_heading_ids(html):
    toc, n = [], 0

    def rep(m):
        nonlocal n
        n += 1
        attrs, inner = m.group(1), m.group(2)
        if 'id="' in attrs:
            hid = re.search(r'id="([^"]+)"', attrs).group(1)
            toc.append((hid, _text(inner).strip()))
            return m.group(0)
        hid = f"part-{n}"
        toc.append((hid, _text(inner).strip()))
        return f'<h2{attrs} id="{hid}">{inner}</h2>'
    return re.sub(r"<h2([^>]*)>(.*?)</h2>", rep, html, flags=re.S), toc


def extract_faqs(html):
    faqs = [(_text(q).strip(), _text(a).strip()) for q, a in re.findall(
        r'<div class="faq-q">(.*?)</div>\s*<div class="faq-a">(.*?)</div>', html, flags=re.S)]
    for block in re.findall(r'<div class="faq">(.*?)</div>\s*(?=<|$)', html, flags=re.S):
        for q, a in re.findall(r"<summary>(.*?)</summary>\s*<p>(.*?)</p>", block, flags=re.S):
            faqs.append((_text(q).strip(), _text(a).strip()))
    return faqs


def cover_src(a, ext="webp"):
    if not a.get("cover"):
        return ""
    stem = Path(a["cover"]).stem
    return f'{url(a["lang"], "blog/" + a["slug"] + "/")}{stem}.{ext}'


def copy_assets(a):
    """Copy images next to the article page and make WebP copies of jpg/png."""
    src = SRC / a["slug"]
    dest = ROOT / ("ar" if a["lang"] == "ar" else "") / "blog" / a["slug"]
    dest.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
    except ImportError:
        Image = None
    for f in src.iterdir():
        if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"):
            shutil.copy2(f, dest / f.name)
            if Image and f.suffix.lower() in (".jpg", ".jpeg", ".png"):
                webp = dest / (f.stem + ".webp")
                if not (src / webp.name).exists():
                    Image.open(f).convert("RGB").save(webp, "WEBP", quality=82)


def body_images(html):
    """Use the WebP copy for jpg/png images and lazy-load them."""
    html = re.sub(r'(<img[^>]*src=")(?!https?:|/)([^"]+)\.(jpe?g|png)"', r'\1\2.webp"', html)
    return re.sub(r"<img(?![^>]*loading=)", '<img loading="lazy" decoding="async"', html)


def card(a, t):
    meta, lang = a["meta"], a["lang"]
    sec = SECTIONS[a["section"]][lang]
    img = (f'<img src="{cover_src(a)}" alt="{escape(meta.get("cover_alt", ""))}" loading="lazy" width="640" height="360">'
           if a.get("cover") else '<span class="post-noimg" aria-hidden="true"></span>')
    return (f'<a class="post-card" href="{url(lang, "blog/" + a["slug"] + "/")}">{img}'
            f'<span class="post-body"><span class="post-tag">{escape(sec)}</span><h3>{escape(meta["title"])}</h3>'
            f'<p>{escape(meta["excerpt"])}</p><span class="post-meta">{fmt_date(a["date"], lang)}</span></span></a>')


# ---------------------------------------------------------------- pages
def build(emit, services, locations):
    """Build every blog page. Returns {lang: set(paths)} and problems."""
    arts, problems = load()
    paths = {"en": set(), "ar": set()}
    for lang, items in arts.items():
        if not items:
            continue
        t, ui = S[lang], UI[lang]
        trail_home = [(ui["home"], "")]
        other = "ar" if lang == "en" else "en"
        other_has_blog = bool(arts[other])

        # index + pagination + sections (naqaa-cleaning.com blog index design)
        pages = [items[i:i + PER_PAGE] for i in range(0, len(items), PER_PAGE)]
        counts = {k: sum(1 for a in items if a["section"] == k) for k in SECTIONS}

        def chips(current):
            out = [(url(lang, "blog/"), t["all"], len(items), current == "blog/")]
            out += [(url(lang, f"blog/category/{k}/"), v[lang], counts[k], current == f"blog/category/{k}/") for k, v in SECTIONS.items() if counts[k]]
            return "".join(f'<a href="{h}"' + (' aria-current="page" class="on"' if on else "") + f'>{escape(x)} <small>{n}</small></a>' for h, x, n, on in out)

        for i, group in enumerate(pages):
            path = "blog/" if i == 0 else f"blog/page/{i + 1}/"
            trail = trail_home + [(t["blog"], "blog/")] + ([(f'{t["page"]} {i + 1}', path)] if i else [])
            title = t["title"] if i == 0 else f'{t["title"]} ({t["page"]} {i + 1})'
            schema = [breadcrumb_schema(lang, trail), {"@type": "Blog", "name": t["h1"], "url": abs_url(lang, path), "publisher": business_ref()}]
            both = other_has_blog and i == 0
            emit(lang, path, render_index(lang, path, title, t["desc"], schema, group, chips("blog/" if i == 0 else ""), pager_html(lang, i, len(pages)),
                                          url(other, "blog/" if other_has_blog else ""), both, noindex=i > 0))
            paths[lang].add(path)

        for k, v in SECTIONS.items():
            group = [a for a in items if a["section"] == k]
            if not group:
                continue
            path = f"blog/category/{k}/"
            trail = trail_home + [(t["blog"], "blog/"), (v[lang], path)]
            other_has_sec = any(a["section"] == k for a in arts[other])
            emit(lang, path, render_index(lang, path, t["sec_title"].format(v[lang]), t["sec_desc"].format(v[lang]), [breadcrumb_schema(lang, trail)],
                                          group, chips(path), "", url(other, path if other_has_sec else ("blog/" if other_has_blog else "")),
                                          other_has_sec, h1=v[lang]))
            paths[lang].add(path)

        # articles (naqaa-cleaning.com article design, see tools/article.py)
        for a in items:
            copy_assets(a)
            path = f"blog/{a['slug']}/"
            same = [b for b in items if b is not a and b["section"] == a["section"]]
            rest = [b for b in items if b is not a and b["section"] != a["section"]]
            emit(lang, path, render_article(a, (same + rest)[:3], other_has_blog))
            paths[lang].add(path)
    return paths, problems


# ---------------------------------------------------------------- article page (Riyadh design)
TPL = ROOT / "templates" / "article"
_SVG = 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"'
I_CAL = f'<svg {_SVG}><rect x="3" y="4.5" width="18" height="17" rx="3"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/></svg>'
I_CLOCK = f'<svg {_SVG}><circle cx="12" cy="12" r="9.5"/><path d="M12 7v5l3.5 2"/></svg>'
I_USER = f'<svg {_SVG}><circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/></svg>'

A = {
    "ar": {"home": "الرئيسية", "author": "فريق نقاء للتنظيف", "min": "دقيقة قراءة", "toc": "محتويات المقال", "parts": "قسم",
           "book_b": "تبي تعرف السعر قبل ما تحجز؟", "book_s": "اختار الخدمة واعرف سعرك بالدرهم، أو كلمنا على واتساب.",
           "price": "اعرف سعرك", "wa": "واتساب", "related": "مقالات ممكن تهمك",
           "why": "لماذا نقاء للتنظيف؟", "why_rows": ["سعر واضح بالدرهم قبل الحجز", "قائمة مهام لكل خدمة", "فريق مدرب والمعدات علينا", "دبي وأبوظبي والشارقة وعجمان"],
           "side_h": "عايز تعرف السعر قبل ما تقرر؟", "side_p": "ابعت احتياجك وصور المكان وخد عرض واضح", "side_btn": "واتساب الآن", "side_note": "🏷 رد سريع ومساعدة في اختيار الخدمة",
           "cta_h": "احجز الآن مع نقاء للتنظيف", "cta_p": "خدمات تنظيف للمنازل والفلل والمكاتب في الإمارات بسعر واضح وفريق مدرب",
           "cta_list": ["سعر واضح بالدرهم قبل البدء", "فريق حسب المساحة ومعدات احترافية", "مواد مناسبة لكل سطح", "دبي وأبوظبي والشارقة وعجمان"],
           "cta_wa": "تواصل عبر واتساب", "cta_call": "اتصل بنا مباشرة",
           "wa_msg": "السلام عليكم، قرأت مقال في مدونة نقاء وأريد الاستفسار عن خدمة تنظيف", "bc": "مسار التنقل"},
    "en": {"home": "Home", "author": "Naqaa Cleaning team", "min": "min read", "toc": "In this article", "parts": "sections",
           "book_b": "Want the price before you book?", "book_s": "Pick the service and get your price in AED, or message us on WhatsApp.",
           "price": "Get your price", "wa": "WhatsApp", "related": "You may also like",
           "why": "Why Naqaa Cleaning?", "why_rows": ["Clear price in AED before booking", "A checklist for every service", "Trained team, equipment included", "Dubai, Abu Dhabi, Sharjah, Ajman"],
           "side_h": "Want a price before you decide?", "side_p": "Send what you need and a few photos, get a clear quote", "side_btn": "WhatsApp now", "side_note": "🏷 Quick reply and help choosing the service",
           "cta_h": "Book with Naqaa Cleaning", "cta_p": "Home, villa and office cleaning across the UAE with a clear price and a trained team",
           "cta_list": ["Clear price in AED before we start", "Team sized to your space, pro equipment", "The right products for every surface", "Dubai, Abu Dhabi, Sharjah and Ajman"],
           "cta_wa": "Message us on WhatsApp", "cta_call": "Call us",
           "wa_msg": "Hello, I read an article on the Naqaa blog and would like to ask about a cleaning service", "bc": "Breadcrumb"},
}


def render_article(a, related, other_has_blog):
    from urllib.parse import quote
    from tools.home import _tel_display
    lang, meta, slug = a["lang"], a["meta"], a["slug"]
    t = A[lang]
    icons = json.loads((ROOT / "templates" / "home" / "icons.json").read_text(encoding="utf-8"))
    path = f"blog/{slug}/"
    sec = SECTIONS[a["section"]]
    wa = f"https://wa.me/{wa_number()}?text={quote(t['wa_msg'])}"
    other = "ar" if lang == "en" else "en"
    both = other in a["langs"]
    alt_url = url(other, path if both else ("blog/" if other_has_blog else ""))

    # content: heading ids, WebP images, booking boxes before the 3rd and the 2/3 heading
    html = body_images(re.sub(r"<!--.*?-->", "", a["body"], flags=re.S))
    n = 0

    def hid(m):
        nonlocal n
        n += 1
        return f'<h2{m.group(1)} id="s{n}">'
    html = re.sub(r"<h2((?:(?!id=)[^>])*)>", hid, html)
    toc = [(i, _text(x).strip()) for i, x in re.findall(r'<h2[^>]*id="(s\d+)"[^>]*>(.*?)</h2>', html, flags=re.S)]
    book = (f'<aside class="art-book" aria-label="{t["price"]}"><div class="art-book-txt"><b>{t["book_b"]}</b><span>{t["book_s"]}</span></div>'
            f'<div class="art-book-btns"><a class="bk-p" data-nq="price" href="{url(lang, "get-a-quote/")}">{icons["ICON_CALC"]}{t["price"]}</a>'
            f'<a class="bk-w" href="{wa}" target="_blank" rel="noopener">{icons["ICON_WA"]}{t["wa"]}</a></div></aside>\n')
    for k in sorted({3, max(4, round(len(toc) * 2 / 3))}, reverse=True):
        if k <= len(toc):
            html = html.replace(f'<h2 id="s{k}">', book + f'<h2 id="s{k}">', 1)
    toc_ol = "<ol>" + "".join(f'<li><a href="#{i}">{escape(x)}</a></li>' for i, x in toc) + "</ol>"
    toc_sum = f'<summary>{t["toc"]} <small>{len(toc)} {t["parts"]}</small></summary>'
    inline_toc = f'<details class="art-toc art-toc-inline">{toc_sum}{toc_ol}</details>\n'
    if '<div class="intro-box">' in html:
        end = html.index("</div>", html.index('<div class="intro-box">')) + 6
        html = html[:end] + "\n" + inline_toc + html[end:]
    else:
        html = inline_toc + html

    mins = reading_minutes(a["body"], lang)
    cover_alt = escape(meta.get("cover_alt") or meta["title"])
    cover = f'<figure class="art-cover"><img src="{cover_src(a)}" alt="{cover_alt}" fetchpriority="high" decoding="async"></figure>' if a.get("cover") else ""
    rel = ""
    if related:
        rel = (f'<section class="art-related" aria-labelledby="art-rel-h"><h2 class="art-related-h" id="art-rel-h">{t["related"]}</h2><div class="art-rel-grid">' +
               "".join(f'<a class="art-rel" href="{url(lang, "blog/" + b["slug"] + "/")}">'
                       + (f'<img src="{cover_src(b)}" alt="{escape(b["meta"].get("cover_alt") or b["meta"]["title"])}" loading="lazy" decoding="async">' if b.get("cover") else "")
                       + f'<div class="art-rel-b"><span class="art-rel-cat">{escape(SECTIONS[b["section"]][lang])}</span><h3>{escape(b["meta"]["title"])}</h3>'
                       f'<span class="art-rel-m">{I_CLOCK}{reading_minutes(b["body"], lang)} {t["min"]}</span></div></a>' for b in related) + "</div></section>")
    cta = (f'<div class="cta-section"><h2>{t["cta_h"]}</h2><p>{t["cta_p"]}</p><ul class="cta-list">' + "".join(f"<li>{x}</li>" for x in t["cta_list"]) +
           f'</ul><div class="cta-buttons"><a href="{wa}" class="btn-whatsapp" target="_blank" rel="noopener">{icons["ICON_WA"]}{t["cta_wa"]}</a>'
           f'<a href="tel:+{tel_number()}" class="btn-phone">{icons["ICON_CALL"]}{t["cta_call"]}</a></div></div>')
    side = (f'<aside class="sidebar"><div class="sidebar-inner"><details class="art-toc art-toc-side" open>{toc_sum}{toc_ol}</details>'
            f'<div class="sidebar-card"><div class="sidebar-card-head"><h4>{t["why"]}</h4></div><div class="sidebar-card-body"><div class="quick-prices">'
            + "".join(f'<div class="qp-row"><span class="qp-label">{x}</span><span class="qp-price">✔</span></div>' for x in t["why_rows"]) +
            f'</div></div></div><div class="sidebar-cta"><h4>{t["side_h"]}</h4><p>{t["side_p"]}</p><a href="{wa}" class="btn-whatsapp" target="_blank" rel="noopener">{icons["ICON_WA"]}{t["side_btn"]}</a>'
            f'<div class="sidebar-discount">{t["side_note"]}</div></div></div></aside>')
    crumbs = [(t["home"], url(lang, "")), (S[lang]["blog"], url(lang, "blog/")), (sec[lang], url(lang, f"blog/category/{a['section']}/"))]
    bc = "".join(f'<a href="{h}">{escape(x)}</a><span class="bc-sep">›</span>' for x, h in crumbs) + f'<span>{escape(meta.get("short_title") or meta["title"])}</span>'

    # SEO head + structured data
    trail = [(t["home"], ""), (S[lang]["blog"], "blog/"), (sec[lang], f"blog/category/{a['section']}/"), (meta.get("short_title") or meta["title"], path)]
    img = (C.SITE_URL + cover_src(a, Path(a["cover"]).suffix.lstrip(".").lower())) if a.get("cover") else C.SITE_URL + "/assets/og-default.png"
    faqs = extract_faqs(a["body"])
    schema = [{"@type": "BlogPosting", "headline": meta["title"], "description": meta["desc"], "image": img,
               "datePublished": a["date"], "dateModified": a.get("updated") or a["date"], "inLanguage": lang, "wordCount": len(_text(a["body"]).split()),
               "author": {"@type": "Organization", "name": C.BRAND[lang], "url": abs_url(lang, "")},
               "publisher": business_ref(), "mainEntityOfPage": abs_url(lang, path)}, breadcrumb_schema(lang, trail)]
    if faqs:
        schema.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in faqs]})
    title = meta.get("seo_title") or f'{meta["title"]} | {C.BRAND_SHORT[lang]}'
    head = seo_head(lang, path, title, meta["desc"], schema, has_alt=both, og_image=img, og_type="article")

    from tools import shell
    header = shell.header(lang, alt_url)
    footer = shell.footer(lang, t["wa_msg"])
    styles = (TPL / "styles.html").read_text(encoding="utf-8")
    dir_ = "rtl" if lang == "ar" else "ltr"
    return f'''<!doctype html>
<html lang="{lang}" dir="{dir_}">
<head>
{head}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cairo:wght@300..900&display=swap">
<link rel="stylesheet" href="/assets/nq/nq-ui.css">
{styles}<link rel="stylesheet" href="/assets/nq/nq-article.css">
<link rel="stylesheet" href="/assets/nq/uae-article.css">
<script src="/assets/nq/nq-article.js" defer></script>
</head>
<body class="nq-inner nq-art">
{header}
<header class="art-head"><div class="art-head-in">
<nav class="breadcrumb" aria-label="{t["bc"]}">{bc}</nav>
<span class="art-cat">{escape(sec[lang])}</span>
<h1>{escape(meta["title"])}</h1>
<div class="art-meta"><span>{I_CAL}{fmt_date(a["date"], lang)}</span><span>{I_CLOCK}{mins} {t["min"]}</span><span>{I_USER}{t["author"]}</span></div>
</div></header>
<div class="art-paper">
{cover}
<div class="page-wrapper">
<main class="article-body">
{html}
{cta}
{rel}
</main>
{side}
</div>
</div>
{footer}
<script src="/assets/nq/nq-ui.js" defer></script>
</body>
</html>
'''


# ---------------------------------------------------------------- blog index (Riyadh design)
_CHEV_PREV = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>'
_CHEV_NEXT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg>'
IDX = {"ar": {"h1": 'مدونة خبراء <span>نقاء</span>', "read": "اقرأ المقال", "prev": "السابقة", "next": "التالية", "of": "من", "page": "صفحة", "nav": "أقسام المدونة", "pages": "صفحات المدونة"},
       "en": {"h1": 'The <span>Naqaa</span> experts blog', "read": "Read article", "prev": "Previous", "next": "Next", "of": "of", "page": "Page", "nav": "Blog sections", "pages": "Blog pages"}}


def pager_html(lang, i, total):
    if total < 2:
        return ""
    t = IDX[lang]
    href = lambda n: url(lang, "blog/" if n == 1 else f"blog/page/{n}/")
    prev = (f'<a class="pg-prev" href="{href(i)}" rel="prev">{_CHEV_PREV}<span>{t["prev"]}</span></a>' if i
            else f'<span class="pg-prev is-off" aria-hidden="true">{_CHEV_PREV}<span>{t["prev"]}</span></span>')
    nxt = (f'<a class="pg-next" href="{href(i + 2)}" rel="next"><span>{t["next"]}</span>{_CHEV_NEXT}</a>' if i + 1 < total
           else f'<span class="pg-next is-off" aria-hidden="true"><span>{t["next"]}</span>{_CHEV_NEXT}</span>')
    nums = "".join(f'<li><span aria-current="page">{n}</span></li>' if n == i + 1 else f'<li><a href="{href(n)}" aria-label="{t["page"]} {n}">{n}</a></li>'
                   for n in range(1, total + 1))
    return (f'<div class="pager" role="navigation" aria-label="{t["pages"]}">{prev}<ol class="pg-nums">{nums}</ol>'
            f'<span class="pg-count">{t["page"]} <b>{i + 1}</b> {t["of"]} {total}</span>{nxt}</div>')


def index_card(a):
    lang, meta = a["lang"], a["meta"]
    img = (f'<div class="blog-card-img"><img src="{cover_src(a)}" alt="{escape(meta.get("cover_alt") or meta["title"])}" loading="lazy"></div>'
           if a.get("cover") else '<div class="blog-card-img"></div>')
    return (f'<a href="{url(lang, "blog/" + a["slug"] + "/")}" class="blog-card-link"><article class="blog-card">{img}'
            f'<div class="blog-card-body"><span class="blog-cat">{escape(SECTIONS[a["section"]][lang])}</span>'
            f'<h2 class="blog-card-title">{escape(meta["title"])}</h2><p class="blog-card-excerpt">{escape(meta["excerpt"])}</p>'
            f'<div class="blog-date"><span>{I_CLOCK}{reading_minutes(a["body"], lang)} {A[lang]["min"]}</span><span class="bd-more">{IDX[lang]["read"]}</span></div>'
            f'</div></article></a>')


def render_index(lang, path, title, desc, schema, group, chips_html, pager, alt_url, has_alt, noindex=False, h1=None):
    from tools import shell
    t = IDX[lang]
    h1_html = escape(h1) if h1 else t["h1"]
    head = seo_head(lang, path, title, desc, schema, has_alt=has_alt, noindex=noindex)
    styles = (ROOT / "templates" / "blogindex" / "styles.html").read_text(encoding="utf-8")
    dir_ = "rtl" if lang == "ar" else "ltr"
    grid = '<div class="blog-grid" data-card="3">' + "".join(index_card(a) for a in group) + "</div>"
    return f'''<!doctype html>
<html lang="{lang}" dir="{dir_}">
<head>
{head}
{shell.head_assets()}{styles}<link rel="stylesheet" href="/assets/nq/nq-fbar.css">
<link rel="stylesheet" href="/assets/nq/nq-blog.css">
<link rel="stylesheet" href="/assets/nq/uae-blog.css">
</head>
<body class="nq-inner nq-blogidx">
{shell.header(lang, alt_url)}
<main id="main">
<header class="bh"><div class="bh-bg" aria-hidden="true"><img src="/images/hero/naqaa-team.webp" alt="" fetchpriority="high" decoding="async"></div><div class="bh-in"><h1>{h1_html}</h1></div></header>
<section class="blog-paper">
<div class="blog-sections" role="navigation" aria-label="{t["nav"]}">{chips_html}</div>
<div class="container">{grid}</div>
{pager}
</section>
</main>
{shell.footer(lang)}
<script src="/assets/nq/nq-ui.js" defer></script>
</body>
</html>
'''
