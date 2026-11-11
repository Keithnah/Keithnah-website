"""The "page not found" page (404.html), shown by Hostinger for any address that does not exist (.htaccess).

It keeps visitors on the site: shortcuts to the projects, lists, news and a WhatsApp button,
in the visitor's language. Links are absolute (/...) because it is shown at any address.
Not indexed by search engines. Run by tools/build_all.py.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import site_header as SH

T = {
    'en': {'h': 'This page has moved or no longer exists', 'p': 'The link may be old, or the project page was renamed. These will help you find what you were looking for:',
           'proj': 'All new launch projects', 'best': 'Best new launch lists', 'news': "Keith's market notes", 'cmp': 'Compare projects', 'home': 'Home page',
           'wa': 'Ask Keith on WhatsApp', 'wa_p': 'Tell Keith which project or area you were looking for, and he will send it to you.'},
    'zh-CN': {'h': '这个页面已移动或不存在', 'p': '链接可能已过期，或项目页面已改名。以下链接可以帮你找到想看的内容：',
              'proj': '全部新楼盘项目', 'best': '精选新楼盘榜单', 'news': 'Keith 市场短评', 'cmp': '比较项目', 'home': '首页',
              'wa': 'WhatsApp 问 Keith', 'wa_p': '告诉 Keith 你在找哪个项目或地区，他会直接发给你。'},
    'zh-TW': {'h': '這個頁面已移動或不存在', 'p': '連結可能已過期，或項目頁面已改名。以下連結可以幫你找到想看的內容：',
              'proj': '全部新樓盤項目', 'best': '精選新樓盤榜單', 'news': 'Keith 市場短評', 'cmp': '比較項目', 'home': '首頁',
              'wa': 'WhatsApp 問 Keith', 'wa_p': '告訴 Keith 你在找哪個項目或地區，他會直接發給你。'},
    'ms': {'h': 'Halaman ini telah dipindahkan atau tidak wujud lagi', 'p': 'Pautan mungkin lama, atau nama halaman projek telah ditukar. Pautan ini boleh membantu anda:',
           'proj': 'Semua projek baharu', 'best': 'Senarai projek baharu terbaik', 'news': 'Nota pasaran Keith', 'cmp': 'Bandingkan projek', 'home': 'Halaman utama',
           'wa': 'Tanya Keith di WhatsApp', 'wa_p': 'Beritahu Keith projek atau kawasan yang anda cari, dan dia akan menghantarnya kepada anda.'},
    'ja': {'h': 'このページは移動したか、存在しません', 'p': 'リンクが古いか、物件ページの名前が変わった可能性があります。こちらからお探しください：',
           'proj': 'すべての新築プロジェクト', 'best': 'おすすめ新築リスト', 'news': 'Keith のマーケットノート', 'cmp': 'プロジェクトを比較', 'home': 'ホーム',
           'wa': 'WhatsApp で Keith に質問', 'wa_p': 'お探しの物件やエリアを Keith に伝えていただければ、すぐにお送りします。'},
    'ko': {'h': '이 페이지는 이동되었거나 더 이상 존재하지 않습니다', 'p': '링크가 오래되었거나 프로젝트 페이지 이름이 바뀌었을 수 있습니다. 아래에서 찾아보세요:',
           'proj': '전체 신규 분양 프로젝트', 'best': '추천 신규 분양 목록', 'news': 'Keith의 마켓 노트', 'cmp': '프로젝트 비교', 'home': '홈페이지',
           'wa': 'WhatsApp으로 Keith에게 문의', 'wa_p': '찾으시던 프로젝트나 지역을 Keith에게 알려주시면 바로 보내드립니다.'},
}
WA = 'https://api.whatsapp.com/send/?phone=60102821568&text=%28KNRE%29+Hi+Keith%2C+I+was+looking+for+a+page+on+your+website.&type=phone_number&app_absent=0'
LINKS = [('/projects.html', 'proj'), ('/best/', 'best'), ('/market-notes.html', 'news'), ('/compare.html', 'cmp'), ('/', 'home')]
en = T['en']
cards = ''.join('<a class="nf-c" href="%s"><span data-t="%s">%s</span><i>→</i></a>' % (h, k, en[k]) for h, k in LINKS)
page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Page not found | Keith Nah</title>
<meta name="description" content="This page has moved or no longer exists.">
<meta name="robots" content="noindex, follow">
<link rel="icon" type="image/png" href="/images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
<style>
:root{--ink:#15142b;--grey:#5f5e74;--line:rgba(21,20,43,.09);--gold:#5E60CE;}
*{box-sizing:border-box;margin:0;padding:0;} body{font-family:Inter,system-ui,sans-serif;background:#F7F6FB;color:var(--ink);line-height:1.6;}
a{color:inherit;text-decoration:none;}
.nf{max-width:760px;margin:0 auto;padding:150px 20px 90px;text-align:center;}
.nf-n{font:700 clamp(84px,16vw,150px)/1 'Playfair Display',Georgia,serif;color:var(--gold);letter-spacing:.02em;}
.nf h1{font:700 clamp(24px,3.6vw,34px)/1.25 'Playfair Display',Georgia,serif;margin:14px 0 10px;}
.nf > p{color:var(--grey);font-size:15.5px;max-width:560px;margin:0 auto 30px;}
.nf-g{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;text-align:left;}
.nf-c{display:flex;justify-content:space-between;align-items:center;background:#fff;border:1px solid var(--line);border-radius:16px;padding:18px 20px;font-weight:700;font-size:15px;transition:all .25s;}
.nf-c i{font-style:normal;color:var(--gold);} .nf-c:hover{border-color:var(--gold);box-shadow:0 12px 28px rgba(29,27,79,.08);transform:translateY(-2px);}
.nf-wa{margin-top:30px;background:#fff;border:1px solid var(--line);border-radius:20px;padding:24px;}
.nf-wa p{color:var(--grey);font-size:14.5px;margin-bottom:14px;}
.nf-wa a{display:inline-flex;align-items:center;gap:8px;background:#25D366;color:#fff;font-weight:700;padding:12px 22px;border-radius:100px;}
footer{border-top:1px solid var(--line);padding:26px 5vw;font-size:13px;color:var(--grey);text-align:center;}
</style>
</head>
<body>
<header>
  <a class="logo" href="/"><img src="/images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Keith Nah Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="%s" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
<main class="nf">
  <div class="nf-n">404</div>
  <h1 data-t="h">%s</h1>
  <p data-t="p">%s</p>
  <div class="nf-g">%s</div>
  <div class="nf-wa"><p data-t="wa_p">%s</p><a href="%s" target="_blank" rel="noopener"><span data-t="wa">%s</span></a></div>
</main>
<footer>&copy; 2026 Keith Nah Real Estate</footer>
<script src="/lead-tracker.js"></script>
<script>(function(){var T=%s;function go(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}var D=T[l]||T.en;
document.querySelectorAll("[data-t]").forEach(function(e){e.textContent=D[e.getAttribute("data-t")];});document.documentElement.lang=l;}
go();document.addEventListener("DOMContentLoaded",function(){var s=window.knSetLang;if(typeof s==="function")window.knSetLang=function(){var r=s.apply(this,arguments);go();return r;};go();});
try{if(window.gtag)gtag("event","page_not_found",{page_location:location.href,page_referrer:document.referrer});}catch(e){}})();</script>
</body>
</html>
''' % (WA, en['h'], en['p'], cards, en['wa_p'], WA, en['wa'], json.dumps(T, ensure_ascii=False))
page = SH.apply(page, '/', '')
open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8').write(page)

# Hostinger shows it for every missing address
p = os.path.join(ROOT, '.htaccess')
h = open(p, encoding='utf-8').read()
if 'ErrorDocument 404' not in h:
    h = h.rstrip('\n') + '\n\n# Friendly "page not found" page\nErrorDocument 404 /404.html\n'
    open(p, 'w', encoding='utf-8').write(h)
print('404 page written')
