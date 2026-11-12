"""Move the big inline scripts of the main pages into their own files, so pages download faster.

The home, projects, news, compare, calculator and market-notes pages carry large blocks of data
(project details, translations, articles). Inline, every visitor downloads them again with every
page and every language version. As files (assets/data/<page>-<n>.js?v=<hash>) the browser keeps
them, and all 6 language versions share one copy.

The generators edit these blocks in the pages, so tools/build_all.py runs
    python3 tools/externalize.py in    first: put the blocks back inline
    python3 tools/externalize.py out   last (before the language copies): move them out again
Run "in" yourself before using a tool on these pages outside build_all.
JSON-LD (structured data) stays inline for search engines.
"""
import glob
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
PAGES = ['index.html', 'projects.html', 'blog.html', 'compare.html', 'calculator.html', 'market-notes.html']
DATA = 'assets/data'
MIN = 15000
EXT = re.compile(r'<script src="assets/data/([a-z0-9-]+\.js)\?v=[0-9a-f]+" data-kn-inline="([^"]*)"></script>')


def inline():
    n = 0
    for p in PAGES:
        if not os.path.exists(p):
            continue
        t = open(p, encoding='utf-8').read()

        def back(m):
            body = open(os.path.join(DATA, m.group(1)), encoding='utf-8').read()
            attrs = m.group(2).replace('&quot;', '"')
            return '<script%s>%s</script>' % (attrs, body)
        t2 = EXT.sub(back, t)
        if t2 != t:
            open(p, 'w', encoding='utf-8').write(t2)
            n += 1
    print('externalize in: data put back inline on %d page(s)' % n)


def out():
    os.makedirs(DATA, exist_ok=True)
    keep, n = set(), 0
    for p in PAGES:
        if not os.path.exists(p):
            continue
        t = open(p, encoding='utf-8').read()
        if EXT.search(t):
            inline()
            t = open(p, encoding='utf-8').read()
        base = p[:-5]
        k = [0]

        def move(m):
            attrs, body = m.group(1), m.group(2)
            if len(body) < MIN or 'ld+json' in attrs or ' src=' in attrs or 'document.currentScript' in body or 'document.write' in body:
                return m.group(0)
            k[0] += 1
            name = '%s-%d.js' % (base, k[0])
            path = os.path.join(DATA, name)
            if not os.path.exists(path) or open(path, encoding='utf-8').read() != body:
                open(path, 'w', encoding='utf-8').write(body)
            keep.add(name)
            v = hashlib.sha1(body.encode('utf-8')).hexdigest()[:10]
            return '<script src="assets/data/%s?v=%s" data-kn-inline="%s"></script>' % (name, v, attrs.replace('"', '&quot;'))
        t2 = re.sub(r'<script([^>]*)>(.*?)</script>', move, t, flags=re.S)
        if t2 != t:
            open(p, 'w', encoding='utf-8').write(t2)
            n += 1
    for f in glob.glob(os.path.join(DATA, '*.js')):
        if os.path.basename(f) not in keep:
            os.remove(f)
    print('externalize out: %d data file(s) from %d page(s)' % (len(keep), n))


if __name__ == '__main__':
    {'in': inline, 'out': out}[sys.argv[1] if len(sys.argv) > 1 else 'out']()
