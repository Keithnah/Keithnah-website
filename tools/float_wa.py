"""The floating "Chat with Keith" WhatsApp button with a pulsing glow, on every page.

The project, article and topic page generators use FLOAT_CSS and float_html().
For the hand-built pages in the site root, run:
    python3 tools/float_wa.py
Safe to run again.
"""
import glob
import re

LABEL = 'Chat with Keith'
FLOAT_CSS = """
/* KN-FLOAT:START */
a.float-wa.float-wa{position:fixed;right:22px;bottom:22px;z-index:60;display:inline-flex;align-items:center;gap:11px;width:auto;height:auto;
  padding:13px 24px 13px 18px;border-radius:100px;background:#25D366;color:#fff;font:700 16px/1 'Inter',system-ui,sans-serif;letter-spacing:0;
  text-decoration:none;animation:knWaPulse 2.6s ease-in-out infinite;transition:transform .25s ease;}
a.float-wa.float-wa:hover{transform:translateY(-2px) scale(1.03);color:#fff;}
a.float-wa.float-wa svg{width:26px;height:26px;flex:0 0 26px;fill:#fff;}
a.float-wa.float-wa .fw-txt{white-space:nowrap;}
@keyframes knWaPulse{
  0%,100%{box-shadow:0 0 0 4px rgba(37,211,102,.18),0 0 14px 2px rgba(37,211,102,.30),0 8px 22px rgba(0,0,0,.16);}
  50%{box-shadow:0 0 0 12px rgba(37,211,102,.10),0 0 30px 10px rgba(37,211,102,.45),0 8px 22px rgba(0,0,0,.16);}
}
@media(max-width:600px){a.float-wa.float-wa{right:16px;bottom:16px;padding:11px 18px 11px 14px;font-size:14px;gap:9px;}a.float-wa.float-wa svg{width:22px;height:22px;flex-basis:22px;}}
@media(prefers-reduced-motion:reduce){a.float-wa.float-wa{animation:none;box-shadow:0 0 0 6px rgba(37,211,102,.18),0 8px 22px rgba(0,0,0,.16);}}
/* KN-FLOAT:END */
"""
SVG = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2.05 22l5.25-1.38'
       'c1.44.79 3.06 1.2 4.72 1.2h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.87 9.87 0 0012.04 2zm5.82 14.06c-.24.68-1.42 1.3-1.95 1.38'
       '-.5.08-1.13.11-1.82-.11-.42-.13-.96-.31-1.65-.61-2.9-1.25-4.79-4.17-4.94-4.36-.14-.19-1.18-1.57-1.18-3s.75-2.13 1.02-2.42c.27-.29.58-.36.78-.36h.56'
       'c.18 0 .42-.07.66.5.24.58.82 2 .89 2.15.07.14.12.31.02.5-.1.19-.14.31-.29.48-.14.17-.3.38-.43.51-.14.14-.29.3-.13.58.17.29.74 1.22 1.59 1.98 1.09.97'
       ' 2.01 1.27 2.3 1.41.29.14.46.12.63-.07.17-.19.72-.84.91-1.13.19-.29.38-.24.65-.14.26.1 1.68.79 1.97.94.29.14.48.21.55.33.07.12.07.7-.17 1.38z"/></svg>')


def float_html(href):
    return '<a class="float-wa" href="%s" target="_blank" rel="noopener" aria-label="%s on WhatsApp">%s<span class="fw-txt">%s</span></a>' % (
        href, LABEL, SVG, LABEL)


DEFAULT_HREF = ('https://api.whatsapp.com/send/?phone=60102821568&amp;text=%28KNRE%29+Hi+Keith%2C+I+would+like+to+explore+more+on+Malaysia+Property.'
                '&amp;type=phone_number&amp;app_absent=0')
ANCHOR = re.compile(r'<a\b[^>]*class="float-wa[^"]*"[^>]*>.*?</a>', re.S)


def fix_page(path):
    t = open(path, encoding='utf-8').read()
    found = list(ANCHOR.finditer(t))
    if found:
        keep = found[-1].group(0)
        href = re.search(r'href="([^"]+)"', keep).group(1)
        for m in reversed(found[:-1]):  # an older duplicate button sat in the same corner on some pages
            t = t[:m.start()] + t[m.end():].lstrip('\n')
        t = ANCHOR.sub(lambda _: float_html(href), t)
    else:
        t = t.replace('</body>', float_html(DEFAULT_HREF) + '\n</body>', 1)
    t = re.sub(r'<style id="kn-float">.*?</style>\n?', '', t, flags=re.S)
    t = t.replace('</head>', '<style id="kn-float">%s</style>\n</head>' % FLOAT_CSS, 1)
    open(path, 'w', encoding='utf-8').write(t)


if __name__ == '__main__':
    pages = sorted(glob.glob('*.html'))
    for p in pages:
        fix_page(p)
    print('Floating WhatsApp button updated on %d pages' % len(pages))
