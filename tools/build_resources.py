"""Build resources.html (the Free Toolkit) and put it in the main menu where MM2H used to be.

Layout: a buyer's path in four steps.
  01 Explore an area  - free PDF area guides (each has its own landing page in guides/, see
                        tools/build_guides.py) and the all-projects map
  02 Compare & work out the numbers - popular comparisons and the calculator
  03 Learn            - the MM2H guide and Keith's YouTube videos
  04 Talk to Keith    - one-to-one advice on WhatsApp
Menu: "MM2H 第二家园" is replaced by "Free Toolkit" (免费资源 in Chinese) on the static pages; the
generated pages take it from the NAV lists. MM2H stays in the mobile menus, on this page and at
mm2h.html. Texts in all six site languages. Safe to run again.
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
import build_area_pages as A  # noqa: E402
import build_guides as G  # noqa: E402
import site_header as SH  # noqa: E402

E = lambda s: html.escape(str(s), quote=True)
SITE = 'https://keithnah.com'
waq = G.waq
N = len(A.P)
LABEL = 'Free Toolkit'
NAV_TR = {"zh-CN": "免费资源", "zh-TW": "免費資源", "ms": "Kit Percuma", "ja": "無料ツールキット", "ko": "무료 툴킷"}

try:
    import opencc
    _cc = opencc.OpenCC('s2tw').convert
except ImportError:
    _cc = lambda s: s

GUIDES = G.guides()

T = {
    'en': {
        'title': 'Free Toolkit', 'eb': 'Free Toolkit', 'h1': 'Do your homework before you buy',
        'sub': 'Free area guides, comparisons, a map, a calculator and videos, laid out in the order most buyers need them.',
        's1': 'Explore an area', 's2': 'Compare and do the numbers', 's3': 'Learn the basics', 's4': 'Talk to Keith',
        'g_t': 'Free area guides (PDF)', 'g_s': 'Every new launch in one area, in one PDF: prices, psf, sizes, completion, rail stations and a map. Pick an area to download.',
        'g_n': '{n} projects', 'g_f': 'from {p}', 'pdf': 'PDF',
        'map_t': 'Interactive map of every new launch', 'map_d': 'All %d projects on one map. Tap a pin for the price and project page.' % N, 'map_b': 'Open the map',
        'cmp_t': 'Popular comparisons', 'cmp_d': 'Bukit Jalil, KL City Centre under RM1M, under RM500K and 11 more: prices, psf and monthly instalments side by side.', 'cmp_b': 'Start comparing',
        'calc_t': 'Monthly instalment calculator', 'calc_d': 'Enter the price and down payment to see the monthly instalment, total interest and how much you can borrow.', 'calc_b': 'Calculate now',
        'mm_t': 'MM2H guide (Malaysia My Second Home)', 'mm_d': 'The tiers, the fixed deposit and what foreign buyers can purchase, explained on one page.', 'mm_b': 'Read the guide',
        'yt_t': 'Market videos, one question each', 'yt_d': 'Can foreigners buy, why Malaysia leads Southeast Asia, and project site visits.', 'yt_b': 'Watch on YouTube',
        'k_t': 'Not sure where to start?', 'k_d': 'Tell Keith your budget, preferred area and purpose. He will shortlist the projects worth a closer look, free of charge.', 'k_b': 'WhatsApp Keith',
    },
    'zh-CN': {
        'title': '免费资源', 'eb': '免费资源', 'h1': '买房前，先把功课做好',
        'sub': '地区懒人包、项目比较、地图、计算器和影片，按大多数买家的顺序排好，全部免费。',
        's1': '先看地区', 's2': '比较项目、算清楚', 's3': '了解基本知识', 's4': '跟 Keith 聊',
        'g_t': '免费地区懒人包（PDF）', 'g_s': '一个地区的新项目整理成一份 PDF：价格、呎价、面积、竣工、轨道站和地图。选一个地区下载。',
        'g_n': '{n} 个项目', 'g_f': '{p} 起', 'pdf': 'PDF',
        'map_t': '全马新楼盘互动地图', 'map_d': '%d 个项目标在同一张地图上，点一下就看到价格和项目页。' % N, 'map_b': '打开地图',
        'cmp_t': '热门项目比较', 'cmp_d': 'Bukit Jalil、KL City Centre RM1M 以下、RM500K 以下等 14 组，并排比较价格、呎价和月供。', 'cmp_b': '开始比较',
        'calc_t': '月供计算器', 'calc_d': '输入房价和首付，马上算出月供、总利息和可贷款额。', 'calc_b': '马上计算',
        'mm_t': 'MM2H 第二家园指南', 'mm_d': '三种等级、定期存款要求、外国人可以买什么，一页讲清楚。', 'mm_b': '阅读指南',
        'yt_t': '房市分析影片，一支讲一个问题', 'yt_d': '外国人能不能买、为什么东南亚首选马来西亚、项目实地看房。', 'yt_b': '去 YouTube 看',
        'k_t': '不知道从哪里开始？', 'k_d': '告诉 Keith 你的预算、地区和用途，他免费帮你筛出值得细看的项目。', 'k_b': 'WhatsApp Keith',
    },
    'ms': {
        'title': 'Kit Percuma', 'eb': 'Kit Percuma', 'h1': 'Buat kerja rumah sebelum membeli',
        'sub': 'Panduan kawasan, perbandingan, peta, kalkulator dan video percuma, disusun mengikut urutan yang diperlukan kebanyakan pembeli.',
        's1': 'Teroka kawasan', 's2': 'Banding dan kira', 's3': 'Fahami asasnya', 's4': 'Bercakap dengan Keith',
        'g_t': 'Panduan kawasan percuma (PDF)', 'g_s': 'Semua projek baharu satu kawasan dalam satu PDF: harga, harga sk, saiz, tarikh siap, stesen rel dan peta. Pilih kawasan untuk muat turun.',
        'g_n': '{n} projek', 'g_f': 'dari {p}', 'pdf': 'PDF',
        'map_t': 'Peta interaktif semua projek baharu', 'map_d': 'Kesemua %d projek dalam satu peta. Ketik pin untuk harga dan halaman projek.' % N, 'map_b': 'Buka peta',
        'cmp_t': 'Perbandingan popular', 'cmp_d': 'Bukit Jalil, KL City Centre bawah RM1M, bawah RM500K dan 11 lagi: harga, harga sk dan ansuran bulanan sebelah-menyebelah.', 'cmp_b': 'Mula membanding',
        'calc_t': 'Kalkulator ansuran bulanan', 'calc_d': 'Masukkan harga dan deposit untuk melihat ansuran bulanan, jumlah faedah dan jumlah pinjaman yang layak.', 'calc_b': 'Kira sekarang',
        'mm_t': 'Panduan MM2H (Malaysia My Second Home)', 'mm_d': 'Peringkat, simpanan tetap dan apa yang boleh dibeli oleh pembeli asing, dalam satu halaman.', 'mm_b': 'Baca panduan',
        'yt_t': 'Video pasaran, satu soalan setiap satu', 'yt_d': 'Bolehkah warga asing membeli, mengapa Malaysia pilihan utama di Asia Tenggara, dan lawatan tapak projek.', 'yt_b': 'Tonton di YouTube',
        'k_t': 'Tidak pasti mahu mula dari mana?', 'k_d': 'Beritahu Keith bajet, kawasan dan tujuan anda. Dia akan menyenarai pendek projek yang patut dilihat, percuma.', 'k_b': 'WhatsApp Keith',
    },
    'ja': {
        'title': '無料ツールキット', 'eb': '無料ツールキット', 'h1': '購入前に、まず下調べを',
        'sub': 'エリアガイド、物件比較、地図、計算機、動画を、多くの購入者が必要とする順に並べました。すべて無料です。',
        's1': 'エリアを知る', 's2': '比較して計算する', 's3': '基本を学ぶ', 's4': 'Keith に相談',
        'g_t': '無料エリアガイド（PDF）', 'g_s': 'エリアの新築物件を1つのPDFに：価格、単価、面積、完成時期、最寄り駅、地図。エリアを選んでダウンロード。',
        'g_n': '{n}件', 'g_f': '{p}から', 'pdf': 'PDF',
        'map_t': '全新築物件のインタラクティブ地図', 'map_d': '%d件の物件を1つの地図に。ピンをタップすると価格と物件ページが見られます。' % N, 'map_b': '地図を開く',
        'cmp_t': '人気の物件比較', 'cmp_d': 'Bukit Jalil、KL City Centre RM1M以下、RM500K以下など14組。価格・単価・月々の返済を並べて比較。', 'cmp_b': '比較を始める',
        'calc_t': '月々の返済計算機', 'calc_d': '価格と頭金を入力すると、月々の返済額、総利息、借入可能額がすぐにわかります。', 'calc_b': '計算する',
        'mm_t': 'MM2H ガイド（Malaysia My Second Home）', 'mm_d': 'ランク、定期預金の条件、外国人が購入できる物件を1ページで解説。', 'mm_b': 'ガイドを読む',
        'yt_t': '市場解説動画、1本に1テーマ', 'yt_d': '外国人は購入できるか、なぜ東南アジアでマレーシアなのか、物件の現地見学。', 'yt_b': 'YouTube で見る',
        'k_t': 'どこから始めればいいか迷ったら', 'k_d': '予算、希望エリア、目的を Keith に伝えてください。検討する価値のある物件を無料で絞り込みます。', 'k_b': 'WhatsApp Keith',
    },
    'ko': {
        'title': '무료 툴킷', 'eb': '무료 툴킷', 'h1': '사기 전에, 먼저 공부부터',
        'sub': '지역 가이드, 비교, 지도, 계산기, 영상을 대부분의 구매자가 필요로 하는 순서대로 정리했습니다. 모두 무료입니다.',
        's1': '지역 살펴보기', 's2': '비교하고 계산하기', 's3': '기본 알아보기', 's4': 'Keith와 상담',
        'g_t': '무료 지역 가이드 (PDF)', 'g_s': '한 지역의 신규 분양을 하나의 PDF로: 가격, 평방피트당 가격, 면적, 준공, 역, 지도. 지역을 골라 다운로드하세요.',
        'g_n': '{n}개 프로젝트', 'g_f': '{p}부터', 'pdf': 'PDF',
        'map_t': '전국 신규 분양 인터랙티브 지도', 'map_d': '%d개 프로젝트를 한 지도에. 핀을 누르면 가격과 프로젝트 페이지를 볼 수 있습니다.' % N, 'map_b': '지도 열기',
        'cmp_t': '인기 프로젝트 비교', 'cmp_d': 'Bukit Jalil, KL City Centre RM1M 이하, RM500K 이하 등 14개 조합. 가격, 평방피트당 가격, 월 상환액을 나란히 비교.', 'cmp_b': '비교 시작',
        'calc_t': '월 상환액 계산기', 'calc_d': '가격과 계약금을 입력하면 월 상환액, 총 이자, 대출 가능 금액을 바로 확인할 수 있습니다.', 'calc_b': '지금 계산',
        'mm_t': 'MM2H 가이드 (Malaysia My Second Home)', 'mm_d': '등급, 정기예금 조건, 외국인이 살 수 있는 부동산을 한 페이지로 설명합니다.', 'mm_b': '가이드 읽기',
        'yt_t': '시장 분석 영상, 한 편에 한 질문', 'yt_d': '외국인도 살 수 있는지, 왜 동남아에서 말레이시아인지, 현장 방문 영상.', 'yt_b': 'YouTube에서 보기',
        'k_t': '어디서부터 시작할지 모르겠다면', 'k_d': '예산, 원하는 지역, 목적을 Keith에게 알려주세요. 살펴볼 만한 프로젝트를 무료로 추려드립니다.', 'k_b': 'WhatsApp Keith',
    },
}
T['zh-TW'] = {k: _cc(v) for k, v in T['zh-CN'].items()}
en = T['en']
ARROW = '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'

# area guide tiles, each with its own photo
used, tiles = set(), []
for g in GUIDES:
    ks = [k for k in g['ids'] if A.PHOTO.get(k)]
    k = next((k for k in ks if A.PHOTO[k] not in used), ks[0] if ks else None)
    if k is not None:
        used.add(A.PHOTO[k])
    low = G.facts(g)['low']
    tiles.append('<a class="gt" href="guides/{s}.html"><img src="{img}" alt="" loading="lazy"><span class="gt-pdf">PDF</span>'
                 '<span class="gt-b"><b>{a}</b><small><span data-gn="{n}">{n} projects</span>{f}</small></span><i>{ar}</i></a>'.format(
                     s=g['slug'], img=E(A.PHOTO.get(k, '')) if k is not None else '', a=E(g['area']), n=g['n'], ar=ARROW,
                     f=(' · <span data-gf="%s">from %s</span>' % (E(G.rm(low)), E(G.rm(low)))) if low else ''))


def tool(key, img, href, ext=False, cls=''):
    x = ' target="_blank" rel="noopener"' if ext else ''
    return ('<a class="tl %s" href="%s"%s><span class="tl-b"><b data-r="%s_t">%s</b><span data-r="%s_d">%s</span><em><span data-r="%s_b">%s</span>%s</em></span>'
            '<span class="tl-i"><img src="images/res/%s" alt="" loading="lazy"></span></a>') % (
        cls, E(href), x, key, E(en[key + '_t']), key, E(en[key + '_d']), key, E(en[key + '_b']), ARROW, img)


STEP = lambda n, k: '<div class="sh"><span class="sn">%s</span><h2 data-r="%s">%s</h2></div>' % (n, k, E(en[k]))
body = '''<header>
  <a class="logo" href=""><img src="images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Keith Nah Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="{wa}" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
<section class="th"><div class="wrap">
  <span class="eb" data-r="eb">Free Toolkit</span>
  <h1 data-r="h1">{h1}</h1>
  <p data-r="sub">{sub}</p>
  <nav class="path" aria-label="Steps"><a href="#s1"><i>01</i><span data-r="s1">{s1}</span></a><a href="#s2"><i>02</i><span data-r="s2">{s2}</span></a><a href="#s3"><i>03</i><span data-r="s3">{s3}</span></a><a href="#s4"><i>04</i><span data-r="s4">{s4}</span></a></nav>
</div></section>
<main class="wrap">
  <section id="s1" class="st1">{st1}
    <div class="gh2"><div><h3 data-r="g_t">{g_t}</h3><p data-r="g_s">{g_s}</p></div></div>
    <div class="gg">{tiles}</div>
    {map}
  </section>
  <section id="s2">{st2}<div class="two">{cmp}{calc}</div></section>
  <section id="s3">{st3}<div class="two">{mm}{yt}</div></section>
  <section id="s4" class="kb">
    <div class="kb-i"><img src="images/6b39ef32b4958165.jpg" alt="Keith Nah" loading="lazy"></div>
    <div class="kb-b"><span class="sn">04</span><h2 data-r="k_t">{k_t}</h2><p data-r="k_d">{k_d}</p><a class="kb-btn" href="{kwa}" target="_blank" rel="noopener"><span data-r="k_b">WhatsApp Keith</span>{ar}</a></div>
  </section>
</main>
<footer>&copy; 2026 Keith Nah Real Estate. All rights reserved.</footer>'''.format(
    wa=E(waq('Hi Keith, I would like to explore more on Malaysia Property.')), h1=E(en['h1']), sub=E(en['sub']),
    s1=E(en['s1']), s2=E(en['s2']), s3=E(en['s3']), s4=E(en['s4']), st1=STEP('01', 's1'), st2=STEP('02', 's2'), st3=STEP('03', 's3'),
    g_t=E(en['g_t']), g_s=E(en['g_s']), tiles=''.join(tiles),
    map=tool('map', 'map.jpg', 'projects.html#projectMap', cls='wide'),
    cmp=tool('cmp', 'compare.jpg', 'compare.html#popular'), calc=tool('calc', 'calculator.jpg', 'calculator.html'),
    mm=tool('mm', 'mm2h-guide.jpg', 'mm2h.html'), yt=tool('yt', 'videos.jpg', 'https://www.youtube.com/@KeithNahRealEstate/videos', ext=True),
    k_t=E(en['k_t']), k_d=E(en['k_d']), kwa=E(waq('Hi Keith, I would like one-to-one advice on Malaysia property.')), ar=ARROW)

CSS = '''
:root{--bg:#F7F6FB;--ink:#15142b;--grey:#5f5e74;--line:rgba(21,20,43,.09);--gold:#5E60CE;--deep:#1d1b4f;}
*{box-sizing:border-box;margin:0;padding:0;} body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6;}
a{color:inherit;text-decoration:none;} img{display:block;max-width:100%;}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif;line-height:1.2;}
.wrap{max-width:1180px;margin:0 auto;padding:0 5vw;}
.th{background:radial-gradient(900px 420px at 90% -20%,rgba(94,96,206,.45),transparent 60%),linear-gradient(160deg,#1d1b4f,#2b2973 75%,#34358a);color:#fff;padding:70px 0 0;overflow:hidden;}
.th .eb{font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:#b9b4ff;font-weight:700;}
.th h1{font-size:clamp(34px,5vw,58px);margin:10px 0 14px;max-width:820px;} .th p{opacity:.85;max-width:640px;font-size:16px;margin-bottom:40px;}
.path{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border-top:1px solid rgba(255,255,255,.15);}
.path a{display:flex;align-items:center;gap:12px;padding:22px 18px 24px 0;font-weight:600;font-size:15px;opacity:.9;transition:opacity .2s;position:relative;}
.path a:hover{opacity:1;} .path a:after{content:"";position:absolute;left:0;right:18px;bottom:0;height:3px;background:#5E60CE;transform:scaleX(0);transform-origin:left;transition:transform .3s;} .path a:hover:after{transform:scaleX(1);}
.path i{font-style:normal;font-family:'Playfair Display',serif;font-size:26px;color:#b9b4ff;}
section[id]{padding-top:64px;scroll-margin-top:80px;}
.sh{display:flex;align-items:baseline;gap:14px;margin-bottom:22px;} .sn{font-family:'Playfair Display',serif;font-size:42px;color:var(--gold);line-height:1;}
.sh h2{font-size:clamp(26px,3vw,36px);}
.gh2 h3{font-family:'Inter',sans-serif;font-size:18px;font-weight:800;} .gh2 p{color:var(--grey);font-size:14.5px;max-width:720px;margin:4px 0 18px;}
.gg{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px;}
.gt{position:relative;display:block;border-radius:18px;overflow:hidden;aspect-ratio:4/3.2;background:#2a2870;color:#fff;isolation:isolate;}
.gt img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform .6s;z-index:-2;}
.gt:before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,17,48,.05) 20%,rgba(18,17,48,.88));z-index:-1;}
.gt:hover img{transform:scale(1.06);}
.gt-pdf{position:absolute;top:12px;left:12px;background:#fff;color:var(--deep);font-size:11px;font-weight:800;letter-spacing:.08em;padding:4px 9px;border-radius:7px;}
.gt-b{position:absolute;left:16px;right:52px;bottom:14px;} .gt-b b{display:block;font-size:17px;line-height:1.25;} .gt-b small{font-size:12px;opacity:.85;}
.gt i{position:absolute;right:14px;bottom:16px;width:30px;height:30px;border-radius:50%;background:rgba(255,255,255,.18);display:flex;align-items:center;justify-content:center;transition:background .25s;}
.gt:hover i{background:var(--gold);} .gt i svg,.tl em svg,.kb-btn svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round;}
.tl{display:grid;grid-template-columns:1fr 46%;gap:0;background:#fff;border:1px solid var(--line);border-radius:20px;overflow:hidden;transition:transform .3s,box-shadow .3s;min-height:220px;}
.tl:hover{transform:translateY(-3px);box-shadow:0 18px 40px rgba(29,27,79,.12);}
.tl-b{padding:26px 24px;display:flex;flex-direction:column;} .tl-b b{font-size:19px;font-weight:800;line-height:1.3;margin-bottom:8px;} .tl-b>span{color:var(--grey);font-size:14px;flex:1;}
.tl em{font-style:normal;display:inline-flex;align-items:center;gap:8px;margin-top:16px;color:var(--gold);font-weight:800;font-size:14px;}
.tl-i{background:#efeefb;overflow:hidden;} .tl-i img{width:100%;height:100%;object-fit:cover;object-position:left top;transition:transform .5s;} .tl:hover .tl-i img{transform:scale(1.04);}
.tl.wide{grid-template-columns:1fr 1.25fr;}
.two{display:grid;grid-template-columns:1fr 1fr;gap:18px;}
.kb{display:grid;grid-template-columns:300px 1fr;gap:0;background:var(--deep);color:#fff;border-radius:24px;overflow:hidden;margin:64px 0 80px;padding-top:0 !important;}
.kb-i img{width:100%;height:100%;object-fit:cover;min-height:280px;} .kb-b{padding:40px 44px;display:flex;flex-direction:column;justify-content:center;}
.kb-b .sn{color:#b9b4ff;font-size:34px;} .kb-b h2{font-size:clamp(26px,3vw,36px);margin:8px 0 10px;} .kb-b p{opacity:.85;max-width:560px;margin-bottom:22px;}
.kb-btn{align-self:flex-start;display:inline-flex;align-items:center;gap:10px;background:#25D366;color:#fff;font-weight:800;padding:14px 24px;border-radius:100px;transition:transform .2s;} .kb-btn:hover{transform:translateY(-2px);}
footer{border-top:1px solid var(--line);padding:26px 5vw;font-size:13px;color:var(--grey);text-align:center;}
@media(max-width:980px){.gg{grid-template-columns:repeat(3,1fr);} .two{grid-template-columns:1fr;} .path{grid-template-columns:1fr 1fr;}}
@media(max-width:640px){.th{padding-top:40px;} .th p{margin-bottom:24px;} .path a{padding:14px 10px 16px 0;font-size:13.5px;} .path i{font-size:21px;}
  .gg{grid-template-columns:1fr 1fr;gap:10px;} .gt{border-radius:14px;} .gt-b{left:12px;right:40px;bottom:10px;} .gt-b b{font-size:15px;} .gt i{right:10px;bottom:12px;width:26px;height:26px;}
  .tl,.tl.wide{grid-template-columns:1fr;} .tl-i{order:-1;aspect-ratio:12/6;} .kb{grid-template-columns:1fr;} .kb-i img{min-height:0;aspect-ratio:4/3;object-position:center 20%;} .kb-b{padding:28px 24px;} .sn{font-size:34px;}}
'''

JS = '''<script>(function(){var T=%s;
function lang(){var l='en';try{l=localStorage.getItem('kn_lang')||'en'}catch(e){}return T[l]?l:'en';}
function apply(){var L=T[lang()];document.querySelectorAll('[data-r]').forEach(function(el){var v=L[el.getAttribute('data-r')];if(v)el.textContent=v;});
document.querySelectorAll('[data-gn]').forEach(function(el){el.textContent=L.g_n.replace('{n}',el.getAttribute('data-gn'));});
document.querySelectorAll('[data-gf]').forEach(function(el){el.textContent=L.g_f.replace('{p}',el.getAttribute('data-gf'));if(window.knApplyCurrency)try{knApplyCurrency(el)}catch(e){}});
document.title=L.title+' | Keith Nah Real Estate';}
document.addEventListener('DOMContentLoaded',function(){var s=window.knSetLang;if(typeof s==='function')window.knSetLang=function(){var r=s.apply(this,arguments);apply();return r;};apply();});
apply();})();</script>''' % json.dumps(T, ensure_ascii=False)

desc = 'Free toolkit from Keith Nah: PDF area guides of new launch condos, the MM2H guide, project comparisons, an interactive map, videos and a mortgage calculator.'
page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Free Toolkit | Keith Nah Real Estate</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{site}/resources.html">
<meta property="og:title" content="Free Toolkit | Keith Nah Real Estate"><meta property="og:description" content="{desc}"><meta property="og:url" content="{site}/resources.html"><meta property="og:image" content="{site}/images/res/area-guides.jpg">
<link rel="icon" type="image/png" href="images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
{body}
<script src="lead-tracker.js"></script>
{js}
</body>
</html>
'''.format(desc=E(desc), site=SITE, css=CSS, body=body, js=JS)
open('resources.html', 'w', encoding='utf-8').write(SH.apply(page, '', 'resources.html'))

# ---------- main menu: MM2H -> Free Toolkit on the static pages ----------
STATIC = ['index.html', 'projects.html', 'compare.html', 'blog.html', 'about-keith.html', 'calculator.html', 'mm2h.html']
TRJ = json.dumps(NAV_TR, ensure_ascii=False)
for f in STATIC:
    t = open(f, encoding='utf-8').read()
    o = t
    t = re.sub(r'<a href="mm2h\.html"( data-i18n="nav_mm2h")?( class="active")?>MM2H 第二家园</a>',
               lambda m: '<a href="resources.html"%s>%s</a>' % (' data-i18n="nav_res"' if m.group(1) else '', LABEL), t)
    t = re.sub(r'(<a href="resources\.html"(?: data-i18n="nav_res")?>)[^<]*(</a>)', lambda m: m.group(1) + LABEL + m.group(2), t)
    t = re.sub(r'"(?:Free Resources|%s)": \{[^}]*\}, "About Keith": \{"zh-CN"' % LABEL, lambda _: '"About Keith": {"zh-CN"', t)
    if '"About Keith": {"zh-CN"' in t:   # header translations (compact JSON)
        t = t.replace('"About Keith": {"zh-CN"', '"%s": %s, "About Keith": {"zh-CN"' % (LABEL, TRJ), 1)
    if 'data-i18n="nav_res"' in t:
        t = re.sub(r'"nav_res": \{[^}]*\},\n  ', '', t)
        t = t.replace('"nav_about": {', '"nav_res": %s,\n  "nav_about": {' % TRJ, 1)
    if t != o:
        open(f, 'w', encoding='utf-8').write(t)

# mobile drawer on the static pages (built from the header links): keep MM2H under the toolkit
DR_A = "      L.appendChild(c);\n    });\n    var lg=document.getElementById('knLang');"
DR_B = ("      L.appendChild(c);\n      if(h==='resources.html'){ var m2=document.createElement('a'); m2.href='mm2h.html'; m2.textContent='MM2H 第二家园';"
        " if(cur==='mm2h.html') m2.className='active'; L.appendChild(m2); }\n    });\n    var lg=document.getElementById('knLang');")
for f in STATIC:
    t = open(f, encoding='utf-8').read()
    if DR_A in t and "m2.href='mm2h.html'" not in t:
        open(f, 'w', encoding='utf-8').write(t.replace(DR_A, DR_B, 1))

# sitemap: the toolkit and the guide pages
if os.path.exists('sitemap.xml'):
    sm = open('sitemap.xml', encoding='utf-8').read()
    add = ['resources.html'] + ['guides/%s.html' % g['slug'] for g in GUIDES]
    new = ''.join('  <url><loc>%s/%s</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>\n' % (SITE, u) for u in add if '/%s<' % u not in sm)
    if new:
        open('sitemap.xml', 'w', encoding='utf-8').write(sm.replace('</urlset>', new + '</urlset>'))
print('resources: %d area guides' % len(GUIDES))
