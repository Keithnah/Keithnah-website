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
from urllib.parse import quote

import float_wa as FW
import site_header as SH
import i18n_pages as I18N

try:
    LISTS_OF = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'list_membership.json'), encoding='utf-8'))
except (OSError, ValueError):
    LISTS_OF = {}
try:
    PLACES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project_places.json'), encoding='utf-8'))
except (OSError, ValueError):
    PLACES = []
try:
    TAG_GROUPS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tag_groups.json'), encoding='utf-8'))
except (OSError, ValueError):
    TAG_GROUPS = {}

SITE = 'https://keithnah.com'
OUT = 'property'
WA = '60102821568'
TODAY = datetime.date.today().isoformat()
E = lambda s: html.escape(str(s if s is not None else ''), quote=True)

src = open('projects.html', encoding='utf-8').read()


try:
    COORDS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project_coords.json'), encoding='utf-8'))
except Exception:
    COORDS = {}

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
# Article page slugs written by tools/build_news_page.py
ART_PAGE = json.load(open('tools/article_slugs.json', encoding='utf-8')) if os.path.exists('tools/article_slugs.json') else {}

# Card photo and property type, by card index
# Not shown on the site: permit and licence numbers, sales gallery / showroom addresses
HIDDEN_FACTS = ['Sales Office', 'Showroom', 'Sales Gallery', 'Property Gallery', "Developer's Licence", 'Advertising Permit', 'Building Plan Approval']
PHOTO, TYPE = {}, {}
for m in re.finditer(r'data-idx="(\d+)" onclick="openDetailModal\(\1\)">(.*?)<p class="proj-loc">', src, re.S):
    k = int(m.group(1))
    im = re.search(r'<img\b(?=[^>]*\bclass="proj-photo")[^>]*\bsrc="([^"]+)"', m.group(2))
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
.lst-chips{display:flex;flex-wrap:wrap;gap:8px;}.lst-chip{background:#fff;border:1px solid var(--line);border-radius:100px;padding:9px 15px;font-size:13.5px;font-weight:500;}.lst-chip:hover{border-color:var(--gold);color:var(--gold);}
.tg-sub{color:var(--grey);font-size:14px;margin:-6px 0 18px;}
.tg-box{background:#fff;border:1px solid var(--line);border-radius:14px;padding:6px 24px;}
.tg-row{display:grid;grid-template-columns:170px 1fr;gap:16px;align-items:start;padding:18px 0;border-top:1px solid var(--line);} .tg-row:first-child{border-top:0;}
.tg-label{font-size:11px;letter-spacing:0.14em;text-transform:uppercase;color:var(--grey);font-weight:700;margin:8px 0 0;}
.tg-list{display:flex;flex-wrap:wrap;gap:8px;}
.tg{display:inline-flex;align-items:center;gap:7px;font-size:13px;font-weight:500;color:#111;background:var(--bg);border:1px solid transparent;border-radius:100px;padding:7px 14px;transition:border-color .15s,color .15s,background .15s;}
.tg svg{width:12px;height:12px;color:var(--gold);flex:0 0 12px;} .tg:hover{border-color:var(--gold);color:var(--gold);background:#fff;}
@media(max-width:700px){.tg-box{padding:4px 16px;}.tg-row{grid-template-columns:1fr;gap:10px;padding:16px 0;}.tg-label{margin:0;}}
.stats{display:grid;grid-template-columns:repeat(5,1fr);background:#fff;border:1px solid var(--line);border-radius:12px;margin-bottom:46px;}
.stat{padding:20px 22px;border-left:1px solid var(--line);} .stat:first-child{border-left:0;}
.stat span{display:block;font-size:11px;letter-spacing:0.14em;text-transform:uppercase;color:var(--grey);font-weight:600;margin-bottom:6px;}
.stat strong{font-family:'Playfair Display',serif;font-size:18px;}
section.blk{margin-bottom:50px;}
.blk h2{font-size:clamp(24px,2.6vw,32px);margin-bottom:18px;}
.blk p.lead{color:#333;font-size:16px;max-width:860px;}
.points{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(190px,1fr);gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:6px;scrollbar-width:thin;}
.point{background:#fff;border:1px solid var(--line);border-radius:10px;padding:18px;display:flex;flex-direction:column;gap:12px;scroll-snap-align:start;}
.point b{flex:0 0 32px;width:32px;height:32px;border-radius:50%;background:var(--gold);color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;}
.point p{margin:0;font-size:14.5px;line-height:1.6;}
@media(max-width:700px){.points{grid-auto-columns:78%;}}
.pi{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 10px 30px rgba(17,17,17,0.08);border:1px solid var(--line);}
.pi-head{background:linear-gradient(135deg,#5E60CE,#4A4CB8);color:#fff;text-align:center;font:700 22px/1.3 'Inter',sans-serif;padding:20px 16px;letter-spacing:0.01em;}
.pi table{width:100%;border-collapse:collapse;}
.pi th,.pi td{padding:16px 24px;text-align:left;vertical-align:top;font-size:15px;line-height:1.55;}
.pi th{width:24%;min-width:170px;background:#5E60CE;color:#fff;font-weight:600;border-bottom:1px solid rgba(255,255,255,0.22);}
.pi td{color:#222;border-bottom:1px solid var(--line);}
.pi tr:last-child th{border-bottom:0;} .pi tr:last-child td{border-bottom:0;}
.pi tr:nth-child(even) td{background:#FAFAFD;}
html[dir=rtl] .pi th,html[dir=rtl] .pi td{text-align:right;}
@media(max-width:600px){.pi th,.pi td{display:block;width:auto;padding:10px 16px;}.pi th{border-bottom:0;font-size:13px;padding-bottom:8px;}.pi td{padding-top:10px;padding-bottom:14px;}.pi-head{font-size:19px;padding:16px;}}
.amen{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px;} .amen li{list-style:none;background:#fff;border:1px solid var(--line);border-radius:100px;padding:6px 14px;font-size:13px;}
.pd-layout-selector{display:flex;gap:24px;align-items:flex-start;}
.pd-layout-sidebar{display:flex;flex-direction:column;gap:10px;width:240px;flex-shrink:0;}
.pd-layout-tab{display:flex;flex-direction:column;align-items:flex-start;gap:3px;text-align:left;width:100%;padding:14px 16px;border-radius:10px;border:1px solid var(--line);background:var(--ivory);cursor:pointer;transition:all .25s var(--ease);font-family:inherit;}
.pd-layout-tab:hover{border-color:var(--gold);}
.pd-layout-tab.active{background:var(--gold);border-color:var(--gold);}
.pd-layout-tab.active .pd-layout-tab-type,.pd-layout-tab.active .pd-layout-tab-meta{color:#fff;}
.pd-layout-tab-type{font-size:14.5px;font-weight:700;color:var(--ink);}
.pd-layout-tab-meta{font-size:12.5px;color:var(--grey);font-weight:600;}
.pd-layout-display{flex:1;min-width:0;background:var(--ivory);border:1px solid var(--line);border-radius:10px;overflow:hidden;}
.pd-layout-display-media{position:relative;display:flex;align-items:center;justify-content:center;background:#fff;padding:20px;}
.pd-layout-display-media img{width:auto;height:auto;max-width:100%;max-height:70vh;object-fit:contain;display:block;margin:0 auto;}
.pd-layout-display-body{padding:22px 24px 26px;}
.pd-layout-display-body h3{font-size:20px;margin-bottom:8px;}
.pd-layout-display-body p{font-size:14.5px;color:var(--grey);margin-bottom:16px;line-height:1.6;font-weight:500;}
.pd-layout-tags{display:flex;gap:8px;flex-wrap:wrap;}
.pd-layout-tag{padding:6px 13px;border-radius:100px;background:rgba(94,96,206,0.1);color:var(--gold);font-size:11.5px;font-weight:700;}
.pd-layout-fallback{width:100%;min-height:320px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#EDEBFB,#F9F8F6);color:var(--gold);}
.pd-layout-fallback svg{width:32%;}
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
@media(max-width:900px){.hero{grid-template-columns:1fr;gap:22px;}.pd-layout-selector{flex-direction:column;}.pd-layout-sidebar{flex-direction:row;overflow-x:auto;width:100%;gap:8px;padding-bottom:6px;}.pd-layout-tab{flex:0 0 auto;min-width:130px;width:auto;}.price{font-size:24px;}.hero h1{font-size:34px;}.stats{grid-template-columns:repeat(2,1fr);}.stat{border-left:0;border-top:1px solid var(--line);}.stat:first-child{grid-column:1/-1;border-top:0;}.wa-btn span{display:none;}.wrap{padding:0 16px;}.cta{padding:28px 20px;}}
'''
CSS += FW.FLOAT_CSS


NAV = [('', 'Home'), ('projects.html', 'View Projects'), ('compare.html', 'Compare Projects'), ('blog.html', 'News'),
       ('calculator.html', 'Calculator'), ('resources.html', 'Free Toolkit'), ('about-keith.html', 'About Keith')]


def area_slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower().replace('&', 'and')).strip('-')


def _myr(s):
    import build_area_pages
    return build_area_pages.price_rm(s)


MO_CSS = (
    '.mo-line{margin:-10px 0 22px;font-size:14px;color:var(--grey);display:flex;flex-wrap:wrap;gap:6px 10px;align-items:baseline;}'
    '.mo-line b{font-family:"Playfair Display",serif;font-size:20px;color:var(--ink);}'
    '.mo-line a{color:var(--gold);font-weight:600;font-size:13px;text-decoration:underline;text-underline-offset:3px;}'
    '.mo-box{display:grid;grid-template-columns:1.2fr 1fr;gap:0;background:#fff;border:1px solid var(--line);border-radius:14px;overflow:hidden;}'
    '.mo-in{padding:26px;display:grid;gap:18px;}'
    '.mo-in label,.mo-in .mo-row{display:grid;gap:8px;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--grey);font-weight:700;}'
    '.mo-f{display:flex;align-items:center;border:1.5px solid var(--line);border-radius:10px;padding:0 14px;background:#FBFAF7;}'
    '.mo-f:focus-within{border-color:var(--gold);}'
    '.mo-f input,.mo-f select{flex:1;border:0;background:transparent;font:600 17px Inter,sans-serif;color:var(--ink);padding:12px 6px;outline:none;min-width:0;}'
    '.mo-f em{font-style:normal;font-size:13px;color:var(--grey);text-transform:none;letter-spacing:0;}'
    '.mo-pills{display:flex;gap:8px;flex-wrap:wrap;}'
    '.mo-pills button{border:1.5px solid var(--line);background:#fff;border-radius:100px;padding:9px 16px;font:600 14px Inter,sans-serif;cursor:pointer;color:var(--ink);}'
    '.mo-pills button.on{background:var(--gold);border-color:var(--gold);color:#fff;}'
    '.mo-out{background:linear-gradient(135deg,#1d1b4f,#3b3c99);color:#fff;padding:26px;display:flex;flex-direction:column;gap:14px;}'
    '.mo-out small{font-size:12px;letter-spacing:.12em;text-transform:uppercase;opacity:.8;font-weight:600;}'
    '.mo-out strong{font-family:"Playfair Display",serif;font-size:40px;line-height:1.1;}'
    '.mo-out ul{list-style:none;display:grid;gap:8px;border-top:1px solid rgba(255,255,255,.15);padding-top:14px;}'
    '.mo-out li{display:flex;justify-content:space-between;gap:10px;font-size:14px;} .mo-out li span{opacity:.8;}'
    '.mo-acts{display:flex;flex-wrap:wrap;gap:10px;margin-top:auto;}'
    '.mo-acts .btn2{border-color:#fff;color:#fff;} .mo-acts .btn2:hover{background:#fff;color:#1d1b4f;}'
    '.mo-note{font-size:12.5px;color:var(--grey);margin-top:12px;}'
    '.mo-dp{display:flex;gap:12px;align-items:center;} .mo-dp .mo-f{flex:0 0 120px;width:120px;min-width:0;} .mo-f input{width:100%;} .mo-box>*,.mo-in>*{min-width:0;} .mo-amt{font:600 15px Inter,sans-serif;color:var(--ink);text-transform:none;letter-spacing:0;}'
    '.mo-rng{width:100%;accent-color:var(--gold);}'
    '.mo-tip{font-size:12px;font-weight:500;color:var(--grey);text-transform:none;letter-spacing:0;line-height:1.5;}'
    '@media(max-width:820px){.mo-box{grid-template-columns:1fr;}.mo-out strong{font-size:34px;}}')

MO_JS = r"""<script>
(function(){
  var box = document.getElementById('loanCalc'); if(!box) return;
  var $ = function(id){ return document.getElementById(id); };
  var num = function(s){ return parseFloat(String(s).replace(/[^\d.]/g, '')) || 0; };
  function cur(){ var c = 'MYR'; try{ c = localStorage.getItem('kn_currency') || 'MYR'; }catch(e){} return (window.KN_RATE && KN_RATE[c]) ? c : 'MYR'; }
  function money(v){ var c = cur(); if(c === 'MYR') return 'RM ' + Math.round(v).toLocaleString('en-US');
    return '~' + KN_SYM[c] + ' ' + Math.round(v * KN_RATE[c]).toLocaleString('en-US'); }
  function setDown(v, from){ v = Math.max(0, Math.min(90, isNaN(v) ? 0 : v));
    if(from !== 'in') $('moDownPct').value = v; if(from !== 'rg') $('moDownRg').value = v; return v; }
  function calc(){
    var price = num($('moPrice').value), down = Math.max(0, Math.min(90, num($('moDownPct').value))), rate = num($('moRate').value), years = num($('moYears').value) || 35;
    var loan = price * (1 - down / 100), n = years * 12, i = rate / 100 / 12;
    var inst = loan <= 0 ? 0 : (i > 0 ? loan * i / (1 - Math.pow(1 + i, -n)) : loan / n);
    $('moInst').textContent = money(inst); $('moLoan').textContent = money(loan);
    $('moDown').textContent = money(price - loan); $('moInt').textContent = money(Math.max(inst * n - loan, 0));
    $('moDownAmt').textContent = money(price - loan);
    $('moDownRg').style.setProperty('--p', down / 90 * 100 + '%');
    var h = document.querySelector('[data-mo]'); if(h) h.textContent = money(inst);
    $('moCur').value = cur();
    $('moFull').href = '../calculator.html?price=' + Math.round(price) + '&down=' + down + '&rate=' + rate + '&years=' + years + '&tab=cost';
  }
  $('moDownPct').addEventListener('input', function(){ setDown(num(this.value), 'in'); calc(); });
  $('moDownPct').addEventListener('blur', function(){ setDown(num(this.value)); calc(); });
  $('moDownRg').addEventListener('input', function(){ setDown(+this.value, 'rg'); calc(); });
  $('moPrice').addEventListener('input', calc); $('moRate').addEventListener('input', calc); $('moYears').addEventListener('change', calc);
  $('moPrice').addEventListener('blur', function(){ var v = num(this.value); this.value = v ? Math.round(v).toLocaleString('en-US') : ''; });
  $('moCur').addEventListener('change', function(){ if(window.knSetCur) knSetCur(this.value); else { try{ localStorage.setItem('kn_currency', this.value); }catch(e){} } calc(); });
  document.addEventListener('kncur', calc);
  document.addEventListener('DOMContentLoaded', calc);
  calc();
})();
</script>"""
MO_DEF = {'down': 10, 'rate': 4.0, 'years': 35}


def _instal(price, down=MO_DEF['down'], rate=MO_DEF['rate'], years=MO_DEF['years']):
    loan, n, i = price * (1 - down / 100.0), years * 12, rate / 100.0 / 12
    return loan * i / (1 - (1 + i) ** -n)


def mo_line(p):
    v = _myr(p.get('price'))
    if not v:
        return ''
    return ('<div class="mo-line"><span>Est. monthly instalment from</span><b data-mo>RM %s</b>'
            '<a href="#loanCalc">Change down payment &amp; rate</a></div>') % format(int(round(_instal(v))), ',')


def mo_block(p, name):
    v = _myr(p.get('price'))
    if not v:
        return ''
    from urllib.parse import quote_plus
    wa = 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0' % quote_plus(
        "(KNRE) Hi Keith, I'm interested in %s and would like to know the loan options." % name)
    years = ''.join('<option value="%d"%s>%d</option>' % (y, ' selected' if y == MO_DEF['years'] else '', y) for y in (35, 30, 25, 20, 15, 10))
    curs = ''.join('<option value="%s">%s</option>' % (c, c) for c in ('MYR', 'USD', 'SGD', 'CNY', 'JPY', 'KRW'))
    pills = ''.join('<button type="button" data-d="%d"%s>%d%%</button>' % (d, ' class="on"' if d == MO_DEF['down'] else '', d) for d in (10, 20, 30, 40))
    return ('<style>%s</style><section class="blk" id="loanCalc"><h2>Monthly Instalment Estimate</h2><div class="mo-box"><div class="mo-in">'
            '<label><span>Property price</span><div class="mo-f"><em>RM</em><input id="moPrice" inputmode="numeric" value="%s" aria-label="Property price"></div></label>'
            '<label><span>Down payment</span><div class="mo-dp"><div class="mo-f"><input id="moDownPct" inputmode="decimal" value="%s" aria-label="Down payment"><em>%%</em></div><div class="mo-amt" id="moDownAmt"></div></div>'
            '<input type="range" class="mo-rng" id="moDownRg" min="0" max="90" step="1" value="%s" aria-label="Down payment"></label>'
            '<label><span>Interest rate (%% p.a.)</span><div class="mo-f"><input id="moRate" inputmode="decimal" value="%.2f" aria-label="Interest rate"><em>%%</em></div></label>'
            '<label><span>Loan tenure (years)</span><div class="mo-f"><select id="moYears" aria-label="Loan tenure">%s</select></div>'
            '<small class="mo-tip">Malaysians can borrow until age 70. Foreigners usually get a shorter tenure; contact Keith for advice.</small></label>'
            '<label><span>Show in currency</span><div class="mo-f"><select id="moCur" aria-label="Currency">%s</select></div></label>'
            '</div><div class="mo-out"><small>Estimated monthly instalment</small><strong id="moInst">RM 0</strong>'
            '<ul><li><span>Loan amount</span><b id="moLoan"></b></li><li><span>Down payment</span><b id="moDown"></b></li><li><span>Total interest</span><b id="moInt"></b></li></ul>'
            '<div class="mo-acts"><a class="btn2" id="moFull" href="../calculator.html">Stamp duty &amp; legal fees →</a>'
            '<a class="wa-btn" href="%s" target="_blank" rel="noopener">Ask Keith about loan options</a></div></div></div>'
            '<p class="mo-note">Estimate only, based on the starting price. Your bank decides the final loan amount, interest rate and tenure; foreign buyers may need a larger down payment.</p>'
            '</section>%s') % (MO_CSS, format(int(v), ','), MO_DEF['down'], MO_DEF['down'], MO_DEF['rate'], years, curs, E(wa), MO_JS)


try:
    VIDEOS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project_videos.json'), encoding='utf-8'))
except (OSError, ValueError):
    VIDEOS = {}
YT_CSS = ('.yt-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px;}'
          '.yt{position:relative;aspect-ratio:16/9;border-radius:14px;overflow:hidden;background:#000;cursor:pointer;box-shadow:0 14px 34px rgba(17,17,17,.12);}'
          '.yt img{width:100%;height:100%;object-fit:cover;transition:transform .4s;}'
          '.yt:hover img{transform:scale(1.03);}'
          '.yt button{position:absolute;inset:0;margin:auto;width:76px;height:54px;border:0;border-radius:14px;background:rgba(255,0,0,.9);cursor:pointer;display:flex;align-items:center;justify-content:center;}'
          '.yt button svg{width:26px;height:26px;fill:#fff;}'
          '.yt iframe{position:absolute;inset:0;width:100%;height:100%;border:0;}'
          '.yt-more{display:inline-block;margin-top:14px;color:var(--gold);font-weight:600;font-size:14px;}')
YT_JS = """<script>
document.querySelectorAll('.yt[data-id]').forEach(function(el){
  el.addEventListener('click', function(){
    if(el.querySelector('iframe')) return;
    el.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + el.getAttribute('data-id') + '?autoplay=1&rel=0" title="' + el.getAttribute('data-title') + '" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>';
  });
});
</script>"""


try:
    VMETA = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'video_meta.json'), encoding='utf-8'))
except (OSError, ValueError):
    VMETA = {}


def _vclean(s):
    s = re.sub(r'(?<![A-Za-z])KLCC(?![A-Za-z])', 'KL City Centre', s or '', flags=re.I)   # site wording rules apply to video titles too
    s = re.sub(r'(?<![A-Za-z])air\s*bnb(?![A-Za-z])', 'short-stay', s, flags=re.I)
    return re.sub(r'\s+', ' ', s.replace('#', ' ')).strip()


def video_ld(ids, display):
    """VideoObject structured data (needs the upload date, from tools/fetch_video_meta.py)."""
    out = []
    for v in ids:
        m = VMETA.get(v)
        if not m or not m.get('date'):
            continue
        title = _vclean(m.get('title')) or '%s video tour' % display
        out.append({'@context': 'https://schema.org', '@type': 'VideoObject', 'name': title[:100],
                    'description': '%s video tour by Keith Nah: %s' % (display, title),
                    'thumbnailUrl': 'https://i.ytimg.com/vi/%s/hqdefault.jpg' % v, 'uploadDate': m['date'],
                    'embedUrl': 'https://www.youtube.com/embed/%s' % v, 'url': 'https://www.youtube.com/watch?v=%s' % v,
                    'author': {'@type': 'Person', 'name': 'Keith Nah', 'url': 'https://www.youtube.com/@KeithNahRealEstate'}})
    return ('<script type="application/ld+json">%s</script>' % json.dumps(out, ensure_ascii=False).replace('</', '<\\/')) if out else ''


def video_block(name, display):
    ids = VIDEOS.get(name) or []
    if not ids:
        return ''
    cards = ''.join(
        '<div class="yt" data-id="%s" data-title="%s video tour" role="button" tabindex="0" aria-label="Play %s video">'
        '<img src="https://i.ytimg.com/vi/%s/hqdefault.jpg" alt="%s video tour by Keith Nah" loading="lazy">'
        '<button type="button" aria-label="Play"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></button></div>' % (
            v, E(display), E(display), v, E(display)) for v in ids)
    return ('<style>%s</style><section class="blk" id="video"><h2>Video Tour</h2><div class="yt-grid">%s</div>'
            '<a class="yt-more" href="https://www.youtube.com/@KeithNahRealEstate" target="_blank" rel="noopener">More videos on Keith\'s YouTube channel →</a></section>%s') % (
        YT_CSS, cards, YT_JS) + video_ld(ids, display)


# Market notes about each project (tools/note_links.py): written for the notes builder, shown on the pages.
import note_links as NL
PIDX = [{'name': P[i]['name'], 'slug': SLUGS[i], 'state': (PLACES[i] if i < len(PLACES) else ('', ''))[0],
         'area': (PLACES[i] if i < len(PLACES) else ('', P[i].get('tag', '')))[1],
         'dev': str((P[i].get('details_extra') or {}).get('Developer', ''))} for i in range(len(P))]
json.dump(PIDX, open(NL.INDEX, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
NOTE_LIST = NL.notes()
NOTES_OF = {}
for _n in NOTE_LIST:
    for _p in NL.related(_n, PIDX):
        NOTES_OF.setdefault(_p['slug'], []).append(_n)


import hubs_data as HB
HUBS = HB.compute(P, SLUGS, PLACES)
json.dump(HUBS, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hubs.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
DEV_OF = {i: (b, d) for b, d in HUBS['developers'].items() for i in d['ix']}


def hub_stations(i):
    st = [s for s in HUBS['stations'].values() if i in s['ix']]
    if not st:
        return ''
    return '<div style="margin-top:18px">%s<div class="hb-chips">%s</div></div>' % (HB.tx('b_near', tag='p', cls='hb-sub'), ''.join(
        '<a class="hb-chip" href="../station/%s.html">🚆 %s %s</a>' % (s['slug'], E(s['label']), HB.tx('n_proj', tag='b', n=len(s['ix']))) for s in st))


def hub_vs(i, display):
    ps = [x for x in HUBS['pairs'] if i in (x['a'], x['b'])]
    if not ps:
        return ''
    cards = ''.join('<a href="../vs/%s.html"><small>%s</small>%s vs %s</a>' % (x['slug'], E(x['area']), E(P[x['a']]['name']), E(P[x['b']]['name'])) for x in ps)
    return '<section class="blk">%s<div class="hb-vs">%s</div></section>' % (HB.tx('b_cmp', tag='h2', x=display), cards)


def notes_block(i):
    """Up to 3 notes: first those about this project, then the latest about its state."""
    mine = list(NOTES_OF.get(SLUGS[i], []))
    for n in NOTE_LIST:
        if len(mine) >= 3:
            break
        if n not in mine and n['area'].get('en') == PIDX[i]['state']:
            mine.append(n)
    mine = mine[:3]
    if not mine:
        return ''
    data = {n['_id']: {'t': n['title'], 'a': n['area']} for n in mine}
    cards = ''.join('<a class="art" href="../%s"><small><span data-na="%s">%s</span> · %s</small><h3 data-nt="%s">%s</h3></a>' % (
        n['_page'], n['_id'], E(n['area'].get('en', '')), E(n['date']), n['_id'], E(n['title'].get('en', ''))) for n in mine)
    js = ('<script>(function(){var D=%s,H=%s,l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}'
          'function go(){try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}var h=document.getElementById("knNotesH");if(h)h.textContent=H[l]||H.en;'
          'document.querySelectorAll("[data-nt]").forEach(function(e){var x=D[e.getAttribute("data-nt")];e.textContent=x.t[l]||x.t.en;});'
          'document.querySelectorAll("[data-na]").forEach(function(e){var x=D[e.getAttribute("data-na")];e.textContent=x.a[l]||x.a.en;});}'
          'go();document.addEventListener("DOMContentLoaded",go);})();</script>') % (
        json.dumps(data, ensure_ascii=False).replace('</', '<\\/'), json.dumps(NL.NOTES_LBL, ensure_ascii=False))
    return '<section class="blk"><h2 id="knNotesH">%s</h2><div class="cards">%s</div>%s</section>' % (E(NL.NOTES_LBL['en']), cards, js)


def page(i):
    p, tg, slug = P[i], TAGS[i], SLUGS[i]
    name, display = p['name'], tg[0]
    url = '%s/%s/%s.html' % (SITE, OUT, slug)
    photo = PHOTO.get(i, '')
    state, area = PLACES[i] if i < len(PLACES) else ('', p['tag'])
    title = '%s | Price, Floor Plan & Unit Types | Keith Nah' % display
    bits = [x for x in [p.get('price'), p.get('size'), p.get('rooms'), p.get('tenure')] if x]
    desc = '%s, %s: %s. Completion %s. See floor plans, unit types and nearby projects, and WhatsApp Keith Nah for the latest price.' % (
        display, p['loc'], ', '.join(bits), p.get('completion') or 'to be confirmed')
    msg = "Hi Keith, I'm interested in %s and would like to find out more." % name

    stats = ''.join('<div class="stat"><span>%s</span><strong>%s</strong></div>' % (E(k), SH.price_tag(E(v), _myr(v)) if k == 'Starting Price' else E(v)) for k, v in [
        ('Starting Price', p.get('price')), ('Size', p.get('size')), ('Bedrooms', p.get('rooms')),
        ('Tenure', p.get('tenure')), ('Completion', p.get('completion'))] if v)
    order = ['This project', 'Location & landmarks', 'Transit', 'Tenure & status', 'Price & unit type', 'Area & developer', '中文搜索']
    groups = {g: [] for g in order}
    low = name.lower()
    for t_ in tg:
        if t_.lower().startswith(low):
            g = 'This project'
        elif re.search(r'[\u4e00-\u9fff]', t_):
            g = '中文搜索'
        elif t_ in TAG_GROUPS:
            g = TAG_GROUPS[t_]
        elif re.search(r'\bnear\b', t_, re.I):
            g = 'Location & landmarks'
        elif re.search(r'^(freehold|leasehold) ', t_, re.I):
            g = 'Tenure & status'
        else:
            g = 'Area & developer'
        groups[g].append(t_)
    groups = [(g, groups[g]) for g in order]
    tags = ''.join('<div class="tg-row"><p class="tg-label">%s</p><div class="tg-list">%s</div></div>' % (E(lbl), ''.join(
        '<a class="tg" href="../projects.html?tag=%s#tagSection">%s<span>%s</span></a>' % (E(x.replace(' ', '+')), TAG_SVG, E(x)) for x in items))
        for lbl, items in groups if items)
    points = ''.join('<div class="point"><b>%d</b><p>%s</p></div>' % (n + 1, E(x)) for n, x in enumerate(p.get('selling_points') or []))
    extra = dict(p.get('details_extra') or {})
    for k in HIDDEN_FACTS:
        extra.pop(k, None)
    rows = [('Project Name', display), ('Developer', extra.pop('Developer', '')), ('Location', p.get('loc')),
            ('Property Type', TYPE.get(i, 'Residential')), ('Tenure', p.get('tenure')), ('Status', p.get('status')),
            ('Starting Price', p.get('price')), ('Size', p.get('size')), ('Bedrooms', p.get('rooms')), ('Completion', p.get('completion'))]
    rows += list(extra.items())
    facts = ''.join('<tr><th scope="row">%s</th><td>%s%s</td></tr>' % (E(k), E(v), (' ' + HB.tx('b_devlink', tag='a', cls='hb-devlink', attrs='href="../developer/%s.html"' % DEV_OF[i][1]['slug'], n=len(DEV_OF[i][1]['ix']), d=DEV_OF[i][0])) if k == 'Developer' and i in DEV_OF else '') for k, v in rows if v)
    amen = ''.join('<li>%s</li>' % E(a) for a in (p.get('amenities') or []))
    LS = p.get('layouts') or []
    FALLBACK = '<div class="pd-layout-fallback"><svg viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="1.4"><rect x="10" y="10" width="80" height="80"/><line x1="50" y1="10" x2="50" y2="60"/><line x1="10" y1="60" x2="90" y2="60"/><line x1="70" y1="60" x2="70" y2="90"/></svg></div>'
    tabs = ''.join(
        '<button type="button" class="pd-layout-tab%s" role="tab" aria-selected="%s" aria-controls="lay-%d" data-i="%d"><span class="pd-layout-tab-type">%s</span><span class="pd-layout-tab-meta">%s</span></button>' % (
            ' active' if n == 0 else '', 'true' if n == 0 else 'false', n, n, E(l.get('type')), E(l.get('size')))
        for n, l in enumerate(LS))
    panels = ''.join(
        '<div class="lay-panel" id="lay-%d" role="tabpanel"%s><div class="pd-layout-display-media">%s</div>'
        '<div class="pd-layout-display-body"><h3>%s</h3><p>%s</p><div class="pd-layout-tags">%s</div></div></div>' % (
            n, '' if n == 0 else ' hidden',
            ('<img src="%s" alt="%s %s floor plan"%s>' % (E(up(l['img'])), E(display), E(l.get('type')), '' if n == 0 else ' loading="lazy"')) if l.get('img') else FALLBACK,
            E(l.get('type')), E(l.get('desc')),
            ''.join('<span class="pd-layout-tag">%s</span>' % E(x) for x in [l.get('size'), l.get('rooms')] if x))
        for n, l in enumerate(LS))
    layouts = ('<div class="pd-layout-selector"><div class="pd-layout-sidebar" role="tablist" aria-label="Unit types">%s</div>'
               '<div class="pd-layout-display">%s</div></div>' % (tabs, panels)) if LS else ''
    fits = ''.join('<div class="fit"><h3>%s</h3><p>%s</p></div>' % (E(f.get('title')), E(f.get('desc'))) for f in (p.get('buyer_fit') or []))
    near = ''.join(
        '<a class="card" href="%s.html">%s<div><h3>%s</h3><small>%s</small><span>%s</span></div></a>' % (
            SLUGS[j], ('<img src="%s" alt="%s" loading="lazy">' % (E(up(PHOTO[j])), E(P[j]['name'])) if PHOTO.get(j) else '<i class="noimg"></i>'),
            E(P[j]['name']), E(P[j]['loc']), E(P[j].get('price')))
        for j in (p.get('nearby') or []) if 0 <= j < len(P) and j != i)
    arts = ''.join('<a class="art" href="%s"><small>%s</small><h3>%s</h3></a>' % (
        ('../article/%s.html' % ART_PAGE[a]) if a in ART_PAGE else '../blog.html?article=' + a, E(ART[a][0]), E(ART[a][1]))
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
    # Richer place data for search engines: map position, town/state, and the key facts as properties.
    _loc = [x.strip() for x in (p.get('loc') or '').split(',') if x.strip()]
    if len(_loc) >= 2:
        ld[1]['address']['addressLocality'] = _loc[-2]
        ld[1]['address']['addressRegion'] = _loc[-1]
    _c = COORDS.get(name)
    if _c:
        ld[1]['geo'] = {'@type': 'GeoCoordinates', 'latitude': _c[0], 'longitude': _c[1]}
    _facts = dict(rows)
    ld[1]['additionalProperty'] = [{'@type': 'PropertyValue', 'name': k_, 'value': str(_facts[k_])}
                                   for k_ in ('Starting Price', 'Size', 'Bedrooms', 'Tenure', 'Completion', 'Status', 'Developer') if _facts.get(k_)]
    _u = re.sub(r'[^0-9]', '', str(_facts.get('Total Units') or _facts.get('Number of Units') or ''))
    if _u and len(_u) <= 5:
        ld[1]['numberOfAccommodationUnits'] = {'@type': 'QuantitativeValue', 'value': int(_u)}
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
<style>{css}{hub_css}</style>
</head>
<body>
<header>
  <a class="logo" href="../"><img src="{logo}" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Keith Nah Real Estate</small></span></a>
  <nav>{nav}</nav>
  <a class="wa-btn" href="{wa}" target="_blank" rel="noopener">{wasvg}<span>WhatsApp Keith</span></a>
</header>
<main class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="../">Home</a><span>›</span><a href="../projects.html">Projects</a><span>›</span>{statecrumb}<a href="{areahref}">{area}</a><span>›</span><strong>{display}</strong></nav>
  <div class="hero">
    <div class="hero-img">{heroimg}</div>
    <div>
      <div class="badges"><span class="badge">{status}</span><span class="badge alt">{area}</span><span class="badge alt">{ptype}</span></div>
      <h1>{display}</h1>
      <p class="loc">{loc}</p>
      <div class="price"><small>Starting Price</small>{price}</div>{moline}
      <div class="ctas"><a class="wa-btn" href="{wa}" target="_blank" rel="noopener">{wasvg}WhatsApp Keith</a><a class="btn2" href="../compare.html">Compare projects</a></div>
    </div>
  </div>
  <div class="stats">{stats}</div>
  <section class="blk"><h2>About {display}</h2><p class="lead">{overview}</p></section>
  {points_blk}
  {facts_blk}
  <section class="blk"><h2>Location</h2><p class="lead">{loctext}</p>{amen_blk}{stn_blk}</section>
  {video_blk}
  {layouts_blk}
  {fits_blk}
  {mo_blk}
  {lists_blk}
  {near_blk}
  {vs_blk}
  {arts_blk}
  {notes_blk}
  {tags_blk}
  <div class="cta"><h2>Want Keith's take on {display}?</h2><p>Ask for the latest price, available units and the full floor plans.</p><a class="wa-btn" href="{wa}" target="_blank" rel="noopener">{wasvg}WhatsApp Keith About This Project</a></div>
  <p class="note">Prices, sizes and availability are indicative and subject to change. Confirm current figures with Keith before making decisions.</p>
</main>
<footer>&copy; 2026 Keith Nah Real Estate · <a href="../projects.html">All projects</a> · <a href="../best/">Best new launch lists</a> · <a href="../about-keith.html">About Keith</a> · <a href="../privacy-policy.html">Privacy Policy</a> · <a href="../terms-of-use.html">Terms of Use</a> · <a href="https://www.youtube.com/@KeithNahRealEstate" target="_blank" rel="noopener">YouTube</a> · <a href="https://www.instagram.com/keithnah_/" target="_blank" rel="noopener">Instagram</a></footer>
{floatwa}
<script>
document.addEventListener('click',function(e){{
  var b=e.target.closest('.pd-layout-tab'); if(!b) return;
  var box=b.closest('.pd-layout-selector'), i=b.getAttribute('data-i');
  box.querySelectorAll('.pd-layout-tab').forEach(function(x){{ var on=x===b; x.classList.toggle('active',on); x.setAttribute('aria-selected',on?'true':'false'); }});
  box.querySelectorAll('.lay-panel').forEach(function(p){{ p.hidden=p.id!=='lay-'+i; }});
}});
</script>
<script src="../lead-tracker.js"></script>
{hub_js}
</body>
</html>
'''.format(
        floatwa=FW.float_html(E(wa(msg))),
        title=E(title), desc=E(desc), kw=E(', '.join(tg)), url=E(url), icon=E(up(ICON)), logo=E(up(LOGO)),
        ogimg=('<meta property="og:image" content="%s/%s">\n' % (SITE, E(photo))) if photo else '',
        ld=json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'), css=CSS, nav=nav, wa=E(wa(msg)), wasvg=WA_SVG,
        areahash=E(quote(state + '/' + area if state else area, safe='/')), area=E(area),
        areahref=('../area/%s.html' % area_slug(area)) if state and os.path.exists('area/%s.html' % area_slug(area)) else '../projects.html#' + E(quote(state + '/' + area if state else area, safe='/')),
        statecrumb=('<a href="%s">%s</a><span>›</span>' % ((('../area/%s.html' % area_slug(state)) if os.path.exists('area/%s.html' % area_slug(state)) else '../projects.html#' + E(quote(state))), E(state))) if state else '', display=E(display),
        heroimg=('<img src="%s" alt="%s" fetchpriority="high">' % (E(up(photo)), E(display))) if photo else '<div class="hero-ph"><svg viewBox="0 0 200 200" fill="none" stroke="currentColor" stroke-width="2"><path d="M60 190V70l40-30 40 30v120z"/><path d="M60 90h80M60 110h80M60 130h80M60 150h80M85 190v-25h30v25"/></svg></div>',
        status=E(p.get('status')), ptype=E(TYPE.get(i, 'Residential')), loc=E(p['loc']), price=SH.price_tag(E(p.get('price')), _myr(p.get('price'))), moline=mo_line(p), mo_blk=mo_block(p, name), video_blk=video_block(name, display),
        tags=tags, stats=stats, overview=E(p.get('overview')), loctext=E(p.get('loc_text')),
        points_blk=('<section class="blk"><h2>Top Highlights</h2><div class="points">%s</div></section>' % points) if points else '',
        facts_blk=('<section class="blk"><h2>Project Details</h2><div class="pi"><div class="pi-head">Project Information</div><table>%s</table></div></section>' % facts) if facts else '',
        amen_blk=('<ul class="amen">%s</ul>' % amen) if amen else '',
        layouts_blk=('<section class="blk"><h2>%s Floor Plans &amp; Unit Types</h2><div class="layouts">%s</div></section>' % (E(display), layouts)) if layouts else '',
        lists_blk=(('<section class="blk"><h2>Featured in these lists</h2><div class="lst-chips">%s</div></section>' % ''.join(
            '<a class="lst-chip" href="../best/%s.html">%s</a>' % (E(s), E(t2)) for s, t2 in LISTS_OF.get(str(i), []))) if LISTS_OF.get(str(i)) else ''),
        tags_blk=('<section class="blk tg-sec"><h2>Popular Searches for %s</h2><p class="tg-sub">Tap a tag to see every project that matches it.</p><div class="tg-box">%s</div></section>' % (E(display), tags)) if tg else '',
        fits_blk=('<section class="blk"><h2>Who Should Consider %s?</h2><div class="fits">%s</div></section>' % (E(display), fits)) if fits else '',
        near_blk=('<section class="blk"><h2>Nearby Projects</h2><div class="cards">%s</div></section>' % near) if near else '',
        arts_blk=('<section class="blk"><h2>Related Articles</h2><div class="cards">%s</div></section>' % arts) if arts else '',
        notes_blk=notes_block(i), stn_blk=hub_stations(i), vs_blk=hub_vs(i, display),
        hub_css=HB.CSS, hub_js=HB.js() if (i in DEV_OF or any(i in s['ix'] for s in HUBS['stations'].values()) or any(i in (x['a'], x['b']) for x in HUBS['pairs'])) else '')


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
          'return s ? \'<a class="pd-page-link" href="property/\'+s+\'.html">View full project page &rarr;</a>\' : \'\'; }\n'
          '/* Every project opens its own page */\nwindow.openDetailModal=function(i){ var s=KN_SLUGS[i]; if(s) location.href=\'property/\'+s+\'.html\'; };</script>' % json.dumps(SLUGS))
    t = t.replace('<script src="lead-tracker.js"></script>', js.lstrip('\n') + '\n<script src="lead-tracker.js"></script>', 1)
    css = '  .proj-page-link{color:inherit;} .proj-page-link:hover{color:var(--gold);}\n  .pd-page-link{display:inline-block; margin:6px 0 4px; font:600 13px \'Inter\',sans-serif; color:var(--gold); border-bottom:1px solid currentColor;}\n'
    if '.pd-page-link{' not in t:
        t = t.replace('  /* ---------- PROJECT TAGS ---------- */', css + '  /* ---------- PROJECT TAGS ---------- */', 1)
    src = t
    open('projects.html', 'w', encoding='utf-8').write(t)


def link_home_page():
    """Make the Home page's featured project cards open the project pages (idempotent)."""
    path = 'index.html'
    h = open(path, encoding='utf-8').read()
    i = h.index('PROJECT_DETAILS = ')
    HP = json.JSONDecoder().raw_decode(h[h.index('=', i) + 1:].lstrip())[0]
    by_name = {p['name']: SLUGS[k] for k, p in enumerate(P)}
    hs = [by_name.get(p['name'], '') for p in HP]
    missing = [p['name'] for p, s in zip(HP, hs) if not s]
    assert not missing, missing
    h = re.sub(r'<script id="kn-page-links">.*?</script>\n', '', h, flags=re.S)
    h = re.sub(r'<h3><a class="proj-page-link" href="property/[^"]+" onclick="event.stopPropagation\(\)">(.*?)</a></h3>', r'<h3>\1</h3>', h)

    def card(m):
        k = int(m.group(1))
        return re.sub(r'<h3>(.*?)</h3>', lambda x: '<h3><a class="proj-page-link" href="property/%s.html" onclick="event.stopPropagation()">%s</a></h3>' % (hs[k], x.group(1)), m.group(0), count=1)
    h, n = re.subn(r'data-idx="(\d+)" onclick="openDetailModal\(\1\)">.*?<h3>.*?</h3>', card, h, flags=re.S)
    js = ('<script id="kn-page-links">var KN_HOME_SLUGS = %s;\n'
          'window.openDetailModal=function(i){ var s=KN_HOME_SLUGS[i]; if(s) location.href=\'property/\'+s+\'.html\'; };</script>' % json.dumps(hs))
    h = h.replace('<script src="lead-tracker.js"></script>', js + '\n<script src="lead-tracker.js"></script>', 1)
    if '.proj-page-link{' not in h:
        h = h.replace('</style>', '  .proj-page-link{color:inherit;}\n</style>', 1)
    open(path, 'w', encoding='utf-8').write(h)
    return n


def write_sitemap():
    main = [('', '1.0', 'weekly'), ('projects.html', '0.9', 'weekly'), ('compare.html', '0.7', 'monthly'),
            ('blog.html', '0.8', 'weekly'), ('calculator.html', '0.7', 'monthly'), ('find-my-home.html', '0.7', 'weekly'), ('mm2h.html', '0.7', 'monthly'), ('resources.html', '0.7', 'monthly'),
            ('about-keith.html', '0.8', 'monthly'), ('privacy-policy.html', '0.3', 'yearly'), ('terms-of-use.html', '0.3', 'yearly')]
    rows = [(SITE + '/' + u, pr, cf) for u, pr, cf in main] + [('%s/%s/%s.html' % (SITE, OUT, s), '0.8', 'monthly') for s in SLUGS]
    import glob
    rows += [('%s/%s' % (SITE, p), '0.8', 'weekly') for p in sorted(glob.glob('area/*.html'))]
    rows += [('%s/best/' % SITE, '0.8', 'weekly')] + [('%s/%s' % (SITE, p), '0.7', 'weekly') for p in sorted(glob.glob('best/*.html')) if not p.endswith('index.html')]
    rows += [('%s/%s' % (SITE, p), '0.6', 'monthly') for p in sorted(glob.glob('topic/*.html'))]
    rows += [('%s/%s' % (SITE, p), '0.6', 'yearly') for p in sorted(glob.glob('article/*.html'))]
    x = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    x += ''.join('  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>\n' % (E(u), TODAY, cf, pr) for u, pr, cf in rows)
    open('sitemap.xml', 'w', encoding='utf-8').write(x + '</urlset>\n')
    return len(rows)


if __name__ == '__main__':
    I18N.USE_KN[0] = True
    I18N.DATA.update(v for p in P for f in ('size', 'rooms', 'tenure', 'completion', 'price', 'status') for v in [p.get(f)] if v)
    I18N.DATA.update(v for p in P for l in (p.get('layouts') or []) for v in (l.get('size'), l.get('rooms')) if v)
    I18N.DATA.update(v for p in P for k, v in (p.get('details_extra') or {}).items() if k == 'Title' and isinstance(v, str))
    os.makedirs(OUT, exist_ok=True)
    for i in range(len(P)):
        open('%s/%s.html' % (OUT, SLUGS[i]), 'w', encoding='utf-8').write(SH.apply(page(i), '../', 'projects.html'))
    link_projects_page()
    print('home page cards linked:', link_home_page())
    n = write_sitemap()
    print('wrote %d project pages in %s/, linked projects.html, sitemap has %d URLs' % (len(P), OUT, n))
