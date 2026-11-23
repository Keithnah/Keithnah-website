"""FAQ by topic: faq.html (all topics) and faq-<slug>.html (one page per topic), plus FAQ blocks on related pages.

Questions and answers, in every site language, live in tools/faq_topics.json. The home page FAQ, the News page
FAQ preview and the structured data (FAQPage) all read the same file.
Related pages get a short block (a few questions + a link) between KN-FAQREL markers:
    foreign-buyers.html -> Foreign buyers, calculator.html -> Costs & taxes, topic/<slug>.html -> the matching topic.
The pages translate themselves in the browser (data-hb); tools/build_lang_pages.js makes the language copies.
"""
import datetime
import html
import json
import os
import re
import sys
from urllib.parse import quote_plus

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import hubs_data as HB
import site_header as SH

E = lambda s: html.escape(str(s), quote=True)
SITE = 'https://keithnah.com/'
DATA = json.load(open(os.path.join(HERE, 'faq_topics.json'), encoding='utf-8'))
TOP, QS = DATA['topics'], DATA['questions']
LANGS = ['en', 'zh-CN', 'ms', 'ja', 'ko']
UI = {
    'en': {'eb': 'Property FAQ', 'h1': 'Every question, by topic', 'lead': 'Answers to what buyers ask Keith most, grouped so you find yours fast.',
           'search': 'Search a question, e.g. stamp duty, MM2H, loan', 'search_t': 'Search this topic', 'go': 'Search', 'none': 'No question matches. Try another word, or ask Keith on WhatsApp.',
           'nq': '{n} questions', 'soon': 'Questions coming soon', 'all': 'See all questions →', 'pop_eb': 'Most asked', 'pop_h': 'Start here',
           'back': '← News', 'hub': '← All FAQ topics', 'toc': 'Questions', 'topics': 'Other topics', 'cta_h': 'Still have a question?',
           'cta_p': 'Ask Keith on WhatsApp. He replies personally.', 'cta_b': 'WhatsApp Keith', 'updated': 'Updated {d}', 'rel_h': 'Questions buyers ask', 'rel_more': 'See all {n} questions on {t} →',
           'h1_t': '{t}: questions and answers'},
    'zh-CN': {'eb': '房产常见问题', 'h1': '所有问题，按主题整理', 'lead': '买家最常问 Keith 的问题，按主题分好，方便你快速找到答案。',
              'search': '搜索问题，例如印花税、MM2H、贷款', 'search_t': '在这个主题里搜索', 'go': '搜索', 'none': '找不到相关问题，换个字试试，或在 WhatsApp 问 Keith。',
              'nq': '{n} 个问题', 'soon': '问题即将加入', 'all': '查看全部问题 →', 'pop_eb': '最多人问', 'pop_h': '从这里开始',
              'back': '← 新闻', 'hub': '← 全部 FAQ 主题', 'toc': '问题目录', 'topics': '其他主题', 'cta_h': '还有问题？',
              'cta_p': '在 WhatsApp 问 Keith，他会亲自回复。', 'cta_b': 'WhatsApp Keith', 'updated': '更新于 {d}', 'rel_h': '买家常问的问题', 'rel_more': '查看「{t}」全部 {n} 个问题 →',
              'h1_t': '{t}：常见问题与解答'},
    'ms': {'eb': 'Soalan Lazim Hartanah', 'h1': 'Setiap soalan, mengikut topik', 'lead': 'Jawapan kepada soalan yang paling kerap ditanya kepada Keith, disusun supaya anda cepat menemuinya.',
           'search': 'Cari soalan, cth. duti setem, MM2H, pinjaman', 'search_t': 'Cari dalam topik ini', 'go': 'Cari', 'none': 'Tiada soalan yang sepadan. Cuba perkataan lain, atau tanya Keith di WhatsApp.',
           'nq': '{n} soalan', 'soon': 'Soalan akan ditambah', 'all': 'Lihat semua soalan →', 'pop_eb': 'Paling kerap ditanya', 'pop_h': 'Mula di sini',
           'back': '← Berita', 'hub': '← Semua topik Soalan Lazim', 'toc': 'Soalan', 'topics': 'Topik lain', 'cta_h': 'Masih ada soalan?',
           'cta_p': 'Tanya Keith di WhatsApp. Dia membalas sendiri.', 'cta_b': 'WhatsApp Keith', 'updated': 'Dikemas kini {d}', 'rel_h': 'Soalan yang ditanya pembeli', 'rel_more': 'Lihat kesemua {n} soalan tentang {t} →',
           'h1_t': '{t}: soalan dan jawapan'},
    'ja': {'eb': '不動産 FAQ', 'h1': 'すべての質問をトピック別に', 'lead': '購入者が Keith によく尋ねる質問を、探しやすいようにトピック別にまとめました。',
           'search': '質問を検索（例：印紙税、MM2H、ローン）', 'search_t': 'このトピック内を検索', 'go': '検索', 'none': '該当する質問がありません。別の言葉で試すか、WhatsApp で Keith にお尋ねください。',
           'nq': '{n} 件の質問', 'soon': '質問は近日追加', 'all': 'すべての質問を見る →', 'pop_eb': 'よくある質問', 'pop_h': 'まずはここから',
           'back': '← ニュース', 'hub': '← FAQ トピック一覧', 'toc': '質問一覧', 'topics': 'ほかのトピック', 'cta_h': 'まだ疑問がありますか？',
           'cta_p': 'WhatsApp で Keith にお尋ねください。本人が返信します。', 'cta_b': 'WhatsApp で連絡', 'updated': '{d} 更新', 'rel_h': '購入者からよくある質問', 'rel_more': '「{t}」の全 {n} 件を見る →',
           'h1_t': '{t}：よくある質問と回答'},
    'ko': {'eb': '부동산 FAQ', 'h1': '모든 질문을 주제별로', 'lead': '구매자들이 Keith에게 가장 많이 묻는 질문을 주제별로 정리해 빠르게 찾을 수 있습니다.',
           'search': '질문 검색 (예: 인지세, MM2H, 대출)', 'search_t': '이 주제에서 검색', 'go': '검색', 'none': '일치하는 질문이 없습니다. 다른 단어로 찾거나 WhatsApp으로 Keith에게 물어보세요.',
           'nq': '질문 {n}개', 'soon': '질문 추가 예정', 'all': '모든 질문 보기 →', 'pop_eb': '가장 많이 묻는 질문', 'pop_h': '여기서 시작하세요',
           'back': '← 뉴스', 'hub': '← 전체 FAQ 주제', 'toc': '질문 목록', 'topics': '다른 주제', 'cta_h': '아직 궁금한 점이 있나요?',
           'cta_p': 'WhatsApp으로 Keith에게 물어보세요. 직접 답합니다.', 'cta_b': 'WhatsApp으로 문의', 'updated': '{d} 업데이트', 'rel_h': '구매자들이 묻는 질문', 'rel_more': '{t} 질문 {n}개 모두 보기 →',
           'h1_t': '{t}: 질문과 답변'},
}
T = {l: dict(UI[l]) for l in LANGS}
for t in TOP:
    for l in LANGS:
        T[l]['tn_' + t['slug']] = t['name'].get(l) or t['name']['en']
        T[l]['td_' + t['slug']] = t['desc'].get(l) or t['desc']['en']
for qid, x in QS.items():
    for l in LANGS:
        T[l]['q_' + qid] = x['q'].get(l) or x['q']['en']
        T[l]['a_' + qid] = x['a'].get(l) or x['a']['en']
try:
    import opencc
    _cc = opencc.OpenCC('s2tw').convert
    T['zh-TW'] = {k: _cc(v) for k, v in T['zh-CN'].items()}
    for qid, x in QS.items():   # hand-made zh-TW where it exists
        if 'zh-TW' in x['q']:
            T['zh-TW']['q_' + qid] = x['q']['zh-TW']
        if 'zh-TW' in x['a']:
            T['zh-TW']['a_' + qid] = x['a']['zh-TW']
except Exception:
    T['zh-TW'] = dict(T['zh-CN'])
for l in T:
    T[l]['nq1'] = T[l]['nq'].replace('{n}', '1')
T['en']['nq1'] = '1 question'
EN = T['en']
POPULAR = ['h1', 'h11', 'h6', 'h12']  # filled up with first questions of the topics below
TODAY = datetime.date.today()
UPDATED = TODAY.strftime('%b %Y')
WA = 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0'


def tx(key, tag='span', cls='', attrs='', **v):
    s = EN[key]
    for k, val in v.items():
        s = s.replace('{%s}' % k, str(val))
    hv = (" data-hv='%s'" % E(json.dumps({k: str(val) for k, val in v.items()}, ensure_ascii=False)).replace("'", '&#x27;')) if v else ''
    return '<%s data-hb="%s"%s%s%s>%s</%s>' % (tag, key, hv, (' class="%s"' % cls) if cls else '', (' ' + attrs) if attrs else '', E(s), tag)


def wa(msg):
    return WA % quote_plus('(KNRE) ' + msg)


def icon(p):
    return '<span class="fq-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="%s"/></svg></span>' % p


CSS = '''
:root{--ink:#15142b;--grey:#55546b;--line:rgba(21,20,43,.1);--gold:#5E60CE;--bg:#F9F8F6;--soft:#f3f1fa}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:Inter,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6}a{color:inherit;text-decoration:none}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif;line-height:1.2}
.fx{max-width:1180px;margin:0 auto;padding:0 5vw}.fx-eb{display:block;font:700 12px Inter,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:var(--gold)}
.fx-hero{padding:130px 0 30px;text-align:center;background:linear-gradient(180deg,#f3f1fa,#F9F8F6)}.fx-back{display:inline-block;margin-bottom:14px;color:var(--gold);font-weight:700;font-size:15px}
.fx-hero h1{font-size:clamp(32px,5vw,54px);margin:10px 0 12px}.fx-hero p{color:var(--grey);max-width:720px;margin:0 auto 22px;font-size:16.5px}
.fx-search{max-width:620px;margin:0 auto;display:flex;align-items:center;gap:10px;background:#fff;border:1.5px solid rgba(94,96,206,.35);border-radius:100px;padding:6px 6px 6px 20px;box-shadow:0 14px 34px rgba(29,27,79,.1)}
.fx-search input{flex:1;min-width:0;border:0;outline:0;font:500 16px Inter,sans-serif;background:none;color:var(--ink)}.fx-search button{background:var(--gold);color:#fff;border:0;border-radius:100px;padding:11px 20px;font:700 14px Inter,sans-serif;cursor:pointer}
.fx-none{display:none;text-align:center;color:var(--grey);margin:18px 0}
.fx-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:34px 0 10px}
.fx-card{display:flex;flex-direction:column;background:#fff;border:1px solid var(--line);border-radius:20px;overflow:hidden;transition:border-color .2s,box-shadow .2s,transform .2s}
.fx-card:hover{border-color:var(--gold);box-shadow:0 16px 34px rgba(29,27,79,.12);transform:translateY(-3px)}
.fq-ic{width:46px;height:46px;border-radius:13px;background:#eeedfb;display:flex;align-items:center;justify-content:center;color:var(--gold)}.fq-ic svg{width:24px;height:24px}
.fx-ch{background:linear-gradient(135deg,#1d1b4f,#34318a);color:#fff;padding:20px 20px 18px}.fx-ch .fq-ic{background:rgba(255,255,255,.14);color:#fff}
.fx-ch b{display:block;font:700 20px 'Playfair Display',serif;margin:14px 0 4px;color:#fff}.fx-ch small{display:block;color:#d6d6f3;font-size:13.5px;line-height:1.5}.fx-ch .n{display:inline-block;background:#fff;color:#3d3fb0;font:700 11.5px Inter,sans-serif;padding:3px 10px;border-radius:100px;margin:10px 0 0}
.fx-card ul{list-style:none;margin:4px 20px 0}.fx-card li{font-size:13px;color:#2f2e45;padding:7px 0;border-bottom:1px dashed rgba(21,20,43,.08)}
.fx-card em{margin-top:auto;padding:12px 20px 18px;color:var(--gold);font-style:normal;font-weight:700;font-size:13.5px}
.fx-pop{margin:30px 0 40px}.fx-pop h2,.fx-sec h2{font-size:clamp(24px,3vw,32px);margin:8px 0 16px}
.fx-g2{display:grid;grid-template-columns:270px minmax(0,1fr);gap:34px;align-items:start;padding:30px 0 30px}
.fx-toc{display:block;position:sticky;top:96px;background:#fff;border:1px solid var(--line);border-radius:18px;padding:16px;max-height:calc(100vh - 120px);overflow:auto}
.fx-toc b{display:block;font:700 12px Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);margin-bottom:8px}.fx-toc a{display:flex;gap:8px;white-space:normal;line-height:1.4;font-size:13px;padding:7px 0;color:#2f2e45;border-top:1px solid rgba(21,20,43,.06)}.fx-toc a i{font-style:normal;color:var(--gold);font-weight:800}
.fx-tabs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;max-width:980px;margin:26px auto 0;background:#fff;border:1px solid rgba(21,20,43,.1);border-radius:20px;padding:8px;box-shadow:0 10px 28px rgba(29,27,79,.06)}
.fx-tabs a{display:flex;align-items:center;gap:10px;border-radius:14px;padding:10px 12px;font:700 13.5px Inter,sans-serif;color:var(--ink);text-align:left;line-height:1.25}.fx-tabs a:hover{background:var(--soft)}
.fx-tabs .fq-ic{flex:0 0 32px;width:32px;height:32px;border-radius:10px}.fx-tabs .fq-ic svg{width:18px;height:18px}.fx-tabs a.on{background:#1d1b4f;color:#fff}.fx-tabs a.on .fq-ic{background:rgba(255,255,255,.16);color:#fff}
.fx-q{background:#fff;border:1px solid var(--line);border-radius:18px;padding:20px 22px;margin-bottom:12px;scroll-margin-top:100px}.fx-q h3{display:flex;gap:12px;font:700 18px Inter,sans-serif}.fx-q h3 i{font-style:normal;color:var(--gold);font-weight:800;flex:0 0 auto}
.fx-q p{margin:10px 0 0;color:#2f2e45;line-height:1.75;font-size:15.5px}.fx-q .src{margin-top:10px;font-size:12.5px;color:#77768c}.fx-q .src a{color:var(--gold);text-decoration:underline}
.fx-acc{background:#fff;border:1px solid var(--line);border-radius:16px;margin-bottom:10px}.fx-acc summary{cursor:pointer;list-style:none;padding:15px 44px 15px 18px;position:relative;font-weight:700;font-size:15px}.fx-acc summary::-webkit-details-marker{display:none}
.fx-acc summary:after{content:"+";position:absolute;right:18px;top:12px;color:var(--gold);font:700 22px Inter,sans-serif}.fx-acc[open] summary:after{content:"−"}.fx-acc p{padding:0 18px 16px;color:#2f2e45;line-height:1.7;font-size:14.5px}
.fx-soon{background:#fff;border:1px dashed rgba(94,96,206,.4);border-radius:18px;padding:30px;text-align:center;color:var(--grey)}
.cta{background:#111;color:#fff;border-radius:22px;padding:30px;text-align:center;margin:30px 0 60px}.cta h2{color:#fff;margin-bottom:8px;font-size:clamp(22px,3vw,28px)}.cta p{color:#cfcfe0}
.cta a{display:inline-block;margin-top:14px;background:#25D366;color:#fff;padding:12px 24px;border-radius:100px;font-weight:700}
footer{border-top:1px solid var(--line);padding:26px 5vw;font-size:13px;color:var(--grey);text-align:center}
@media(max-width:760px){.fx-tabs{grid-template-columns:1fr 1fr}.fx-tabs a{padding:9px 10px;font-size:13px}}
@media(max-width:980px){.fx-grid{grid-template-columns:1fr 1fr}.fx-g2{grid-template-columns:1fr}.fx-toc{position:static;max-height:none}}
@media(max-width:600px){.fx-grid{grid-template-columns:1fr}.fx-hero{padding-top:110px}}
'''
SEARCH_JS = ('<script>(function(){var i=document.getElementById("fxS"),n=document.getElementById("fxNone");if(!i)return;'
             'function run(){var q=i.value.trim().toLowerCase(),hit=0;document.querySelectorAll("[data-fq]").forEach(function(e){var ok=!q||e.textContent.toLowerCase().indexOf(q)>=0;'
             'e.style.display=ok?"":"none";if(ok)hit++;});if(n)n.style.display=hit?"none":"block";}'
             'i.addEventListener("input",run);var b=document.getElementById("fxGo");if(b)b.addEventListener("click",run);'
             'var m=location.search.match(/[?&]q=([^&]+)/);if(m){i.value=decodeURIComponent(m[1].replace(/\\+/g," "));run();}})();</script>')
SEARCH_PH = '<script>(function(){function f(){var T=%s,l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}l=(document.documentElement.getAttribute("data-page-lang")||l);'\
            'var i=document.getElementById("fxS");if(i&&T[l])i.placeholder=T[l];}f();document.addEventListener("DOMContentLoaded",f);})();</script>'


def shell(rel, title, desc, body, ld, ph_key):
    url = SITE + rel
    page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s">
<meta property="og:type" content="website">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:url" content="%s">
<link rel="icon" type="image/png" href="images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@500;700&display=swap" rel="stylesheet">
<script type="application/ld+json">%s</script>
<style>%s</style>
</head>
<body>
<header>
  <a class="logo" href="./"><img src="images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Malaysia Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="%s" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
%s
<footer>&copy; 2026 Keith Nah Real Estate · <a href="blog.html">News</a> · <a href="faq.html">FAQ</a> · <a href="foreign-buyers.html">Foreign Buyers</a> · <a href="privacy-policy.html">Privacy Policy</a></footer>
<script src="lead-tracker.js"></script>
%s%s%s
</body>
</html>
''' % (E(title), E(desc), url, E(title), E(desc), url, json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'), CSS,
       E(wa('Hi Keith, I have a question about buying property in Malaysia.')), body,
       HB.JS % json.dumps(T, ensure_ascii=False).replace('</', '<\\/'), SEARCH_JS,
       SEARCH_PH % json.dumps({l: T[l][ph_key] for l in T}, ensure_ascii=False))
    page = SH.apply(page, '', 'blog.html')
    open(rel, 'w', encoding='utf-8').write(page)
    return url


def faq_ld(ids, url):
    return {'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': [
        {'@type': 'Question', 'name': QS[i]['q']['en'], 'acceptedAnswer': {'@type': 'Answer', 'text': QS[i]['a']['en']}} for i in ids]}


def cta():
    return '<div class="cta">%s%s<a href="%s" target="_blank" rel="noopener">%s</a></div>' % (
        tx('cta_h', 'h2'), tx('cta_p', 'p'), E(wa('Hi Keith, I have a question about buying property in Malaysia.')), tx('cta_b'))


def acc(i):
    return '<details class="fx-acc" data-fq><summary>%s</summary>%s</details>' % (tx('q_' + i), tx('a_' + i, 'p'))


written = []
# ---- hub ----
cards = ''
for t in TOP:
    n = len(t['ids'])
    cards += '<a class="fx-card" data-fq href="faq-%s.html"><div class="fx-ch">%s<b>%s</b>%s%s</div><ul>%s</ul>%s</a>' % (
        t['slug'], icon(t['icon']), tx('tn_' + t['slug']), tx('td_' + t['slug'], 'small'),
        (tx('nq1', 'span', 'n') if n == 1 else tx('nq', 'span', 'n', n=n)) if n else tx('soon', 'span', 'n'),
        ''.join('<li>%s</li>' % tx('q_' + i) for i in t['ids'][:3]), tx('all', 'em'))
pop = []
for i in POPULAR + [t['ids'][0] for t in TOP if t['ids']]:
    if i not in pop:
        pop.append(i)
pop = pop[:8]
body = '''<main><section class="fx-hero"><div class="fx"><a class="fx-back" href="blog.html">%s</a>%s%s%s
<div class="fx-search"><span aria-hidden="true">&#128269;</span><input id="fxS" type="search" placeholder="%s" aria-label="Search"><button type="button" id="fxGo">%s</button></div></div></section>
<div class="fx"><p class="fx-none" id="fxNone">%s</p><div class="fx-grid">%s</div>
<section class="fx-pop">%s%s%s</section>%s</div></main>''' % (
    tx('back'), tx('eb', 'span', 'fx-eb'), tx('h1', 'h1'), tx('lead', 'p'), E(EN['search']), tx('go'), tx('none'), cards,
    tx('pop_eb', 'span', 'fx-eb'), tx('pop_h', 'h2'), ''.join(acc(i) for i in pop), cta())
all_ids = list(dict.fromkeys(i for t in TOP for i in t['ids']))   # a question can sit in two topics; count it once
ld = {'@context': 'https://schema.org', '@graph': [
    {'@type': 'CollectionPage', 'name': 'Malaysia Property FAQ by Topic', 'url': SITE + 'faq.html'},
    {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': k + 1, 'url': SITE + 'faq-%s.html' % t['slug'], 'name': t['name']['en']} for k, t in enumerate(TOP)]},
    {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'News', 'item': SITE + 'blog.html'}, {'@type': 'ListItem', 'position': 2, 'name': 'FAQ', 'item': SITE + 'faq.html'}]}]}
written.append(shell('faq.html', 'Malaysia Property FAQ: %d Answers by Topic | Keith Nah' % len(all_ids),
                     '%d answers to what buyers ask about Malaysian property, by topic: first home, foreign buyers, investment, costs and taxes, the buying process and more.' % len(all_ids),
                     body, ld, 'search'))

# ---- topic pages ----
for k, t in enumerate(TOP):
    s, ids = t['slug'], t['ids']
    tabs = ''.join('<a href="faq-%s.html"%s>%s%s</a>' % (o['slug'], ' class="on" aria-current="page"' if o is t else '', icon(o['icon']), tx('tn_' + o['slug'])) for o in TOP)
    if ids:
        toc = ''.join('<a href="#q%02d"><i>Q%02d</i>%s</a>' % (n, n, tx('q_' + i)) for n, i in enumerate(ids, 1))
        items = ''.join('<article class="fx-q" id="q%02d" data-fq><h3><i>Q%02d</i>%s</h3>%s<div class="src">%s%s</div></article>' % (
            n, n, tx('q_' + i), tx('a_' + i, 'p'),
            ('<a href="%s" target="_blank" rel="noopener nofollow">%s</a> · ' % (E(QS[i]['src']['url']), E(QS[i]['src']['name']))) if QS[i].get('src') else '',
            tx('updated', d=UPDATED)) for n, i in enumerate(ids, 1))
        main = '<div class="fx-g2"><nav class="fx-toc" aria-label="Questions">%s%s</nav><div><p class="fx-none" id="fxNone">%s</p>%s</div></div>' % (tx('toc', 'b'), toc, tx('none'), items)
    else:
        main = '<div class="fx-soon" style="margin:30px 0">%s</div>' % tx('soon', 'p')
    others = ''.join('<a class="fx-card" href="faq-%s.html"><div class="fx-ch">%s<b>%s</b>%s</div>%s</a>' % (o['slug'], icon(o['icon']), tx('tn_' + o['slug']), tx('td_' + o['slug'], 'small'), tx('all', 'em'))
                     for o in (TOP[(k + 1) % len(TOP)], TOP[(k + 2) % len(TOP)], TOP[(k + 3) % len(TOP)], TOP[(k + 4) % len(TOP)]))
    body = '''<main><section class="fx-hero"><div class="fx"><a class="fx-back" href="faq.html">%s</a>%s%s%s
<div class="fx-search"><span aria-hidden="true">&#128269;</span><input id="fxS" type="search" placeholder="%s" aria-label="Search"><button type="button" id="fxGo">%s</button></div><div class="fx-tabs">%s</div></div></section>
<div class="fx">%s<section class="fx-sec">%s<div class="fx-grid">%s</div></section>%s</div></main>''' % (
        tx('hub'), (tx('nq1', 'span', 'fx-eb') if len(ids) == 1 else tx('nq', 'span', 'fx-eb', n=len(ids))) if ids else tx('soon', 'span', 'fx-eb'), tx('h1_t', 'h1', t=t['name']['en']), tx('td_' + s, 'p'),
        E(EN['search_t']), tx('go'), tabs, main, tx('topics', 'h2'), others, cta())
    url = SITE + 'faq-%s.html' % s
    ld = {'@context': 'https://schema.org', '@graph': ([faq_ld(ids, url)] if ids else []) + [
        {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'News', 'item': SITE + 'blog.html'},
                                                         {'@type': 'ListItem', 'position': 2, 'name': 'FAQ', 'item': SITE + 'faq.html'},
                                                         {'@type': 'ListItem', 'position': 3, 'name': t['name']['en'], 'item': url}]}]}
    # the h1 text depends on the topic name in each language: give it a per-topic key
    for l in T:
        T[l]['h1_' + s] = T[l]['h1_t'].replace('{t}', T[l]['tn_' + s])
    body = body.replace('data-hb="h1_t" data-hv=', 'data-hb="h1_%s" data-x=' % s, 1)
    written.append(shell('faq-%s.html' % s, '%s FAQ: Malaysia Property Questions Answered | Keith Nah' % t['name']['en'],
                         (t['desc']['en'] + ' %d questions with short, clear answers.' % len(ids)) if ids else t['desc']['en'], body, ld, 'search_t'))


# ---- blocks on related pages ----
REL_CSS = ('<style>.kn-frel{max-width:1180px;margin:10px auto 40px;padding:0 5vw}.kn-frel h2{font:700 clamp(22px,2.8vw,30px) "Playfair Display",serif;margin:6px 0 14px}'
           '.kn-frel .eb{display:block;font:700 12px Inter,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:#5E60CE}'
           '.kn-frel details{background:#fff;border:1px solid rgba(21,20,43,.1);border-radius:16px;margin-bottom:10px}.kn-frel summary{cursor:pointer;list-style:none;padding:15px 44px 15px 18px;position:relative;font:700 15px Inter,sans-serif;color:#15142b}'
           '.kn-frel summary::-webkit-details-marker{display:none}.kn-frel summary:after{content:"+";position:absolute;right:18px;top:12px;color:#5E60CE;font:700 22px Inter,sans-serif}.kn-frel details[open] summary:after{content:"−"}'
           '.kn-frel details p{padding:0 18px 16px;color:#2f2e45;line-height:1.7;font:400 14.5px Inter,sans-serif}.kn-frel a.more{display:inline-block;margin-top:8px;color:#5E60CE;font:700 14.5px Inter,sans-serif}</style>')
TOPIC_MAP = {'foreign-buyer-rules': 'foreign-buyers', 'costs-tax-and-stamp-duty': 'costs-and-taxes', 'loan-and-financing': 'first-home-buyer',
             'rental-yield-and-airbnb': 'investment', 'investment-strategy': 'investment', 'market-outlook': 'investment', 'mm2h': 'foreign-buyers',
             'johor-and-singapore-buyers': 'foreign-buyers', 'new-launch-reviews': 'buying-process', 'expat-living': 'owning'}


def rel_block(slug, root, n=5):
    t = next(x for x in TOP if x['slug'] == slug)
    ids = t['ids'][:n]
    return ('<!-- KN-FAQREL:START -->%s<section class="kn-frel" data-no-currency>%s%s%s<a class="more" href="%sfaq-%s.html">%s</a></section>%s<!-- KN-FAQREL:END -->' % (
        REL_CSS, tx('rel_h', 'span', 'eb'), tx('tn_' + slug, 'h2'), ''.join(acc(i) for i in ids), root, slug,
        tx('rel_more', t=t['name']['en'], n=len(t['ids'])).replace('data-hb="rel_more"', 'data-hb="rm_%s"' % slug), HB.JS % json.dumps(
            {l: {k: v for k, v in T[l].items() if k in {'rel_h', 'tn_' + slug, 'rm_' + slug} or k[2:] in ids} for l in T}, ensure_ascii=False).replace('</', '<\\/')))


for l in T:
    for t in TOP:
        T[l]['rm_' + t['slug']] = T[l]['rel_more'].replace('{t}', T[l]['tn_' + t['slug']]).replace('{n}', str(len(t['ids'])))


def put(path, block, before):
    if not os.path.exists(path):
        return False
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'<!-- KN-FAQREL:START -->.*?<!-- KN-FAQREL:END -->', '', s, flags=re.S)
    i = s.rfind(before) if before else -1
    if i < 0:
        i = s.rfind('<footer')
    if i < 0:
        return False
    open(path, 'w', encoding='utf-8').write(s[:i] + block + s[i:])
    return True


n_rel = 0
n_rel += put('calculator.html', rel_block('costs-and-taxes', ''), '<footer')
for ts, fs in TOPIC_MAP.items():
    n_rel += put('topic/%s.html' % ts, rel_block(fs, '../'), '<footer')

# ---- sitemap ----
if os.path.exists('sitemap.xml'):
    sm = open('sitemap.xml', encoding='utf-8').read()
    sm = re.sub(r'  <url>\n    <loc>https://keithnah.com/faq-[^<]*</loc>.*?</url>\n', '', sm, flags=re.S)
    sm = sm.replace('</urlset>', ''.join('  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n' % (u, TODAY.isoformat())
                                         for u in written if '/faq-' in u) + '</urlset>')
    open('sitemap.xml', 'w', encoding='utf-8').write(sm)
print('faq: hub + %d topic pages, %d questions, blocks on %d related pages' % (len(TOP), len(all_ids), n_rel))


# ---- home page: topic cards above the questions; 6 questions shown, the rest on the FAQ pages ----
HOME_CSS = ('<style>#faq .hf-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;max-width:1100px;margin:26px auto 26px}'
            '#faq .hf-grid a{display:flex;align-items:center;gap:12px;background:linear-gradient(135deg,#1d1b4f,#34318a);border:1px solid transparent;box-shadow:0 10px 24px rgba(29,27,79,.16);border-radius:16px;padding:14px 16px;text-align:left;transition:border-color .2s,box-shadow .2s,transform .2s}'
            '#faq .hf-grid a:hover{box-shadow:0 16px 32px rgba(29,27,79,.26);transform:translateY(-2px)}'
            '#faq .hf-grid .fq-ic{flex:0 0 42px;width:42px;height:42px;border-radius:12px;background:rgba(255,255,255,.14);display:flex;align-items:center;justify-content:center;color:#fff}#faq .hf-grid svg{width:22px;height:22px}'
            '#faq .hf-grid b{display:block;font:700 15px Inter,sans-serif;color:#fff}#faq .hf-grid small{display:block;font:600 12.5px Inter,sans-serif;color:#c9caff}'
            '#faq .faq-list .faq-item:nth-child(n+7){display:none!important}#faq .faq-more-wrap,#faq [data-i18n="faq_more_btn"]{display:none!important}'
            '#faq .hf-all{text-align:center;margin:18px 0 6px}#faq .hf-all a{display:inline-block;background:#5E60CE;color:#fff;font:700 15px Inter,sans-serif;padding:13px 26px;border-radius:100px;box-shadow:0 12px 26px rgba(94,96,206,.28)}'
            '@media(max-width:900px){#faq .hf-grid{grid-template-columns:1fr 1fr}}@media(max-width:480px){#faq .hf-grid{gap:8px}#faq .hf-grid a{padding:12px}#faq .hf-grid .fq-ic{display:none}}</style>')
for l in T:
    T[l]['hf_all'] = {'en': 'See all {n} questions by topic →', 'zh-CN': '按主题查看全部 {n} 个问题 →', 'zh-TW': '按主題查看全部 {n} 個問題 →', 'ms': 'Lihat kesemua {n} soalan mengikut topik →',
                      'ja': 'トピック別に全 {n} 件の質問を見る →', 'ko': '주제별로 질문 {n}개 모두 보기 →'}[l].replace('{n}', str(len(all_ids)))
    for t in TOP:
        T[l]['hn_' + t['slug']] = (T[l]['nq1'] if len(t['ids']) == 1 else T[l]['nq'].replace('{n}', str(len(t['ids'])))) if t['ids'] else T[l]['soon']
grid = ''.join('<a href="faq-%s.html">%s<span>%s%s</span></a>' % (t['slug'], icon(t['icon']), tx('tn_' + t['slug'], 'b'), tx('hn_' + t['slug'], 'small')) for t in TOP)
keys = {'hf_all'} | {'tn_' + t['slug'] for t in TOP} | {'hn_' + t['slug'] for t in TOP}
HOME = ('<!-- KN-HFAQ:START -->%s<div class="hf-grid">%s</div>%s<!-- KN-HFAQ:END -->' % (
    HOME_CSS, grid, HB.JS % json.dumps({l: {k: v for k, v in T[l].items() if k in keys} for l in T}, ensure_ascii=False).replace('</', '<\\/')))
HOME_ALL = '<!-- KN-HFAQ2:START --><p class="hf-all"><a href="faq.html">%s</a></p><!-- KN-HFAQ2:END -->' % tx('hf_all')
s = open('index.html', encoding='utf-8').read()
s = re.sub(r'<!-- KN-HFAQ2?:START -->.*?<!-- KN-HFAQ2?:END -->', '', s, flags=re.S)
i = s.index('<section id="faq">')
j = s.index('<div class="faq-list">', i)
s = s[:j] + HOME + '\n  ' + s[j:]
k = s.index('<div class="faq-cta">', j)
s = s[:k] + HOME_ALL + '\n  ' + s[k:]
open('index.html', 'w', encoding='utf-8').write(s)
print('faq: topic cards on the home page')
