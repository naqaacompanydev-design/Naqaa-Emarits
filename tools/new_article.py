#!/usr/bin/env python3
"""Create a new blog article from the template.

  python3 tools/new_article.py --slug move-out-cleaning-checklist-dubai --section moving --langs ar,en \
      --cover path/to/cover.jpg

Creates content/blog/<slug>/ with body.<lang>.html for each language and adds the article at the top
of content/blog/articles.json as a draft. Then:
  1. fill title / desc / excerpt / cover_alt in articles.json (every TODO),
  2. write the content in body.<lang>.html,
  3. set "draft": false and run: python3 build.py
"""
import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.blog import SECTIONS, SRC  # noqa: E402

BODY = {
    "ar": """<!-- محتوى المقالة: ابدأ من هنا. لا تضف <h1> ولا فهرس ولا وقت قراءة ولا صندوق حجز: الموقع يضيفهم.

مكونات جاهزة (انسخ ما تحتاجه):
  <h2>عنوان قسم</h2>  <p>فقرة</p>
  <div class="tip-box"><b>نصيحة</b>النص</div>
  <div class="warn-box"><b>تنبيه</b>النص</div>
  <ul class="check"><li>نقطة</li></ul>
  <ol class="steps-list"><li>خطوة</li></ol>
  <figure><img src="photo.jpg" alt="وصف الصورة"><figcaption>تعليق</figcaption></figure>
  <h2>أسئلة شائعة</h2>
  <div class="faq"><details><summary>السؤال؟</summary><p>الإجابة.</p></details></div>
روابط داخلية للخدمات: /ar/services/deep-cleaning/  /ar/locations/dubai/
-->
<p>TODO: مقدمة قصيرة تشرح للقارئ ماذا سيستفيد من المقال.</p>

<h2>TODO: أول قسم</h2>
<p>TODO</p>

<h2>TODO: ثاني قسم</h2>
<p>TODO</p>

<h2>TODO: ثالث قسم</h2>
<p>TODO</p>
<!-- محتوى المقالة: انتهى -->
""",
    "en": """<!-- Article content starts here. Don't add an <h1>, table of contents, reading time or booking box: the site adds them.

Ready components (copy what you need):
  <h2>Section heading</h2>  <p>Paragraph</p>
  <div class="tip-box"><b>Tip</b>Text</div>
  <div class="warn-box"><b>Watch out</b>Text</div>
  <ul class="check"><li>Point</li></ul>
  <ol class="steps-list"><li>Step</li></ol>
  <figure><img src="photo.jpg" alt="Describe the image"><figcaption>Caption</figcaption></figure>
  <h2>FAQ</h2>
  <div class="faq"><details><summary>Question?</summary><p>Answer.</p></details></div>
Internal links: /services/deep-cleaning/  /locations/dubai/
-->
<p>TODO: a short intro that tells the reader what they will get from this article.</p>

<h2>TODO: first section</h2>
<p>TODO</p>

<h2>TODO: second section</h2>
<p>TODO</p>

<h2>TODO: third section</h2>
<p>TODO</p>
<!-- Article content ends here -->
""",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", required=True, help="English, lowercase, words joined by -")
    ap.add_argument("--section", required=True, choices=list(SECTIONS))
    ap.add_argument("--langs", default="ar,en", help="ar, en or ar,en (default)")
    ap.add_argument("--cover", help="cover image (jpg/png/webp), ideally 1600x900 or larger")
    a = ap.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", a.slug):
        sys.exit("✗ slug must be lowercase English words joined by - (e.g. sofa-cleaning-tips-dubai)")
    langs = [l.strip() for l in a.langs.split(",") if l.strip()]
    if not langs or any(l not in ("ar", "en") for l in langs):
        sys.exit("✗ --langs must be ar, en or ar,en")
    folder = SRC / a.slug
    if folder.exists():
        sys.exit(f"✗ {folder.relative_to(ROOT)} already exists")
    folder.mkdir(parents=True)
    for l in langs:
        (folder / f"body.{l}.html").write_text(BODY[l], encoding="utf-8")
    cover = ""
    if a.cover:
        src = Path(a.cover)
        if not src.exists():
            sys.exit(f"✗ cover not found: {src}")
        cover = "cover" + src.suffix.lower()
        shutil.copy2(src, folder / cover)

    path = SRC / "articles.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    entry = {"slug": a.slug, "section": a.section, "date": date.today().isoformat(), "updated": "", "draft": True, "cover": cover}
    for l in langs:
        entry[l] = {"title": "TODO", "short_title": "", "desc": "TODO (120-155 characters for Google)",
                    "excerpt": "TODO (one or two lines for the blog card)", "cover_alt": "TODO" if cover else ""}
    data.insert(0, entry)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✓ created {folder.relative_to(ROOT)}/ ({', '.join('body.' + l + '.html' for l in langs)}) and added a draft to articles.json")
    print("  next: fill the TODOs, set \"draft\": false, then run python3 build.py")


if __name__ == "__main__":
    main()
