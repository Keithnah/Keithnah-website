"""Save title and upload date of every YouTube video on the project pages (tools/video_meta.json).

Search engines need them for the VideoObject structured data on the project pages.
Run after adding videos to tools/project_videos.json (needs internet); the build only reads the file.
    python3 tools/fetch_video_meta.py
"""
import datetime
import json
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'video_meta.json')
ids = sorted({v for vs in json.load(open(os.path.join(HERE, 'project_videos.json'), encoding='utf-8')).values() for v in vs})
meta = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}
UA = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-US,en;q=0.9'}
for vid in ids:
    if vid in meta:
        continue
    try:
        page = urllib.request.urlopen(urllib.request.Request('https://www.youtube.com/watch?v=%s&hl=en' % vid, headers=UA), timeout=30).read().decode('utf-8', 'ignore')
        tm = re.search(r'<meta property="og:title" content="([^"]*)"', page) or re.search(r'<meta name="title" content="([^"]*)"', page)
        o = {'title': __import__('html').unescape(tm.group(1)) if tm else ''}
        m = re.search(r'"uploadDate":"([^"]+)"', page) or re.search(r'"publishDate":"([^"]+)"', page)
        if m:
            date = m.group(1)[:10]
        else:
            d = re.search(r'"dateText":\{"simpleText":"(?:Premiered |Streamed live on )?([A-Z][a-z]{2} \d{1,2}, \d{4})"', page)
            date = datetime.datetime.strptime(d.group(1), '%b %d, %Y').date().isoformat() if d else ''
        dm = re.search(r'"shortDescription":"((?:[^"\\]|\\.)*)"', page)
        desc = json.loads('"%s"' % dm.group(1)) if dm else ''
        if date:
            meta[vid] = {'title': o['title'], 'date': date}
            print(vid, date, o['title'][:60])
        else:
            print(vid, 'no date found')
    except Exception as e:
        print(vid, 'failed:', e)
json.dump(meta, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('%d of %d videos have metadata' % (len(meta), len(ids)))
