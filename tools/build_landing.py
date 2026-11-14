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

    nav = [('overview', 'Overview'), ('five', '5 things'), ('details', 'Details'), ('layouts', 'Layouts'), ('price', 'Price'), ('location', 'Location'),
           ('foreign', 'Foreign buyers'), ('faq', 'FAQ')]
    navh = ''.join('<a href="#%s">%s</a>' % (k, E(v)) for k, v in nav)
    st, area = A.PLACES[i]
    crumbs = '<a href="{r}">Home</a><i>›</i><a href="{r}projects.html">Projects</a><i>›</i><a href="{r}area/{s}.html">{st}</a><i>›</i><a href="{r}area/{a}.html">{ar}</a><i>›</i><b>{n}</b>'.format(
        r=root, s=A.slug(st), st=E(st), a=A.slug(area), ar=E(area), n=E(name))
    mo = ''
    try:
        mo = re.search(r'data-mo>([^<]+)<', open('property/%s.html' % slug, encoding='utf-8').read()).group(1)
    except (OSError, AttributeError):
        pass
    badges = ''.join('<span class="lp-bd%s">%s</span>' % (c, E(v)) for c, v in ((' dark', p.get('status')), ('', area), ('', A.TYPE.get(i, 'Residential'))) if v)
    rows = [('Project Name', name), ('Location', p['loc']), ('Property Type', A.TYPE.get(i, 'Residential')), ('Tenure', p['tenure']), ('Status', p.get('status', '')),
            ('Starting Price', p['price']), ('Size', p['size']), ('Bedrooms', p['rooms']), ('Completion', p['completion'])] + [(k, v) for k, v in ex.items() if k not in ('Title', 'Address')]
    details = ''.join('<tr><th scope="row">%s</th><td>%s</td></tr>' % (E(a), E(b)) for a, b in rows if b)
    fits = ''.join('<div><b>%s</b><p>%s</p></div>' % (E(f['title']), E(f['desc'])) for f in p.get('buyer_fit') or [])

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
        navh=navh, crumbs=crumbs, mo=E(mo), badges=badges, details=details, fits=fits, loc=E(p['loc']), wa_price=wa_price, chat=chat, eyebrow=E(L['eyebrow']), hook=E(L['hook']), intro=E(L['intro']), factsh=factsh,
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
*{{box-sizing:border-box;margin:0;padding:0}} html{{scroll-behavior:smooth;scroll-padding-top:120px}} @media(max-width:1180px){{html{{scroll-padding-top:160px}}}} body{{font-family:Inter,system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6}}
a{{color:inherit;text-decoration:none}} img{{display:block;max-width:100%}} button{{font:inherit}}
h1,h2,h3{{font-family:'Playfair Display',Georgia,serif;line-height:1.2}}
.lp-head{{position:sticky;top:0;z-index:50;box-shadow:0 6px 20px rgba(29,27,79,.18)}}
.lp-util{{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:6px 4vw;background:#1d1b4f}}
.lp-sws{{display:flex;gap:8px}} .lp-sw{{position:relative}} .lp-sel{{all:unset;cursor:pointer;display:flex;align-items:center;gap:6px;font:600 12px Inter,sans-serif;color:#fff;padding:6px 12px;border-radius:99px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22)}}
.lp-sel:hover{{background:rgba(255,255,255,.22)}} .lp-sel svg{{width:13px;height:13px;stroke:#fff;fill:none;stroke-width:1.6}}
.lp-menu{{display:none;position:absolute;top:calc(100% + 8px);right:0;background:#fff;border:1px solid rgba(17,17,17,.08);border-radius:12px;box-shadow:0 16px 40px rgba(17,17,17,.18);padding:8px;z-index:80;min-width:210px}} .lp-menu.cur{{min-width:260px}} .lp-menu.open{{display:block}}
.lp-menu a{{display:flex;align-items:center;gap:10px;white-space:nowrap;padding:9px 14px;font:500 13px Inter,sans-serif;color:#111;border-radius:8px;cursor:pointer}} .lp-menu a:hover{{background:#F9F8F6}} .lp-menu a.active{{color:#5E60CE;font-weight:700}}
.lp-bar{{display:flex;align-items:center;gap:18px;padding:10px 4vw;background:#5E60CE;box-shadow:0 6px 20px rgba(29,27,79,.18)}}
.lp-home{{display:inline-flex;align-items:center;gap:6px;color:#fff;font-size:12.5px;font-weight:700;white-space:nowrap;opacity:.9}} .lp-home:hover{{opacity:1;text-decoration:underline}}  .lp-hs{{display:none;font-style:normal}} @media(max-width:820px){{.lp-hs{{display:inline}}}}
.lp-logo{{display:flex;align-items:center;gap:10px;color:#fff}} .lp-logo img{{width:38px;height:38px;border-radius:50%}} .lp-logo b{{font-family:'Playfair Display',serif;font-size:17px;display:block;line-height:1.1;white-space:nowrap}} .lp-logo small{{font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;opacity:.75}}
.lp-nav{{display:flex;gap:20px;margin:0 auto}} .lp-nav a{{color:rgba(255,255,255,.9);font-size:12.5px;font-weight:600;letter-spacing:.08em;text-transform:uppercase}} .lp-nav a:hover{{color:#fff}}
.lp-cta{{background:var(--wa);color:#fff;font-weight:700;font-size:13.5px;padding:10px 18px;border-radius:99px;white-space:nowrap}}
.lp-eb{{display:block;font-size:12px;font-weight:800;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);margin-bottom:12px}}
.lp-top{{max-width:1180px;margin:0 auto;padding:22px 5vw 0}} .lp-crumb{{display:flex;flex-wrap:wrap;gap:8px;font-size:13.5px;color:var(--grey);margin-bottom:22px}} .lp-crumb i{{font-style:normal;opacity:.5}} .lp-crumb b{{color:var(--ink)}}
.lp-hero{{display:grid;grid-template-columns:1.05fr 1fr;gap:40px;align-items:center}} .lp-photo{{border-radius:20px;overflow:hidden;aspect-ratio:4/3;background:var(--soft);box-shadow:0 18px 40px rgba(29,27,79,.14)}} .lp-photo img{{width:100%;height:100%;object-fit:cover}}
.lp-bds{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}} .lp-bd{{font-size:11.5px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;padding:6px 12px;border-radius:99px;background:#ecebfb;color:var(--gold)}} .lp-bd.dark{{background:var(--ink);color:#fff}}
.lp-info h1{{font-size:clamp(38px,4.6vw,60px);font-weight:700}} .lp-hook{{color:var(--gold);font-weight:700;font-size:16px;margin:8px 0 4px}} .lp-locl{{color:var(--grey);font-size:15.5px}}
.lp-sp{{margin:18px 0 6px}} .lp-sp small{{display:block;font-size:11.5px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--grey)}} .lp-sp b{{font-family:'Playfair Display',serif;font-size:clamp(28px,3vw,38px);color:var(--gold)}}
.lp-mo{{font-size:14.5px;color:var(--grey)}} .lp-mo b{{font-family:'Playfair Display',serif;font-size:20px;color:var(--ink);margin-left:6px}} .lp-mo a{{display:block;color:var(--gold);font-weight:600;font-size:13.5px;text-decoration:underline;margin-top:2px}}
.lp-info .lp-btns{{margin-top:18px}} .lp-out{{display:inline-flex;align-items:center;padding:14px 22px;border-radius:99px;border:1.5px solid var(--ink);font-weight:700;font-size:14.5px}}
.lp-facts{{display:grid;grid-template-columns:repeat(5,1fr);background:#fff;border:1px solid var(--line);border-radius:18px;margin-top:34px}} .lp-facts div{{padding:18px 20px;border-left:1px solid var(--line)}} .lp-facts div:first-child{{border:0}} .lp-facts small{{display:block;font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--grey)}} .lp-facts b{{font-family:'Playfair Display',serif;font-size:17px}}
.pi{{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 10px 30px rgba(17,17,17,.08);border:1px solid var(--line);margin-top:24px}}
.pi-head{{background:linear-gradient(135deg,#5E60CE,#4A4CB8);color:#fff;text-align:center;font:700 22px/1.3 Inter,sans-serif;padding:20px 16px}}
.pi table{{width:100%;border-collapse:collapse}} .pi th,.pi td{{padding:16px 24px;text-align:left;vertical-align:top;font-size:15px;line-height:1.55}}
.pi th{{width:24%;min-width:170px;background:#5E60CE;color:#fff;font-weight:600;border-bottom:1px solid rgba(255,255,255,.22)}} .pi td{{color:#222;border-bottom:1px solid var(--line)}}
.pi tr:last-child th,.pi tr:last-child td{{border-bottom:0}} .pi tr:nth-child(even) td{{background:#FAFAFD}}
@media(max-width:820px){{.pi th,.pi td{{display:block;width:auto;padding:10px 16px}} .pi th{{border-bottom:0;font-size:13px;padding-bottom:8px}} .pi td{{padding-top:10px;padding-bottom:14px}} .pi-head{{font-size:19px;padding:16px}}}}
.lp-dt{{background:#fff;border:1px solid var(--line);border-radius:20px;overflow:hidden;margin-top:24px}} .lp-dt table{{width:100%;border-collapse:collapse}} .lp-dt th,.lp-dt td{{text-align:left;padding:13px 22px;border-bottom:1px solid var(--line);font-size:14.5px;vertical-align:top}} .lp-dt th{{width:32%;color:var(--grey);font-weight:600;background:#faf9fd}} .lp-dt tr:last-child th,.lp-dt tr:last-child td{{border:0}}
.lp-fits{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:22px}} .lp-fits div{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:20px}} .lp-fits b{{font-size:16px}} .lp-fits p{{color:var(--grey);font-size:14px;margin-top:4px}}
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
@media(max-width:1180px){{.lp-nav{{display:none}} .lp-bar{{justify-content:space-between}} .lp-cta{{margin-left:auto}}}}
@media(max-width:820px){{.lp-nums{{grid-template-columns:1fr 1fr}} .lp-pane.on,.lp-price,.lp-loc{{grid-template-columns:1fr;display:grid}} .lp-pane{{padding:16px}} .lp-pd dl{{grid-template-columns:1fr 1fr}} .lp-nbs{{grid-template-columns:1fr}}
 .lp-hero{{grid-template-columns:1fr;gap:22px}} .lp-top{{padding:16px 20px 0}} .lp-facts{{grid-template-columns:1fr 1fr}} .lp-facts div{{border-left:0;border-top:1px solid var(--line)}} .lp-fits{{grid-template-columns:1fr}} .lp-dt th,.lp-dt td{{padding:11px 14px;font-size:13.5px}} .lp-home span{{display:none}} .lp-logo>span{{display:none}} .lp-sec{{padding:64px 20px 0}} .lp-five li{{padding:18px;gap:14px}} .lp-fb{{padding:28px 22px}} .lp-logo small{{display:none}} .lp-cta{{padding:9px 14px;font-size:12.5px}}}}
.lp-chips{{display:none}} @media(max-width:1180px){{.lp-chips{{display:flex;position:sticky;top:100px;z-index:30;gap:8px;overflow-x:auto;padding:10px 16px;background:var(--bg);border-bottom:1px solid var(--line)}} .lp-chips a{{flex:0 0 auto;font-size:13px;font-weight:700;padding:7px 14px;border-radius:99px;background:#fff;border:1px solid var(--line)}}}}
</style>
</head>
<body>
<header class="lp-head" id="lpBar"><div class="lp-util"><a class="lp-home" href="{root}">&larr; <span>Back to home website</span><em class="lp-hs">Home</em></a><div class="lp-sws"><div class="lp-sw"><button type="button" class="lp-sel" data-m="lpLang"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.5 4 5.7 4 9s-1.5 6.5-4 9c-2.5-2.5-4-5.7-4-9s1.5-6.5 4-9z"/></svg><span id="lpLangLab">English</span></button><div class="lp-menu" id="lpLang"><a data-lang="en"><img src="{root}images/flags/gb.svg" alt="" width="20" height="15">English</a><a data-lang="zh-CN"><img src="{root}images/flags/cn.svg" alt="" width="20" height="15">简体中文</a><a data-lang="zh-TW"><img src="{root}images/flags/tw.svg" alt="" width="20" height="15">繁體中文</a><a data-lang="ms"><img src="{root}images/flags/my.svg" alt="" width="20" height="15">Bahasa Malaysia</a><a data-lang="ja"><img src="{root}images/flags/jp.svg" alt="" width="20" height="15">日本語</a><a data-lang="ko"><img src="{root}images/flags/kr.svg" alt="" width="20" height="15">한국어</a></div></div><div class="lp-sw"><button type="button" class="lp-sel" data-m="lpCur"><svg viewBox="0 0 24 24"><circle cx="8" cy="8" r="5"/><circle cx="16" cy="16" r="5"/></svg><span id="lpCurLab">MYR</span></button><div class="lp-menu cur" id="lpCur"><a data-cur="MYR"><img src="{root}images/flags/my.svg" alt="" width="20" height="15"><b>MYR</b> Malaysian Ringgit</a><a data-cur="USD"><img src="{root}images/flags/us.svg" alt="" width="20" height="15"><b>USD</b> US Dollar</a><a data-cur="SGD"><img src="{root}images/flags/sg.svg" alt="" width="20" height="15"><b>SGD</b> Singapore Dollar</a><a data-cur="CNY"><img src="{root}images/flags/cn.svg" alt="" width="20" height="15"><b>CNY</b> Chinese Yuan</a><a data-cur="JPY"><img src="{root}images/flags/jp.svg" alt="" width="20" height="15"><b>JPY</b> Japanese Yen</a><a data-cur="KRW"><img src="{root}images/flags/kr.svg" alt="" width="20" height="15"><b>KRW</b> Korean Won</a></div></div></div></div><div class="lp-bar"><a class="lp-logo" href="{root}"><img src="{root}images/f304c8479b1fe873.png" alt="Keith Nah"><span><b>Keith Nah</b><small>Malaysia Real Estate</small></span></a><nav class="lp-nav">{navh}</nav><a class="lp-cta" href="{wa_price}" target="_blank" rel="noopener">Get the price list</a></div></header>
<div class="lp-top"><nav class="lp-crumb" aria-label="Breadcrumb">{crumbs}</nav>
<section class="lp-hero"><div class="lp-photo"><img src="{photo}" alt="{name}"></div><div class="lp-info"><div class="lp-bds">{badges}</div><h1>{name}</h1><p class="lp-hook">{hook}</p><p class="lp-locl">{loc}</p>
<div class="lp-sp"><small>Starting price</small><b>{price}</b></div><div class="lp-mo">Est. monthly instalment from<b>{mo}</b><a href="{root}calculator.html">Change down payment &amp; rate</a></div>
<div class="lp-btns"><a class="lp-wa" href="{wa_price}" target="_blank" rel="noopener">{chat}<span>Get the latest price list</span></a><a class="lp-out" href="{root}compare.html">Compare projects</a></div></div></section>
<div class="lp-facts">{factsh}</div></div>
<div class="lp-chips">{navh}</div>
<section class="lp-sec" id="overview"><span class="lp-eb">Overview</span><h2>Two towers, four layouts, in the middle of Kuala Lumpur.</h2><p>{overview}</p><div class="lp-nums">{nums}</div></section>
<section class="lp-sec" id="five"><span class="lp-eb">Before you look</span><h2>Five things worth knowing first.</h2><ol class="lp-five">{five}</ol></section>
<section class="lp-sec" id="details"><span class="lp-eb">Project details</span><h2>{name} at a glance.</h2><div class="pi"><div class="pi-head">Project Information</div><table>{details}</table></div><div class="lp-fits">{fits}</div></section>
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
<script>(function(){{var b=document.getElementById('lpBar');var f=document.querySelector('.lp-float');function s(){{f.classList.toggle('show',window.scrollY>window.innerHeight*0.8);}}s();window.addEventListener('scroll',s,{{passive:true}});
var LL={{"en":"English","zh-CN":"简体中文","zh-TW":"繁體中文","ms":"Bahasa Malaysia","ja":"日本語","ko":"한국어"}};
function get(k,d){{try{{return localStorage.getItem(k)||d}}catch(e){{return d}}}}function put(k,v){{try{{localStorage.setItem(k,v)}}catch(e){{}}}}
function mark(){{var l=get('kn_lang','en'),c=get('kn_currency','MYR');document.getElementById('lpLangLab').textContent=LL[l]||'English';document.getElementById('lpCurLab').textContent=c;
document.querySelectorAll('[data-lang]').forEach(function(a){{a.classList.toggle('active',a.getAttribute('data-lang')===l);}});document.querySelectorAll('[data-cur]').forEach(function(a){{a.classList.toggle('active',a.getAttribute('data-cur')===c);}});}}mark();
document.addEventListener('click',function(e){{var s=e.target.closest('.lp-sel');document.querySelectorAll('.lp-menu.open').forEach(function(m){{if(!s||m.id!==s.getAttribute('data-m'))m.classList.remove('open');}});
if(s){{document.getElementById(s.getAttribute('data-m')).classList.toggle('open');return;}}
var a=e.target.closest('[data-lang]');if(a){{put('kn_lang',a.getAttribute('data-lang'));mark();return;}}var c=e.target.closest('[data-cur]');if(c){{put('kn_currency',c.getAttribute('data-cur'));mark();return;}}}});
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
