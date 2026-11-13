"""Remove a project from the site.

Takes the project out of projects.html (PROJECT_DETAILS, PS_META, KN_TAGS, its card,
the nearby lists of other projects) and compare.html (PROJECTS and its card), renumbers
every later project, lowers the "N active and completed projects" count (also in
i18n-projects-*.js), drops it from tools/new_projects/places.json and
tools/project_coords.json, and deletes its generated pages (property/, vs/, language
copies, share images). The URLs are added to .htaccess as "410 Gone" so Google drops them.

Run from the repository root, then rebuild:
    python3 tools/externalize.py in
    python3 tools/remove_project.py "Project Name"
    python3 tools/build_all.py
"""
import glob
import json
import os
import re
import subprocess
import sys

from add_projects import js_value

LANGS = ['zh', 'zh-tw', 'ms', 'ja', 'ko']


def div_block(s, start):
    """End of the <div> that opens at start (matching closing tag)."""
    depth = 0
    for m in re.finditer(r'<div\b|</div>', s[start:]):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0:
            return start + m.end()
    raise ValueError('unclosed div')


def renumber(s, k, pat):
    """Lower every index n > k by one in matches of pat (one group: the number)."""
    return re.sub(pat, lambda m: m.group(0).replace(m.group(1), str(int(m.group(1)) - 1)) if int(m.group(1)) > k else m.group(0), s)


def drop_card(s, cls, k):
    m = re.search(r'\n?[ \t]*<div class="%s"[^>]*data-idx="%d"' % (cls, k), s)
    assert m, '%s card %d not found' % (cls, k)
    st = s.index('<div', m.start())
    return s[:m.start()] + s[div_block(s, st):]


def main(name):
    s = open('projects.html', encoding='utf-8').read()
    assert name in [p['name'] for p in js_value(open('compare.html', encoding='utf-8').read(), 'const PROJECTS = ')[0]], 'not in compare.html'
    assert 'const PROJECT_DETAILS = ' in s, 'run tools/externalize.py in first'
    D, d0, d1 = js_value(s, 'const PROJECT_DETAILS = ')
    hits = [i for i, p in enumerate(D) if p['name'] == name]
    assert len(hits) == 1, 'project not found: %r' % name
    k = hits[0]
    T = js_value(s, 'var KN_TAGS = ')[0]
    slug = re.sub(r'[^a-z0-9]+', '-', T[k][0].lower().replace('&', ' and ').replace("'", '').replace('’', '')).strip('-')
    total = len(D) - 1

    # 1) PROJECT_DETAILS (+ nearby lists)
    del D[k]
    for p in D:
        if 'nearby' in p:
            p['nearby'] = [n - 1 if n > k else n for n in p['nearby'] if n != k]
    s = s[:d0] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + s[d1:]
    # 2) PS_META
    a = s.index('var PS_META=') + len('var PS_META=')
    e = s.index('];', a) + 1
    meta = json.loads(s[a:e])
    del meta[k]
    s = s[:a] + json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + s[e:]
    # 3) KN_TAGS
    T, t0, t1 = js_value(s, 'var KN_TAGS = ')
    del T[k]
    s = s[:t0] + json.dumps(T, ensure_ascii=False) + s[t1:]
    # 4) card + renumber later cards
    s = drop_card(s, 'proj-card', k)
    s = renumber(s, k, r'data-idx="(\d+)"')
    s = renumber(s, k, r'openDetailModal\((\d+)\)')
    s = re.sub(r'<p>\d+ active and completed projects', '<p>%d active and completed projects' % total, s, count=1)
    open('projects.html', 'w', encoding='utf-8').write(s)

    # 5) compare.html
    c = open('compare.html', encoding='utf-8').read()
    C, c0, c1 = js_value(c, 'const PROJECTS = ')
    kc = [i for i, p in enumerate(C) if p['name'] == name][0]  # compare.html has its own (A-Z) order
    del C[kc]
    c = c[:c0] + json.dumps(C, ensure_ascii=False, separators=(',', ':')) + c[c1:]
    c = drop_card(c, 'cmp-card', kc)
    c = renumber(c, kc, r'data-idx="(\d+)"')
    c = renumber(c, kc, r'toggleSelect\((\d+)\)')
    open('compare.html', 'w', encoding='utf-8').write(c)

    # 6) project count in the translations
    for f in glob.glob('i18n-projects-*.js'):
        t = open(f, encoding='utf-8').read()
        i = t.find('"%d active and completed projects' % (total + 1))
        if i < 0:
            continue
        ke = t.index('":"', i)
        v, n = json.JSONDecoder().raw_decode(t[ke + 2:])
        raw = t[ke + 2:ke + 2 + n]
        t = t[:i] + '"%d' % total + t[i + 1 + len(str(total + 1)):ke + 2] + raw.replace(str(total + 1), str(total), 1) + t[ke + 2 + n:]
        open(f, 'w', encoding='utf-8').write(t)

    # 7) tools data keyed by name
    for f, indent in [('tools/new_projects/places.json', 1), ('tools/project_coords.json', None)]:
        if os.path.exists(f):
            raw = open(f, encoding='utf-8').read()
            d = json.loads(raw)
            if d.pop(name, None) is not None:
                ind = 1 if raw.startswith('{\n "') else (2 if raw.startswith('{\n  "') else indent)
                open(f, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=ind) + ('\n' if raw.endswith('\n') else ''))

    # 8) generated pages
    gone = ['property/%s.html' % slug] + [p for p in glob.glob('vs/*.html') if re.search(r'(^|/|-vs-)%s(-vs-|\.html$)' % re.escape(slug), p)]
    files = []
    for g in gone:
        files += [g] + ['%s/%s' % (l, g) for l in LANGS]
    files += glob.glob('images/og/*%s*' % slug)
    files = [f for f in files if os.path.exists(f)]
    if files:
        subprocess.run(['git', 'rm', '-q', '--'] + files, check=False)
        for f in files:
            if os.path.exists(f):
                os.remove(f)

    # 9) tell search engines the pages are gone for good
    ht = open('.htaccess', encoding='utf-8').read()
    lines = []
    for g in gone:
        for prefix in [''] + [l + '/' for l in LANGS]:
            rule = 'Redirect gone /%s%s' % (prefix, g)
            if rule not in ht:
                lines.append(rule)
    if lines:
        mark = '# Removed projects (410 Gone)'
        if mark not in ht:
            ht = ht.rstrip('\n') + '\n\n' + mark + '\n'
        ht = ht.replace(mark + '\n', mark + '\n' + '\n'.join(lines) + '\n', 1)
        open('.htaccess', 'w', encoding='utf-8').write(ht)
    print('Removed %s (index %d, slug %s); %d projects left; %d files deleted; %d URLs marked 410' % (name, k, slug, total, len(files), len(lines)))


if __name__ == '__main__':
    main(sys.argv[1])
