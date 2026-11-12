"""The floating "Chat with Keith" WhatsApp button with a pulsing glow, and the back-to-top button above it, on every page.

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
/* back to top, above the WhatsApp button */
.kn-fab{position:fixed;right:22px;bottom:22px;z-index:60;display:flex;flex-direction:column;align-items:center;gap:12px;}
.kn-fab a.float-wa.float-wa{position:static;right:auto;bottom:auto;}
.kn-top{width:48px;height:48px;border-radius:50%;background:#fff;border:1.5px solid #d6d6d6;box-shadow:0 6px 18px rgba(0,0,0,.12);display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;color:#555;
  opacity:0;visibility:hidden;transform:translateY(8px);transition:opacity .25s ease,transform .25s ease,visibility .25s,border-color .2s,color .2s;}
.kn-top.show{opacity:1;visibility:visible;transform:none;}
.kn-top:hover{border-color:var(--gold,#5E60CE);color:var(--gold,#5E60CE);}
.kn-top svg{width:20px;height:20px;}
@media(max-width:600px){.kn-fab{right:16px;bottom:16px;gap:10px;}.kn-top{width:44px;height:44px;}}
@media(prefers-reduced-motion:reduce){.kn-top{transition:none;}}
/* phones: the header WhatsApp button would push the menu button off screen; the floating button stays */
@media(max-width:560px){header .whatsapp-btn,header .wa-btn,.nav-right .whatsapp-btn{display:none!important;}.hamburger{margin-left:auto;padding:6px 4px;}}
/* KN-FLOAT:END */
"""
SVG = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2.05 22l5.25-1.38'
       'c1.44.79 3.06 1.2 4.72 1.2h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.87 9.87 0 0012.04 2zm5.82 14.06c-.24.68-1.42 1.3-1.95 1.38'
       '-.5.08-1.13.11-1.82-.11-.42-.13-.96-.31-1.65-.61-2.9-1.25-4.79-4.17-4.94-4.36-.14-.19-1.18-1.57-1.18-3s.75-2.13 1.02-2.42c.27-.29.58-.36.78-.36h.56'
       'c.18 0 .42-.07.66.5.24.58.82 2 .89 2.15.07.14.12.31.02.5-.1.19-.14.31-.29.48-.14.17-.3.38-.43.51-.14.14-.29.3-.13.58.17.29.74 1.22 1.59 1.98 1.09.97'
       ' 2.01 1.27 2.3 1.41.29.14.46.12.63-.07.17-.19.72-.84.91-1.13.19-.29.38-.24.65-.14.26.1 1.68.79 1.97.94.29.14.48.21.55.33.07.12.07.7-.17 1.38z"/></svg>')


TOP_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 15l6-6 6 6"/></svg>'
TOP_JS = ("<script>(function(){var b=document.getElementById('knTop');if(!b)return;"
          "function s(){b.classList.toggle('show',(window.pageYOffset||document.documentElement.scrollTop)>300);}"
          "window.addEventListener('scroll',s,{passive:true});s();"
          "b.addEventListener('click',function(){var r=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;window.scrollTo({top:0,behavior:r?'auto':'smooth'});});})();</script>")


def float_html(href):
    """Back-to-top button stacked above the WhatsApp button, in one fixed corner group."""
    wa = '<a class="float-wa" href="%s" target="_blank" rel="noopener" aria-label="%s on WhatsApp">%s<span class="fw-txt">%s</span></a>' % (
        href, LABEL, SVG, LABEL)
    return ('<div class="kn-fab"><button type="button" class="kn-top" id="knTop" aria-label="Back to top">%s</button>%s</div><!--/kn-fab-->%s'
            % (TOP_SVG, wa, TOP_JS))


DEFAULT_HREF = ('https://api.whatsapp.com/send/?phone=60102821568&amp;text=%28KNRE%29+Hi+Keith%2C+I+would+like+to+explore+more+on+Malaysia+Property.'
                '&amp;type=phone_number&amp;app_absent=0')
ANCHOR = re.compile(r'<a\b[^>]*class="float-wa[^"]*"[^>]*>.*?</a>', re.S)


def fix_page(path):
    t = open(path, encoding='utf-8').read()
    # unwrap an earlier corner group so the WhatsApp link inside it is found again
    t = re.sub(r'<div class="kn-fab">.*?(<a\b[^>]*class="float-wa.*?</a>)</div><!--/kn-fab--><script>\(function\(\)\{var b=document\.getElementById\(\'knTop\'\).*?</script>',
               lambda m: m.group(1), t, flags=re.S)
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


# ---------- mobile menu for pages that have no menu button (project, article, topic, legal pages)
MNAV_CSS = """<style id="kn-mnav-css">
.kn-burger{display:none;margin-left:auto;background:none;border:0;color:#fff;font-size:26px;line-height:1;padding:6px 4px;cursor:pointer;}
@media(max-width:1100px){.kn-burger{display:block;}}
#knMnav{position:fixed;inset:0;z-index:2147483000;display:none;}
#knMnav.open{display:block;}
#knMnav .kn-mbg{position:absolute;inset:0;background:rgba(10,10,30,.55);}
#knMnav .kn-mpanel{position:absolute;top:0;right:0;bottom:0;width:min(82vw,340px);background:#1d1b4f;color:#fff;padding:20px 22px 28px;overflow-y:auto;box-shadow:-8px 0 30px rgba(0,0,0,.35);}
html[dir=rtl] #knMnav .kn-mpanel{right:auto;left:0;}
#knMnav .kn-mclose{display:block;margin-left:auto;background:none;border:0;color:#fff;font-size:30px;line-height:1;cursor:pointer;padding:4px 8px;}
#knMnav .kn-mlinks a{display:block;color:#fff;text-decoration:none;font-size:17px;letter-spacing:.04em;padding:15px 4px;border-bottom:1px solid rgba(255,255,255,.12);}
#knMnav .kn-mlinks a.active{color:#b9b4ff;font-weight:600;}
#knMnav .kn-mwa{display:block;margin-top:24px;text-align:center;background:#25d366;color:#fff;text-decoration:none;border-radius:999px;padding:13px;font-weight:600;}
</style>"""
MNAV_JS = ("<script>function knMnav(o){var d=document.getElementById('knMnav');if(!d)return;o=(o===undefined)?!d.classList.contains('open'):o;"
           "d.classList.toggle('open',o);document.body.style.overflow=o?'hidden':'';}"
           "document.addEventListener('keydown',function(e){if(e.key==='Escape')knMnav(false);});</script>")


def add_mobile_nav(t):
    """Add a menu button to the header and a slide-in menu with the header's own links. Idempotent."""
    if 'class="hamburger"' in t or '<header' not in t:
        return t
    t = re.sub(r'<style id="kn-mnav-css">.*?</style>\n?', '', t, flags=re.S)
    t = re.sub(r'(<!--kn-burger-->)?\s*<button type="button" class="kn-burger".*?</button>', lambda m: m.group(1) or '', t, flags=re.S)
    t = re.sub(r'<div id="knMnav".*?</div></div><!--/knMnav-->\n?<script>function knMnav.*?</script>\n?', '', t, flags=re.S)
    h0 = t.index('<header'); h1 = t.index('</header>', h0)
    nav = re.search(r'<nav>(.*?)</nav>', t[h0:h1], re.S)
    wa = re.search(r'<a class="(?:wa-btn|float-wa)"[^>]*href="([^"]+)"', t)
    links = nav.group(1) if nav else ''
    if 'mm2h.html' not in links:   # MM2H left the main menu for the Free Toolkit; keep it in the mobile menu
        m = re.search(r'href="([^"]*)resources\.html"', links)
        if m:
            links = links.replace('</a>', '</a>', 1)
            i = links.index(m.group(0)); j = links.index('</a>', i) + 4
            links = links[:j] + '<a href="%smm2h.html">MM2H 第二家园</a>' % m.group(1) + links[j:]
    panel = ('<div id="knMnav" aria-hidden="true"><div class="kn-mbg" onclick="knMnav(false)"></div><div class="kn-mpanel">'
             '<button type="button" class="kn-mclose" aria-label="Close" onclick="knMnav(false)">&times;</button>'
             '<div class="kn-mlinks">%s</div>%s</div></div><!--/knMnav-->\n' % (
                 links, ('<a class="kn-mwa" href="%s" target="_blank" rel="noopener">Chat with Keith</a>' % wa.group(1)) if wa else ''))
    burger = '<button type="button" class="kn-burger" aria-label="Menu" onclick="knMnav()">&#9776;</button>'
    if '<!--kn-burger-->' in t[h0:h1]:
        t = t[:h0] + t[h0:h1].replace('<!--kn-burger-->', '<!--kn-burger-->' + burger, 1) + t[h1:]
    else:
        t = t[:h1] + burger + '\n' + t[h1:]
    t = t.replace('</head>', MNAV_CSS + '\n</head>', 1)
    t = t.replace('</body>', panel + MNAV_JS + '\n</body>', 1)
    return t


if __name__ == '__main__':
    pages = sorted(glob.glob('*.html'))
    for p in pages:
        fix_page(p)
    newer = sorted(glob.glob('notes/*.html') + glob.glob('developer/*.html') + glob.glob('station/*.html') + glob.glob('vs/*.html') + glob.glob('mm2h/*.html'))
    for p in newer:   # these generators do not add the floating button themselves
        s = open(p, encoding='utf-8').read()
        if 'class="kn-fab"' not in s:
            m = re.search(r'<a class="wa-btn"[^>]*href="([^"]+)"', s)
            if m:
                s = s.replace('</head>', '<style>' + FLOAT_CSS + '</style>\n</head>', 1).replace('</body>', float_html(m.group(1)) + '\n</body>', 1)
                open(p, 'w', encoding='utf-8').write(s)
    sub = sorted(glob.glob('property/*.html') + glob.glob('article/*.html') + glob.glob('topic/*.html') + glob.glob('area/*.html') + glob.glob('best/*.html') + glob.glob('guides/*.html')) + newer
    n = 0
    for p in pages + sub:
        s = open(p, encoding='utf-8').read()
        s2 = add_mobile_nav(s)
        if s2 != s:
            open(p, 'w', encoding='utf-8').write(s2)
            n += 1
    print('Floating WhatsApp button updated on %d pages; mobile menu added to %d pages' % (len(pages), n))
