"""Add Keith's new YouTube videos to the project pages (tools/project_videos.json).

Reads the latest videos on https://www.youtube.com/@KeithNahRealEstate/videos and matches each title
to a project on the site by the name in its 【...】 brackets (e.g. 【PAVILION SQUARE】 -> Pavilion Square).
New matches are added to tools/project_videos.json; then tools/fetch_video_meta.py saves their titles and
dates, and the next build shows them in the project page's Video section (and its menu item).
Videos that match no project, or more than one, are only listed, never guessed.

    python3 tools/sync_youtube_videos.py          (prints what it added; exit code 0)
"""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
URL = 'https://www.youtube.com/@KeithNahRealEstate/videos'
VF = os.path.join(HERE, 'project_videos.json')


def norm(s):
    return re.sub(r'[^a-z0-9]+', ' ', (s or '').lower().replace('&', ' and ')).strip()


def channel_videos():
    page = urllib.request.urlopen(urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-US,en;q=0.9'}), timeout=30).read().decode('utf-8', 'ignore')
    data = json.loads(re.search(r'var ytInitialData = (\{.*?\});</script>', page, re.S).group(1))
    out = []

    def walk(o):
        if isinstance(o, dict):
            l = o.get('lockupViewModel')
            if l and l.get('contentId'):
                try:
                    out.append((l['contentId'], l['metadata']['lockupMetadataViewModel']['title']['content']))
                except (KeyError, TypeError):
                    pass
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(data)
    seen, res = set(), []
    for v, t in out:
        if v not in seen:
            seen.add(v)
            res.append((v, t))
    return res


def project_names():
    src = open('projects.html', encoding='utf-8').read()
    if 'const PROJECT_DETAILS = ' not in src:
        subprocess.run([sys.executable, os.path.join(HERE, 'externalize.py'), 'in'], check=True, capture_output=True)
        src = open('projects.html', encoding='utf-8').read()
        subprocess.run([sys.executable, os.path.join(HERE, 'externalize.py'), 'out'], check=True, capture_output=True)
    i = src.index('const PROJECT_DETAILS = ') + len('const PROJECT_DETAILS = ')
    return [p['name'] for p in json.JSONDecoder().raw_decode(src[i:])[0]]


def match(title, names):
    keys = [norm(k) for k in re.findall(r'【([^】]+)】', title)]
    hits = set()
    for k in keys:
        if len(k) < 3:
            continue
        for n in names:
            nn = norm(re.sub(r'\s*[@(].*$', '', n))       # "Branniganz Suites @ Bukit Bintang" -> "branniganz suites"
            words = [w for w in nn.split() if w not in ('the', 'residence', 'residences', 'suites', 'suite')]
            if nn and (nn in k or k in nn or (words and all(w in k.split() for w in words))):
                hits.add(n)
    return sorted(hits)


if __name__ == '__main__':
    videos = channel_videos()
    names = project_names()
    V = json.load(open(VF, encoding='utf-8'))
    known = {v for vs in V.values() for v in vs}
    added, unmatched = [], []
    for vid, title in videos:
        if vid in known:
            continue
        hits = match(title, names)
        if len(hits) == 1:
            V.setdefault(hits[0], []).append(vid)
            added.append((hits[0], vid, title))
        else:
            unmatched.append((vid, title, hits))
    if added:
        json.dump(V, open(VF, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        subprocess.run([sys.executable, os.path.join(HERE, 'fetch_video_meta.py')])
    # can each video play on the site? (the owner can turn off "Allow embedding" in YouTube Studio)
    MF = os.path.join(HERE, 'video_meta.json')
    meta = json.load(open(MF, encoding='utf-8')) if os.path.exists(MF) else {}
    flips = []
    for vid in sorted({v for vs in V.values() for v in vs}):
        try:
            urllib.request.urlopen(urllib.request.Request('https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=%s&format=json' % vid,
                                                          headers={'User-Agent': 'Mozilla/5.0'}), timeout=20)
            ok = True
        except urllib.error.HTTPError as e:
            ok = e.code not in (401, 403)
        except OSError:
            continue
        m = meta.setdefault(vid, {})
        if m.get('embed', True) != ok:
            flips.append((vid, ok))
        m['embed'] = ok
    if flips:
        json.dump(meta, open(MF, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    blocked = [v for v, m in meta.items() if m.get('embed') is False]
    print('youtube: %d videos on the channel, %d new on project pages, %d embedding changes' % (len(videos), len(added), len(flips)))
    for v, ok in flips:
        print('  embedding %s for %s' % ('on' if ok else 'OFF (opens on YouTube)', v))
    if blocked:
        print('  embedding off (plays on YouTube only): ' + ', '.join(blocked))
    for n, v, t in added:
        print('  added  %s <- %s (%s)' % (n, v, t[:70]))
    for v, t, h in unmatched:
        print('  no project for %s (%s)%s' % (v, t[:70], (' — several matches: ' + ', '.join(h)) if h else ''))
