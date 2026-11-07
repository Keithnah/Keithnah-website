"""Set a project's main photo (card cover on View Projects and Compare, hero on its project page).

Resizes the picture to at most 1200 px, saves it as images/<sha1-16>.jpg and
puts it on the project's cards in projects.html and compare.html (replacing
any earlier photo). Then run tools/build_project_pages.py.

Usage: python3 tools/set_project_photo.py "Project Name" path/to/photo.jpg [more "Name" photo pairs]
"""
import hashlib
import html
import io
import re
import sys

from PIL import Image

E = lambda s: html.escape(s, quote=True)


def save(path):
    im = Image.open(path).convert('RGB')
    im.thumbnail((1200, 1200), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=82, optimize=True, progressive=True)
    raw = buf.getvalue()
    name = 'images/%s.jpg' % hashlib.sha1(raw).hexdigest()[:16]
    open(name, 'wb').write(raw)
    return name


def set_photo(page, card_cls, media_cls, photo_cls, name, img):
    t = open(page, encoding='utf-8').read()
    hit = 0
    for m in re.finditer(r'<div class="%s"[^>]*data-idx="(\d+)"' % card_cls, t):
        block_end = t.find('<div class="%s"' % card_cls, m.end())
        block = t[m.start():block_end if block_end > 0 else len(t)]
        if not re.search(r'>%s</(?:a|h4)>' % re.escape(E(name)), block):
            continue
        new = re.sub(r'\s*<img class="%s"[^>]*>' % photo_cls, '', block, count=1)
        new = re.sub(r'(<div class="%s"[^>]*>)' % media_cls, lambda x: x.group(1) + '\n      <img class="%s" src="%s" alt="%s" loading="lazy">' % (photo_cls, img, E(name)), new, count=1)
        t = t[:m.start()] + new + t[m.start() + len(block):]
        hit += 1
        break
    assert hit, '%s: no card for %s' % (page, name)
    open(page, 'w', encoding='utf-8').write(t)


if __name__ == '__main__':
    args = sys.argv[1:]
    assert args and len(args) % 2 == 0, __doc__
    for name, path in zip(args[::2], args[1::2]):
        img = save(path)
        set_photo('projects.html', 'proj-card', 'proj-media', 'proj-photo', name, img)
        set_photo('compare.html', 'cmp-card', 'cmp-card-media', 'cmp-card-photo', name, img)
        print(name, '->', img)
