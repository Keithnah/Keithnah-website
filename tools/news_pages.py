"""Article pages (article/<slug>.html) and topic landing pages (topic/<slug>.html).

Built from the ARTICLES data in blog.html and the TOPICS in news_content.py.
Called by tools/build_news_page.py; run that script, not this one.
"""
import datetime
import html
import json
import os
import re
from urllib.parse import quote_plus

from news_content import GUIDES, TOPICS

SITE = 'https://keithnah.com'
PAGE = 'blog.html'


def T(s):
    return html.escape(html.unescape(s), quote=False)


def A(s):
    return html.escape(html.unescape(s), quote=True)


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower().replace('&', 'and')).strip('-')


def wa(msg):
    return 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0' % quote_plus('(KNRE) ' + msg)


def load_articles():
    blog = open(PAGE, encoding='utf-8').read()
    i = blog.index('const ARTICLES =') + len('const ARTICLES =')
    arts = json.JSONDecoder().raw_decode(blog[i:].lstrip())[0]
    slugs = {}
    for k, a in arts.items():
        s = slug(re.sub(r"'s\b", 's', html.unescape(a['title'])))[:70].strip('-')
        while s in slugs.values():
            s += '-2'
        slugs[k] = s
    return arts, slugs


ARTICLES, ART_SLUGS = load_articles()

PAGE_CSS = r"""
.art-hero{border-radius:14px;padding:46px 40px;color:#fff;margin:6px 0 34px;position:relative;overflow:hidden;}
.art-hero .icon-art{position:absolute;right:30px;bottom:0;width:240px;opacity:.18;color:#fff;}
.art-cat{display:inline-block;font:700 11px 'Inter',sans-serif;letter-spacing:0.14em;text-transform:uppercase;background:rgba(255,255,255,0.16);padding:6px 12px;border-radius:100px;margin-bottom:14px;}
.art-hero h1{font-size:clamp(28px,4vw,44px);max-width:820px;margin-bottom:12px;position:relative;}
.art-hero time{font-size:13px;opacity:.85;}
.art-wrap{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:44px;align-items:start;margin-bottom:20px;}
.art-body .lead{font-size:18px;line-height:1.75;color:#222;margin-bottom:24px;}
.art-body h2{font-size:clamp(22px,2.4vw,28px);margin:30px 0 12px;}
.art-body p{font-size:16px;line-height:1.8;color:#2a2a2a;margin-bottom:14px;}
.art-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:30px 0;}
.art-stat{background:#fff;border:1px solid var(--line);border-radius:10px;padding:16px;}
.art-stat b{display:block;font-family:'Playfair Display',serif;font-size:24px;color:var(--gold);margin-bottom:4px;}
.art-stat span{font-size:13px;color:var(--grey);}
.art-take{background:#EEEEFB;border-left:4px solid var(--gold);border-radius:8px;padding:18px 22px;margin:26px 0;font-size:16px;line-height:1.7;}
.art-take strong{display:block;font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:var(--gold);margin-bottom:6px;}
.art-side{position:sticky;top:90px;display:flex;flex-direction:column;gap:16px;}
.side-box{background:#fff;border:1px solid var(--line);border-radius:12px;padding:20px;}
.side-box h3{font-size:16px;margin-bottom:12px;}
.side-box p{font-size:14px;color:var(--grey);margin-bottom:10px;}
.side-box .wa-btn{width:100%;justify-content:center;}
.chips{display:flex;flex-wrap:wrap;gap:8px;}
.chip{font:600 13px 'Inter',sans-serif;background:#EFE7DA;border-radius:6px;padding:8px 12px;color:var(--ink);}
.chip:hover{background:#111;color:#fff;} .chip em{font-style:normal;font-size:11px;color:#6b6257;margin-left:6px;} .chip:hover em{color:rgba(255,255,255,.7);}
.topic-head{margin:10px 0 28px;} .topic-head h1{font-size:clamp(32px,4.4vw,50px);margin:8px 0 10px;} .topic-head p{color:var(--grey);font-size:16px;max-width:760px;}
.eyebrow2{font:600 11px 'Inter',sans-serif;letter-spacing:0.28em;text-transform:uppercase;color:var(--gold);}
.acards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px;margin-bottom:40px;}
.acard{display:flex;flex-direction:column;background:#fff;border:1px solid var(--line);border-top:3px solid var(--gold);border-radius:10px;padding:22px;transition:transform .3s var(--ease),box-shadow .3s;}
.acard:hover{transform:translateY(-4px);box-shadow:0 16px 32px rgba(17,17,17,0.09);}
.acard small{font:700 11px 'Inter',sans-serif;letter-spacing:0.1em;text-transform:uppercase;color:var(--gold);}
.acard h2,.acard h3{font-size:19px;line-height:1.3;margin:8px 0 8px;}
.acard p{font-size:13.5px;color:var(--grey);flex:1;}
.acard span{margin-top:12px;font-size:12.5px;font-weight:700;}
.guide-box{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;background:#111;color:#fff;border-radius:12px;padding:22px 26px;margin-bottom:34px;}
.guide-box p{font-family:'Playfair Display',serif;font-size:20px;} .guide-box a{background:#fff;color:#111;padding:11px 20px;border-radius:100px;font-size:13px;font-weight:700;}
@media(max-width:980px){.art-wrap{grid-template-columns:1fr;}.art-side{position:static;}.acards{grid-template-columns:1fr 1fr;}}
@media(max-width:640px){.acards{grid-template-columns:1fr;}.art-stats{grid-template-columns:1fr;}.art-hero{padding:30px 22px;}.art-hero .icon-art{width:150px;}}
"""

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og}"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}">
<link rel="icon" type="image/png" href="../images/d795398568d23a46.png">
<link rel="apple-touch-icon" href="../apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;0,800;1,500&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{ld}</script>
<style>{css}{pcss}</style>
</head>
<body>
<header>
  <a class="logo" href="../"><img src="../images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Keith Nah Real Estate</small></span></a>
  <nav>{nav}</nav>
  <a class="wa-btn" href="{wa}" target="_blank" rel="noopener">{wasvg}<span>WhatsApp Keith</span></a>
</header>
<main class="wrap">
{body}
</main>
<footer>&copy; 2026 Keith Nah Real Estate · <a href="../blog.html">News</a> · <a href="../projects.html">All projects</a> · <a href="../privacy-policy.html">Privacy Policy</a> · <a href="../terms-of-use.html">Terms of Use</a> · <a href="https://www.youtube.com/@KeithNahRealEstate" target="_blank" rel="noopener">YouTube</a> · <a href="https://www.instagram.com/keithnah_/" target="_blank" rel="noopener">Instagram</a></footer>
<a class="float-wa" href="{wa}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">{wasvg}</a>
<script src="../lead-tracker.js"></script>
</body>
</html>
"""


def shell(title, desc, url, body, ld, og='article', msg='Hi Keith, I have a question about Malaysian property.'):
    import build_project_pages as bp  # shared header, nav and styles
    nav = ''.join('<a href="../{0}"{1}>{2}</a>'.format(h, ' class="active"' if h == 'blog.html' else '', html.escape(n)) for h, n in bp.NAV)
    return SHELL.format(title=A(title), desc=A(desc), url=A(url), og=og, ld=json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'),
                        css=bp.CSS, pcss=PAGE_CSS, nav=nav, wa=A(wa(msg)), wasvg=bp.WA_SVG, body=body)


def iso(d):
    return datetime.datetime.strptime(d, '%d %b %Y').date().isoformat()


def excerpt(s, n):
    s = html.unescape(s)
    return s if len(s) <= n else s[:n].rsplit(' ', 1)[0].rstrip('.,;:—– ') + '…'


def acard(aid, tag='h2'):
    a = ARTICLES[aid]
    return '<a class="acard" href="../article/{s}.html"><small>{c} · {d}</small><{t}>{h}</{t}><p>{p}</p><span>Read article →</span></a>'.format(
        s=ART_SLUGS[aid], c=T(a['cat']), d=T(a['date']), t=tag, h=T(a['title']), p=T(excerpt(a['intro'], 170)))


def chips(names):
    return '<div class="chips">%s</div>' % ''.join(
        '<a class="chip" href="../topic/{s}.html">{n}<em>{c}</em></a>'.format(s=slug(tp[0]), n=T(tp[0]), c=len(tp[1]))
        for tp in TOPICS if tp[0] in names)


def crumbs(*parts):
    out = '<a href="../">Home</a><span>›</span><a href="../blog.html">News</a>'
    for href, label in parts[:-1]:
        out += '<span>›</span><a href="{0}">{1}</a>'.format(href, T(label))
    out += '<span>›</span><strong>%s</strong>' % T(parts[-1][1])
    return '<nav class="crumbs" aria-label="Breadcrumb">%s</nav>' % out


def write_pages():
    os.makedirs('article', exist_ok=True)
    os.makedirs('topic', exist_ok=True)
    topics_of = {}
    for tp in TOPICS:
        for a in tp[1]:
            topics_of.setdefault(a, []).append(tp[0])
    newest = sorted(ARTICLES, key=lambda k: iso(ARTICLES[k]['date']), reverse=True)
    guides = {g['id']: g for g in GUIDES}

    for aid, a in ARTICLES.items():
        url = '%s/article/%s.html' % (SITE, ART_SLUGS[aid])
        title = html.unescape(a['title'])
        g = (a.get('grad') or '#1c1a17,#3a3226').split(',')
        mine = topics_of.get(aid, [])
        related = [k for k in newest if k != aid and set(topics_of.get(k, [])) & set(mine)][:3] or [k for k in newest if k != aid][:3]
        secs = ''.join('<h2>%s</h2>%s' % (T(s['h2']), ''.join('<p>%s</p>' % T(p) for p in s['paragraphs'])) for s in a['sections'])
        stats = ''.join('<div class="art-stat"><b>%s</b><span>%s</span></div>' % (T(s['value']), T(s['label'])) for s in a.get('stats', []))
        trail = ([('../topic/%s.html' % slug(mine[0]), mine[0])] if mine else []) + [('', title)]
        body = """
  {crumbs}
  <div class="art-hero" style="background:linear-gradient(135deg,{g1},{g2});">{icon}<span class="art-cat">{cat}</span><h1>{h1}</h1><time datetime="{iso}">{date} · Keith Nah</time></div>
  <div class="art-wrap">
    <article class="art-body">
      <p class="lead">{intro}</p>
      {secs}
      {stats}
      <div class="art-take"><strong>Key takeaway</strong>{take}</div>
    </article>
    <aside class="art-side">
      <div class="side-box"><h3>Talk to Keith</h3><p>Questions about this topic or a project? Keith replies on WhatsApp.</p><a class="wa-btn" href="{wa}" target="_blank" rel="noopener">WhatsApp Keith</a></div>
      {topics}
    </aside>
  </div>
  <section class="blk"><h2>Related articles</h2><div class="acards">{related}</div></section>""".format(
            crumbs=crumbs(*trail), g1=g[0], g2=g[1] if len(g) > 1 else g[0], icon=a.get('icon', ''), cat=T(a['cat']), h1=T(a['title']),
            iso=iso(a['date']), date=T(a['date']), intro=T(a['intro']), secs=secs,
            stats=('<div class="art-stats">%s</div>' % stats) if stats else '', take=T(a['takeaway']),
            wa=A(wa('Hi Keith, I read "%s" on your website and have a question.' % title)),
            topics=('<div class="side-box"><h3>Topics</h3>%s</div>' % chips(mine)) if mine else '',
            related=''.join(acard(k, 'h3') for k in related))
        ld = [{'@context': 'https://schema.org', '@type': 'Article', 'headline': title, 'datePublished': iso(a['date']),
               'author': {'@type': 'Person', 'name': 'Keith Nah'}, 'publisher': {'@type': 'Organization', 'name': 'Keith Nah Real Estate'},
               'description': excerpt(a['intro'], 300), 'mainEntityOfPage': url, 'articleSection': html.unescape(a['cat'])},
              {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
                  {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
                  {'@type': 'ListItem', 'position': 2, 'name': 'News', 'item': SITE + '/blog.html'},
                  {'@type': 'ListItem', 'position': 3, 'name': title, 'item': url}]}]
        open('article/%s.html' % ART_SLUGS[aid], 'w', encoding='utf-8').write(
            shell('%s | Keith Nah' % title, excerpt(a['intro'], 158), url, body, ld,
                  msg='Hi Keith, I read "%s" on your website and have a question.' % title))

    for name, ids, desc, gid in TOPICS:
        s = slug(name)
        url = '%s/topic/%s.html' % (SITE, s)
        ids_sorted = sorted(ids, key=lambda k: iso(ARTICLES[k]['date']), reverse=True)
        gbox = ''
        if name == 'MM2H':
            gbox += '<div class="guide-box"><p>See the MM2H tiers, requirements and costs side by side.</p><a href="../mm2h.html">MM2H explained →</a></div>'
        if gid in guides:
            gd = guides[gid]
            gbox += '<div class="guide-box"><p>Want the step-by-step version? Read our {0} guide.</p><a href="../blog.html#{1}">{0} →</a></div>'.format(T(gd['tab']), gd['id'])
        body = """
  {crumbs}
  <div class="topic-head"><span class="eyebrow2">Topic · {n} article{pl}</span><h1>{h1}</h1><p>{desc}</p></div>
  <div class="acards">{cards}</div>
  {gbox}
  <section class="blk"><h2>More topics</h2>{more}</section>""".format(
            crumbs=crumbs(('../blog.html#blog', 'Topics'), ('', name)), n=len(ids), pl='' if len(ids) == 1 else 's', h1=T(name), desc=T(desc),
            cards=''.join(acard(k) for k in ids_sorted), gbox=gbox, more=chips([tp[0] for tp in TOPICS if tp[0] != name]))
        ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': '%s: property articles' % name, 'url': url, 'description': desc,
              'hasPart': [{'@type': 'Article', 'headline': html.unescape(ARTICLES[k]['title']), 'url': '%s/article/%s.html' % (SITE, ART_SLUGS[k])} for k in ids_sorted]}
        open('topic/%s.html' % s, 'w', encoding='utf-8').write(
            shell('%s: Malaysia Property Articles | Keith Nah' % name, '%s %d article%s by Keith Nah.' % (desc, len(ids), '' if len(ids) == 1 else 's'),
                  url, body, ld, og='website', msg='Hi Keith, I was reading about %s on your website.' % name))

    json.dump(ART_SLUGS, open('tools/article_slugs.json', 'w', encoding='utf-8'), indent=1)
    print('Wrote %d article pages and %d topic pages' % (len(ARTICLES), len(TOPICS)))
