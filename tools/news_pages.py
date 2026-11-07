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
import news_i18n as I

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
    from news_content import EXTRA_ARTICLES
    for k, v in EXTRA_ARTICLES.items():
        arts.setdefault(k, v)
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
  <div class="hdr-right">{menu}<a class="wa-btn" href="{wa}" target="_blank" rel="noopener">{wasvg}<span>{l_wa}</span></a></div>
</header>
<main class="wrap">
{body}
</main>
<footer>&copy; 2026 Keith Nah Real Estate · <a href="../blog.html">{l_news}</a> · <a href="../projects.html">{l_all}</a> · <a href="../privacy-policy.html">{l_priv}</a> · <a href="../terms-of-use.html">{l_terms}</a> · <a href="https://www.youtube.com/@KeithNahRealEstate" target="_blank" rel="noopener">YouTube</a> · <a href="https://www.instagram.com/keithnah_/" target="_blank" rel="noopener">Instagram</a></footer>
<a class="float-wa" href="{wa}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">{wasvg}</a>
{tscript}
{menujs}
<script src="../lead-tracker.js"></script>
</body>
</html>
"""


def shell(c, title, desc, url, body, ld, og='article', msg='Hi Keith, I have a question about Malaysian property.'):
    import build_project_pages as bp  # shared header, nav and styles
    nav = ''.join('<a href="../{0}"{1}>{2}</a>'.format(h, ' class="active"' if h == 'blog.html' else '', c.tt(n)) for h, n in bp.NAV)
    return SHELL.format(title=A(title), desc=A(desc), url=A(url), og=og, ld=json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'),
                        css=bp.CSS, pcss=PAGE_CSS + I.MENU_CSS, nav=nav, wa=A(wa(msg)), wasvg=bp.WA_SVG, body=body, menu=I.menu_html(),
                        l_wa=c.tt('WhatsApp Keith'), l_news=c.tt('News'), l_all=c.tt('All projects'), l_priv=c.tt('Privacy Policy'),
                        l_terms=c.tt('Terms of Use'), tscript=c.script(), menujs=I.menu_js())


def iso(d):
    return datetime.datetime.strptime(d, '%d %b %Y').date().isoformat()


def excerpt(s, n):
    s = html.unescape(s)
    return s if len(s) <= n else s[:n].rsplit(' ', 1)[0].rstrip('.,;:—– ') + '…'


def excerpt_any(s, l):
    """Excerpt for any language: CJK has no spaces and packs more meaning per character."""
    s = html.unescape(s)
    n = {'zh-CN': 70, 'zh-TW': 70, 'ja': 80, 'ko': 95}.get(l, 170)
    if len(s) <= n:
        return s
    cut = s[:n]
    if ' ' in cut and l not in ('zh-CN', 'zh-TW', 'ja'):
        cut = cut.rsplit(' ', 1)[0]
    return cut.rstrip('.,;:—–、。， ') + '…'


def tr_excerpt(text, n=170):
    full = I.tr(text)
    return {l: excerpt_any(v, l) for l, v in full.items()}


def acard(c, aid, tag='h2'):
    a = ARTICLES[aid]
    return ('<a class="acard" href="../article/{s}.html"><small>{c} · <span data-date="{iso}">{d}</span></small><{t}>{h}</{t}><p>{p}</p><span>{r}</span></a>').format(
        s=ART_SLUGS[aid], c=c.tt(a['cat']), iso=iso(a['date']), d=T(a['date']), t=tag, h=c.tt(a['title']),
        p=c.tt(excerpt(a['intro'], 170), tr_excerpt(a['intro'])), r=c.tt('Read article →'))


def chips(c, names):
    return '<div class="chips">%s</div>' % ''.join(
        '<a class="chip" href="../topic/{s}.html">{n}<em>{k}</em></a>'.format(s=slug(tp[0]), n=c.tt(tp[0]), k=len(tp[1]))
        for tp in TOPICS if tp[0] in names)


def crumbs(c, *parts):
    out = '<a href="../">%s</a><span>›</span><a href="../blog.html">%s</a>' % (c.tt('Home'), c.tt('News'))
    for href, label in parts[:-1]:
        out += '<span>›</span><a href="{0}">{1}</a>'.format(href, c.tt(label))
    out += '<span>›</span><strong>%s</strong>' % c.tt(parts[-1][1])
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
    missing = set()

    for aid, a in ARTICLES.items():
        c = I.Collector()
        url = '%s/article/%s.html' % (SITE, ART_SLUGS[aid])
        title = html.unescape(a['title'])
        g = (a.get('grad') or '#1c1a17,#3a3226').split(',')
        mine = topics_of.get(aid, [])
        related = [k for k in newest if k != aid and set(topics_of.get(k, [])) & set(mine)][:3] or [k for k in newest if k != aid][:3]
        secs = ''.join('<h2>%s</h2>%s' % (c.tt(s['h2']), ''.join('<p>%s</p>' % c.tt(p) for p in s['paragraphs'])) for s in a['sections'])
        stats = ''.join('<div class="art-stat"><b>%s</b><span>%s</span></div>' % (T(s['value']), c.tt(s['label'])) for s in a.get('stats', []))
        trail = ([('../topic/%s.html' % slug(mine[0]), mine[0])] if mine else []) + [('', title)]
        body = """
  {crumbs}
  <div class="art-hero" style="background:linear-gradient(135deg,{g1},{g2});">{icon}<span class="art-cat">{cat}</span><h1>{h1}</h1><time datetime="{iso}"><span data-date="{iso}">{date}</span> · Keith Nah</time></div>
  <div class="art-wrap">
    <article class="art-body">
      <p class="lead">{intro}</p>
      {secs}
      {stats}
      <div class="art-take"><strong>{l_take}</strong>{take}</div>
    </article>
    <aside class="art-side">
      <div class="side-box"><h3>{l_talk}</h3><p>{l_q}</p><a class="wa-btn" href="{wa}" target="_blank" rel="noopener">{l_wa}</a></div>
      {topics}
    </aside>
  </div>
  <section class="blk"><h2>{l_rel}</h2><div class="acards">{related}</div></section>""".format(
            crumbs=crumbs(c, *trail), g1=g[0], g2=g[1] if len(g) > 1 else g[0], icon=a.get('icon', ''), cat=c.tt(a['cat']), h1=c.tt(a['title']),
            iso=iso(a['date']), date=T(a['date']), intro=c.tt(a['intro']), secs=secs,
            stats=('<div class="art-stats">%s</div>' % stats) if stats else '', take=c.tt(a['takeaway']),
            l_take=c.tt('Key takeaway'), l_talk=c.tt('Talk to Keith'), l_q=c.tt('Questions about this topic or a project? Keith replies on WhatsApp.'),
            l_wa=c.tt('WhatsApp Keith'), l_rel=c.tt('Related articles'),
            wa=A(wa('Hi Keith, I read "%s" on your website and have a question.' % title)),
            topics=('<div class="side-box"><h3>%s</h3>%s</div>' % (c.tt('Topics'), chips(c, mine))) if mine else '',
            related=''.join(acard(c, k, 'h3') for k in related))
        for p in [a['title'], a['intro'], a['takeaway']] + [s['h2'] for s in a['sections']] + [p for s in a['sections'] for p in s['paragraphs']]:
            if not I.tr(p):
                missing.add((aid, p[:60]))
        ld = [{'@context': 'https://schema.org', '@type': 'Article', 'headline': title, 'datePublished': iso(a['date']),
               'author': {'@type': 'Person', 'name': 'Keith Nah'}, 'publisher': {'@type': 'Organization', 'name': 'Keith Nah Real Estate'},
               'description': excerpt(a['intro'], 300), 'mainEntityOfPage': url, 'articleSection': html.unescape(a['cat'])},
              {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
                  {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
                  {'@type': 'ListItem', 'position': 2, 'name': 'News', 'item': SITE + '/blog.html'},
                  {'@type': 'ListItem', 'position': 3, 'name': title, 'item': url}]}]
        page = shell(c, '%s | Keith Nah' % title, excerpt(a['intro'], 158), url, body, ld,
                     msg='Hi Keith, I read "%s" on your website and have a question.' % title)
        open('article/%s.html' % ART_SLUGS[aid], 'w', encoding='utf-8').write(page)

    for name, ids, desc, gid in TOPICS:
        c = I.Collector()
        s = slug(name)
        url = '%s/topic/%s.html' % (SITE, s)
        ids_sorted = sorted(ids, key=lambda k: iso(ARTICLES[k]['date']), reverse=True)
        gbox = ''
        if name == 'MM2H':
            gbox += '<div class="guide-box"><p>%s</p><a href="../mm2h.html">%s</a></div>' % (
                c.tt('See the MM2H tiers, requirements and costs side by side.'), c.tt('MM2H explained →'))
        if gid in guides:
            gd = guides[gid]
            arrow = {l: v + ' →' for l, v in I.tr(gd['tab']).items()}
            gbox += '<div class="guide-box"><p>{0}</p><a href="../blog.html#{1}">{2}</a></div>'.format(
                c.tt('Want the step-by-step version? Read our %s guide.' % gd['tab'], I.fmt('Want the step-by-step version? Read our {guide} guide.', guide=gd['tab'])),
                gd['id'], c.tt(gd['tab'] + ' →', arrow))
        n = len(ids)
        word = 'article' if n == 1 else 'articles'
        head = {l: '%s · %d %s' % (I.tr('Topic').get(l, 'Topic'), n, I.tr(word).get(l, word)) for l in I.LANGS}
        body = """
  {crumbs}
  <div class="topic-head"><span class="eyebrow2">{head}</span><h1>{h1}</h1><p>{desc}</p></div>
  <div class="acards">{cards}</div>
  {gbox}
  <section class="blk"><h2>{l_more}</h2>{more}</section>""".format(
            crumbs=crumbs(c, ('../blog.html#blog', 'Topics'), ('', name)), head=c.tt('Topic · %d %s' % (n, word), head), h1=c.tt(name), desc=c.tt(desc),
            cards=''.join(acard(c, k) for k in ids_sorted), gbox=gbox, l_more=c.tt('More topics'),
            more=chips(c, [tp[0] for tp in TOPICS if tp[0] != name]))
        ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': '%s: property articles' % name, 'url': url, 'description': desc,
              'hasPart': [{'@type': 'Article', 'headline': html.unescape(ARTICLES[k]['title']), 'url': '%s/article/%s.html' % (SITE, ART_SLUGS[k])} for k in ids_sorted]}
        page = shell(c, '%s: Malaysia Property Articles | Keith Nah' % name, '%s %d %s by Keith Nah.' % (desc, n, word),
                     url, body, ld, og='website', msg='Hi Keith, I was reading about %s on your website.' % name)
        open('topic/%s.html' % s, 'w', encoding='utf-8').write(page)

    json.dump(ART_SLUGS, open('tools/article_slugs.json', 'w', encoding='utf-8'), indent=1)
    print('Wrote %d article pages and %d topic pages; untranslated article text: %d' % (len(ARTICLES), len(TOPICS), len(missing)))
    for m in sorted(missing)[:10]:
        print('  missing:', m)
