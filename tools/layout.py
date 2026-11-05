"""Shared page shell: <head> (SEO + structured data), header, footer, contact bar and components."""
import json
import re
from html import escape

from tools import config as C

# ---------- interface strings ----------
UI = {
    "en": {
        "brand_sub": "Cleaning · UAE",
        "nav_services": "Services", "nav_locations": "Locations", "nav_about": "About",
        "nav_faq": "FAQ", "nav_contact": "Contact", "nav_blog": "Blog", "nav_quote": "Get a price",
        "menu": "Menu", "skip": "Skip to content", "home": "Home",
        "other_lang": "العربية", "other_lang_label": "اقرأ هذه الصفحة بالعربية",
        "wa": "WhatsApp", "call": "Call", "wa_cta": "Get a price on WhatsApp", "price": "Get your price",
        "draft": "Preview build · phone numbers, domain and licence details are placeholders until confirmed",
        "f_services": "Services", "f_locations": "Locations", "f_company": "Company",
        "f_about": "Naqaa brings the cleaning standards it built in Riyadh to homes, villas and offices in the UAE.",
        "f_privacy": "Privacy", "f_terms": "Terms", "f_licence": "Trade licence no.",
        "f_sister": "Naqaa in Saudi Arabia",
        "aside_title": "Get a price on WhatsApp",
        "aside_text": "Tell us the home size, the service and your area. We reply with a clear price in AED.",
        "aside_more": "Related pages", "book_title": "Book your service with Naqaa", "why_title": "Why Naqaa?", "call_now": "Call now",
        "why_rows": ["Clear price in AED before booking", "Equipment and materials included", "A checklist for every service", "Dubai, Abu Dhabi, Sharjah, Ajman"],
        "stats": [("4", "emirates covered"), ("6", "cleaning services"), ("AED", "clear price upfront"), ("✓", "equipment included")],
        "final_h": "Ready for a cleaner place this week?",
        "final_p": "Send the details on WhatsApp and get your price before anything is booked.",
        "see_services": "See services", "learn_more": "Read more →", "price_arrow": "Get a price →",
        "faq_title": "Questions people ask",
        # quote form
        "q_title": "Quick quote", "q_sub": "Three taps, then we send your price on WhatsApp.",
        "q_size": "Home size", "q_service": "Service", "q_emirate": "Emirate",
        "q_area": "Area or building (optional)", "q_area_ph": "e.g. Dubai Marina, Al Reem",
        "q_btn": "Send me the price", "q_note": "No payment now. You confirm after you see the price.",
        "sizes": [("Studio", "Studio"), ("1BR", "1BR"), ("2BR", "2BR"), ("3BR", "3BR"), ("4BR+", "4BR+"), ("Villa", "Villa"), ("Office", "Office")],
    },
    "ar": {
        "brand_sub": "للتنظيف · الإمارات",
        "nav_services": "الخدمات", "nav_locations": "المناطق", "nav_about": "من نحن",
        "nav_faq": "الأسئلة", "nav_contact": "تواصل معنا", "nav_blog": "المدونة", "nav_quote": "اعرف السعر",
        "menu": "القائمة", "skip": "انتقل إلى المحتوى", "home": "الرئيسية",
        "other_lang": "English", "other_lang_label": "Read this page in English",
        "wa": "واتساب", "call": "اتصل", "wa_cta": "اطلب السعر على واتساب", "price": "اعرف سعرك",
        "draft": "نسخة معاينة · أرقام التواصل والدومين وبيانات الرخصة مؤقتة حتى يتم تأكيدها",
        "f_services": "الخدمات", "f_locations": "المناطق", "f_company": "الشركة",
        "f_about": "نقاء تنقل معايير التنظيف التي بنتها في الرياض إلى البيوت والفلل والمكاتب في الإمارات.",
        "f_privacy": "الخصوصية", "f_terms": "الشروط", "f_licence": "رقم الرخصة التجارية",
        "f_sister": "نقاء في السعودية",
        "aside_title": "اعرف السعر على واتساب",
        "aside_text": "أخبرنا بحجم البيت والخدمة ومنطقتك، ونرد عليك بسعر واضح بالدرهم.",
        "aside_more": "صفحات ذات صلة", "book_title": "احجز خدمتك الآن مع نقاء", "why_title": "لماذا نقاء؟", "call_now": "اتصل الآن",
        "why_rows": ["سعر واضح بالدرهم قبل الحجز", "المعدات والمواد علينا", "قائمة مهام لكل خدمة", "دبي وأبوظبي والشارقة وعجمان"],
        "stats": [("4", "إمارات نخدمها"), ("6", "خدمات تنظيف"), ("AED", "سعر واضح بالدرهم"), ("✓", "المعدات علينا")],
        "final_h": "جاهز لمكان أنظف هذا الأسبوع؟",
        "final_p": "أرسل التفاصيل على واتساب واعرف السعر قبل أي حجز.",
        "see_services": "تصفح الخدمات", "learn_more": "اقرأ المزيد ←", "price_arrow": "اعرف السعر ←",
        "faq_title": "أسئلة شائعة",
        "q_title": "عرض سعر سريع", "q_sub": "ثلاث اختيارات، ونرسل لك السعر على واتساب.",
        "q_size": "حجم المكان", "q_service": "الخدمة", "q_emirate": "الإمارة",
        "q_area": "المنطقة أو المبنى (اختياري)", "q_area_ph": "مثال: دبي مارينا، جزيرة الريم",
        "q_btn": "أرسل لي السعر", "q_note": "لا دفع الآن. تؤكد الحجز بعد أن ترى السعر.",
        "sizes": [("Studio", "استوديو"), ("1BR", "غرفة"), ("2BR", "غرفتين"), ("3BR", "3 غرف"), ("4BR+", "4 غرف+"), ("Villa", "فيلا"), ("Office", "مكتب")],
    },
}

# ---------- icons (inline SVG, decorative) ----------
_S = 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"'
ICONS = {
    "home": f'<svg {_S}><path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/></svg>',
    "spark": f'<svg {_S}><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8"/></svg>',
    "truck": f'<svg {_S}><rect x="3" y="7" width="13" height="10" rx="1"/><path d="M16 10h3l2 3v4h-5"/><circle cx="7" cy="18" r="1.6"/><circle cx="18" cy="18" r="1.6"/></svg>',
    "sofa": f'<svg {_S}><path d="M4 12V9a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v3"/><path d="M2 12a2 2 0 0 1 4 0v2h12v-2a2 2 0 0 1 4 0v5H2z"/><path d="M5 17v2M19 17v2"/></svg>',
    "drop": f'<svg {_S}><path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/></svg>',
    "office": f'<svg {_S}><rect x="4" y="3" width="16" height="18" rx="1"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2"/></svg>',
    "pin": f'<svg {_S}><path d="M12 21s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>',
    "shield": f'<svg {_S}><path d="M12 3l7 3v6c0 4.5-3 7.7-7 9-4-1.3-7-4.5-7-9V6z"/><path d="M9 12l2 2 4-4"/></svg>',
    "bucket": f'<svg {_S}><path d="M3 7h18M6 7l1 13h10l1-13M9 7V4h6v3"/></svg>',
    "receipt": f'<svg {_S}><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></svg>',
    "redo": f'<svg {_S}><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/></svg>',
    "menu": f'<svg {_S}><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
}
WA_ICON = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .2-3.3-.7-2.8-1.1-4.5-3.9-4.7-4.1-.1-.2-1.1-1.5-1.1-2.8s.7-2 1-2.3c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.9 2.1c.1.2.1.3 0 .5l-.3.5-.4.4c-.1.2-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.3 2.4 1.5.3.1.5.1.6-.1l.9-1c.2-.3.4-.2.6-.1l2 .9c.3.1.5.2.5.3.1.2.1.7-.1 1.3z"/></svg>'
CALL_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2z"/></svg>'
CALC_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 12h2M12 12h2M8 16h2M12 16h2"/></svg>'
LOGO_MARK = '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M20 3l5 12 12 5-12 5-5 12-5-12-12-5 12-5z" fill="none" stroke="#C9A84C" stroke-width="2.2" stroke-linejoin="round"/><circle cx="20" cy="20" r="3.2" fill="#C9A84C"/></svg>'


# Set by build.py: True once a language has at least one published article.
BLOG_LIVE = {"en": False, "ar": False}


# ---------- URLs ----------
def url(lang, path):
    """Site-relative URL for a page path like 'services/deep-cleaning/' ('' = home)."""
    return ("/ar/" if lang == "ar" else "/") + path


def abs_url(lang, path):
    return C.SITE_URL + url(lang, path)


def wa_number():
    return C.WHATSAPP or C.PLACEHOLDER_NUMBER


def tel_number():
    return C.PHONE or C.WHATSAPP or C.PLACEHOLDER_NUMBER


def is_placeholder():
    return not (C.WHATSAPP and C.PHONE)


# ---------- structured data ----------
def business_ref():
    return {"@id": C.SITE_URL + "/#business"}


def business_schema(lang, locations):
    data = {
        "@type": "LocalBusiness",
        "@id": C.SITE_URL + "/#business",
        "name": C.BRAND[lang],
        "alternateName": C.BRAND["ar" if lang == "en" else "en"],
        "url": abs_url(lang, ""),
        "logo": C.SITE_URL + "/assets/logo.svg",
        "image": C.SITE_URL + "/assets/og-default.png",
        "areaServed": [{"@type": "City", "name": n} for n in locations],
        "knowsLanguage": ["en", "ar"],
    }
    if C.PHONE or C.WHATSAPP:
        data["telephone"] = "+" + (C.PHONE or C.WHATSAPP)
    if C.EMAIL:
        data["email"] = C.EMAIL
    return data


def breadcrumb_schema(lang, trail):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": abs_url(lang, path)}
            for i, (name, path) in enumerate(trail)
        ],
    }


def faq_schema(faqs):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ],
    }


# ---------- components ----------
def quote_form(lang, services, locations, preset_service=None, preset_location=None, heading="h2"):
    t = UI[lang]
    sizes = "".join(
        f'<input type="radio" name="size" id="sz-{i}" value="{v}" data-label="{escape(label)}"{" checked" if i == 2 else ""}>'
        f'<label for="sz-{i}">{escape(label)}</label>'
        for i, (v, label) in enumerate(t["sizes"])
    )
    svc_opts = "".join(
        f'<option value="{s["slug"]}"{" selected" if s["slug"] == preset_service else ""}>{escape(s[lang]["name"])}</option>'
        for s in services
    )
    loc_opts = "".join(
        f'<option value="{l["slug"]}"{" selected" if l["slug"] == preset_location else ""}>{escape(l[lang]["name"])}</option>'
        for l in locations
    )
    return f'''<form class="quote" id="quote" data-wa="{wa_number()}" aria-labelledby="q-title">
  <{heading} id="q-title">{t["q_title"]}</{heading}>
  <p class="sub">{t["q_sub"]}</p>
  <fieldset class="field"><legend>{t["q_size"]}</legend><div class="seg">{sizes}</div></fieldset>
  <div class="field"><label for="q-service">{t["q_service"]}</label><select id="q-service" name="service">{svc_opts}</select></div>
  <div class="field"><label for="q-emirate">{t["q_emirate"]}</label><select id="q-emirate" name="emirate">{loc_opts}</select></div>
  <div class="field"><label for="q-area">{t["q_area"]}</label><input type="text" id="q-area" name="area" autocomplete="address-level3" placeholder="{t["q_area_ph"]}"></div>
  <button class="btn btn-wa" type="submit">{WA_ICON}<span>{t["q_btn"]}</span></button>
  <p class="note">{t["q_note"]}</p>
</form>'''


def booking_bar(lang, services, locations):
    """One-line booking bar (home hero): service, emirate, size, WhatsApp button."""
    t = UI[lang]
    svc = "".join(f'<option value="{s["slug"]}">{escape(s[lang]["name"])}</option>' for s in services)
    loc = "".join(f'<option value="{l["slug"]}">{escape(l[lang]["name"])}</option>' for l in locations)
    size = "".join(f'<option value="{v}"{" selected" if i == 2 else ""}>{escape(label)}</option>' for i, (v, label) in enumerate(t["sizes"]))
    return f'''<form class="bookbar" id="quote" data-wa="{wa_number()}" aria-label="{t["q_title"]}">
  <label for="bb-service"><small>{t["q_service"]}</small><select id="bb-service" name="service">{svc}</select></label>
  <label for="bb-emirate"><small>{t["q_emirate"]}</small><select id="bb-emirate" name="emirate">{loc}</select></label>
  <label for="bb-size"><small>{t["q_size"]}</small><select id="bb-size" name="size">{size}</select></label>
  <button class="btn btn-wa" type="submit">{WA_ICON}<span>{t["price"]}</span></button>
</form>'''


def faq_block(faqs):
    return '<div class="faq">' + "".join(
        f"<details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>" for q, a in faqs
    ) + "</div>"


SERVICE_IMG = {
    "home-cleaning": "/images/hero/home-carpet.webp", "deep-cleaning": "/images/deep-cleaning.webp",
    "move-in-move-out-cleaning": "/images/hero/hero-home.webp", "sofa-carpet-cleaning": "/images/majlis-cleaning.webp",
    "water-tank-cleaning": "/images/tank-cleaning-insulation.webp", "office-cleaning": "/images/office-cleaning.webp",
}
DEFAULT_IMG = "/images/hero/hero-sofa.webp"


def cards(items, cols=""):
    """items: (href, icon_key or None, title, text, more_label[, image])"""
    out = []
    for it in items:
        href, icon, title, text, more = it[:5]
        img = it[5] if len(it) > 5 else None
        ph = f'<span class="r-ph"><img src="{img}" alt="" loading="lazy" decoding="async"></span>' if img else ""
        ic = f'<span class="ic">{ICONS[icon]}</span>' if icon else ""
        out.append(f'<a class="card{" r-img" if img else ""}" href="{href}">{ph}<span class="r-cb">{ic}<h3>{escape(title)}</h3><p>{escape(text)}</p><span class="more">{more}</span></span></a>')
    return f'<div class="cards {cols}">' + "".join(out) + "</div>"


def crumbs_html(lang, trail):
    items = []
    for i, (name, path) in enumerate(trail):
        if i == len(trail) - 1:
            items.append(f'<li><span aria-current="page">{escape(name)}</span></li>')
        else:
            items.append(f'<li><a href="{url(lang, path)}">{escape(name)}</a></li>')
    aria = "مسار الصفحة" if lang == "ar" else "Breadcrumb"
    return f'<nav class="crumbs" aria-label="{aria}"><ol>{"".join(items)}</ol></nav>'


def final_cta(lang):
    t = UI[lang]
    return f'''<section class="final r-final"><div class="wrap"><div class="r-final-card">
  <h2>{t["final_h"]}</h2><p>{t["final_p"]}</p>
  <div class="btn-row"><a class="btn btn-gold" href="{url(lang, "get-a-quote/")}">{CALC_ICON}<span>{t["price"]}</span></a>
  <a class="btn btn-wa" href="https://wa.me/{wa_number()}" target="_blank" rel="noopener">{WA_ICON}<span>{t["wa_cta"]}</span></a>
  <a class="btn btn-line" href="tel:+{tel_number()}">{CALL_ICON}<span>{t["call_now"]}</span></a></div>
</div></div></section>'''


def aside(lang, related):
    from tools.shell import tel_display
    t = UI[lang]
    links = "".join(f'<li><a href="{href}">{escape(name)}</a></li>' for href, name in related)
    why = "".join(f"<li>{escape(x)}</li>" for x in t["why_rows"])
    return f'''<aside class="aside">
  <div class="box r-book"><h2>{t["book_title"]}</h2>
    <a class="btn btn-gold" href="tel:+{tel_number()}">{CALL_ICON}<span dir="ltr">{tel_display()}</span></a>
    <a class="btn btn-wa" href="https://wa.me/{wa_number()}" target="_blank" rel="noopener">{WA_ICON}<span>{t["wa_cta"]}</span></a>
    <p>{t["aside_text"]}</p></div>
  <div class="box r-why"><h2>{t["why_title"]}</h2><ul>{why}</ul></div>
  <div class="box"><h2>{t["aside_more"]}</h2><ul>{links}</ul></div>
</aside>'''


# ---------- analytics ----------
def analytics():
    out = []
    if C.GTM_ID:
        out.append(f"<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{C.GTM_ID}');</script>")
    if C.GA_ID:
        out.append(f'<script async src="https://www.googletagmanager.com/gtag/js?id={C.GA_ID}"></script>'
                   f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{C.GA_ID}');</script>")
    if C.CLARITY_ID:
        out.append(f'<script>(function(c,l,a,r,i,t,y){{c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);}})(window,document,"clarity","script","{C.CLARITY_ID}");</script>')
    return "\n".join(out)


FONTS = {
    "en": "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap",
    "ar": "https://fonts.googleapis.com/css2?family=Cairo:wght@600;800;900&family=IBM+Plex+Sans+Arabic:wght@400;600;700&display=swap",
}


# ---------- full page ----------
def seo_head(lang, path, title, description, schema=(), has_alt=True, noindex=False, og_image=None, og_type="website"):
    """charset, analytics, title/description, canonical, hreflang, Open Graph, icons and JSON-LD."""
    graph = [dict(s) for s in schema]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")) if graph else ""
    alt = ""
    if has_alt:
        alt = (f'<link rel="alternate" hreflang="en" href="{abs_url("en", path)}">\n'
               f'<link rel="alternate" hreflang="ar" href="{abs_url("ar", path)}">\n'
               f'<link rel="alternate" hreflang="x-default" href="{abs_url("en", path)}">')
    og_locale = "ar_AE" if lang == "ar" else "en_AE"
    robots = "noindex,follow" if noindex else "index,follow,max-image-preview:large"
    verify = f'<meta name="google-site-verification" content="{C.GSC_VERIFY}">' if C.GSC_VERIFY else ""
    ld_tag = f'<script type="application/ld+json">{ld}</script>' if ld else ""
    return f'''<meta charset="utf-8">
{analytics()}
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{abs_url(lang, path)}">
{alt}
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{escape(C.BRAND[lang])}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{abs_url(lang, path)}">
<meta property="og:image" content="{og_image or C.SITE_URL + "/assets/og-default.png"}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:locale" content="{og_locale}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0D1828">
{verify}
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
{ld_tag}'''


def page(lang, path, title, description, body, services, locations, schema=(), current=None, has_alt=True, noindex=False,
         alt_path=None, og_image=None, og_type="website"):
    t = UI[lang]
    other = "en" if lang == "ar" else "ar"
    dir_ = "rtl" if lang == "ar" else "ltr"
    graph = [dict(s) for s in schema]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")) if graph else ""
    alt = ""
    if has_alt:
        alt = (f'<link rel="alternate" hreflang="en" href="{abs_url("en", path)}">\n'
               f'<link rel="alternate" hreflang="ar" href="{abs_url("ar", path)}">\n'
               f'<link rel="alternate" hreflang="x-default" href="{abs_url("en", path)}">')
    og_locale = "ar_AE" if lang == "ar" else "en_AE"
    robots = "noindex,follow" if noindex else "index,follow,max-image-preview:large"
    verify = f'<meta name="google-site-verification" content="{C.GSC_VERIFY}">' if C.GSC_VERIFY else ""

    def nav_link(key, p):
        cur = ' aria-current="page"' if current == p else ""
        return f'<a href="{url(lang, p)}"{cur}>{t[key]}</a>'

    nav_items = [("nav_services", "services/"), ("nav_locations", "locations/")] + ([("nav_blog", "blog/")] if BLOG_LIVE[lang] else []) + [("nav_about", "about/"), ("nav_faq", "faq/"), ("nav_contact", "contact/")]
    nav = "".join(nav_link(k, p) for k, p in nav_items)
    alt_target = path if alt_path is None else alt_path
    lang_link = f'<a class="lang-link" href="{url(other, alt_target)}" hreflang="{other}" lang="{other}" aria-label="{t["other_lang_label"]}">{t["other_lang"]}</a>'

    from tools import shell
    body = cardify(body)
    return f'''<!doctype html>
<html lang="{lang}" dir="{dir_}">
<head>
{seo_head(lang, path, title, description, schema, has_alt, noindex, og_image, og_type)}
{shell.head_assets()}<link rel="stylesheet" href="/assets/site.css">
<link rel="stylesheet" href="/assets/riyadh-inner.css">
</head>
<body class="nq-inner r-page">
<a class="skip" href="#main">{t["skip"]}</a>
{shell.header(lang, url(other, alt_target))}
<main id="main">
{body}
</main>
{shell.footer(lang)}
<script src="/assets/site.js" defer></script>
<script src="/assets/nq/nq-ui.js" defer></script>
</body>
</html>
'''


def cardify(body):
    """Riyadh look: every <h2> section inside an article.prose becomes its own card."""
    def wrap(m):
        inner = m.group(2)
        parts = re.split(r"(?=<h2[ >])", inner)
        out = []
        for part in parts:
            if not part.strip():
                continue
            out.append(f'<section class="r-card">{part}</section>' if part.lstrip().startswith("<h2") else f'<div class="r-card r-card-lead">{part}</div>')
        return f'<article class="{m.group(1)}">' + "".join(out) + "</article>"
    return re.sub(r'<article class="(prose(?! post)[^"]*)">(.*?)</article>', wrap, body, flags=re.S)
