"""Builds seo-noscript.html: the page's text as plain HTML for crawlers that do not run JavaScript.

Why: on Wix the homepage is drawn by custom elements (JavaScript), so the raw HTML has no headings or text.
Google runs JavaScript, but other crawlers, link readers and AI tools may not. This block goes into the Wix
Custom Code as a <noscript> in the body: browsers with JavaScript never show it, and it holds the same text
as the page. Re-generate (python3 build.py) and re-paste it in Wix whenever the content changes.

Everything comes from the site content (content/*.json through tools/build.py), plus the hero and "why" text
and the admissions steps read from the built template, so it cannot drift from the page by hand edits.
"""
import html, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(os.path.dirname(HERE), 'sfcs-homepage')
E = lambda s: re.sub(r'\s+([,.;:])', r'\1', html.escape(str(s or ''), quote=False)).replace('"', '&quot;')


def _site_data():
    sys.path.insert(0, os.path.join(SITE, 'tools'))
    import importlib
    b = importlib.import_module('build')
    return b.build_data()


def _section_text(page, sid):
    """Plain headings/paragraphs/list items of one template section (no buttons, forms, images)."""
    m = re.search(r'<section[^>]*id="%s"[^>]*>(.*?)\n  </section>' % sid, page, re.S)
    if not m:
        raise SystemExit('section %s not found in the built page' % sid)
    s = m.group(1)
    s = re.sub(r'<(script|style|button|form|svg|canvas|dialog)\b.*?</\1>', '', s, flags=re.S)
    out = []
    for tag, inner in re.findall(r'<(h2|h3|p|li)\b[^>]*>(.*?)</\1>', s, re.S):
        t = re.sub(r'<[^>]+>', '', inner)
        t = html.unescape(re.sub(r'\s+', ' ', t)).strip()
        if t and len(t) > 2:
            out.append((tag, t))
    return out


def build():
    d = _site_data()
    tmp = tempfile.mkdtemp()
    subprocess.run([sys.executable, os.path.join(SITE, 'tools', 'build.py'), tmp], check=True, capture_output=True)
    page = open(os.path.join(tmp, 'index.html'), encoding='utf-8').read()
    c = d['contact']
    o = []
    o.append('<h1>No classroom film school: School of Film and Cinema Studies (SFCS), Indore and Ahmedabad</h1>')
    o.append("<p>India's only all-practical film school. Learn on real sets with professional equipment from your first day, in Indore and Ahmedabad. Admissions %s.</p>" % E(d['session']))
    if d['announcement'].get('show') and d['announcement'].get('text'):
        o.append('<p>%s</p>' % E(d['announcement']['text']))
    o.append('<nav><a href="%s">Apply now</a></nav>' % E(d['apply_url']))

    # Why SFCS
    why = _section_text(page, 'why')
    nums = re.findall(r'<span class="n"[^>]*>(\d+)</span><span class="bar"></span><h3>(.*?)</h3>', page)
    for tag, t in why:
        for n, label in nums:
            if tag == 'h3' and t == html.unescape(label):
                t = '%s %s' % (n, t.lower())

        o.append('<%s>%s</%s>' % ('h2' if tag == 'h2' else 'p' if tag in ('p', 'li') else 'h3', E(t), 'h2' if tag == 'h2' else 'p' if tag in ('p', 'li') else 'h3'))

    # Courses and fees
    o.append('<h2>Courses and fees %s</h2>' % E(d['session']))
    o.append('<p>Foundation is three practical months with a batch short film. Intense is three months of deeper, one-to-one training plus three months of placement.</p><ul>')
    for k in d['courses']:
        o.append('<li><strong>%s</strong>: %s Foundation %s; Intense %s.</li>' % (E(k['name']), E(k['description']), E(k['foundation_fmt']), E(k['intense_fmt'])))
    o.append('</ul>')

    # Projects
    o.append('<h2>Our projects</h2><p>Short films made by SFCS students and mentors.</p><ul>')
    for p in d['projects']:
        cr = '; '.join('%s: %s' % (E(x['role']), E(x['names'])) for x in (p.get('credits') or []))
        o.append('<li><strong>%s</strong>. %s %s</li>' % (E(p['title']), E(p.get('tagline')), cr))
    o.append('</ul>')
    if d.get('festivals'):
        o.append('<h3>Festival selections</h3><ul>%s</ul>' % ''.join('<li>%s, %s</li>' % (E(f['name']), E(f['year'])) for f in d['festivals']))

    # Grants
    for g in d['grants']:
        o.append('<h2>%s</h2><p>%s</p>' % (E(g['name']), E(g['summary'])))
        if g.get('opens_long'):
            o.append('<p>Opens %s%s.</p>' % (E(g['opens_long']), (' and closes %s' % E(g['closes_long'])) if g.get('has_closes') and g.get('closes_long') else ''))
        for r in g.get('rules') or []:
            t = re.sub(r'<[^>]+>', ' ', r.get('body_html', ''))
            t = html.unescape(re.sub(r'\s+', ' ', t)).strip()
            if t:
                parts = [x.strip() for x in r.get('heading', '').split('\u2014')]
                head = (parts[1] if len(parts) > 1 else parts[0]).capitalize()
                o.append('<h3>%s</h3><p>%s</p>' % (E(head), E(t)))

    # Admissions steps
    for tag, t in _section_text(page, 'admissions'):
        o.append('<%s>%s</%s>' % ('h2' if tag == 'h2' else 'p' if tag in ('p', 'li') else 'h3', E(t), 'h2' if tag == 'h2' else 'p' if tag in ('p', 'li') else 'h3'))

    # Campuses
    o.append('<h2>Two cities, no classrooms</h2><ul>')
    for k in d['campuses']:
        o.append('<li><strong>%s</strong> (%s): %s <a href="%s">%s</a></li>' % (E(k['city']), E(k['status']), E(k['description']), E(k['link_url']), E(k['link_text'])))
    o.append('</ul>')

    # FAQ
    o.append('<h2>Questions, answered</h2>')
    for q in d['faq']:
        o.append('<h3>%s</h3><p>%s</p>' % (E(q['question']), E(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', q.get('answer_html') or q.get('answer') or '')).strip())))

    # Contact
    o.append('<h2>Contact</h2><p>Email <a href="mailto:%s">%s</a>. Phone and WhatsApp %s. Instagram <a href="%s">@schooloffilmindia</a>.</p>' % (E(c['email']), E(c['email']), E(c['phone']), E(c['instagram_url'])))
    return '<noscript>\n' + '\n'.join(o) + '\n</noscript>\n'


if __name__ == '__main__':
    out = build()
    open(os.path.join(HERE, 'seo-noscript.html'), 'w', encoding='utf-8').write(out)
    txt = re.sub(r'<[^>]+>', ' ', out)
    print('seo-noscript.html: %d bytes, %d words, h1=%d h2=%d h3=%d' % (len(out), len(txt.split()), out.count('<h1>'), out.count('<h2>'), out.count('<h3>')))
