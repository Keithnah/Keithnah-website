"""Weekly site check: broken links and gaps in the project data.

- Every internal link on every English page must point to a file that exists.
- With --external, the news source links in the market notes are fetched too (a 404 means the
  outlet moved or removed the article).
- Projects missing a price, a developer, a completion date or a photo are listed.
Prints a summary; with --post the result goes to the Apps Script web app (type "Site Check"),
which sends it to Keith on Telegram. Run by .github/workflows/site-check.yml every Monday.
"""
import glob
import html
import json
import os
import re
import sys
import urllib.request
from urllib.parse import urljoin, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
SITE = 'https://keithnah.com/'
DIRS = ['', 'article', 'area', 'best', 'developer', 'guides', 'mm2h', 'notes', 'property', 'station', 'topic', 'vs']


def exists(path):
    path = path.split('#')[0].split('?')[0]
    if path in ('', '/'):
        return True
    p = path.lstrip('/')
    if p.endswith('/'):
        p += 'index.html'
    return os.path.exists(p) or os.path.exists(p + '/index.html')


broken = {}
pages = 0
for d in DIRS:
    for f in sorted(glob.glob(os.path.join(d, '*.html') if d else '*.html')):
        pages += 1
        t = open(f, encoding='utf-8').read()
        base = SITE + f
        for m in re.finditer(r'<(?:a|link|img|script)\b[^>]*?(?:href|src)="([^"]+)"', t):
            u = html.unescape(m.group(1))
            if u.startswith(('#', 'mailto:', 'tel:', 'javascript:', 'data:', 'whatsapp:')) or re.search(r"[{}'+]| \+ ", u):
                continue
            full = urljoin(base, u)
            if not full.startswith(SITE):
                continue
            path = urlparse(full).path
            if path.startswith(('/tg/', '/guides/get.php', '/downloads/')) or path.endswith('.php'):
                continue
            if not exists(path):
                broken.setdefault(path, set()).add(f)

src_bad = []
if '--external' in sys.argv:
    notes = json.load(open(os.path.join(HERE, 'market_notes.json'), encoding='utf-8'))
    seen = set()
    for n in notes:
        for s in n.get('sources', []):
            u = s['url']
            if u in seen:
                continue
            seen.add(u)
            try:
                req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (site check)'})
                code = urllib.request.urlopen(req, timeout=20).status
            except urllib.error.HTTPError as e:
                code = e.code
            except Exception:
                code = 0
            if code in (404, 410):
                src_bad.append({'url': u, 'note': n['title'].get('en', ''), 'code': code})

# gaps in the project data
import subprocess
src = open('projects.html', encoding='utf-8').read()
moved = 'const PROJECT_DETAILS = ' not in src
if moved:
    subprocess.run([sys.executable, os.path.join(HERE, 'externalize.py'), 'in'], check=True, capture_output=True)
    src = open('projects.html', encoding='utf-8').read()
i = src.index('const PROJECT_DETAILS = ')
P = json.JSONDecoder().raw_decode(src[src.index('=', i) + 1:].lstrip())[0]
idx = json.load(open(os.path.join(HERE, 'project_index.json'), encoding='utf-8'))
gaps = {'price': [], 'developer': [], 'completion': [], 'photo': []}
for k, p in enumerate(P):
    name = p['name']
    if not re.search(r'RM\s?\d', p.get('price') or ''):
        gaps['price'].append(name)
    if not (p.get('details_extra') or {}).get('Developer'):
        gaps['developer'].append(name)
    if re.search(r'^\s*(TBC|-|)\s*$', p.get('completion') or '', re.I):
        gaps['completion'].append(name)
    page = 'property/%s.html' % idx[k]['slug']
    if os.path.exists(page) and 'og:image' not in open(page, encoding='utf-8').read():
        gaps['photo'].append(name)

if moved:
    subprocess.run([sys.executable, os.path.join(HERE, 'externalize.py'), 'out'], check=True, capture_output=True)

result = {'type': 'Site Check', 'pages': pages,
          'broken': [{'path': p, 'on': sorted(v)[:3], 'count': len(v)} for p, v in sorted(broken.items(), key=lambda x: -len(x[1]))][:15],
          'broken_total': len(broken), 'sources': src_bad[:10], 'gaps': {k: v[:12] for k, v in gaps.items()},
          'gap_counts': {k: len(v) for k, v in gaps.items()}}
print(json.dumps(result, ensure_ascii=False, indent=1))

if '--post' in sys.argv:
    ep = re.search(r"https://script\.google\.com/macros/s/[^']*/exec", open('lead-tracker.js', encoding='utf-8').read()).group(0)
    req = urllib.request.Request(ep, data=json.dumps(result).encode(), headers={'Content-Type': 'text/plain'})
    try:
        print('posted:', urllib.request.urlopen(req, timeout=30).read()[:200])
    except Exception as e:
        print('post failed:', e)
