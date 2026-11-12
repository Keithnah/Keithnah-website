"""Add Google Analytics 4 (keithnah.com, G-6WFGZZ4FTC) to every English page.

The language copies (/zh/, /ms/, ...) are rendered from these pages, so they get it too;
content_group tells the reports which language version was viewed. WhatsApp clicks and
Quick Enquiry submissions are sent as "generate_lead" events by lead-tracker.js.
Run by tools/build_all.py; safe to run again (the block is replaced, never duplicated).
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GA_ID = 'G-6WFGZZ4FTC'
DIRS = ['', 'article', 'area', 'best', 'developer', 'guides', 'mm2h', 'notes', 'property', 'station', 'topic', 'vs']
SNIPPET = ('<!-- KN-GA --><script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>'
           '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
           "if(!window.KN_RENDER){gtag('js',new Date());gtag('config','%s',{content_group:document.documentElement.getAttribute('data-page-lang')||'en'});}"
           '</script><!-- /KN-GA -->') % (GA_ID, GA_ID)
# Microsoft Clarity (heatmaps and session recordings). Empty = off. The project ID is public
# (it is in every page anyway), not a secret: clarity.microsoft.com > project > Settings > Overview.
CLARITY_ID = 'zchi5vsr4l'
if CLARITY_ID:
    SNIPPET = SNIPPET.replace('<!-- /KN-GA -->', '<script>if(!window.KN_RENDER){(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};'
        't=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);'
        '})(window,document,"clarity","script","%s");}</script><!-- /KN-GA -->' % CLARITY_ID)
BLOCK = re.compile(r'<!-- KN-GA -->.*?<!-- /KN-GA -->\n?', re.S)

n = 0
for d in DIRS:
    folder = os.path.join(ROOT, d)
    for f in sorted(os.listdir(folder)):
        if not f.endswith('.html'):
            continue
        p = os.path.join(folder, f)
        t = open(p, encoding='utf-8').read()
        t2 = BLOCK.sub('', t)
        t2 = re.sub(r'</head>', SNIPPET + '\n</head>', t2, count=1, flags=re.I)
        if t2 != t:
            open(p, 'w', encoding='utf-8').write(t2)
            n += 1
print('analytics: Google Analytics %s on %d updated page(s)' % (GA_ID, n))
