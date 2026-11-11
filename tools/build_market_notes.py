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
import sys as _sys
_sys.path.insert(0, HERE)
import note_links as NL
_PROJ = NL.projects()
NL.assign_pages(NOTES)
for _n in NOTES:
    _n['projects'] = [{'name': p['name'], 'href': 'property/%s.html' % p['slug']} for p in NL.related(_n, _PROJ)]
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
.mn-p{display:flex;flex-wrap:wrap;gap:8px 10px;align-items:center;margin-top:14px;font-size:12px;font-weight:700;color:var(--grey);}
.mn-p span{letter-spacing:.08em;text-transform:uppercase;font-size:11px;} .mn-p a{font-size:13px;font-weight:700;color:var(--gold);background:#f3f1fa;border-radius:100px;padding:6px 13px;} .mn-p a:hover{background:var(--gold);color:#fff;}
.mn-list{display:flex;flex-direction:column;gap:12px;}
.mn-list h4{font:700 12px Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--grey);margin-bottom:2px;}
.mn-i{all:unset;box-sizing:border-box;cursor:pointer;display:block;background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px 18px;transition:all .25s;}
.mn-i:hover,.mn-i.on{border-color:rgba(94,96,206,.5);box-shadow:0 10px 24px rgba(29,27,79,.08);} .mn-i.on{background:#f6f5fc;}
.mn-i small{display:flex;gap:8px;font-size:11.5px;font-weight:600;color:var(--grey);margin-bottom:5px;} .mn-i small i{font-style:normal;color:var(--gold);font-weight:700;}
.mn-i b{font-family:'Playfair Display',serif;font-size:17px;line-height:1.35;color:var(--ink);}
.mn-all{display:block;text-align:center;font-size:13px;font-weight:700;color:var(--gold);padding:12px;border:1px dashed rgba(94,96,206,.4);border-radius:14px;} .mn-all:hover{background:#f6f5fc;}
.mn-src{margin:-2px 0 12px;font-size:12.5px;color:var(--grey);font-weight:600;display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center;}
.mn-src a{color:var(--gold);font-weight:700;text-decoration:underline;text-underline-offset:3px;} .mn-src a:after{content:" ↗";text-decoration:none;}
.mn-foot{margin-top:24px;display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;font-size:12.5px;color:var(--grey);font-weight:500;}
.mn-foot a{font-weight:700;color:#1f9d55;}
@media(max-width:900px){.mn-g{grid-template-columns:1fr;} .mn-f{padding:24px 22px;} .mn{padding:120px 16px 48px;} #market-notes ~ .journal-hero{padding-top:60px;}}
'''

WA = 'https://api.whatsapp.com/send/?phone=60102821568&text=%28KNRE%29+Hi+Keith%2C+about+your+market+note+%22{t}%22...&type=phone_number&app_absent=0'


for _l, _v in NL.LBL.items():
    LBL[_l]['proj'] = _v


def proj_html(n, l, attr=''):
    ps = n.get('projects') or []
    if not ps:
        return ''
    return '<div class="mn-p"><span%s>%s</span>%s</div>' % (attr, E(LBL[l]['proj']), ''.join('<a href="%s">%s</a>' % (E(x['href']), E(x['name'])) for x in ps))


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
             '<div class="mn-meta"><span class="mn-tag">%s</span><span>%s</span></div>%s<h3><a href="%s">%s</a></h3><p class="mn-b">%s</p>'
             '<div class="mn-take"><span>%s</span><p>%s</p></div><div class="mn-l">%s</div>%s') % (
        E(pick(n0['area'], 'en')), E(n0['date']), src_html(n0, 'en'), E(n0['_page']), E(pick(n0['title'], 'en')), E(pick(n0['body'], 'en')), E(en['take']), E(pick(n0['take'], 'en')),
        ''.join('<a href="%s">%s</a>' % (E(x['href']), E(pick(x['label'], 'en'))) for x in n0.get('links', [])), proj_html(n0, 'en'))
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
            '<div class="mn-meta"><span class="mn-tag">\'+e(p(x.area,l))+\'</span><span>\'+e(fd(x.date,l))+\'</span></div>\'+((x.sources||[]).length?\'<div class="mn-src"><span>\'+e(T.src)+\'</span>\'+x.sources.map(function(z){return \'<a href="\'+e(z.url)+\'" target="_blank" rel="noopener nofollow">\'+e(z.name)+\'</a>\';}).join("")+\'</div>\':"")+\'<h3><a href="\'+e(x._page)+\'">\'+e(p(x.title,l))+\'</a></h3><p class="mn-b">\'+e(p(x.body,l))+\'</p>'
            '<div class="mn-take"><span>\'+e(T.take)+\'</span><p>\'+e(p(x.take,l))+\'</p></div><div class="mn-l">\'+(x.links||[]).map(function(a){return \'<a href="\'+a.href+\'">\'+e(p(a.label,l))+\'</a>\';}).join("")+\'</div>\'+((x.projects||[]).length?\'<div class="mn-p"><span>\'+e(T.proj)+\'</span>\'+x.projects.map(function(q){return \'<a href="\'+e(q.href)+\'">\'+e(q.name)+\'</a>\';}).join("")+\'</div>\':"");'
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


def ld_json():
    """Structured data: each note as a NewsArticle by Keith Nah, with its own address on the archive page."""
    items, k = [], 0
    for n in NOTES:
        if k < 40:
            body = pick(n['body'], 'en')
            items.append({'@type': 'ListItem', 'position': k + 1, 'item': {
                '@type': 'NewsArticle', 'headline': pick(n['title'], 'en')[:110],
                'datePublished': n['date'] + 'T12:00:00+08:00', 'dateModified': n['date'] + 'T12:00:00+08:00',
                'url': 'https://keithnah.com/market-notes.html#n-%s-%d' % (n['date'], k),
                'description': body.split('\n\n')[0][:300], 'articleSection': pick(n['area'], 'en'), 'inLanguage': 'en',
                'author': {'@type': 'Person', 'name': 'Keith Nah', 'url': 'https://keithnah.com/about-keith.html'},
                'publisher': {'@type': 'Organization', 'name': 'Keith Nah Real Estate', 'logo': {'@type': 'ImageObject', 'url': 'https://keithnah.com/apple-touch-icon.png'}},
                'isBasedOn': [s['url'] for s in n.get('sources', [])]}})
        k += 1
    return json.dumps({'@context': 'https://schema.org', '@type': 'ItemList', 'name': "Keith Nah's Market Notes", 'itemListElement': items}, ensure_ascii=False).replace('</', '<\\/')


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
        return ('<article class="na" id="n-%s-%d" data-k="%d"><div class="mn-meta"><span class="mn-tag" data-f="area">%s</span><span data-d="%s">%s</span></div>%s'
                '<h2><a href="%s" data-f="title">%s</a></h2><p class="mn-b" data-f="body">%s</p><div class="mn-take"><span data-mn="take">%s</span><p data-f="take">%s</p></div>'
                '<div class="mn-l">%s</div>%s</article>') % (
            n['date'], k, k, E(pick(n['area'], 'en')), n['date'], n['date'], src_html(n, 'en'), E(n['_page']), E(pick(n['title'], 'en')), E(pick(n['body'], 'en')), E(en['take']),
            E(pick(n['take'], 'en')), ''.join('<a href="%s" data-li="%d">%s</a>' % (E(x['href']), j, E(pick(x['label'], 'en'))) for j, x in enumerate(n.get('links', []))), proj_html(n, 'en', ' data-mn="proj"'))
    k = 0; cards = ''; lst = ''
    for m, ns in months:
        lst += '<h3 class="nl-h" data-m="%s">%s</h3>' % (m, m)
        for n in ns:
            cards += card(n, k)
            lst += ('<button type="button" class="nl-i" data-k="%d"><small><span data-d="%s">%s</span><i data-la="%d">%s</i></small>'
                    '<b data-lt="%d">%s</b></button>') % (k, n['date'], n['date'], k, E(pick(n['area'], 'en')), k, E(pick(n['title'], 'en')))
            k += 1
    body = ('<div class="nlay"><div class="nmain" id="nMain">%s</div><aside class="nside"><div class="nside-h"><span data-mn="all">%s</span> <em>%d</em></div>'
            '<div class="nlist" id="nList">%s</div></aside></div>') % (cards, E(LBL['en']['all']), len(NOTES), lst)
    css = CSS + '''
:root{--bg:#F7F6FB;--ink:#15142b;--grey:#5f5e74;--line:rgba(21,20,43,.09);--gold:#5E60CE;}
*{box-sizing:border-box;margin:0;padding:0;} body{font-family:Inter,system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6;}
a{color:inherit;text-decoration:none;} h1,h2,h3{font-family:'Playfair Display',Georgia,serif;line-height:1.25;}
.eyebrow{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);font-weight:700;}
.nw{max-width:1240px;margin:0 auto;padding:56px 5vw 80px;}
.nlay{display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:26px;align-items:start;margin-top:8px;}
.nmain .na{display:none;margin:0;} .nmain .na.on{display:block;animation:nIn .35s ease;}
@keyframes nIn{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:none;}}
.nside{position:sticky;top:96px;background:#fff;border:1px solid var(--line);border-radius:20px;overflow:hidden;box-shadow:0 12px 30px rgba(29,27,79,.06);}
.nside-h{padding:16px 18px;border-bottom:1px solid var(--line);font:800 13px Inter,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:var(--ink);display:flex;justify-content:space-between;align-items:center;}
.nside-h em{font-style:normal;background:#efeefb;color:var(--gold);border-radius:100px;padding:2px 10px;font-size:12px;}
.nlist{max-height:calc(100vh - 190px);overflow-y:auto;padding:8px 10px 14px;overscroll-behavior:contain;}
.nlist::-webkit-scrollbar{width:6px;} .nlist::-webkit-scrollbar-thumb{background:rgba(94,96,206,.3);border-radius:6px;}
.nl-h{font:800 11px Inter,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--grey);margin:12px 8px 8px;}
.nl-i{all:unset;box-sizing:border-box;cursor:pointer;display:block;width:100%;padding:12px 12px;border-radius:12px;border:1px solid transparent;transition:background .2s,border-color .2s;}
.nl-i:hover{background:#f6f5fc;} .nl-i.on{background:#f3f1fa;border-color:rgba(94,96,206,.45);}
.nl-i small{display:flex;gap:8px;font-size:11.5px;font-weight:600;color:var(--grey);margin-bottom:3px;} .nl-i small i{font-style:normal;color:var(--gold);font-weight:700;}
.nl-i b{display:block;font-family:'Playfair Display',serif;font-size:15.5px;line-height:1.35;color:var(--ink);}
@media(max-width:960px){.nlay{grid-template-columns:1fr;gap:16px;} .nside{position:static;order:-1;} .nlist{max-height:248px;} .nside-h{padding:12px 16px;}} .nw h1{font-size:clamp(30px,4.4vw,46px);margin:8px 0 8px;} .nw > p{color:var(--grey);margin-bottom:26px;}
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
          'document.querySelectorAll("[data-la]").forEach(function(e){e.textContent=p(N[+e.getAttribute("data-la")].area,l);});'
          'document.querySelectorAll("[data-lt]").forEach(function(e){e.textContent=p(N[+e.getAttribute("data-lt")].title,l);});'
          'document.title=T.all+" | Keith Nah Real Estate";}'
          'function show(k,scroll){var cs=document.querySelectorAll(".na"),f=null;cs.forEach(function(c){var on=+c.dataset.k===k;c.classList.toggle("on",on);if(on)f=c;});'
          'document.querySelectorAll(".nl-i").forEach(function(b){var on=+b.dataset.k===k;b.classList.toggle("on",on);if(on&&scroll!=="no"){var L2=document.getElementById("nList");var bt=b.offsetTop-L2.offsetTop;if(bt<L2.scrollTop||bt>L2.scrollTop+L2.clientHeight-60)L2.scrollTop=bt-60;}});'
          'if(f){try{history.replaceState(null,"","#"+f.id);}catch(e){}if(scroll==="top"){var m=document.getElementById("nMain");var y=m.getBoundingClientRect().top+pageYOffset-90;if(pageYOffset>y)scrollTo({top:y,behavior:"smooth"});}}}'
          'document.getElementById("nList").addEventListener("click",function(e){var b=e.target.closest(".nl-i");if(b)show(+b.dataset.k,"top");});'
          'function fromHash(){var h=location.hash.slice(1),el=h&&document.getElementById(h);show(el&&el.classList.contains("na")?+el.dataset.k:0,"list");}'
          'fromHash();addEventListener("hashchange",fromHash);'
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
<script type="application/ld+json">%s</script>
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
''' % (ld_json(), css, E(en['eb']), E(en['all']), E(en['archive']), body, E(en['foot']), js)
    open('market-notes.html', 'w', encoding='utf-8').write(SH.apply(page, '', 'blog.html'))
    if os.path.exists('sitemap.xml'):
        sm = open('sitemap.xml', encoding='utf-8').read()
        sm = re.sub(r'  <url>\n    <loc>https://keithnah.com/market-notes.html</loc>.*?</url>\n', '', sm, flags=re.S)
        sm = sm.replace('</urlset>', '  <url>\n    <loc>https://keithnah.com/market-notes.html</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>0.7</priority>\n  </url>\n</urlset>' % NOTES[0]['date'])
        open('sitemap.xml', 'w', encoding='utf-8').write(sm)


if NOTES:
    archive()


# ---------- one page per note: notes/<date>-<title words>.html (search engines can find each note) ----------
NP_LBL = {
    'en': {'home': 'Home', 'news': 'News', 'older': 'Older note', 'newer': 'Newer note', 'by': "Keith Nah's market note"},
    'zh-CN': {'home': '首页', 'news': '新闻', 'older': '上一则', 'newer': '下一则', 'by': 'Keith Nah 市场短评'},
    'zh-TW': {'home': '首頁', 'news': '新聞', 'older': '上一則', 'newer': '下一則', 'by': 'Keith Nah 市場短評'},
    'ms': {'home': 'Utama', 'news': 'Berita', 'older': 'Nota sebelumnya', 'newer': 'Nota seterusnya', 'by': 'Nota pasaran Keith Nah'},
    'ja': {'home': 'ホーム', 'news': 'ニュース', 'older': '前のノート', 'newer': '次のノート', 'by': 'Keith Nah のマーケットノート'},
    'ko': {'home': '홈', 'news': '뉴스', 'older': '이전 노트', 'newer': '다음 노트', 'by': 'Keith Nah의 마켓 노트'},
}
for _l in NP_LBL:
    NP_LBL[_l].update(LBL[_l])

NP_CSS = '''
:root{--bg:#F7F6FB;--ink:#15142b;--grey:#5f5e74;--line:rgba(21,20,43,.09);--gold:#5E60CE;}
*{box-sizing:border-box;margin:0;padding:0;} body{font-family:Inter,system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6;}
a{color:inherit;text-decoration:none;} h1,h2,h3{font-family:'Playfair Display',Georgia,serif;line-height:1.25;}
.nw{max-width:860px;margin:0 auto;padding:120px 5vw 80px;}
.bc{font-size:13px;color:var(--grey);font-weight:600;margin-bottom:18px;display:flex;flex-wrap:wrap;gap:6px;} .bc a{color:var(--gold);}
.na{background:#fff;border:1px solid var(--line);border-radius:22px;padding:32px 34px;box-shadow:0 18px 44px rgba(29,27,79,.08);position:relative;overflow:hidden;}
.na:before{content:"";position:absolute;left:0;top:0;bottom:0;width:5px;background:linear-gradient(#5E60CE,#9a98f0);}
.na h1{font-size:clamp(26px,3.6vw,38px);margin:4px 0 16px;}
.na p.mn-b{color:#3d3c55;font-size:16px;line-height:1.85;font-weight:500;white-space:pre-line;} .na .mn-take p{white-space:pre-line;font-size:15px;}
.pn{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:22px;}
.pn a{display:block;background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px 18px;transition:all .25s;}
.pn a:hover{border-color:var(--gold);box-shadow:0 10px 24px rgba(29,27,79,.08);}
.pn small{display:block;font-size:11.5px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin-bottom:4px;}
.pn b{font-family:'Playfair Display',serif;font-size:16px;line-height:1.35;} .pn .nx{text-align:right;grid-column:2;}
.np-cta{margin-top:22px;display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;font-size:13px;color:var(--grey);}
.np-cta a.wa{background:#25D366;color:#fff;font-weight:700;padding:12px 20px;border-radius:100px;font-size:14px;}
.np-cta a.all{color:var(--gold);font-weight:700;}
footer{border-top:1px solid var(--line);padding:26px 5vw;font-size:13px;color:var(--grey);text-align:center;}
@media(max-width:640px){.na{padding:24px 20px;} .pn{grid-template-columns:1fr;} .pn .nx{grid-column:1;text-align:left;}}
'''


def note_pages():
    import sys
    sys.path.insert(0, HERE)
    import site_header as SH
    from urllib.parse import quote_plus
    os.makedirs('notes', exist_ok=True)
    keep = set()
    en = NP_LBL['en']
    up = lambda h: h if h.startswith(('http', '/', '#')) else '../' + h
    for i, n in enumerate(NOTES):
        older = NOTES[i + 1] if i + 1 < len(NOTES) else None
        newer = NOTES[i - 1] if i > 0 else None
        url = 'https://keithnah.com/' + n['_page']
        title = pick(n['title'], 'en')
        first = pick(n['body'], 'en').split('\n\n')[0]
        wa = 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0' % quote_plus('(KNRE) Hi Keith, about your market note "%s"...' % title)
        links = ''.join('<a href="%s" data-li="%d">%s</a>' % (E(up(x['href'])), j, E(pick(x['label'], 'en'))) for j, x in enumerate(n.get('links', [])))
        projs = ''.join('<a href="../%s">%s</a>' % (E(x['href']), E(x['name'])) for x in n.get('projects', []))
        pn = ''
        if older:
            pn += '<a class="pv" href="../%s"><small data-mn="older">%s</small><b data-pt-o="1">%s</b></a>' % (E(older['_page']), E(en['older']), E(pick(older['title'], 'en')))
        if newer:
            pn += '<a class="nx" href="../%s"><small data-mn="newer">%s</small><b data-pt-n="1">%s</b></a>' % (E(newer['_page']), E(en['newer']), E(pick(newer['title'], 'en')))
        ld = [{'@context': 'https://schema.org', '@type': 'NewsArticle', 'headline': title[:110], 'description': first[:300],
               'datePublished': n['date'] + 'T12:00:00+08:00', 'dateModified': n['date'] + 'T12:00:00+08:00', 'mainEntityOfPage': url,
               'image': 'https://keithnah.com/images/4382969133d212d0.jpg', 'articleSection': pick(n['area'], 'en'),
               'author': {'@type': 'Person', 'name': 'Keith Nah', 'url': 'https://keithnah.com/about-keith.html'},
               'publisher': {'@type': 'Organization', 'name': 'Keith Nah Real Estate', 'logo': {'@type': 'ImageObject', 'url': 'https://keithnah.com/apple-touch-icon.png'}},
               'isBasedOn': [s['url'] for s in n.get('sources', [])]},
              {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
                  {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': 'https://keithnah.com/'},
                  {'@type': 'ListItem', 'position': 2, 'name': 'News', 'item': 'https://keithnah.com/blog.html'},
                  {'@type': 'ListItem', 'position': 3, 'name': 'Market notes', 'item': 'https://keithnah.com/market-notes.html'},
                  {'@type': 'ListItem', 'position': 4, 'name': title, 'item': url}]}]
        data = {'area': n['area'], 'title': n['title'], 'body': n['body'], 'take': n['take'], 'links': n.get('links', []),
                'o': older and older['title'], 'n': newer and newer['title']}
        js = ('<script>(function(){var N=%s,L=%s;function lg(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}return L[l]?l:"en";}'
              'function p(d,l){return !d?"":typeof d==="string"?d:(d[l]||d.en||"");}'
              'function go(){var l=lg(),T=L[l];document.querySelectorAll("[data-mn]").forEach(function(e){e.textContent=T[e.getAttribute("data-mn")];});'
              'document.querySelectorAll("[data-f]").forEach(function(e){e.textContent=p(N[e.getAttribute("data-f")],l);});'
              'document.querySelectorAll("[data-li]").forEach(function(e){e.textContent=p(N.links[+e.getAttribute("data-li")].label,l);});'
              'var o=document.querySelector("[data-pt-o]"),x=document.querySelector("[data-pt-n]");if(o)o.textContent=p(N.o,l);if(x)x.textContent=p(N.n,l);'
              'document.querySelectorAll("[data-d]").forEach(function(e){var d=new Date(e.getAttribute("data-d")+"T12:00:00+08:00");try{e.textContent=d.toLocaleDateString(l==="en"?"en-GB":l,{day:"numeric",month:"long",year:"numeric"});}catch(z){}});}'
              'go();document.addEventListener("DOMContentLoaded",function(){var s=window.knSetLang;if(typeof s==="function")window.knSetLang=function(){var r=s.apply(this,arguments);go();return r;};go();});})();</script>') % (
            json.dumps(data, ensure_ascii=False).replace('</', '<\\/'), json.dumps(NP_LBL, ensure_ascii=False))
        page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%s | Keith Nah</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s">
<meta property="og:type" content="article">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:url" content="%s">
<meta property="og:image" content="https://keithnah.com/images/4382969133d212d0.jpg">
<meta property="article:published_time" content="%sT12:00:00+08:00">
<link rel="icon" type="image/png" href="../images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">%s</script>
<style>%s</style>
</head>
<body>
<header>
  <a class="logo" href="../"><img src="../images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Keith Nah Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="%s" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
<main class="nw">
  <nav class="bc" aria-label="Breadcrumb"><a href="../" data-mn="home">%s</a><span>›</span><a href="../blog.html#market-notes" data-mn="news">%s</a><span>›</span><a href="../market-notes.html" data-mn="all">%s</a></nav>
  <article class="na">
    <div class="mn-meta"><span class="mn-tag" data-f="area">%s</span><time datetime="%s" data-d="%s">%s</time></div>
    %s
    <h1 data-f="title">%s</h1>
    <p class="mn-b" data-f="body">%s</p>
    <div class="mn-take"><span data-mn="take">%s</span><p data-f="take">%s</p></div>
    <div class="mn-l">%s</div>
    %s
  </article>
  <div class="pn">%s</div>
  <div class="np-cta"><span data-mn="foot">%s</span><span><a class="all" href="../market-notes.html" data-mn="all">%s</a> &nbsp; <a class="wa" href="%s" target="_blank" rel="noopener" data-mn="ask">%s</a></span></div>
</main>
<footer>&copy; 2026 Keith Nah Real Estate. All rights reserved.</footer>
<script src="../lead-tracker.js"></script>
%s
</body>
</html>
''' % (E(title), E(first[:300]), url, E(title), E(first[:300]), url, n['date'],
            json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'), CSS + NP_CSS, E(wa),
            E(en['home']), E(en['news']), E(en['all']), E(pick(n['area'], 'en')), n['date'], n['date'], n['date'],
            src_html(n, 'en'), E(title), E(pick(n['body'], 'en')), E(en['take']), E(pick(n['take'], 'en')), links,
            ('<div class="mn-p"><span data-mn="proj">%s</span>%s</div>' % (E(en['proj']), projs)) if projs else '',
            pn, E(en['foot']), E(en['all']), E(wa), E(en['ask']), js)
        page = SH.apply(page, '../', 'blog.html')
        open(n['_page'], 'w', encoding='utf-8').write(page)
        keep.add(os.path.basename(n['_page']))
    for f in os.listdir('notes'):
        if f.endswith('.html') and f not in keep:
            os.remove(os.path.join('notes', f))
    # sitemap: one entry per note page
    if os.path.exists('sitemap.xml'):
        sm = open('sitemap.xml', encoding='utf-8').read()
        sm = re.sub(r'  <url>\n    <loc>https://keithnah.com/notes/[^<]*</loc>.*?</url>\n', '', sm, flags=re.S)
        sm = sm.replace('</urlset>', ''.join('  <url>\n    <loc>https://keithnah.com/%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>\n' % (n['_page'], n['date']) for n in NOTES) + '</urlset>')
        open('sitemap.xml', 'w', encoding='utf-8').write(sm)
    print('note pages: %d' % len(keep))


if NOTES:
    note_pages()

print('market notes: %d (archive page market-notes.html)' % len(NOTES))


# ---------- home page: LED news ticker with the latest 1-2 days of notes ----------
def ticker():
    if not NOTES:
        return ''
    days = sorted({n['date'] for n in NOTES}, reverse=True)[:2]
    items = []
    k_all = {id(n): i for i, n in enumerate(NOTES)}
    for n in NOTES:
        if n['date'] in days:
            items.append(n)
    data = [{'d': n['date'], 'a': n['area'], 't': n['title'], 'k': k_all[id(n)], 'u': n['_page']} for n in items]
    lab = {'en': ['Market Notes', 'Live'], 'zh-CN': ['每日市场短评', '最新'], 'zh-TW': ['每日市場短評', '最新'], 'ms': ['Nota Pasaran', 'Terkini'],
           'ja': ['マーケットノート', '最新'], 'ko': ['마켓 노트', '최신']}
    def item_html(x, l):
        return ('<a class="tk-i" href="%s"><span class="tk-a">%s</span><span class="tk-t">%s</span><span class="tk-sep" aria-hidden="true">◆</span></a>') % (
            E(x['u']), E(pick(x['a'], l).upper() if l == 'en' else pick(x['a'], l)), E(pick(x['t'], l)))
    row = ''.join(item_html(x, 'en') for x in data)
    css = ('.tk{position:absolute;left:0;right:0;top:var(--tk-top,76px);z-index:3;display:flex;align-items:stretch;height:50px;background:#07071a;'
           'border-bottom:1px solid rgba(255,255,255,.08);box-shadow:0 10px 30px rgba(7,7,26,.22);overflow:hidden;font-family:"SFMono-Regular",Menlo,Consolas,"Liberation Mono",monospace;}'
           '.tk:before{content:"";position:absolute;inset:0;pointer-events:none;z-index:2;background-image:radial-gradient(rgba(255,255,255,.07) 1px,transparent 1.2px);background-size:4px 4px;}'
           '.tk:after{content:"";position:absolute;top:0;bottom:0;right:0;width:80px;pointer-events:none;z-index:2;background:linear-gradient(90deg,transparent,#07071a);}'
           '.tk-l{position:relative;z-index:3;flex-shrink:0;display:flex;align-items:center;gap:10px;padding:0 18px 0 20px;background:#5E60CE;color:#fff;'
           'font:800 12px Inter,sans-serif;letter-spacing:.12em;text-transform:uppercase;clip-path:polygon(0 0,100% 0,calc(100% - 14px) 100%,0 100%);padding-right:30px;}'
           '.tk-l i{width:8px;height:8px;border-radius:50%;background:#3dff8a;box-shadow:0 0 8px #3dff8a;animation:tkBlink 1.4s ease-in-out infinite;}'
           '.tk-l small{font-weight:600;opacity:.8;letter-spacing:.08em;}'
           '@keyframes tkBlink{50%{opacity:.25;}}'
           '.tk-v{position:relative;flex:1;overflow:hidden;display:flex;align-items:center;}'
           '.tk-r{display:flex;width:max-content;animation:tkRun var(--tk-dur,60s) linear infinite;will-change:transform;}'
           '.tk:hover .tk-r{animation-play-state:paused;}'
           '@keyframes tkRun{to{transform:translate3d(-50%,0,0);}}'
           '.tk-i{display:inline-flex;align-items:center;gap:12px;padding:0 4px 0 26px;white-space:nowrap;font-size:15px;letter-spacing:.04em;text-decoration:none;}'
           '.tk-a{color:#ffb547;font-weight:700;text-shadow:0 0 6px rgba(255,181,71,.75);}'
           '.tk-t{color:#7dffb0;font-weight:600;text-shadow:0 0 6px rgba(61,255,138,.6);}'
           '.tk-i:hover .tk-t{color:#fff;text-shadow:0 0 8px rgba(255,255,255,.8);}'
           '.tk-sep{color:#5E60CE;font-size:11px;padding-left:20px;text-shadow:0 0 6px rgba(94,96,206,.9);}'
           '@media(max-width:640px){.tk{height:42px;} .tk-l{font-size:10.5px;padding:0 24px 0 12px;gap:7px;} .tk-l small{display:none;} .tk-i{font-size:13px;padding-left:18px;gap:9px;} .tk-sep{padding-left:12px;}}'
           '@media(prefers-reduced-motion:reduce){.tk-r{animation:none;} .tk-v{overflow-x:auto;}}')
    js = ('<script>(function(){var D=%s,L=%s,r=document.getElementById("tkR"),lb=document.getElementById("tkL");if(!r)return;'
          'function lg(){var l="en";try{l=(typeof currentLang!=="undefined"&&currentLang)||localStorage.getItem("kn_lang")||"en"}catch(e){}return L[l]?l:"en";}'
          'function p(d,l){return typeof d==="string"?d:(d[l]||d.en||"");}function e(s){var d=document.createElement("div");d.textContent=s;return d.innerHTML;}'
          'function build(){var l=lg(),h=D.map(function(x){var a=p(x.a,l);return \'<a class="tk-i" href="\'+x.u+\'"><span class="tk-a">\'+e(l==="en"?a.toUpperCase():a)+\'</span><span class="tk-t">\'+e(p(x.t,l))+\'</span><span class="tk-sep" aria-hidden="true">◆</span></a>\';}).join("");'
          'var once=h;while(once.length<4000&&D.length)once+=h;r.innerHTML=once+once;lb.innerHTML=\'<i></i>\'+e(L[l][0])+\' <small>\'+e(L[l][1])+\'</small>\';'
          'requestAnimationFrame(function(){var w=r.scrollWidth/2;r.style.setProperty("--tk-dur",Math.max(25,w/55)+"s");});}'
          'function top(){var h=document.getElementById("siteHeader")||document.querySelector("header");var t=document.querySelector(".tk");if(h&&t)t.style.setProperty("--tk-top",h.getBoundingClientRect().height+"px");}top();addEventListener("resize",top);build();document.addEventListener("DOMContentLoaded",function(){var s=window.setLanguage;if(typeof s==="function")window.setLanguage=function(){var x=s.apply(this,arguments);build();return x;};build();});})();</script>') % (
        json.dumps(data, ensure_ascii=False).replace('</', '<\\/'), json.dumps(lab, ensure_ascii=False))
    return ('<!-- KN-TICKER:START --><style>%s</style><div class="tk" aria-label="Keith\'s latest market notes"><div class="tk-l" id="tkL"><i></i>Market Notes <small>Live</small></div>'
            '<div class="tk-v"><div class="tk-r" id="tkR">%s%s</div></div></div>%s<!-- KN-TICKER:END -->\n') % (css, row, row, js)


ix = open('index.html', encoding='utf-8').read()
ix = re.sub(r'<!-- KN-TICKER:START -->.*?<!-- KN-TICKER:END -->\n', '', ix, flags=re.S)
tk = ticker()
if tk:
    h0 = ix.index('<section class="hero" id="home">')
    h1 = ix.index('</section>', h0)
    ix = ix[:h1] + tk + ix[h1:]
open('index.html', 'w', encoding='utf-8').write(ix)
print('home ticker: %s' % ('on' if tk else 'off'))
