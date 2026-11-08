"""Build resources.html (Free Resources) and put it in the main menu where MM2H used to be.

- resources.html: cards for area guides (requested on WhatsApp, sent by Keith via Drive),
  the MM2H guide, popular comparisons, the all-projects map, YouTube videos, the calculator
  and one-to-one advice. Texts in all six site languages.
- Main menu: "MM2H 第二家园" is replaced by "Free Resources" on the static pages; the
  generated pages take it from the NAV lists. MM2H stays reachable from the resources page,
  the mobile menu (tools/float_wa.py) and its own URL, mm2h.html.
Safe to run again.
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
import site_header as SH  # noqa: E402

E = lambda s: html.escape(str(s), quote=True)
SITE = 'https://keithnah.com'
WA = 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0'
waq = lambda m: WA % re.sub(r'\s', '+', '(KNRE) ' + m)
N = len(A.P)

try:
    import opencc
    _cc = opencc.OpenCC('s2tw').convert
except ImportError:
    _cc = lambda s: s

# ---------- area guides offered in the pop-up ----------
groups = A.groups()
areas = []
for st, sub in groups.items():
    for ar, ids in sub.items():
        if len(ids) >= 3:
            areas.append((ar, st, ids))
for st in ('Penang', 'Johor', 'Selangor'):
    ids = [k for v in groups.get(st, {}).values() for k in v]
    if ids:
        areas.append((st, st, ids))
areas.sort(key=lambda x: (-len(x[2]), x[0]))
areas = areas[:12]


def names(ids, n=3):
    ns = sorted((A.P[k]['name'] for k in ids), key=lambda s: s.lower())
    return ', '.join(ns[:n]) + ('…' if len(ns) > n else '')


# ---------- texts ----------
T = {
    'en': {
        'title': 'Free Resources', 'eyebrow': 'Free Resources',
        'lead': 'Where would you like to start?',
        'sub': 'Some buyers start from a city, some already have a project in mind, and some just want to understand the market. Guides, maps, comparisons and videos are sorted below.',
        'c1t': 'Area guides: every new launch in one area, in one file', 'c1d': 'Pick an area and Keith will send you the projects for sale there, with prices and locations, in one guide.', 'c1b': 'Choose an area', 'c1g': 'Free guide',
        'c2t': 'MM2H guide (Malaysia My Second Home)', 'c2d': 'The tiers, the fixed deposit and what foreign buyers can purchase, explained on one page.', 'c2b': 'Read the guide', 'c2g': 'Free to read',
        'c3t': 'Popular project comparisons', 'c3d': 'Bukit Jalil, KL City Centre under RM1M, under RM500K and more: prices, psf and monthly instalments side by side in one tap.', 'c3b': 'Start comparing', 'c3g': 'View now',
        'c4t': 'Interactive map of every new launch', 'c4d': 'All %d projects on one map. Tap a pin to see the price and open the project page.' % N, 'c4b': 'Open the map', 'c4g': 'View now',
        'c5t': 'Market videos, one question each', 'c5d': 'Can foreigners buy, why Malaysia leads Southeast Asia, and project site visits, all on YouTube.', 'c5b': 'Watch on YouTube', 'c5g': 'Free to watch',
        'c6t': 'Monthly instalment calculator', 'c6d': 'Enter the price and down payment to see the monthly instalment, total interest and how much you can borrow.', 'c6b': 'Calculate now', 'c6g': 'Free tool',
        'c7t': 'One-to-one advice', 'c7d': 'Tell Keith your budget, preferred area and purpose, and he will shortlist the projects worth a closer look.', 'c7b': 'WhatsApp Keith', 'c7g': 'Free advice',
        'mt': 'Which area are you looking at?', 'ms': 'Pick an area and Keith will send you the guide for it on WhatsApp.',
        'mg': '{a} guide', 'mn': '{n} projects: {x}', 'mo': 'View online', 'mf': 'More areas are added as new projects launch.',
    },
    'zh-CN': {
        'title': '免费资源', 'eyebrow': '免费资源',
        'lead': '你想先从哪里开始？',
        'sub': '有人先看城市，有人心里已经有项目，也有人只想先了解市场。懒人包、地图、比较和影片，都分好类放在下面。',
        'c1t': '地区懒人包：一区的新项目，一份看完', 'c1d': '选一个地区，Keith 把那一区在卖的项目、价格和位置整理成一份发给你。', 'c1b': '选地区拿资料', 'c1g': '免费索取',
        'c2t': 'MM2H 第二家园指南', 'c2d': '三种等级、定期存款要求、外国人可以买什么，一页讲清楚。', 'c2b': '阅读指南', 'c2g': '免费阅读',
        'c3t': '热门项目比较', 'c3d': 'Bukit Jalil、KL City Centre RM1M 以下、RM500K 以下等热门组合，一键并排比较价格、呎价和月供。', 'c3b': '开始比较', 'c3g': '直接看',
        'c4t': '全马新楼盘互动地图', 'c4d': '%d 个项目标在同一张地图上，点一下就看到价格和项目页。' % N, 'c4b': '打开地图', 'c4g': '直接看',
        'c5t': '房市分析影片，一支讲一个问题', 'c5d': '外国人能不能买、为什么东南亚首选马来西亚、项目实地看房，都在 YouTube。', 'c5b': '去 YouTube 看', 'c5g': '免费观看',
        'c6t': '月供计算器', 'c6d': '输入房价和首付，马上算出月供、总利息和可贷款额。', 'c6b': '马上计算', 'c6g': '免费工具',
        'c7t': '一对一免费咨询', 'c7d': '告诉 Keith 你的预算、地区和用途，他帮你筛出值得细看的项目。', 'c7b': 'WhatsApp Keith', 'c7g': '免费咨询',
        'mt': '你在看哪个地区？', 'ms': '选一个地区，Keith 会在 WhatsApp 把那一区整理好的资料发给你。',
        'mg': '{a} 懒人包', 'mn': '一次看 {n} 个项目：{x}', 'mo': '先在线看', 'mf': '有新项目推出时，会陆续加入更多地区。',
    },
    'ms': {
        'title': 'Sumber Percuma', 'eyebrow': 'Sumber Percuma',
        'lead': 'Dari mana anda mahu bermula?',
        'sub': 'Ada pembeli bermula dengan bandar, ada yang sudah ada projek pilihan, dan ada yang mahu memahami pasaran dahulu. Panduan, peta, perbandingan dan video disusun di bawah.',
        'c1t': 'Panduan kawasan: semua projek baharu satu kawasan dalam satu fail', 'c1d': 'Pilih kawasan dan Keith akan menghantar projek yang dijual di sana, dengan harga dan lokasi, dalam satu panduan.', 'c1b': 'Pilih kawasan', 'c1g': 'Panduan percuma',
        'c2t': 'Panduan MM2H (Malaysia My Second Home)', 'c2d': 'Peringkat, simpanan tetap dan apa yang boleh dibeli oleh pembeli asing, diterangkan dalam satu halaman.', 'c2b': 'Baca panduan', 'c2g': 'Bacaan percuma',
        'c3t': 'Perbandingan projek popular', 'c3d': 'Bukit Jalil, KL City Centre bawah RM1M, bawah RM500K dan lain-lain: harga, harga sk dan ansuran bulanan sebelah-menyebelah dengan satu ketikan.', 'c3b': 'Mula membanding', 'c3g': 'Lihat sekarang',
        'c4t': 'Peta interaktif semua projek baharu', 'c4d': 'Kesemua %d projek dalam satu peta. Ketik pin untuk melihat harga dan membuka halaman projek.' % N, 'c4b': 'Buka peta', 'c4g': 'Lihat sekarang',
        'c5t': 'Video pasaran, satu soalan setiap satu', 'c5d': 'Bolehkah warga asing membeli, mengapa Malaysia pilihan utama di Asia Tenggara, dan lawatan tapak projek, semuanya di YouTube.', 'c5b': 'Tonton di YouTube', 'c5g': 'Tontonan percuma',
        'c6t': 'Kalkulator ansuran bulanan', 'c6d': 'Masukkan harga dan deposit untuk melihat ansuran bulanan, jumlah faedah dan jumlah pinjaman yang layak.', 'c6b': 'Kira sekarang', 'c6g': 'Alat percuma',
        'c7t': 'Nasihat satu-ke-satu', 'c7d': 'Beritahu Keith bajet, kawasan pilihan dan tujuan anda, dan dia akan menyenarai pendek projek yang patut dilihat.', 'c7b': 'WhatsApp Keith', 'c7g': 'Nasihat percuma',
        'mt': 'Kawasan mana yang anda lihat?', 'ms': 'Pilih kawasan dan Keith akan menghantar panduannya melalui WhatsApp.',
        'mg': 'Panduan {a}', 'mn': '{n} projek: {x}', 'mo': 'Lihat dalam talian', 'mf': 'Lebih banyak kawasan akan ditambah apabila projek baharu dilancarkan.',
    },
    'ja': {
        'title': '無料リソース', 'eyebrow': '無料リソース',
        'lead': 'どこから始めますか？',
        'sub': '都市から探す方、気になる物件がある方、まず市場を知りたい方。ガイド、地図、比較、動画を下にまとめました。',
        'c1t': 'エリアガイド：エリアの新築物件を1つの資料に', 'c1d': 'エリアを選ぶと、Keith がそのエリアの販売中物件を価格と場所付きでまとめてお送りします。', 'c1b': 'エリアを選ぶ', 'c1g': '無料ガイド',
        'c2t': 'MM2H ガイド（Malaysia My Second Home）', 'c2d': 'ランク、定期預金の条件、外国人が購入できる物件を1ページで解説。', 'c2b': 'ガイドを読む', 'c2g': '無料で読める',
        'c3t': '人気の物件比較', 'c3d': 'Bukit Jalil、KL City Centre RM1M以下、RM500K以下など。価格・平方フィート単価・月々の返済をワンタップで比較。', 'c3b': '比較を始める', 'c3g': 'すぐ見る',
        'c4t': '全新築物件のインタラクティブ地図', 'c4d': '%d件の物件を1つの地図に。ピンをタップすると価格と物件ページが見られます。' % N, 'c4b': '地図を開く', 'c4g': 'すぐ見る',
        'c5t': '市場解説動画、1本に1テーマ', 'c5d': '外国人は購入できるか、なぜ東南亜でマレーシアなのか、物件の現地見学など、YouTube で公開中。', 'c5b': 'YouTube で見る', 'c5g': '無料で見る',
        'c6t': '月々の返済計算機', 'c6d': '価格と頭金を入力すると、月々の返済額、総利息、借入可能額がすぐにわかります。', 'c6b': '計算する', 'c6g': '無料ツール',
        'c7t': '個別無料相談', 'c7d': '予算、希望エリア、目的を Keith に伝えれば、検討する価値のある物件を絞り込みます。', 'c7b': 'WhatsApp Keith', 'c7g': '無料相談',
        'mt': 'どのエリアをご覧ですか？', 'ms': 'エリアを選ぶと、Keith が WhatsApp でガイドをお送りします。',
        'mg': '{a} ガイド', 'mn': '{n}件の物件：{x}', 'mo': 'オンラインで見る', 'mf': '新しい物件の発売に合わせてエリアを追加していきます。',
    },
    'ko': {
        'title': '무료 자료', 'eyebrow': '무료 자료',
        'lead': '어디서부터 시작할까요?',
        'sub': '도시부터 보는 분, 이미 관심 프로젝트가 있는 분, 시장부터 알고 싶은 분. 가이드, 지도, 비교, 영상을 아래에 정리했습니다.',
        'c1t': '지역 가이드: 한 지역의 신규 분양을 한 파일로', 'c1d': '지역을 고르면 Keith가 그 지역 분양 중인 프로젝트를 가격과 위치와 함께 정리해 보내드립니다.', 'c1b': '지역 선택', 'c1g': '무료 가이드',
        'c2t': 'MM2H 가이드 (Malaysia My Second Home)', 'c2d': '등급, 정기예금 조건, 외국인이 살 수 있는 부동산을 한 페이지로 설명합니다.', 'c2b': '가이드 읽기', 'c2g': '무료 열람',
        'c3t': '인기 프로젝트 비교', 'c3d': 'Bukit Jalil, KL City Centre RM1M 이하, RM500K 이하 등. 가격, 평방피트당 가격, 월 상환액을 한 번에 비교하세요.', 'c3b': '비교 시작', 'c3g': '바로 보기',
        'c4t': '전국 신규 분양 인터랙티브 지도', 'c4d': '%d개 프로젝트를 한 지도에. 핀을 누르면 가격과 프로젝트 페이지를 볼 수 있습니다.' % N, 'c4b': '지도 열기', 'c4g': '바로 보기',
        'c5t': '시장 분석 영상, 한 편에 한 질문', 'c5d': '외국인도 살 수 있는지, 왜 동남아에서 말레이시아인지, 현장 방문 영상까지 YouTube에 있습니다.', 'c5b': 'YouTube에서 보기', 'c5g': '무료 시청',
        'c6t': '월 상환액 계산기', 'c6d': '가격과 계약금을 입력하면 월 상환액, 총 이자, 대출 가능 금액을 바로 확인할 수 있습니다.', 'c6b': '지금 계산', 'c6g': '무료 도구',
        'c7t': '1:1 무료 상담', 'c7d': '예산, 원하는 지역, 목적을 Keith에게 알려주시면 살펴볼 만한 프로젝트를 추려드립니다.', 'c7b': 'WhatsApp Keith', 'c7g': '무료 상담',
        'mt': '어느 지역을 보고 계신가요?', 'ms': '지역을 고르면 Keith가 WhatsApp으로 가이드를 보내드립니다.',
        'mg': '{a} 가이드', 'mn': '{n}개 프로젝트: {x}', 'mo': '온라인으로 보기', 'mf': '새 프로젝트가 나오면 지역을 계속 추가합니다.',
    },
}
T['ja']['c5d'] = T['ja']['c5d'].replace('東南亜', '東南アジア')
T['zh-TW'] = {k: _cc(v) for k, v in T['zh-CN'].items()}

ICON = {
    'layers': '<path d="M12 3 2 8l10 5 10-5-10-5z"/><path d="m2 13 10 5 10-5"/><path d="m2 18 10 5 10-5" opacity=".0"/>',
    'book': '<path d="M4 4h7a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4z"/><path d="M20 4h-5a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h6z"/>',
    'cols': '<rect x="3" y="4" width="7" height="16" rx="1.5"/><rect x="14" y="4" width="7" height="16" rx="1.5"/>',
    'pin': '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    'play': '<circle cx="12" cy="12" r="9"/><path d="m10 8.5 5.5 3.5-5.5 3.5z"/>',
    'calc': '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 12h2M14 12h2M8 16h2M14 16h2"/>',
    'chat': '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.7A8 8 0 1 1 21 12z"/>',
}
CARDS = [
    ('c1', 'area-guides.jpg', 'layers', '#guides', ' data-open="areas"'),
    ('c2', 'mm2h-guide.jpg', 'book', 'mm2h.html', ''),
    ('c3', 'compare.jpg', 'cols', 'compare.html#popular', ''),
    ('c4', 'map.jpg', 'pin', 'projects.html#projectMap', ''),
    ('c5', 'videos.jpg', 'play', 'https://www.youtube.com/@KeithNahRealEstate/videos', ' target="_blank" rel="noopener"'),
    ('c6', 'calculator.jpg', 'calc', 'calculator.html', ''),
    ('c7', 'consult.jpg', 'chat', waq('Hi Keith, I would like one-to-one advice on Malaysia property.'), ' target="_blank" rel="noopener"'),
]
en = T['en']
cards = ''.join(
    '<article class="rc"><a class="rc-img" href="{h}"{x}><img src="images/res/{img}" alt="" loading="lazy" width="1200" height="700"></a>'
    '<div class="rc-b"><span class="rc-ic"><svg viewBox="0 0 24 24">{ic}</svg></span><span class="rc-g" data-r="{k}g">{g}</span>'
    '<h2 data-r="{k}t">{t}</h2><p data-r="{k}d">{d}</p><a class="rc-btn" href="{h}"{x}><span data-r="{k}b">{b}</span>'
    '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a></div></article>'.format(
        h=E(h), x=x, img=img, ic=ICON[ic], k=k, g=E(en[k + 'g']), t=E(en[k + 't']), d=E(en[k + 'd']), b=E(en[k + 'b']))
    for k, img, ic, h, x in CARDS)

rows = ''.join(
    '<div class="ar"><a class="ar-main" href="{wa}" target="_blank" rel="noopener"><b data-a="{a}" data-n="{n}">{a} guide</b>'
    '<small data-x="{x}" data-n="{n}">{n} projects: {x}</small><svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>'
    '<a class="ar-on" href="area/{s}.html" data-r="mo">View online</a></div>'.format(
        wa=E(waq('Hi Keith, please send me the %s guide (%d projects).' % (a, len(ids)))), a=E(a), n=len(ids), x=E(names(ids)), s=A.slug(a))
    for a, st, ids in areas)

CSS = '''
:root{--bg:#F9F8F6;--ink:#111;--grey:#5A5A5A;--line:rgba(17,17,17,0.08);--gold:#5E60CE;--deep:#1d1b4f;}
*{box-sizing:border-box;margin:0;padding:0;} body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6;}
a{color:inherit;text-decoration:none;} img{display:block;max-width:100%;}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif;line-height:1.25;}
.wrap{max-width:1180px;margin:0 auto;padding:0 5vw;}
.rh{padding:64px 0 34px;} .rh .eb{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);font-weight:700;}
.rh h1{font-size:clamp(34px,5vw,56px);margin:8px 0 14px;} .rh .lead{font-size:18px;font-weight:700;margin-bottom:6px;} .rh p{color:var(--grey);max-width:780px;font-size:15px;}
.rg{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:26px;padding-bottom:80px;}
.rc{background:#fff;border:1px solid var(--line);border-radius:20px;padding:18px;box-shadow:0 10px 30px rgba(29,27,79,.05);transition:transform .3s,box-shadow .3s;display:flex;flex-direction:column;}
.rc:hover{transform:translateY(-3px);box-shadow:0 18px 40px rgba(29,27,79,.12);}
.rc-img{display:block;border-radius:14px;overflow:hidden;background:#f3f1fa;aspect-ratio:12/7;} .rc-img img{width:100%;height:100%;object-fit:cover;transition:transform .5s;} .rc:hover .rc-img img{transform:scale(1.03);}
.rc-b{padding:18px 6px 6px;display:flex;flex-direction:column;flex:1;}
.rc-ic{width:40px;height:40px;border-radius:11px;background:#f3f1fa;border:1px solid rgba(94,96,206,.2);display:flex;align-items:center;justify-content:center;margin-bottom:12px;}
.rc-ic svg{width:20px;height:20px;fill:none;stroke:var(--gold);stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;}
.rc-g{font-size:11.5px;font-weight:700;color:var(--gold);letter-spacing:.06em;text-transform:uppercase;}
.rc h2{font-family:'Inter',sans-serif;font-size:19px;font-weight:800;margin:4px 0 8px;} .rc p{color:var(--grey);font-size:14px;margin-bottom:18px;flex:1;}
.rc-btn{align-self:flex-start;display:inline-flex;align-items:center;gap:8px;background:var(--gold);color:#fff;font-weight:700;font-size:14px;padding:12px 22px;border-radius:100px;transition:background .25s;}
.rc-btn:hover{background:var(--deep);} .rc-btn svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round;}
.rm{position:fixed;inset:0;z-index:100;display:none;align-items:center;justify-content:center;background:rgba(12,12,30,.55);padding:20px;backdrop-filter:blur(3px);}
.rm.open{display:flex;} .rm-box{background:#fff;border-radius:22px;width:min(640px,100%);max-height:88vh;display:flex;flex-direction:column;box-shadow:0 30px 80px rgba(0,0,0,.3);}
.rm-h{display:flex;justify-content:space-between;gap:14px;padding:24px 24px 16px;border-bottom:1px solid var(--line);} .rm-h h3{font-family:'Inter',sans-serif;font-size:24px;font-weight:800;} .rm-h p{color:var(--grey);font-size:13.5px;margin-top:4px;}
.rm-x{all:unset;cursor:pointer;width:40px;height:40px;flex-shrink:0;border-radius:12px;background:#f3f3f6;display:flex;align-items:center;justify-content:center;font-size:22px;}
.rm-l{overflow-y:auto;padding:14px 18px;display:flex;flex-direction:column;gap:10px;}
.ar{border:1px solid var(--line);border-radius:14px;transition:border-color .2s,background .2s;} .ar:hover{border-color:rgba(94,96,206,.45);background:#f7f6fd;}
.ar-main{display:grid;grid-template-columns:1fr 22px;gap:2px 12px;padding:14px 18px 6px;align-items:center;} .ar-main b{font-size:16.5px;font-weight:800;} .ar-main small{grid-row:2;color:var(--grey);font-size:12.5px;}
.ar-main svg{grid-row:1/3;grid-column:2;width:20px;height:20px;fill:none;stroke:var(--gold);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;}
.ar-on{display:inline-block;margin:0 18px 12px;font-size:12px;font-weight:700;color:var(--gold);} .ar-on:after{content:" →";}
.rm-f{padding:12px 24px 18px;border-top:1px solid var(--line);font-size:12px;color:var(--grey);}
footer{border-top:1px solid var(--line);padding:26px 5vw;font-size:13px;color:var(--grey);text-align:center;}
.rc:last-child:nth-child(odd){grid-column:1/-1;flex-direction:row;gap:26px;align-items:center;} .rc:last-child:nth-child(odd) .rc-img{flex:0 0 48%;} .rc:last-child:nth-child(odd) .rc-b{padding:6px 10px;}
@media(max-width:760px){.rg{grid-template-columns:1fr;gap:18px;} .rc:last-child:nth-child(odd){flex-direction:column;gap:0;align-items:stretch;} .rh{padding:40px 0 24px;} .rc{padding:12px;border-radius:16px;} .rm{padding:0;align-items:flex-end;} .rm-box{border-radius:20px 20px 0 0;max-height:90vh;} .rm-h h3{font-size:20px;}}
'''

JS = '''<script>(function(){var T=%s;
function lang(){var l='en';try{l=localStorage.getItem('kn_lang')||'en'}catch(e){}return T[l]?l:'en';}
function f(s,o){return s.replace(/\\{(\\w)\\}/g,function(_,k){return o[k];});}
function apply(){var L=T[lang()];document.querySelectorAll('[data-r]').forEach(function(el){var v=L[el.getAttribute('data-r')];if(v)el.textContent=v;});
document.querySelectorAll('[data-a]').forEach(function(el){el.textContent=f(L.mg,{a:el.getAttribute('data-a')});});
document.querySelectorAll('small[data-x]').forEach(function(el){el.textContent=f(L.mn,{n:el.getAttribute('data-n'),x:el.getAttribute('data-x')});});
document.title=L.title+' | Keith Nah Real Estate';}
var m=document.getElementById('rmAreas');
function open(o){m.classList.toggle('open',o);document.body.style.overflow=o?'hidden':'';}
document.addEventListener('click',function(e){if(e.target.closest('[data-open="areas"]')){e.preventDefault();open(true);}else if(e.target===m||e.target.closest('.rm-x'))open(false);});
document.addEventListener('keydown',function(e){if(e.key==='Escape')open(false);});
if(location.hash==='#guides')open(true);
document.addEventListener('DOMContentLoaded',function(){var s=window.knSetLang;if(typeof s==='function')window.knSetLang=function(){var r=s.apply(this,arguments);apply();return r;};apply();});
apply();})();</script>''' % json.dumps(T, ensure_ascii=False)

desc = 'Free resources from Keith Nah: area guides of new launch condos, the MM2H guide, project comparisons, an interactive map, videos and a mortgage calculator.'
page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Free Resources | Keith Nah Real Estate</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{site}/resources.html">
<meta property="og:title" content="Free Resources | Keith Nah Real Estate"><meta property="og:description" content="{desc}"><meta property="og:url" content="{site}/resources.html"><meta property="og:image" content="{site}/images/res/area-guides.jpg">
<link rel="icon" type="image/png" href="images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<header>
  <a class="logo" href=""><img src="images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Keith Nah Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="{wa}" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
<main class="wrap">
  <section class="rh"><span class="eb" data-r="eyebrow">Free Resources</span><h1 data-r="title">Free Resources</h1>
    <p class="lead" data-r="lead">{lead}</p><p data-r="sub">{sub}</p></section>
  <section class="rg">{cards}</section>
</main>
<div class="rm" id="rmAreas" role="dialog" aria-modal="true" aria-labelledby="rmT"><div class="rm-box">
  <div class="rm-h"><div><h3 id="rmT" data-r="mt">{mt}</h3><p data-r="ms">{ms}</p></div><button type="button" class="rm-x" aria-label="Close">&times;</button></div>
  <div class="rm-l">{rows}</div>
  <div class="rm-f" data-r="mf">{mf}</div>
</div></div>
<footer>&copy; 2026 Keith Nah Real Estate. All rights reserved.</footer>
{js}
</body>
</html>
'''.format(desc=E(desc), site=SITE, css=CSS, wa=E(waq('Hi Keith, I would like to explore more on Malaysia Property.')),
           lead=E(en['lead']), sub=E(en['sub']), cards=cards, mt=E(en['mt']), ms=E(en['ms']), rows=rows, mf=E(en['mf']), js=JS)
out = SH.apply(page, '', 'resources.html')
open('resources.html', 'w', encoding='utf-8').write(out)

# ---------- main menu: MM2H -> Free Resources on the static pages ----------
FR = {"zh-CN": "免费资源", "zh-TW": "免費資源", "ms": "Sumber Percuma", "ja": "無料リソース", "ko": "무료 자료"}
STATIC = ['index.html', 'projects.html', 'compare.html', 'blog.html', 'about-keith.html', 'calculator.html', 'mm2h.html']
for f in STATIC:
    t = open(f, encoding='utf-8').read()
    o = t
    t = re.sub(r'<a href="mm2h\.html"( data-i18n="nav_mm2h")?( class="active")?>MM2H 第二家园</a>',
               lambda m: '<a href="resources.html"%s>Free Resources</a>' % (' data-i18n="nav_res"' if m.group(1) else ''), t)
    if '"Free Resources": {' not in t and '"About Keith": {"zh-CN"' in t:   # header translations (compact JSON)
        t = t.replace('"About Keith": {"zh-CN"', '"Free Resources": %s, "About Keith": {"zh-CN"' % json.dumps(FR, ensure_ascii=False), 1)
    if 'data-i18n="nav_res"' in t and '"nav_res"' not in t.split('data-i18n="nav_res"', 1)[1]:
        t = t.replace('"nav_about": {', '"nav_res": %s,\n  "nav_about": {' % json.dumps(FR, ensure_ascii=False), 1)
    if t != o:
        open(f, 'w', encoding='utf-8').write(t)

# mobile drawer on the static pages (built from the header links): keep MM2H under Free Resources
DR_A = "      L.appendChild(c);\n    });\n    var lg=document.getElementById('knLang');"
DR_B = ("      L.appendChild(c);\n      if(h==='resources.html'){ var m2=document.createElement('a'); m2.href='mm2h.html'; m2.textContent='MM2H \u7b2c\u4e8c\u5bb6\u56ed';"
        " if(cur==='mm2h.html') m2.className='active'; L.appendChild(m2); }\n    });\n    var lg=document.getElementById('knLang');")
for f in STATIC:
    t = open(f, encoding='utf-8').read()
    if DR_A in t and "m2.href='mm2h.html'" not in t:
        open(f, 'w', encoding='utf-8').write(t.replace(DR_A, DR_B, 1))
        print('drawer', f)

# sitemap
sm = open('sitemap.xml', encoding='utf-8').read() if os.path.exists('sitemap.xml') else ''
if sm and '/resources.html' not in sm:
    sm = sm.replace('</urlset>', '  <url><loc>%s/resources.html</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>\n</urlset>' % SITE)
    open('sitemap.xml', 'w', encoding='utf-8').write(sm)
print('resources: %d cards, %d area guides' % (len(CARDS), len(areas)))
