"""Project articles: one or two articles about a single project (article/<slug>.html).

Data: tools/project_articles.json, a list of
  {slug, project (the project's page slug), date "14 Nov 2026", cat, title, intro, takeaway: {lang: text},
   sections: [{h2: {lang: text}, paragraphs: [{lang: text}]}], stats: [{value, label: {lang: text}}],
   sources: [{name, url}]}
Texts are en and zh-CN (zh-TW by OpenCC); ms, ja and ko are used when given, English otherwise.
The page uses the article shell of tools/news_pages.py (site header, menu, language switch).
Each article links to its project page, and the project page lists it (tools/build_landing.py, related()).

Written in a plain, neutral voice: facts from the project data and named news reports only,
no legal topics, no exaggerated downsides, none of the site's banned words.

    python3 tools/build_project_articles.py
"""
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
sys.path.insert(0, HERE)
import news_pages as NP  # noqa: E402

try:
    import opencc
    _cc = opencc.OpenCC('s2tw').convert
except ImportError:
    _cc = lambda s: s

PATH = os.path.join(HERE, 'project_articles.json')
SITE = 'https://keithnah.com'
E = lambda s: html.escape(str(s), quote=True)


AUTO = os.path.join(HERE, 'project_articles_auto.json')   # written by tools/gen_project_articles.py


def load():
    out, seen = [], set()
    preview = os.environ.get('KN_PREVIEW') == '1'   # drafts ("draft": true) are built only for a preview
    for p in (PATH, AUTO):
        if os.path.exists(p):
            for a in json.load(open(p, encoding='utf-8')):
                if (a.get('draft') and not preview) or a['slug'] in seen:
                    continue
                seen.add(a['slug'])
                out.append(a)
    return out


def tx(d):
    """{lang: text} -> (english, translations for Collector.tt)."""
    out = {l: v for l, v in d.items() if l != 'en' and v}
    if 'zh-CN' in out and 'zh-TW' not in out:
        out['zh-TW'] = _cc(out['zh-CN'])
    return d['en'], out


def project_names():
    idx = os.path.join(HERE, 'project_index.json')
    try:
        return {p['slug']: p['name'] for p in json.load(open(idx, encoding='utf-8'))}
    except (OSError, ValueError):
        return {}


CSS = """
.pa-proj{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;background:#1d1b4f;color:#fff;border-radius:14px;padding:20px 24px;margin:26px 0}
.pa-proj b{font-family:'Playfair Display',serif;font-size:20px;display:block} .pa-proj small{opacity:.8;font-size:13px}
.pa-proj a{background:#fff;color:#1d1b4f;padding:11px 20px;border-radius:100px;font-size:13px;font-weight:700;white-space:nowrap}
.pa-src{font-size:13px;color:var(--grey);margin-top:18px} .pa-src a{text-decoration:underline}
"""


def page(a, names, others):
    c = NP.I.Collector()
    t = lambda d, tag='span': c.tt(*tx(d), tag=tag)
    name = names.get(a['project'], a['project'])
    title = a['title']['en']
    url = '%s/article/%s.html' % (SITE, a['slug'])
    secs = ''.join('<h2>%s</h2>%s' % (t(s['h2']), ''.join('<p>%s</p>' % t(p) for p in s['paragraphs'])) for s in a['sections'])
    stats = ''.join('<div class="art-stat"><b>%s</b>%s</div>' % (E(s['value']), t(s['label'])) for s in a.get('stats', []))
    src = ''
    if a.get('sources'):
        src = '<p class="pa-src">%s %s</p>' % (c.tt('Sources:', {'zh-CN': '资料来源：', 'zh-TW': '資料來源：', 'ms': 'Sumber:', 'ja': '出典：', 'ko': '출처:'}),
                                              ' · '.join('<a href="%s" target="_blank" rel="noopener">%s</a>' % (E(s['url']), E(s['name'])) for s in a['sources']))
    proj = ('<div class="pa-proj"><div><b>%s</b><small>%s</small></div><a href="../property/%s.html">%s</a></div>') % (
        E(name), c.tt('Prices, layouts, location and FAQ', {'zh-CN': '价格、户型、地点和常见问题', 'zh-TW': '價格、戶型、地點和常見問題', 'ms': 'Harga, susun atur, lokasi dan soalan lazim', 'ja': '価格、間取り、立地、よくある質問', 'ko': '가격, 타입, 위치, 자주 묻는 질문'}),
        a['project'], c.tt('View project →', {'zh-CN': '查看项目 →', 'zh-TW': '查看項目 →', 'ms': 'Lihat projek →', 'ja': 'プロジェクトを見る →', 'ko': '프로젝트 보기 →'}))
    more = ''.join('<a class="acard" href="%s.html"><small>%s</small><h3>%s</h3><p>%s</p><span>%s</span></a>' % (
        o['slug'], t(o['cat']), t(o['title']), t(o['intro']), c.tt('Read article →')) for o in others)
    iso = NP.iso(a['date'])
    h1 = t(a['title'])   # registered first, so the breadcrumb shows the translated title too
    body = """
  {crumbs}
  <div class="art-hero" style="background:linear-gradient(135deg,#1d1b4f,#5E60CE);"><span class="art-cat">{cat}</span><h1>{h1}</h1><time datetime="{iso}"><span data-date="{iso}">{date}</span> · Keith Nah</time></div>
  <div class="art-wrap">
    <article class="art-body">
      <p class="lead">{intro}</p>
      {secs}
      {stats}
      <div class="art-take"><strong>{l_take}</strong>{take}</div>
      {proj}
      {src}
    </article>
    <aside class="art-side">
      <div class="side-box"><h3>{l_talk}</h3><p>{l_q}</p><a class="wa-btn" href="{wa}" target="_blank" rel="noopener">{l_wa}</a></div>
    </aside>
  </div>
  {more}""".format(
        crumbs=NP.crumbs(c, ('../property/%s.html' % a['project'], name), ('', title)), cat=t(a['cat']), h1=h1, iso=iso, date=E(a['date']),
        intro=t(a['intro']), secs=secs, stats=('<div class="art-stats">%s</div>' % stats) if stats else '',
        l_take=c.tt("Keith's take", {'zh-CN': 'Keith 怎么看', 'zh-TW': 'Keith 怎麼看', 'ms': 'Pandangan Keith', 'ja': 'Keith の見方', 'ko': 'Keith의 생각'}), take=t(a['takeaway']), proj=proj, src=src,
        l_talk=c.tt('Talk to Keith'), l_q=c.tt('Questions about this topic or a project? Keith replies on WhatsApp.'), l_wa=c.tt('WhatsApp Keith'),
        wa=E(NP.wa('Hi Keith, I read "%s" on your website and have a question.' % title)),
        more=('<section class="blk"><h2>%s</h2><div class="acards">%s</div></section>' % (
            c.tt('More about %s' % name, {'zh-CN': '更多关于 %s' % name, 'zh-TW': '更多關於 %s' % name, 'ms': 'Lagi tentang %s' % name, 'ja': '%s の関連記事' % name, 'ko': '%s 관련 기사 더 보기' % name}), more)) if more else '')
    ld = [{'@context': 'https://schema.org', '@type': 'Article', 'headline': title, 'datePublished': iso, 'dateModified': iso,
           'author': {'@type': 'Person', 'name': 'Keith Nah', 'url': SITE + '/about-keith.html'},
           'publisher': {'@type': 'Organization', 'name': 'Keith Nah Real Estate', 'url': SITE + '/', 'logo': {'@type': 'ImageObject', 'url': SITE + '/apple-touch-icon.png'}},
           'description': NP.excerpt(a['intro']['en'], 300), 'mainEntityOfPage': url, 'about': {'@type': 'Residence', 'name': name, 'url': '%s/property/%s.html' % (SITE, a['project'])}},
          {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
              {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
              {'@type': 'ListItem', 'position': 2, 'name': name, 'item': '%s/property/%s.html' % (SITE, a['project'])},
              {'@type': 'ListItem', 'position': 3, 'name': title, 'item': url}]}]
    out = NP.shell(c, '%s | Keith Nah' % title, NP.excerpt(a['intro']['en'], 158), url, body, ld,
                   msg='Hi Keith, I read "%s" on your website and have a question.' % title)
    return out.replace('</style>', CSS + '</style>', 1)


def main():
    arts = load()
    names = project_names()
    os.makedirs('article', exist_ok=True)
    for a in arts:
        others = [o for o in arts if o['project'] == a['project'] and o['slug'] != a['slug']]
        open('article/%s.html' % a['slug'], 'w', encoding='utf-8').write(page(a, names, others))
    print('project articles: %d' % len(arts))


if __name__ == '__main__':
    main()
