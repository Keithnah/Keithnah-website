"""Market data page (market-data.html): starting prices and entry price per sq ft by state and area,
worked out from the new launch projects on this site. PREVIEW: English only, not in build_all yet.

Entry price per sq ft = the published starting price (gross) / the smallest unit size. It is a rough
guide to how areas compare, not a transaction price or a valuation.
"""
import collections
import html
import json
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
sys.path.insert(0, HERE)
import hubs_data as HB
import site_header as SH

src = open('projects.html', encoding='utf-8').read()
i = src.index('const PROJECT_DETAILS = ')
P = json.JSONDecoder().raw_decode(src[src.index('=', i) + 1:].lstrip())[0]
IDX = json.load(open(os.path.join(HERE, 'project_index.json'), encoding='utf-8'))
E = html.escape
AREA_PAGES = {os.path.basename(f)[:-5] for f in os.listdir('area')}

rows = []
for k, p in enumerate(P):
    pr = HB.price(p.get('price'))
    sizes = [int(x.replace(',', '')) for x in re.findall(r'(\d[\d,]{2,})\s*(?:–|-|sq)', (p.get('size') or '') + ' sq')]
    sz = min(sizes) if sizes else None
    y = re.search(r'(20\d\d)', p.get('completion') or '')
    rows.append({'n': p['name'], 'slug': IDX[k]['slug'], 'state': IDX[k]['state'], 'area': IDX[k]['area'], 'price': pr,
                 'psf': round(pr / sz) if pr and sz and sz >= 300 else None, 'fh': 'freehold' in (p.get('tenure') or '').lower(),
                 'ready': p.get('status') == 'Completed' or (bool(y) and int(y.group(1)) <= 2027)})


def summary(rs):
    ps = [r['psf'] for r in rs if r['psf']]
    pr = [r['price'] for r in rs if r['price']]
    return {'n': len(rs), 'psf': round(st.median(ps)) if ps else None, 'lo': min(pr) if pr else None,
            'med': round(st.median(pr)) if pr else None, 'fh': round(100 * sum(r['fh'] for r in rs) / len(rs)),
            'ready': sum(r['ready'] for r in rs), 'np': len(ps)}


by_state = collections.defaultdict(list)
for r in rows:
    by_state[r['state']].append(r)
states = sorted(by_state, key=lambda s: -len(by_state[s]))
ALL = summary(rows)


def money(v):
    return HB.rm(v) if v else '–'


tiles = ''.join('<div class="md-t"><small>%s</small><b>%s</b><span>median entry psf · %d projects</span></div>'
                % (E(s), ('RM%s' % format(summary(by_state[s])['psf'], ',')) if summary(by_state[s])['psf'] else '–', len(by_state[s]))
                for s in states[:4])

# bar chart: areas with 2+ projects that have an entry psf
areas = collections.defaultdict(list)
for r in rows:
    areas[(r['state'], r['area'])].append(r)
bars = sorted([(a, summary(v)) for a, v in areas.items() if summary(v)['np'] >= 2], key=lambda x: -x[1]['psf'])
top = max(s['psf'] for _, s in bars)
chart = ''.join('<div class="md-b"><span class="l">%s<small>%s</small></span><span class="tr"><i style="width:%.1f%%"></i></span><b>RM%s</b></div>'
                % (E(a[1]), E(a[0]), 100 * s['psf'] / top, format(s['psf'], ',')) for a, s in bars)

table = ''
for s in states:
    sub = sorted(((a, v) for (st_, a), v in areas.items() if st_ == s), key=lambda x: -len(x[1]))
    S = summary(by_state[s])
    table += ('<tr class="st"><td>%s</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%d%%</td><td>%d</td></tr>'
              % (E(s), S['n'], money(S['lo']), money(S['med']), ('RM%s' % format(S['psf'], ',')) if S['psf'] else '–', S['fh'], S['ready']))
    for a, v in sub:
        A = summary(v)
        slug = HB.slugify(a)
        name = '<a href="area/%s.html">%s</a>' % (slug, E(a)) if slug in AREA_PAGES else E(a)
        table += ('<tr><td>%s</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%d%%</td><td>%d</td></tr>'
                  % (name, A['n'], money(A['lo']), money(A['med']), ('RM%s' % format(A['psf'], ',')) if A['psf'] else '–', A['fh'], A['ready']))

CSS = '''
:root{--ink:#15142b;--grey:#5f5e74;--line:rgba(21,20,43,.09);--gold:#5E60CE;--bg:#F7F6FB;}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:Inter,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6}a{color:inherit;text-decoration:none}
h1,h2{font-family:'Playfair Display',Georgia,serif;line-height:1.2}
.md{max-width:1080px;margin:0 auto;padding:120px 5vw 70px}
.md-h{text-align:center;margin-bottom:28px}.md-h .eb{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);font-weight:800}
.md-h h1{font-size:clamp(30px,4.6vw,46px);margin:8px 0 10px}.md-h p{color:var(--grey);max-width:680px;margin:0 auto}
.md-ts{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-bottom:22px}
.md-t{background:#fff;border:1px solid var(--line);border-radius:20px;padding:18px 20px;box-shadow:0 10px 30px rgba(29,27,79,.06)}
.md-t small{display:block;font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--grey)}
.md-t b{display:block;font-size:30px;font-weight:800;color:var(--ink);margin:4px 0 0}.md-t span{font-size:12.5px;color:var(--grey)}
.md-c{background:#fff;border:1px solid var(--line);border-radius:24px;padding:26px;margin-bottom:22px;box-shadow:0 10px 30px rgba(29,27,79,.06)}
.md-c h2{font-size:24px;margin-bottom:4px}.md-c>p{color:var(--grey);font-size:13.5px;margin-bottom:18px}
.md-b{display:grid;grid-template-columns:190px 1fr 86px;align-items:center;gap:12px;padding:7px 0;border-bottom:1px solid #f1f0f7}
.md-b .l{font-weight:700;font-size:14px;line-height:1.25}.md-b .l small{display:block;font-weight:500;color:var(--grey);font-size:11.5px}
.md-b .tr{height:14px;background:#efeefb;border-radius:100px;overflow:hidden}.md-b .tr i{display:block;height:100%;border-radius:100px;background:linear-gradient(90deg,#5E60CE,#9a98f0)}
.md-b b{text-align:right;font-size:14px}
.md-tb{overflow-x:auto}.md-tb table{width:100%;border-collapse:collapse;font-size:13.5px;min-width:640px}
.md-tb th{text-align:left;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--grey);padding:10px 10px;border-bottom:2px solid var(--line)}
.md-tb td{padding:9px 10px;border-bottom:1px solid #f1f0f7}.md-tb td:first-child{padding-left:22px}.md-tb tr.st td{background:#f6f5ff;font-weight:800}.md-tb tr.st td:first-child{padding-left:10px}
.md-tb td a{color:var(--gold);font-weight:600}.md-tb td:not(:first-child),.md-tb th:not(:first-child){text-align:right}
.md-n{font-size:12.5px;color:var(--grey);margin-top:14px}
.md-cta{text-align:center;margin-top:26px}.md-cta a{display:inline-block;background:#25D366;color:#fff;font-weight:700;padding:14px 26px;border-radius:14px;box-shadow:0 10px 24px rgba(37,211,102,.3)}
@media(max-width:600px){.md-b{grid-template-columns:110px 1fr 70px;gap:8px}.md-c{padding:18px}}
'''

page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Malaysia New Launch Prices by Area: Entry Price per sq ft | Keith Nah</title>
<meta name="description" content="Starting prices, entry price per sq ft and freehold share of new launch condos by state and area in Malaysia, from %d projects.">
<link rel="canonical" href="https://keithnah.com/market-data.html">
<link rel="icon" type="image/png" href="images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
<style>%s</style>
</head>
<body>
<header>
  <a class="logo" href="./"><img src="images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Keith Nah Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="https://api.whatsapp.com/send/?phone=60102821568&amp;type=phone_number&amp;app_absent=0" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
<main class="md">
  <div class="md-h"><span class="eb">Market Data</span><h1>New Launch Prices by Area</h1>
  <p>Starting prices and entry price per sq ft of the %d new launch projects on this site, by state and area. Updated with every project change.</p></div>
  <div class="md-ts">%s</div>
  <section class="md-c"><h2>Entry price per sq ft by area</h2><p>Median of each project's published starting price divided by its smallest unit. Areas with at least 2 priced projects.</p>%s</section>
  <section class="md-c"><h2>All states and areas</h2><p>Starting prices are the developers' published gross prices.</p>
  <div class="md-tb"><table><thead><tr><th>Area</th><th>Projects</th><th>Lowest start</th><th>Median start</th><th>Entry psf</th><th>Freehold</th><th>Ready by 2027</th></tr></thead><tbody>%s</tbody></table></div>
  <p class="md-n">Entry price per sq ft is a rough guide for comparing areas, not a transaction price or valuation. Prices change; ask Keith for the latest price list.</p></section>
  <div class="md-cta"><a href="https://api.whatsapp.com/send/?phone=60102821568&amp;type=phone_number&amp;app_absent=0" target="_blank" rel="noopener">Ask Keith about an area</a></div>
</main>
<footer></footer>
</body>
</html>
''' % (len(rows), CSS, len(rows), tiles, chart, table)
open(sys.argv[1] if len(sys.argv) > 1 else 'market-data.html', 'w', encoding='utf-8').write(SH.apply(page, '', 'blog.html'))
print('market data: %d projects, %d states, %d areas in chart' % (len(rows), len(states), len(bars)))
