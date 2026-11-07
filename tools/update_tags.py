"""Add landmark tags (Merdeka 118, KLCC, Pavilion KL, TRX, KL Tower ...) to projects.

A project only gets a landmark tag when its own data (location, location
text, amenities, overview or highlights) mentions that landmark, so every
tag stays true. Rewrites the tags inside projects.html: KN_TAGS, the
card tag pills and the Tag Selection list. Then run
tools/build_project_pages.py to refresh the project pages.

Run from the repository root:
    python3 tools/update_tags.py
    python3 tools/build_project_pages.py
Safe to run again: landmark tags are recomputed, not added twice.
"""
import html
import json
import re

# landmark: (pattern found in the project's text, tags people search for)
LANDMARKS = [
    ('Merdeka 118', r'merdeka ?118|menara merdeka|pnb ?118',
     ['condo near Merdeka 118', 'Menara Merdeka 118 condo', '默迪卡118附近公寓']),
    ('KLCC', r'\bklcc\b|kl city centre park|suria kl city centre|petronas|twin towers',
     ['condo near KL City Centre', 'condo near Petronas Twin Towers', '双子塔附近公寓']),
    ('Pavilion KL', r'pavilion (kuala lumpur|kl\b|bukit bintang|mall|shopping)|pavilion elite',
     ['condo near Pavilion KL', 'Pavilion Bukit Bintang condo', '柏威年附近公寓']),
    ('TRX', r'\btrx\b|tun razak exchange',
     ['condo near TRX', 'TRX condo for sale']),
    ('Exchange 106', r'exchange 106',
     ['condo near The Exchange 106']),
    ('KL Tower', r'kl tower|menara kl\b|menara kuala lumpur',
     ['condo near KL Tower', 'Menara KL condo', '吉隆坡塔附近公寓']),
    ('Bukit Bintang', r'bukit bintang',
     ['condo near Bukit Bintang']),
    ('KL Sentral', r'kl sentral',
     ['condo near KL Sentral']),
    ('Mid Valley KL', r'mid ?valley(?! ?southkey)',
     ['condo near Mid Valley Megamall']),
    ('Mid Valley Southkey', r'mid ?valley ?southkey',
     ['condo near Mid Valley Southkey']),
    ('Bukit Jalil Stadium', r'national stadium|axiata arena|bukit jalil stadium',
     ['condo near Bukit Jalil National Stadium']),
    ('Pavilion Bukit Jalil', r'pavilion bukit jalil',
     ['condo near Pavilion Bukit Jalil']),
    ('Bangsar South', r'bangsar south',
     ['condo near Bangsar South']),
    ('Gurney', r'gurney',
     ['condo near Gurney Drive']),
    ('Penang Bridge', r'penang bridge|second bridge|sultan abdul halim',
     ['condo near Penang Bridge']),
    ('RTS Link', r'\brts\b|bukit chagar',
     ['condo near RTS Link JB']),
    ('JB CIQ', r'\bciq\b',
     ['condo near JB CIQ']),
]
ALL_LM_TAGS = {t for _, _, tags in LANDMARKS for t in tags}

# Feature tags, worked out from each project's own data so every tag stays true.
# tag -> group shown on the project page
TRANSIT = [
    (r'\bLRT\b', ['condo near LRT station', '近LRT公寓']),
    (r'\bMRT\b', ['condo near MRT station', '近MRT公寓']),
    (r'\bKTM\b', ['condo near KTM station']),
    (r'\bmonorail\b', ['condo near KL Monorail']),
    (r'\bBRT\b', ['condo near BRT station']),
]
REGIONS = {'KL': 'Kuala Lumpur', 'Selangor': 'Selangor', 'Penang': 'Penang', 'Johor': 'Johor', 'Sabah': 'Sabah', 'Terengganu': 'Terengganu', 'Kelantan': 'Kelantan'}
GROUP = {}


def price_rm(s):
    s = (s or '').replace(',', '')
    m = re.search(r'RM\s*([\d.]+)\s*(k|m|mil|million)?\b', s, re.I)
    if not m:
        return None
    v = float(m.group(1))
    u = (m.group(2) or '').lower()
    return v * 1000 if u == 'k' else v * 1e6 if u in ('m', 'mil', 'million') else v


def features(p, tg):
    out = []

    def add(group, *tags):
        for x in tags:
            GROUP[x] = group
            out.append(x)
    text = ' '.join([p.get('loc', ''), p.get('loc_text', ''), p.get('overview', '')]
                    + (p.get('amenities') or []) + (p.get('selling_points') or []))
    for pat, tags in TRANSIT:
        if re.search(pat, text, re.I):
            add('Transit', *tags)
    region = next((REGIONS[m.group(1)] for x in tg for m in [re.match(r'new launch condo (KL|Selangor|Penang|Johor|Sabah|Terengganu|Kelantan)$', x)] if m), None)
    if region:
        add('Location & landmarks', '%s property' % region)
    tenure = (p.get('tenure') or '').lower()
    if tenure.startswith('freehold'):
        add('Tenure & status', 'freehold property', '永久地契房产')
    elif tenure.startswith('leasehold'):
        add('Tenure & status', 'leasehold property', '租赁地契房产')
        if region:
            add('Tenure & status', 'leasehold condo %s' % ('KL' if region == 'Kuala Lumpur' else region))
    status = p.get('status') or ''
    if status in ('Coming Soon', 'New Launch'):
        add('Tenure & status', 'latest new launch 2026', '2026最新楼盘')
    elif status == 'Under Construction':
        add('Tenure & status', 'under construction condo')
    elif status == 'Completed':
        add('Tenure & status', 'completed condo, ready to move in', '现房')
    y = re.search(r'\b(20[2-4]\d)\b', p.get('completion') or '')
    if y and status != 'Completed':
        add('Tenure & status', 'completion %s' % y.group(1))
    v = price_rm(p.get('price'))
    if v:
        add('Price & unit type', 'condo under RM500K' if v < 500000 else 'condo RM500K to RM1M' if v < 1000000 else 'condo above RM1M')
    rooms = p.get('rooms') or ''
    if re.search(r'dual ?key', rooms + ' ' + text, re.I):
        add('Price & unit type', 'dual key unit')
    if re.search(r'studio', rooms, re.I):
        add('Price & unit type', 'studio unit')
    return out


FEATURE_TAGS = None  # filled below
TAG_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.6 13.4l-7.2 7.2a2 2 0 01-2.8 0L3 13V3h10l7.6 7.6a2 2 0 010 2.8z"/><circle cx="7.5" cy="7.5" r="1.5"/></svg>'
E = lambda s: html.escape(s, quote=True)

src = open('projects.html', encoding='utf-8').read()


def js_json(marker):
    i = src.index(marker) + len(marker)
    return json.JSONDecoder().raw_decode(src[i:])[0], i


P, _ = js_json('const PROJECT_DETAILS = ')
TAGS, ti = js_json('var KN_TAGS = ')

try:
    OLD_FEATURES = set(json.load(open('tools/tag_groups.json', encoding='utf-8')))
except (OSError, ValueError):
    OLD_FEATURES = set()
OLD_FEATURES -= {x for tg in TAGS for x in tg[:1]}  # never drop a project name
_m = src.index('var PS_META=') + len('var PS_META=')
META = json.loads(src[_m:src.index('];', _m) + 1])


def dev_of(p):
    return (p.get('details_extra') or {}).get('Developer') or META[P.index(p)].get('d', '')


new = []
for p, tg in zip(P, TAGS):
    base = [t for t in tg if t not in ALL_LM_TAGS and t not in OLD_FEATURES]
    text = ' '.join([p.get('loc', ''), p.get('loc_text', ''), p.get('overview', '')]
                    + (p.get('amenities') or []) + (p.get('selling_points') or [])).lower()
    add = [t for lm, pat, tags in LANDMARKS if re.search(pat, text) for t in tags
           if not (lm == 'KLCC' and 'EXSIM' in (dev_of(p) or ''))]  # EXSIM bans the word "KLCC" in marketing
    for x in add:
        GROUP[x] = 'Location & landmarks'
    add += features(p, base)
    seen = set()
    new.append([t for t in base + add if not (t.lower() in seen or seen.add(t.lower()))])

# 1) KN_TAGS
old_len = len(json.dumps(TAGS, ensure_ascii=False))
assert src[ti:ti + old_len] == json.dumps(TAGS, ensure_ascii=False), 'KN_TAGS layout changed'
src = src[:ti] + json.dumps(new, ensure_ascii=False) + src[ti + old_len:]

# 2) Card pills: first two tags that are not the project name, then +N
def card_tags(k):
    tg = new[k]
    name = tg[0].lower()
    pick = [x for x in tg if not x.lower().startswith(name)][:2]
    rest = len(tg) - len(pick)
    s = ''.join('<span class="ptag" data-t="%s">%s%s</span>' % (E(x), TAG_SVG, E(x)) for x in pick)
    if rest > 0:
        s += '<span class="ptag-more" data-idx="%d">+%d</span>' % (k, rest)
    return '<div class="proj-tags">%s</div>' % s


def card(m):
    k = int(m.group(1))
    return re.sub(r'<div class="proj-tags">.*?</div>', lambda _: card_tags(k), m.group(0), count=1, flags=re.S)


src, n = re.subn(r'data-idx="(\d+)" onclick="openDetailModal\(\1\)">.*?<div class="proj-tags">.*?</div>', card, src, flags=re.S)
assert n == len(P), n

# 3) Tag Selection list, most used first
counts = {}
for tg in new:
    for t in tg:
        counts[t] = counts.get(t, 0) + 1
order = sorted(counts, key=lambda t: (-counts[t], t.lower()))
opts = ''.join('<label class="ts-opt"><input type="checkbox" value="%s"><span>%s</span><em>(%d)</em></label>' % (E(t), E(t), counts[t]) for t in order)
src, n = re.subn(r'(<div class="ts-list" id="tsList">).*?(</div>)', lambda m: m.group(1) + opts + m.group(2), src, count=1, flags=re.S)
assert n == 1

open('projects.html', 'w', encoding='utf-8').write(src)
json.dump(dict(sorted(GROUP.items())), open('tools/tag_groups.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
lm = sorted({t for t in order if t in ALL_LM_TAGS}, key=lambda t: -counts[t])
print('tags: %d unique (%d landmark tags); per project %d-%d' % (len(order), len(lm), min(map(len, new)), max(map(len, new))))
print('landmark tags:', ', '.join('%s (%d)' % (t, counts[t]) for t in lm))
