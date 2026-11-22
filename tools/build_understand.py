"""Understand Malaysia: one page per topic (understand/<slug>.html) plus an index (understand/index.html).

Texts: tools/i18n/understand.json (title, summary, short text and buyer note of each topic, shared with the
Foreign Buyers section) and tools/i18n/understand_pages_<lang>.json (key facts, sections, labels).
Photos: images/understand/<key>.jpg from Wikimedia Commons, credits in tools/understand_photos.json.
The pages translate themselves in the browser (data-hb); tools/build_lang_pages.js makes the language copies.
"""
import datetime
import html
import json
import os
import re
import sys
from urllib.parse import quote_plus

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.chdir(ROOT)
import hubs_data as HB
import site_header as SH

E = lambda s: html.escape(str(s if s is not None else ''), quote=True)
SITE = 'https://keithnah.com/'
LANGS = ['en', 'zh-CN', 'ms', 'ja', 'ko']

BASE = json.load(open(os.path.join(HERE, 'i18n', 'understand.json'), encoding='utf-8'))
T = {}
for l in LANGS:
    T[l] = dict(BASE[l])
    T[l].update(json.load(open(os.path.join(HERE, 'i18n', 'understand_pages_%s.json' % l), encoding='utf-8')))
try:
    import opencc
    _cc = opencc.OpenCC('s2tw').convert
    T['zh-TW'] = {k: _cc(v) for k, v in T['zh-CN'].items()}
except Exception:
    T['zh-TW'] = dict(T['zh-CN'])
EN = T['en']
PHOTOS = json.load(open(os.path.join(HERE, 'understand_photos.json'), encoding='utf-8'))
LIC = {'CC BY-SA 4.0': 'https://creativecommons.org/licenses/by-sa/4.0/', 'CC BY-SA 3.0': 'https://creativecommons.org/licenses/by-sa/3.0/',
       'CC BY-SA 2.0': 'https://creativecommons.org/licenses/by-sa/2.0/', 'CC BY 4.0': 'https://creativecommons.org/licenses/by/4.0/',
       'CC BY 2.0': 'https://creativecommons.org/licenses/by/2.0/', 'CC0': 'https://creativecommons.org/publicdomain/zero/1.0/'}

# (number, slug, photo key, related links, official sources)
SRC = {'dosm': ('Department of Statistics Malaysia', 'https://www.dosm.gov.my'),
       'gov': ('Malaysian Government portal', 'https://www.malaysia.gov.my'),
       'unesco': ('UNESCO: Melaka and George Town', 'https://whc.unesco.org/en/list/1223'),
       'arkib': ('National Archives of Malaysia', 'https://www.arkib.gov.my'),
       'dbp': ('Dewan Bahasa dan Pustaka', 'https://www.dbp.gov.my'),
       'moe': ('Ministry of Education', 'https://www.moe.gov.my'),
       'halal': ('JAKIM Halal Malaysia', 'https://www.halal.gov.my'),
       'tour': ('Tourism Malaysia', 'https://www.malaysia.travel'),
       'kabinet': ('Cabinet Division: public holidays', 'https://www.kabinet.gov.my'),
       'rapid': ('Rapid KL', 'https://myrapid.com.my'),
       'ktmb': ('KTMB', 'https://www.ktmb.com.my'),
       'klia': ('KLIA Ekspres', 'https://www.kliaekspres.com'),
       'bnm': ('Bank Negara Malaysia', 'https://www.bnm.gov.my'),
       'moh': ('Ministry of Health', 'https://www.moh.gov.my'),
       'imi': ('Immigration Department of Malaysia', 'https://www.imi.gov.my'),
       'met': ('Malaysian Meteorological Department', 'https://www.met.gov.my'),
       'mm2h': ('MM2H (official)', 'https://mm2h.gov.my')}
A = lambda slug, name: ('area/%s.html' % slug, None, name)   # area pages keep the English place name
R = lambda href, key: (href, key, None)
TOPICS = [
    (1, 'malaysia-at-a-glance', 'glance', [R('foreign-buyers.html', 'r_fb'), A('kuala-lumpur', 'Kuala Lumpur'), A('penang', 'Penang'), A('johor', 'Johor')], ['dosm', 'gov']),
    (2, 'history', 'history', [A('george-town', 'George Town'), A('melaka', 'Melaka'), A('kuala-lumpur', 'Kuala Lumpur')], ['unesco', 'arkib']),
    (3, 'people-and-religion', 'people', [R('foreign-buyers.html', 'r_fb'), R('projects.html', 'r_proj')], ['dosm', 'gov']),
    (4, 'languages', 'languages', [R('foreign-buyers.html', 'r_fb'), R('projects.html', 'r_proj')], ['dbp', 'moe']),
    (5, 'food', 'food', [A('bukit-bintang', 'Bukit Bintang'), A('george-town', 'George Town'), A('kuala-lumpur', 'Kuala Lumpur')], ['halal', 'tour']),
    (6, 'festivals-and-holidays', 'festivals', [R('foreign-buyers.html', 'r_fb'), R('calculator.html', 'r_calc')], ['kabinet', 'tour']),
    (7, 'getting-around', 'transport', [R('station/index.html', 'r_station'), R('projects.html', 'r_proj')], ['rapid', 'ktmb', 'klia']),
    (8, 'shopping-malls', 'malls', [A('bukit-bintang', 'Bukit Bintang'), A('bukit-jalil', 'Bukit Jalil'), A('jb-city-centre', 'JB City Centre')], ['tour']),
    (9, 'places-to-visit', 'places', [A('george-town', 'George Town'), A('melaka', 'Melaka'), A('kota-kinabalu', 'Kota Kinabalu')], ['tour', 'unesco']),
    (10, 'cost-of-living', 'cost', [R('calculator.html', 'r_calc'), R('foreign-buyers.html', 'r_fb')], ['dosm', 'bnm']),
    (11, 'schools-and-healthcare', 'schools', [A('mont-kiara', 'Mont Kiara'), R('projects.html', 'r_proj')], ['moe', 'moh']),
    (12, 'visas-safety-weather', 'visas', [R('mm2h.html', 'r_mm2h'), R('foreign-buyers.html', 'r_fb')], ['imi', 'met', 'mm2h']),
]
ICONS = {  # simple line icons for the key facts
    1: '<path d="M12 2a10 10 0 100 20 10 10 0 000-20zM2 12h20M12 2c3 3 3 17 0 20M12 2c-3 3-3 17 0 20"/>',
    2: '<path d="M4 21h16M6 21V10M10 21V10M14 21V10M18 21V10M3 10l9-6 9 6"/>',
    3: '<path d="M9 11a4 4 0 100-8 4 4 0 000 8zM2 21v-1a6 6 0 0112 0v1M17 11a3 3 0 100-6M22 21v-1a5 5 0 00-4-5"/>',
    4: '<path d="M4 5h16v11H9l-5 4z"/>',
}

WA = 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0'


def tx(key, tag='span', cls='', attrs=''):
    return '<%s data-hb="%s"%s%s>%s</%s>' % (tag, key, (' class="%s"' % cls) if cls else '', (' ' + attrs) if attrs else '', E(EN[key]), tag)


def credit(k):
    if k not in PHOTOS:
        return ''
    p = PHOTOS[k]
    lic = p['lic']
    name = re.sub(r'<[^>]+>', '', p['artist']).strip()
    lic_html = '<a href="%s" target="_blank" rel="noopener license">%s</a>' % (LIC[lic], E(lic)) if lic in LIC else E(lic)
    return '%s: <a href="%s" target="_blank" rel="noopener">%s</a>, Wikimedia Commons, %s' % (tx('ui_photo'), E(p['page']), E(name), lic_html)


CSS = '''
:root{--ink:#15142b;--grey:#55546b;--line:rgba(21,20,43,.1);--gold:#5E60CE;--bg:#F9F8F6;--soft:#f3f1fa}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:Inter,sans-serif;background:var(--bg);color:var(--ink);line-height:1.65}a{color:inherit;text-decoration:none}img{display:block;max-width:100%}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif;line-height:1.2}.w{max-width:1100px;margin:0 auto;padding:0 5vw}
.eb{display:block;font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);font-weight:700}
.crumb{font-size:13px;color:var(--grey);margin:0 0 16px;display:flex;flex-wrap:wrap;gap:6px}.crumb a{color:var(--gold);font-weight:600}
.uh{padding:118px 0 0}.uh h1{font-size:clamp(30px,4.6vw,50px);margin:10px 0 10px}.uh .lead{font-size:17.5px;color:var(--grey);max-width:760px}
.uph{margin:26px 0 0;border-radius:24px;overflow:hidden;position:relative;background:#ddd;aspect-ratio:21/9}
.uph img{width:100%;height:100%;object-fit:cover}.uph .num{position:absolute;left:18px;top:16px;background:rgba(17,17,17,.72);color:#fff;font:700 12px Inter,sans-serif;letter-spacing:.14em;padding:6px 12px;border-radius:100px}
.cred{font-size:11.5px;color:#77768c;margin-top:8px}.cred a{text-decoration:underline}
.ug{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:36px;padding:34px 0 10px;align-items:start}
.ub p.in{font-size:17px;line-height:1.75;color:#24233a;margin-bottom:8px}
.ub h2{font-size:clamp(22px,2.6vw,28px);margin:30px 0 10px}.ub p{font-size:16px;line-height:1.8;color:#2f2e45}
.buy{margin:30px 0 0;background:#1d1b4f;color:#fff;border-radius:20px;padding:22px 24px}.buy b{display:block;font:700 12px Inter,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:#c9caff;margin-bottom:6px}.buy p{color:#fff;font-size:16px}
.kf{position:sticky;top:96px;background:#fff;border:1px solid var(--line);border-radius:20px;padding:20px 20px 8px;box-shadow:0 14px 34px rgba(29,27,79,.07)}
.kf h3{font:700 12px Inter,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);margin-bottom:12px}
.kf div{display:flex;gap:12px;padding:12px 0;border-top:1px solid var(--line)}.kf svg{flex:0 0 34px;width:34px;height:34px;padding:7px;border-radius:10px;background:var(--soft);stroke:var(--gold);fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.kf small{display:block;font-size:12px;font-weight:700;color:#6b6a80;text-transform:uppercase;letter-spacing:.06em}.kf strong{display:block;font-size:15.5px;color:var(--ink);line-height:1.4}
.rel{margin-top:16px;background:#fff;border:1px solid var(--line);border-radius:20px;padding:18px 20px}.rel h3{font:700 12px Inter,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);margin-bottom:8px}
.rel a{display:block;padding:8px 0;border-top:1px solid var(--line);font-weight:600;font-size:14.5px}.rel a:after{content:" →";color:var(--gold)}.rel a:hover{color:var(--gold)}
.src{margin:34px 0 0;padding:18px 20px;border-radius:16px;background:var(--soft);font-size:14px;color:var(--grey)}.src b{color:var(--ink);display:block;margin-bottom:4px}
.src a{color:var(--gold);font-weight:600;margin-right:14px;display:inline-block}
.pn{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:34px 0 10px}.pn a{display:flex;align-items:center;gap:14px;background:#fff;border:1px solid var(--line);border-radius:18px;padding:12px;transition:border-color .2s,box-shadow .2s}
.pn a:hover{border-color:var(--gold);box-shadow:0 12px 26px rgba(29,27,79,.08)}.pn img{width:84px;height:62px;border-radius:12px;object-fit:cover;flex:0 0 84px}.pn small{display:block;color:var(--gold);font-weight:700;font-size:11.5px;letter-spacing:.12em;text-transform:uppercase}.pn b{font:700 16px 'Playfair Display',serif}
.pn a.nx{flex-direction:row-reverse;text-align:right}
.ul-h{margin:44px 0 14px;font-size:24px}
.ul{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.ul a,.ux a{display:block;background:#fff;border:1px solid var(--line);border-radius:18px;overflow:hidden;transition:transform .25s,box-shadow .25s}.ul a:hover,.ux a:hover{transform:translateY(-3px);box-shadow:0 16px 32px rgba(29,27,79,.12)}
.ul img{width:100%;aspect-ratio:3/2;object-fit:cover}.ul span{display:block;padding:10px 12px 12px;font:700 14.5px Inter,sans-serif}.ul a.on{outline:2px solid var(--gold)}
.ux{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:26px}.ux img{width:100%;aspect-ratio:3/2;object-fit:cover}.ux .b{padding:16px 18px 18px}.ux i{font:700 11.5px Inter,sans-serif;letter-spacing:.14em;color:var(--gold);font-style:normal}
.ux h2{font-size:20px;margin:4px 0 6px}.ux p{font-size:14px;color:var(--grey)}.ux em{display:inline-block;margin-top:10px;color:var(--gold);font-weight:700;font-size:13.5px;font-style:normal}
.cta{background:#111;color:#fff;border-radius:22px;padding:30px;text-align:center;margin:40px 0 60px}.cta h2{color:#fff;margin-bottom:8px;font-size:clamp(22px,3vw,28px)}.cta p{color:#cfcfe0}
.cta a{display:inline-block;margin-top:14px;background:#25D366;color:#fff;padding:12px 24px;border-radius:100px;font-weight:700}
footer{border-top:1px solid var(--line);padding:26px 5vw;font-size:13px;color:var(--grey);text-align:center}
@media(max-width:900px){.ug{grid-template-columns:1fr;gap:10px}.ug aside{order:-1;margin-bottom:14px}.kf{position:static}.ul{grid-template-columns:repeat(3,1fr)}.ux{grid-template-columns:1fr 1fr}}
@media(max-width:620px){.uh{padding-top:100px}.uph{aspect-ratio:4/3;border-radius:18px}.ul{grid-template-columns:1fr 1fr}.ux{grid-template-columns:1fr}.pn{grid-template-columns:1fr}.pn img{width:64px;height:50px;flex-basis:64px}.ub p{font-size:15.5px}}
'''


def shell(rel, title, desc, body, ld, img):
    url = SITE + rel.replace('index.html', '')
    page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s">
<meta property="og:type" content="article">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:url" content="%s">
<meta property="og:image" content="%s">
<link rel="icon" type="image/png" href="../images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@500;700&display=swap" rel="stylesheet">
<script type="application/ld+json">%s</script>
<style>%s</style>
</head>
<body>
<header>
  <a class="logo" href="../"><img src="../images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Malaysia Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="%s" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
%s
<footer>&copy; 2026 Keith Nah Real Estate · <a href="../foreign-buyers.html">Foreign Buyers</a> · <a href="./">Understand Malaysia</a> · <a href="../projects.html">All projects</a> · <a href="../privacy-policy.html">Privacy Policy</a></footer>
<script src="../lead-tracker.js"></script>
%s
</body>
</html>
''' % (E(title), E(desc), url, E(title), E(desc), url, SITE + img, json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'), CSS,
       E(WA % quote_plus('(KNRE) Hi Keith, I am reading your Understand Malaysia guide and would like to ask about buying in Malaysia.')),
       body, HB.JS % json.dumps(T, ensure_ascii=False).replace('</', '<\\/'))
    page = SH.apply(page, '../', 'foreign-buyers.html')
    os.makedirs(os.path.dirname(rel), exist_ok=True)
    open(rel, 'w', encoding='utf-8').write(page)
    return url


def crumbs(*items):
    out = '<nav class="crumb" aria-label="Breadcrumb">'
    for n, (href, inner) in enumerate(items):
        out += ('<span>›</span>' if n else '') + ('<a href="%s">%s</a>' % (href, inner) if href else '<span>%s</span>' % inner)
    return out + '</nav>'


def bc_ld(*items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': n + 1, 'name': name, 'item': url} for n, (name, url) in enumerate(items)]}


def cta():
    return '<div class="cta">%s%s<a href="%s" target="_blank" rel="noopener">%s</a></div>' % (
        tx('ui_cta_h', 'h2'), tx('ui_cta_p', 'p'),
        E(WA % quote_plus('(KNRE) Hi Keith, I am reading your Understand Malaysia guide and would like to ask about buying in Malaysia.')), tx('ui_cta_b'))


written = []
today = datetime.date.today().isoformat()
for idx, (n, slug, pk, rel, srcs) in enumerate(TOPICS):
    img = 'images/understand/%s.jpg' % pk
    facts = ''.join('<div><svg viewBox="0 0 24 24" aria-hidden="true">%s</svg><span>%s%s</span></div>' % (
        ICONS[i], tx('p%dk%dl' % (n, i), 'small'), tx('p%dk%dv' % (n, i), 'strong')) for i in range(1, 5))
    secs = ''.join(tx('p%ds%dh' % (n, i), 'h2') + tx('p%ds%dp' % (n, i), 'p') for i in range(1, 4))
    rels = ''.join('<a href="../%s">%s</a>' % (h, tx(k) if k else E(name)) for h, k, name in rel)
    src = ''.join('<a href="%s" target="_blank" rel="noopener">%s</a>' % (SRC[s][1], E(SRC[s][0])) for s in srcs)
    pv, nx = TOPICS[idx - 1], TOPICS[(idx + 1) % len(TOPICS)]
    pn = ''.join('<a class="%s" href="%s.html"><img src="../images/understand/%s.jpg" alt="" loading="lazy" width="84" height="62"><span>%s%s</span></a>' % (
        c, t[1], t[2], tx(lab, 'small'), tx('t%dh' % t[0], 'b')) for c, lab, t in (('pv', 'ui_prev', pv), ('nx', 'ui_next', nx)))
    grid = ''.join('<a href="%s.html"%s><img src="../images/understand/%s.jpg" alt="" loading="lazy" width="300" height="200">%s</a>' % (
        t[1], ' class="on" aria-current="page"' if t[0] == n else '', t[2], tx('t%dh' % t[0])) for t in TOPICS)
    body = '''<main>
<section class="uh"><div class="w">%s%s%s%s
<figure class="uph"><img src="../%s" alt="%s" width="1400" height="933" fetchpriority="high"><span class="num">%02d / 12</span></figure>
<p class="cred">%s</p></div></section>
<div class="w"><div class="ug"><article class="ub">%s%s<div class="buy">%s%s</div>
<div class="src">%s%s<br>%s</div></article>
<aside><div class="kf">%s%s</div><div class="rel">%s%s</div></aside></div>
<nav class="pn" aria-label="More topics">%s</nav>
%s<div class="ul">%s</div>
%s</div>
</main>''' % (crumbs(('../foreign-buyers.html', tx('ui_back')), ('./', tx('ui_eb')), (None, tx('t%dh' % n))),
              tx('ui_eb', 'span', 'eb'), tx('t%dh' % n, 'h1'), tx('t%ds' % n, 'p', 'lead'),
              img, E(EN['t%dh' % n]), n, credit(pk),
              tx('t%db' % n, 'p', 'in'), secs, tx('ui_buy', 'b'), tx('t%dy' % n, 'p'),
              tx('ui_src', 'b'), tx('ui_src_p'), src,
              tx('ui_facts', 'h3'), facts, tx('ui_rel', 'h3'), rels,
              pn, tx('ui_all', 'h2', 'ul-h'), grid, cta())
    title = '%s | Understand Malaysia | Keith Nah' % EN['t%dh' % n]
    desc = EN['t%ds' % n] + ' ' + EN['t%db' % n]
    desc = desc if len(desc) <= 158 else desc[:155].rsplit(' ', 1)[0] + '…'
    url = SITE + 'understand/%s.html' % slug
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Article', 'headline': EN['t%dh' % n], 'description': desc, 'image': SITE + img, 'url': url, 'inLanguage': 'en',
         'author': {'@type': 'Person', 'name': 'Keith Nah'}, 'publisher': {'@type': 'Organization', 'name': 'Keith Nah Real Estate'}},
        bc_ld(('Foreign Buyers', SITE + 'foreign-buyers.html'), ('Understand Malaysia', SITE + 'understand/'), (EN['t%dh' % n], url))]}
    written.append(shell('understand/%s.html' % slug, title, desc, body, ld, img))

# ---- index ----
cards = ''.join('<a href="%s.html"><img src="../images/understand/%s.jpg" alt="" loading="lazy" width="420" height="280"><div class="b"><i>%02d</i>%s%s%s</div></a>' % (
    slug, pk, n, tx('t%dh' % n, 'h2'), tx('t%ds' % n, 'p'), tx('ui_open', 'em')) for n, slug, pk, _, _ in TOPICS)
body = '''<main>
<section class="uh"><div class="w">%s%s%s%s</div></section>
<div class="w"><div class="ux">%s</div>%s</div>
</main>''' % (crumbs(('../foreign-buyers.html', tx('ui_back')), (None, tx('ui_eb'))), tx('ui_eb', 'span', 'eb'), tx('ui_idx_h', 'h1'), tx('ui_idx_p', 'p', 'lead'), cards, cta())
desc = EN['ui_idx_p']
ld = {'@context': 'https://schema.org', '@graph': [
    {'@type': 'CollectionPage', 'name': EN['ui_idx_h'], 'description': desc, 'url': SITE + 'understand/'},
    {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': SITE + 'understand/%s.html' % t[1], 'name': EN['t%dh' % t[0]]} for i, t in enumerate(TOPICS)]},
    bc_ld(('Foreign Buyers', SITE + 'foreign-buyers.html'), ('Understand Malaysia', SITE + 'understand/'))]}
written.insert(0, shell('understand/index.html', 'Understand Malaysia: 12 Topics for New Buyers | Keith Nah', desc, body, ld, 'images/understand/glance.jpg'))

# ---- sitemap ----
if os.path.exists('sitemap.xml'):
    sm = open('sitemap.xml', encoding='utf-8').read()
    sm = re.sub(r'  <url>\n    <loc>https://keithnah.com/understand/[^<]*</loc>.*?</url>\n', '', sm, flags=re.S)
    sm = sm.replace('</urlset>', ''.join('  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>\n' % (u, today) for u in written) + '</urlset>')
    open('sitemap.xml', 'w', encoding='utf-8').write(sm)
print('understand: %d pages' % len(written))
