# SFCS website for Wix (embed file)

`sfcs-site.js` is the public School of Film and Cinema Studies homepage as one `<sfcs-site>` custom element,
used on a Wix Studio page. It holds only the public website (design, text, animations). The site is built
from a separate private repository; this repo is only the finished file.

## Text for crawlers that do not run JavaScript (SEO)

The homepage is drawn by JavaScript, so the raw HTML Wix sends has no headings or text. `seo_noscript.py` writes `seo-noscript.html`: the same text (headline, courses and fees, projects, grant, admissions, campuses, FAQ, contact) as a `<noscript>` block. Visitors with JavaScript never see it.

It is installed in Wix under **Settings → Custom code → Body - end → "SEO text for crawlers (noscript)"** (all pages, essential).

**When the content changes** (fees, FAQ, grant dates, films, campuses): run `python3 seo_noscript.py`, commit `seo-noscript.html`, then in Wix open that snippet (⋯ → Edit) and replace its code with the new file. The text should match what the page shows, so don't skip this.
