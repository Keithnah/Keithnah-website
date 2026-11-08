"""Free area guides: a PDF per area and a landing page per guide.

- downloads/guides/<slug>.pdf   the guide (A4): cover, area at a glance with a map, a comparison
                                 table and a sheet for every project. Built with Chromium
                                 (tools/render_guides.js) only when the data changed, so the
                                 PDFs do not change on every build.
- images/guides/<slug>-N.jpg    previews of the first pages, shown on the landing page.
- guides/<slug>.html            landing page: what is inside, the projects, and a short form
                                 (name, email, WhatsApp, WeChat/LINE). The form goes to the same
                                 Google Sheet / Telegram as the Quick Enquiry, then the PDF downloads.
Never put agent-only information in a guide (rebates, packages, commission and so on).
"""
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
sys.path.insert(0, HERE)
import build_area_pages as A  # noqa: E402
import site_header as SH  # noqa: E402

E = lambda s: html.escape(str(s if s is not None else ''), quote=True)
SITE = 'https://keithnah.com'
WA = 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0'
waq = lambda m: WA % re.sub(r'\s', '+', '(KNRE) ' + m)
BAN = re.compile(r'GRR|MRR|guarantee|rental return|rebate|\bnett\b|commission|airbnb|klcc|licen[cs]e no|permit|\bBP\b|sales gallery|'
                 r'showroom|cash ?back|discount|package|mana ?mana|\blppsa\b', re.I)
MONTH = datetime.date.today().strftime('%B %Y')
YEAR = datetime.date.today().year


def _compare_rows():
    s = open('compare.html', encoding='utf-8').read()
    i = s.index('=', s.index('const PROJECTS = ')) + 1
    return {r['name']: r for r in json.JSONDecoder().raw_decode(s[i:].lstrip())[0]}


CMP = _compare_rows()
KIDX = {p['name']: k for k, p in enumerate(A.P)}


def guides():
    """The areas that get a guide: every area with 3+ projects, plus Penang, Johor and Selangor."""
    groups = A.groups()
    out = []
    for st, sub in groups.items():
        for ar, ids in sub.items():
            if len(ids) >= 3:
                out.append((ar, st, ids))
    for st in ('Penang', 'Johor', 'Selangor'):
        ids = [k for v in groups.get(st, {}).values() for k in v]
        if ids:
            out.append((st, st, ids))
    out.sort(key=lambda x: (-len(x[2]), x[0]))
    res = []
    for ar, st, ids in out[:12]:
        ids = sorted(ids, key=lambda k: A.P[k]['name'].lower())
        res.append({'area': ar, 'state': st, 'ids': ids, 'slug': A.slug(ar), 'n': len(ids)})
    return res


def facts(g):
    rows = [CMP.get(A.P[k]['name'], {}) for k in g['ids']]
    prices = [r['nPrice'] for r in rows if r.get('nPrice')]
    yrs = sorted({r['nYear'] for r in rows if r.get('nYear')})
    free = sum(1 for r in rows if (r.get('tenure') or '').lower().startswith('freehold'))
    rails = []
    for r in rows:
        m = re.match(r'(.*?(?:MRT|LRT|Monorail|RTS|KTM|BRT)[^,(;–-]*)', r.get('rail') or '')
        if m and m.group(1).strip() not in rails:
            rails.append(m.group(1).strip())
    return {'low': min(prices) if prices else None, 'yrs': yrs, 'free': free, 'rails': rails[:4]}


def clean_list(xs, n):
    out = []
    for x in xs or []:
        if x and not BAN.search(x) and x not in out:
            out.append(x)
    return out[:n]


# ---------------- PDF source ----------------
PDF_CSS = '''
@page{size:A4;margin:0;}
*{box-sizing:border-box;margin:0;padding:0;}
html,body{-webkit-print-color-adjust:exact;print-color-adjust:exact;}
body{font-family:Inter,'Noto Sans',Arial,sans-serif;color:#15142b;background:#fff;font-size:10.5pt;line-height:1.45;}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif;line-height:1.15;}
.pg{width:210mm;height:297mm;position:relative;overflow:hidden;page-break-after:always;break-after:page;padding:16mm 15mm 18mm;}
.pg:last-child{page-break-after:auto;break-after:auto;}
.ft{position:absolute;left:15mm;right:15mm;bottom:8mm;display:flex;justify-content:space-between;font-size:7.5pt;color:#8a89a0;border-top:1px solid #e7e6ef;padding-top:3mm;}
.ey{font-size:8pt;letter-spacing:.22em;text-transform:uppercase;color:#5E60CE;font-weight:700;}
/* cover */
.cover{padding:0;color:#fff;background:#1d1b4f;}
.cover .ph{position:absolute;inset:0;background-size:cover;background-position:center;}
.cover .sh{position:absolute;inset:0;background:linear-gradient(180deg,rgba(29,27,79,.25) 0%,rgba(29,27,79,.55) 45%,rgba(18,17,48,.96) 78%);}
.cover .in{position:absolute;left:16mm;right:16mm;bottom:22mm;}
.cover .brand{position:absolute;top:14mm;left:16mm;right:16mm;display:flex;align-items:center;gap:4mm;font-family:'Playfair Display',serif;font-size:14pt;}
.cover .brand img{width:13mm;height:13mm;border-radius:50%;background:#fff;}
.cover .brand small{display:block;font-family:Inter,sans-serif;font-size:7pt;letter-spacing:.2em;opacity:.8;}
.cover .tag{display:inline-block;background:#5E60CE;color:#fff;font-size:8.5pt;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:2mm 4mm;border-radius:100px;margin-bottom:6mm;}
.cover h1{font-size:44pt;margin-bottom:4mm;} .cover h2{font-family:Inter,sans-serif;font-weight:500;font-size:15pt;opacity:.92;margin-bottom:10mm;}
.cover .st{display:flex;gap:0;border-top:1px solid rgba(255,255,255,.25);padding-top:6mm;}
.cover .st div{flex:1;padding-right:5mm;} .cover .st b{display:block;font-family:'Playfair Display',serif;font-size:19pt;} .cover .st span{font-size:8pt;letter-spacing:.12em;text-transform:uppercase;opacity:.75;}
/* glance */
.gl h2{font-size:24pt;margin:2mm 0 4mm;} .gl p.lead{font-size:11pt;color:#3d3c55;margin-bottom:6mm;}
.boxes{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm;margin-bottom:6mm;}
.boxes div{background:#f3f1fa;border-radius:3mm;padding:4mm;} .boxes b{display:block;font-family:'Playfair Display',serif;font-size:15pt;color:#1d1b4f;} .boxes span{font-size:7.5pt;color:#5a5a6e;text-transform:uppercase;letter-spacing:.08em;}
.map{width:100%;height:105mm;border-radius:3mm;overflow:hidden;border:1px solid #e3e2ee;background:#eef0f4 center/cover no-repeat;margin-bottom:5mm;}
.rails{font-size:9pt;color:#3d3c55;} .rails b{color:#1d1b4f;}
.how{margin-top:5mm;display:grid;grid-template-columns:1fr 1fr 1fr;gap:3mm;}
.how div{border:1px solid #e7e6ef;border-radius:3mm;padding:3.5mm;font-size:8.5pt;color:#3d3c55;} .how b{display:block;color:#1d1b4f;font-size:9.5pt;margin-bottom:1mm;}
/* table */
.tb h2{font-size:20pt;margin:2mm 0 5mm;}
table{width:100%;border-collapse:collapse;font-size:8.3pt;}
th{background:#1d1b4f;color:#fff;text-align:left;font-weight:600;padding:2.6mm 2mm;font-size:7.5pt;letter-spacing:.04em;text-transform:uppercase;}
td{padding:2.4mm 2mm;border-bottom:1px solid #ecebf3;vertical-align:top;} tr:nth-child(even) td{background:#faf9fd;}
td:nth-child(4){white-space:nowrap;} td.n{font-weight:700;color:#1d1b4f;} td.n small{display:block;font-weight:500;color:#7a7990;font-size:7pt;}
.note{font-size:7.5pt;color:#7a7990;margin-top:3mm;}
/* project sheets */
.ps{display:flex;flex-direction:column;gap:6mm;}
.pj{display:grid;grid-template-columns:70mm 1fr;gap:5mm;height:122mm;border:1px solid #e7e6ef;border-radius:4mm;overflow:hidden;}
.pj .im{background:#ddd center/cover no-repeat;position:relative;}
.pj .im span{position:absolute;left:3mm;top:3mm;background:#fff;color:#1d1b4f;font-size:7pt;font-weight:700;padding:1mm 2.5mm;border-radius:100px;}
.pj .bd{padding:5mm 5mm 4mm 0;display:flex;flex-direction:column;}
.pj h3{font-size:15pt;color:#1d1b4f;} .pj .lc{font-size:8.3pt;color:#6a6980;margin:1mm 0 3mm;}
.kv{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2mm 3mm;margin-bottom:3mm;}
.kv div{font-size:8.3pt;} .kv span{display:block;font-size:6.6pt;color:#7a7990;text-transform:uppercase;letter-spacing:.06em;}
.kv b{font-weight:700;color:#15142b;}
.pj ul{list-style:none;font-size:8.2pt;color:#3d3c55;flex:1;} .pj li{padding-left:4mm;position:relative;margin-bottom:1.2mm;} .pj li:before{content:"";position:absolute;left:0;top:1.6mm;width:1.6mm;height:1.6mm;border-radius:50%;background:#5E60CE;}
.pj .ln{font-size:7.5pt;color:#5E60CE;font-weight:700;}
/* back */
.bk{background:#1d1b4f;color:#fff;}
.bk h2{font-size:28pt;margin:6mm 0 5mm;} .bk p{font-size:11pt;opacity:.9;max-width:150mm;margin-bottom:5mm;}
.bk .kp{display:flex;gap:7mm;align-items:center;margin:10mm 0;} .bk .kp img{width:45mm;height:55mm;object-fit:cover;border-radius:4mm;border:1.5mm solid #fff;}
.bk .ct div{font-size:11pt;margin-bottom:2.5mm;} .bk .ct b{display:inline-block;width:32mm;opacity:.7;font-weight:500;font-size:9pt;text-transform:uppercase;letter-spacing:.1em;}
.bk .dis{position:absolute;left:15mm;right:15mm;bottom:14mm;font-size:7.5pt;opacity:.65;line-height:1.5;}
'''


def rm(v):
    return 'RM%s' % format(int(round(v, -2)), ',') if v else '—'


def pdf_html(g, map_png):
    ids = g['ids']
    f = facts(g)
    P = A.P
    photo = lambda k: 'file://' + os.path.join(ROOT, A.PHOTO[k]) if A.PHOTO.get(k) else ''
    cov = next((photo(k) for k in ids if A.PHOTO.get(k)), '')
    yrs = f['yrs']
    yr_txt = ('Ready' if yrs and yrs[0] == 0 and len(yrs) == 1 else
              '%s–%s' % (yrs[0] or 'Ready', yrs[-1]) if len(yrs) > 1 else (str(yrs[0]) if yrs else 'TBC'))
    foot = lambda n: '<div class="ft"><span>%s New Launch Guide · %s</span><span>Keith Nah Real Estate · keithnah.com</span><span>%d</span></div>' % (E(g['area']), MONTH, n)
    pages = []
    # cover
    pages.append('<section class="pg cover"><div class="ph" style="background-image:url(\'%s\')"></div><div class="sh"></div>'
                 '<div class="brand"><img src="file://%s/images/f304c8479b1fe873.png" alt=""><div>Keith Nah 鈞晖<small>KEITH NAH REAL ESTATE</small></div></div>'
                 '<div class="in"><span class="tag">Free buyer\'s guide · %s</span><h1>%s</h1><h2>New launch projects, compared side by side</h2>'
                 '<div class="st"><div><b>%d</b><span>Projects</span></div><div><b>%s</b><span>Starting from</span></div><div><b>%d of %d</b><span>Freehold</span></div><div><b>%s</b><span>Completion</span></div></div></div></section>' % (
                     cov, ROOT, MONTH, E(g['area']), g['n'], rm(f['low']), f['free'], g['n'], E(yr_txt)))
    # at a glance
    intro = A.INTRO.get(g['area']) or A.INTRO.get(g['state']) or ''
    pages.append('<section class="pg gl"><span class="ey">At a glance</span><h2>%s in one look</h2><p class="lead">%s</p>'
                 '<div class="boxes"><div><b>%d</b><span>Projects in this guide</span></div><div><b>%s</b><span>Lowest starting price</span></div>'
                 '<div><b>%d</b><span>Freehold projects</span></div><div><b>%s</b><span>Completion years</span></div></div>'
                 '<div class="map" style="background-image:url(\'file://%s\')"></div>'
                 '<p class="rails"><b>Rail stations near these projects:</b> %s</p>'
                 '<div class="how"><div><b>1. Compare</b>The table on the next page puts every project side by side.</div>'
                 '<div><b>2. Shortlist</b>Each project sheet shows prices, sizes, fees and highlights.</div>'
                 '<div><b>3. Ask Keith</b>Send your shortlist on WhatsApp for floor plans and the latest prices.</div></div>%s</section>' % (
                     E(g['area']), E(intro), g['n'], rm(f['low']), f['free'], E(yr_txt), map_png, E(', '.join(f['rails']) or 'see each project sheet'), foot(2)))
    # comparison table (11 rows per page)
    chunks = [ids[i:i + 11] for i in range(0, len(ids), 11)]
    pn = 3
    for ci, ch in enumerate(chunks):
        trs = ''.join('<tr><td class="n">%s<small>%s</small></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            E(P[k]['name']), E(A.PLACES[k][1]), E(CMP[P[k]['name']]['price']), E(CMP[P[k]['name']].get('psfTxt') or '—'),
            E(P[k].get('size')), E(P[k].get('rooms')), E(P[k].get('tenure')), E(P[k].get('completion'))) for k in ch)
        pages.append('<section class="pg tb"><span class="ey">Side by side</span><h2>All %d projects compared%s</h2>'
                     '<table><thead><tr><th>Project</th><th>Starting price</th><th>Price psf</th><th>Size</th><th>Bedrooms</th><th>Tenure</th><th>Completion</th></tr></thead><tbody>%s</tbody></table>'
                     '<p class="note">Prices are starting prices (gross) and change often. Ask Keith for the latest price list.</p>%s</section>' % (
                         g['n'], ' (cont.)' if ci else '', trs, foot(pn)))
        pn += 1
    # project sheets, two per page
    for i in range(0, len(ids), 2):
        cards = ''
        for k in ids[i:i + 2]:
            p, c = P[k], CMP[P[k]['name']]
            pts = clean_list((p.get('selling_points') or []) + (p.get('points') or []), 5)
            kv = [('Starting price', c['price']), ('Price psf', c.get('psfTxt') or '—'),
                  ('Est. monthly*', ('RM %s' % format(c['nMo'], ',')) if c.get('nMo') else '—'),
                  ('Size', p.get('size')), ('Bedrooms', p.get('rooms')), ('Tenure', p.get('tenure')),
                  ('Completion', p.get('completion')), ('Developer', c.get('dev') or '—'), ('Maintenance', c.get('maint') or '—')]
            kvh = ''.join('<div><span>%s</span><b>%s</b></div>' % (E(a), E(re.sub(r'\s*\((?:incl|including|excl|excluding)[^)]*\)', '', str(b))[:46])) for a, b in kv)
            cards += ('<article class="pj"><div class="im" style="background-image:url(\'%s\')"><span>%s</span></div><div class="bd"><h3>%s</h3><div class="lc">%s%s</div>'
                      '<div class="kv">%s</div><ul>%s</ul><div class="ln">keithnah.com/property/%s.html</div></div></article>') % (
                photo(k), E(p.get('status') or ''), E(p['name']), E(p.get('loc') or ''), (' · ' + E(c['rail'])) if c.get('rail') else '',
                kvh, ''.join('<li>%s</li>' % E(x) for x in pts), A.SLUG.get(k, A.slug(p['name'])))
        pages.append('<section class="pg"><span class="ey">Project sheets</span><div class="ps" style="margin-top:4mm">%s</div>'
                     '<p class="note">*Estimate with 10%% down payment, 4%% interest, 35 years. Details are from developer materials and may change.</p>%s</section>' % (cards, foot(pn)))
        pn += 1
    # back page
    pages.append('<section class="pg bk"><span class="ey" style="color:#b9b4ff">Next step</span><h2>Shortlisted a few?<br>Let\'s look at them together.</h2>'
                 '<p>Send Keith the projects you like. He will reply with floor plans, the latest prices and what each one suits best, whether you want to live in it, rent it out or hold it.</p>'
                 '<div class="kp"><img src="file://%s/images/6b39ef32b4958165.jpg" alt=""><img src="file://%s/images/4382969133d212d0.jpg" alt=""></div>'
                 '<div class="ct"><div><b>WhatsApp</b>+60 10-282 1568</div><div><b>Website</b>keithnah.com</div><div><b>YouTube</b>@KeithNahRealEstate</div></div>'
                 '<p class="dis">This guide is for general information only. Prices, sizes, completion dates and other details come from developer materials, '
                 'are indicative and can change without notice. Please confirm the latest details with Keith before making any decision. © %d Keith Nah Real Estate.</p></section>' % (ROOT, ROOT, YEAR))
    return ('<!DOCTYPE html><html><head><meta charset="utf-8"><title>%s New Launch Guide | Keith Nah Real Estate</title>'
            '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">'
            '<style>%s</style></head><body>%s</body></html>') % (E(g['area']), PDF_CSS, ''.join(pages)), len(pages)


def build_pdfs(gs, force=False):
    """Render the PDFs and page previews with Chromium when the guide data changed."""
    state_p = os.path.join(HERE, 'guide_pdfs.json')
    try:
        state = json.load(open(state_p))
    except (OSError, ValueError):
        state = {}
    work = os.path.join(HERE, '.guide_build')
    os.makedirs(work, exist_ok=True)
    os.makedirs('downloads/guides', exist_ok=True)
    os.makedirs('images/guides', exist_ok=True)
    jobs = []
    for g in gs:
        mp = os.path.join(work, g['slug'] + '-map.png')
        src, npg = pdf_html(g, mp)
        h = hashlib.sha1((src.replace(MONTH, '') + PDF_CSS).encode()).hexdigest()[:12]
        g['pages'] = npg
        if not force and state.get(g['slug'], {}).get('h') == h and os.path.exists('downloads/guides/%s.pdf' % g['slug']):
            g['pages'] = state[g['slug']].get('pages', npg)
            continue
        hp = os.path.join(work, g['slug'] + '.html')
        open(hp, 'w', encoding='utf-8').write(src)
        jobs.append({'slug': g['slug'], 'html': hp, 'map': mp, 'area': os.path.join(ROOT, 'area', g['slug'] + '.html'),
                     'pdf': os.path.join(ROOT, 'downloads/guides', g['slug'] + '.pdf'), 'prev': os.path.join(work, g['slug'] + '-p'), 'h': h, 'pages': npg})
    if jobs:
        jp = os.path.join(work, 'jobs.json')
        json.dump(jobs, open(jp, 'w'))
        try:
            r = subprocess.run(['node', os.path.join(HERE, 'render_guides.js'), jp], capture_output=True, text=True, timeout=1500)
        except (OSError, subprocess.TimeoutExpired) as e:
            print('PDF step skipped:', e)
            return
        if r.returncode:
            print('PDF step failed:', (r.stderr or r.stdout)[-400:])
            return
        from PIL import Image
        for j in jobs:
            for n in (1, 2, 3):
                p = '%s%d.png' % (j['prev'], n)
                if os.path.exists(p):
                    im = Image.open(p).convert('RGB')
                    im.thumbnail((620, 880))
                    im.save('images/guides/%s-%d.jpg' % (j['slug'], n), quality=82)
            state[j['slug']] = {'h': j['h'], 'pages': j['pages']}
        json.dump(state, open(state_p, 'w'), indent=1, sort_keys=True)
    shutil.rmtree(work, ignore_errors=True)
    print('PDFs rendered: %d' % len(jobs))


# ---------------- landing pages ----------------
UI = {
    'en': {'eb': 'Free PDF guide', 'h1': '{a} New Launch Guide {y}', 'sub': 'Every new launch in {a} in one PDF: starting prices, price psf, sizes, completion dates, nearest rail stations, a location map and a sheet for each project.',
           'p': 'Projects', 'from': 'Starting from', 'fh': 'Freehold', 'cy': 'Completion', 'pg': 'PDF · {n} pages',
           'ft': 'Get the free guide', 'fs': 'Fill in your details and the PDF downloads straight away.',
           'name': 'Name', 'email': 'Email', 'wa': 'WhatsApp number', 'wc': 'WeChat / LINE ID (optional)', 'go': 'Download the PDF',
           'priv': 'Keith may contact you about this guide. Your details are never shared.', 'need': 'Please fill in your name, email and WhatsApp number (or a WeChat / LINE ID).',
           'okT': 'Your guide is ready', 'okS': 'The download should start on its own. If it does not, tap the button below.', 'dl': 'Download again', 'ask': 'Questions? WhatsApp Keith',
           'in': "What's inside", 'i1': 'Side-by-side table', 'i1d': 'All {n} projects on one page: price, psf, size, bedrooms, tenure and completion.',
           'i2': 'A sheet per project', 'i2d': 'Photo, key numbers, maintenance fee, developer and highlights.',
           'i3': 'Location map', 'i3d': 'Where each project sits, with the rail stations nearby.', 'i4': 'Monthly instalments', 'i4d': 'An estimate for every project, so you can see what fits your budget.',
           'inc': 'Projects in this guide', 'more': 'Other area guides', 'back': 'Free Toolkit', 'n_p': '{n} projects'},
    'zh-CN': {'eb': '免费 PDF 懒人包', 'h1': '{a} 新楼盘懒人包 {y}', 'sub': '{a} 所有新项目整理成一份 PDF：起价、呎价、面积、竣工时间、最近的轨道站、位置地图，还有每个项目的资料页。',
              'p': '项目', 'from': '起价', 'fh': '永久地契', 'cy': '竣工', 'pg': 'PDF · {n} 页',
              'ft': '免费领取懒人包', 'fs': '填写资料后，PDF 会马上下载。',
              'name': '名字', 'email': '电邮', 'wa': 'WhatsApp 号码', 'wc': '微信 / LINE ID（选填）', 'go': '下载 PDF',
              'priv': 'Keith 可能会就这份资料联系你。你的资料不会分享给任何人。', 'need': '请填写名字、电邮和 WhatsApp 号码（或微信 / LINE ID）。',
              'okT': '懒人包已准备好', 'okS': '下载会自动开始。如果没有，请按下面的按钮。', 'dl': '再次下载', 'ask': '有问题？WhatsApp Keith',
              'in': '懒人包里有什么', 'i1': '并排比较表', 'i1d': '{n} 个项目放在同一页：价格、呎价、面积、卧室、产权和竣工。',
              'i2': '每个项目一页资料', 'i2d': '照片、重点数字、管理费、发展商和项目亮点。',
              'i3': '位置地图', 'i3d': '每个项目的位置，以及附近的轨道站。', 'i4': '月供估算', 'i4d': '每个项目都有月供估算，马上知道哪个适合你的预算。',
              'inc': '懒人包里的项目', 'more': '其他地区懒人包', 'back': '免费资源', 'n_p': '{n} 个项目'},
    'ms': {'eb': 'Panduan PDF percuma', 'h1': 'Panduan Projek Baharu {a} {y}', 'sub': 'Semua projek baharu di {a} dalam satu PDF: harga permulaan, harga sk, saiz, tarikh siap, stesen rel terdekat, peta lokasi dan satu halaman bagi setiap projek.',
           'p': 'Projek', 'from': 'Harga dari', 'fh': 'Pegangan bebas', 'cy': 'Siap', 'pg': 'PDF · {n} halaman',
           'ft': 'Dapatkan panduan percuma', 'fs': 'Isi butiran anda dan PDF akan dimuat turun serta-merta.',
           'name': 'Nama', 'email': 'E-mel', 'wa': 'Nombor WhatsApp', 'wc': 'ID WeChat / LINE (pilihan)', 'go': 'Muat turun PDF',
           'priv': 'Keith mungkin menghubungi anda tentang panduan ini. Butiran anda tidak akan dikongsi.', 'need': 'Sila isi nama, e-mel dan nombor WhatsApp (atau ID WeChat / LINE).',
           'okT': 'Panduan anda sudah sedia', 'okS': 'Muat turun akan bermula sendiri. Jika tidak, tekan butang di bawah.', 'dl': 'Muat turun semula', 'ask': 'Ada soalan? WhatsApp Keith',
           'in': 'Kandungan panduan', 'i1': 'Jadual perbandingan', 'i1d': 'Kesemua {n} projek dalam satu halaman: harga, harga sk, saiz, bilik, pegangan dan tarikh siap.',
           'i2': 'Satu halaman setiap projek', 'i2d': 'Foto, angka utama, yuran penyelenggaraan, pemaju dan kelebihan.',
           'i3': 'Peta lokasi', 'i3d': 'Lokasi setiap projek, dengan stesen rel berdekatan.', 'i4': 'Ansuran bulanan', 'i4d': 'Anggaran untuk setiap projek, supaya anda tahu yang mana sesuai dengan bajet.',
           'inc': 'Projek dalam panduan ini', 'more': 'Panduan kawasan lain', 'back': 'Kit Percuma', 'n_p': '{n} projek'},
    'ja': {'eb': '無料PDFガイド', 'h1': '{a} 新築物件ガイド {y}', 'sub': '{a} の新築物件をすべて1つのPDFに。最低価格、平方フィート単価、面積、完成時期、最寄り駅、地図、物件ごとの資料ページ付き。',
           'p': '物件数', 'from': '最低価格', 'fh': '自由保有', 'cy': '完成', 'pg': 'PDF · {n}ページ',
           'ft': '無料ガイドを受け取る', 'fs': '情報を入力すると、すぐにPDFがダウンロードされます。',
           'name': 'お名前', 'email': 'メール', 'wa': 'WhatsApp 番号', 'wc': 'WeChat / LINE ID（任意）', 'go': 'PDFをダウンロード',
           'priv': 'このガイドについて Keith からご連絡する場合があります。情報が共有されることはありません。', 'need': 'お名前、メール、WhatsApp 番号（または WeChat / LINE ID）を入力してください。',
           'okT': 'ガイドの準備ができました', 'okS': 'ダウンロードが自動で始まります。始まらない場合は下のボタンを押してください。', 'dl': 'もう一度ダウンロード', 'ask': '質問は Keith の WhatsApp へ',
           'in': 'ガイドの内容', 'i1': '比較表', 'i1d': '{n}件の物件を1ページで比較：価格、単価、面積、ベッドルーム、保有形態、完成時期。',
           'i2': '物件ごとの資料', 'i2d': '写真、主な数字、管理費、デベロッパー、特徴。',
           'i3': '地図', 'i3d': '各物件の位置と近くの駅。', 'i4': '月々の返済目安', 'i4d': 'すべての物件に返済目安付き。予算に合う物件がすぐわかります。',
           'inc': 'ガイドに含まれる物件', 'more': 'ほかのエリアガイド', 'back': '無料ツールキット', 'n_p': '{n}件'},
    'ko': {'eb': '무료 PDF 가이드', 'h1': '{a} 신규 분양 가이드 {y}', 'sub': '{a}의 모든 신규 분양을 하나의 PDF로: 시작 가격, 평방피트당 가격, 면적, 준공 시기, 가까운 역, 위치 지도, 프로젝트별 자료 페이지.',
           'p': '프로젝트', 'from': '시작 가격', 'fh': '자유보유', 'cy': '준공', 'pg': 'PDF · {n}페이지',
           'ft': '무료 가이드 받기', 'fs': '정보를 입력하면 PDF가 바로 다운로드됩니다.',
           'name': '이름', 'email': '이메일', 'wa': 'WhatsApp 번호', 'wc': 'WeChat / LINE ID (선택)', 'go': 'PDF 다운로드',
           'priv': '이 가이드와 관련해 Keith가 연락드릴 수 있습니다. 정보는 공유되지 않습니다.', 'need': '이름, 이메일, WhatsApp 번호(또는 WeChat / LINE ID)를 입력해 주세요.',
           'okT': '가이드가 준비되었습니다', 'okS': '다운로드가 자동으로 시작됩니다. 시작되지 않으면 아래 버튼을 누르세요.', 'dl': '다시 다운로드', 'ask': '질문은 Keith의 WhatsApp으로',
           'in': '가이드 내용', 'i1': '비교표', 'i1d': '{n}개 프로젝트를 한 페이지에: 가격, 평방피트당 가격, 면적, 침실, 소유 형태, 준공.',
           'i2': '프로젝트별 자료', 'i2d': '사진, 주요 수치, 관리비, 개발사, 특징.',
           'i3': '위치 지도', 'i3d': '각 프로젝트의 위치와 가까운 역.', 'i4': '월 상환액', 'i4d': '모든 프로젝트의 예상 월 상환액으로 예산에 맞는 곳을 바로 확인하세요.',
           'inc': '가이드에 포함된 프로젝트', 'more': '다른 지역 가이드', 'back': '무료 툴킷', 'n_p': '{n}개 프로젝트'},
}
try:
    import opencc
    _cc = opencc.OpenCC('s2tw').convert
    UI['zh-TW'] = {k: _cc(v) for k, v in UI['zh-CN'].items()}
except ImportError:
    UI['zh-TW'] = dict(UI['zh-CN'])


def endpoint():
    m = re.search(r"LEADS_ENDPOINT = '([^']+)'", open('lead-tracker.js', encoding='utf-8').read())
    return m.group(1) if m else ''


LCSS = '''
:root{--bg:#F7F6FB;--ink:#15142b;--grey:#5f5e74;--line:rgba(21,20,43,.09);--gold:#5E60CE;--deep:#1d1b4f;}
*{box-sizing:border-box;margin:0;padding:0;} body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6;}
a{color:inherit;text-decoration:none;} img{display:block;max-width:100%;}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif;line-height:1.18;}
.wrap{max-width:1180px;margin:0 auto;padding:0 5vw;}
.gh{background:radial-gradient(1100px 500px at 85% -10%,rgba(94,96,206,.35),transparent 60%),linear-gradient(160deg,#1d1b4f 0%,#2a2870 70%,#3b3c99 100%);color:#fff;padding:54px 0 70px;}
.gh .wrap{display:grid;grid-template-columns:1.05fr .95fr;gap:48px;align-items:start;}
.crumb{font-size:12.5px;opacity:.75;margin-bottom:18px;} .crumb a:hover{text-decoration:underline;}
.gh .eb{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22);border-radius:100px;padding:6px 14px;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;}
.gh .eb svg{width:14px;height:14px;fill:none;stroke:#fff;stroke-width:2;}
.gh h1{font-size:clamp(32px,4.4vw,52px);margin:16px 0 14px;} .gh p.sub{font-size:16px;opacity:.88;max-width:560px;}
.st{display:flex;gap:28px;margin:26px 0 30px;flex-wrap:wrap;} .st b{display:block;font-family:'Playfair Display',serif;font-size:28px;} .st span{font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;opacity:.7;}
.stack{position:relative;height:360px;max-width:520px;}
.stack img{position:absolute;width:36%;height:auto;border-radius:8px;box-shadow:0 24px 50px rgba(0,0,0,.4);border:1px solid rgba(255,255,255,.2);background:#fff;}
.stack img:nth-child(1){left:0;top:30px;transform:rotate(-6deg);} .stack img:nth-child(1){left:2%;} .stack img:nth-child(2){left:30%;top:0;z-index:2;} .stack img:nth-child(3){left:58%;top:34px;transform:rotate(6deg);}
.stack .pc{position:absolute;left:0;bottom:-6px;z-index:3;background:#fff;color:var(--deep);font-size:12px;font-weight:800;padding:6px 12px;border-radius:100px;}
.fm{background:#fff;color:var(--ink);border-radius:22px;padding:28px;box-shadow:0 30px 70px rgba(10,10,40,.35);position:relative;}
.fm h2{font-family:'Inter',sans-serif;font-size:22px;font-weight:800;} .fm .fs{color:var(--grey);font-size:13.5px;margin:4px 0 18px;}
.fl{display:block;margin-bottom:12px;} .fl span{display:block;font-size:12px;font-weight:700;color:var(--grey);margin-bottom:5px;}
.fl input,.fl select{width:100%;font:inherit;font-size:15px;padding:12px 14px;border:1.5px solid #dddcea;border-radius:12px;background:#fbfbfe;outline:none;transition:border-color .2s;}
.fl input:focus,.fl select:focus{border-color:var(--gold);background:#fff;}
.ph{display:grid;grid-template-columns:110px 1fr;gap:8px;}
.go{all:unset;box-sizing:border-box;width:100%;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:10px;background:var(--gold);color:#fff;font-weight:800;font-size:16px;padding:15px;border-radius:14px;margin-top:6px;transition:background .25s;}
.go:hover{background:var(--deep);} .go svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round;}
.priv{font-size:11.5px;color:var(--grey);margin-top:10px;display:flex;gap:6px;} .priv svg{flex-shrink:0;width:14px;height:14px;fill:none;stroke:var(--gold);stroke-width:2;margin-top:2px;}
.err{display:none;color:#b42318;font-size:12.5px;font-weight:600;margin:4px 0 6px;}
.ok{display:none;text-align:center;padding:10px 0;} .ok .ic{width:58px;height:58px;border-radius:50%;background:#e8f7ee;margin:0 auto 12px;display:flex;align-items:center;justify-content:center;}
.ok .ic svg{width:28px;height:28px;fill:none;stroke:#1f9d55;stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round;} .ok h2{margin-bottom:6px;} .ok p{color:var(--grey);font-size:14px;margin-bottom:16px;}
.ok .wa{display:inline-block;margin-top:12px;font-weight:700;color:#1f9d55;font-size:14px;}
.fm.done form{display:none;} .fm.done .ok{display:block;} .fm.done>h2,.fm.done>.fs{display:none;}
.sec{padding:64px 0 0;} .sec h2{font-size:clamp(26px,3vw,34px);margin-bottom:22px;}
.ins{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;}
.ins div{background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px;} .ins i{display:flex;width:44px;height:44px;border-radius:12px;background:#efeefb;align-items:center;justify-content:center;margin-bottom:14px;font-style:normal;font-weight:800;color:var(--gold);}
.ins b{display:block;font-size:16px;margin-bottom:6px;} .ins p{font-size:13.5px;color:var(--grey);}
.pl{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;}
.pl a{display:flex;gap:12px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:16px;padding:10px;transition:border-color .2s,transform .2s;} .pl a:hover{border-color:rgba(94,96,206,.5);transform:translateY(-2px);}
.pl img{width:64px;height:64px;border-radius:12px;object-fit:cover;flex-shrink:0;background:#eee;} .pl b{display:block;font-size:14.5px;line-height:1.3;} .pl small{color:var(--grey);font-size:12.5px;}
.og{display:flex;flex-wrap:wrap;gap:10px;padding-bottom:80px;} .og a{background:#fff;border:1px solid var(--line);border-radius:100px;padding:9px 16px;font-size:14px;font-weight:600;} .og a:hover{border-color:var(--gold);color:var(--gold);}
.og a small{color:var(--grey);font-weight:500;margin-left:4px;}
footer{border-top:1px solid var(--line);padding:26px 5vw;font-size:13px;color:var(--grey);text-align:center;}
@media(max-width:960px){.gh .wrap{grid-template-columns:1fr;gap:30px;} .stack{height:300px;} .ins{grid-template-columns:1fr 1fr;} .pl{grid-template-columns:1fr 1fr;}}
@media(max-width:600px){.gh{padding:30px 0 44px;} .ins,.pl{grid-template-columns:1fr;} .fm{padding:22px;border-radius:18px;} .st{gap:20px;} .st b{font-size:24px;} .stack{height:min(62vw,250px);}}
'''

CODES = ['+60', '+65', '+86', '+852', '+853', '+886', '+81', '+82', '+62', '+66', '+84', '+63', '+61', '+44', '+1', '+971', '+91']


def landing(g, all_g):
    f = facts(g)
    ids = g['ids']
    root = '../'
    yrs = f['yrs']
    yr_txt = ('%s–%s' % (yrs[0] or 'Ready', yrs[-1]) if len(yrs) > 1 else (str(yrs[0] or 'Ready') if yrs else 'TBC'))
    pdf = '../downloads/guides/%s.pdf' % g['slug']
    prev = ''.join('<img src="../images/guides/%s-%d.jpg" alt="" width="620" height="877">' % (g['slug'], n) for n in (1, 2, 3)
                   if os.path.exists('images/guides/%s-%d.jpg' % (g['slug'], n)))
    plist = ''.join('<a href="../property/%s.html"><img src="../%s" alt="" loading="lazy"><span><b>%s</b><small>%s</small></span></a>' % (
        A.SLUG.get(k, A.slug(A.P[k]['name'])), E(A.PHOTO.get(k, '')), E(A.P[k]['name']), E(CMP[A.P[k]['name']]['price'])) for k in ids)
    others = ''.join('<a href="%s.html">%s<small data-np="%d">%d projects</small></a>' % (o['slug'], E(o['area']), o['n'], o['n']) for o in all_g if o['slug'] != g['slug'])
    t = UI['en']
    F = lambda s, **kw: s.format(**kw)
    codes = ''.join('<option%s>%s</option>' % (' selected' if c == '+60' else '', c) for c in CODES)
    ico = {'lock': '<svg viewBox="0 0 24 24"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>',
           'doc': '<svg viewBox="0 0 24 24"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/></svg>',
           'dl': '<svg viewBox="0 0 24 24"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>'}
    wa_q = waq('Hi Keith, I downloaded the %s guide and have a few questions.' % g['area'])
    body = '''<header>
  <a class="logo" href="../"><img src="../images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Keith Nah Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="{wa}" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
<section class="gh"><div class="wrap">
  <div>
    <div class="crumb"><a href="../resources.html" data-u="back">Free Toolkit</a> › {area}</div>
    <span class="eb">{doc}<span data-u="eb">Free PDF guide</span></span>
    <h1 data-uf="h1">{h1}</h1>
    <p class="sub" data-uf="sub">{sub}</p>
    <div class="st"><div><b>{n}</b><span data-u="p">Projects</span></div><div><b>{low}</b><span data-u="from">Starting from</span></div><div><b>{free}/{n}</b><span data-u="fh">Freehold</span></div><div><b>{yrs}</b><span data-u="cy">Completion</span></div></div>
    <div class="stack">{prev}<span class="pc" data-uf="pg">PDF · {pages} pages</span></div>
  </div>
  <div class="fm" id="get">
    <h2 data-u="ft">Get the free guide</h2><p class="fs" data-u="fs">Fill in your details and the PDF downloads straight away.</p>
    <form id="gForm" novalidate>
      <label class="fl"><span data-u="name">Name</span><input name="name" autocomplete="name" required></label>
      <label class="fl"><span data-u="email">Email</span><input name="email" type="email" autocomplete="email" required></label>
      <label class="fl"><span data-u="wa">WhatsApp number</span><div class="ph"><select name="code" aria-label="Country code">{codes}</select><input name="phone" type="tel" inputmode="tel" autocomplete="tel-national"></div></label>
      <label class="fl"><span data-u="wc">WeChat / LINE ID (optional)</span><input name="wc"></label>
      <p class="err" id="gErr" data-u="need">Please fill in your name, email and WhatsApp number (or a WeChat / LINE ID).</p>
      <button type="submit" class="go"><span data-u="go">Download the PDF</span>{dlic}</button>
      <p class="priv">{lock}<span data-u="priv">Keith may contact you about this guide. Your details are never shared.</span></p>
    </form>
    <div class="ok"><div class="ic"><svg viewBox="0 0 24 24"><path d="M5 13l4 4 10-10"/></svg></div><h2 data-u="okT">Your guide is ready</h2><p data-u="okS">The download should start on its own. If it does not, tap the button below.</p>
      <a class="go" id="gDl" href="{pdf}" download><span data-u="dl">Download again</span>{dlic}</a><a class="wa" href="{waq}" target="_blank" rel="noopener" data-u="ask">Questions? WhatsApp Keith</a></div>
  </div>
</div></section>
<main class="wrap">
  <section class="sec"><h2 data-u="in">What's inside</h2><div class="ins">
    <div><i>01</i><b data-u="i1">Side-by-side table</b><p data-uf="i1d">{i1d}</p></div>
    <div><i>02</i><b data-u="i2">A sheet per project</b><p data-u="i2d">{i2d}</p></div>
    <div><i>03</i><b data-u="i3">Location map</b><p data-u="i3d">{i3d}</p></div>
    <div><i>04</i><b data-u="i4">Monthly instalments</b><p data-u="i4d">{i4d}</p></div></div></section>
  <section class="sec"><h2 data-u="inc">Projects in this guide</h2><div class="pl">{plist}</div></section>
  <section class="sec"><h2 data-u="more">Other area guides</h2><div class="og">{others}</div></section>
</main>
<footer>&copy; {year} Keith Nah Real Estate. All rights reserved.</footer>'''.format(
        wa=E(waq('Hi Keith, I am looking at new launches in %s.' % g['area'])), area=E(g['area']), doc=ico['doc'], h1=E(F(t['h1'], a=g['area'], y=YEAR)),
        sub=E(F(t['sub'], a=g['area'])), n=g['n'], low=E(rm(f['low'])), free=f['free'], yrs=E(yr_txt), prev=prev, pages=g.get('pages', ''),
        codes=codes, dlic=ico['dl'], lock=ico['lock'], pdf=pdf, waq=E(wa_q), i1d=E(F(t['i1d'], n=g['n'])), i2d=E(t['i2d']), i3d=E(t['i3d']), i4d=E(t['i4d']),
        plist=plist, others=others, year=YEAR)
    js = '''<script>(function(){var U=%s,G=%s,EP=%s;
function lang(){var l='en';try{l=localStorage.getItem('kn_lang')||'en'}catch(e){}return U[l]?l:'en';}
function fm(s){return s.replace(/\\{(\\w)\\}/g,function(_,k){return {a:G.area,y:G.year,n:k==='n'?(G.pages||G.n):G.n}[k];});}
function apply(){var L=U[lang()];document.querySelectorAll('[data-u]').forEach(function(el){var v=L[el.getAttribute('data-u')];if(v)el.textContent=v;});
document.querySelectorAll('[data-uf]').forEach(function(el){var k=el.getAttribute('data-uf'),v=L[k];if(!v)return;el.textContent=k==='pg'?v.replace('{n}',G.pages):k==='i1d'?v.replace('{n}',G.n):fm(v);});
document.querySelectorAll('[data-np]').forEach(function(el){el.textContent=L.n_p.replace('{n}',el.getAttribute('data-np'));});}
var box=document.getElementById('get'),f=document.getElementById('gForm'),err=document.getElementById('gErr'),dl=document.getElementById('gDl');
function done(auto){box.classList.add('done');if(auto){try{dl.click();}catch(e){location.href=dl.href;}}}
try{if(localStorage.getItem('kn_guide_ok'))f.querySelector('[name=name]').value=JSON.parse(localStorage.getItem('kn_guide_ok')).name||'';}catch(e){}
f.addEventListener('submit',function(e){e.preventDefault();var d={};['name','email','code','phone','wc'].forEach(function(k){d[k]=(f.elements[k].value||'').trim();});
var okMail=/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(d.email);
if(!d.name||!okMail||(!d.phone&&!d.wc)){err.style.display='block';return;}err.style.display='none';
var dev=/iPad|Tablet/i.test(navigator.userAgent)?'Tablet':/Mobi|Android|iPhone/i.test(navigator.userAgent)?'Mobile':'Desktop';
var body=JSON.stringify({type:'Quick Enquiry',source:'KNRE website',page:'Area guide: '+G.area,button:'Area guide PDF download',name:d.name,code:d.code,phone:d.phone,email:d.email,
area:G.area,look:'Free '+G.area+' guide (PDF)'+(d.wc?' · WeChat/LINE: '+d.wc:''),message:d.wc?('WeChat/LINE: '+d.wc):'',lang:document.documentElement.getAttribute('lang')||lang(),device:dev,referrer:document.referrer||'',url:location.href});
try{if(EP){if(!(navigator.sendBeacon&&navigator.sendBeacon(EP,new Blob([body],{type:'text/plain'}))))fetch(EP,{method:'POST',mode:'no-cors',keepalive:true,headers:{'Content-Type':'text/plain'},body:body});}}catch(e){}
try{localStorage.setItem('kn_guide_ok',JSON.stringify({name:d.name,t:Date.now()}));}catch(e){}
done(true);});
document.addEventListener('DOMContentLoaded',function(){var s=window.knSetLang;if(typeof s==='function')window.knSetLang=function(){var r=s.apply(this,arguments);apply();return r;};apply();});
apply();})();</script>''' % (json.dumps(UI, ensure_ascii=False), json.dumps({'area': g['area'], 'n': g['n'], 'pages': g.get('pages', ''), 'year': YEAR}, ensure_ascii=False), json.dumps(endpoint()))
    title = '%s New Launch Guide %d (Free PDF) | Keith Nah Real Estate' % (g['area'], YEAR)
    desc = 'Free PDF guide to all %d new launch projects in %s: prices, psf, sizes, completion dates, rail stations and a map.' % (g['n'], g['area'])
    page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{site}/guides/{s}.html">
<meta property="og:title" content="{t}"><meta property="og:description" content="{d}"><meta property="og:url" content="{site}/guides/{s}.html"><meta property="og:image" content="{site}/images/guides/{s}-1.jpg">
<link rel="icon" type="image/png" href="../images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
{body}
<script src="../lead-tracker.js"></script>
{js}
</body>
</html>
'''.format(t=E(title), d=E(desc), site=SITE, s=g['slug'], css=LCSS, body=body, js=js)
    return SH.apply(page, root, 'resources.html')


if __name__ == '__main__':
    gs = guides()
    build_pdfs(gs, force='--force' in sys.argv)
    os.makedirs('guides', exist_ok=True)
    for g in gs:
        open('guides/%s.html' % g['slug'], 'w', encoding='utf-8').write(landing(g, gs))
    print('guides: %d landing pages, %d PDFs' % (len(gs), sum(os.path.exists('downloads/guides/%s.pdf' % g['slug']) for g in gs)))
