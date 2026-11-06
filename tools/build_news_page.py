"""Build the News page (blog.html) sections: Buying Guide, FAQ and Blog topics.

Content lives in tools/news_content.py. The FAQ questions and answers,
with their translations, are taken from the Home page (index.html), so
both pages stay the same. Run from the repository root:
    python3 tools/build_news_page.py
Safe to run again: the generated blocks sit between KN-NEWS markers and
are replaced on every run.
"""
import html
import json
import re
from urllib.parse import quote_plus

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from news_content import AS_AT, GUIDES, LABELS, TOPICS
from news_pages import ART_SLUGS, write_pages

LANGS = ['zh-CN', 'zh-TW', 'ms', 'ta', 'ja', 'ko', 'ar']
PAGE = 'blog.html'


def T(s):
    """Text as the browser serialises it in innerHTML (so translation keys match)."""
    return html.escape(html.unescape(s), quote=False)


def A(s):
    return html.escape(html.unescape(s), quote=True)


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower().replace('&', 'and')).strip('-')


def wa(msg):
    return 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0' % quote_plus('(KNRE) ' + msg)


TR = {}


def unit(make):
    """Register a translatable block: make(label) returns its inner HTML."""
    en = make(lambda s: s)
    tr = {}
    for l in LANGS:
        tr[l] = make(lambda s, l=l: LABELS.get(s, {}).get(l, s))
    if any(tr[l] != en for l in LANGS):
        TR[en] = tr
    return en


def L(s):
    return T(s)


# ---------- FAQ from the Home page ----------
index = open('index.html', encoding='utf-8').read()
FAQ = []
for n, q, a in re.findall(r'data-i18n="faq_q(\d+)">(.*?)<span class="faq-icon">.*?<p data-i18n="faq_a\1">(.*?)</p>', index, re.S):
    def tr_of(key):
        i = index.find('"%s":' % key)
        if i < 0:
            return {}
        obj, _ = json.JSONDecoder().raw_decode(index[index.index('{', i):])
        return obj
    FAQ.append((T(q.strip()), T(a.strip()), tr_of('faq_q' + n), tr_of('faq_a' + n)))
assert len(FAQ) >= 30, len(FAQ)

# ---------- HTML ----------
ICONS = {
    'new-property': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 21V9l8-6 8 6v12"/><path d="M9 21v-6h6v6"/><path d="M15 3h3v4"/></svg>',
    'subsale': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><circle cx="12" cy="14" r="2"/><path d="M12 16v3"/></svg>',
    'foreign-buyers': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/></svg>',
}
WA_SVG = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2.05 22l5.25-1.38c1.44.79 3.06 1.2 4.72 1.2h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.87 9.87 0 0012.04 2z"/></svg>'


def guides_html():
    tabs = ''.join(
        '<button type="button" class="bg-tab%s" role="tab" aria-selected="%s" data-guide="%s">%s%s</button>' % (
            ' active' if k == 0 else '', 'true' if k == 0 else 'false', g['id'],
            '<span class="bg-tab-icon" aria-hidden="true">%s</span>' % ICONS[g['id']],
            '<span class="bg-tab-title">%s</span><span class="bg-tab-sub">%s</span>' % (unit(lambda t, g=g: L(t(g['tab']))), unit(lambda t, g=g: L(t(g['tab_sub'])))))
        for k, g in enumerate(GUIDES))
    panels = ''
    for k, g in enumerate(GUIDES):
        rows = ''.join('<tr><th scope="row">%s</th><td>%s</td></tr>' % (T(a), T(b)) for a, b in g['numbers'])
        steps = ''.join('<li><a href="#%s-stage-%d"><b>%d</b><span>%s</span></a></li>' % (g['id'], n + 1, n + 1, T(s[0])) for n, s in enumerate(g['stages']))
        stages = ''.join(
            '<article class="bg-stage" id="%s-stage-%d"><div class="bg-stage-num">Stage %d</div><h4>%s</h4><ul>%s</ul></article>' % (
                g['id'], n + 1, n + 1, T(s[0]), ''.join('<li>%s</li>' % T(x) for x in s[1]))
            for n, s in enumerate(g['stages']))
        faqs = ''.join('<details class="bg-faq"><summary>%s</summary><p>%s</p></details>' % (T(q), T(a)) for q, a in g['faq'])
        panels += '''
    <div class="bg-panel" id="%(id)s" role="tabpanel"%(hidden)s data-no-currency>
      <h3 class="bg-h3">%(title)s</h3>
      <div class="bg-top">
        <div class="bg-short"><p class="bg-label">%(l_short)s</p><p>%(short)s</p></div>
        <div class="bg-numbers"><p class="bg-label">%(l_numbers)s</p><table>%(rows)s</table></div>
      </div>
      <p class="bg-label">%(l_stages)s</p>
      <ol class="bg-steps">%(steps)s</ol>
      <div class="bg-stages">%(stages)s</div>
      <p class="bg-label">%(l_faq)s</p>
      <div class="bg-faqs">%(faqs)s</div>
      <div class="bg-cta"><p>%(l_cta)s</p><a class="bg-wa wa-link" href="%(wa)s" target="_blank" rel="noopener">%(wasvg)s<span>%(l_wa)s</span></a></div>
      <p class="bg-note">Figures as at %(asat)s. Rules and rates change; confirm the details for your purchase with Keith or your lawyer before you commit.</p>
    </div>''' % dict(id=g['id'], hidden='' if k == 0 else ' hidden', title=T(g['title']), short=T(g['short']), rows=rows, steps=steps,
                     stages=stages, faqs=faqs, wa=A(wa('Hi Keith, I have a question about %s.' % g['tab'].lower())), wasvg=WA_SVG, asat=AS_AT,
                     l_short=unit(lambda t: L(t('Short answer'))), l_numbers=unit(lambda t: L(t('Key numbers at a glance'))),
                     l_stages=unit(lambda t: L(t('Six stages, start to finish'))), l_faq=unit(lambda t: L(t('Questions buyers ask'))),
                     l_cta=unit(lambda t: L(t('Stuck on a step? Ask Keith directly.'))), l_wa=L('WhatsApp Keith'))
    return '''
<section class="nw-sec bg-sec" id="buying-guide">
  <p class="nw-eyebrow">%s</p>
  <h2 class="nw-h2">%s</h2>
  <p class="nw-sub">%s</p>
  <div class="bg-tabs" role="tablist">%s</div>%s
</section>''' % (unit(lambda t: L(t('Buying Guide'))), unit(lambda t: L(t('Buying property in Malaysia, step by step.'))),
                 unit(lambda t: L(t('Pick the guide that matches your purchase. Each one covers the key numbers, the six stages and the questions buyers ask most.'))),
                 tabs, panels)


def faq_html():
    items = ''
    for n, (q, a, tq, ta) in enumerate(FAQ):
        qh = '<span>%s</span><i aria-hidden="true">+</i>' % q
        if tq:
            TR[qh] = {l: '<span>%s</span><i aria-hidden="true">+</i>' % T(tq[l]) for l in LANGS if l in tq}
        if ta:
            TR[a] = {l: T(ta[l]) for l in LANGS if l in ta}
        items += '<div class="nf-item%s"><button type="button" class="nf-q" aria-expanded="false">%s</button><div class="nf-a"><p>%s</p></div></div>' % (
            ' nf-more' if n >= 12 else '', qh, a)
    return '''
<section class="nw-sec nf-sec" id="faq" data-no-currency>
  <p class="nw-eyebrow">%s</p>
  <h2 class="nw-h2">%s</h2>
  <p class="nw-sub">%s</p>
  <div class="nf-list" id="nfList">%s</div>
  <div class="nf-btns"><button type="button" class="nf-toggle" id="nfAll">%s</button><button type="button" class="nf-toggle" id="nfFew" hidden>%s</button></div>
</section>''' % (unit(lambda t: L(t('FAQ'))), unit(lambda t: L(t('Common Questions'))), unit(lambda t: L(t('Answers to what buyers ask Keith most often.'))),
                 items, unit(lambda t: L(t('Show all questions'))),
                 unit(lambda t: L(t('Show fewer questions'))))


def blog_html(counts):
    chips = unit(lambda t: ''.join('<a class="bt-chip" href="topic/%s.html">%s<em>%d</em></a>' % (slug(tp[0]), L(t(tp[0])), counts[tp[0]]) for tp in TOPICS))
    return '''
<section class="nw-sec bt-sec" id="blog">
  <p class="nw-eyebrow">%s</p>
  <h2 class="nw-h2">%s</h2>
  <p class="bt-label">%s</p>
  <div class="bt-chips" id="btChips">%s</div>
</section>''' % (unit(lambda t: L(t('Blog'))), unit(lambda t: L(t('Latest Property News & Insights'))), unit(lambda t: L(t('Filter by topic'))), chips)


QUICKNAV = '<nav class="nw-jump" aria-label="On this page"><a href="#buying-guide">%s</a><a href="#faq">%s</a><a href="#blog">%s</a></nav>'

CSS = r'''
  /* KN-NEWS:CSS:START */
  .nw-jump{display:flex;justify-content:center;gap:16px;flex-wrap:wrap;margin-top:34px;}
  .nw-jump-btn{display:flex;align-items:center;gap:14px;min-width:230px;padding:14px 18px 14px 14px;border-radius:14px;background:var(--gold);color:#fff;text-align:left;box-shadow:0 12px 28px rgba(94,96,206,0.28);transition:transform .3s var(--ease),box-shadow .3s var(--ease),background .3s;}
  .nw-jump-btn:hover{transform:translateY(-3px);background:#4B4DB8;box-shadow:0 18px 34px rgba(94,96,206,0.38);}
  .nw-jump-ic{flex:0 0 44px;height:44px;border-radius:12px;background:rgba(255,255,255,0.16);display:flex;align-items:center;justify-content:center;}
  .nw-jump-ic svg{width:22px;height:22px;}
  .nw-jump-txt{display:flex;flex-direction:column;flex:1;line-height:1.25;}
  .nw-jump-txt b{font:700 16px 'Inter',sans-serif;}
  .nw-jump-txt small{font:500 12.5px 'Inter',sans-serif;color:rgba(255,255,255,0.78);margin-top:3px;}
  .nw-jump-arrow{font-size:18px;opacity:.85;transition:transform .3s var(--ease);}
  .nw-jump-btn:hover .nw-jump-arrow{transform:translateY(3px);}
  @media(max-width:760px){ .nw-jump{gap:10px;} .nw-jump-btn{min-width:0;width:100%;max-width:360px;} }
  .bt-label{font:700 11px 'Inter',sans-serif;letter-spacing:0.16em;text-transform:uppercase;color:var(--grey);margin:18px 0 0;}
  .nw-sec{max-width:1240px;margin:0 auto;padding:70px 5vw 10px;scroll-margin-top:80px;}
  .nw-eyebrow{font:600 11px 'Inter',sans-serif;letter-spacing:0.28em;text-transform:uppercase;color:var(--gold);margin-bottom:10px;}
  .nw-h2{font-size:clamp(28px,3.4vw,40px);line-height:1.18;margin-bottom:10px;}
  .nw-sub{color:var(--grey);font-size:15px;font-weight:500;max-width:720px;margin-bottom:28px;}
  .bg-tabs{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:26px;}
  .bg-tab{display:grid;grid-template-columns:44px 1fr;grid-template-rows:auto auto;column-gap:14px;align-items:center;text-align:left;padding:18px 20px;border-radius:12px;border:1px solid var(--line);background:#fff;cursor:pointer;font-family:inherit;transition:all .3s var(--ease);}
  .bg-tab:hover{border-color:var(--gold);}
  .bg-tab.active{background:var(--gold);border-color:var(--gold);box-shadow:0 14px 30px rgba(94,96,206,0.25);}
  .bg-tab-icon{grid-row:1/3;width:44px;height:44px;border-radius:50%;background:#EEEEFB;color:var(--gold);display:flex;align-items:center;justify-content:center;}
  .bg-tab-icon svg{width:22px;height:22px;}
  .bg-tab-title{font:700 16px 'Inter',sans-serif;color:var(--ink);}
  .bg-tab-sub{font-size:12.5px;color:var(--grey);font-weight:500;line-height:1.4;}
  .bg-tab.active .bg-tab-title,.bg-tab.active .bg-tab-sub{color:#fff;}
  .bg-tab.active .bg-tab-icon{background:rgba(255,255,255,0.18);color:#fff;}
  .bg-panel{background:#fff;border:1px solid var(--line);border-radius:14px;padding:34px 34px 26px;}
  .bg-h3{font-size:clamp(22px,2.6vw,30px);margin-bottom:22px;}
  .bg-label{font:700 11px 'Inter',sans-serif;letter-spacing:0.16em;text-transform:uppercase;color:var(--gold);margin:6px 0 12px;}
  .bg-top{display:grid;grid-template-columns:minmax(0,0.9fr) minmax(0,1.1fr);gap:26px;margin-bottom:30px;}
  .bg-short{background:#EEEEFB;border-radius:10px;padding:22px 24px;}
  .bg-short p:last-child{font-size:15.5px;line-height:1.7;color:#1d1d3a;font-weight:500;}
  .bg-numbers table{width:100%;border-collapse:collapse;font-size:13.5px;}
  .bg-numbers th,.bg-numbers td{text-align:left;vertical-align:top;padding:10px 12px;border-bottom:1px solid var(--line);}
  .bg-numbers th{width:38%;font-weight:700;color:var(--ink);}
  .bg-numbers td{color:#333;font-weight:500;}
  .bg-steps{list-style:none;display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-bottom:18px;counter-reset:none;}
  .bg-steps a{display:flex;flex-direction:column;gap:6px;padding:12px;border-radius:10px;background:var(--bg);border:1px solid var(--line);height:100%;font-size:12.5px;font-weight:600;color:var(--ink);}
  .bg-steps a:hover{border-color:var(--gold);}
  .bg-steps b{width:26px;height:26px;border-radius:50%;background:var(--gold);color:#fff;display:flex;align-items:center;justify-content:center;font-size:12px;}
  .bg-stages{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-bottom:30px;}
  .bg-stage{border:1px solid var(--line);border-top:3px solid var(--gold);border-radius:10px;padding:18px 20px;scroll-margin-top:90px;}
  .bg-stage-num{font:700 11px 'Inter',sans-serif;letter-spacing:0.14em;text-transform:uppercase;color:var(--gold);margin-bottom:4px;}
  .bg-stage h4{font-size:18px;margin-bottom:10px;}
  .bg-stage ul{margin-left:18px;} .bg-stage li{font-size:14px;color:#333;font-weight:500;margin-bottom:7px;line-height:1.55;}
  .bg-faqs{margin-bottom:26px;}
  .bg-faq{border-bottom:1px solid var(--line);}
  .bg-faq summary{cursor:pointer;list-style:none;padding:14px 30px 14px 0;font-weight:700;font-size:15px;position:relative;}
  .bg-faq summary::-webkit-details-marker{display:none;}
  .bg-faq summary::after{content:'+';position:absolute;right:4px;top:12px;font-size:20px;color:var(--gold);}
  .bg-faq[open] summary::after{content:'\2212';}
  .bg-faq p{padding:0 0 16px;color:#333;font-size:14.5px;font-weight:500;line-height:1.65;}
  .bg-cta{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;background:#111;color:#fff;border-radius:12px;padding:20px 24px;}
  .bg-cta p{font-family:'Playfair Display',serif;font-size:20px;}
  .bg-wa{display:inline-flex;align-items:center;gap:8px;background:#25D366;color:#fff;padding:12px 22px;border-radius:100px;font-size:13px;font-weight:600;}
  .bg-note{margin-top:14px;font-size:12px;color:var(--grey);font-weight:500;}
  .nf-list{columns:2;column-gap:36px;}
  .nf-item{border-bottom:1px solid var(--line);break-inside:avoid;-webkit-column-break-inside:avoid;}
  .nf-sec:not(.nf-open) .nf-more{display:none;}
  .nf-q{width:100%;display:flex;justify-content:space-between;align-items:flex-start;gap:16px;text-align:left;background:none;border:0;padding:16px 0;cursor:pointer;font:700 15px 'Inter',sans-serif;color:var(--ink);}
  .nf-q i{font-style:normal;color:var(--gold);font-size:20px;line-height:1;transition:transform .25s;}
  .nf-item.open .nf-q i{transform:rotate(45deg);}
  .nf-a{display:none;padding:0 0 16px;} .nf-item.open .nf-a{display:block;}
  .nf-a p{color:#333;font-size:14.5px;font-weight:500;line-height:1.65;}
  .nf-btns{text-align:center;margin-top:24px;}
  .nf-toggle{font:600 13px 'Inter',sans-serif;padding:12px 26px;border-radius:100px;border:1px solid #111;background:transparent;color:#111;cursor:pointer;}
  .nf-toggle:hover{background:#111;color:#fff;}
  .bt-sec{padding-bottom:0;}
  .bt-chips{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px;}
  .bt-chip{display:inline-flex;align-items:center;gap:10px;font:600 14.5px 'Inter',sans-serif;color:var(--ink);background:#EFE7DA;border:1px solid transparent;border-radius:6px;padding:12px 16px;cursor:pointer;transition:all .25s var(--ease);}
  .bt-chip em{font-style:normal;font-size:12px;font-weight:700;color:#6b6257;}
  .bt-chip:hover{border-color:#111;}
  a.article-read{color:inherit;}
  .bt-chip.active{background:#111;color:#fff;} .bt-chip.active em{color:rgba(255,255,255,0.7);}
  .bt-all{background:#fff;border-color:var(--line);}
  .journal-grid{padding-top:36px;}
  @media(max-width:900px){
    .bg-tabs{grid-template-columns:1fr;}
    .bg-top{grid-template-columns:1fr;}
    .bg-steps{grid-template-columns:repeat(3,1fr);}
    .bg-stages{grid-template-columns:1fr;}
    .nf-list{columns:1;}
    .bg-panel{padding:24px 18px 20px;}
    .nw-sec{padding:50px 16px 6px;}
  }
  @media(max-width:480px){ .bg-steps{grid-template-columns:repeat(2,1fr);} .bt-chip{font-size:13.5px;padding:10px 13px;} }
  /* KN-NEWS:CSS:END */
'''

JS = r'''<!-- KN-NEWS:JS:START -->
<script>
/* News page sections: buying guide tabs, FAQ, blog topics */
(function(){
  if(window.KN_TR_PAGE) Object.assign(window.KN_TR_PAGE, __TR__);
  // Buying guide tabs
  var tabs = document.querySelectorAll('.bg-tab');
  function showGuide(id, scroll){
    var ok = false;
    tabs.forEach(function(t){ var on = t.getAttribute('data-guide') === id; t.classList.toggle('active', on); t.setAttribute('aria-selected', on ? 'true' : 'false'); if(on) ok = true; });
    if(!ok) return false;
    document.querySelectorAll('.bg-panel').forEach(function(p){ p.hidden = p.id !== id; });
    if(scroll) document.getElementById('buying-guide').scrollIntoView({behavior:'smooth', block:'start'});
    return true;
  }
  tabs.forEach(function(t){ t.addEventListener('click', function(){ showGuide(t.getAttribute('data-guide')); try{ history.replaceState(null, '', '#' + t.getAttribute('data-guide')); }catch(e){} }); });
  function fromHash(){
    var h = (location.hash || '').replace('#', ''), stage = h.match(/^(.+)-stage-\d+$/);
    if(h && (showGuide(h, true) || (stage && showGuide(stage[1])))){ if(stage) setTimeout(function(){ var el = document.getElementById(h); if(el) el.scrollIntoView({block:'start'}); }, 50); }
  }
  fromHash(); window.addEventListener('hashchange', fromHash);
  // FAQ
  document.querySelectorAll('.nf-q').forEach(function(q){
    q.addEventListener('click', function(){ var it = q.parentNode, open = !it.classList.contains('open'); it.classList.toggle('open', open); q.setAttribute('aria-expanded', open ? 'true' : 'false'); });
  });
  var sec = document.getElementById('faq'), all = document.getElementById('nfAll'), few = document.getElementById('nfFew');
  if(all && few){
    all.addEventListener('click', function(){ sec.classList.add('nf-open'); all.hidden = true; few.hidden = false; });
    few.addEventListener('click', function(){ sec.classList.remove('nf-open'); all.hidden = false; few.hidden = true; sec.scrollIntoView({behavior:'smooth', block:'start'}); });
  }
  // Articles open their own page (blog.html?article=a1 links keep working)
  var SLUGS = __ART_SLUGS__;
  window.openArticle = function(id){ if(SLUGS[id]) location.href = 'article/' + SLUGS[id] + '.html'; };
  try{ var q = new URLSearchParams(location.search).get('article'); if(q && SLUGS[q]) location.replace('article/' + SLUGS[q] + '.html'); }catch(e){}
  if(typeof knApplyContent === 'function') knApplyContent();
})();
</script>
<!-- KN-NEWS:JS:END -->
'''


def build():
    t = open(PAGE, encoding='utf-8').read()

    # Blog topics on each article card
    counts = {tp[0]: len(tp[1]) for tp in TOPICS}
    by_article = {}
    for tp in TOPICS:
        for a in tp[1]:
            by_article.setdefault(a, []).append(slug(tp[0]))

    def card(m):
        aid = m.group(2)
        s = re.sub(r' data-topics="[^"]*"', '', m.group(0))
        return s.replace('data-id="%s"' % aid, 'data-id="%s" data-topics="%s"' % (aid, ' '.join(by_article.get(aid, []))), 1)
    t, n = re.subn(r'<div class="article-card" data-cat="([^"]+)" data-id="(a\d+)"(?: data-topics="[^"]*")?', card, t)
    assert n >= 31, n

    def read_link(m):
        aid = m.group(1)
        return re.sub(r'<(?:span|a) class="article-read"[^>]*>Read Article →</(?:span|a)>',
                      '<a class="article-read" href="article/%s.html">Read Article →</a>' % ART_SLUGS[aid], m.group(0), count=1)
    t, n = re.subn(r'data-id="(a\d+)"[^>]*onclick="openArticle\(\'\1\'\)">.*?class="article-read"[^>]*>Read Article →</(?:span|a)>', read_link, t, flags=re.S)
    assert n >= 31, n

    # Sections (replace the old filter bar on the first run)
    TR.clear()
    block = ('<!-- KN-NEWS:SECTIONS:START -->' + guides_html() + faq_html() + blog_html(counts) +
             '\n<div class="filters" id="filters" hidden></div>\n<!-- KN-NEWS:SECTIONS:END -->')
    if '<!-- KN-NEWS:SECTIONS:START -->' in t:
        t = re.sub(r'<!-- KN-NEWS:SECTIONS:START -->.*?<!-- KN-NEWS:SECTIONS:END -->', lambda _: block, t, flags=re.S)
    else:
        t, n = re.subn(r'<!-- =+ FILTERS =+ -->\s*<div class="filters" id="filters">.*?</div>', lambda _: block, t, count=1, flags=re.S)
        assert n == 1, 'filter bar not found'

    # Quick links under the hero
    ic = {
        'g': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 21V9l8-6 8 6v12"/><path d="M9 21v-6h6v6"/></svg>',
        'f': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 015 .5c0 1.7-2.5 2-2.5 3.5"/><circle cx="12" cy="17" r=".6" fill="currentColor"/></svg>',
        'b': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 9h8M8 13h8M8 17h5"/></svg>'}
    def jump(href, key, title, sub):
        return ('<a class="nw-jump-btn" href="#%s"><span class="nw-jump-ic" aria-hidden="true">%s</span>'
                '<span class="nw-jump-txt">%s</span><span class="nw-jump-arrow" aria-hidden="true">&darr;</span></a>' % (
                    href, ic[key], unit(lambda t_: '<b>%s</b><small>%s</small>' % (L(t_(title)), L(t_(sub))))))
    qn = '<nav class="nw-jump" aria-label="On this page">%s%s%s</nav>' % (
        jump('buying-guide', 'g', 'Buying Guide', 'Step-by-step guides'),
        jump('faq', 'f', 'FAQ', '%d answers' % len(FAQ)),
        jump('blog', 'b', 'Blog', 'Articles by topic'))
    t = re.sub(r'\s*<nav class="nw-jump".*?</nav>', '', t, flags=re.S)
    i = t.index('<section class="journal-hero">')
    j = t.index('</section>', i)
    t = t[:j] + '  ' + qn + '\n' + t[j:]

    # CSS and JS
    t = re.sub(r'\s*/\* KN-NEWS:CSS:START \*/.*?/\* KN-NEWS:CSS:END \*/\n', '\n', t, flags=re.S)
    t = t.replace('</style>', CSS + '</style>', 1)
    t = re.sub(r'<!-- KN-NEWS:JS:START -->.*?<!-- KN-NEWS:JS:END -->\n', '', t, flags=re.S)
    js = JS.replace('__TR__', json.dumps(TR, ensure_ascii=False).replace('</', '<\\/')).replace('__TOPICS__', json.dumps([slug(tp[0]) for tp in TOPICS])).replace('__ART_SLUGS__', json.dumps(ART_SLUGS))
    t = t.replace('<script src="lead-tracker.js"></script>', js + '<script src="lead-tracker.js"></script>', 1)

    # Let the generated script add translations to the page's private TR table
    if 'window.KN_TR_PAGE = TR;' not in t:
        k = t.index('const TR = ') + len('const TR = ')
        _, n_end = json.JSONDecoder().raw_decode(t[k:])
        e = k + n_end
        assert t[e] == ';', t[e:e + 5]
        t = t[:e + 1] + ' window.KN_TR_PAGE = TR;' + t[e + 1:]

    # Keep legal figures in the guides and FAQ in Ringgit when the visitor switches currency
    old = "if(p.closest && p.closest('#currMenu,#currSwitch')) return NodeFilter.FILTER_REJECT;"
    if old in t:
        t = t.replace(old, "if(p.closest && p.closest('#currMenu,#currSwitch,[data-no-currency]')) return NodeFilter.FILTER_REJECT;")
    assert '[data-no-currency]' in t

    open(PAGE, 'w', encoding='utf-8').write(t)
    print('News page built: %d guides, %d FAQ, %d topics, %d translated blocks' % (len(GUIDES), len(FAQ), len(TOPICS), len(TR)))
    return t


def fix_stamp_duty_article():
    """Article a19 said foreigners pay no extra stamp duty; since 1 Jan 2026 they pay a flat 8%."""
    t = open(PAGE, encoding='utf-8').read()
    i = t.index('const ARTICLES =') + len('const ARTICLES =')
    while t[i] == ' ':
        i += 1
    arts, end = json.JSONDecoder().raw_decode(t[i:])
    a = arts['a19']
    p0 = a['sections'][0]['paragraphs'][0]
    if 'surcharge' in p0:
        a['sections'][0]['paragraphs'][0] = (
            "Stamp duty on the transfer depends on who is buying. Malaysian citizens and permanent residents pay a "
            "tiered scale: 1% on the first RM100,000, 2% on the next RM400,000, 3% on the next RM500,000 and 4% on "
            "anything above RM1 million. Foreign buyers pay a flat 8% on residential property transferred from "
            "1 January 2026, so on a prime KL unit the difference runs to tens of thousands of ringgit.")
        a['stats'] = [
            {'value': '8% Flat', 'label': 'Stamp duty for foreign buyers on residential property from 1 Jan 2026'},
            {'value': '1% to 4%', 'label': 'Tiered rates for Malaysians and PRs'},
            {'value': 'State Fees', 'label': 'Consent charges vary by state'}]
        print('Corrected article a19 (foreign buyer stamp duty)')
    # a6 and a9 said Malaysia has no surcharge for foreign buyers
    a6, a9 = arts['a6'], arts['a9']
    if 'has no direct equivalent for Singaporeans buying in Malaysia' in a6['sections'][0]['paragraphs'][1]:
        a6['sections'][0]['paragraphs'][1] = (
            "Singapore's Additional Buyer's Stamp Duty (ABSD) adds a significant surcharge on second and subsequent "
            "purchases for Singaporean citizens, and an even steeper one for foreigners buying in Singapore. Malaysia "
            "has no ABSD. Singaporeans buying here pay Malaysia's foreign-buyer stamp duty, a flat 8% on residential "
            "property from 1 January 2026, which is still far below Singapore's surcharges, so a Malaysian second "
            "property remains much cheaper to acquire than a second property back home.")
        a6['stats'][1] = {'value': '8% Flat', 'label': "Malaysia's foreign-buyer stamp duty, with no ABSD"}
        a6['takeaway'] = a6['takeaway'].replace(
            'and none of the additional stamp duty surcharges that make a second property back home expensive',
            "and a flat 8% stamp duty instead of the ABSD that makes a second property back home expensive")
        print('Corrected article a6 (stamp duty for Singaporean buyers)')
    p = a9['sections'][1]['paragraphs'][0]
    if 'Malaysia has no direct equivalent surcharge for foreign buyers' in p:
        a9['sections'][1]['paragraphs'][0] = p.replace(
            'Malaysia has no direct equivalent surcharge for foreign buyers, though state consent fees and minimum purchase thresholds still apply and vary by state.',
            'Malaysia has no ABSD, but foreign buyers pay a flat 8% stamp duty on residential property from 1 January 2026 (Malaysians pay 1% to 4%), and state consent fees and minimum purchase thresholds still apply and vary by state.')
        a9['stats'][2] = {'value': '8% Flat', 'label': 'Stamp duty for foreign buyers in Malaysia (no ABSD)'}
        print('Corrected article a9 (stamp duty comparison)')
    new = json.dumps(arts, ensure_ascii=False)
    if new != t[i:i + end]:
        t = t[:i] + new + t[i + end:]
        open(PAGE, 'w', encoding='utf-8').write(t)


if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    fix_stamp_duty_article()
    build()
    write_pages()
