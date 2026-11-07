"""'Best of' and search-intent pages: best/<slug>.html plus best/index.html.

Each page is a filtered, sorted list built from the project data (price,
tenure, transit tags, completion, size, psf), with a short intro, project
cards, a comparison table and FAQ. Uses the look of the area guides.

    python3 tools/build_list_pages.py                  # writes best/*.html
    python3 tools/build_list_pages.py --preview DIR     # standalone preview with absolute links
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_area_pages as A
import float_wa as FW
import site_header as SH

P, PLACES, E, SITE, YEAR = A.P, A.PLACES, A.E, A.SITE, A.YEAR
TAGS = A.js('var KN_TAGS = ')


def nums(s):
    return [float(x.replace(',', '')) for x in re.findall(r'\d[\d,]*(?:\.\d+)?', s or '')]


def price(k):
    return A.price_rm(P[k].get('price'))


def psf(k):
    v = (P[k].get('details_extra') or {}).get('Price per Sqft', '')
    n = [x for x in nums(v) if x >= 200]
    return min(n) if n else None


def size_max(k):
    n = [x for x in nums(P[k].get('size')) if x >= 200]
    return max(n) if n else None


def year(k):
    y = [int(x) for x in re.findall(r'\b(20[2-4]\d)\b', P[k].get('completion') or '')]
    return min(y) if y else None


def when(k):
    """Sort key for the earliest completion: year, then quarter (month names map to quarters)."""
    c = P[k].get('completion') or ''
    best = None
    for m in re.finditer(r'(?:Q([1-4])\s*)?(?:(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*)?(20[2-4]\d)', c):
        q = int(m.group(1)) if m.group(1) else ('JanFebMarAprMayJunJulAugSepOctNovDec'.index(m.group(2)) // 9 + 1 if m.group(2) else 4)
        key = (int(m.group(3)), q)
        best = key if best is None or key < best else best
    return best or (9999, 9)


def has(k, tag):
    return any(t.lower() == tag.lower() for t in TAGS[k])


free = lambda k: (P[k].get('tenure') or '').lower().startswith('freehold')
done = lambda k: (P[k].get('status') or '') == 'Completed'
rail = lambda k: has(k, 'condo near MRT station') or has(k, 'condo near LRT station')
ALL = list(range(len(P)))
by_price = lambda ks: sorted(ks, key=lambda k: price(k) or 9e9)

# slug, title, h1, intro, ids, sort note, extra column (label, function)
LISTS = [
    ('freehold-under-rm1-million-near-mrt-lrt', 'Freehold Condos Under RM1 Million Near MRT/LRT',
     'Freehold new launches under RM1 million, near an MRT or LRT station',
     'Freehold title, a starting price below RM1 million and a rail station nearby: three things many buyers want and few projects offer together. These are the ones Keith lists, cheapest first.',
     by_price([k for k in ALL if free(k) and price(k) and price(k) < 1e6 and rail(k)]), None),
    ('new-launch-under-rm500k', 'New Launch Property Under RM500K in Malaysia',
     'New launches under RM500,000',
     'Entry-level new launches with a published starting price below RM500,000, for first-home buyers and investors with a smaller budget. Sorted from the lowest starting price.',
     by_price([k for k in ALL if price(k) and price(k) < 5e5]), None),
    ('new-launch-rm500k-to-rm1-million', 'New Launch Condos from RM500K to RM1 Million',
     'New launches from RM500,000 to RM1 million',
     "The most popular price band for upgraders and families: projects starting between RM500,000 and RM1 million. Sorted from the lowest starting price.",
     by_price([k for k in ALL if price(k) and 5e5 <= price(k) < 1e6]), None),
    ('luxury-new-launch-above-rm1-million', 'Luxury New Launch Condos Above RM1 Million',
     'Luxury new launches from RM1 million',
     'Premium and luxury projects with a starting price of RM1 million or more, from city-centre suites to large family residences. Sorted from the lowest starting price.',
     by_price([k for k in ALL if price(k) and price(k) >= 1e6]), None),
    ('lowest-price-per-sqft-kuala-lumpur', 'Lowest Price per Sqft New Launches in Kuala Lumpur',
     'Kuala Lumpur new launches with the lowest price per sqft',
     'Price per square foot is the fairest way to compare projects of different sizes. These Kuala Lumpur projects are sorted by their published starting psf (gross), lowest first.',
     sorted([k for k in ALL if PLACES[k][0] == 'Kuala Lumpur' and psf(k)], key=psf), ('From psf', lambda k: 'RM%s' % format(int(psf(k)), ','))),
    ('largest-homes-under-rm1-5-million', 'Largest New Launch Homes Under RM1.5 Million',
     'The largest homes under RM1.5 million',
     'The 20 projects starting below RM1.5 million with the largest unit sizes, biggest first. Useful for families who need space without a luxury budget.',
     sorted([k for k in ALL if price(k) and price(k) < 1.5e6 and size_max(k)], key=lambda k: -size_max(k))[:20], ('Largest unit', lambda k: '%s sqft' % format(int(size_max(k)), ','))),
    ('freehold-condo-kuala-lumpur', 'Freehold New Launch Condos in Kuala Lumpur',
     'Freehold new launches in Kuala Lumpur',
     'Freehold title means you own the land with no lease to renew. These are the freehold projects Keith lists in Kuala Lumpur, cheapest first.',
     by_price([k for k in ALL if PLACES[k][0] == 'Kuala Lumpur' and free(k)]), None),
    ('freehold-condo-selangor', 'Freehold New Launch Condos in Selangor',
     'Freehold new launches in Selangor',
     'Freehold projects in Selangor, from Petaling Jaya and Damansara to Kwasa Damansara and Subang Jaya, cheapest first.',
     by_price([k for k in ALL if PLACES[k][0] == 'Selangor' and free(k)]), None),
    ('condo-near-mrt-station', 'New Launch Condos Near MRT Stations',
     'New launches near an MRT station',
     'Projects whose location includes an MRT station within reach, for car-free commuting and steady rental demand. Cheapest first.',
     by_price([k for k in ALL if has(k, 'condo near MRT station')]), None),
    ('condo-near-lrt-station', 'New Launch Condos Near LRT Stations',
     'New launches near an LRT station',
     'Projects close to an LRT station, from KL City Centre and Bangsar South to Bukit Jalil and Ara Damansara. Cheapest first.',
     by_price([k for k in ALL if has(k, 'condo near LRT station')]), None),
    ('dual-key-units', 'Dual Key New Launch Condos in Malaysia',
     'New launches with dual-key units',
     'A dual-key unit splits into two separate spaces with their own doors and bathrooms: live in one and rent out the other, or rent both. These projects offer dual-key layouts.',
     by_price([k for k in ALL if has(k, 'dual key unit')]), None),
    ('studio-units', 'New Launch Condos with Studio Units',
     'New launches with studio units',
     'Studio and compact suites for first-time investors and single professionals. Cheapest first.',
     by_price([k for k in ALL if has(k, 'studio unit')]), None),
    ('completed-ready-to-move-in', 'Completed Condos Ready to Move In',
     'Completed projects, ready to move in',
     'Projects that are already completed, so you can view the actual unit and move in or rent it out straight away.',
     by_price([k for k in ALL if done(k)]), None),
    ('completing-by-2028', 'New Launches Completing by 2028',
     'New launches completing by 2028',
     'Under-construction projects with an expected completion year of 2028 or earlier, sorted by completion date, soonest first.',
     sorted([k for k in ALL if not done(k) and year(k) and year(k) <= 2028], key=lambda k: (when(k), price(k) or 9e9)), ('Completion', lambda k: E(P[k].get('completion')))),
    ('near-rts-link-johor-bahru', 'Property Near the RTS Link in Johor Bahru',
     'Johor Bahru projects near the RTS Link',
     'The RTS Link will connect Bukit Chagar in Johor Bahru with Woodlands in Singapore. These projects list the RTS Link or the JB CIQ checkpoint among their nearby landmarks.',
     by_price([k for k in ALL if has(k, 'condo near RTS Link JB') or has(k, 'condo near JB CIQ')]), None),
]


# ---------- more lists, all rule based (new projects join automatically) ----------
TXT = lambda k: ' '.join([P[k].get('loc', ''), P[k].get('loc_text', ''), P[k].get('overview', '')] + (P[k].get('amenities') or [])
                         + (P[k].get('selling_points') or []) + (P[k].get('points') or [])).lower()


def beds(k):
    """(min, max) bedrooms from the rooms text; Studio counts as 0."""
    r = re.sub(r'\d+(?:\+\d)?\s*Bath\w*', '', P[k].get('rooms') or '', flags=re.I)
    n = [int(x) for x in re.findall(r'(\d)(?:\+\d)?\s*(?:–|-|to|Bed|R\b|Room|$|\s)', r)]
    if re.search(r'studio', r, re.I):
        n.append(0)
    return (min(n), max(n)) if n else None


def units(k):
    m = re.search(r'(\d[\d,]*)\s*(?:units|suites|homes)', (P[k].get('details_extra') or {}).get('Total Units', ''), re.I)
    return int(m.group(1).replace(',', '')) if m else None


def title(k):
    return (P[k].get('details_extra') or {}).get('Title', '')


st = lambda k: PLACES[k][0]
bed_has = lambda k, n: beds(k) is not None and beds(k)[0] <= n <= beds(k)[1]
anytag = lambda k, *ts: any(has(k, t) for t in ts)
LISTS += [
    ('new-launch-under-rm800k', 'New Launch Condos Under RM800K', 'New launches under RM800,000',
     'A popular budget for first homes and investment units: projects with a published starting price below RM800,000, cheapest first.',
     by_price([k for k in ALL if price(k) and price(k) < 8e5]), None),
    ('new-launch-kuala-lumpur-under-rm700k', 'New Launch Condos in Kuala Lumpur Under RM700K', 'Kuala Lumpur new launches under RM700,000',
     'Kuala Lumpur addresses that start below RM700,000, from the city centre to Bukit Jalil and Bangsar South. Cheapest first.',
     by_price([k for k in ALL if st(k) == 'Kuala Lumpur' and price(k) and price(k) < 7e5]), None),
    ('new-launch-selangor-under-rm700k', 'New Launch Condos in Selangor Under RM700K', 'Selangor new launches under RM700,000',
     'Selangor projects that start below RM700,000, in Petaling Jaya, Damansara, Kwasa Damansara and Subang Jaya. Cheapest first.',
     by_price([k for k in ALL if st(k) == 'Selangor' and price(k) and price(k) < 7e5]), None),
    ('freehold-condo-penang', 'Freehold New Launch Condos in Penang', 'Freehold new launches in Penang',
     'Freehold projects on Penang island and the mainland, cheapest first.',
     by_price([k for k in ALL if st(k) == 'Penang' and free(k)]), None),
    ('freehold-condo-johor-bahru', 'Freehold New Launch Condos in Johor Bahru', 'Freehold new launches in Johor Bahru',
     'Freehold projects in Johor Bahru, close to the Causeway and the upcoming RTS Link. Cheapest first.',
     by_price([k for k in ALL if st(k) == 'Johor' and free(k)]), None),
    ('2-bedroom-new-launch', '2-Bedroom New Launch Condos', 'New launches with 2-bedroom units',
     'Projects that offer 2-bedroom layouts, a favourite of young couples and rental investors. Cheapest first.',
     by_price([k for k in ALL if bed_has(k, 2)]), ('Bedrooms', lambda k: E(P[k].get('rooms')))),
    ('3-bedroom-new-launch', '3-Bedroom New Launch Condos', 'New launches with 3-bedroom units',
     'Projects that offer 3-bedroom layouts for families and upgraders. Cheapest first.',
     by_price([k for k in ALL if bed_has(k, 3)]), ('Bedrooms', lambda k: E(P[k].get('rooms')))),
    ('4-bedroom-family-homes', '4-Bedroom and Larger Family Homes', 'New launches with 4 bedrooms or more',
     'Projects with 4-bedroom (or larger) layouts for big and multi-generation families. Cheapest first.',
     by_price([k for k in ALL if beds(k) and beds(k)[1] >= 4]), ('Bedrooms', lambda k: E(P[k].get('rooms')))),
    ('large-condo-above-1500-sqft', 'Large New Launch Condos Above 1,500 sqft', 'Large homes above 1,500 sqft',
     'Projects whose largest layouts are 1,500 sqft or more, sorted by largest unit size, biggest first.',
     sorted([k for k in ALL if size_max(k) and size_max(k) >= 1500], key=lambda k: -size_max(k)), ('Largest unit', lambda k: '%s sqft' % format(int(size_max(k)), ','))),
    ('residential-title-condo', 'Residential Title New Launch Condos', 'New launches with residential title',
     'Residential title usually means residential utility rates and maintenance rules, and is preferred by many owner-occupiers over commercial-titled serviced apartments. Cheapest first.',
     by_price([k for k in ALL if 'residential' in title(k).lower() and 'commercial' not in title(k).lower()]), None),
    ('low-density-condo', 'Low Density New Launch Condos (Under 400 Units)', 'Low-density projects with fewer than 400 units',
     'Fewer neighbours means quieter lifts, facilities and car parks. These projects have under 400 units in total, fewest first.',
     sorted([k for k in ALL if units(k) and 10 < units(k) < 400], key=units), ('Total units', lambda k: format(units(k), ','))),
    ('latest-new-launch-2026', 'Latest New Launches in Malaysia (2026)', 'The latest new launches',
     'Projects that are newly launched or coming soon, so you can get in at the start. Cheapest first.',
     by_price([k for k in ALL if (P[k].get('status') or '') in ('Coming Soon', 'New Launch')]), None),
    ('condo-near-international-school', 'New Launch Condos Near International Schools', 'New launches near international schools',
     'Projects that list an international school among their nearby amenities, for expat and local families. Cheapest first.',
     by_price([k for k in ALL if 'international school' in TXT(k)]), None),
    ('condo-near-hospital', 'New Launch Condos Near Hospitals', 'New launches near hospitals',
     'Projects that list a hospital or medical centre nearby, useful for retirees, families and medical staff. Cheapest first.',
     by_price([k for k in ALL if re.search(r'hospital|medical centre', TXT(k))]), None),
    ('condo-near-university', 'New Launch Condos Near Universities', 'New launches near universities',
     'Projects close to a university, popular with lecturers, families and student-rental investors. Cheapest first.',
     by_price([k for k in ALL if re.search(r'universit', TXT(k))]), None),
    ('condo-near-pavilion', 'New Launch Condos Near Pavilion', 'New launches near Pavilion Kuala Lumpur and Pavilion Bukit Jalil',
     'Projects within reach of Pavilion Kuala Lumpur in Bukit Bintang or Pavilion Bukit Jalil. Cheapest first.',
     by_price([k for k in ALL if anytag(k, 'condo near Pavilion KL', 'condo near Pavilion Bukit Jalil')]), None),
    ('condo-near-petronas-twin-towers', 'New Launch Condos Near the Petronas Twin Towers', 'New launches near the Petronas Twin Towers',
     'Projects around the Petronas Twin Towers and KL City Centre Park, cheapest first.',
     by_price([k for k in ALL if anytag(k, 'condo near KL City Centre', 'condo near Petronas Twin Towers')]), None),
    ('condo-near-trx-merdeka-118', 'New Launch Condos Near TRX and Merdeka 118', 'New launches near TRX, Exchange 106 and Merdeka 118',
     "Projects close to Kuala Lumpur's new skyline landmarks: Tun Razak Exchange (TRX), Exchange 106 and Merdeka 118. Cheapest first.",
     by_price([k for k in ALL if anytag(k, 'condo near TRX', 'condo near The Exchange 106', 'condo near Merdeka 118')]), None),
    ('condo-near-mid-valley', 'New Launch Condos Near Mid Valley', 'New launches near Mid Valley',
     'Projects close to Mid Valley Megamall or Mid Valley Southkey, cheapest first.',
     by_price([k for k in ALL if anytag(k, 'condo near Mid Valley Megamall', 'condo near Mid Valley Southkey')]), None),
    ('sea-view-waterfront-condo', 'Sea View and Waterfront New Launch Condos', 'Sea-view and waterfront new launches',
     'Projects that mention sea views or a waterfront setting, from Penang and Melaka to Kota Kinabalu and Kuala Terengganu. Cheapest first.',
     by_price([k for k in ALL if re.search(r'sea view|sea-view|waterfront|seafront|sea-facing', TXT(k))]), None),
    ('greenre-green-building-condo', 'GreenRE Certified Green Building Condos', 'GreenRE-certified green buildings',
     'Projects that are GreenRE certified or designed to green-building standards, for lower running costs and healthier living. Cheapest first.',
     by_price([k for k in ALL if 'greenre' in TXT(k) or 'greenre' in json.dumps(P[k].get('details_extra') or {}).lower()]), None),
    ('condo-with-infinity-pool', 'New Launch Condos with an Infinity or Sky Pool', 'New launches with an infinity or sky pool',
     'Projects with an infinity pool, sky pool or rooftop pool among their facilities. Cheapest first.',
     by_price([k for k in ALL if re.search(r'infinity pool|sky pool|rooftop pool|sky infinity', TXT(k))]), None),
    ('condo-near-ktm-station', 'New Launch Condos Near KTM Stations', 'New launches near a KTM station',
     'Projects close to a KTM Komuter station, cheapest first.',
     by_price([k for k in ALL if has(k, 'condo near KTM station') or re.search(r'\bktm\b', TXT(k))]), None),
]
LISTS = [l for l in LISTS if len(l[4]) >= 3]  # no thin pages

import i18n_pages as I
for _s, _t, _h, _i, _ids, _x in LISTS:
    I.register({_s + '.t': _t, _s + '.h': _h, _s + '.i': _i})
I.register(I.TPL)
I.register({'intro.' + k: v for k, v in A.INTRO.items()})


def membership():
    """{project index: [(slug, title), ...]} for the lists each project appears in."""
    m = {}
    for s, t, h, it, ids, x in LISTS:
        for k in ids:
            m.setdefault(k, []).append((s, t))
    return m


def page(slug, title, h1, intro, ids, extra, root, lists):
    n = len(ids)
    proj = lambda k: '%sproperty/%s.html' % (root, A.SLUG.get(k, A.slug(P[k]['name'])))
    img = lambda k: ('<img src="%s%s" alt="%s" loading="lazy">' % (root, E(A.PHOTO[k]), E(P[k]['name']))) if A.PHOTO.get(k) else '<i class="noimg"></i>'
    wa = 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0' % re.sub(r'\s', '+', '(KNRE) Hi Keith, I saw your list: %s.' % h1)
    cards = ''.join(
        '<a class="card" href="%s">%s<div class="card-b"><small>#%d · %s</small><h3>%s</h3><p>%s</p>'
        '<ul><li><b>Size</b>%s</li><li><b>Bedrooms</b>%s</li><li><b>Tenure</b>%s</li><li><b>Completion</b>%s</li></ul>'
        '<div class="price">%s</div></div></a>' % (
            proj(k), img(k), i + 1, E('%s, %s' % (PLACES[k][1], PLACES[k][0])), E(P[k]['name']), E(P[k]['loc']),
            E(P[k].get('size')), E(P[k].get('rooms')), E(P[k].get('tenure')), E(P[k].get('completion')), SH.price_tag(E(P[k].get('price')), price(k)))
        for i, k in enumerate(ids))
    xh = ('<th>%s</th>' % E(extra[0])) if extra else ''
    rows = ''.join('<tr><td>%d</td><td><a href="%s">%s</a></td><td>%s</td>%s<td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        i + 1, proj(k), E(P[k]['name']), E(PLACES[k][1]), ('<td>%s</td>' % extra[1](k)) if extra else '', E(P[k].get('price')),
        E(P[k].get('size')), E(P[k].get('tenure')), E(P[k].get('completion'))) for i, k in enumerate(ids))
    low = min([price(k) for k in ids if price(k)] or [0])
    faq = [('How many projects are on this list?', 'There are %d projects on this list: %s.' % (n, ', '.join(P[k]['name'] for k in ids))),
           ('How is this list made?', 'It is built from the published details of every project on keithnah.com and updates automatically when projects are added or prices change. Prices are gross starting prices.')]
    if low:
        faq.append(('What is the lowest starting price on this list?', 'About %s (gross), at %s.' % (A.rm(low), P[min((k for k in ids if price(k)), key=price)]['name'])))
    faq.append(('Can Keith help me choose between these projects?', 'Yes. WhatsApp Keith with your budget, preferred area and whether you will live in or rent out the unit, and he will shortlist the best fits and share the latest prices and available units.'))
    faq_html = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (E(q), E(a)) for q, a in faq)
    others = ''.join('<a class="chip" href="%s.html">%s<em>%d</em></a>' % (s, E(t2), len(i2)) for s, t2, h, it, i2, x in lists if s != slug and i2)
    url = '%s/best/%s.html' % (SITE, slug)
    ld = [{'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
              {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
              {'@type': 'ListItem', 'position': 2, 'name': 'Best new launch lists', 'item': SITE + '/best/'},
              {'@type': 'ListItem', 'position': 3, 'name': title, 'item': url}]},
          {'@context': 'https://schema.org', '@type': 'ItemList', 'name': title, 'numberOfItems': n,
           'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': '%s/property/%s.html' % (SITE, A.SLUG.get(k, '')), 'name': P[k]['name']} for i, k in enumerate(ids)]},
          {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
              {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}]
    full_title = '%s (%d) | Keith Nah' % (title, YEAR)
    desc = '%d projects: %s Prices, sizes, tenure and completion compared.' % (n, intro.split('. ')[0] + '.')
    nav = ''.join('<a href="%s%s">%s</a>' % (root, h, E(t)) for h, t in A.NAV)
    return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{full}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{full}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}">
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
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{root}">Home</a><span>›</span><a href="index.html">Best new launch lists</a><span>›</span><strong>{title}</strong></nav>
  <section class="hero">
    <span class="eyebrow">Updated {year} · {n} projects</span>
    <h1>{h1} ({year})</h1>
    <p>{intro}</p>
  </section>
  <section class="blk"><div class="cards">{cards}</div></section>
  <section class="blk"><h2>Compare at a glance</h2><div class="tbl"><table><thead><tr><th>#</th><th>Project</th><th>Area</th>{xh}<th>Starting price</th><th>Size</th><th>Tenure</th><th>Completion</th></tr></thead><tbody>{rows}</tbody></table></div></section>
  <section class="blk faq"><h2>About this list</h2>{faq}</section>
  <section class="blk"><h2>More lists</h2><div class="chips">{others}</div></section>
  <div class="cta"><h2>Not sure which one fits you?</h2><p>Send Keith your budget and needs, and he will shortlist the right projects and units.</p><a class="wa-btn" href="{wa}" target="_blank" rel="noopener">WhatsApp Keith</a></div>
  <p class="note">Prices are gross starting prices as published and may change. Lists are generated from the project details on this site; confirm the latest prices, units and terms with Keith before deciding.</p>
</main>
<footer>&copy; {year} Keith Nah Real Estate · REN 60517 · IQI Global · <a href="{root}projects.html">All projects</a> · <a href="{root}privacy-policy.html">Privacy Policy</a> · <a href="{root}terms-of-use.html">Terms of Use</a></footer>
{floatwa}
<script src="{root}lead-tracker.js"></script>
</body>
</html>
'''.format(full=E(full_title), desc=E(desc), url=url, root=root, ld=json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'),
           css=A.CSS, fcss=FW.FLOAT_CSS, nav=nav, wa=E(wa), title=E(title), year=YEAR, n=n, h1=E(h1), intro=E(intro),
           cards=cards, xh=xh, rows=rows, faq=faq_html, others=others, floatwa=FW.float_html(E(wa)))


def index(root, lists):
    items = ''.join('<a class="card" href="%s.html"><div class="card-b"><small>%d projects</small><h3>%s</h3><p>%s</p></div></a>' % (
        s, len(ids), E(t), E(it)) for s, t, h, it, ids, x in lists if ids)
    p = page('index', 'Best New Launch Lists', 'Best new launch lists', 'Shortcuts to the projects that match what you are looking for: budget, freehold, near rail, dual key, studios, completion date and more. Every list updates automatically.', [], None, root, lists)
    p = re.sub(r'<section class="blk"><div class="cards"></div></section>.*?<section class="blk"><h2>More lists</h2>.*?</section>',
               lambda _: '<section class="blk"><div class="cards">%s</div></section>' % items, p, flags=re.S)
    p = p.replace('<link rel="canonical" href="%s/best/index.html">' % SITE, '<link rel="canonical" href="%s/best/">' % SITE)
    p = p.replace('<strong>Best New Launch Lists</strong>', '<strong>Best new launch lists</strong>').replace(
        '<span>›</span><a href="index.html">Best new launch lists</a>', '')
    p = re.sub(r'<span class="eyebrow">Updated \d+ · 0 projects</span>', '<span class="eyebrow">Updated %d</span>' % YEAR, p)
    return p


def build(out, root):
    os.makedirs(out, exist_ok=True)
    lists = [l for l in LISTS if l[4]]
    for s, t, h, it, ids, x in lists:
        open(os.path.join(out, s + '.html'), 'w', encoding='utf-8').write(SH.apply(page(s, t, h, it, ids, x, root, lists), root, 'projects.html'))
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(SH.apply(index(root, lists), root, 'projects.html'))
    I.save_en()
    json.dump({str(k): v for k, v in membership().items()}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'list_membership.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    return [(s, len(ids)) for s, t, h, it, ids, x in lists]



QUICK = [('new-launch-under-rm500k', 'Under RM500K', 'Budget'), ('new-launch-under-rm800k', 'Under RM800K', 'Budget'),
         ('freehold-under-rm1-million-near-mrt-lrt', 'Freehold under RM1M near rail', 'Freehold'),
         ('condo-near-mrt-station', 'Near an MRT station', 'Transit'), ('3-bedroom-new-launch', '3-bedroom units', 'Layout'),
         ('dual-key-units', 'Dual key units', 'Layout'), ('completed-ready-to-move-in', 'Ready to move in', 'Completion'),
         ('latest-new-launch-2026', 'Latest new launches', 'New'), ('lowest-price-per-sqft-kuala-lumpur', 'Lowest psf in KL', 'Value'),
         ('condo-near-international-school', 'Near international schools', 'Lifestyle'), ('freehold-condo-kuala-lumpur', 'Freehold in KL', 'Freehold'),
         ('sea-view-waterfront-condo', 'Sea view & waterfront', 'Lifestyle')]
QUICK_CSS = (
    '.bl-section{max-width:1240px;margin:0 auto;padding:70px 5vw 40px;}'
    '.bl-box{background:linear-gradient(135deg,#1d1b4f 0%,#3b3c99 60%,#5E60CE 100%);border-radius:22px;padding:40px clamp(20px,4vw,48px);color:#fff;position:relative;overflow:hidden;box-shadow:0 24px 60px rgba(29,27,79,.25);}'
    '.bl-box:before{content:"";position:absolute;right:-80px;top:-80px;width:260px;height:260px;border-radius:50%;background:rgba(255,255,255,.06);}'
    '.bl-head{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;flex-wrap:wrap;margin-bottom:26px;position:relative;}'
    '.bl-eyebrow{font:600 11px Inter,sans-serif;letter-spacing:.28em;text-transform:uppercase;color:#c9c6ff;}'
    '.bl-title{font-size:clamp(26px,3vw,36px);margin:6px 0 6px;color:#fff;}'
    '.bl-sub{color:rgba(255,255,255,.78);font-size:14px;font-weight:500;max-width:620px;}'
    '.bl-all{display:inline-flex;align-items:center;gap:8px;background:#fff;color:#1d1b4f;border-radius:100px;padding:13px 22px;font:700 12px Inter,sans-serif;letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;transition:transform .25s;}'
    '.bl-all:hover{transform:translateY(-2px);}'
    '.bl-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;position:relative;}'
    '.bl-tile{display:flex;flex-direction:column;gap:4px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.16);border-radius:14px;padding:16px 18px;color:#fff;transition:background .25s,transform .25s,border-color .25s;}'
    '.bl-tile:hover{background:#fff;color:#1d1b4f;transform:translateY(-3px);border-color:#fff;}'
    '.bl-tile .bl-g{font:600 10px Inter,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:#c9c6ff;}'
    '.bl-tile:hover .bl-g{color:#5E60CE;}'
    '.bl-tile .bl-n{font:700 16px "Playfair Display",serif;line-height:1.3;}'
    '.bl-tile .bl-c{font:500 12.5px Inter,sans-serif;opacity:.75;}'
    '@media(max-width:1000px){.bl-grid{grid-template-columns:repeat(3,1fr);}}'
    '@media(max-width:700px){.bl-section{padding:50px 16px 30px;}.bl-box{padding:28px 18px;border-radius:18px;}.bl-grid{grid-template-columns:1fr 1fr;gap:10px;}.bl-tile{padding:13px 14px;}.bl-tile .bl-n{font-size:14.5px;}.bl-all{width:100%;justify-content:center;}}')


def link_projects_page():
    """'Best New Launch Lists' block above Browse by Tag on View Projects (idempotent)."""
    have = {l[0]: len(l[4]) for l in LISTS}
    tiles = ''.join('<a class="bl-tile" href="best/%s.html"><div class="bl-g">%s</div><div class="bl-n">%s</div><div class="bl-c">%d projects →</div></a>' % (s, E(g), E(lab), have[s])
                    for s, lab, g in QUICK if s in have)
    block = ('<!-- KN-QUICK:START --><style>%s</style><section class="bl-section" id="bestLists"><div class="bl-box"><div class="bl-head"><div>'
             '<span class="bl-eyebrow">Shortcuts · updated %d</span><h2 class="bl-title">Best New Launch Lists</h2>'
             '<p class="bl-sub">Ready-made shortlists by budget, freehold, MRT and LRT, layout and completion date. New projects join the right lists automatically.</p></div>'
             '<a class="bl-all" href="best/">View all %d lists →</a></div><div class="bl-grid">%s</div></div></section><!-- KN-QUICK:END -->\n') % (
        QUICK_CSS, YEAR, len(LISTS), tiles)
    t = open('projects.html', encoding='utf-8').read()
    t = re.sub(r'<!-- KN-QUICK:START -->.*?<!-- KN-QUICK:END -->\n?', '', t, flags=re.S)
    a = '<!-- ===================== TAG SELECTION ===================== -->'
    assert a in t
    t = t.replace(a, block + a, 1)
    open('projects.html', 'w', encoding='utf-8').write(t)
    strings = {'Best New Launch Lists': ('ui.index_t', {}), 'Shortcuts · updated %d' % YEAR: ('qp.eyebrow', {'y': YEAR}),
               E('Ready-made shortlists by budget, freehold, MRT and LRT, layout and completion date. New projects join the right lists automatically.'): ('qp.sub', {}),
               'View all %d lists →' % len(LISTS): ('tpl.viewall', {'n': len(LISTS)})}
    for n, (s, lab, g) in enumerate(QUICK):
        if s in have:
            strings[E(lab)] = ('qp.l%d' % (n + 1), {})
            strings[E(g)] = ('qp.' + g, {})
            strings['%d projects →' % have[s]] = ('tpl.nprojarrow', {'n': have[s]})
    I.merge_projects_page(strings)


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--preview':
        print(build(os.path.join(sys.argv[2], 'best'), SITE + '/'))
    else:
        print(build('best', '../'))
        link_projects_page()
