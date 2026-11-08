"""Find map positions for projects (OpenStreetMap Nominatim) and cache them.

Writes tools/project_coords.json: {project name: [lat, lng, precision]} where
precision is 'project' (the building or its street address) or 'area' (the
area centre, used when the project itself is not on the map yet). Only projects
missing from the file are looked up, so it is safe to run again after adding
projects. Edit the file by hand to correct a position (set precision 'manual').
"""
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'project_coords.json')
UA = 'keithnah-website-map-builder/1.0'


def search(q):
    url = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode({'q': q, 'format': 'json', 'limit': 1, 'countrycodes': 'my'})
    time.sleep(1.1)
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30))
    except Exception as e:
        print('  ! %s: %s' % (q, e), file=sys.stderr)
        return None
    return (float(r[0]['lat']), float(r[0]['lon'])) if r else None


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def main():
    sys.path.insert(0, HERE)
    import build_area_pages as A
    coords = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}
    centres = {}
    for i, p in enumerate(A.P):
        name = p['name']
        if name in coords:
            continue
        state, area = A.PLACES[i]
        key = (area, state)
        if key not in centres:
            centres[key] = search('%s, %s, Malaysia' % (area, state)) or search('%s, Malaysia' % state)
        centre = centres[key]
        short = re.sub(r'\s*[@(].*$', '', name).strip()
        found = None
        for q in ['%s, %s' % (name, area), '%s, %s' % (short, area), p.get('loc') or '']:
            if not q:
                continue
            g = search(q + ', Malaysia')
            if g and centre and km(g, centre) <= 15:
                found = (g, 'project')
                break
        if not found and centre:
            found = (centre, 'area')
        if found:
            coords[name] = [round(found[0][0], 6), round(found[0][1], 6), found[1]]
            print('%-45s %s %s' % (name, found[1], coords[name][:2]))
            json.dump(coords, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('%d projects have map positions' % len(coords))


if __name__ == '__main__':
    main()
