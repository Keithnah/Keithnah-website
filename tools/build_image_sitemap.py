"""List the site's photos and floor plans in sitemap-images.xml so they can appear in Google Images.

The image files have short hash names, so this tells search engines which page each image
belongs to. robots.txt points to it. Run by tools/build_all.py.
"""
import glob
import os
import re
from urllib.parse import urljoin

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://keithnah.com/'
DIRS = ['', 'property', 'area', 'best', 'article', 'guides', 'topic']
SKIP = ('images/flags/', 'f304c8479b1fe873')   # flags and the logo
os.chdir(ROOT)
urls, total = [], 0
for d in DIRS:
    for p in sorted(glob.glob(os.path.join(d, '*.html') if d else '*.html')):
        if p == '404.html':
            continue
        t = open(p, encoding='utf-8').read()
        if 'noindex' in t[:3000]:
            continue
        page = SITE + ('' if p == 'index.html' else p)
        seen = []
        for m in re.finditer(r'<img[^>]+src="([^"]+)"', t):
            s = m.group(1)
            if s.startswith(('data:', 'http')) and not s.startswith(SITE):
                continue
            u = urljoin(SITE + p, s).split('?')[0]
            if not u.startswith(SITE + 'images/') or any(x in u for x in SKIP) or not re.search(r'\.(jpe?g|png|webp)$', u, re.I):
                continue
            if u not in seen:
                seen.append(u)
        for m in re.finditer(r"url\('([^']+\.(?:jpe?g|png|webp))'\)", t):   # background photos (home hero)
            u = urljoin(SITE + p, m.group(1))
            if u.startswith(SITE + 'images/') and u not in seen:
                seen.append(u)
        if seen:
            urls.append((page, seen[:1000]))
            total += len(seen[:1000])
xml = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
for page, imgs in urls:
    xml.append('  <url><loc>%s</loc>%s</url>' % (page, ''.join('<image:image><image:loc>%s</image:loc></image:image>' % i for i in imgs)))
xml.append('</urlset>')
open('sitemap-images.xml', 'w', encoding='utf-8').write('\n'.join(xml) + '\n')
r = open('robots.txt', encoding='utf-8').read()
if 'sitemap-images.xml' not in r:
    r = r.rstrip('\n') + '\nSitemap: https://keithnah.com/sitemap-images.xml\n'
    open('robots.txt', 'w', encoding='utf-8').write(r)
print('image sitemap: %d images on %d pages' % (total, len(urls)))
