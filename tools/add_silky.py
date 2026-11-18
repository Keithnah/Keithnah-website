"""Silky scrolling on every page (smooth mouse-wheel glide on computers, sections and cards rising softly into view,
photos drifting inside their frames, a thin reading-progress bar). Same feel as homeinmalaysia.com.

Copies tools/silky_src.js to /silky.js and adds one <script> tag (KN-SILKY marker) before </body> on every page.
Phones keep their native scrolling; nothing moves for visitors who ask for reduced motion. Safe to run again.

    python3 tools/add_silky.py
"""
import glob
import hashlib
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)

src = open(os.path.join(HERE, 'silky_src.js'), encoding='utf-8').read()
open('silky.js', 'w', encoding='utf-8').write(src)
v = hashlib.md5(src.encode()).hexdigest()[:8]
TAG = '<!-- KN-SILKY --><script src="/silky.js?v=%s" defer></script>' % v
RX = re.compile(r'<!-- KN-SILKY --><script src="/silky\.js[^"]*" defer></script>')

n = 0
for f in glob.glob('**/*.html', recursive=True):
    if f.startswith(('tools/', 'vendor/', 'node_modules/', 'downloads/', 'tg/')) or os.path.basename(f).startswith('preview-'):
        continue
    s = open(f, encoding='utf-8').read()
    if '</body>' not in s:
        continue
    t = RX.sub(TAG, s) if RX.search(s) else s.replace('</body>', TAG + '\n</body>', 1) if s.count('</body>') == 1 else s[:s.rfind('</body>')] + TAG + '\n' + s[s.rfind('</body>'):]
    if t != s:
        open(f, 'w', encoding='utf-8').write(t)
        n += 1
print('silky: silky.js v%s; pages updated: %d' % (v, n))
