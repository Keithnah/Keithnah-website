"""Share images (og:image) for every page that has none: the picture WhatsApp, Facebook, Telegram
and LinkedIn show when someone shares a link.

Each image (1200x630, images/og/<page>.jpg) shows the page's best photo, a label, the title,
the starting price where the title has one, and the Keith Nah brand bar. Project pages keep their
own project photo. Images are drawn by tools/render_og.js and only redrawn when the text or photo
changes. The language copies (/zh/ ...) use the same image. Run by tools/build_all.py.
"""
import glob
import hashlib
import html
import json
import os
import re
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
SITE = 'https://keithnah.com/'
DIRS = ['', 'area', 'article', 'best', 'developer', 'guides', 'mm2h', 'notes', 'station', 'topic', 'vs']
CACHE = os.path.join(HERE, 'og_cache.json')
FALLBACK = 'images/18c3c17601a2ba81.jpg'   # Kuala Lumpur skyline (home hero)
SKIP_IMG = ('f304c8479b1fe873', 'images/flags/', 'images/og/', 'ffb01572bcbd138e')   # logo, flags, share images, YouTube icon
LABEL = {'area': 'New launch guide', 'best': 'Best new launch list', 'article': "Keith's article", 'topic': 'Property articles',
         'notes': "Keith's market note", 'developer': 'Developer', 'station': 'Browse by station', 'vs': 'Side by side', 'guides': 'Free PDF guide'}
BLOCK = re.compile(r'<!-- KN-OG -->.*?<!-- /KN-OG -->\n?', re.S)


def size(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size[0] * im.size[1]
    except Exception:
        return 0


def photos(t, rel, n=1):
    """The clearest content photos on the page (largest of the first few)."""
    seen = []
    for m in re.finditer(r'<img[^>]+src="([^"]+)"', t):
        s = m.group(1).split('?')[0]
        p = os.path.normpath(os.path.join(os.path.dirname(rel), s)) if not s.startswith('http') else ''
        if p.startswith('images/') and not any(x in p for x in SKIP_IMG) and re.search(r'\.(jpe?g|png|webp)$', p, re.I) and os.path.exists(p) and p not in seen:
            seen.append(p)
        if len(seen) >= 6:
            break
    if n == 2:
        return seen[:2]
    best = sorted(seen[:4], key=size, reverse=True)
    return best[:1]


def job(rel, t):
    folder = rel.split('/')[0] if '/' in rel else ''
    m = re.search(r'<title>([^<]*)</title>', t)
    title = html.unescape(m.group(1)) if m else 'Keith Nah Real Estate'
    parts = [x.strip() for x in title.split(' | ')]
    head = parts[0]
    sub = next((x for x in parts[1:] if x.startswith('From ')), '')
    if sub:
        sub = sub.replace('From ', 'from ')
    if folder == 'notes':
        area = re.search(r'data-f="area">([^<]*)<', t)
        eb = "Keith's market note" + (' · ' + html.unescape(area.group(1)) if area else '')
    elif folder == 'vs':
        area = re.search(r'data-hb="vs_eb"[^>]*>Side by side · ([^<]*)<', t)
        eb = 'Side by side' + (' · ' + html.unescape(area.group(1)) if area else '')
        head = head.replace(': Which One Fits You?', '')
        sub = sub or 'Which one fits you?'
    elif folder:
        eb = LABEL.get(folder, 'Keith Nah Real Estate')
    else:
        eb = 'Keith Nah Real Estate'
    if rel == 'index.html':
        head, eb = 'New launch property in Malaysia, explained by Keith Nah', 'Kuala Lumpur · Penang · Johor'
    imgs = photos(t, rel, 2 if folder == 'vs' else 1)
    if folder == 'vs' and len(imgs) < 2:
        imgs = imgs[:1]
    imgs = imgs or [FALLBACK]
    slug = rel[:-5].replace('/', '-')
    return {'out': 'images/og/%s.jpg' % slug, 'eb': eb, 't': head, 'sub': sub, 'imgs': imgs, 'vs': folder == 'vs' and len(imgs) == 2}


def tags(j, t):
    url = SITE + j['out']
    out = '<!-- KN-OG -->'
    if 'property="og:title"' not in t:
        m = re.search(r'<title>([^<]*)</title>', t)
        d = re.search(r'<meta name="description" content="([^"]*)"', t)
        out += '<meta property="og:type" content="website">'
        if m:
            out += '<meta property="og:title" content="%s">' % m.group(1).replace('"', '&quot;')
        if d:
            out += '<meta property="og:description" content="%s">' % d.group(1)
    out += ('<meta property="og:image" content="%s"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
            '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="%s">' % (url, url))
    return out + '<!-- /KN-OG -->'


try:
    cache = json.load(open(CACHE, encoding='utf-8'))
except (OSError, ValueError):
    cache = {}
todo, pages = [], []
for d in DIRS:
    for p in sorted(glob.glob(os.path.join(d, '*.html') if d else '*.html')):
        if p == '404.html':
            continue
        t = open(p, encoding='utf-8').read()
        t0 = BLOCK.sub('', t)
        if 'property="og:image"' in t0:   # the page already has its own picture (project pages, ...)
            continue
        j = job(p, t0)
        key = hashlib.sha1(json.dumps([j, [os.path.getsize(i) for i in j['imgs']]], sort_keys=True).encode()).hexdigest()[:16]
        if cache.get(j['out']) != key or not os.path.exists(j['out']):
            todo.append(j)
        cache[j['out']] = key
        pages.append((p, t, t0, j))
if todo:
    f = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False)
    json.dump(todo, f)
    f.close()
    r = subprocess.run(['node', os.path.join(HERE, 'render_og.js'), f.name], capture_output=True, text=True)
    os.unlink(f.name)
    if r.returncode:
        raise SystemExit('render_og.js failed: ' + r.stderr[-2000:])
n = 0
for p, t, t0, j in pages:
    blk = tags(j, t0)
    m = re.search(r'<meta property="og:url"[^>]*>', t0)
    t2 = (t0[:m.end()] + blk + t0[m.end():]) if m else t0.replace('</head>', blk + '\n</head>', 1)
    if t2 != t:
        open(p, 'w', encoding='utf-8').write(t2)
        n += 1
keep = {j['out'] for _p, _t, _t0, j in pages}
for f in glob.glob('images/og/*.jpg'):
    if f not in keep:
        os.remove(f)
        cache.pop(f, None)
json.dump({k: v for k, v in cache.items() if k in keep}, open(CACHE, 'w', encoding='utf-8'), indent=0)
print('share images: %d pages, %d drawn now' % (len(pages), len(todo)))
