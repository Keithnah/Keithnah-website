"""Merge project content translations into i18n-projects-<lang>.js.

The View Projects pop-up, the compare page and the project pages all read
project translations from i18n-projects-<lang>.js (English text -> translation).
This adds:
  * tools/i18n/proj_tr/*.json: {id: [zh-CN, ms, ja, ko]} for the English texts in
    tools/i18n/proj_en.json (zh-TW is converted from zh-CN when OpenCC is available,
    otherwise the zh-CN text is used);
  * unit details (sizes, bedrooms, tenure, completion, prices) translated by the
    word rules in tools/i18n_pages.py when no translation exists yet;
and removes entries for texts that must never appear (guaranteed rental returns).
Place names and project names stay in English.

Run from the repository root (tools/build_all.py runs it):
    python3 tools/merge_project_translations.py
"""
import glob
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
ORDER = ['zh-CN', 'ms', 'ja', 'ko']
BANNED = re.compile(r'GRR|MRR|[Gg]uaranteed [Rr]ental|[Rr]ental [Rr]eturn|Mana Mana|保证租金|保證租金')


def to_tw(s, _cc=[]):
    if not _cc:
        try:
            import opencc
            _cc.append(opencc.OpenCC('s2tw').convert)
        except ImportError:
            _cc.append(lambda x: x)
    return _cc[0](s)


def load_js(l):
    p = os.path.join(ROOT, 'i18n-projects-%s.js' % l)
    t = open(p, encoding='utf-8').read()
    m = 'window.KN_TR["%s"]=' % l
    a = t.index(m) + len(m)
    d, n = json.JSONDecoder().raw_decode(t[a:])
    return p, t, a, n, d


def main():
    import i18n_pages as I
    from add_projects import js_value
    en = json.load(open(os.path.join(HERE, 'i18n', 'proj_en.json'), encoding='utf-8'))
    tr = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'i18n', 'proj_tr', '*.json'))):
        tr.update(json.load(open(f, encoding='utf-8')))
    s = open(os.path.join(ROOT, 'projects.html'), encoding='utf-8').read()
    D = js_value(s, 'const PROJECT_DETAILS = ')[0]
    data = set()
    for p in D:
        data.update(v for k in ('size', 'rooms', 'tenure', 'completion', 'price', 'status') for v in [p.get(k)] if v)
        data.update(v for l in (p.get('layouts') or []) for v in (l.get('size'), l.get('rooms')) if v)
    added = {}
    for l in I.LANGS:
        p, t, a, n, d = load_js(l)
        before = dict(d)
        for k in [k for k, v in d.items() if BANNED.search(k) or BANNED.search(v)]:
            del d[k]
        for tid, row in tr.items():
            if tid not in en:
                continue
            v = row[ORDER.index('zh-CN')] if l == 'zh-TW' else row[ORDER.index(l)]
            if l == 'zh-TW':
                v = to_tw(v)
            if v and v != en[tid]:
                d[html.escape(en[tid], quote=False)] = html.escape(v, quote=False)
        for x in data:
            k = html.escape(x, quote=False)
            if k in d or x in d:
                continue
            v = I.data(x, l)
            if v:
                d[k] = html.escape(v, quote=False)
        if d != before:
            open(p, 'w', encoding='utf-8').write(t[:a] + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + t[a + n:])
        added[l] = len(d) - len(before)
    print('project translations merged:', ', '.join('%s %+d' % kv for kv in added.items()))


if __name__ == '__main__':
    main()
