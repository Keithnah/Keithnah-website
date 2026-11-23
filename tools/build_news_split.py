"""Split the News page into a hub and three landing pages.

blog.html (News) keeps the hero at the top, a row of section buttons, Keith's Market Notes and a short
preview of each section. The full sections get their own pages:
    buying-guide.html   Buying Guide (new property, subsale, foreign buyers)
    faq.html            Common questions
    articles.html       Blog: every article with the topic filter
Market Data (market-data.html) and Market Notes (market-notes.html) already have their own pages.

Runs after build_news_page.py, build_market_notes.py and build_data.py, which rebuild the full blog.html
sections on every run, so this script always starts from the full page. Translations: the pages are
copies of blog.html, so they keep its translation scripts; tools/build_lang_pages.js makes the language copies.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(HERE))
SITE = 'https://keithnah.com/'

t = open('blog.html', encoding='utf-8').read()
if '<!-- KN-NWHUB -->' in t:
    raise SystemExit('news split: blog.html is already the hub; run build_news_page.py first')
open(os.path.join(HERE, 'news_full.html'), 'w', encoding='utf-8').write(t)   # the full page, restored at the start of the next build


def cut(start, end, s=None):
    s = t if s is None else s
    i = s.index(start)
    j = s.index(end, i) + (len(end) if end.startswith('<!-- KN-') and end.endswith(':END -->') else 0)
    return i, j


def sec(sid):
    m = re.search(r'<section class="nw-sec [a-z -]+"[^>]*\bid="%s"[^>]*>.*?\n</section>' % sid, t, re.S)
    return m.group(0)


# ---- pieces of the full page ----
ni, nj = cut('<!-- KN-NOTES:START -->', '<!-- KN-NOTES:END -->')
notes = t[ni:nj]
hi, hj = cut('<!-- ===================== JOURNAL HERO', '<!-- KN-NEWS:SECTIONS:START -->')
hero = t[hi:hj]
si, sj = cut('<!-- KN-NEWS:SECTIONS:START -->', '<!-- KN-NEWS:SECTIONS:END -->')
gi = t.index('<!-- ===================== ARTICLE GRID')
ui = t.index('<!-- ===================== SUBSCRIBE')
prefix, grid, suffix = t[:min(ni, hi)], t[gi:ui], t[ui:]
guide, faq, videos, blog = sec('buying-guide'), sec('faq'), sec('videos'), sec('blog')
SEC_CSS = ''.join(re.findall(r'<style>.*?</style>', re.sub(r'<!-- KN-ND:START -->.*?<!-- KN-ND:END -->', '', t[si:sj], flags=re.S), re.S))
m = re.search(r'<!-- KN-ND:START -->.*?<!-- KN-ND:END -->', t, re.S)
nd = m.group(0) if m else ''

# ---- section buttons: every button opens its own page ----
nav = re.search(r'<nav class="nw-jump".*?</nav>', hero, re.S).group(0)
NOTE_BTN = ('<a class="nw-jump-btn" href="market-notes.html"><span class="nw-jump-ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'
            '<path d="M5 4h11l3 3v13H5z"/><path d="M9 10h6M9 14h6M9 18h3"/></svg></span><span class="nw-jump-txt"><b><span data-nwh="mn">Market Notes</span></b>'
            '<small><span data-nwh="mn_s">Keith’s daily take</span></small></span><span class="nw-jump-arrow" aria-hidden="true">&rarr;</span></a>')
PAGES = {'#buying-guide': 'buying-guide.html', '#market-data': 'market-data.html', '#faq': 'faq.html', '#blog': 'articles.html'}


def nav_for(active, root=''):
    n = re.sub(r'(href="#blog">.*?<b>)Blog(</b>)', r'\1<span data-nwh="art">Articles</span>\2', nav, count=1, flags=re.S)
    for a, b in PAGES.items():
        n = n.replace('href="%s"' % a, 'href="%s%s"' % (root, b))
    n = n.replace('&darr;', '&rarr;').replace('<nav class="nw-jump" aria-label="On this page">',
                                              '<nav class="nw-jump nw-tabs" aria-label="News sections">' + NOTE_BTN, 1)
    if active:
        n = n.replace('<a class="nw-jump-btn" href="%s"' % active, '<a class="nw-jump-btn on" aria-current="page" href="%s"' % active, 1)
    return n


CSS = ('<style>'
       'nav.nw-jump.nw-tabs{display:grid!important;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px;max-width:1240px;margin:34px auto 0}'
       'nav.nw-tabs .nw-jump-btn{min-width:0!important;padding:14px 14px 14px 12px;gap:12px}nav.nw-tabs .nw-jump-txt{min-width:0}nav.nw-tabs .nw-jump-arrow{display:none}nav.nw-tabs .nw-jump-txt small{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.nw-tabs .nw-jump-btn.on{background:#1d1b4f;box-shadow:0 14px 30px rgba(29,27,79,.25)}'
       '.nw-tabs .nw-jump-txt b{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'
       '.journal-hero + #market-notes, .journal-hero ~ .mn{padding-top:56px}'
       '.nw-sub-hero{padding-bottom:38px}.nw-sub-hero h1{font-size:clamp(34px,5vw,58px)}.nw-back{display:inline-block;margin-bottom:14px;color:var(--gold);font-weight:700;font-size:14px}'
       '.nw-more{display:flex;justify-content:center;margin-top:26px}.nw-more a{display:inline-flex;align-items:center;gap:8px;background:#5E60CE;color:#fff;font-weight:700;'
       'padding:13px 26px;border-radius:100px;box-shadow:0 12px 26px rgba(94,96,206,.28);transition:transform .2s,box-shadow .2s}.nw-more a:hover{transform:translateY(-2px);box-shadow:0 16px 32px rgba(94,96,206,.36)}'
       '.nw-gcards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:24px}.nw-gcards a{display:block;background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px;'
       'transition:border-color .2s,box-shadow .2s}.nw-gcards a:hover{border-color:var(--gold);box-shadow:0 14px 30px rgba(29,27,79,.1)}.nw-gcards b{display:block;font:700 19px "Playfair Display",serif;margin:10px 0 6px}'
       '.nw-gcards small{color:var(--grey);font-size:14px;line-height:1.55;display:block}.nw-gcards em{display:inline-block;margin-top:12px;color:var(--gold);font-style:normal;font-weight:700;font-size:13.5px}'
       '.nw-gcards .ic{width:44px;height:44px;border-radius:12px;background:#eeedfb;display:flex;align-items:center;justify-content:center;color:#5E60CE}.nw-gcards .ic svg{width:24px;height:24px}'
       '@media(max-width:1100px){nav.nw-jump.nw-tabs{grid-template-columns:repeat(3,minmax(0,1fr))}}'
       '@media(max-width:760px){nav.nw-jump.nw-tabs{grid-template-columns:1fr 1fr;gap:10px}nav.nw-tabs .nw-jump-btn:last-child{grid-column:1/-1}.nw-gcards{grid-template-columns:1fr}}'
       '@media(max-width:420px){.nw-tabs .nw-jump-btn{padding:12px}.nw-tabs .nw-jump-ic{display:none}}'
       '</style>')
HUB_TX = ('<script>(function(){var T={"en":{"art":"Articles","mn":"Market Notes","mn_s":"Keith’s daily take","g_more":"Open the Buying Guide","f_more":"See all {n} answers","b_more":"See all {n} articles",'
          '"back":"← News","gn":"New property","gs":"Subsale","gf":"Foreign buyers","gn_p":"Buying from a developer: booking, SPA, loan and handover.",'
          '"gs_p":"Buying from an owner: offer, searches, loan and transfer.","gf_p":"The minimum price, state consent and the costs for foreigners.","open":"Read the guide →"},'
          '"zh-CN":{"art":"文章","mn":"每日市场短评","mn_s":"Keith 每日观点","g_more":"打开买房指南","f_more":"查看全部 {n} 个问答","b_more":"查看全部 {n} 篇文章","back":"← 新闻","gn":"新楼盘","gs":"二手房","gf":"外国买家",'
          '"gn_p":"向发展商购买：订房、买卖合约、贷款和交屋。","gs_p":"向屋主购买：出价、查册、贷款和过户。","gf_p":"最低价格、州政府批准和外国人的费用。","open":"阅读指南 →"},'
          '"zh-TW":{"art":"文章","mn":"每日市場短評","mn_s":"Keith 每日觀點","g_more":"打開買房指南","f_more":"查看全部 {n} 個問答","b_more":"查看全部 {n} 篇文章","back":"← 新聞","gn":"新樓盤","gs":"二手房","gf":"外國買家",'
          '"gn_p":"向發展商購買：訂房、買賣合約、貸款和交屋。","gs_p":"向屋主購買：出價、查冊、貸款和過戶。","gf_p":"最低價格、州政府批准和外國人的費用。","open":"閱讀指南 →"},'
          '"ms":{"art":"Artikel","mn":"Nota Pasaran","mn_s":"Pandangan harian Keith","g_more":"Buka Panduan Membeli","f_more":"Lihat kesemua {n} jawapan","b_more":"Lihat kesemua {n} artikel","back":"← Berita","gn":"Hartanah baharu","gs":"Subjualan","gf":"Pembeli asing",'
          '"gn_p":"Membeli daripada pemaju: tempahan, SPA, pinjaman dan serahan kunci.","gs_p":"Membeli daripada pemilik: tawaran, carian, pinjaman dan pindah milik.","gf_p":"Harga minimum, kelulusan negeri dan kos untuk warga asing.","open":"Baca panduan →"},'
          '"ja":{"art":"記事","mn":"マーケットノート","mn_s":"Keith の毎日の視点","g_more":"購入ガイドを開く","f_more":"全 {n} 件の回答を見る","b_more":"全 {n} 本の記事を見る","back":"← ニュース","gn":"新築","gs":"中古","gf":"外国人購入者",'
          '"gn_p":"デベロッパーから購入：予約、SPA、ローン、引き渡し。","gs_p":"オーナーから購入：オファー、登記確認、ローン、名義変更。","gf_p":"最低購入価格、州の許可、外国人の費用。","open":"ガイドを読む →"},'
          '"ko":{"art":"기사","mn":"마켓 노트","mn_s":"Keith의 매일 코멘트","g_more":"구매 가이드 열기","f_more":"답변 {n}개 모두 보기","b_more":"기사 {n}개 모두 보기","back":"← 뉴스","gn":"신규 분양","gs":"재판매","gf":"외국인 구매자",'
          '"gn_p":"개발사에서 구매: 예약, SPA, 대출, 인도.","gs_p":"소유주에게 구매: 제안, 등기 확인, 대출, 이전.","gf_p":"최저 가격, 주 정부 승인, 외국인 비용.","open":"가이드 읽기 →"}};'
          'function lg(){var l="en";try{l=document.documentElement.getAttribute("data-page-lang")||localStorage.getItem("kn_lang")||"en"}catch(e){}return T[l]?l:"en";}'
          'function go(){var l=lg();document.querySelectorAll("[data-nwh]").forEach(function(e){var s=T[l][e.getAttribute("data-nwh")]||T.en[e.getAttribute("data-nwh")];'
          'if(s)e.textContent=s.replace("{n}",e.getAttribute("data-n")||"");});}go();document.addEventListener("DOMContentLoaded",go);'
          'var w=window.knSetLang;if(typeof w==="function"){window.knSetLang=function(){var r=w.apply(this,arguments);go();return r;};}})();</script>')


def nwh(key, en, n=None):
    return '<span data-nwh="%s"%s>%s</span>' % (key, ' data-n="%d"' % n if n is not None else '', en.replace('{n}', str(n) if n is not None else ''))


_m = re.search(r'(\d+) answers</small>', hero)
n_faq = int(_m.group(1)) if _m else faq.count('class="nf-item"')
n_art = grid.count('class="article-card"')

# ---- the hub (blog.html): hero first, then the notes and a preview of each section ----
hub_hero = hero.replace(nav, nav_for(None))
G_IC = {'n': '<path d="M4 21V9l8-6 8 6v12"/><path d="M9 21v-6h6v6"/>', 's': '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-5h4v5"/>',
        'f': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>'}
gcards = ''.join('<a href="buying-guide.html#%s"><span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">%s</svg></span><b>%s</b><small>%s</small><em>%s</em></a>' % (
    anchor, G_IC[k], nwh('g' + k, title), nwh('g%s_p' % k, desc), nwh('open', 'Read the guide →')) for k, anchor, title, desc in [
    ('n', 'new-property', 'New property', 'Buying from a developer: booking, SPA, loan and handover.'),
    ('s', 'subsale', 'Subsale', 'Buying from an owner: offer, searches, loan and transfer.'),
    ('f', 'foreign-buyers', 'Foreign buyers', 'The minimum price, state consent and the costs for foreigners.')])
g_head = re.search(r'<section class="nw-sec bg-sec" id="buying-guide">\s*(<p class="nw-eyebrow">.*?</p>\s*<h2 class="nw-h2">.*?</h2>\s*<p class="nw-sub">.*?</p>)', guide, re.S).group(1)
guide_prev = '<section class="nw-sec bg-sec" id="buying-guide">%s<div class="nw-gcards">%s</div><div class="nw-more"><a href="buying-guide.html">%s →</a></div></section>' % (
    g_head, gcards, nwh('g_more', 'Open the Buying Guide'))
items = re.findall(r'<div class="nf-item">.*?</div></div>', faq, re.S)
f_head = re.search(r'<section class="nw-sec nf-sec"[^>]*>(\s*<p class="nw-eyebrow">.*?</p>\s*<h2 class="nw-h2">.*?</h2>\s*<p class="nw-sub">.*?</p>)', faq, re.S).group(1)
faq_prev = ('<section class="nw-sec nf-sec" id="faq" data-no-currency>%s<div class="nf-list nf-prev" id="nfList">%s</div><div class="nw-more"><a href="faq.html">%s →</a></div></section>' % (
    f_head, ''.join(items[:6]), nwh('f_more', 'See all {n} answers', n_faq)))
cards = re.findall(r'  <div class="article-card".*?\n  </div>\n', grid, re.S)
blog = blog.replace('<p class="nw-eyebrow">Blog</p>', '<p class="nw-eyebrow"><span data-nwh="art">Articles</span></p>', 1)
blog_prev = (re.sub(r'\s*<p class="bt-label">.*?</div>', '', blog, count=1, flags=re.S).replace('\n</section>', '', 1) +
             '<div class="journal-grid" id="journalGrid">\n%s</div><div class="nw-more"><a href="articles.html">%s →</a></div>\n</section>\n' % (
                 ''.join(cards[:6]), nwh('b_more', 'See all {n} articles', n_art)))
import news_hub_modules  # noqa: E402
nh_top, nh_tools, nh_js = news_hub_modules.build()
hub = (prefix + SEC_CSS + CSS + hub_hero + nh_top + '\n<!-- KN-NWHUB -->\n' + guide_prev + nd + '\n' + faq_prev + '\n' + videos + '\n' + blog_prev +
       nh_tools + '<div class="filters" id="filters" hidden></div>\n' + suffix.replace('</body>', HUB_TX + nh_js + '\n</body>', 1))


# ---- landing pages ----
def landing(fname, active, eyebrow_key, eyebrow, h1, lead, body, title, desc):
    head = prefix
    url = SITE + fname
    head = re.sub(r'<title>[^<]*</title>', '<title>%s</title>' % title, head, count=1)
    head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + desc, head, count=1)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, head, count=1)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + url, head, count=1)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + title, head, count=1)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + desc, head, count=1)
    head = re.sub(r'<!-- KN-LD:START -->.*?<!-- KN-LD:END -->', '<!-- KN-LD:START --><!-- KN-LD:END -->', head, flags=re.S)
    top = ('<section class="journal-hero nw-sub-hero"><a class="nw-back" href="blog.html">%s</a><span class="eyebrow">%s</span><h1>%s</h1><p>%s</p>%s</section>\n' % (
        nwh('back', '← News'), eyebrow, h1, lead, ''))
    page = head + SEC_CSS + CSS + top + body + suffix.replace('</body>', HUB_TX + '\n</body>', 1)
    open(fname, 'w', encoding='utf-8').write(page)


strip_head = lambda s: re.sub(r'(<section[^>]*>)\s*<p class="nw-eyebrow">.*?</p>\s*<h2 class="nw-h2">.*?</h2>\s*(<p class="nw-sub">.*?</p>)?', r'\1', s, count=1, flags=re.S)
landing('buying-guide.html', 'buying-guide.html', 'g', 'Buying Guide', 'Buying property in Malaysia, step by step',
        'New property, subsale and the rules for foreign buyers: the key numbers, the stages and the questions buyers ask most.',
        strip_head(guide), 'Malaysia Property Buying Guide: New, Subsale & Foreign Buyers | Keith Nah',
        'Step-by-step guides to buying property in Malaysia: new launches, subsale homes and the rules and costs for foreign buyers.')
landing('articles.html', 'articles.html', 'b', nwh('art', 'Articles'), 'Latest property news and insights',
        'Every article by topic: market outlook, new launch reviews, area guides, foreign buyer rules and more.',
        strip_head(blog) + '\n<div class="filters" id="filters" hidden></div>\n' + grid, 'Malaysia Property Articles: News & Insights | Keith Nah',
        'Articles on the Malaysian property market by topic: new launch reviews, area guides, foreign buyer rules, costs and the market outlook.')
open('blog.html', 'w', encoding='utf-8').write(hub)
print('news split: hub + buying-guide.html, faq.html (%d answers), articles.html (%d articles)' % (n_faq, n_art))
