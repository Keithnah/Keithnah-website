"""Build one search-friendly page per project: property/<slug>.html.

Reads the project data and tags that already live in projects.html
(PROJECT_DETAILS, KN_TAGS, the cards and the article lists), writes a
static page for every project, links the cards and popups in
projects.html to those pages, and rewrites sitemap.xml.

Run from the repository root after editing projects.html:
    python3 tools/build_project_pages.py
Safe to run again: pages and links are regenerated each time.
"""
import datetime
import html
import json
import os
import re

SITE = 'https://keithnah.com'
OUT = 'property'
WA = '60102821568'
TODAY = datetime.date.today().isoformat()
E = lambda s: html.escape(str(s if s is not None else ''), quote=True)

src = open('projects.html', encoding='utf-8').read()


def js_json(name):
    i = src.index('const %s = ' % name) if ('const %s = ' % name) in src else src.index('var %s = ' % name)
    i = src.index('=', i) + 1
    return json.JSONDecoder().raw_decode(src[i:].lstrip())[0]


P = js_json('PROJECT_DETAILS')
TAGS = js_json('KN_TAGS')
assert len(P) == len(TAGS)

# Article titles and which articles belong to which project / area
ART = {m[0]: (m[2], m[4]) for m in re.findall(
    r"\b(a\d+):\{cat:(['\"])(.*?)\2,\s*title:(['\"])(.*?)\4\}", src)}


def js_lists(name):
    i = src.index('const %s = {' % name)
    block = src[i:src.index('};', i)]
    return {m[1]: re.findall(r"'(a\d+)'", m[2]) for m in re.findall(
        r"(['\"])(.+?)\1\s*:\s*(\[[^\]]*\])", block)}


OVR, LOCA = js_lists('PROJECT_ARTICLE_OVERRIDES'), js_lists('LOC_ARTICLES')

# Card photo and property type, by card index
PHOTO, TYPE = {}, {}
for m in re.finditer(r'data-idx="(\d+)" onclick="openDetailModal\(\1\)">(.*?)<p class="proj-loc">', src, re.S):
    k = int(m.group(1))
    im = re.search(r'<img class="proj-photo" src="([^"]+)"', m.group(2))
    ty = re.search(r'badge-type type-[a-z]+">([^<]+)<', m.group(2))
    PHOTO[k] = im.group(1) if im else ''
    TYPE[k] = ty.group(1) if ty else 'Residential'

LOGO = re.search(r'<img class="logo-mark-img" src="([^"]+)"', src).group(1)
ICON = re.search(r'<link rel="icon" type="image/png" href="([^"]+)"', src).group(1)


def slugify(s):
    s = s.lower().replace('&', ' and ').replace("'", '').replace('’', '')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


SLUGS = []
for i, p in enumerate(P):
    s = slugify(TAGS[i][0])
    while s in SLUGS:
        s += '-2'
    SLUGS.append(s)


def up(path):  # path relative to the site root, seen from property/
    return path if path.startswith(('http', 'data:', '#')) else '../' + path


def wa(msg):
    from urllib.parse import quote_plus
    return 'https://api.whatsapp.com/send/?phone=%s&text=%s&type=phone_number&app_absent=0' % (WA, quote_plus('(KNRE) ' + msg))


TAG_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.6 13.4l-7.2 7.2a2 2 0 01-2.8 0L3 13V3h10l7.6 7.6a2 2 0 010 2.8z"/><circle cx="7.5" cy="7.5" r="1.5"/></svg>'
WA_SVG = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2.05 22l5.25-1.38c1.44.79 3.06 1.2 4.72 1.2h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.87 9.87 0 0012.04 2zm5.8 14.06c-.24.68-1.42 1.3-1.95 1.34-.5.04-.97.23-3.27-.68-2.77-1.09-4.53-3.93-4.67-4.11-.13-.18-1.11-1.48-1.11-2.82 0-1.34.7-2 .95-2.27.25-.27.54-.34.72-.34l.52.01c.17 0 .39-.06.61.47.24.56.79 1.92.86 2.06.07.14.11.3.02.48-.09.18-.13.29-.27.45-.13.16-.28.35-.4.47-.13.13-.27.28-.12.55.16.27.7 1.15 1.5 1.86 1.03.92 1.9 1.2 2.17 1.34.27.13.43.11.59-.07.16-.18.68-.79.86-1.06.18-.27.36-.23.61-.14.25.09 1.59.75 1.86.88.27.14.45.2.52.32.07.11.07.66-.17 1.34z"/></svg>'

CSS = r'''
:root{--bg:#F9F8F6;--ivory:#FBFAF7;--gold:#5E60CE;--ink:#111;--grey:#5A5A5A;--line:rgba(17,17,17,0.08);--ease:cubic-bezier(.22,.7,.2,1);}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--ink);font-family:'Inter',sans-serif;font-weight:500;line-height:1.6;-webkit-font-smoothing:antialiased;}
h1,h2,h3,h4{font-family:'Playfair Display',serif;font-weight:700;letter-spacing:0.01em;line-height:1.2;}
a{color:inherit;text-decoration:none;} img{display:block;max-width:100%;}
header{position:sticky;top:0;z-index:50;display:flex;align-items:center;justify-content:space-between;gap:20px;padding:14px 5vw;background:var(--gold);box-shadow:0 2px 18px rgba(17,17,17,0.08);}
.logo{display:flex;align-items:center;gap:11px;color:#fff;}
.logo img{width:42px;height:42px;border-radius:50%;object-fit:contain;}
.logo b{font-family:'Playfair Display',serif;font-size:21px;font-weight:800;display:block;line-height:1.1;}
.logo small{font-size:9px;letter-spacing:0.14em;text-transform:uppercase;color:rgba(255,255,255,0.8);}
header nav{display:flex;gap:24px;flex-wrap:wrap;}
header nav a{color:#fff;font-size:15px;}
header nav a.active,header nav a:hover{text-decoration:underline;text-underline-offset:6px;}
.wa-btn{display:inline-flex;align-items:center;gap:8px;background:#25D366;color:#fff;padding:11px 22px;border-radius:100px;font-size:13px;font-weight:600;white-space:nowrap;}
.wa-btn:hover{box-shadow:0 10px 24px rgba(37,211,102,0.35);}
@media(max-width:1100px){header nav{display:none;}}
.wrap{max-width:1180px;margin:0 auto;padding:0 5vw;}
.crumbs{font-size:13px;color:var(--grey);padding:22px 0 10px;display:flex;flex-wrap:wrap;gap:6px;}
.crumbs a:hover{color:var(--gold);} .crumbs span{opacity:.5;}
.hero{display:grid;grid-template-columns:1.15fr 1fr;gap:40px;align-items:center;padding:16px 0 40px;}
.hero-img{border-radius:12px;overflow:hidden;aspect-ratio:4/3;background:linear-gradient(135deg,#1c1a17,#3a3226);}
.hero-img img{width:100%;height:100%;object-fit:cover;}
.hero-ph{width:100%;height:100%;display:flex;align-items:center;justify-content:center;color:rgba(255,255,255,0.35);} .hero-ph svg{width:38%;}
.badges{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px;}
.badge{font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;padding:6px 12px;border-radius:100px;background:#111;color:#fff;}
.badge.alt{background:#EEEEFB;color:var(--gold);}
.hero h1{font-size:clamp(32px,4.4vw,52px);margin-bottom:10px;}
.loc{color:var(--grey);font-size:16px;margin-bottom:18px;}
.price{font-family:'Playfair Display',serif;font-size:30px;color:var(--gold);font-weight:700;margin-bottom:22px;}
.price small{display:block;font-family:'Inter',sans-serif;font-size:11px;letter-spacing:0.14em;text-transform:uppercase;color:var(--grey);font-weight:600;}
.ctas{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:22px;}
.btn2{display:inline-flex;align-items:center;gap:8px;padding:12px 22px;border-radius:100px;border:1px solid #111;font-size:13px;font-weight:600;}
.btn2:hover{background:#111;color:#fff;}
.tags{display:flex;flex-wrap:wrap;gap:8px;}
.tag{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:var(--grey);background:#fff;border:1px solid rgba(17,17,17,0.14);border-radius:100px;padding:6px 13px;}
.tag svg{width:12px;height:12px;opacity:.7;} .tag:hover{border-color:var(--gold);color:var(--gold);}
.stats{display:grid;grid-template-columns:repeat(5,1fr);background:#fff;border:1px solid var(--line);border-radius:12px;margin-bottom:46px;}
.stat{padding:20px 22px;border-left:1px solid var(--line);} .stat:first-child{border-left:0;}
.stat span{display:block;font-size:11px;letter-spacing:0.14em;text-transform:uppercase;color:var(--grey);font-weight:600;margin-bottom:6px;}
.stat strong{font-family:'Playfair Display',serif;font-size:18px;}
section.blk{margin-bottom:50px;}
.blk h2{font-size:clamp(24px,2.6vw,32px);margin-bottom:18px;}
.blk p.lead{color:#333;font-size:16px;max-width:860px;}
.points{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;}
.point{background:#fff;border:1px solid var(--line);border-radius:10px;padding:20px;display:flex;gap:14px;}
.point b{flex:0 0 32px;height:32px;border-radius:50%;background:var(--gold);color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden;}
.fact{padding:14px 18px;border-bottom:1px solid var(--line);border-right:1px solid var(--line);}
.fact span{display:block;font-size:11px;letter-spacing:0.12em;text-transform:uppercase;color:var(--grey);font-weight:600;}
.fact strong{font-weight:600;font-size:14.5px;}
.amen{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px;} .amen li{list-style:none;background:#fff;border:1px solid var(--line);border-radius:100px;padding:6px 14px;font-size:13px;}
.layouts{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px;}
.layout{background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden;display:flex;flex-direction:column;}
.layout figure{background:#f3f2ef;aspect-ratio:4/3;display:flex;align-items:center;justify-content:center;}
.layout figure img{width:100%;height:100%;object-fit:contain;}
.layout div{padding:16px 18px;} .layout h3{font-size:18px;margin-bottom:4px;}
.layout .meta{font-size:12px;color:var(--gold);font-weight:700;margin-bottom:8px;} .layout p{font-size:13.5px;color:var(--grey);}
.fits{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;}
.fit{background:#fff;border:1px solid var(--line);border-top:3px solid var(--gold);border-radius:10px;padding:20px;} .fit h3{font-size:17px;margin-bottom:6px;} .fit p{font-size:14px;color:var(--grey);}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;}
.card{background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden;transition:transform .3s var(--ease),box-shadow .3s;}
.card:hover{transform:translateY(-3px);box-shadow:0 14px 30px rgba(17,17,17,0.09);}
.card img{width:100%;aspect-ratio:16/10;object-fit:cover;} .card .noimg{display:block;aspect-ratio:16/10;background:linear-gradient(135deg,#1c1a17,#3a3226);} .card div{padding:14px 16px;}
.card h3{font-size:17px;} .card small{display:block;color:var(--grey);font-size:12px;} .card span{color:var(--gold);font-size:13px;font-weight:700;}
.art{display:block;background:#fff;border:1px solid var(--line);border-left:3px solid var(--gold);border-radius:8px;padding:16px 18px;}
.art small{font-size:11px;letter-spacing:0.1em;text-transform:uppercase;color:var(--gold);font-weight:700;} .art h3{font-size:16px;margin-top:4px;}
.cta{background:#111;color:#f2ede2;border-radius:14px;padding:40px;text-align:center;margin:10px 0 60px;}
.cta h2{color:#fff;margin-bottom:10px;} .cta p{opacity:.8;margin-bottom:20px;}
.note{font-size:12px;color:var(--grey);padding:0 0 30px;}
footer{background:#0C0C0C;color:#bbb;padding:34px 5vw;font-size:13px;text-align:center;}
footer a{color:#fff;}
.float-wa{position:fixed;right:22px;bottom:22px;width:56px;height:56px;border-radius:50%;background:#25D366;color:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 10px 26px rgba(0,0,0,0.25);z-index:60;}
@media(max-width:900px){.hero{grid-template-columns:1fr;gap:22px;}.price{font-size:24px;}.hero h1{font-size:34px;}.stats{grid-template-columns:repeat(2,1fr);}.stat{border-left:0;border-top:1px solid var(--line);}.stat:first-child{grid-column:1/-1;border-top:0;}.wa-btn span{display:none;}.wrap{padding:0 16px;}.cta{padding:28px 20px;}}
'''

NAV = [('', 'Home'), ('projects.html', 'View Projects'), ('compare.html', 'Compare Projects'), ('blog.html', 'News'),
       ('calculator.html', 'Calculator'), ('mm2h.html', 'MM2H 第二家园'), ('about-keith.html', 'About Keith')]


def page(i):
    p, tg, slug = P[i], TAGS[i], SLUGS[i]
    name, display = p['name'], tg[0]
    url = '%s/%s/%s.html' % (SITE, OUT, slug)
    photo = PHOTO.get(i, '')
    area = p['tag']
    title = '%s | Price, Floor Plan & Unit Types | Keith Nah' % display
    bits = [x for x in [p.get('price'), p.get('size'), p.get('rooms'), p.get('tenure')] if x]
    desc = '%s, %s: %s. Completion %s. See floor plans, unit types and nearby projects, and WhatsApp Keith Nah for the latest price.' % (
        display, p['loc'], ', '.join(bits), p.get('completion') or 'to be confirmed')
    msg = "Hi Keith, I'm interested in %s and would like to find out more." % name

    stats = ''.join('<div class="stat"><span>%s</span><strong>%s</strong></div>' % (E(k), E(v)) for k, v in [
        ('Starting Price', p.get('price')), ('Size', p.get('size')), ('Bedrooms', p.get('rooms')),
        ('Tenure', p.get('tenure')), ('Completion', p.get('completion'))] if v)
    tags = ''.join('<a class="tag" href="../projects.html?tag=%s#tagSection">%s%s</a>' % (E(t.replace(' ', '+')), TAG_SVG, E(t)) for t in tg)
    points = ''.join('<div class="point"><b>%d</b><p>%s</p></div>' % (n + 1, E(x)) for n, x in enumerate(p.get('selling_points') or []))
    facts = ''.join('<div class="fact"><span>%s</span><strong>%s</strong></div>' % (E(k), E(v)) for k, v in (p.get('details_extra') or {}).items())
    amen = ''.join('<li>%s</li>' % E(a) for a in (p.get('amenities') or []))
    layouts = ''.join(
        '<article class="layout"><figure>%s</figure><div><h3>%s</h3><p class="meta">%s</p><p>%s</p></div></article>' % (
            ('<img src="%s" alt="%s %s floor plan" loading="lazy">' % (E(up(l['img'])), E(display), E(l.get('type'))) if l.get('img') else ''),
            E(l.get('type')), E(' · '.join(x for x in [l.get('size'), l.get('rooms')] if x)), E(l.get('desc')))
        for l in (p.get('layouts') or []))
    fits = ''.join('<div class="fit"><h3>%s</h3><p>%s</p></div>' % (E(f.get('title')), E(f.get('desc'))) for f in (p.get('buyer_fit') or []))
    near = ''.join(
        '<a class="card" href="%s.html">%s<div><h3>%s</h3><small>%s</small><span>%s</span></div></a>' % (
            SLUGS[j], ('<img src="%s" alt="%s" loading="lazy">' % (E(up(PHOTO[j])), E(P[j]['name'])) if PHOTO.get(j) else '<i class="noimg"></i>'),
            E(P[j]['name']), E(P[j]['loc']), E(P[j].get('price')))
        for j in (p.get('nearby') or []) if 0 <= j < len(P) and j != i)
    arts = ''.join('<a class="art" href="../blog.html?article=%s"><small>%s</small><h3>%s</h3></a>' % (a, E(ART[a][0]), E(ART[a][1]))
                   for a in (OVR.get(name) or LOCA.get(area) or ['a4', 'a11', 'a20']) if a in ART)
    nav = ''.join('<a href="../%s"%s>%s</a>' % (h, ' class="active"' if h == 'projects.html' else '', E(t)) for h, t in NAV)

    ld = [{
        '@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Projects', 'item': SITE + '/projects.html'},
            {'@type': 'ListItem', 'position': 3, 'name': display, 'item': url}]},
        {'@context': 'https://schema.org', '@type': 'ApartmentComplex', 'name': display, 'url': url,
         'description': p.get('overview', ''), 'image': (SITE + '/' + photo) if photo else None,
         'address': {'@type': 'PostalAddress', 'streetAddress': p['loc'], 'addressCountry': 'MY'},
         'keywords': ', '.join(tg)}]
    ld[1] = {k: v for k, v in ld[1].items() if v}

    return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{kw}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
{ogimg}<link rel="icon" type="image/png" href="{icon}">
<link rel="apple-touch-icon" href="../apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;0,800;1,500&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{ld}</script>
<style>{css}</style>
</head>
<body>
<header>
  <a class="logo" href="../"><img src="{logo}" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Keith Nah Real Estate</small></span></a>
  <nav>{nav}</nav>
  <a class="wa-btn" href="{wa}" target="_blank" rel="noopener">{wasvg}<span>WhatsApp Keith</span></a>
</header>
<main class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="../">Home</a><span>›</span><a href="../projects.html">Projects</a><span>›</span><a href="../projects.html#{areahash}">{area}</a><span>›</span><strong>{display}</strong></nav>
  <div class="hero">
    <div class="hero-img">{heroimg}</div>
    <div>
      <div class="badges"><span class="badge">{status}</span><span class="badge alt">{area}</span><span class="badge alt">{ptype}</span></div>
      <h1>{display}</h1>
      <p class="loc">{loc}</p>
      <div class="price"><small>Starting Price</small>{price}</div>
      <div class="ctas"><a class="wa-btn" href="{wa}" target="_blank" rel="noopener">{wasvg}WhatsApp Keith</a><a class="btn2" href="../compare.html">Compare projects</a></div>
      <div class="tags">{tags}</div>
    </div>
  </div>
  <div class="stats">{stats}</div>
  <section class="blk"><h2>About {display}</h2><p class="lead">{overview}</p></section>
  {points_blk}
  {facts_blk}
  <section class="blk"><h2>Location</h2><p class="lead">{loctext}</p>{amen_blk}</section>
  {layouts_blk}
  {fits_blk}
  {near_blk}
  {arts_blk}
  <div class="cta"><h2>Want Keith's take on {display}?</h2><p>Ask for the latest price, available units and the full floor plans.</p><a class="wa-btn" href="{wa}" target="_blank" rel="noopener">{wasvg}WhatsApp Keith About This Project</a></div>
  <p class="note">Prices, sizes and availability are indicative and subject to change. Confirm current figures with Keith before making decisions.</p>
</main>
<footer>&copy; 2026 Keith Nah Real Estate · <a href="../projects.html">All projects</a> · <a href="../about-keith.html">About Keith</a></footer>
<a class="float-wa" href="{wa}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">{wasvg}</a>
<script src="../lead-tracker.js"></script>
</body>
</html>
'''.format(
        title=E(title), desc=E(desc), kw=E(', '.join(tg)), url=E(url), icon=E(up(ICON)), logo=E(up(LOGO)),
        ogimg=('<meta property="og:image" content="%s/%s">\n' % (SITE, E(photo))) if photo else '',
        ld=json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'), css=CSS, nav=nav, wa=E(wa(msg)), wasvg=WA_SVG,
        areahash=E(area.replace(' ', '%20').replace('&', '%26')), area=E(area), display=E(display),
        heroimg=('<img src="%s" alt="%s" fetchpriority="high">' % (E(up(photo)), E(display))) if photo else '<div class="hero-ph"><svg viewBox="0 0 200 200" fill="none" stroke="currentColor" stroke-width="2"><path d="M60 190V70l40-30 40 30v120z"/><path d="M60 90h80M60 110h80M60 130h80M60 150h80M85 190v-25h30v25"/></svg></div>',
        status=E(p.get('status')), ptype=E(TYPE.get(i, 'Residential')), loc=E(p['loc']), price=E(p.get('price')),
        tags=tags, stats=stats, overview=E(p.get('overview')), loctext=E(p.get('loc_text')),
        points_blk=('<section class="blk"><h2>Top Highlights</h2><div class="points">%s</div></section>' % points) if points else '',
        facts_blk=('<section class="blk"><h2>Project Details</h2><div class="facts">%s</div></section>' % facts) if facts else '',
        amen_blk=('<ul class="amen">%s</ul>' % amen) if amen else '',
        layouts_blk=('<section class="blk"><h2>%s Floor Plans &amp; Unit Types</h2><div class="layouts">%s</div></section>' % (E(display), layouts)) if layouts else '',
        fits_blk=('<section class="blk"><h2>Who Should Consider %s?</h2><div class="fits">%s</div></section>' % (E(display), fits)) if fits else '',
        near_blk=('<section class="blk"><h2>Nearby Projects</h2><div class="cards">%s</div></section>' % near) if near else '',
        arts_blk=('<section class="blk"><h2>Related Articles</h2><div class="cards">%s</div></section>' % arts) if arts else '')


def link_projects_page():
    """Link card titles and the popup to the new pages (idempotent)."""
    global src
    t = src
    t = re.sub(r'\n<script>var KN_SLUGS = .*?</script>', '', t, flags=re.S)
    t = re.sub(r'<h3><a class="proj-page-link" href="property/[^"]+" onclick="event.stopPropagation\(\)">(.*?)</a></h3>', r'<h3>\1</h3>', t)

    def card(m):
        k = int(m.group(1))
        return re.sub(r'<h3>(.*?)</h3>', lambda h: '<h3><a class="proj-page-link" href="property/%s.html" onclick="event.stopPropagation()">%s</a></h3>' % (SLUGS[k], h.group(1)), m.group(0), count=1)
    t, n = re.subn(r'data-idx="(\d+)" onclick="openDetailModal\(\1\)">.*?<h3>.*?</h3>', card, t, flags=re.S)
    assert n == len(P), n
    hook = "+ knTagsHtml(p)"
    if "knPageLink(p)" not in t:
        t = t.replace(hook, "+ knPageLink(p)\n      " + hook, 1)
    js = ('\n<script>var KN_SLUGS = %s;\nfunction knPageLink(p){ var s=KN_SLUGS[PROJECT_DETAILS.indexOf(p)]; '
          'return s ? \'<a class="pd-page-link" href="property/\'+s+\'.html">View full project page &rarr;</a>\' : \'\'; }</script>' % json.dumps(SLUGS))
    t = t.replace('<script src="lead-tracker.js"></script>', js.lstrip('\n') + '\n<script src="lead-tracker.js"></script>', 1)
    css = '  .proj-page-link{color:inherit;} .proj-page-link:hover{color:var(--gold);}\n  .pd-page-link{display:inline-block; margin:6px 0 4px; font:600 13px \'Inter\',sans-serif; color:var(--gold); border-bottom:1px solid currentColor;}\n'
    if '.pd-page-link{' not in t:
        t = t.replace('  /* ---------- PROJECT TAGS ---------- */', css + '  /* ---------- PROJECT TAGS ---------- */', 1)
    src = t
    open('projects.html', 'w', encoding='utf-8').write(t)


def write_sitemap():
    main = [('', '1.0', 'weekly'), ('projects.html', '0.9', 'weekly'), ('compare.html', '0.7', 'monthly'),
            ('blog.html', '0.8', 'weekly'), ('calculator.html', '0.7', 'monthly'), ('mm2h.html', '0.7', 'monthly'),
            ('about-keith.html', '0.8', 'monthly')]
    rows = [(SITE + '/' + u, pr, cf) for u, pr, cf in main] + [('%s/%s/%s.html' % (SITE, OUT, s), '0.8', 'monthly') for s in SLUGS]
    x = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    x += ''.join('  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>\n' % (E(u), TODAY, cf, pr) for u, pr, cf in rows)
    open('sitemap.xml', 'w', encoding='utf-8').write(x + '</urlset>\n')
    return len(rows)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for i in range(len(P)):
        open('%s/%s.html' % (OUT, SLUGS[i]), 'w', encoding='utf-8').write(page(i))
    link_projects_page()
    n = write_sitemap()
    print('wrote %d project pages in %s/, linked projects.html, sitemap has %d URLs' % (len(P), OUT, n))
