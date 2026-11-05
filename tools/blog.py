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
from tools.layout import (UI, abs_url, breadcrumb_schema, business_ref, crumbs_html, final_cta, page, quote_form, url)

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
    faqs = []
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

        # index + pagination
        pages = [items[i:i + PER_PAGE] for i in range(0, len(items), PER_PAGE)]
        counts = {k: sum(1 for a in items if a["section"] == k) for k in SECTIONS}
        chips = (f'<a class="post-chip on" href="{url(lang, "blog/")}">{t["all"]} <b>{len(items)}</b></a>' +
                 "".join(f'<a class="post-chip" href="{url(lang, "blog/category/" + k + "/")}">{escape(v[lang])} <b>{counts[k]}</b></a>'
                         for k, v in SECTIONS.items() if counts[k]))

        def listing(path, h1, lead, trail, group, title, desc, current_chip=None):
            ch = chips if current_chip is None else chips.replace(' on"', '"').replace(f'href="{url(lang, current_chip)}"', f'href="{url(lang, current_chip)}" aria-current="page"')
            grid = '<div class="post-grid">' + "".join(card(a, t) for a in group) + "</div>"
            return (f'<section class="hero hero-inner"><div class="wrap">{crumbs_html(lang, trail)}<p class="eyebrow">{t["blog"]}</p>'
                    f'<h1>{escape(h1)}</h1><p class="lead">{escape(lead)}</p></div></section>'
                    f'<section class="band"><div class="wrap"><nav class="post-chips" aria-label="{t["blog"]}">{ch}</nav>{grid}{{PAGER}}</div></section>'
                    + final_cta(lang))

        for i, group in enumerate(pages):
            path = "blog/" if i == 0 else f"blog/page/{i + 1}/"
            trail = trail_home + [(t["blog"], "blog/")] + ([(f'{t["page"]} {i + 1}', path)] if i else [])
            pager = ""
            if len(pages) > 1:
                prev = (f'<a href="{url(lang, "blog/" if i == 1 else f"blog/page/{i}/")}">{t["prev"]}</a>' if i else "<span></span>")
                nxt = (f'<a href="{url(lang, f"blog/page/{i + 2}/")}">{t["next"]}</a>' if i + 1 < len(pages) else "<span></span>")
                pager = f'<nav class="pager" aria-label="{t["page"]}">{prev}<span>{t["page"]} {i + 1} / {len(pages)}</span>{nxt}</nav>'
            title = t["title"] if i == 0 else f'{t["title"]} ({t["page"]} {i + 1})'
            body = listing(path, t["h1"], t["lead"], trail, group, title, t["desc"]).replace("{PAGER}", pager)
            schema = [breadcrumb_schema(lang, trail), {"@type": "Blog", "name": t["h1"], "url": abs_url(lang, path), "publisher": business_ref()}]
            alt = path if other_has_blog and i == 0 else ("blog/" if other_has_blog else "")
            emit(lang, path, page(lang, path, title, t["desc"], body, services, locations, schema, current="blog/",
                                  has_alt=(other_has_blog and i == 0), alt_path=alt, noindex=i > 0))
            paths[lang].add(path)

        # section pages
        for k, v in SECTIONS.items():
            group = [a for a in items if a["section"] == k]
            if not group:
                continue
            path = f"blog/category/{k}/"
            trail = trail_home + [(t["blog"], "blog/"), (v[lang], path)]
            other_has_sec = any(a["section"] == k for a in arts[other])
            body = listing(path, v[lang], t["sec_desc"].format(v[lang]), trail, group, "", "", current_chip=path).replace("{PAGER}", "")
            emit(lang, path, page(lang, path, t["sec_title"].format(v[lang]), t["sec_desc"].format(v[lang]), body, services, locations,
                                  [breadcrumb_schema(lang, trail)], current="blog/", has_alt=other_has_sec,
                                  alt_path=path if other_has_sec else ("blog/" if other_has_blog else "")))
            paths[lang].add(path)

        # articles
        for a in items:
            copy_assets(a)
            meta, slug = a["meta"], a["slug"]
            path = f"blog/{slug}/"
            sec = SECTIONS[a["section"]]
            trail = trail_home + [(t["blog"], "blog/"), (sec[lang], f"blog/category/{a['section']}/"), (meta.get("short_title") or meta["title"], path)]
            html, toc = add_heading_ids(body_images(a["body"]))
            faqs = extract_faqs(a["body"])
            mins = reading_minutes(a["body"], lang)
            toc_html = ""
            if len(toc) >= 3:
                toc_html = (f'<details class="toc" open><summary>{t["toc"]}</summary><ol>' +
                            "".join(f'<li><a href="#{hid}">{escape(txt)}</a></li>' for hid, txt in toc) + "</ol></details>")
            cover = (f'<figure class="post-cover"><img src="{cover_src(a)}" alt="{escape(meta.get("cover_alt", ""))}" width="1200" height="675" fetchpriority="high"></figure>'
                     if a.get("cover") else "")
            same = [b for b in items if b is not a and b["section"] == a["section"]]
            rest = [b for b in items if b is not a and b["section"] != a["section"]]
            rel = (same + rest)[:3]
            rel_html = (f'<section class="post-related"><h2>{t["related"]}</h2><div class="post-grid">' +
                        "".join(card(b, t) for b in rel) + "</div></section>") if rel else ""
            updated = f' · {t["updated"]} {fmt_date(a["updated"], lang)}' if a.get("updated") else ""
            eyebrow = f'{escape(sec[lang])} · {fmt_date(a["date"], lang)}{updated} · {mins} {t["min"]}'
            svc_link = (url(lang, f'services/{sec["service"]}/'), next(s[lang]["name"] for s in services if s["slug"] == sec["service"]))
            side = (f'<div class="aside">{quote_form(lang, services, locations, preset_service=sec["service"])}'
                    f'<div class="box"><h2>{t["service_box"]}</h2><ul><li><a href="{svc_link[0]}">{escape(svc_link[1])}</a></li>'
                    + "".join(f'<li><a href="{url(lang, "blog/" + b["slug"] + "/")}">{escape(b["meta"].get("short_title") or b["meta"]["title"])}</a></li>' for b in rel[:3])
                    + "</ul></div></div>")
            body = (f'<section class="hero hero-inner"><div class="wrap">{crumbs_html(lang, trail)}<p class="eyebrow">{eyebrow}</p>'
                    f'<h1>{escape(meta["title"])}</h1><p class="lead">{escape(meta["excerpt"])}</p></div></section>'
                    f'<section class="band"><div class="wrap layout"><article class="prose post">{cover}{toc_html}{html}{rel_html}</article>{side}</div></section>'
                    + final_cta(lang))
            img = (C.SITE_URL + cover_src(a, Path(a["cover"]).suffix.lstrip(".").lower())) if a.get("cover") else C.SITE_URL + "/assets/og-default.png"
            posting = {"@type": "BlogPosting", "headline": meta["title"], "description": meta["desc"], "image": img,
                       "datePublished": a["date"], "dateModified": a.get("updated") or a["date"], "inLanguage": lang,
                       "author": {"@type": "Organization", "name": C.BRAND[lang], "url": abs_url(lang, "")},
                       "publisher": business_ref(), "mainEntityOfPage": abs_url(lang, path)}
            schema = [posting, breadcrumb_schema(lang, trail)] + ([{"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in faqs]}] if faqs else [])
            both = other in a["langs"]
            emit(lang, path, page(lang, path, meta.get("seo_title") or f'{meta["title"]} | {C.BRAND_SHORT[lang]}', meta["desc"], body,
                                  services, locations, schema, current="blog/", has_alt=both,
                                  alt_path=path if both else ("blog/" if other_has_blog else ""),
                                  og_image=img, og_type="article"))
            paths[lang].add(path)
    return paths, problems
