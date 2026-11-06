"""Move photos embedded in the HTML pages (base64 data: URIs) into images/.

Pages load much faster and stay well under Google's 15 MB per-page limit
when photos are separate files. Each photo is named by a hash of its
content, so the same photo used on several pages is stored once.

Usage (from the repository root):
    python3 tools/extract_images.py index.html projects.html compare.html ...

Safe to run again: pages without embedded photos are left unchanged.
Tiny inline images (icons under ~3 KB) stay embedded.
"""
import base64
import hashlib
import io
import os
import re
import sys

try:
    from PIL import Image
except ImportError:  # recompression is optional
    Image = None

OUT_DIR = 'images'
MIN_B64_LEN = 4000          # keep icons and other tiny images inline
RECOMPRESS_OVER = 150_000   # re-encode JPEGs larger than this (bytes)
EXT = {'jpeg': 'jpg', 'jpg': 'jpg', 'png': 'png', 'webp': 'webp', 'gif': 'gif'}
PAT = re.compile(r'data:image/(jpeg|jpg|png|webp|gif);base64,([A-Za-z0-9+/=]+)')


def maybe_smaller_jpeg(raw):
    if Image is None or len(raw) <= RECOMPRESS_OVER:
        return raw
    try:
        im = Image.open(io.BytesIO(raw))
        im = im.convert('RGB')
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=82, optimize=True, progressive=True)
        out = buf.getvalue()
        return out if len(out) < len(raw) else raw
    except Exception:
        return raw


def extract(path):
    html = open(path, encoding='utf-8').read()
    written = reused = 0

    def repl(m):
        nonlocal written, reused
        kind, b64 = m.group(1), m.group(2)
        if len(b64) < MIN_B64_LEN:
            return m.group(0)
        raw = base64.b64decode(b64)
        name = '%s/%s.%s' % (OUT_DIR, hashlib.sha1(raw).hexdigest()[:16], EXT[kind])
        if os.path.exists(name):
            reused += 1
        else:
            data = maybe_smaller_jpeg(raw) if EXT[kind] == 'jpg' else raw
            with open(name, 'wb') as fh:
                fh.write(data)
            written += 1
        return name

    new = PAT.sub(repl, html)
    if new != html:
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(new)
    print('%-18s %6.2f MB -> %5.2f MB  (%d new photos, %d reused)'
          % (path, len(html.encode()) / 1e6, len(new.encode()) / 1e6, written, reused))


if __name__ == '__main__':
    os.makedirs(OUT_DIR, exist_ok=True)
    for p in sys.argv[1:]:
        extract(p)
