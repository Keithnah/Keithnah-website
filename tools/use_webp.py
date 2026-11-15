"""Serve WebP images where they are smaller than the JPG; keep the JPG everywhere else.

1. For every images/**/*.jpg, write a WebP copy next to it (quality 75) and keep it only if it is
   at least 3% smaller than the JPG. JPGs are never changed or deleted.
2. In every HTML page:
   - <img src="….jpg"> with a smaller WebP: src points to the WebP, with onerror falling back to the JPG
     (browsers that cannot show WebP load the JPG instead);
   - inline background images and CSS background-image declarations get an image-set() line after the
     original, so browsers that do not support it keep the JPG;
   - the hero preload asks for the WebP (type="image/webp", so other browsers skip it).
   Open Graph images, sitemaps and JavaScript data keep the JPG.
Safe to run again. Run by tools/build_all.py as the last step before the language pages.

    python3 tools/use_webp.py
"""
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
from PIL import Image  # noqa: E402

QUALITY, MIN_SAVING = 75, 0.03


SKIP = os.path.join(HERE, 'webp_skip.json')   # JPGs whose WebP was not smaller (not converted again)


def make_webps():
    import json
    skip = json.load(open(SKIP)) if os.path.exists(SKIP) else {}
    made = kept = 0
    for j in sorted(glob.glob('images/**/*.jpg', recursive=True)):
        w = j[:-4] + '.webp'
        mt = int(os.path.getmtime(j))
        if (os.path.exists(w) and os.path.getmtime(w) >= mt) or skip.get(j) == mt:
            kept += 1
            continue
        try:
            Image.open(j).convert('RGB').save(w, 'WEBP', quality=QUALITY, method=6)
        except Exception:
            continue
        if os.path.getsize(w) > os.path.getsize(j) * (1 - MIN_SAVING):
            os.remove(w)   # not smaller: the page keeps the JPG
            skip[j] = mt
        else:
            skip.pop(j, None)
            made += 1
    json.dump(skip, open(SKIP, 'w'), indent=0, sort_keys=True)
    return made, kept


def has_webp(path):
    return os.path.exists(path[:-4] + '.webp')


def fs_path(page, url):
    """Site URL used on a page -> file path in the repository, or None."""
    if url.startswith(('http:', 'https:', 'data:', '//')):
        return None
    p = url.lstrip('/') if url.startswith('/') else os.path.normpath(os.path.join(os.path.dirname(page), url))
    return p if p.startswith('images/') and p.endswith('.jpg') else None


def fix_page(page, s):
    b = re.search(r'<base href="/([^"]*)"', s[:5000])   # language copies resolve links from the English page's folder
    if b:
        page = b.group(1) + os.path.basename(page)
    def img(m):
        tag = m.group(0)
        if 'onerror=' in tag:
            return tag
        sm = re.search(r'\ssrc="([^"]+\.jpg)"', tag)
        if not sm:
            return tag
        p = fs_path(page, sm.group(1))
        if not p or not has_webp(p):
            return tag
        jpg = sm.group(1)
        return tag.replace(sm.group(0), ' src="%s" onerror="this.onerror=null;this.src=\'%s\'"' % (jpg[:-4] + '.webp', jpg), 1)
    s = re.sub(r'<img\b[^>]*>', img, s)

    def bg(m):   # background-image:url('x.jpg') in a style attribute or a <style> block
        decl, url = m.group(0), m.group(2)
        p = fs_path(page, url)
        if not p or not has_webp(p):
            return decl
        layered = decl.replace("url('%s')" % url, "image-set(url('%s') type('image/webp'),url('%s') type('image/jpeg'))" % (url[:-4] + '.webp', url))
        return decl + ';' + layered
    s = re.sub(r"background-image:(\s*(?:linear-gradient\([^;]*?\)\s*,\s*)?)url\('([^']+\.jpg)'\)(?!;background-image:image-set)", bg, s)

    def pre(m):
        tag, href = m.group(0), m.group(1)
        p = fs_path(page, href)
        if not p or not has_webp(p) or 'image/webp' in tag:
            return tag
        return tag.replace('href="%s"' % href, 'href="%s" type="image/webp"' % (href[:-4] + '.webp'))
    s = re.sub(r'<link rel="preload" as="image" href="([^"]+\.jpg)"[^>]*>', pre, s)
    return s


def main():
    made, kept = make_webps()
    n = 0
    for f in glob.glob('**/*.html', recursive=True):
        if f.startswith(('tools/', 'vendor/', 'node_modules/')):
            continue
        s = open(f, encoding='utf-8').read()
        t = fix_page(f, s)
        if t != s:
            open(f, 'w', encoding='utf-8').write(t)
            n += 1
    print('webp: %d new, %d existing; pages updated: %d' % (made, kept, n))


if __name__ == '__main__':
    main()
