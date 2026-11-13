"""MM2H library and enquiry form.

- Every article in tools/mm2h_articles.json becomes its own page: mm2h/<slug>.html.
- mm2h.html gets an "MM2H Library" section (articles in two groups) and an MM2H enquiry form
  under the tier comparison. The form saves the enquiry in the KNRE Leads sheet and Telegram
  (through lead-tracker.js, as a Quick Enquiry marked "MM2H"), then offers WhatsApp.
Articles and page labels in all 6 languages (tools/mm2h_articles_zh.json, tools/mm2h_articles_i18n.json).
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
sys.path.insert(0, HERE)
import site_header as SH

E = html.escape
A = json.load(open(os.path.join(HERE, 'mm2h_articles.json'), encoding='utf-8'))
GROUPS = [('guide', 'Understand MM2H', 'Tiers, costs, property rules and the steps, explained plainly.'),
          ('compare', 'MM2H vs other countries', 'How Malaysia compares with other long-stay and residency programmes.')]
WA = 'https://api.whatsapp.com/send/?phone=60102821568&type=phone_number&app_absent=0&text='

ART_CSS = '''
:root{--ink:#15142b;--grey:#5f5e74;--line:rgba(21,20,43,.09);--gold:#5E60CE;--bg:#F7F6FB;}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:Inter,sans-serif;background:var(--bg);color:var(--ink);line-height:1.7}a{color:inherit;text-decoration:none}.ma-src a{text-decoration:underline}
h1,h2{font-family:'Playfair Display',Georgia,serif;line-height:1.2}
.ma-top{background:linear-gradient(135deg,#1d1b4f,#3b3cb0);color:#fff;padding:120px 5vw 46px}
.ma-top .in{max-width:860px;margin:0 auto}.ma-cr{font-size:13px;opacity:.75}.ma-cr a{text-decoration:none}
.ma-tag{display:inline-block;margin:18px 0 12px;font-size:11.5px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;background:rgba(255,255,255,.14);padding:5px 12px;border-radius:999px}
.ma-top h1{font-size:clamp(28px,4.4vw,44px)}.ma-top p{margin-top:12px;font-size:17px;opacity:.85;max-width:720px}.ma-top small{display:block;margin-top:14px;opacity:.7;font-size:13px}
.ma{max-width:860px;margin:-26px auto 0;padding:0 5vw 60px;position:relative}
.ma-f{display:grid;grid-template-columns:repeat(4,1fr);background:#fff;border-radius:20px;box-shadow:0 18px 44px rgba(29,27,79,.12);overflow:hidden}
.ma-f div{padding:16px 18px;border-right:1px solid var(--line)}.ma-f div:last-child{border:0}.ma-f small{display:block;font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--grey)}
.ma-f b{font-size:15.5px}
.ma-s{display:grid;grid-template-columns:54px 1fr;gap:6px 18px;margin-top:38px}.ma-s i{font-style:normal;font:700 30px 'Playfair Display',Georgia,serif;color:#c9c6f2;line-height:1}
.ma-s h2{font-size:24px;margin-bottom:6px}.ma-s p{color:#33324a;font-size:16px}
.ma-k{margin-top:40px;background:#fff;border-left:5px solid var(--gold);border-radius:16px;padding:22px 24px;display:grid;grid-template-columns:56px 1fr;gap:16px;align-items:start}
.ma-k img{width:56px;height:56px;border-radius:50%;background:#15142b}.ma-k b{display:block;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin-bottom:4px}.ma-k p{font-size:15.5px}
.ma-src{margin-top:30px;font-size:13px;color:var(--grey)}.ma-src a{color:var(--gold)}.ma-src li{margin:3px 0 0 18px}
.ma-nt{margin-top:14px;font-size:12.5px;color:var(--grey)}
.ma-cta{margin-top:30px;display:flex;gap:10px;flex-wrap:wrap}.ma-cta a{flex:1 1 240px;text-align:center;padding:14px;border-radius:14px;font-weight:700;text-decoration:none}
.ma-cta .w{background:#25D366;color:#fff}.ma-cta .f{border:1.5px solid #d9d6ea;background:#fff}
.ma-rel{margin-top:40px}.ma-rel h3{font:700 20px 'Playfair Display',Georgia,serif;margin-bottom:10px}.ma-rel a{display:block;padding:12px 16px;background:#fff;border:1px solid var(--line);border-radius:12px;margin-bottom:8px;text-decoration:none;font-weight:600}
.ma-rel a:hover{border-color:var(--gold);color:var(--gold)}
footer{border-top:1px solid var(--line);padding:26px 5vw;font-size:13px;color:var(--grey);text-align:center}
@media(max-width:700px){.ma-f{grid-template-columns:1fr 1fr}.ma-f div:nth-child(2){border-right:0}.ma-f div:nth-child(-n+2){border-bottom:1px solid var(--line)}.ma-s{grid-template-columns:34px 1fr}.ma-s i{font-size:22px}}
'''


def article_page(a):
    grp = dict((g, t) for g, t, _ in GROUPS)[a['group']]
    facts = ''.join('<div><small>%s</small><b>%s</b></div>' % (E(k), E(v)) for k, v in a['facts'])
    secs = ''.join('<section class="ma-s"><i>%02d</i><div><h2>%s</h2><p>%s</p></div></section>' % (k + 1, E(h), E(p)) for k, (h, p) in enumerate(a['sections']))
    src = ''.join('<li><a href="%s" target="_blank" rel="noopener nofollow">%s</a></li>' % (E(u), E(n)) for n, u in a['sources'])
    rel = ''.join('<a href="%s.html">%s →</a>' % (x['slug'], E(x['title'])) for x in A if x['slug'] != a['slug'])
    wa = WA + 'Hi+Keith%2C+I+read+your+MM2H+article+and+have+a+question.'
    ld = json.dumps({'@context': 'https://schema.org', '@type': 'Article', 'headline': a['title'], 'description': a['desc'],
                     'author': {'@type': 'Person', 'name': 'Keith Nah'}, 'publisher': {'@type': 'Organization', 'name': 'Keith Nah Real Estate'},
                     'mainEntityOfPage': 'https://keithnah.com/mm2h/%s.html' % a['slug']}, ensure_ascii=False)
    page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Keith Nah</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://keithnah.com/mm2h/{slug}.html">
<meta property="og:type" content="article"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<link rel="icon" type="image/png" href="../images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{ld}</script>
<style>{css}</style>
</head>
<body>
<header>
  <a class="logo" href="../"><img src="../images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Malaysia Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="{wa}" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
<div class="ma-top"><div class="in"><div class="ma-cr"><a href="../">Home</a> › <a href="../mm2h.html">MM2H</a> › {grp}</div>
<span class="ma-tag">{grp}</span><h1>{title}</h1><p>{desc}</p><small data-mr="{read}">By Keith Nah · {read} min read</small></div></div>
<main class="ma"><div class="ma-f">{facts}</div>{secs}
<div class="ma-k"><img src="../images/f304c8479b1fe873.png" alt=""><div><b>Keith's take</b><p>{take}</p></div></div>
<div class="ma-src"><b>Sources</b><ul>{src}</ul></div>
<p class="ma-nt">MM2H terms are set by the Malaysian government and change from time to time. This article is a guide, not immigration or tax advice; confirm the current rules with a licensed MM2H agent.</p>
<div class="ma-cta"><a class="w" href="{wa}" target="_blank" rel="noopener">Ask Keith on WhatsApp</a><a class="f" href="../mm2h.html#enquire">Fill in the MM2H enquiry form</a></div>
<div class="ma-rel"><h3>More from the MM2H library</h3>{rel}<a href="../mm2h.html#library">All MM2H articles →</a></div>
</main>
<footer></footer>
<script src="../lead-tracker.js"></script>
</body>
</html>
'''.format(title=E(a['title']), desc=E(a['desc']), slug=a['slug'], css=ART_CSS, ld=ld, wa=E(wa), grp=E(grp), read=a['read'],
           facts=facts, secs=secs, take=E(a['take']), src=src, rel=rel)
    return SH.apply(page, '../', 'mm2h.html')


LIB_CSS = '''<style>
.ml{max-width:1180px;margin:0 auto;padding:80px 5vw 20px}.ml .eb,.me .eb{display:block;font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:#5E60CE;font-weight:800}
.ml h2{font-family:'Playfair Display',Georgia,serif;font-size:clamp(28px,3.6vw,40px);line-height:1.2;margin:6px 0 8px}.ml .ld{color:#5f5e74;max-width:680px}
.ml-tabs{display:flex;gap:8px;margin:24px 0 18px;flex-wrap:wrap}.ml-tabs button{border:1.5px solid #dcd9ee;background:#fff;border-radius:999px;padding:10px 18px;font:700 14px Inter,sans-serif;color:#15142b;cursor:pointer}
.ml-tabs button.on{background:#15142b;border-color:#15142b;color:#fff}.ml-tabs button i{font-style:normal;opacity:.6;margin-left:6px}
.ml-g p.gd{color:#5f5e74;font-size:14px;margin-bottom:14px}
.ml-l{display:grid;grid-template-columns:1fr 1fr;gap:0 34px;border-top:1px solid rgba(21,20,43,.09)}
.ml-a{display:grid;grid-template-columns:46px 1fr 26px;gap:14px;align-items:center;padding:18px 4px;border-bottom:1px solid rgba(21,20,43,.09);text-decoration:none;color:#15142b;transition:background .2s}
.ml-a:hover{background:#f3f1ff}.ml-a i{font-style:normal;font:700 22px 'Playfair Display',Georgia,serif;color:#5E60CE}
.ml-a b{display:block;font-size:16px;line-height:1.35}.ml-a small{display:block;color:#5f5e74;font-size:13px;margin-top:3px}.ml-a span{color:#5E60CE;font-size:20px;transition:transform .2s}.ml-a:hover span{transform:translateX(4px)}
.me{max-width:1180px;margin:0 auto;padding:70px 5vw 90px}.me-in{display:grid;grid-template-columns:.9fr 1.1fr;gap:36px;background:#15142b;color:#fff;border-radius:28px;padding:40px;overflow:hidden}
.me-in h2{font-family:'Playfair Display',Georgia,serif;font-size:clamp(28px,3.4vw,38px);line-height:1.2;margin:6px 0 12px}.me-in .eb{color:#a9a7ff}.me-in>div:first-child p{color:rgba(255,255,255,.7);font-size:15px}
.me-in ul{margin:18px 0 0;padding:0;list-style:none}.me-in li{padding:8px 0 8px 28px;position:relative;color:rgba(255,255,255,.85);font-size:14.5px}.me-in li:before{content:"✓";position:absolute;left:0;color:#25D366;font-weight:800}
.me-f{background:#fff;color:#15142b;border-radius:20px;padding:24px;display:grid;grid-template-columns:1fr 1fr;gap:12px}
.me-f label{display:block;font-size:11.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#5f5e74;margin-bottom:5px}
.me-f input,.me-f select,.me-f textarea{width:100%;border:1.5px solid #dcd9ee;border-radius:12px;padding:11px 12px;font:500 14.5px Inter,sans-serif;color:#15142b;background:#fff}
.me-f input:focus,.me-f select:focus,.me-f textarea:focus{outline:0;border-color:#5E60CE}.me-f .full{grid-column:1/-1}.me-f .ph{display:grid;grid-template-columns:96px 1fr;gap:8px}
.me-f textarea{min-height:84px;resize:vertical}.me-f button{grid-column:1/-1;border:0;border-radius:14px;padding:15px;background:#5E60CE;color:#fff;font:700 15.5px Inter,sans-serif;cursor:pointer}
.me-f button:hover{background:#4a4cc0}.me-f .er{grid-column:1/-1;color:#c0392b;font-size:13px}.me-f .nt{grid-column:1/-1;font-size:12px;color:#5f5e74}
.me-ok{grid-column:1/-1;text-align:center;padding:20px 6px}.me-ok b{display:block;font:700 24px 'Playfair Display',Georgia,serif;margin-bottom:6px}.me-ok p{color:#5f5e74;font-size:14.5px}
.me-ok a{display:inline-block;margin-top:14px;background:#25D366;color:#fff;font-weight:700;padding:13px 22px;border-radius:14px;text-decoration:none}
@media(max-width:900px){.ml-l{grid-template-columns:1fr}.me-in{grid-template-columns:1fr;padding:26px}}
@media(max-width:520px){.me-f{grid-template-columns:1fr;padding:18px}.me{padding:50px 16px 70px}}
</style>'''


def library():
    tabs, panes = '', ''
    for k, (g, name, d) in enumerate(GROUPS):
        items = [a for a in A if a['group'] == g]
        tabs += '<button type="button" data-g="%s"%s><span>%s</span><i>%d</i></button>' % (g, ' class="on"' if k == 0 else '', E(name), len(items))
        lst = ''.join('<a class="ml-a" href="mm2h/%s.html"><i>%02d</i><div><b>%s</b><small>%s</small></div><span>→</span></a>'
                      % (a['slug'], n + 1, E(a['title']), E(a['desc']))
                      for n, a in enumerate(items))
        panes += '<div class="ml-g" data-g="%s"%s><p class="gd">%s</p><div class="ml-l">%s</div></div>' % (g, '' if k == 0 else ' hidden', E(d), lst)
    return ('<section class="ml" id="library"><span class="eb">MM2H Library</span><h2>Read before you apply</h2>'
            '<p class="ld">Short, plain-English articles on how MM2H works, what it costs and how it compares with other countries. Written by Keith from what his clients ask.</p>'
            '<div class="ml-tabs">%s</div>%s</section>') % (tabs, panes)


def sel(name, label, opts):
    return '<div><label for="me_%s">%s</label><select id="me_%s" name="%s"><option value="">Choose</option>%s</select></div>' % (
        name, E(label), name, name, ''.join('<option>%s</option>' % E(o) for o in opts))


FORM = ('<section class="me" id="enquire"><div class="me-in"><div><span class="eb">MM2H enquiry</span><h2>Tell Keith about your MM2H plan</h2>'
        '<p>Share a few details and Keith will reply within a day with homes that meet your tier, the area that suits your family, and the next steps.</p>'
        '<ul><li>Homes that meet both the MM2H and the foreign buyer minimum</li><li>Introduction to a licensed MM2H agent for the application</li><li>Help with the purchase, from booking to keys</li></ul></div>'
        '<form class="me-f" id="meForm" novalidate>'
        '<div class="full"><label for="me_name">Full name *</label><input id="me_name" name="name" autocomplete="name" required></div>'
        '<div class="full"><label for="me_phone">WhatsApp number *</label><div class="ph"><input name="code" value="+60" aria-label="Country code" autocomplete="tel-country-code"><input id="me_phone" name="phone" type="tel" autocomplete="tel-national" required></div></div>'
        '<div class="full"><label for="me_email">Email</label><input id="me_email" name="email" type="email" autocomplete="email"></div>'
        '<div><label for="me_nat">Nationality</label><input id="me_nat" name="nat" autocomplete="country-name"></div>'
        + sel('age', 'Age of main applicant', ['21 to 24', '25 to 34', '35 to 49', '50 to 59', '60 or above'])
        + sel('who', 'Who is moving', ['Just me', 'Me and my partner', 'Family with children', 'Family with parents'])
        + sel('tier', 'Programme of interest', ['Not sure yet', 'Silver', 'Gold', 'Platinum', 'Johor Forest City SFZ', 'Sarawak S-MM2H', 'Sabah MM2H'])
        + sel('area', 'Preferred area', ['Not sure yet', 'Kuala Lumpur', 'Selangor', 'Penang', 'Johor Bahru', 'Sabah', 'Sarawak'])
        + sel('budget', 'Property budget', ['RM500,000 to RM600,000', 'RM600,000 to RM1 million', 'RM1 million to RM2 million', 'Above RM2 million'])
        + sel('when', 'When would you like to move', ['Within 6 months', '6 to 12 months', '1 to 2 years', 'Just exploring'])
        + '<div class="full"><label for="me_msg">Anything else Keith should know</label><textarea id="me_msg" name="msg"></textarea></div>'
        '<p class="er" role="alert"></p><button type="submit">Send my MM2H enquiry</button>'
        '<p class="nt"><span>By sending, you agree to our Privacy Policy. Keith only uses your details to reply to this enquiry.</span> <a href="privacy-policy.html">Privacy Policy</a></p></form></div></section>')

JS = r'''<script>(function(){
document.querySelectorAll(".ml-tabs button").forEach(function(b){b.addEventListener("click",function(){var g=b.getAttribute("data-g");
document.querySelectorAll(".ml-tabs button").forEach(function(x){x.classList.toggle("on",x===b);});document.querySelectorAll(".ml-g").forEach(function(p){p.hidden=p.getAttribute("data-g")!==g;});});});
var f=document.getElementById("meForm");if(!f)return;var L={nat:"Nationality",age:"Age",who:"Who is moving",tier:"Programme",area:"Preferred area",budget:"Property budget",when:"Timing",msg:"Notes"};
f.addEventListener("submit",function(ev){ev.preventDefault();var v=function(n){return (f.elements[n].value||"").trim();},er=f.querySelector(".er"),d=v("phone").replace(/[^0-9]/g,"");
if(!v("name")||d.length<6){er.textContent="Please add your name and WhatsApp number.";return;}er.textContent="";
var lines=["(KNRE) Hi Keith, I filled in the MM2H enquiry form on your website.","Name: "+v("name"),"WhatsApp: "+v("code")+" "+v("phone")];if(v("email"))lines.push("Email: "+v("email"));
["nat","age","who","tier","area","budget","when","msg"].forEach(function(n){if(v(n))lines.push(L[n]+": "+v(n));});var msg=lines.join("\n"),nm=v("name").replace(/[<>&"]/g,"");
if(typeof window.knLead==="function")window.knLead({type:"Quick Enquiry",button:"MM2H enquiry form",name:v("name"),code:v("code"),phone:v("phone"),email:v("email"),area:v("area"),look:"MM2H"+(v("tier")?": "+v("tier"):""),message:msg});
f.innerHTML='<div class="me-ok"><b>Thank you, '+nm+'</b><p>Keith has your MM2H enquiry and will reply on WhatsApp within a day. Want to start the chat now?</p><a target="_blank" rel="noopener" href="https://api.whatsapp.com/send/?phone=60102821568&type=phone_number&app_absent=0&text='+encodeURIComponent(msg)+'">Message Keith on WhatsApp</a></div>';});})();</script>'''



# ---------- translations: every element whose whole text is a known English phrase gets data-mt ----------
import opencc
_cc = opencc.OpenCC('s2tw').convert
CH = {  # en: [zh-CN, ms, ja, ko]
 'Understand MM2H': ['了解 MM2H', 'Fahami MM2H', 'MM2H を知る', 'MM2H 이해하기'],
 'MM2H vs other countries': ['MM2H 对比其他国家', 'MM2H berbanding negara lain', 'MM2H と他国の比較', 'MM2H vs 다른 나라'],
 'Tiers, costs, property rules and the steps, explained plainly.': ['等级、费用、买房规定和申请步骤，用简单的话说清楚。', 'Tahap, kos, peraturan hartanah dan langkah, diterangkan dengan mudah.', '各ティア、費用、不動産のルール、手続きをわかりやすく解説。', '등급, 비용, 부동산 규정, 절차를 쉽게 설명합니다.'],
 'How Malaysia compares with other long-stay and residency programmes.': ['马来西亚和其他国家长住、居留计划的比较。', 'Perbandingan Malaysia dengan program tinggal lama dan residensi lain.', 'マレーシアと他国の長期滞在・居住プログラムの比較。', '말레이시아와 다른 나라 장기 체류·거주 프로그램 비교.'],
 'MM2H Library': ['MM2H 文章库', 'Perpustakaan MM2H', 'MM2H ライブラリー', 'MM2H 라이브러리'],
 'Read before you apply': ['申请前先读', 'Baca sebelum memohon', '申請前に読む', '신청 전에 읽어 보세요'],
 'Short, plain-English articles on how MM2H works, what it costs and how it compares with other countries. Written by Keith from what his clients ask.': ['简短易懂的文章，说明 MM2H 怎么运作、要花多少钱，以及和其他国家怎么比。由 Keith 根据客户常问的问题撰写。', 'Artikel ringkas tentang cara MM2H berfungsi, kosnya dan perbandingannya dengan negara lain. Ditulis oleh Keith berdasarkan soalan pelanggannya.', 'MM2H の仕組み、費用、他国との比較を短くわかりやすくまとめた記事。お客様からよくある質問をもとに Keith が書いています。', 'MM2H의 작동 방식, 비용, 다른 나라와의 비교를 짧고 쉽게 정리한 글. 고객들의 질문을 바탕으로 Keith가 썼습니다.'],
 'MM2H enquiry': ['MM2H 咨询', 'Pertanyaan MM2H', 'MM2H のお問い合わせ', 'MM2H 문의'],
 'Tell Keith about your MM2H plan': ['告诉 Keith 你的 MM2H 计划', 'Beritahu Keith tentang rancangan MM2H anda', 'MM2H の計画を Keith に伝える', 'Keith에게 MM2H 계획을 알려 주세요'],
 'Share a few details and Keith will reply within a day with homes that meet your tier, the area that suits your family, and the next steps.': ['留下一些资料，Keith 会在一天内回复：符合你等级的房子、适合你家庭的地区，以及下一步。', 'Kongsi sedikit maklumat dan Keith akan membalas dalam sehari dengan rumah yang memenuhi tahap anda, kawasan yang sesuai untuk keluarga dan langkah seterusnya.', 'いくつか情報をお知らせいただければ、Keith が1日以内に、ティアに合う物件、ご家族に合うエリア、次のステップをご案内します。', '몇 가지 정보를 남기시면 Keith가 하루 안에 등급에 맞는 집, 가족에게 맞는 지역, 다음 단계를 알려 드립니다.'],
 'Homes that meet both the MM2H and the foreign buyer minimum': ['同时符合 MM2H 和外国人购房门槛的房子', 'Rumah yang memenuhi minimum MM2H dan pembeli asing', 'MM2H と外国人購入の最低価格の両方を満たす物件', 'MM2H와 외국인 구매 최저가를 모두 충족하는 집'],
 'Introduction to a licensed MM2H agent for the application': ['介绍持牌 MM2H 代理处理申请', 'Pengenalan kepada ejen MM2H berlesen untuk permohonan', '申請のための認可 MM2H エージェントのご紹介', '신청을 위한 공인 MM2H 에이전트 소개'],
 'Help with the purchase, from booking to keys': ['协助买房，从订房到交钥匙', 'Bantuan pembelian, dari tempahan hingga kunci', '予約から鍵の受け取りまで購入をサポート', '예약부터 열쇠 인도까지 구매 지원'],
 'Full name *': ['姓名 *', 'Nama penuh *', 'お名前 *', '성명 *'],
 'WhatsApp number *': ['WhatsApp 号码 *', 'Nombor WhatsApp *', 'WhatsApp 番号 *', 'WhatsApp 번호 *'],
 'Email': ['电邮', 'E-mel', 'メール', '이메일'],
 'Nationality': ['国籍', 'Kewarganegaraan', '国籍', '국적'],
 'Age of main applicant': ['主申请人年龄', 'Umur pemohon utama', '主申請者の年齢', '주 신청자 나이'],
 'Who is moving': ['谁一起搬来', 'Siapa yang berpindah', '移住する人', '이주하는 사람'],
 'Programme of interest': ['想申请的计划', 'Program yang diminati', '関心のあるプログラム', '관심 있는 프로그램'],
 'Preferred area': ['想住的地区', 'Kawasan pilihan', '希望エリア', '선호 지역'],
 'Property budget': ['买房预算', 'Bajet hartanah', '物件の予算', '부동산 예산'],
 'When would you like to move': ['想什么时候搬', 'Bila anda mahu berpindah', 'いつ頃移住したいですか', '언제 이주하고 싶으세요'],
 'Anything else Keith should know': ['还有什么要告诉 Keith', 'Apa-apa lagi yang Keith perlu tahu', 'Keith に伝えたいこと', 'Keith가 알아야 할 다른 내용'],
 'Choose': ['请选择', 'Pilih', '選択', '선택'],
 'Not sure yet': ['还不确定', 'Belum pasti', 'まだ決めていない', '아직 모르겠어요'],
 'Just me': ['只有我', 'Saya seorang', '自分だけ', '저 혼자'],
 'Me and my partner': ['我和伴侣', 'Saya dan pasangan', '自分とパートナー', '저와 배우자'],
 'Family with children': ['带孩子的家庭', 'Keluarga dengan anak', '子ども連れの家族', '자녀가 있는 가족'],
 'Family with parents': ['带父母的家庭', 'Keluarga dengan ibu bapa', '親と一緒の家族', '부모님과 함께하는 가족'],
 'Within 6 months': ['6 个月内', 'Dalam 6 bulan', '6か月以内', '6개월 이내'],
 '6 to 12 months': ['6 至 12 个月', '6 hingga 12 bulan', '6〜12か月', '6~12개월'],
 '1 to 2 years': ['1 至 2 年', '1 hingga 2 tahun', '1〜2年', '1~2년'],
 'Just exploring': ['只是了解一下', 'Sekadar meninjau', '情報収集中', '알아보는 중'],
 '60 or above': ['60 岁或以上', '60 atau lebih', '60歳以上', '60세 이상'],
 'Send my MM2H enquiry': ['送出我的 MM2H 咨询', 'Hantar pertanyaan MM2H saya', 'MM2H のお問い合わせを送信', 'MM2H 문의 보내기'],
 'By sending, you agree to our Privacy Policy. Keith only uses your details to reply to this enquiry.': ['送出即表示你同意我们的隐私政策。Keith 只会用你的资料回复这次咨询。', 'Dengan menghantar, anda bersetuju dengan Dasar Privasi kami. Keith hanya menggunakan maklumat anda untuk membalas pertanyaan ini.', '送信すると、プライバシーポリシーに同意したものとみなされます。いただいた情報はこのお問い合わせへの返信にのみ使います。', '보내시면 개인정보 처리방침에 동의하는 것으로 간주됩니다. Keith는 이 문의에 답하는 데만 정보를 사용합니다.'],
 'Privacy Policy': ['隐私政策', 'Dasar Privasi', 'プライバシーポリシー', '개인정보 처리방침'],
 '21 to 24': ['21 至 24 岁', '21 hingga 24', '21〜24歳', '21~24세'], '25 to 34': ['25 至 34 岁', '25 hingga 34', '25〜34歳', '25~34세'],
 '35 to 49': ['35 至 49 岁', '35 hingga 49', '35〜49歳', '35~49세'], '50 to 59': ['50 至 59 岁', '50 hingga 59', '50〜59歳', '50~59세'],
 'RM500,000 to RM600,000': ['RM50 万至 RM60 万', 'RM500,000 hingga RM600,000', 'RM50万〜RM60万', 'RM50만~RM60만'],
 'RM600,000 to RM1 million': ['RM60 万至 RM100 万', 'RM600,000 hingga RM1 juta', 'RM60万〜RM100万', 'RM60만~RM100만'],
 'RM1 million to RM2 million': ['RM100 万至 RM200 万', 'RM1 juta hingga RM2 juta', 'RM100万〜RM200万', 'RM100만~RM200만'],
 'Above RM2 million': ['RM200 万以上', 'Melebihi RM2 juta', 'RM200万超', 'RM200만 이상'],
 # article page chrome
 "Keith's take": ['Keith 的看法', 'Pandangan Keith', 'Keith の見解', 'Keith의 의견'],
 'Sources': ['资料来源', 'Sumber', '出典', '출처'],
 'Ask Keith on WhatsApp': ['WhatsApp 问 Keith', 'Tanya Keith di WhatsApp', 'WhatsApp で Keith に相談', 'WhatsApp으로 Keith에게 문의'],
 'Fill in the MM2H enquiry form': ['填写 MM2H 咨询表格', 'Isi borang pertanyaan MM2H', 'MM2H お問い合わせフォームに記入', 'MM2H 문의 양식 작성'],
 'More from the MM2H library': ['MM2H 文章库的其他文章', 'Lagi dari perpustakaan MM2H', 'MM2H ライブラリーの他の記事', 'MM2H 라이브러리의 다른 글'],
 'All MM2H articles →': ['全部 MM2H 文章 →', 'Semua artikel MM2H →', 'MM2H の記事一覧 →', '모든 MM2H 글 →'],
 'MM2H terms are set by the Malaysian government and change from time to time. This article is a guide, not immigration or tax advice; confirm the current rules with a licensed MM2H agent.': ['MM2H 条件由马来西亚政府制定，会不时更改。本文仅供参考，不构成移民或税务建议；请向持牌 MM2H 代理确认最新规定。', 'Syarat MM2H ditetapkan oleh kerajaan Malaysia dan berubah dari semasa ke semasa. Artikel ini panduan, bukan nasihat imigresen atau cukai; sahkan peraturan terkini dengan ejen MM2H berlesen.', 'MM2H の条件はマレーシア政府が定め、随時変更されます。本記事は参考情報であり、移民や税務の助言ではありません。最新のルールは認可 MM2H エージェントにご確認ください。', 'MM2H 조건은 말레이시아 정부가 정하며 수시로 바뀝니다. 이 글은 참고용이며 이민·세무 자문이 아닙니다. 최신 규정은 공인 MM2H 에이전트에게 확인하세요.'],
}
TR = {}
for en, v in CH.items():
    TR[E(en)] = {'zh-CN': v[0], 'zh-TW': _cc(v[0]), 'ms': v[1], 'ja': v[2], 'ko': v[3]}
ZH = json.load(open(os.path.join(HERE, 'mm2h_articles_zh.json'), encoding='utf-8'))
for a in A:
    z = ZH.get(a['slug'])
    if not z:
        continue
    pairs = [(a['title'], z['title']), (a['desc'], z['desc']), (a['take'], z['take'])]
    pairs += [(x, y) for p, q in zip(a['facts'], z['facts']) for x, y in zip(p, q)]
    pairs += [(x, y) for p, q in zip(a['sections'], z['sections']) for x, y in zip(p, q)]
    for en, zh in pairs:
        TR.setdefault(E(en), {}).update({'zh-CN': zh, 'zh-TW': _cc(zh)})
# Malay, Japanese and Korean article texts
OT = json.load(open(os.path.join(HERE, 'mm2h_articles_i18n.json'), encoding='utf-8'))
for lang, arts in OT.items():
    for a in A:
        z = arts.get(a['slug'])
        if not z:
            continue
        pairs = [(a['title'], z['title']), (a['desc'], z['desc']), (a['take'], z['take'])]
        pairs += [(x, y) for p, q in zip(a['facts'], z['facts']) for x, y in zip(p, q)]
        pairs += [(x, y) for p, q in zip(a['sections'], z['sections']) for x, y in zip(p, q)]
        for en, tr in pairs:
            TR.setdefault(E(en), {})[lang] = tr
MIN_READ = {'zh-CN': '{n} 分钟阅读', 'zh-TW': '{n} 分鐘閱讀', 'ms': '{n} minit bacaan', 'ja': '{n}分で読めます', 'ko': '{n}분 읽기'}


def translate(page):
    """Tag every element whose whole text is a known phrase, and add the script that swaps it."""
    used, keys = {}, {}

    def tag(m):
        txt = m.group(3)
        if txt not in TR:
            return m.group(0)
        k = keys.setdefault(txt, len(keys))
        used[k] = dict(TR[txt], en=txt)
        return '<%s%s data-mt="%d">%s</%s>' % (m.group(1), m.group(2), k, txt, m.group(1))
    page = re.sub(r'<(h1|h2|h3|p|b|small|span|label|option|button|li|summary|a)((?:\s[^<>]*)?)>([^<>]+)</\1>', tag, page)
    js = ('<script>(function(){var T=%s,R=%s;function f(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}'
          'document.querySelectorAll("[data-mt]").forEach(function(x){var t=T[x.getAttribute("data-mt")];if(!t)return;var v=t[l]||t.en;'
          'if(x.tagName==="OPTION"&&!x.hasAttribute("value"))x.setAttribute("value",t.en);x.innerHTML=v;});'
          'document.querySelectorAll("[data-mr]").forEach(function(x){var n=x.getAttribute("data-mr");x.textContent=R[l]?R[l].replace("{n}",n):"By Keith Nah · "+n+" min read";});}f();'
          'document.addEventListener("DOMContentLoaded",function(){var s=window.knSetLang;if(typeof s==="function")window.knSetLang=function(){var r=s.apply(this,arguments);f();return r;};f();});})();</script>'
          ) % (json.dumps({str(k): v for k, v in used.items()}, ensure_ascii=False), json.dumps({k: 'Keith Nah · ' + v for k, v in MIN_READ.items()}, ensure_ascii=False))
    return page.replace('</body>', js + '\n</body>', 1)


os.makedirs('mm2h', exist_ok=True)
keep = set()
for a in A:
    open('mm2h/%s.html' % a['slug'], 'w', encoding='utf-8').write(translate(article_page(a)))
    keep.add(a['slug'] + '.html')
for f in os.listdir('mm2h'):
    if f.endswith('.html') and f not in keep:
        os.remove(os.path.join('mm2h', f))

out = sys.argv[1] if len(sys.argv) > 1 else 'mm2h.html'
t = open('mm2h.html', encoding='utf-8').read()
t = re.sub(r'<!-- KN-MM2H:START -->.*?<!-- KN-MM2H:END -->\n?', '', t, flags=re.S)
i = t.index('<section class="mm2h-tiers">')
j = t.index('</section>', i) + len('</section>')
t = t[:j] + '\n<!-- KN-MM2H:START -->' + translate(LIB_CSS + library() + FORM + JS + '</body>').replace('</body>', '') + '<!-- KN-MM2H:END -->' + t[j:]
# the old intro said MM2H does not need a property purchase; since 2024 every federal tier does
t = t.replace("MM2H is separate from property ownership itself — it doesn't require buying real estate to qualify on its own, but combining the two is common among Keith's clients who want both a home and a long-stay pass in Kuala Lumpur.",
              "Since 2024 every federal tier also needs a residential property purchase above a minimum price, so choosing the tier and choosing the home go together. Keith helps clients match the two.")
NEW = "Since 2024 every federal tier also needs a residential property purchase above a minimum price, so choosing the tier and choosing the home go together. Keith helps clients match the two."
NEW_TR = {'zh-CN': '自 2024 年起，每个联邦等级都必须购买一套达到最低价格的住宅，所以选等级和选房子要一起考虑。Keith 会帮客户把两者配合好。',
          'ms': 'Sejak 2024, setiap tahap persekutuan juga memerlukan pembelian hartanah kediaman melebihi harga minimum, jadi memilih tahap dan memilih rumah perlu dibuat bersama. Keith membantu klien memadankan kedua-duanya.',
          'ja': '2024年以降、連邦の各ティアでは最低価格以上の住宅購入も必要です。そのため、ティア選びと住まい選びは一緒に考えることになります。Keith が両方を合わせるお手伝いをします。',
          'ko': '2024년부터 모든 연방 등급은 최저 가격 이상의 주택 구입도 필요합니다. 그래서 등급 선택과 집 선택을 함께 해야 합니다. Keith가 두 가지를 맞추도록 도와드립니다.'}
NEW_TR['zh-TW'] = _cc(NEW_TR['zh-CN'])
t = re.sub(r'("' + re.escape(NEW) + r'":)\{[^{}]*\}', lambda m: m.group(1) + json.dumps(NEW_TR, ensure_ascii=False), t, count=1)
open(out, 'w', encoding='utf-8').write(t)
print('mm2h: %d article page(s), library and enquiry form on %s' % (len(A), out))
