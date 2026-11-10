"""Keith's Market Notes on the News page (blog.html).

Notes live in tools/market_notes.json, newest first:
  [{"date": "2026-11-11", "area": {"en": "Kuala Lumpur", "zh-CN": "吉隆坡", ...},
    "title": {lang: text}, "body": {lang: text}, "take": {lang: text},
    "links": [{"label": {lang: text}, "href": "article/....html"}]}]
Languages: en, zh-CN, zh-TW, ms, ja, ko (a missing language falls back to English).
The section sits right under the News hero and stays hidden while there are no notes.
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
NOTES = sorted(NOTES, key=lambda n: n['date'], reverse=True)[:30]

LBL = {
    'en': {'eb': "Keith's Market Notes", 'h2': 'One minute on the <em>market</em>, every day',
           'p': 'Short notes from Keith on what moved in Malaysian property and the economy, and what it means if you are buying.',
           'take': "Keith's take", 'earlier': 'Earlier notes', 'foot': "Opinions are Keith's own and are not financial advice.", 'ask': 'Ask Keith about this →'},
    'zh-CN': {'eb': 'Keith 每日市场短评', 'h2': '每天一分钟，看懂<em>房市</em>', 'p': 'Keith 每天用几句话说说马来西亚房产和经济的变化，以及对买家的意义。',
              'take': 'Keith 怎么看', 'earlier': '往期短评', 'foot': '以上为 Keith 的个人观点，并非投资建议。', 'ask': '就这个问 Keith →'},
    'zh-TW': {'eb': 'Keith 每日市場短評', 'h2': '每天一分鐘，看懂<em>房市</em>', 'p': 'Keith 每天用幾句話說說馬來西亞房產和經濟的變化，以及對買家的意義。',
              'take': 'Keith 怎麼看', 'earlier': '往期短評', 'foot': '以上為 Keith 的個人觀點，並非投資建議。', 'ask': '就這個問 Keith →'},
    'ms': {'eb': 'Nota Pasaran Keith', 'h2': 'Seminit tentang <em>pasaran</em>, setiap hari', 'p': 'Nota ringkas Keith tentang perkembangan hartanah dan ekonomi Malaysia, dan maksudnya untuk pembeli.',
           'take': 'Pandangan Keith', 'earlier': 'Nota terdahulu', 'foot': 'Pendapat ini milik Keith sendiri dan bukan nasihat kewangan.', 'ask': 'Tanya Keith tentang ini →'},
    'ja': {'eb': 'Keith のマーケットノート', 'h2': '毎日1分で<em>市場</em>がわかる', 'p': 'マレーシアの不動産と経済の動きと、購入者にとっての意味を Keith が短く解説します。',
           'take': 'Keith の見方', 'earlier': '過去のノート', 'foot': '内容は Keith 個人の見解であり、投資助言ではありません。', 'ask': 'これについて Keith に相談 →'},
    'ko': {'eb': 'Keith의 마켓 노트', 'h2': '매일 1분, <em>시장</em> 읽기', 'p': '말레이시아 부동산과 경제의 변화, 그리고 구매자에게 주는 의미를 Keith가 짧게 정리합니다.',
           'take': 'Keith의 시각', 'earlier': '지난 노트', 'foot': 'Keith 개인의 의견이며 투자 조언이 아닙니다.', 'ask': '이 내용으로 Keith에게 문의 →'},
}

CSS = '''
.mn{padding:72px 5vw 64px;background:linear-gradient(180deg,#f6f5fc,#fff);border-bottom:1px solid var(--line);}
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
.mn-f p.mn-b{color:#3d3c55;font-size:15px;line-height:1.75;font-weight:500;}
.mn-take{margin:18px 0 20px;background:#f6f5fc;border-radius:14px;padding:16px 18px;}
.mn-take span{display:block;font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin-bottom:6px;}
.mn-take p{font-size:14.5px;line-height:1.7;font-weight:600;color:#1d1b4f;}
.mn-l{display:flex;flex-wrap:wrap;gap:10px;}
.mn-l a{font-size:13px;font-weight:700;padding:9px 16px;border-radius:100px;border:1px solid var(--line);background:#fff;transition:all .25s;}
.mn-l a:first-child{background:#111;color:#fff;border-color:#111;} .mn-l a:hover{border-color:var(--gold);color:var(--gold);} .mn-l a:first-child:hover{background:var(--gold);color:#fff;border-color:var(--gold);}
.mn-list{display:flex;flex-direction:column;gap:12px;}
.mn-list h4{font:700 12px Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--grey);margin-bottom:2px;}
.mn-i{all:unset;box-sizing:border-box;cursor:pointer;display:block;background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px 18px;transition:all .25s;}
.mn-i:hover,.mn-i.on{border-color:rgba(94,96,206,.5);box-shadow:0 10px 24px rgba(29,27,79,.08);} .mn-i.on{background:#f6f5fc;}
.mn-i small{display:flex;gap:8px;font-size:11.5px;font-weight:600;color:var(--grey);margin-bottom:5px;} .mn-i small i{font-style:normal;color:var(--gold);font-weight:700;}
.mn-i b{font-family:'Playfair Display',serif;font-size:17px;line-height:1.35;color:var(--ink);}
.mn-foot{margin-top:24px;display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;font-size:12.5px;color:var(--grey);font-weight:500;}
.mn-foot a{font-weight:700;color:#1f9d55;}
@media(max-width:900px){.mn-g{grid-template-columns:1fr;} .mn-f{padding:24px 22px;} .mn{padding:52px 16px 48px;}}
'''

WA = 'https://api.whatsapp.com/send/?phone=60102821568&text=%28KNRE%29+Hi+Keith%2C+about+your+market+note+%22{t}%22...&type=phone_number&app_absent=0'


def pick(d, l):
    if isinstance(d, str):
        return d
    return d.get(l) or d.get('en') or next(iter(d.values()), '')


def section():
    en = LBL['en']
    n0 = NOTES[0]
    first = ('<div class="mn-by"><img src="images/4382969133d212d0.jpg" alt="Keith Nah"><div><b>Keith Nah 鈞晖</b><small>Keith Nah · REN 60517</small></div></div>'
             '<div class="mn-meta"><span class="mn-tag">%s</span><span>%s</span></div><h3>%s</h3><p class="mn-b">%s</p>'
             '<div class="mn-take"><span>%s</span><p>%s</p></div><div class="mn-l">%s</div>') % (
        E(pick(n0['area'], 'en')), E(n0['date']), E(pick(n0['title'], 'en')), E(pick(n0['body'], 'en')), E(en['take']), E(pick(n0['take'], 'en')),
        ''.join('<a href="%s">%s</a>' % (E(x['href']), E(pick(x['label'], 'en'))) for x in n0.get('links', [])))
    items = ''.join('<button type="button" class="mn-i%s" data-i="%d"><small><span>%s</span><i>%s</i></small><b>%s</b></button>' % (
        ' on' if i == 0 else '', i, E(n['date']), E(pick(n['area'], 'en')), E(pick(n['title'], 'en'))) for i, n in enumerate(NOTES[:8]))
    lst = '<div class="mn-list"><h4 data-mn="earlier">%s</h4>%s</div>' % (E(en['earlier']), items) if len(NOTES) > 1 else ''
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
            '<div class="mn-take"><span>\'+e(T.take)+\'</span><p>\'+e(p(x.take,l))+\'</p></div><div class="mn-l">\'+(x.links||[]).map(function(a){return \'<a href="\'+a.href+\'">\'+e(p(a.label,l))+\'</a>\';}).join("")+\'</div>\';'
            'document.querySelectorAll(".mn-i").forEach(function(b){b.classList.toggle("on",+b.dataset.i===i);});'
            'var a=document.getElementById("mnAsk");if(a)a.href=%s.replace("{t}",encodeURIComponent(p(x.title,"en")));}'
            'function labels(){var l=lg(),T=L[l];document.querySelectorAll("[data-mn]").forEach(function(el){el.textContent=T[el.getAttribute("data-mn")];});'
            'document.querySelectorAll("[data-mn-h]").forEach(function(el){el.innerHTML=T[el.getAttribute("data-mn-h")];});'
            'document.querySelectorAll(".mn-i").forEach(function(b){var x=N[+b.dataset.i];b.querySelector("small span").textContent=fd(x.date,l);b.querySelector("small i").textContent=p(x.area,l);b.querySelector("b").textContent=p(x.title,l);});show(cur);}'
            'document.querySelectorAll(".mn-i").forEach(function(b){b.addEventListener("click",function(){show(+b.dataset.i);if(innerWidth<900)f.scrollIntoView({behavior:"smooth",block:"start"});});});'
            'document.addEventListener("DOMContentLoaded",function(){var s=window.setLanguage;if(typeof s==="function")window.setLanguage=function(){var r=s.apply(this,arguments);labels();return r;};labels();});'
            'labels();})();</script><!-- KN-NOTES:END -->\n') % (
        CSS, E(en['eb']), en['h2'], E(en['p']), '' if len(NOTES) > 1 else ' solo', first, lst, E(en['foot']),
        E(WA.replace('{t}', '')), E(en['ask']), json.dumps(NOTES, ensure_ascii=False).replace('</', '<\\/'), json.dumps(LBL, ensure_ascii=False),
        json.dumps(WA))


s = open('blog.html', encoding='utf-8').read()
s = re.sub(r'<!-- KN-NOTES:START -->.*?<!-- KN-NOTES:END -->\n', '', s, flags=re.S)
if NOTES:
    i = s.index('</section>') + len('</section>\n')   # right under the News hero
    s = s[:i] + section() + s[i:]
open('blog.html', 'w', encoding='utf-8').write(s)
print('market notes: %d' % len(NOTES))
