"""Add new projects to the site from a JSON file in tools/new_projects/.

Adds each project (if its name is not already on the site) to projects.html
(PROJECT_DETAILS, PS_META, KN_TAGS, a card at the end of the grid, the
developer list) and compare.html (PROJECTS, the area buttons), and records
its state and area in tools/new_projects/places.json for tools/update_areas.py.

Then run, from the repository root:
    python3 tools/build_all.py
That rebuilds tags, area guides, the best-of lists (new projects join every
list whose rule they match), project pages, news, sitemap and llms.txt.
New project texts also need translations: add them to tools/i18n/proj_en.json and a
file in tools/i18n/proj_tr/ ({id: [zh-CN, ms, ja, ko]}); build_all merges them.
The site's languages are English, 简体中文, 繁體中文, Bahasa Malaysia, 日本語 and 한국어.

Usage: python3 tools/add_projects.py tools/new_projects/<file>.json
"""
import html
import json
import os
import re
import sys
from urllib.parse import quote_plus

E = lambda s: html.escape(s, quote=True)
STATUS_CLASS = {'Under Construction': 'status-construction', 'Coming Soon': 'status-comingsoon', 'New Launch': 'status-comingsoon', 'Completed': 'status-completed'}
TYPE_CLASS = {'Residential': 'type-residential', 'Serviced Apartment': 'type-serviced', 'Commercial Suites': 'type-commercial'}
DETAIL_KEYS = ['name', 'tag', 'price', 'tenure', 'size', 'rooms', 'completion', 'status', 'loc', 'overview', 'points', 'amenities',
               'loc_text', 'nearby', 'selling_points', 'facilities', 'layouts', 'buyer_fit', 'details_extra']


def js_value(src, marker):
    i = src.index(marker) + len(marker)
    while src[i] == ' ':
        i += 1
    val, n = json.JSONDecoder().raw_decode(src[i:])
    return val, i, i + n


def wa(name):
    return 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0' % quote_plus(
        '(KNRE) Hi Keith, I would like to know more about "%s".' % name)


def compare_cards(c, todo, index):
    """Card markup in the compare page's project picker, copied from an existing card."""
    tpl = re.search(r'  <div class="cmp-card" data-idx="48".*?\n  </div>\n', c, re.S).group(0)
    out = ''
    for p in todo:
        k = index[p['name']]
        x = tpl.replace('data-idx="48" onclick="toggleSelect(48)"', 'data-idx="%d" onclick="toggleSelect(%d)"' % (k, k))
        x = re.sub(r'data-search="[^"]*"', 'data-search="%s"' % E(('%s %s %s' % (p['name'], p['tag'], p['area'])).lower()), x)
        x = re.sub(r'\s*<img class="cmp-card-photo"[^>]*>', '', x, count=1)
        x = re.sub(r'<span class="cmp-card-status [^"]+">[^<]*</span>', '<span class="cmp-card-status %s">%s</span>' % (STATUS_CLASS[p['status']], E(p['status'])), x)
        x = re.sub(r'<span class="cmp-card-tag">[^<]*</span>', '<span class="cmp-card-tag">%s</span>' % E(p['tag']), x)
        x = re.sub(r'<h4>[^<]*</h4>', '<h4>%s</h4>' % E(p['name']), x)
        x = re.sub(r'<p class="cmp-card-loc">[^<]*</p>', '<p class="cmp-card-loc">%s</p>' % E(p['loc']), x)
        x = re.sub(r'(<div class="cmp-card-foot">\s*<strong>)[^<]*(</strong>)', lambda m_: m_.group(1) + E(p['price_short']) + m_.group(2), x)
        assert 'Tagbay' not in x
        out += x
    end = re.search(r'  </div>\n\s*<div class="cmp-empty" id="cmpEmpty">', c).start()
    return c[:end] + out + c[end:]


def main(spec_path):
    import no_klcc
    new = json.loads(no_klcc.clean(open(spec_path, encoding='utf-8').read()))
    s = open('projects.html', encoding='utf-8').read()
    D, d0, d1 = js_value(s, 'const PROJECT_DETAILS = ')
    names = {p['name'] for p in D}
    todo = [p for p in new if p['name'] not in names]
    if not todo:
        print('Nothing to add: every project is already on the site')
        return
    start = len(D)
    index = {p['name']: start + k for k, p in enumerate(todo)}

    # nearby: other new projects in the same state first, then others in the same group
    for p in todo:
        same = [index[q['name']] for q in todo if q is not p and q['state'] == p['state']]
        others = [index[q['name']] for q in todo if q is not p and q['state'] != p['state']]
        p['nearby'] = (same + others)[:3]
        p.setdefault('facilities', [])

    # 1) PROJECT_DETAILS
    D += [{k: p[k] for k in DETAIL_KEYS} for p in todo]
    s = s[:d0] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + s[d1:]

    # 2) PS_META (completion years, completed?, developer group)
    a = s.index('var PS_META=') + len('var PS_META=')
    e = s.index('];', a) + 1
    meta = json.loads(s[a:e]) + [{'y': p['years'], 'c': p['status'] == 'Completed', 'd': p['developer_group']} for p in todo]
    s = s[:a] + json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + s[e:]

    # 3) KN_TAGS (the base tags; tools/update_tags.py adds landmark and feature tags)
    T, t0, t1 = js_value(s, 'var KN_TAGS = ')
    T += [p['tags'] for p in todo]
    s = s[:t0] + json.dumps(T, ensure_ascii=False) + s[t1:]

    # 4) Developer list in the search form
    m = re.search(r'(<select id="psDev">)(.*?)(</select>)', s, re.S)
    devs = re.findall(r'<option value="([^"]+)">', m.group(2))
    devs = sorted({html.unescape(x) for x in devs if x != 'All'} | {p['developer_group'] for p in todo if p['developer_group']}, key=str.lower)
    s = s[:m.start()] + m.group(1) + '<option value="All">Any developer</option>' + ''.join(
        '<option value="%s">%s</option>' % (E(x), E(x)) for x in devs) + m.group(3) + s[m.end():]

    # 5) Cards: copy an existing card's markup
    tpl = re.search(r'  <div class="proj-card"[^>]*data-idx="48".*?\n  </div>\n', s, re.S).group(0)
    assert 'Tagbay Suites' in tpl, 'template card moved'
    cards = ''
    for p in todo:
        k = index[p['name']]
        c = tpl
        c = re.sub(r'<div class="proj-card"[^>]*>', '<div class="proj-card" data-tag="%s" data-idx="%d" onclick="openDetailModal(%d)">' % (E(p['tag']), k, k), c, count=1)
        c = re.sub(r'\s*<img class="proj-photo"[^>]*>', '', c, count=1)
        c = re.sub(r'<span class="proj-badge badge-status [^"]+">[^<]*</span>', '<span class="proj-badge badge-status %s">%s</span>' % (STATUS_CLASS[p['status']], E(p['status'])), c)
        c = re.sub(r'<span class="proj-badge badge-type [^"]+">[^<]*</span>', '<span class="proj-badge badge-type %s">%s</span>' % (TYPE_CLASS[p['type']], E(p['type'])), c)
        c = re.sub(r'href="https://api\.whatsapp\.com/send/\?[^"]*"', 'href="%s"' % wa(p['name']), c)
        c = re.sub(r'<span class="proj-tag">[^<]*</span>', '<span class="proj-tag">%s</span>' % E(p['area']), c)
        slug = re.sub(r'[^a-z0-9]+', '-', p['name'].lower()).strip('-')
        c = re.sub(r'<h3>.*?</h3>', '<h3><a class="proj-page-link" href="property/%s.html" onclick="event.stopPropagation()">%s</a></h3>' % (slug, E(p['name'])), c, count=1)
        c = re.sub(r'<p class="proj-loc">[^<]*</p>', '<p class="proj-loc">%s</p>' % E(p['loc']), c)
        c = re.sub(r'<div class="proj-tags">.*?</div>', '<div class="proj-tags"></div>', c, count=1, flags=re.S)
        for label, val in [('Size', p['size_short']), ('Rooms', p['rooms_short']), ('Tenure', p['tenure']), ('Completion', p['completion_short'])]:
            c = re.sub(r'(<small>%s</small><strong>)[^<]*(</strong>)' % label, lambda m_, v=val: m_.group(1) + E(v) + m_.group(2), c)
        c = re.sub(r'(<strong class="proj-price">)[^<]*(</strong>)', lambda m_: m_.group(1) + E(p['price_short']) + m_.group(2), c)
        c = c.replace('data-idx="48"', 'data-idx="%d"' % k).replace('openDetailModal(48)', 'openDetailModal(%d)' % k)
        assert 'Tagbay' not in c, c[:300]
        cards += c
    # after the last card, inside the grid: find the last card and its matching closing tag
    st = s.rindex('<div class="proj-card"', s.index('id="projGrid"'), s.index('id="projEmpty"'))
    depth, pos = 0, st
    for m_ in re.finditer(r'<div\b|</div>', s[st:]):
        depth += 1 if m_.group(0) == '<div' else -1
        if depth == 0:
            pos = st + m_.end()
            break
    end = pos
    s = s[:end] + '\n' + cards.rstrip('\n') + s[end:]
    # hero line with the project count
    s = re.sub(r'<p>\d+ active and completed projects', '<p>%d active and completed projects' % len(D), s, count=1)  # update its translations in i18n-projects-*.js too
    open('projects.html', 'w', encoding='utf-8').write(s)

    # 6) compare.html
    c = open('compare.html', encoding='utf-8').read()
    C, c0, c1 = js_value(c, 'const PROJECTS = ')
    icon = C[48]['icon']
    C += [{'name': p['name'], 'tag': p['tag'], 'type': p['type'], 'tenure': p['tenure'], 'status': p['status'], 'completion': p['completion_short'],
           'price': p['price_short'], 'size': p['size_short'], 'rooms': p['rooms_short'], 'loc': p['loc'], 'icon': icon, 'grad': '#1e1a20,#3a2e3f'} for p in todo]
    c = c[:c0] + json.dumps(C, ensure_ascii=False, separators=(',', ':')) + c[c1:]
    c = compare_cards(c, todo, index)
    counts = {}
    for x in C:
        counts[x.get('tag')] = counts.get(x.get('tag'), 0) + 1
    for tag in sorted({p['tag'] for p in todo}):
        btn = '<div class="cmp-filter-btn" data-tag="%s">' % E(tag)
        olds = list(re.finditer(r'\n      <div class="cmp-filter-btn" data-tag="[^"]+">[^<]*</div>', c))
        if btn not in c and olds:  # older compare pages only; area filters are now built by update_areas.py
            last = olds[-1]
            c = c[:last.end()] + '\n      %s%s (%d)</div>' % (btn, E(tag), counts[tag]) + c[last.end():]
    c = re.sub(r'(<div class="cmp-filter-btn" data-tag="([^"]+)">)([^<(]*)\(\d+\)(</div>)',
               lambda m_: '%s%s(%d)%s' % (m_.group(1), m_.group(3), counts.get(html.unescape(m_.group(2)), 0), m_.group(4)), c)
    open('compare.html', 'w', encoding='utf-8').write(c)

    # 7) state and area for tools/update_areas.py
    pf = os.path.join('tools', 'new_projects', 'places.json')
    places = json.load(open(pf, encoding='utf-8')) if os.path.exists(pf) else {}
    for p in todo:
        places[p['name']] = [p['state'], p['area']]
    json.dump(places, open(pf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('Added %d projects (now %d): %s' % (len(todo), len(D), ', '.join(p['name'] for p in todo)))


if __name__ == '__main__':
    main(sys.argv[1])
