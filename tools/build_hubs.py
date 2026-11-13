"""Developer pages (developer/), station pages (station/) and head-to-head comparisons (vs/).

Built from tools/hubs.json (written by tools/build_project_pages.py) and the project details,
so they update whenever projects change. Also adds the entry blocks on projects.html, compare.html
and the area pages, and lists every page in sitemap.xml. Texts for all 6 languages are in
tools/hubs_data.py; the language copies are made by tools/build_lang_pages.js.
"""
import datetime
import glob
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.chdir(ROOT)
import hubs_data as HB
import site_header as SH

E = lambda s: html.escape(str(s if s is not None else ''), quote=True)
Y = datetime.date.today().year
TX = HB.tx
src = open('projects.html', encoding='utf-8').read()


def js_json(name):
    i = src.index('const %s = ' % name) if ('const %s = ' % name) in src else src.index('var %s = ' % name)
    i = src.index('=', i) + 1
    return json.JSONDecoder().raw_decode(src[i:].lstrip())[0]


P = js_json('PROJECT_DETAILS')
IDX = json.load(open(os.path.join(HERE, 'project_index.json'), encoding='utf-8'))
HUBS = json.load(open(os.path.join(HERE, 'hubs.json'), encoding='utf-8'))
WA = 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0'


def wa(msg):
    from urllib.parse import quote_plus
    return WA % quote_plus('(KNRE) ' + msg)


def photo(i):
    try:
        t = open('property/%s.html' % IDX[i]['slug'], encoding='utf-8').read()
        m = re.search(r'og:image" content="https://keithnah\.com/([^"]+)"', t)
        return '../' + m.group(1) if m else ''
    except OSError:
        return ''


def plain_places(ix):
    st = []
    for i in ix:
        s = IDX[i]['state'] or IDX[i]['area']
        if s and s not in st:
            st.append(s)
    return st


CSS = '''
:root{--ink:#15142b;--grey:#5f5e74;--line:rgba(21,20,43,.09);--gold:#5E60CE;--bg:#F9F8F6;}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:Inter,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6}a{color:inherit;text-decoration:none}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif;line-height:1.2}.w{max-width:1180px;margin:0 auto;padding:0 5vw}
.hero{padding:130px 0 34px;background:linear-gradient(180deg,#f3f1fa,#F9F8F6)}.eb{display:block;font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);font-weight:700}
.hero h1{font-size:clamp(28px,4.4vw,48px);margin:10px 0 12px}.hero p{color:var(--grey);max-width:760px;font-size:16px}
.crumb{font-size:13px;color:var(--grey);margin-bottom:18px;display:flex;flex-wrap:wrap;gap:6px}.crumb a{color:var(--gold);font-weight:600}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:24px}
.st{background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px 18px}.st b{display:block;font:700 26px 'Playfair Display',serif;color:var(--gold)}.st small{color:var(--grey);font-weight:600;font-size:12.5px}
.sec{padding:30px 0}.sec h2{font-size:clamp(23px,3vw,31px);margin-bottom:16px}.sec h3.grp{font-size:20px;margin:22px 0 12px}.sec h3.grp small{color:var(--grey);font:600 13px Inter,sans-serif}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px}.chip{background:#fff;border:1px solid var(--line);border-radius:100px;padding:8px 16px;font-size:13px;font-weight:700;cursor:pointer;font-family:Inter,sans-serif;color:var(--ink)}.chip.on{background:var(--ink);color:#fff}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px}
.card{display:block;background:#fff;border:1px solid var(--line);border-radius:18px;overflow:hidden;box-shadow:0 10px 26px rgba(29,27,79,.06);transition:transform .25s,box-shadow .25s}
.card:hover{transform:translateY(-3px);box-shadow:0 16px 34px rgba(29,27,79,.12)}.card img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;background:#eee}
.card .cb{padding:14px 16px 16px}.card h3{font-size:19px}.card small{color:var(--grey);font-size:12.5px;display:block;margin:2px 0 8px}.card .pr{color:var(--gold);font-weight:700;font-size:14px}
.card .tg{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}.card .tg span{font-size:11.5px;font-weight:700;background:#f3f1fa;color:var(--gold);padding:3px 9px;border-radius:100px}
.walk{font-size:13px;color:#1d1b4f;background:#f6f5fc;border-radius:10px;padding:8px 10px;margin-top:10px;font-weight:600}
.faq details{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 18px;margin-bottom:10px}.faq summary{font-weight:700;cursor:pointer}.faq p{color:var(--grey);margin-top:8px;font-size:14.5px}
.cta{background:#111;color:#fff;border-radius:22px;padding:30px;text-align:center;margin:24px 0 60px}.cta h2{color:#fff;margin-bottom:8px;font-size:clamp(22px,3vw,28px)}.cta p{color:#cfcfe0}
.cta a{display:inline-block;margin-top:14px;background:#25D366;color:#fff;padding:12px 24px;border-radius:100px;font-weight:700}
.vs{display:grid;grid-template-columns:1fr auto 1fr;gap:16px;align-items:center;margin-top:24px}.vs .card img{aspect-ratio:16/10}
.vsb{font:800 22px 'Playfair Display',serif;color:#fff;background:var(--gold);width:58px;height:58px;border-radius:50%;display:flex;align-items:center;justify-content:center}
.tbl{overflow-x:auto}table{width:100%;border-collapse:collapse;background:#fff;border-radius:16px;overflow:hidden;border:1px solid var(--line);font-size:14.5px}
th,td{padding:12px 14px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}thead th{background:#1d1b4f;color:#fff;font-size:13px}
tbody th{color:var(--grey);font-weight:600;width:24%}td.win{background:#eefaf2;font-weight:700}td.win:after{content:" ✓";color:#1f9d55}
.note{color:var(--grey);font-size:12.5px;margin-top:8px}
.diff li{background:#fff;border:1px solid var(--line);border-left:4px solid var(--gold);border-radius:10px;padding:12px 14px;margin-bottom:8px;list-style:none;font-size:14.5px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}.box{background:#fff;border:1px solid var(--line);border-radius:16px;padding:18px}.box h3{font-size:18px;margin-bottom:8px}
.box li{margin-left:18px;font-size:14.5px;color:#3d3c55}.box a{display:inline-block;margin-top:10px;color:var(--gold);font-weight:700;font-size:14px}
.idx{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}.idx a{display:block;background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px 18px;font-weight:700}
.idx a small{display:block;color:var(--gold);font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;margin-bottom:4px}.idx a:hover{border-color:var(--gold)}
footer{border-top:1px solid var(--line);padding:26px 5vw;font-size:13px;color:var(--grey);text-align:center}
@media(max-width:720px){.vs{grid-template-columns:1fr}.vsb{margin:0 auto}.two{grid-template-columns:1fr}table{font-size:13px}th,td{padding:10px}}
'''


def shell(rel, title, desc, body, ld, msg):
    url = 'https://keithnah.com/' + rel.replace('index.html', '')
    page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s">
<meta property="og:type" content="website">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:url" content="%s">
<link rel="icon" type="image/png" href="../images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@500;700&display=swap" rel="stylesheet">
<script type="application/ld+json">%s</script>
<style>%s%s</style>
</head>
<body>
<header>
  <a class="logo" href="../"><img src="../images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Malaysia Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="%s" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
%s
<footer>&copy; 2026 Keith Nah Real Estate · <a href="../projects.html">All projects</a> · <a href="../developer/">Developers</a> · <a href="../station/">Near a station</a> · <a href="../vs/">Comparisons</a> · <a href="../privacy-policy.html">Privacy Policy</a></footer>
<script src="../lead-tracker.js"></script>
%s
</body>
</html>
''' % (E(title), E(desc), url, E(title), E(desc), url, json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'), CSS, HB.CSS, E(wa(msg)), body, HB.js())
    page = SH.apply(page, '../', 'compare.html' if rel.startswith('vs/') else 'projects.html')
    os.makedirs(os.path.dirname(rel), exist_ok=True)
    open(rel, 'w', encoding='utf-8').write(page)
    return url


def crumbs(*items):
    out = '<nav class="crumb" aria-label="Breadcrumb">'
    for n, (href, inner) in enumerate(items):
        out += ('<span>›</span>' if n else '') + ('<a href="%s">%s</a>' % (href, inner) if href else '<span>%s</span>' % inner)
    return out + '</nav>'


def bc_ld(*items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': n + 1, 'name': name, 'item': url} for n, (name, url) in enumerate(items)]}


def card(i, extra=''):
    p = P[i]
    tg = ''.join(HB.val(x) for x in [(p.get('tenure') or '').split(' (')[0], p.get('status')] if x)
    img = photo(i)
    return ('<a class="card" href="../property/%s.html">%s<div class="cb"><h3>%s</h3><small>%s</small>%s<div class="tg">%s</div>%s</div></a>') % (
        IDX[i]['slug'], ('<img src="%s" alt="%s" loading="lazy">' % (E(img), E(p['name']))) if img else '', E(p['name']), E(p.get('loc')), HB.val(p.get('price'), cls='pr'), tg, extra)


def item_list(name, ix):
    return {'@context': 'https://schema.org', '@type': 'ItemList', 'name': name, 'itemListElement': [
        {'@type': 'ListItem', 'position': n + 1, 'url': 'https://keithnah.com/property/%s.html' % IDX[i]['slug'], 'name': P[i]['name']} for n, i in enumerate(ix)]}


written = []
home = ('../', TX('home'))

# ---------- developer pages ----------
for d, info in HUBS['developers'].items():
    ix = info['ix']
    places = plain_places(ix)
    prices = [(HB.price(P[i].get('price')), i) for i in ix if HB.price(P[i].get('price'))]
    lo = min(prices) if prices else None
    fh = sum(1 for i in ix if 'freehold' in (P[i].get('tenure') or '').lower())
    states = []
    for i in ix:
        s = IDX[i]['state']
        if s not in states:
            states.append(s)
    groups = ''
    for s in states:
        mine = [i for i in ix if IDX[i]['state'] == s]
        groups += '<div class="grp" data-st="%s"><h3 class="grp">%s <small>· %s</small></h3><div class="cards">%s</div></div>' % (
            E(s), E(s), TX('n_proj', n=len(mine)), ''.join(card(i) for i in mine))
    chips = '<button class="chip on" data-f="">%s</button>' % TX('all') + ''.join('<button class="chip" data-f="%s">%s</button>' % (E(s), E(s)) for s in states) if len(states) > 1 else ''
    filt = ('<script>document.querySelectorAll(".chip[data-f]").forEach(function(b){b.addEventListener("click",function(){var f=b.getAttribute("data-f");'
            'document.querySelectorAll(".chip[data-f]").forEach(function(x){x.classList.toggle("on",x===b)});document.querySelectorAll(".grp[data-st]").forEach(function(g){g.style.display=!f||g.getAttribute("data-st")===f?"":"none"});});});</script>') if chips else ''
    pl = ', '.join(places)
    faq = [(TX('dq1', tag='summary', d=d, y=Y), TX('da1', tag='p', n=len(ix), d=d, places=pl), 'dq1', 'da1', dict(d=d, y=Y), dict(n=len(ix), d=d, places=pl))]
    if lo:
        faq.append((TX('dq2', tag='summary', d=d), TX('da2', tag='p', p=HB.rm(lo[0]), name=P[lo[1]]['name']), 'dq2', 'da2', dict(d=d), dict(p=HB.rm(lo[0]), name=P[lo[1]]['name'])))
    faq.append((TX('dq3', tag='summary', d=d), TX('da3', tag='p', f=fh, n=len(ix), d=d), 'dq3', 'da3', dict(d=d), dict(f=fh, n=len(ix), d=d)))
    fill = lambda k, v: re.sub(r'\{(\w+)\}', lambda m: str(v.get(m.group(1), m.group(0))), HB.T['en'][k])
    body = '''<main><section class="hero"><div class="w">%s%s%s%s
<div class="stats"><div class="st"><b>%d</b>%s</div><div class="st"><b>%d</b>%s</div>%s<div class="st"><b>%d</b>%s</div></div></div></section>
<section class="sec"><div class="w">%s<div class="chips">%s</div>%s</div></section>
<section class="sec faq"><div class="w">%s%s</div></section>
<section class="w"><div class="cta">%s%s<a href="%s" target="_blank" rel="noopener">WhatsApp Keith</a></div></section></main>%s''' % (
        crumbs(home, ('index.html', TX('dev_crumb')), (None, E(d))), TX('dev_eb', cls='eb', y=Y), TX('dev_h1', tag='h1', d=d, y=Y), TX('dev_p', tag='p', d=d, places=pl),
        len(ix), TX('st_projects', tag='small'), len(states), TX('st_states', tag='small'),
        ('<div class="st"><b>%s</b>%s</div>' % (HB.rm(lo[0]), TX('st_low', tag='small'))) if lo else '', fh, TX('st_fh', tag='small'),
        TX('dev_all', tag='h2', d=d), chips, groups,
        TX('faq_dev', tag='h2', d=d), ''.join('<details%s>%s%s</details>' % (' open' if n == 0 else '', q, a) for n, (q, a, *_r) in enumerate(faq)),
        TX('dev_cta', tag='h2', d=d), TX('cta_p', tag='p'), E(wa('Hi Keith, I am looking at %s projects.' % d)), filt)
    ld = [bc_ld(('Home', 'https://keithnah.com/'), ('Developers', 'https://keithnah.com/developer/'), (d, 'https://keithnah.com/developer/%s.html' % info['slug'])),
          item_list('%s new launch projects' % d, ix),
          {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': fill(qk, qv), 'acceptedAnswer': {'@type': 'Answer', 'text': fill(ak, av)}} for (_q, _a, qk, ak, qv, av) in faq]}]
    written.append(shell('developer/%s.html' % info['slug'], '%s New Launch Projects %d | Keith Nah' % (d, Y),
                         '%d %s new launch projects in %s: starting prices from %s, tenure and completion dates, with floor plans.' % (len(ix), d, pl, HB.rm(lo[0]) if lo else 'request'),
                         body, ld, 'Hi Keith, I am looking at %s projects.' % d))

body = '<main><section class="hero"><div class="w">%s%s%s</div></section><section class="sec"><div class="w"><div class="idx">%s</div></div></section></main>' % (
    crumbs(home, (None, TX('dev_crumb'))), TX('dev_idx_h1', tag='h1', y=Y), TX('dev_idx_p', tag='p'),
    ''.join('<a href="%s.html"><small>%s</small>%s</a>' % (v['slug'], TX('n_proj', n=len(v['ix'])), E(d)) for d, v in HUBS['developers'].items()))
written.append(shell('developer/index.html', 'New Launch Projects by Developer %d | Keith Nah' % Y, 'Malaysian developers with more than one new launch project on keithnah.com, each with all their projects on one page.',
                     body, [bc_ld(('Home', 'https://keithnah.com/'), ('Developers', 'https://keithnah.com/developer/'))], 'Hi Keith, I am looking at new launch projects.'))

# ---------- station pages ----------
stations = list(HUBS['stations'].items())
for name, s in stations:
    ix = s['ix']
    lines = ' & '.join(s['lines'])
    prices = [HB.price(P[i].get('price')) for i in ix if HB.price(P[i].get('price'))]
    areas = {IDX[i]['area'] for i in ix}
    states = {IDX[i]['state'] for i in ix}
    others = [o for n2, o in stations if n2 != name and {IDX[i]['area'] for i in o['ix']} & areas]
    others += [o for n2, o in stations if n2 != name and o not in others and {IDX[i]['state'] for i in o['ix']} & states]
    others = others[:6]

    def walk(i):
        w = HB.walk_note(P[i], name)
        return '<div class="walk">🚶 %s</div>' % TX(w['k'], **({'n': w['n']} if 'n' in w else {}))
    body = '''<main><section class="hero"><div class="w">%s%s%s%s
<div class="stats"><div class="st"><b>%d</b>%s</div><div class="st"><b>%d</b>%s</div>%s</div></div></section>
<section class="sec"><div class="w">%s<div class="cards">%s</div></div></section>
%s
<section class="w"><div class="cta">%s%s<a href="%s" target="_blank" rel="noopener">WhatsApp Keith</a></div></section></main>''' % (
        crumbs(home, ('index.html', TX('stn_crumb')), (None, E(s['label']))), TX('stn_eb', cls='eb', lines=lines, y=Y), TX('stn_h1', tag='h1', s=s['label'], y=Y), TX('stn_p', tag='p', s=s['label']),
        len(ix), TX('st_projects', tag='small'), len(s['lines']), TX('st_lines', tag='small'),
        ('<div class="st"><b>%s</b>%s</div>' % (HB.rm(min(prices)), TX('st_low', tag='small'))) if prices else '',
        TX('stn_list', tag='h2', s=s['label']), ''.join(card(i, walk(i)) for i in ix),
        ('<section class="sec"><div class="w">%s<div class="hb-chips">%s</div></div></section>' % (TX('stn_other', tag='h2'), ''.join(
            '<a class="hb-chip" href="%s.html">🚆 %s %s</a>' % (o['slug'], E(o['label']), TX('n_proj', tag='b', n=len(o['ix']))) for o in others))) if others else '',
        TX('stn_cta', tag='h2'), TX('stn_cta_p', tag='p'), E(wa('Hi Keith, I am looking for a home near %s.' % s['label'])))
    ld = [bc_ld(('Home', 'https://keithnah.com/'), ('Near a station', 'https://keithnah.com/station/'), (s['label'], 'https://keithnah.com/station/%s.html' % s['slug'])),
          item_list('New condos near %s' % s['label'], ix)]
    written.append(shell('station/%s.html' % s['slug'], 'New Condos Near %s %d | Keith Nah' % (s['label'], Y),
                         '%d new launch projects near %s%s, with starting prices, tenure and floor plans.' % (len(ix), s['label'], (', from ' + HB.rm(min(prices))) if prices else ''),
                         body, ld, 'Hi Keith, I am looking for a home near %s.' % s['label']))

body = '<main><section class="hero"><div class="w">%s%s%s</div></section><section class="sec"><div class="w"><div class="idx">%s</div></div></section></main>' % (
    crumbs(home, (None, TX('stn_crumb'))), TX('stn_idx_h1', tag='h1', y=Y), TX('stn_idx_p', tag='p'),
    ''.join('<a href="%s.html"><small>%s</small>🚆 %s</a>' % (s['slug'], TX('n_proj', n=len(s['ix'])), E(s['label'])) for _n, s in stations))
written.append(shell('station/index.html', 'New Condos Near MRT, LRT & Monorail Stations %d | Keith Nah' % Y, 'New launch projects near MRT, LRT, Monorail, KTM and RTS stations in Malaysia, station by station.',
                     body, [bc_ld(('Home', 'https://keithnah.com/'), ('Near a station', 'https://keithnah.com/station/'))], 'Hi Keith, I am looking for a home near a station.'))


# ---------- head-to-head comparisons ----------
def units(p):
    x = p.get('details_extra') or {}
    m = re.search(r'([\d,]{2,})', str(x.get('Total Units') or x.get('Number of Units') or ''))
    return int(m.group(1).replace(',', '')) if m else None


def year(p):
    m = re.search(r'(20\d\d)', str(p.get('completion') or ''))
    return int(m.group(1)) if m else None


def mfee(p):
    x = p.get('details_extra') or {}
    m = re.search(r'RM\s?(\d+(?:\.\d+)?)\s*psf', str(x.get('Maintenance') or x.get('Maintenance Fee') or ''), re.I)
    return float(m.group(1)) if m else None


def short(n):
    return re.sub(r'\s*[@(].*$', '', n).strip() or n


for x in HUBS['pairs']:
    a, b = x['a'], x['b']
    A, B = P[a], P[b]
    na, nb = A['name'], B['name']
    sa, sb = short(na), short(nb)
    XA, XB = A.get('details_extra') or {}, B.get('details_extra') or {}
    pa, pb = HB.price(A.get('price')), HB.price(B.get('price'))
    ua, ub = units(A), units(B)
    ya, yb = year(A), year(B)
    ma, mb = mfee(A), mfee(B)
    fa, fb = 'freehold' in (A.get('tenure') or '').lower(), 'freehold' in (B.get('tenure') or '').lower()
    win = {}
    if pa and pb and pa != pb:
        win['row_price'] = 'a' if pa < pb else 'b'
    if fa != fb:
        win['row_tenure'] = 'a' if fa else 'b'
    if ua and ub and ua != ub:
        win['row_units'] = 'a' if ua < ub else 'b'
    if ya and yb and ya != yb:
        win['row_done'] = 'a' if ya < yb else 'b'
    if ma and mb and ma != mb:
        win['row_mf'] = 'a' if ma < mb else 'b'
    rows = [('row_price', A.get('price'), B.get('price')), ('row_size', A.get('size'), B.get('size')), ('row_rooms', A.get('rooms'), B.get('rooms')),
            ('row_tenure', A.get('tenure'), B.get('tenure')), ('row_units', ua and format(ua, ','), ub and format(ub, ',')),
            ('row_lifts', XA.get('Lifts'), XB.get('Lifts')), ('row_mf', XA.get('Maintenance') or XA.get('Maintenance Fee'), XB.get('Maintenance') or XB.get('Maintenance Fee')),
            ('row_done', A.get('completion'), B.get('completion')), ('row_status', A.get('status'), B.get('status')),
            ('row_dev', XA.get('Developer'), XB.get('Developer')), ('row_loc', A.get('loc'), B.get('loc'))]
    rows = [r for r in rows if r[1] or r[2]]
    tb = ''.join('<tr>%s<td class="%s">%s</td><td class="%s">%s</td></tr>' % (
        TX(k, tag='th', attrs='scope="row"'), 'win' if win.get(k) == 'a' else '', HB.val(va or '–'), 'win' if win.get(k) == 'b' else '', HB.val(vb or '–')) for k, va, vb in rows)
    nm = {'a': sa, 'b': sb}
    other = {'a': sb, 'b': sa}
    diffs = []
    if 'row_price' in win:
        w = win['row_price']
        diffs.append(TX('d_price', tag='li', x=nm[w], d=HB.rm(abs(pa - pb)), p1=HB.rm(min(pa, pb)), p2=HB.rm(max(pa, pb))))
    if 'row_tenure' in win:
        diffs.append(TX('d_fh', tag='li', x=nm[win['row_tenure']], y=other[win['row_tenure']]))
    if 'row_units' in win:
        diffs.append(TX('d_units', tag='li', x=nm[win['row_units']], u1=format(min(ua, ub), ','), u2=format(max(ua, ub), ',')))
    if 'row_done' in win:
        w = win['row_done']
        diffs.append(TX('d_done', tag='li', x=nm[w], c1=A['completion'] if w == 'a' else B['completion'], c2=B['completion'] if w == 'a' else A['completion']))
    if 'row_mf' in win:
        diffs.append(TX('d_mf', tag='li', x=nm[win['row_mf']], m1='RM%.2f psf' % min(ma, mb), m2='RM%.2f psf' % max(ma, mb)))
    if not diffs:
        diffs.append(TX('d_none', tag='li'))
    same = [v for k, va, vb in rows if va and va == vb and k not in ('row_dev', 'row_loc') for v in [va]]
    reason = {'row_price': 'r_price', 'row_tenure': 'r_fh', 'row_units': 'r_units', 'row_done': 'r_done', 'row_mf': 'r_mf'}

    def why(side):
        rs = [reason[k] for k, v in win.items() if v == side]
        return ''.join(TX(r, tag='li') for r in rs) or TX('r_none', tag='li')
    more = [y for y in HUBS['pairs'] if y is not x and ({y['a'], y['b']} & {a, b} or y['area'] == x['area'])][:6]
    title_en = '%s vs %s: Which One Fits You?' % (na, nb)
    body = '''<main><section class="hero"><div class="w">%s%s%s%s<div class="vs">%s<div class="vsb">VS</div>%s</div></div></section>
<section class="sec"><div class="w">%s<ul class="diff">%s</ul>%s</div></section>
<section class="sec"><div class="w">%s<div class="tbl"><table><thead><tr><th></th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div>%s</div></section>
<section class="sec"><div class="w">%s<div class="two"><div class="box">%s<ul>%s</ul><a href="../property/%s.html">%s</a></div><div class="box">%s<ul>%s</ul><a href="../property/%s.html">%s</a></div></div></div></section>
%s
<section class="w"><div class="cta">%s%s<a href="%s" target="_blank" rel="noopener">WhatsApp Keith</a></div></section></main>''' % (
        crumbs(home, ('index.html', TX('vs_crumb')), (None, '%s vs %s' % (E(sa), E(sb)))), TX('vs_eb', cls='eb', a=x['area']), TX('vs_h1', tag='h1', A=na, B=nb), TX('vs_p', tag='p', a=x['area']),
        card(a), card(b),
        TX('vs_key', tag='h2'), ''.join(diffs),
        ('<h2 style="margin-top:24px">%s</h2><ul class="diff"><li>%s</li></ul>' % (TX('vs_same'), ' · '.join(HB.val(v) for v in same))) if same else '',
        TX('vs_full', tag='h2'), E(sa), E(sb), tb, TX('vs_note', tag='p', cls='note'),
        TX('vs_suit', tag='h2'), TX('vs_choose', tag='h3', x=sa), why('a'), IDX[a]['slug'], TX('view'), TX('vs_choose', tag='h3', x=sb), why('b'), IDX[b]['slug'], TX('view'),
        ('<section class="sec"><div class="w">%s<div class="hb-vs">%s</div></div></section>' % (TX('vs_more', tag='h2'), ''.join(
            '<a href="%s.html"><small>%s</small>%s vs %s</a>' % (y['slug'], E(y['area']), E(P[y['a']]['name']), E(P[y['b']]['name'])) for y in more))) if more else '',
        TX('vs_cta', tag='h2'), TX('vs_cta_p', tag='p'), E(wa('Hi Keith, I am comparing %s and %s.' % (na, nb))))
    ld = [bc_ld(('Home', 'https://keithnah.com/'), ('Comparisons', 'https://keithnah.com/vs/'), ('%s vs %s' % (na, nb), 'https://keithnah.com/vs/%s.html' % x['slug'])),
          item_list('%s vs %s' % (na, nb), [a, b])]
    desc = '%s vs %s in %s: starting price, sizes, tenure, units, completion and maintenance side by side.' % (na, nb, x['area'])
    written.append(shell('vs/%s.html' % x['slug'], '%s vs %s | Keith Nah' % (na, nb), desc, body, ld, 'Hi Keith, I am comparing %s and %s.' % (na, nb)))

areas = []
for x in HUBS['pairs']:
    if x['area'] not in areas:
        areas.append(x['area'])
body = '<main><section class="hero"><div class="w">%s%s%s</div></section><section class="sec"><div class="w">%s</div></section></main>' % (
    crumbs(home, (None, TX('vs_crumb'))), TX('vs_idx_h1', tag='h1', y=Y), TX('vs_idx_p', tag='p'),
    ''.join('<h3 class="grp">%s</h3><div class="idx">%s</div>' % (E(ar), ''.join('<a href="%s.html"><small>%s</small>%s vs %s</a>' % (
        y['slug'], E(ar), E(P[y['a']]['name']), E(P[y['b']]['name'])) for y in HUBS['pairs'] if y['area'] == ar)) for ar in areas))
written.append(shell('vs/index.html', 'New Launch Project Comparisons %d | Keith Nah' % Y, 'Similar new launch projects in the same area compared side by side: price, size, tenure, units and completion.',
                     body, [bc_ld(('Home', 'https://keithnah.com/'), ('Comparisons', 'https://keithnah.com/vs/'))], 'Hi Keith, I am comparing projects.'))

# remove pages that no longer have a group
keep = {os.path.normpath(u.replace('https://keithnah.com/', '') or '') for u in written}
for d in ('developer', 'station', 'vs'):
    for f in glob.glob('%s/*.html' % d):
        rel = f if not f.endswith('index.html') else os.path.dirname(f) + '/'
        if os.path.normpath(rel) not in keep and not f.endswith('index.html'):
            os.remove(f)


# ---------- entry blocks on existing pages ----------
def put(path, start, end, block, anchor_fn):
    t = open(path, encoding='utf-8').read()
    t = re.sub(r'%s.*?%s\n?' % (re.escape(start), re.escape(end)), '', t, flags=re.S)
    if block:
        i = anchor_fn(t)
        if i is None:
            print('  (no place for the block on %s)' % path)
            return
        t = t[:i] + start + block + end + '\n' + t[i:]
    open(path, 'w', encoding='utf-8').write(t)


dev_chips = ''.join('<a class="hb-chip" href="developer/%s.html">%s %s</a>' % (v['slug'], E(d), '<b>%d</b>' % len(v['ix'])) for d, v in HUBS['developers'].items())
stn_chips = ''.join('<a class="hb-chip" href="station/%s.html">🚆 %s</a>' % (s['slug'], E(s['label'])) for _n, s in stations)
blk = ('<style>%s</style><section class="hb-wrap" id="byDeveloper">%s%s<div class="hb-chips">%s</div>'
       '<h2 style="margin-top:26px">%s</h2>%s<div class="hb-chips">%s</div></section>%s') % (
    HB.CSS, TX('b_dev_h', tag='h2'), TX('b_dev_p', tag='p', cls='hb-p'), dev_chips, TX('b_stn_h'), TX('b_stn_p', tag='p', cls='hb-p'), stn_chips, HB.js())


def after_quick(t):
    i = t.find('<!-- KN-QUICK:END -->')
    return i + len('<!-- KN-QUICK:END -->') if i >= 0 else None


put('projects.html', '<!-- KN-HUBS:START -->', '<!-- KN-HUBS:END -->', blk, after_quick)

pop = HUBS['pairs'][:]
seen, top = set(), []
for x in pop:   # one per area first, then the rest
    if x['area'] not in seen:
        top.append(x)
        seen.add(x['area'])
top += [x for x in pop if x not in top]
blk = '<style>%s</style><section class="hb-wrap">%s%s<div class="hb-vs">%s</div><p style="margin-top:12px"><a href="vs/" style="color:#5E60CE;font-weight:700">%s</a></p></section>%s' % (
    HB.CSS, TX('b_vs_h', tag='h2'), TX('b_vs_p', tag='p', cls='hb-p'),
    ''.join('<a href="vs/%s.html"><small>%s</small>%s vs %s</a>' % (x['slug'], E(x['area']), E(P[x['a']]['name']), E(P[x['b']]['name'])) for x in top[:9]), TX('b_all'), HB.js())


def after_cmp_hero(t):
    # Keith: the head-to-head comparisons sit right above "Popular comparisons"
    k = t.find('<!-- KN-CMP-PRESETS:START -->')
    if k >= 0:
        return k
    i = t.find('class="cmp-hero"')
    if i < 0:
        return None
    j = t.find('</section>', i)
    return j + len('</section>') if j >= 0 else None


put('compare.html', '<!-- KN-HUBS:START -->', '<!-- KN-HUBS:END -->', blk, after_cmp_hero)

n_area = 0
for f in sorted(glob.glob('area/*.html')):
    slug = os.path.basename(f)[:-5]
    if slug == 'index':
        continue
    mine = {i for i in range(len(P)) if HB.slugify(IDX[i]['area']) == slug or HB.slugify(IDX[i]['state'] or '') == slug}
    if not mine:
        put(f, '<!-- KN-HUBS:START -->', '<!-- KN-HUBS:END -->', '', lambda t: None)
        continue
    name = next((IDX[i]['area'] for i in mine if HB.slugify(IDX[i]['area']) == slug), None) or next(IDX[i]['state'] for i in mine)
    st = [s for _n, s in stations if set(s['ix']) & mine]
    ps = [x for x in HUBS['pairs'] if {x['a'], x['b']} <= mine]
    devs = [(d, v) for d, v in HUBS['developers'].items() if set(v['ix']) & mine]
    parts = ''
    if st:
        parts += '%s<div class="hb-chips">%s</div>' % (TX('b_area_stn', tag='h2', a=name), ''.join(
            '<a class="hb-chip" href="../station/%s.html">🚆 %s %s</a>' % (s['slug'], E(s['label']), '<b>%d</b>' % len(s['ix'])) for s in st))
    if ps:
        parts += '<h2 style="margin-top:24px">%s</h2><div class="hb-vs">%s</div>' % (TX('b_area_vs', a=name), ''.join(
            '<a href="../vs/%s.html"><small>%s</small>%s vs %s</a>' % (x['slug'], E(x['area']), E(P[x['a']]['name']), E(P[x['b']]['name'])) for x in ps[:8]))
    if devs:
        parts += '<h2 style="margin-top:24px">%s</h2><div class="hb-chips">%s</div>' % (TX('b_dev_h'), ''.join(
            '<a class="hb-chip" href="../developer/%s.html">%s <b>%d</b></a>' % (v['slug'], E(d), len(v['ix'])) for d, v in devs))
    blk = ('<style>%s</style><section class="hb-wrap">%s</section>%s' % (HB.CSS, parts, HB.js())) if parts else ''

    def before_faq(t):
        m = re.search(r'Buying in ', t)
        if not m:
            return None
        return t.rfind('<section', 0, m.start())
    put(f, '<!-- KN-HUBS:START -->', '<!-- KN-HUBS:END -->', blk, before_faq)
    n_area += 1 if blk else 0

# ---------- sitemap ----------
if os.path.exists('sitemap.xml'):
    sm = open('sitemap.xml', encoding='utf-8').read()
    sm = re.sub(r'  <url>\n    <loc>https://keithnah.com/(developer|station|vs)/[^<]*</loc>.*?</url>\n', '', sm, flags=re.S)
    today = datetime.date.today().isoformat()
    sm = sm.replace('</urlset>', ''.join('  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.6</priority>\n  </url>\n' % (u, today) for u in written) + '</urlset>')
    open('sitemap.xml', 'w', encoding='utf-8').write(sm)
print('hubs: %d developer, %d station, %d comparison pages; blocks on projects, compare and %d area pages' % (
    len(HUBS['developers']), len(HUBS['stations']), len(HUBS['pairs']), n_area))
