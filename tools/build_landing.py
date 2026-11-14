"""Project landing pages: a focused, one-project version of a property page (preview stage).

The page reads like its own small site: a full-width photo with a one-line hook, a sticky bar with the
project's own sections (Overview, 5 things, Layouts, Price, Location, Foreign buyers, FAQ) and a
WhatsApp button, then the general site blocks (nearby projects, compare, all projects) at the bottom.
A small logo still links home, so a visitor is never stuck.

Facts come from the project data on the site (PROJECT_DETAILS) and the curated notes in LANDING below,
written only from the project's brochure and published details. Nothing is invented.

    python3 tools/externalize.py in
    python3 tools/build_landing.py maba-suitez property/zz-preview.html
    python3 tools/externalize.py out
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
sys.path.insert(0, HERE)
import build_area_pages as A  # noqa: E402

E = lambda s: html.escape(str(s), quote=True)
WA = 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0'
waq = lambda m: WA % re.sub(r'\s', '+', '(KNRE) ' + m).replace('&', '%26')

# Curated per-project content. Every number here is from the project data or brochure.
LANDING = {
    'maba-suitez': {
        'eyebrow': 'KL City Centre · EXSIM',
        'hook': '160 metres from Merdeka MRT, beside Menara Merdeka Maybank',
        'intro': 'Two towers of serviced apartments and office suites on Jalan Hang Jebat, from 323 sq ft, with sky facilities on both roofs and a basketball court in the podium.',
        'numbers': [('914', 'units in two towers'), ('54 / 50', 'storeys, Tower A / Tower B'), ('1.328', 'acres of land'), ('160 m', 'to Merdeka MRT')],
        'five': [
            ('Two minutes on foot to the MRT', 'Merdeka MRT (Kajang line) is about 160 m away. From there Pavilion KL is one station, and TRX and KL Sentral are two.'),
            ('Small units, on purpose', 'Every unit is between 323 and 657 sq ft: office-suite studios, 1+1 room suites and dual-key suites. It is built for city living and renting out, not for families who need three bedrooms.'),
            ('The dual key is the most common type', 'Type C, the 657 sq ft dual-key suite, makes up 377 of the 914 units. It has one room and two bathrooms, so you can live in one part and let the other.'),
            ('Two towers, two sets of sky facilities', 'Tower A has 54 storeys and 534 units, with sky facilities on Levels 53 and 53A. Tower B has 50 storeys and 380 units, with facilities on Levels 47 and 50. Both share the Level 6 podium and its basketball court.'),
            ('Budget for the running costs', 'The maintenance fee is RM0.99 psf including the sinking fund, and car parks are not included with the units (391 bays plus 6 EV bays in the development).'),
        ],
        'layout_fit': {
            'Type A — Office Suite': 'Suits a home office or a first city investment at the lowest entry price.',
            'Type B': 'Suits a single professional or a couple who want a separate room.',
            'Type C — Dual Key': 'Suits owners who want to live in one part and rent out the other, or rent both.',
            'Type C (M) — Dual Key': 'The same dual-key layout, mirrored.',
        },
        'units': {'Type A — Office Suite': 249, 'Type B': 288, 'Type C — Dual Key': 377},
        'foreign': 'The entry units start from RM699,000, below the RM1 million minimum for foreign buyers in Kuala Lumpur. Larger units can meet the minimum, so Keith checks the exact unit and its price before you book.',
        'developer': 'EXSIM is developing MABA Suitez as a joint venture with the Malaysian Basketball Association (MABA), which is why the podium has a full basketball court.',
        'maps': 'MABA Suitez, Jalan Hang Jebat, Kuala Lumpur',
    },
}


def proj_index(slug):
    for i, s in A.SLUG.items():
        if s == slug:
            return i
    raise SystemExit('no project with slug %s' % slug)


def page(slug, root='../'):
    i = proj_index(slug)
    p = A.P[i]
    L = LANDING[slug]
    name = p['name']
    photo = root + A.PHOTO[i] if A.PHOTO.get(i) else ''
    ex = p.get('details_extra') or {}
    w = lambda m: E(waq(m % name if '%s' in m else m))
    wa_price = w("Hi Keith, I'd like the latest price list for %s.")
    chat = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 3.5A11 11 0 0 0 3.2 17.1L2 22l5-1.3A11 11 0 1 0 20.5 3.5z"/></svg>'

    def wbtn(text, msg, cls='lp-wa'):
        return '<a class="%s" href="%s" target="_blank" rel="noopener">%s<span>%s</span></a>' % (cls, w(msg), chat, E(text))

    nav = [('overview', 'Overview'), ('five', '5 things'), ('layouts', 'Layouts'), ('price', 'Price'), ('location', 'Location'),
           ('foreign', 'Foreign buyers'), ('faq', 'FAQ')]
    navh = ''.join('<a href="#%s">%s</a>' % (k, E(v)) for k, v in nav)

    facts = [('From', re.sub(r'^From\s*', '', p['price'])), ('Size', p['size']), ('Type', p['rooms']), ('Tenure', p['tenure']), ('Completion', p['completion'])]
    factsh = ''.join('<div><small>%s</small><b>%s</b></div>' % (E(a), E(b)) for a, b in facts)
    nums = ''.join('<div><b>%s</b><small>%s</small></div>' % (E(a), E(b)) for a, b in L['numbers'])
    five = ''.join('<li><span>%02d</span><div><h3>%s</h3><p>%s</p></div></li>' % (n + 1, E(t), E(d)) for n, (t, d) in enumerate(L['five']))

    lays = p.get('layouts') or []
    tabs = ''.join('<button type="button" class="lp-tab%s" data-t="%d">%s<small>%s</small></button>' % (
        ' on' if n == 0 else '', n, E(re.sub(r'\s+—.*', '', l['type'])), E(l['size'])) for n, l in enumerate(lays))
    panes = ''
    for n, l in enumerate(lays):
        units = L['units'].get(l['type'])
        panes += ('<div class="lp-pane%s" data-p="%d"><div class="lp-plan"><img src="%s%s" alt="%s %s floor plan" loading="lazy"></div><div class="lp-pd">'
                  '<span class="lp-eb">%s</span><h3>%s</h3><dl><div><dt>Size</dt><dd>%s</dd></div><div><dt>Layout</dt><dd>%s</dd></div>%s</dl><p>%s</p><p class="lp-fit">%s</p>%s</div></div>') % (
            ' on' if n == 0 else '', n, root, E(l['img']), E(name), E(l['type']), E(l.get('tag', '')), E(l['type']), E(l['size']), E(l['rooms']),
            ('<div><dt>Units</dt><dd>%d</dd></div>' % units) if units else '', E(l['desc']), E(L['layout_fit'].get(l['type'], '')),
            wbtn('Ask about %s availability' % re.sub(r'\s+—.*', '', l['type']), 'Hi Keith, which %s units are still available at %%s?' % re.sub(r'\s+—.*', '', l['type'])))

    amen = ''.join('<li>%s</li>' % E(a) for a in p.get('amenities') or [])
    faqs = [('Where is %s?' % name, p['loc_text']),
            ('What sizes are available?', 'Units range from %s: %s.' % (p['size'], ', '.join('%s (%s)' % (re.sub(r'\s+—.*', '', l['type']), l['size']) for l in lays[:3]))),
            ('What is the starting price?', ('%s. %s.' % (p['price'], ex.get('Price per Sqft', ''))).strip(' .') + '.'),
            ('Is it freehold or leasehold?', '%s.' % p['tenure']),
            ('Who is the developer?', L['developer']),
            ('When will it be completed?', ('Completion is %s.' % (p['completion'][0].lower() + p['completion'][1:])) if p['completion'] else ''),
            ('What is the maintenance fee?', ex.get('Maintenance Fee', '') + '.'),
            ('Can foreigners buy %s?' % name, L['foreign'])]
    faqh = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (E(q), E(a)) for q, a in faqs if a)
    nearby = ''.join('<a class="lp-nb" href="%s.html"><img src="%s%s" alt=""><b>%s</b><small>%s</small></a>' % (
        A.SLUG.get(k, A.slug(A.P[k]['name'])), root, E(A.PHOTO.get(k, '')), E(A.P[k]['name']), E(A.P[k]['price'])) for k in (p.get('nearby') or [])[:3])
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs if a]}

    return TPL.format(
        name=E(name), title=E('%s: Price, Layouts & Location | Keith Nah' % name), desc=E('%s %s.' % (name, L['hook'])), root=root, photo=E(photo),
        navh=navh, wa_price=wa_price, chat=chat, eyebrow=E(L['eyebrow']), hook=E(L['hook']), intro=E(L['intro']), factsh=factsh,
        overview=E(p['overview']), nums=nums, five=five, tabs=tabs, panes=panes, price=E(p['price']), psf=E(ex.get('Price per Sqft', '')),
        maint=E(ex.get('Maintenance Fee', '')), park=E(ex.get('Car Parks', '')),
        wb_list=wbtn('Request the price list', "Hi Keith, please send me the latest price list for %s."),
        wb_units=wbtn('Check available units', 'Hi Keith, which units are still available at %s?', 'lp-wa lp-wa2'),
        loc_text=E(p['loc_text']), amen=amen, maps=E('https://www.google.com/maps/search/?api=1&query=' + re.sub(r'\s', '+', L['maps'])),
        wb_view=wbtn('Book a viewing or video tour', "Hi Keith, I'd like to book a viewing or a video tour of %s."),
        foreign=E(L['foreign']), wb_foreign=wbtn('Check if a unit meets the minimum', 'Hi Keith, I am a foreign buyer. Which units at %s meet the RM1 million minimum?'),
        faqh=faqh, developer=E(L['developer']), nearby=nearby, ld=json.dumps(ld, ensure_ascii=False))


TPL = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" type="image/png" href="{root}images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{ld}</script>
<style>
:root{{--ink:#15142b;--grey:#5f5e74;--line:rgba(21,20,43,.09);--gold:#5E60CE;--deep:#1d1b4f;--soft:#f3f1fa;--bg:#F9F8F6;--wa:#25d366}}
*{{box-sizing:border-box;margin:0;padding:0}} html{{scroll-behavior:smooth;scroll-padding-top:76px}} body{{font-family:Inter,system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6}}
a{{color:inherit;text-decoration:none}} img{{display:block;max-width:100%}} button{{font:inherit}}
h1,h2,h3{{font-family:'Playfair Display',Georgia,serif;line-height:1.2}}
.lp-bar{{position:fixed;top:0;left:0;right:0;z-index:50;display:flex;align-items:center;gap:24px;padding:12px 4vw;transition:background .3s,box-shadow .3s}}
.lp-bar.solid{{background:rgba(29,27,79,.96);box-shadow:0 8px 24px rgba(0,0,0,.18)}}
.lp-logo{{display:flex;align-items:center;gap:10px;color:#fff}} .lp-logo img{{width:38px;height:38px;border-radius:50%}} .lp-logo b{{font-family:'Playfair Display',serif;font-size:17px;display:block;line-height:1.1}} .lp-logo small{{font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;opacity:.75}}
.lp-nav{{display:flex;gap:22px;margin:0 auto}} .lp-nav a{{color:rgba(255,255,255,.85);font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase}} .lp-nav a:hover{{color:#fff}}
.lp-cta{{background:var(--wa);color:#fff;font-weight:700;font-size:13.5px;padding:10px 18px;border-radius:99px;white-space:nowrap}}
.lp-hero{{position:relative;min-height:100vh;display:flex;align-items:flex-end;padding:120px 6vw 70px;color:#fff;background:#1d1b4f center/cover no-repeat;background-image:linear-gradient(180deg,rgba(15,14,40,.35),rgba(15,14,40,.15) 35%,rgba(15,14,40,.85)),url('{photo}')}}
.lp-hero-in{{max-width:760px}} .lp-eb{{display:block;font-size:12px;font-weight:800;letter-spacing:.2em;text-transform:uppercase;color:#b9b4ff;margin-bottom:12px}}
.lp-hero h1{{font-size:clamp(46px,7vw,92px);letter-spacing:.02em;font-weight:600}} .lp-hook{{font-size:clamp(15px,1.6vw,19px);letter-spacing:.14em;text-transform:uppercase;margin:6px 0 18px;opacity:.95}}
.lp-hero p.lp-intro{{font-size:16.5px;max-width:560px;opacity:.9}} .lp-facts{{display:flex;flex-wrap:wrap;gap:10px 28px;margin:26px 0}} .lp-facts small{{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;opacity:.7}} .lp-facts b{{font-size:16px}}
.lp-btns{{display:flex;gap:12px;flex-wrap:wrap}} .lp-wa,.lp-ghost{{display:inline-flex;align-items:center;gap:9px;padding:14px 24px;border-radius:99px;font-weight:700;font-size:14.5px;transition:transform .2s}}
.lp-wa{{background:var(--wa);color:#fff}} .lp-wa:hover,.lp-ghost:hover{{transform:translateY(-2px)}} .lp-wa svg{{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2}}
.lp-wa2{{background:#fff;color:var(--deep);border:1.5px solid var(--line)}} .lp-ghost{{background:#fff;color:var(--deep)}}
.lp-sec{{max-width:1180px;margin:0 auto;padding:90px 5vw 0}} .lp-sec>.lp-eb{{color:var(--gold)}} .lp-sec h2{{font-size:clamp(28px,3.8vw,44px);margin-bottom:16px;max-width:820px}} .lp-sec>p{{color:var(--grey);font-size:16px;max-width:780px}}
.lp-nums{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:34px}} .lp-nums div{{background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px}} .lp-nums b{{font-family:'Playfair Display',serif;font-size:34px;color:var(--deep);display:block}} .lp-nums small{{color:var(--grey);font-size:13.5px}}
.lp-five{{list-style:none;display:grid;gap:14px;margin-top:30px}} .lp-five li{{display:flex;gap:22px;background:#fff;border:1px solid var(--line);border-radius:18px;padding:24px 26px}} .lp-five li>span{{font-family:'Playfair Display',serif;font-size:30px;color:var(--gold);line-height:1;min-width:46px}}
.lp-five h3{{font-family:Inter,sans-serif;font-size:18px;font-weight:800;margin-bottom:4px}} .lp-five p{{color:var(--grey);font-size:15px}}
.lp-tabs{{display:flex;gap:10px;flex-wrap:wrap;margin:28px 0 18px}} .lp-tab{{all:unset;cursor:pointer;padding:12px 20px;border-radius:14px;background:#fff;border:1.5px solid var(--line);font-weight:800;font-size:15px}} .lp-tab small{{display:block;font-weight:500;font-size:12.5px;color:var(--grey)}}
.lp-tab.on{{background:var(--gold);border-color:var(--gold);color:#fff}} .lp-tab.on small{{color:rgba(255,255,255,.8)}}
.lp-pane{{display:none;grid-template-columns:1.1fr 1fr;gap:34px;background:#fff;border:1px solid var(--line);border-radius:22px;padding:26px}} .lp-pane.on{{display:grid}}
.lp-plan{{background:var(--soft);border-radius:16px;display:flex;align-items:center;justify-content:center;padding:14px}} .lp-plan img{{max-height:460px;object-fit:contain}}
.lp-pd .lp-eb{{color:var(--gold)}} .lp-pd h3{{font-size:28px;margin-bottom:14px}} .lp-pd dl{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:16px}} .lp-pd dl div{{background:var(--soft);border-radius:12px;padding:12px}} .lp-pd dt{{font-size:11.5px;color:var(--grey);font-weight:700;text-transform:uppercase;letter-spacing:.08em}} .lp-pd dd{{font-weight:800}}
.lp-pd p{{color:var(--grey);font-size:15px;margin-bottom:10px}} .lp-fit{{color:var(--ink)!important;font-weight:600}} .lp-pd .lp-wa{{margin-top:8px}}
.lp-price{{display:grid;grid-template-columns:1.2fr 1fr;gap:20px;margin-top:28px}} .lp-pbox{{background:var(--deep);color:#fff;border-radius:22px;padding:30px}} .lp-pbox small{{opacity:.7;font-size:12px;letter-spacing:.14em;text-transform:uppercase}} .lp-pbox b{{display:block;font-family:'Playfair Display',serif;font-size:36px;margin:6px 0 10px}} .lp-pbox p{{opacity:.85;font-size:14.5px}}
.lp-plist{{background:#fff;border:1px solid var(--line);border-radius:22px;padding:26px;display:flex;flex-direction:column;gap:12px}} .lp-plist div{{display:flex;justify-content:space-between;gap:14px;border-bottom:1px solid var(--line);padding-bottom:10px;font-size:14.5px}} .lp-plist div span{{color:var(--grey)}} .lp-plist div b{{text-align:right}}
.lp-row{{display:flex;gap:12px;flex-wrap:wrap;margin-top:20px}}
.lp-loc{{display:grid;grid-template-columns:1fr 1fr;gap:26px;margin-top:26px}} .lp-loc ul{{list-style:none;background:#fff;border:1px solid var(--line);border-radius:20px;padding:12px 24px}} .lp-loc li{{padding:11px 0;border-bottom:1px solid var(--line);font-size:15px}} .lp-loc li:last-child{{border:0}}
.lp-loc p{{color:var(--grey);font-size:15.5px;margin-bottom:16px}} .lp-map{{font-weight:700;color:var(--gold)}}
.lp-fb{{background:linear-gradient(160deg,#1d1b4f,#2b2973 70%,#3b3c99);color:#fff;border-radius:26px;padding:42px;margin-top:10px}} .lp-fb .lp-eb{{color:#b9b4ff}} .lp-fb h2{{color:#fff}} .lp-fb p{{opacity:.88;font-size:16px;max-width:760px;margin-bottom:22px}} .lp-fb a.lp-link{{color:#fff;font-weight:700;margin-left:16px;text-decoration:underline}}
.lp-faq{{display:flex;flex-direction:column;gap:10px;margin-top:24px;max-width:900px}} .lp-faq details{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 20px}} .lp-faq summary{{font-weight:700;cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:12px}} .lp-faq summary:after{{content:"+";color:var(--gold);font-size:22px;line-height:1}} .lp-faq details[open] summary:after{{content:"\\2212"}} .lp-faq p{{color:var(--grey);margin-top:10px;font-size:15px}}
.lp-dev{{background:#fff;border:1px solid var(--line);border-radius:22px;padding:30px;margin-top:24px}} .lp-dev p{{color:var(--grey);font-size:15.5px}}
.lp-more{{max-width:1180px;margin:90px auto 0;padding:50px 5vw;border-top:1px solid var(--line)}} .lp-more h2{{font-size:24px;margin-bottom:18px}} .lp-nbs{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}} .lp-nb{{background:#fff;border:1px solid var(--line);border-radius:16px;overflow:hidden}} .lp-nb img{{width:100%;height:160px;object-fit:cover}} .lp-nb b,.lp-nb small{{display:block;padding:0 16px}} .lp-nb b{{padding-top:12px}} .lp-nb small{{color:var(--grey);padding-bottom:14px}}
.lp-links{{display:flex;gap:18px;flex-wrap:wrap;margin-top:22px}} .lp-links a{{font-weight:700;color:var(--gold)}}
.lp-foot{{background:#080808;color:rgba(255,255,255,.55);text-align:center;padding:30px 5vw;font-size:13px;margin-top:60px}} .lp-foot a{{color:#fff}}
.lp-float{{position:fixed;right:18px;bottom:18px;z-index:40;box-shadow:0 10px 30px rgba(37,211,102,.45);opacity:0;pointer-events:none;transform:translateY(12px);transition:opacity .3s,transform .3s}} .lp-float.show{{opacity:1;pointer-events:auto;transform:none}}
@media(max-width:1100px){{.lp-nav{{display:none}} .lp-bar{{justify-content:space-between}}}}
@media(max-width:820px){{.lp-nums{{grid-template-columns:1fr 1fr}} .lp-pane.on,.lp-price,.lp-loc{{grid-template-columns:1fr;display:grid}} .lp-pane{{padding:16px}} .lp-pd dl{{grid-template-columns:1fr 1fr}} .lp-nbs{{grid-template-columns:1fr}}
 .lp-hero{{padding:110px 22px 50px;min-height:92vh}} .lp-sec{{padding:64px 20px 0}} .lp-five li{{padding:18px;gap:14px}} .lp-fb{{padding:28px 22px}} .lp-logo small{{display:none}} .lp-cta{{padding:9px 14px;font-size:12.5px}}}}
.lp-chips{{display:none}} @media(max-width:1100px){{.lp-chips{{display:flex;position:sticky;top:62px;z-index:30;gap:8px;overflow-x:auto;padding:10px 16px;background:var(--bg);border-bottom:1px solid var(--line)}} .lp-chips a{{flex:0 0 auto;font-size:13px;font-weight:700;padding:7px 14px;border-radius:99px;background:#fff;border:1px solid var(--line)}}}}
</style>
</head>
<body>
<div class="lp-bar" id="lpBar"><a class="lp-logo" href="{root}"><img src="{root}images/f304c8479b1fe873.png" alt="Keith Nah"><span><b>Keith Nah</b><small>Malaysia Real Estate</small></span></a>
<nav class="lp-nav">{navh}</nav><a class="lp-cta" href="{wa_price}" target="_blank" rel="noopener">Get the price list</a></div>
<section class="lp-hero"><div class="lp-hero-in"><span class="lp-eb">{eyebrow}</span><h1>{name}</h1><p class="lp-hook">{hook}</p><p class="lp-intro">{intro}</p>
<div class="lp-facts">{factsh}</div><div class="lp-btns"><a class="lp-wa" href="{wa_price}" target="_blank" rel="noopener">{chat}<span>Get the latest price list</span></a><a class="lp-ghost" href="#layouts">See the layouts &rarr;</a></div></div></section>
<div class="lp-chips">{navh}</div>
<section class="lp-sec" id="overview"><span class="lp-eb">Overview</span><h2>Two towers, four layouts, in the middle of Kuala Lumpur.</h2><p>{overview}</p><div class="lp-nums">{nums}</div></section>
<section class="lp-sec" id="five"><span class="lp-eb">Before you look</span><h2>Five things worth knowing first.</h2><ol class="lp-five">{five}</ol></section>
<section class="lp-sec" id="layouts"><span class="lp-eb">Layouts</span><h2>Choose a layout to see the plan.</h2><div class="lp-tabs">{tabs}</div>{panes}</section>
<section class="lp-sec" id="price"><span class="lp-eb">Price</span><h2>Price and running costs.</h2><div class="lp-price"><div class="lp-pbox"><small>Starting price</small><b>{price}</b><p>Prices change as units sell. Ask Keith for the current price list and the units still open.</p><div class="lp-row">{wb_list}</div></div>
<div class="lp-plist"><div><span>Price per sq ft</span><b>{psf}</b></div><div><span>Maintenance fee</span><b>{maint}</b></div><div><span>Car parks</span><b>{park}</b></div><a class="lp-map" href="{root}calculator.html">Work out the monthly instalment &rarr;</a></div></div>
<div class="lp-row">{wb_units}</div></section>
<section class="lp-sec" id="location"><span class="lp-eb">Location</span><h2>Jalan Hang Jebat, in KL City Centre.</h2><div class="lp-loc"><div><p>{loc_text}</p><a class="lp-map" href="{maps}" target="_blank" rel="noopener">Open in Google Maps &rarr;</a><div class="lp-row">{wb_view}</div></div><ul>{amen}</ul></div></section>
<section class="lp-sec" id="foreign"><div class="lp-fb"><span class="lp-eb">Foreign buyers</span><h2>Buying from overseas? Check the unit first.</h2><p>{foreign}</p>{wb_foreign}<a class="lp-link" href="{root}foreign-buyers.html">Read the foreign buyer guide</a></div></section>
<section class="lp-sec" id="faq"><span class="lp-eb">FAQ</span><h2>{name} FAQ.</h2><div class="lp-faq">{faqh}</div><div class="lp-dev"><span class="lp-eb" style="color:var(--gold)">Developer</span><p>{developer}</p></div></section>
<section class="lp-more"><h2>Also worth a look nearby</h2><div class="lp-nbs">{nearby}</div><div class="lp-links"><a href="{root}compare.html">Compare projects &rarr;</a><a href="{root}projects.html">All projects &rarr;</a><a href="{root}foreign-buyers.html">Foreign buyers &rarr;</a><a href="{root}calculator.html">Calculators &rarr;</a></div></section>
<footer class="lp-foot">&copy; 2026 Keith Nah Real Estate &middot; <a href="{root}">keithnah.com</a></footer>
<a class="lp-wa lp-float" href="{wa_price}" target="_blank" rel="noopener">{chat}<span>WhatsApp Keith</span></a>
<script>(function(){{var b=document.getElementById('lpBar');var f=document.querySelector('.lp-float');function s(){{b.classList.toggle('solid',window.scrollY>60);f.classList.toggle('show',window.scrollY>window.innerHeight*0.8);}}s();window.addEventListener('scroll',s,{{passive:true}});
document.addEventListener('click',function(e){{var t=e.target.closest('.lp-tab');if(!t)return;var k=t.getAttribute('data-t');document.querySelectorAll('.lp-tab').forEach(function(x){{x.classList.toggle('on',x===t);}});
document.querySelectorAll('.lp-pane').forEach(function(x){{x.classList.toggle('on',x.getAttribute('data-p')===k);}});}});}})();</script>
</body>
</html>
'''

if __name__ == '__main__':
    slug = sys.argv[1] if len(sys.argv) > 1 else 'maba-suitez'
    out = sys.argv[2] if len(sys.argv) > 2 else 'property/zz-%s-preview.html' % slug
    open(out, 'w', encoding='utf-8').write(page(slug))
    print('landing page:', out)
