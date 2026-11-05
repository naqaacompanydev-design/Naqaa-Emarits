"""Site-wide settings. Fill the TODO values before launch, then run: python3 build.py"""

# TODO: the real domain (no trailing slash). Canonical URLs, hreflang, sitemap and
# structured data are all built from this, so set it before the site goes live.
SITE_URL = "https://www.naqaa-uae.com"

BRAND = {"en": "Naqaa Cleaning", "ar": "نقاء للتنظيف"}
BRAND_SHORT = {"en": "Naqaa", "ar": "نقاء"}

# TODO: real UAE numbers, digits only with country code (e.g. "9715XXXXXXXX").
# While empty, links use a placeholder and structured data leaves the phone out.
WHATSAPP = ""
PHONE = ""
EMAIL = ""

# TODO: trade licence number as printed on the licence. Shown in the footer when set.
TRADE_LICENCE = ""

# Analytics (leave empty to skip). Same tools as naqaa-cleaning.com.
GA_ID = ""        # e.g. "G-XXXXXXX"
GTM_ID = ""       # e.g. "GTM-XXXXXXX"
CLARITY_ID = ""

# Google Search Console verification token (meta tag content), optional.
GSC_VERIFY = ""

PLACEHOLDER_NUMBER = "971000000000"

# Order matters: this is the order used in menus, footers and cross links.
SERVICES = ["home-cleaning", "deep-cleaning", "move-in-move-out-cleaning",
            "sofa-carpet-cleaning", "water-tank-cleaning", "office-cleaning"]
LOCATIONS = ["dubai", "abu-dhabi", "sharjah", "ajman"]
