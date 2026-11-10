"""Keith's Market Notes on the News page (blog.html).

Notes live in tools/market_notes.json, newest first:
  [{"date": "2026-11-11", "area": {"en": "Kuala Lumpur", "zh-CN": "吉隆坡", ...},
    "title": {lang: text}, "body": {lang: text}, "take": {lang: text},
    "links": [{"label": {lang: text}, "href": "article/....html"}],
    "sources": [{"name": "The Star", "url": "https://..."}]}]   (news reports the note is based on)
Languages: en, zh-CN, zh-TW, ms, ja, ko (a missing language falls back to English).
The section sits at the very top of the News page, above The Journal heading, and stays hidden while there are no notes.
New notes are added by the daily topic flow (see tools/leads-apps-script.gs). Safe to run again.
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
E = lambda s: html.escape(str(s), quote=True)
LANGS = ['en', 'zh-CN', 'zh-TW', 'ms', 'ja', 'ko']
PATH = os.path.join(HERE, 'market_notes.json')
NOTES = json.load(open(PATH, encoding='utf-8')) if os.path.exists(PATH) else []
NOTES = sorted(NOTES, key=lambda n: n['date'], reverse=True)   # every note is kept for good
RECENT = NOTES[:10]                                            # the News page shows the latest 10

LBL = {
    'en': {'eb': "Keith's Market Notes", 'h2': 'One minute on the <em>market</em>, every day',
           'p': 'Keith explains what moved in Malaysian property and the economy, and what it means if you are buying.', 'all': 'All market notes', 'archive': 'Every market note, newest first.',
           'take': "Keith's take", 'src': 'Sources:', 'earlier': 'Earlier notes', 'foot': "Opinions are Keith's own and are not financial advice.", 'ask': 'Ask Keith about this →'},
    'zh-CN': {'eb': 'Keith 每日市场短评', 'h2': '每天一分钟，看懂<em>房市</em>', 'p': 'Keith 每天解读马来西亚房产和经济的变化，以及对买家的意义。', 'all': '全部短评', 'archive': '所有市场短评，最新的在最前面。',
              'take': 'Keith 怎么看', 'src': '新闻来源：', 'earlier': '往期短评', 'foot': '以上为 Keith 的个人观点，并非投资建议。', 'ask': '就这个问 Keith →'},
    'zh-TW': {'eb': 'Keith 每日市場短評', 'h2': '每天一分鐘，看懂<em>房市</em>', 'p': 'Keith 每天解讀馬來西亞房產和經濟的變化，以及對買家的意義。', 'all': '全部短評', 'archive': '所有市場短評，最新的在最前面。',
              'take': 'Keith 怎麼看', 'src': '新聞來源：', 'earlier': '往期短評', 'foot': '以上為 Keith 的個人觀點，並非投資建議。', 'ask': '就這個問 Keith →'},
    'ms': {'eb': 'Nota Pasaran Keith', 'h2': 'Seminit tentang <em>pasaran</em>, setiap hari', 'p': 'Keith menerangkan perkembangan hartanah dan ekonomi Malaysia, dan maksudnya untuk pembeli.', 'all': 'Semua nota pasaran', 'archive': 'Semua nota pasaran, yang terbaharu dahulu.',
           'take': 'Pandangan Keith', 'src': 'Sumber:', 'earlier': 'Nota terdahulu', 'foot': 'Pendapat ini milik Keith sendiri dan bukan nasihat kewangan.', 'ask': 'Tanya Keith tentang ini →'},
    'ja': {'eb': 'Keith のマーケットノート', 'h2': '毎日1分で<em>市場</em>がわかる', 'p': 'マレーシアの不動産と経済の動きと、購入者にとっての意味を Keith が解説します。', 'all': 'すべてのマーケットノート', 'archive': 'すべてのマーケットノート（新しい順）。',
           'take': 'Keith の見方', 'src': '出典：', 'earlier': '過去のノート', 'foot': '内容は Keith 個人の見解であり、投資助言ではありません。', 'ask': 'これについて Keith に相談 →'},
    'ko': {'eb': 'Keith의 마켓 노트', 'h2': '매일 1분, <em>시장</em> 읽기', 'p': '말레이시아 부동산과 경제의 변화, 그리고 구매자에게 주는 의미를 Keith가 정리합니다.', 'all': '전체 마켓 노트', 'archive': '모든 마켓 노트, 최신순.',
           'take': 'Keith의 시각', 'src': '출처:', 'earlier': '지난 노트', 'foot': 'Keith 개인의 의견이며 투자 조언이 아닙니다.', 'ask': '이 내용으로 Keith에게 문의 →'},
}

CSS = '''
.mn{padding:150px 5vw 64px;background:linear-gradient(180deg,#f6f5fc,#fff);border-bottom:1px solid var(--line);}
#market-notes ~ .journal-hero{padding-top:80px;}
.mn-w{max-width:1240px;margin:0 auto;}
.mn-h{margin-bottom:30px;} .mn-h .eyebrow{display:block;margin-bottom:10px;} .mn-h h2{font-size:clamp(28px,3.6vw,42px);line-height:1.15;} .mn-h h2 em{color:var(--gold);}
.mn-h p{color:var(--grey);font-size:14.5px;font-weight:500;max-width:600px;margin-top:8px;}
.mn-g{display:grid;grid-template-columns:1.35fr 1fr;gap:22px;align-items:start;}
.mn-g.solo{grid-template-columns:minmax(0,820px);}
.mn-f{background:#fff;border:1px solid var(--line);border-radius:22px;box-shadow:0 18px 44px rgba(29,27,79,.08);padding:30px 32px;position:relative;overflow:hidden;scroll-margin-top:90px;}
.mn-f:before{content:"";position:absolute;left:0;top:0;bottom:0;width:5px;background:linear-gradient(#5E60CE,#9a98f0);}
.mn-by{display:flex;align-items:center;gap:12px;margin-bottom:18px;}
.mn-by img{width:46px;height:46px;border-radius:50%;object-fit:cover;object-position:center 15%;border:2px solid #fff;box-shadow:0 0 0 2px rgba(94,96,206,.35);}
.mn-by b{display:block;font-size:14px;} .mn-by small{color:var(--grey);font-size:12px;font-weight:500;}
.mn-meta{display:flex;gap:10px;align-items:center;margin-bottom:10px;font-size:12px;font-weight:600;color:var(--grey);}
.mn-tag{background:#efeefb;color:var(--gold);font-weight:700;letter-spacing:.04em;padding:4px 10px;border-radius:100px;}
.mn-f h3{font-size:clamp(22px,2.4vw,28px);line-height:1.25;margin-bottom:12px;}
.mn-f p.mn-b{color:#3d3c55;font-size:15px;line-height:1.8;font-weight:500;white-space:pre-line;}
.mn-take{margin:18px 0 20px;background:#f6f5fc;border-radius:14px;padding:16px 18px;}
.mn-take span{display:block;font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin-bottom:6px;}
.mn-take p{font-size:14.5px;line-height:1.75;font-weight:600;color:#1d1b4f;white-space:pre-line;}
.mn-l{display:flex;flex-wrap:wrap;gap:10px;}
.mn-l a{font-size:13px;font-weight:700;padding:9px 16px;border-radius:100px;border:1px solid var(--line);background:#fff;transition:all .25s;}
.mn-l a:first-child{background:#111;color:#fff;border-color:#111;} .mn-l a:hover{border-color:var(--gold);color:var(--gold);} .mn-l a:first-child:hover{background:var(--gold);color:#fff;border-color:var(--gold);}
.mn-list{display:flex;flex-direction:column;gap:12px;}
.mn-list h4{font:700 12px Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--grey);margin-bottom:2px;}
.mn-i{all:unset;box-sizing:border-box;cursor:pointer;display:block;background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px 18px;transition:all .25s;}
.mn-i:hover,.mn-i.on{border-color:rgba(94,96,206,.5);box-shadow:0 10px 24px rgba(29,27,79,.08);} .mn-i.on{background:#f6f5fc;}
.mn-i small{display:flex;gap:8px;font-size:11.5px;font-weight:600;color:var(--grey);margin-bottom:5px;} .mn-i small i{font-style:normal;color:var(--gold);font-weight:700;}
.mn-i b{font-family:'Playfair Display',serif;font-size:17px;line-height:1.35;color:var(--ink);}
.mn-all{display:block;text-align:center;font-size:13px;font-weight:700;color:var(--gold);padding:12px;border:1px dashed rgba(94,96,206,.4);border-radius:14px;} .mn-all:hover{background:#f6f5fc;}
.mn-src{margin-top:16px;padding-top:12px;border-top:1px dashed var(--line);font-size:12.5px;color:var(--grey);font-weight:600;display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center;}
.mn-src a{color:var(--gold);font-weight:700;text-decoration:underline;text-underline-offset:3px;} .mn-src a:after{content:" ↗";text-decoration:none;}
.mn-foot{margin-top:24px;display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;font-size:12.5px;color:var(--grey);font-weight:500;}
.mn-foot a{font-weight:700;color:#1f9d55;}
@media(max-width:900px){.mn-g{grid-template-columns:1fr;} .mn-f{padding:24px 22px;} .mn{padding:120px 16px 48px;} #market-notes ~ .journal-hero{padding-top:60px;}}
'''

WA = 'https://api.whatsapp.com/send/?phone=60102821568&text=%28KNRE%29+Hi+Keith%2C+about+your+market+note+%22{t}%22...&type=phone_number&app_absent=0'


def pick(d, l):
    if isinstance(d, str):
        return d
    return d.get(l) or d.get('en') or next(iter(d.values()), '')


def src_html(n, l):
    ss = n.get('sources') or []
    if not ss:
        return ''
    return '<div class="mn-src"><span data-mn="src">%s</span>%s</div>' % (E(LBL[l]['src']), ''.join(
        '<a href="%s" target="_blank" rel="noopener nofollow">%s</a>' % (E(z['url']), E(z['name'])) for z in ss))


def section():
    en = LBL['en']
    n0 = NOTES[0]
    first = ('<div class="mn-by"><img src="images/4382969133d212d0.jpg" alt="Keith Nah"><div><b>Keith Nah 鈞晖</b><small>Keith Nah · REN 60517</small></div></div>'
             '<div class="mn-meta"><span class="mn-tag">%s</span><span>%s</span></div><h3>%s</h3><p class="mn-b">%s</p>'
             '<div class="mn-take"><span>%s</span><p>%s</p></div><div class="mn-l">%s</div>%s') % (
        E(pick(n0['area'], 'en')), E(n0['date']), E(pick(n0['title'], 'en')), E(pick(n0['body'], 'en')), E(en['take']), E(pick(n0['take'], 'en')),
        ''.join('<a href="%s">%s</a>' % (E(x['href']), E(pick(x['label'], 'en'))) for x in n0.get('links', [])), src_html(n0, 'en'))
    items = ''.join('<button type="button" class="mn-i%s" data-i="%d"><small><span>%s</span><i>%s</i></small><b>%s</b></button>' % (
        ' on' if i == 0 else '', i, E(n['date']), E(pick(n['area'], 'en')), E(pick(n['title'], 'en'))) for i, n in enumerate(RECENT))
    more = '<a class="mn-all" href="market-notes.html"><span data-mn="all">%s</span> (%d) →</a>' % (E(en['all']), len(NOTES))
    lst = '<div class="mn-list"><h4 data-mn="earlier">%s</h4>%s%s</div>' % (E(en['earlier']), items, more) if len(NOTES) > 1 else ''
    return ('<!-- KN-NOTES:START --><style>%s</style><section class="mn" id="market-notes"><div class="mn-w">'
            '<div class="mn-h"><span class="eyebrow" data-mn="eb">%s</span><h2 data-mn-h="h2">%s</h2><p data-mn="p">%s</p></div>'
            '<div class="mn-g%s"><article class="mn-f" id="mnF">%s</article>%s</div>'
            '<div class="mn-foot"><span data-mn="foot">%s</span><a id="mnAsk" href="%s" target="_blank" rel="noopener" data-mn="ask">%s</a></div></div></section>'
            '<script>(function(){var N=%s,L=%s,f=document.getElementById("mnF"),cur=0;'
            'function lg(){var l="en";try{l=(typeof currentLang!=="undefined"&&currentLang)||localStorage.getItem("kn_lang")||"en"}catch(e){}return L[l]?l:"en";}'
            'function p(d,l){return typeof d==="string"?d:(d[l]||d.en||"");}'
            'function e(s){var d=document.createElement("div");d.textContent=s;return d.innerHTML;}'
            'function fd(s,l){var d=new Date(s+"T12:00:00+08:00");try{return d.toLocaleDateString(l==="en"?"en-GB":l,{day:"numeric",month:"short",year:"numeric"});}catch(x){return s;}}'
            'function show(i){cur=i;var l=lg(),T=L[l],x=N[i];f.innerHTML=\'<div class="mn-by"><img src="images/4382969133d212d0.jpg" alt="Keith Nah"><div><b>Keith Nah 鈞晖</b><small>Keith Nah · REN 60517</small></div></div>'
            '<div class="mn-meta"><span class="mn-tag">\'+e(p(x.area,l))+\'</span><span>\'+e(fd(x.date,l))+\'</span></div><h3>\'+e(p(x.title,l))+\'</h3><p class="mn-b">\'+e(p(x.body,l))+\'</p>'
            '<div class="mn-take"><span>\'+e(T.take)+\'</span><p>\'+e(p(x.take,l))+\'</p></div><div class="mn-l">\'+(x.links||[]).map(function(a){return \'<a href="\'+a.href+\'">\'+e(p(a.label,l))+\'</a>\';}).join("")+\'</div>\'+((x.sources||[]).length?\'<div class="mn-src"><span>\'+e(T.src)+\'</span>\'+x.sources.map(function(z){return \'<a href="\'+e(z.url)+\'" target="_blank" rel="noopener nofollow">\'+e(z.name)+\'</a>\';}).join("")+\'</div>\':"");'
            'document.querySelectorAll(".mn-i").forEach(function(b){b.classList.toggle("on",+b.dataset.i===i);});'
            'var a=document.getElementById("mnAsk");if(a)a.href=%s.replace("{t}",encodeURIComponent(p(x.title,"en")));}'
            'function labels(){var l=lg(),T=L[l];document.querySelectorAll("[data-mn]").forEach(function(el){el.textContent=T[el.getAttribute("data-mn")];});'
            'document.querySelectorAll("[data-mn-h]").forEach(function(el){el.innerHTML=T[el.getAttribute("data-mn-h")];});'
            'document.querySelectorAll(".mn-i").forEach(function(b){var x=N[+b.dataset.i];b.querySelector("small span").textContent=fd(x.date,l);b.querySelector("small i").textContent=p(x.area,l);b.querySelector("b").textContent=p(x.title,l);});show(cur);}'
            'document.querySelectorAll(".mn-i").forEach(function(b){b.addEventListener("click",function(){show(+b.dataset.i);if(innerWidth<900)f.scrollIntoView({behavior:"smooth",block:"start"});});});'
            'document.addEventListener("DOMContentLoaded",function(){var s=window.setLanguage;if(typeof s==="function")window.setLanguage=function(){var r=s.apply(this,arguments);labels();return r;};labels();});'
            'labels();})();</script><!-- KN-NOTES:END -->\n') % (
        CSS, E(en['eb']), en['h2'], E(en['p']), '' if len(NOTES) > 1 else ' solo', first, lst, E(en['foot']),
        E(WA.replace('{t}', '')), E(en['ask']), json.dumps(RECENT, ensure_ascii=False).replace('</', '<\\/'), json.dumps(LBL, ensure_ascii=False),
        json.dumps(WA))


s = open('blog.html', encoding='utf-8').read()
s = re.sub(r'<!-- KN-NOTES:START -->.*?<!-- KN-NOTES:END -->\n', '', s, flags=re.S)
if NOTES:
    i = s.index('<!-- ===================== JOURNAL HERO')   # at the very top of the News page, above The Journal
    s = s[:i] + section() + s[i:]
open('blog.html', 'w', encoding='utf-8').write(s)


def archive():
    import sys
    sys.path.insert(0, HERE)
    import site_header as SH
    en = LBL['en']
    months = []
    for n in NOTES:
        m = n['date'][:7]
        if not months or months[-1][0] != m:
            months.append((m, []))
        months[-1][1].append(n)
    def card(n, k):
        return ('<article class="na" id="n-%s-%d" data-k="%d"><div class="mn-meta"><span class="mn-tag" data-f="area">%s</span><span data-d="%s">%s</span></div>'
                '<h2 data-f="title">%s</h2><p class="mn-b" data-f="body">%s</p><div class="mn-take"><span data-mn="take">%s</span><p data-f="take">%s</p></div>'
                '<div class="mn-l">%s</div>%s</article>') % (
            n['date'], k, k, E(pick(n['area'], 'en')), n['date'], n['date'], E(pick(n['title'], 'en')), E(pick(n['body'], 'en')), E(en['take']),
            E(pick(n['take'], 'en')), ''.join('<a href="%s" data-li="%d">%s</a>' % (E(x['href']), j, E(pick(x['label'], 'en'))) for j, x in enumerate(n.get('links', []))), src_html(n, 'en'))
    k = 0; body = ''
    for m, ns in months:
        body += '<section class="nm"><h3 class="nm-h" data-m="%s">%s</h3>' % (m, m)
        for n in ns:
            body += card(n, k); k += 1
        body += '</section>'
    css = CSS + '''
:root{--bg:#F7F6FB;--ink:#15142b;--grey:#5f5e74;--line:rgba(21,20,43,.09);--gold:#5E60CE;}
*{box-sizing:border-box;margin:0;padding:0;} body{font-family:Inter,system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6;}
a{color:inherit;text-decoration:none;} h1,h2,h3{font-family:'Playfair Display',Georgia,serif;line-height:1.25;}
.eyebrow{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);font-weight:700;}
.nw{max-width:860px;margin:0 auto;padding:56px 5vw 80px;} .nw h1{font-size:clamp(30px,4.4vw,46px);margin:8px 0 8px;} .nw > p{color:var(--grey);margin-bottom:26px;}
.nm{margin-top:34px;} .nm-h{font:800 13px Inter,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--grey);margin-bottom:14px;display:flex;gap:12px;align-items:center;}
.nm-h:after{content:"";flex:1;height:1px;background:var(--line);}
.na{background:#fff;border:1px solid var(--line);border-radius:20px;padding:26px 28px;margin-bottom:16px;scroll-margin-top:90px;}
.na h2{font-size:clamp(20px,2.4vw,25px);margin-bottom:10px;}
.back{display:block;width:fit-content;margin-bottom:18px;font-size:13px;font-weight:700;color:var(--gold);}
.na p.mn-b{color:#3d3c55;font-size:15px;line-height:1.8;font-weight:500;white-space:pre-line;} .na .mn-take p{white-space:pre-line;} .nw .eyebrow{display:block;}
footer{border-top:1px solid var(--line);padding:26px 5vw;font-size:13px;color:var(--grey);text-align:center;}
@media(max-width:640px){.na{padding:20px 18px;}}
'''
    js = ('<script>(function(){var N=%s,L=%s;function lg(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}return L[l]?l:"en";}'
          'function p(d,l){return typeof d==="string"?d:(d[l]||d.en||"");}'
          'function fd(s,l,o){var d=new Date(s+(s.length===7?"-15":"")+"T12:00:00+08:00");try{return d.toLocaleDateString(l==="en"?"en-GB":l,o);}catch(x){return s;}}'
          'function apply(){var l=lg(),T=L[l];document.querySelectorAll("[data-mn]").forEach(function(e){e.textContent=T[e.getAttribute("data-mn")];});'
          'document.querySelectorAll(".na").forEach(function(a){var n=N[+a.dataset.k];a.querySelectorAll("[data-f]").forEach(function(e){e.textContent=p(n[e.getAttribute("data-f")],l);});'
          'a.querySelectorAll("[data-li]").forEach(function(e){e.textContent=p(n.links[+e.getAttribute("data-li")].label,l);});});'
          'document.querySelectorAll("[data-d]").forEach(function(e){e.textContent=fd(e.getAttribute("data-d"),l,{day:"numeric",month:"short",year:"numeric"});});'
          'document.querySelectorAll("[data-m]").forEach(function(e){e.textContent=fd(e.getAttribute("data-m"),l,{month:"long",year:"numeric"});});'
          'document.title=T.all+" | Keith Nah Real Estate";}'
          'document.addEventListener("DOMContentLoaded",function(){var s=window.knSetLang;if(typeof s==="function")window.knSetLang=function(){var r=s.apply(this,arguments);apply();return r;};apply();});apply();})();</script>') % (
        json.dumps(NOTES, ensure_ascii=False).replace('</', '<\\/'), json.dumps(LBL, ensure_ascii=False))
    page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>All market notes | Keith Nah Real Estate</title>
<meta name="description" content="Keith Nah's daily notes on Malaysian property and the economy, and what each change means for buyers.">
<link rel="canonical" href="https://keithnah.com/market-notes.html">
<link rel="icon" type="image/png" href="images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
<style>%s</style>
</head>
<body>
<header>
  <a class="logo" href="./"><img src="images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Keith Nah Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="https://api.whatsapp.com/send/?phone=60102821568&amp;text=(KNRE)+Hi+Keith,+about+your+market+notes.&amp;type=phone_number&amp;app_absent=0" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
<main class="nw">
  <a class="back" href="blog.html#market-notes">← News</a>
  <span class="eyebrow" data-mn="eb">%s</span>
  <h1 data-mn="all">%s</h1>
  <p data-mn="archive">%s</p>
  %s
  <p class="mn-foot" style="margin-top:20px"><span data-mn="foot">%s</span></p>
</main>
<footer>&copy; 2026 Keith Nah Real Estate. All rights reserved.</footer>
<script src="lead-tracker.js"></script>
%s
</body>
</html>
''' % (css, E(en['eb']), E(en['all']), E(en['archive']), body, E(en['foot']), js)
    open('market-notes.html', 'w', encoding='utf-8').write(SH.apply(page, '', 'blog.html'))
    if os.path.exists('sitemap.xml'):
        sm = open('sitemap.xml', encoding='utf-8').read()
        sm = re.sub(r'  <url>\n    <loc>https://keithnah.com/market-notes.html</loc>.*?</url>\n', '', sm, flags=re.S)
        sm = sm.replace('</urlset>', '  <url>\n    <loc>https://keithnah.com/market-notes.html</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>0.7</priority>\n  </url>\n</urlset>' % NOTES[0]['date'])
        open('sitemap.xml', 'w', encoding='utf-8').write(sm)


if NOTES:
    archive()
print('market notes: %d (archive page market-notes.html)' % len(NOTES))
