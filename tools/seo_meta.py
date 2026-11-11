"""Keep page titles and meta descriptions short enough that Google shows them in full.

Google cuts titles after about 60-65 characters and descriptions after about 155-160.
The generators write full-length titles; this step shortens only the ones that are too long,
dropping the least useful words first (brand suffix, "Price, Floor Plan & Unit Types"...)
and putting the key facts (area, starting price) first. Descriptions are cut at the end of a
sentence. Runs in tools/build_all.py after the generators, so it is safe to run again.
"""
import glob
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = ['', 'article', 'area', 'best', 'guides', 'notes', 'property', 'topic']
TMAX, DMAX = 65, 158


def rm(n):
    n = int(n.replace(',', ''))
    return 'RM%.1fM' % (n / 1e6) if n >= 1e6 else 'RM%dK' % round(n / 1e3)


def short_title(t, rel, page):
    if len(t) <= TMAX:
        return t
    steps = [
        lambda s: s.replace(' | Keith Nah Real Estate', ' | Keith Nah'),
        lambda s: s.replace('Price, Floor Plan & Unit Types', 'Price & Floor Plans'),
        lambda s: s.replace(': Malaysia Property Articles', ': Property Articles'),
        lambda s: s.replace(' (Free PDF)', ''),
    ]
    if rel.startswith('area/'):
        m = re.match(r'New Launch Condos in (.+?) (\d{4}) \| Prices & Floor Plans \| Keith Nah$', t)
        if m:
            place, year = m.groups()
            p = re.search(r'from about (RM[\d,]+)', page)
            opts = []
            if p:
                opts.append('%s New Launch Condos %s | From %s | Keith Nah' % (place, year, rm(p.group(1)[2:])))
                opts.append('%s New Launch Condos %s | From %s' % (place, year, rm(p.group(1)[2:])))
            opts += ['%s New Launch Condos %s | Keith Nah' % (place, year), '%s New Launch Condos %s' % (place, year)]
            for o in opts:
                if len(o) <= TMAX:
                    return o
            return opts[-1]
    steps += [
        lambda s: s.replace(' | Price & Floor Plans | Keith Nah', ' | Price & Floor Plans'),
        lambda s: re.sub(r' \| Keith Nah$', '', s),
        lambda s: s.replace(' | Price & Floor Plans', ' | Price'),
    ]
    for f in steps:
        t = f(t)
        if len(t) <= TMAX:
            break
    return t


def short_desc(d):
    if len(d) <= DMAX + 2:
        return d
    cut = d[:DMAX]
    ends = [m.end() for m in re.finditer(r'[.!?](\s|$)', cut)]
    if ends and ends[-1] >= 90:
        return cut[:ends[-1]].strip()
    cut = cut[:cut.rfind(' ')].rstrip(' ,;:–-')
    return cut + '…'


nt = nd = nc = 0
for d in DIRS:
    for p in sorted(glob.glob(os.path.join(ROOT, d, '*.html'))):
        rel = os.path.relpath(p, ROOT)
        page = open(p, encoding='utf-8').read()
        out = page
        m = re.search(r'<title>([^<]*)</title>', out)
        if m:
            t = html.unescape(m.group(1))
            t2 = short_title(t, rel, page)
            if t2 != t:
                out = out[:m.start(1)] + html.escape(t2, quote=False) + out[m.end(1):]
                nt += 1
        m = re.search(r'<meta name="description" content="([^"]*)"', out)
        if m:
            s = html.unescape(m.group(1))
            s2 = short_desc(s)
            if s2 != s:
                out = out[:m.start(1)] + html.escape(s2) + out[m.end(1):]
                nd += 1
        # every English page names its own address, so /index.html and / count as one page
        if '/' not in rel and 'rel="canonical"' not in out and rel != '404.html':
            url = 'https://keithnah.com/' + ('' if rel == 'index.html' else rel)
            out = re.sub(r'(<meta name="description"[^>]*>)', r'\1\n<link rel="canonical" href="%s">' % url, out, count=1)
            nc += 1
        if out != page:
            open(p, 'w', encoding='utf-8').write(out)
print('seo_meta: shortened %d titles and %d descriptions; %d canonical tags added' % (nt, nd, nc))
