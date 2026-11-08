"""Area and state landing pages: "New launch condos in <Area> (2026)".

One page per area (area/<slug>.html) and per state (area/<state>.html), built
from the project data in projects.html and tools/project_places.json: intro,
key numbers, project cards, a comparison table, FAQ (with FAQPage data) and
links to the other areas of the state.

    python3 tools/build_area_pages.py            # writes area/*.html (for the live site)
    python3 tools/build_area_pages.py --preview DIR   # standalone preview copy with absolute links
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import float_wa as FW
import site_header as SH
from collections import OrderedDict

SITE = 'https://keithnah.com'
YEAR = 2026
E = lambda s: html.escape(str(s if s is not None else ''), quote=True)

src = open('projects.html', encoding='utf-8').read()


def js(name):
    i = src.index(name) + len(name)
    return json.JSONDecoder().raw_decode(src[i:].lstrip())[0]


P = js('const PROJECT_DETAILS = ')
PLACES = json.load(open('tools/project_places.json', encoding='utf-8'))
PHOTO, TYPE = {}, {}
for m in re.finditer(r'data-idx="(\d+)" onclick="openDetailModal\(\1\)">(.*?)<p class="proj-loc">', src, re.S):
    k = int(m.group(1))
    im = re.search(r'<img\b(?=[^>]*\bclass="proj-photo")[^>]*\bsrc="([^"]+)"', m.group(2))
    PHOTO[k] = im.group(1) if im else ''
    ty = re.search(r'badge-type[^"]*">([^<]+)<', m.group(2))
    TYPE[k] = ty.group(1) if ty else 'Residential'
SLUG = {}
for m in re.finditer(r'data-idx="(\d+)" onclick="openDetailModal\(\1\)">.*?href="property/([^"]+)\.html"', src, re.S):
    SLUG[int(m.group(1))] = m.group(2)

STATES = ['Kuala Lumpur', 'Selangor', 'Penang', 'Johor', 'Melaka', 'Sabah', 'Terengganu', 'Kelantan']

# Short, factual introductions. Facts that change (prices, counts, completion) come from the data.
INTRO = {
    'Kuala Lumpur': "Kuala Lumpur is Malaysia's capital and its busiest new-launch market, from KL City Centre and TRX to Bukit Bintang, Bangsar, Bukit Jalil and Taman Desa, all linked by the MRT, LRT and Monorail network.",
    'Selangor': "Selangor surrounds Kuala Lumpur and offers more space for the money, with new townships such as Kwasa Damansara and established addresses in Petaling Jaya, Damansara and Subang Jaya.",
    'Penang': "Penang combines a UNESCO heritage city in George Town with an industrial and tech hub around Bayan Lepas and Batu Kawan, and new homes on both the island and the mainland.",
    'Johor': "Johor Bahru sits across the Causeway from Singapore. The Rapid Transit System (RTS) Link to Woodlands is a major draw for new launches around the city centre and Bukit Chagar.",
    'Melaka': "Melaka City is a UNESCO World Heritage city and one of Malaysia's leading domestic tourism destinations.",
    'Sabah': "Kota Kinabalu is Sabah's capital and the gateway to East Malaysia, with a growing waterfront city centre.",
    'Terengganu': "Kuala Terengganu is the capital of Terengganu on the east coast, known for its waterfront, Chinatown and islands.",
    'Kelantan': "Kota Bharu is the capital of Kelantan, with Kubang Kerian as its medical and university hub.",
    'KL City Centre': "KL City Centre is the city's financial and lifestyle core around the Petronas Twin Towers and KL City Centre Park, with Jalan Ampang, Jalan Sultan Ismail, Embassy Row and Kampung Baru on its edges. Most projects here are high-rise suites within walking distance of an LRT or MRT station.",
    'Bukit Bintang': "Bukit Bintang is KL's shopping and entertainment district, home to Pavilion Kuala Lumpur, Lot 10 and the Bukit Bintang City Centre (BBCC) development, served by MRT and Monorail stations.",
    'TRX': "Tun Razak Exchange (TRX) is Kuala Lumpur's new international financial district, built around the Exchange 106 tower, The Exchange TRX mall and a large MRT interchange.",
    'Bukit Jalil': "Bukit Jalil in southern Kuala Lumpur grew around the National Stadium and is now anchored by Pavilion Bukit Jalil and the 80-acre Bukit Jalil Recreational Park, with LRT stations and direct highway links.",
    'Damansara Heights': "Damansara Heights is one of Kuala Lumpur's most established upmarket neighbourhoods, next to Pavilion Damansara Heights and the Semantan MRT station.",
    'Bangsar': "Bangsar is a mature, leafy neighbourhood popular with expats and families, with Bangsar Village, Bangsar Shopping Centre and quick access to Mid Valley and KL Sentral.",
    'Bangsar South': "Bangsar South is a transit-oriented city next to Kerinchi LRT station, with offices, Nexus, The Sphere and a 6-acre park.",
    'Taman Desa': "Taman Desa is a mature neighbourhood off Jalan Klang Lama, close to Mid Valley and Bangsar, with easy access to several highways.",
    'Kwasa Damansara': "Kwasa Damansara is a planned transit-oriented city in Selangor with two MRT stations, Kwasa Damansara and Kwasa Sentral, next to Kota Damansara.",
    'Petaling Jaya': "Petaling Jaya is Selangor's established city next to Kuala Lumpur, with mature neighbourhoods, malls, LRT and MRT stations and many schools.",
    'Bandar Sri Damansara': "Bandar Sri Damansara is a mature township in north-west Kuala Lumpur and Petaling Jaya, close to Desa ParkCity and Kepong.",
    'Ara Damansara': "Ara Damansara is a Petaling Jaya township near Subang Airport, with LRT stations and links to the Federal Highway.",
    'Damansara Damai': "Damansara Damai is a residential area in north Petaling Jaya, close to Damansara Perdana and the LDP.",
    'Damansara Perdana': "Damansara Perdana is a township in north Petaling Jaya near Mutiara Damansara and the Damansara–Puchong Expressway (LDP).",
    'Subang Jaya': "Subang Jaya is a mature Selangor city with Sunway, SS15 and USJ, served by the LRT and the BRT Sunway line.",
    'Batu Kawan': "Batu Kawan is Penang's mainland growth area at the Second Penang Bridge, with IKEA, Design Village outlet mall and an industrial park.",
    'Gelugor': "Gelugor is on Penang island's east coast near the Penang Bridge and Universiti Sains Malaysia, and home to The Light City waterfront development.",
    'George Town': "George Town is Penang's UNESCO World Heritage capital, with the island's main shopping, food and business addresses.",
    'Bayan Lepas': "Bayan Lepas in southern Penang island hosts the airport and the Free Industrial Zone, a major employment hub.",
    'Paya Terubong': "Paya Terubong is a hillside residential area in central Penang island, near Farlim and Air Itam.",
    'Tanjung Bungah': "Tanjung Bungah is a coastal suburb on Penang island's north coast, between Gurney and Batu Ferringhi.",
    'JB City Centre': "Johor Bahru City Centre is next to the Causeway, the JB CIQ checkpoint and the upcoming RTS Link station at Bukit Chagar.",
    'Kebun Teh': "Kebun Teh is a residential area north of Johor Bahru city centre, close to the Johor Bahru Eastern Dispersal Link.",
    'Melaka City': "Melaka City is a UNESCO World Heritage city and a leading tourism destination.",
    'Kota Kinabalu': "Kota Kinabalu is Sabah's capital, with a city-centre waterfront, malls and the international airport close by.",
    'Kuala Terengganu': "Kuala Terengganu is the capital of Terengganu, with a waterfront city centre, Chinatown and boat links to the islands.",
    'Kubang Kerian': "Kubang Kerian in Kota Bharu is home to Hospital Universiti Sains Malaysia and its health campus.",
}
FOREIGN_MIN = {'Kuala Lumpur': 'RM1 million for most residential property types', 'Selangor': 'RM2 million'}


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower().replace('&', 'and')).strip('-')


def price_rm(s):
    """Lowest whole-unit price in RM from a price text, or None (per-sqft prices are ignored)."""
    s = (s or '').replace(',', '')
    for m in re.finditer(r'RM\s*([\d.]+)\s*(k|m|mil|million)?\b(?!\s*(?:psf|per\s*s))', s, re.I):
        v = float(m.group(1)); u = (m.group(2) or '').lower()
        v = v * 1000 if u == 'k' else v * 1e6 if u in ('m', 'mil', 'million') else v
        if v >= 50000:
            return v
    return None


def rm(v):
    return 'RM%s' % format(int(round(v, -2)), ',')


def groups():
    tree = OrderedDict((s, OrderedDict()) for s in STATES)
    for k, (s, a) in enumerate(PLACES):
        tree.setdefault(s, OrderedDict()).setdefault(a, []).append(k)
    for s in tree:
        tree[s] = OrderedDict(sorted(tree[s].items(), key=lambda kv: (-len(kv[1]), kv[0])))
    return tree


CSS = r'''
:root{--bg:#F9F8F6;--ink:#111;--grey:#5A5A5A;--line:rgba(17,17,17,0.08);--gold:#5E60CE;}
*{box-sizing:border-box;margin:0;padding:0;} body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6;}
a{color:inherit;text-decoration:none;} img{display:block;max-width:100%;}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif;line-height:1.2;}
header{position:sticky;top:0;z-index:50;background:#5E60CE;color:#fff;display:flex;align-items:center;gap:24px;padding:14px 5vw;}
.logo{display:flex;align-items:center;gap:10px;} .logo img{width:42px;height:42px;border-radius:50%;} .logo b{font-family:'Playfair Display',serif;font-size:20px;} .logo small{display:block;font-size:10px;letter-spacing:.14em;text-transform:uppercase;opacity:.85;}
header nav{display:flex;gap:22px;flex-wrap:wrap;margin-left:auto;} header nav a{font-size:15px;} header nav a.active{text-decoration:underline;text-underline-offset:6px;}
.wa-btn{display:inline-flex;align-items:center;gap:8px;background:#25D366;color:#fff;border-radius:100px;padding:11px 20px;font-weight:600;font-size:14px;}
@media(max-width:1100px){header nav{display:none;}.wa-btn{margin-left:auto;}}
.wrap{max-width:1180px;margin:0 auto;padding:0 5vw;}
.crumbs{font-size:13px;color:var(--grey);padding:22px 0 10px;display:flex;gap:8px;flex-wrap:wrap;} .crumbs a:hover{color:var(--gold);}
.hero{padding:12px 0 30px;} .eyebrow{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--gold);font-weight:700;}
.hero h1{font-size:clamp(30px,4.4vw,48px);margin:10px 0 14px;} .hero p{color:var(--grey);font-size:16px;max-width:820px;}
.facts{display:grid;grid-template-columns:repeat(4,1fr);background:#fff;border:1px solid var(--line);border-radius:12px;margin:26px 0 40px;}
.facts div{padding:18px 20px;border-left:1px solid var(--line);} .facts div:first-child{border-left:0;}
.facts span{display:block;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--grey);font-weight:600;} .facts strong{font-family:'Playfair Display',serif;font-size:21px;}
.blk{margin:0 0 46px;} .blk h2{font-size:28px;margin-bottom:16px;}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px;}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden;display:flex;flex-direction:column;transition:transform .25s,box-shadow .25s;}
.card:hover{transform:translateY(-3px);box-shadow:0 14px 30px rgba(17,17,17,.08);}
.card img,.card .noimg{width:100%;aspect-ratio:16/10;object-fit:cover;background:linear-gradient(135deg,#1c1a17,#3a3226);}
.card-b{padding:16px 18px 18px;display:flex;flex-direction:column;gap:6px;flex:1;}
.card-b small{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--gold);font-weight:700;}
.card-b h3{font-size:19px;} .card-b p{font-size:13px;color:var(--grey);}
.card-b ul{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:4px 12px;font-size:12.5px;margin-top:4px;} .card-b li b{display:block;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--grey);}
.card-b .price{margin-top:auto;padding-top:10px;font-family:'Playfair Display',serif;font-size:19px;color:var(--gold);font-weight:700;}
.tbl{overflow-x:auto;background:#fff;border:1px solid var(--line);border-radius:12px;}
table{width:100%;border-collapse:collapse;font-size:14px;min-width:720px;} th,td{padding:12px 16px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top;}
th{background:#5E60CE;color:#fff;font-weight:600;font-size:12.5px;letter-spacing:.04em;} tr:last-child td{border-bottom:0;} td a{color:var(--gold);font-weight:600;}
.faq details{background:#fff;border:1px solid var(--line);border-radius:10px;margin-bottom:10px;} .faq summary{padding:15px 18px;font-weight:600;cursor:pointer;}
.faq details p{padding:0 18px 16px;color:var(--grey);}
.chips{display:flex;flex-wrap:wrap;gap:8px;} .chip{background:#fff;border:1px solid var(--line);border-radius:100px;padding:8px 14px;font-size:13.5px;} .chip:hover{border-color:var(--gold);color:var(--gold);} .chip em{font-style:normal;color:var(--grey);margin-left:6px;font-size:12px;}
.cta{background:#1d1b4f;color:#fff;border-radius:14px;padding:34px;text-align:center;margin:10px 0 50px;} .cta h2{font-size:26px;margin-bottom:8px;} .cta p{opacity:.85;margin-bottom:18px;}
.note{font-size:12px;color:var(--grey);margin-bottom:40px;}
footer{border-top:1px solid var(--line);padding:26px 5vw;font-size:13px;color:var(--grey);text-align:center;}
@media(max-width:760px){.facts{grid-template-columns:1fr 1fr;}.facts div:nth-child(3){border-left:0;}.facts div{border-top:1px solid var(--line);}.facts div:nth-child(-n+2){border-top:0;}}
'''

NAV = [('', 'Home'), ('projects.html', 'View Projects'), ('compare.html', 'Compare Projects'), ('blog.html', 'News'),
       ('calculator.html', 'Calculator'), ('mm2h.html', 'MM2H 第二家园'), ('about-keith.html', 'About Keith')]


try:
    COORDS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project_coords.json'), encoding='utf-8'))
except (OSError, ValueError):
    COORDS = {}


def short_rm(v):
    if not v:
        return ''
    return ('RM %.2fM' % (v / 1e6)).replace('.00M', 'M').replace('0M', 'M') if v >= 1e6 else 'RM %dK' % round(v / 1000)


def map_points(ids, root):
    import math
    pts = []
    for k in ids:
        c = COORDS.get(P[k]['name'])
        if not c:
            continue
        pts.append({'k': k, 'lat': c[0], 'lng': c[1]})
    groups = {}
    for p in pts:
        groups.setdefault((round(p['lat'], 5), round(p['lng'], 5)), []).append(p)
    for g in groups.values():
        if len(g) > 1:      # same spot: spread the pins a little so each one can be tapped
            for n, p in enumerate(g):
                a = 2 * math.pi * n / len(g)
                p['lat'] += 0.0022 * math.cos(a)
                p['lng'] += 0.0022 * math.sin(a)
    out = []
    for p in pts:
        k = p['k']
        v = price_rm(P[k].get('price'))
        out.append({'lat': round(p['lat'], 6), 'lng': round(p['lng'], 6), 'n': P[k]['name'], 'a': PLACES[k][1],
                    's': P[k].get('status') or '', 'p': short_rm(v), 'u': '%sproperty/%s.html' % (root, SLUG.get(k, slug(P[k]['name']))),
                    'i': (root + PHOTO[k]) if PHOTO.get(k) else ''})
    return out


MAP_CSS = ('.kd{background:#5E60CE;border:3px solid #fff;border-radius:50%;box-shadow:0 2px 8px rgba(17,17,17,.35);cursor:pointer;transition:transform .15s;}'
           '.kd:hover{transform:scale(1.25);background:#1d1b4f;}'
           '.leaflet-tooltip{font:600 12px Inter,sans-serif;border-radius:8px;padding:5px 9px;}'
           '.kmap{height:440px;border-radius:14px;overflow:hidden;border:1px solid var(--line);background:#eef0f4;z-index:0;}'
           '.kp{background:#5E60CE;color:#fff;font:700 12px Inter,sans-serif;padding:5px 9px;border-radius:100px;white-space:nowrap;box-shadow:0 4px 12px rgba(17,17,17,.25);border:2px solid #fff;transform:translate(-50%,-100%);display:inline-block;position:relative;}'
           '.kp:after{content:"";position:absolute;left:50%;bottom:-7px;margin-left:-5px;border:5px solid transparent;border-top-color:#5E60CE;}'
           '.kp.dot{width:16px;height:16px;padding:0;border-radius:50%;} .kp.dot:after{display:none;}'
           '.kp:hover,.kp.on{background:#1d1b4f;} .kp:hover:after,.kp.on:after{border-top-color:#1d1b4f;}'
           '.kpop{width:220px;font-family:Inter,sans-serif;} .kpop img{width:100%;height:110px;object-fit:cover;border-radius:8px;margin-bottom:8px;}'
           '.kpop b{display:block;font:700 15px "Playfair Display",serif;color:#111;} .kpop small{display:block;color:#5A5A5A;font-size:12px;margin:2px 0 6px;}'
           '.kpop em{font-style:normal;color:#5E60CE;font-weight:700;font-size:14px;} .kpop a{display:block;margin-top:8px;color:#5E60CE;font-weight:700;}'
           '.leaflet-popup-content{margin:12px;} .kmap-note{font-size:12.5px;color:var(--grey);margin-top:10px;}'
           '@media(max-width:700px){.kmap{height:360px;}}')


def map_block(place, ids, root):
    pts = map_points(ids, root)
    if not pts:
        return ''
    return ('<link rel="stylesheet" href="%svendor/leaflet/leaflet.css"><style>%s</style>'
            '<section class="blk"><h2>Map of new launches in %s</h2><div class="kmap" id="kmap" aria-label="Map of projects"></div>'
            '<p class="kmap-note">Pins show each project\'s approximate location. Tap a pin to see the project.</p></section>'
            '<script src="%svendor/leaflet/leaflet.js"></script><script>(function(){var P=%s,VIEW=%s;'
            'var m=L.map("kmap",{scrollWheelZoom:false,dragging:!L.Browser.mobile,tap:false});'
            'L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,'
            'attribution:"&copy; <a href=\\"https://www.openstreetmap.org/copyright\\">OpenStreetMap</a>"}).addTo(m);'
            'var b=[];P.forEach(function(p){var ic=L.divIcon({className:"kd",iconSize:[18,18],iconAnchor:[9,9],popupAnchor:[0,-10]});'
            'var h=function(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}var V=VIEW[l]||VIEW.en;return "<div class=\\"kpop\\">"+(p.i?"<img src=\\""+p.i+"\\" alt=\\"\\">":"")+"<b>"+p.n+"</b><small>"+p.a+(p.s?" · "+p.s:"")+"</small>"+(p.p?"<em>"+(V[0]?V[0]+" ":"")+p.p+"</em>":"")+"<a href=\\""+p.u+"\\">"+V[1]+" →</a></div>"};'
            'L.marker([p.lat,p.lng],{icon:ic,title:p.n,riseOnHover:true}).addTo(m).bindPopup(h,{maxWidth:240}).bindTooltip(p.n+(p.p?" · "+p.p:""),{direction:"top",offset:[0,-8]});b.push([p.lat,p.lng]);});'
            'if(b.length===1)m.setView(b[0],15);else m.fitBounds(b,{padding:[40,40],maxZoom:15});})();</script>') % (
        root, MAP_CSS, E(place), root, json.dumps(pts, ensure_ascii=False).replace('</', '<\\/'),
        json.dumps({'en': ['From', 'View project'], 'zh-CN': ['起价', '查看项目'], 'zh-TW': ['起價', '查看項目'], 'ms': ['Dari', 'Lihat projek'], 'ja': ['', 'プロジェクトを見る'], 'ko': ['', '프로젝트 보기']}, ensure_ascii=False))


def page(state, area, ids, tree, root):
    """root: prefix for links to the rest of the site ('../' live, 'https://keithnah.com/' preview)."""
    place = area or state
    ids = sorted(ids, key=lambda k: re.sub(r'[^a-z0-9 ]', '', P[k]['name'].lower()))
    prices = [(price_rm(P[k]['price']), k) for k in ids if price_rm(P[k]['price'])]
    low = min(prices) if prices else None
    free = [k for k in ids if (P[k].get('tenure') or '').lower().startswith('freehold')]
    years = sorted({int(y) for k in ids for y in re.findall(r'\b(20[2-4]\d)\b', P[k].get('completion') or '')})
    n = len(ids)
    wa_msg = 'Hi Keith, I am looking at new launches in %s.' % place
    wa = 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0' % re.sub(r'\s', '+', '(KNRE) ' + wa_msg)
    url = '%s/area/%s.html' % (SITE, slug(place))
    proj = lambda k: '%sproperty/%s.html' % (root, SLUG.get(k, slug(P[k]['name'])))
    img = lambda k: ('<img src="%s%s" alt="%s" loading="lazy">' % (root, E(PHOTO[k]), E(P[k]['name']))) if PHOTO.get(k) else '<i class="noimg"></i>'

    cards = ''.join(
        '<a class="card" href="%s">%s<div class="card-b"><small>%s · %s</small><h3>%s</h3><p>%s</p>'
        '<ul><li><b>Size</b>%s</li><li><b>Bedrooms</b>%s</li><li><b>Tenure</b>%s</li><li><b>Completion</b>%s</li></ul>'
        '<div class="price">%s</div></div></a>' % (
            proj(k), img(k), E(PLACES[k][1]), E(P[k].get('status') or ''), E(P[k]['name']), E(P[k]['loc']),
            E(P[k].get('size')), E(P[k].get('rooms')), E(P[k].get('tenure')), E(P[k].get('completion')), SH.price_tag(E(P[k].get('price')), price_rm(P[k].get('price'))))
        for k in ids)
    rows = ''.join('<tr><td><a href="%s">%s</a></td>%s<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        proj(k), E(P[k]['name']), ('' if area else '<td>%s</td>' % E(PLACES[k][1])), E(P[k].get('price')), E(P[k].get('size')),
        E(P[k].get('rooms')), E(P[k].get('tenure')), E(P[k].get('completion'))) for k in ids)
    head = '<tr><th>Project</th>%s<th>Starting price</th><th>Size</th><th>Bedrooms</th><th>Tenure</th><th>Completion</th></tr>' % ('' if area else '<th>Area</th>')

    names = lambda ks: ', '.join(P[k]['name'] for k in ks)
    faq = [('How many new launch projects are there in %s?' % place,
            'Keith currently lists %d project%s in %s: %s.' % (n, '' if n == 1 else 's', place, names(ids)))]
    if low:
        faq.append(('What is the lowest starting price for a new property in %s?' % place,
                    'The lowest published starting price is about %s (gross) at %s. Prices change with each phase and unit; ask Keith for the latest figures.' % (rm(low[0]), P[low[1]]['name'])))
    if free:
        faq.append(('Are there freehold projects in %s?' % place,
                    'Yes. Freehold projects here include %s.' % names(free) if len(free) < n else 'Yes, all %d projects listed here are freehold.' % n))
    else:
        faq.append(('Are there freehold projects in %s?' % place, 'The projects Keith lists here are leasehold. Ask Keith about freehold options nearby.'))
    if years:
        faq.append(('When will the new projects in %s be completed?' % place,
                    'Expected completion ranges from %s to %s, depending on the project. Some projects complete a set number of months after the advertising permit (APDL).' % (years[0], years[-1]) if len(years) > 1
                    else 'Expected completion for the listed projects is around %s.' % years[0]))
    fm = FOREIGN_MIN.get(state)
    faq.append(('Can foreigners buy property in %s?' % place,
                ('Yes. Foreign buyers in %s must meet the state minimum purchase price, currently %s, and need state consent.' % (state, fm)) if fm
                else 'Yes, subject to the state minimum purchase price for foreigners and state consent. The threshold differs by state and property type; Keith can confirm it for each project.'))
    faq_html = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (E(q), E(a)) for q, a in faq)

    if area:
        others = [(a, len(v)) for a, v in tree[state].items() if a != area]
        more = ('<section class="blk"><h2>Other areas in %s</h2><div class="chips"><a class="chip" href="%s.html">All of %s<em>%d</em></a>%s</div></section>' % (
            E(state), slug(state), E(state), sum(len(v) for v in tree[state].values()),
            ''.join('<a class="chip" href="%s.html">%s<em>%d</em></a>' % (slug(a), E(a), c) for a, c in others))) if others or True else ''
    else:
        more = '<section class="blk"><h2>Areas in %s</h2><div class="chips">%s</div></section>' % (
            E(state), ''.join('<a class="chip" href="%s.html">%s<em>%d</em></a>' % (slug(a), E(a), len(v)) for a, v in tree[state].items()))
    lm = {}
    try:
        lm = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'list_membership.json'), encoding='utf-8'))
    except (OSError, ValueError):
        pass
    cnt = {}
    for k in ids:
        for s2, t2 in lm.get(str(k), []):
            cnt[(s2, t2)] = cnt.get((s2, t2), 0) + 1
    top = sorted(cnt.items(), key=lambda kv: -kv[1])[:10]
    more += ('<section class="blk"><h2>Popular lists with %s projects</h2><div class="chips">%s<a class="chip" href="%sbest/">All lists →</a></div></section>' % (
        E(place), ''.join('<a class="chip" href="%sbest/%s.html">%s<em>%d</em></a>' % (root, s2, E(t2), c) for (s2, t2), c in top), root)) if top else ''
    states = '<section class="blk"><h2>Other states</h2><div class="chips">%s</div></section>' % ''.join(
        '<a class="chip" href="%s.html">%s<em>%d</em></a>' % (slug(s), E(s), sum(len(v) for v in tree[s].values())) for s in STATES if s != state and tree.get(s))

    title = 'New Launch Condos in %s %d | Prices & Floor Plans | Keith Nah' % (place, YEAR)
    desc = '%d new property launches in %s%s: starting prices%s, sizes, tenure and completion dates, with floor plans for each project.' % (
        n, place, '' if not area else ', ' + state, (' from ' + rm(low[0])) if low else '')
    ld = [{'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
              {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
              {'@type': 'ListItem', 'position': 2, 'name': 'Projects', 'item': SITE + '/projects.html'}] +
              ([{'@type': 'ListItem', 'position': 3, 'name': state, 'item': '%s/area/%s.html' % (SITE, slug(state))}] if area else []) +
              [{'@type': 'ListItem', 'position': 4 if area else 3, 'name': place, 'item': url}]},
          {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'New launch projects in %s' % place,
           'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': '%s/property/%s.html' % (SITE, SLUG.get(k, '')), 'name': P[k]['name']} for i, k in enumerate(ids)]},
          {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
              {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}]
    crumbs = '<a href="%s">Home</a><span>›</span><a href="%sprojects.html">Projects</a><span>›</span>%s<strong>%s</strong>' % (
        root, root, ('<a href="%s.html">%s</a><span>›</span>' % (slug(state), E(state))) if area else '', E(place))
    nav = ''.join('<a href="%s%s"%s>%s</a>' % (root, h, ' class="active"' if h == 'projects.html' else '', E(t)) for h, t in NAV)
    return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}">
<link rel="icon" type="image/png" href="{root}images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{ld}</script>
<style>{css}{fcss}</style>
</head>
<body>
<header>
  <a class="logo" href="{root}"><img src="{root}images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Keith Nah Real Estate</small></span></a>
  <nav>{nav}</nav>
  <a class="wa-btn" href="{wa}" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
<main class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav>
  <section class="hero">
    <span class="eyebrow">{eyebrow}</span>
    <h1>New Launch Condos in {place} ({year})</h1>
    <p>{intro} Keith Nah currently lists {n} project{s} here{lowtxt}. Compare starting prices, sizes, tenure and completion dates below, then open any project for its floor plans.</p>
    <div class="facts"><div><span>Projects</span><strong>{n}</strong></div><div><span>Starting from</span><strong>{low}</strong></div><div><span>Freehold</span><strong>{free} of {n}</strong></div><div><span>Completion</span><strong>{years}</strong></div></div>
  </section>
  {map_blk}
  <section class="blk"><h2>Projects in {place}</h2><div class="cards">{cards}</div></section>
  <section class="blk"><h2>Compare at a glance</h2><div class="tbl"><table><thead>{head}</thead><tbody>{rows}</tbody></table></div></section>
  <section class="blk faq"><h2>Buying in {place}: common questions</h2>{faq}</section>
  {more}
  {states}
  <div class="cta"><h2>Looking for a home or investment in {place}?</h2><p>Tell Keith your budget and needs, and he will shortlist the right units for you.</p><a class="wa-btn" href="{wa}" target="_blank" rel="noopener">WhatsApp Keith</a></div>
  <p class="note">Prices are gross starting prices as published and may change. Confirm the latest prices, units and terms with Keith before deciding.</p>
</main>
<footer>&copy; {year} Keith Nah Real Estate · REN 60517 · IQI Global · <a href="{root}projects.html">All projects</a> · <a href="{root}best/">Best new launch lists</a> · <a href="{root}privacy-policy.html">Privacy Policy</a> · <a href="{root}terms-of-use.html">Terms of Use</a></footer>
{floatwa}
<script src="{root}lead-tracker.js"></script>
</body>
</html>
'''.format(title=E(title), desc=E(desc), url=url, root=root, ld=json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'), css=CSS,
           nav=nav, wa=E(wa), crumbs=crumbs, eyebrow=E(state if area else 'Malaysia'), place=E(place), year=YEAR,
           intro=E(INTRO.get(place, '')), n=n, s='' if n == 1 else 's', lowtxt=(', starting from about %s (gross)' % rm(low[0])) if low else '',
           low=rm(low[0]) if low else '—', free=len(free), years=('%d – %d' % (years[0], years[-1]) if len(years) > 1 else (str(years[0]) if years else 'TBC')),
           cards=cards, map_blk=map_block(place, ids, root), fcss=FW.FLOAT_CSS, floatwa=FW.float_html(E(wa)), head=head, rows=rows, faq=faq_html, more=more, states=states)


def _register():
    import i18n_pages as I
    I.register({'intro.' + k: v for k, v in INTRO.items()})
    I.DATA.update(v for p in P for f in ('size', 'rooms', 'tenure', 'completion', 'price', 'status') for v in [p.get(f)] if v)


_register()


def build(out, root):
    tree = groups()
    os.makedirs(out, exist_ok=True)
    pages = []
    for s in STATES:
        if not tree.get(s):
            continue
        allids = [k for v in tree[s].values() for k in v]
        open(os.path.join(out, slug(s) + '.html'), 'w', encoding='utf-8').write(SH.apply(page(s, None, allids, tree, root), root, 'projects.html'))
        pages.append(slug(s))
        for a, ids in tree[s].items():
            if a == s:
                continue
            open(os.path.join(out, slug(a) + '.html'), 'w', encoding='utf-8').write(SH.apply(page(s, a, ids, tree, root), root, 'projects.html'))
            pages.append(slug(a))
    return pages


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--preview':
        pages = build(os.path.join(sys.argv[2], 'area'), SITE + '/')
    else:
        pages = build('area', '../')
    print('area pages:', len(pages))
