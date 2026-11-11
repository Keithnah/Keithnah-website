"""Connect Keith's market notes with the project pages.

related(note) picks up to 3 projects a note is about: the project or its developer is named,
its area is named, or the note is about the project's state. tools/build_market_notes.py shows
them under each note, and tools/build_project_pages.py shows the notes on each project page.
The project list (tools/project_index.json) is written by build_project_pages.py.
"""
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, 'project_index.json')
NOTES_PATH = os.path.join(HERE, 'market_notes.json')
# other names the news uses for an area
ALIASES = {'JB City Centre': ['Johor Bahru'], 'KL City Centre': ['Kuala Lumpur city centre', 'city centre of Kuala Lumpur'],
           'TRX': ['Tun Razak Exchange'], 'Kwasa Damansara': ['Kwasa'], 'George Town': ['Georgetown']}
LBL = {'en': 'Related projects', 'zh-CN': '相关项目', 'zh-TW': '相關項目', 'ms': 'Projek berkaitan', 'ja': '関連プロジェクト', 'ko': '관련 프로젝트'}
NOTES_LBL = {'en': "Keith's market notes", 'zh-CN': 'Keith 市场短评', 'zh-TW': 'Keith 市場短評', 'ms': 'Nota pasaran Keith', 'ja': 'Keith のマーケットノート', 'ko': 'Keith의 마켓 노트'}


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def notes():
    """Notes newest first, with the same numbering as market-notes.html (#n-<date>-<k>)."""
    if not os.path.exists(NOTES_PATH):
        return []
    ns = sorted(json.load(open(NOTES_PATH, encoding='utf-8')), key=lambda n: n['date'], reverse=True)
    for k, n in enumerate(ns):
        n['_id'] = 'n-%s-%d' % (n['date'], k)
    return ns


def projects():
    try:
        return json.load(open(INDEX, encoding='utf-8'))
    except (OSError, ValueError):
        return []


def _has(text, phrase):
    return re.search(r'(?<![A-Za-z])%s(?![A-Za-z])' % re.escape(phrase), text, re.I) is not None


def related(note, projs, n=3):
    en = lambda d: d.get('en', '') if isinstance(d, dict) else (d or '')
    text = ' '.join([en(note.get('title')), en(note.get('body')), en(note.get('take'))])
    flat = norm(text)
    region = en(note.get('area'))
    scored = []
    for p in projs:
        s = 0
        if _has(text, p['name']):
            s += 10
        dev = norm(re.sub(r'\b(sdn|bhd|berhad|group|holdings|properties|property|development|developments|land)\b', '', p.get('dev', ''), flags=re.I))
        if len(dev) >= 5 and dev in flat:
            s += 4
        if any(_has(text, a) for a in [p['area']] + ALIASES.get(p['area'], [])):
            s += 3
        if region and region == p['state']:
            s += 1
        if s >= (1 if region != 'Malaysia' else 4):
            # same score: a different but fixed choice for each note, so links spread across projects
            tie = hashlib.md5((en(note.get('title')) + p['slug']).encode()).hexdigest()
            scored.append((-s, tie, p))
    scored.sort(key=lambda x: (x[0], x[1]))
    return sorted([x[2] for x in scored[:n]], key=lambda p: p['name'].lower())   # shown A–Z
