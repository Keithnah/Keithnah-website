"""Build resources.html (the Free Toolkit, 免费资源) and put it in the main menu where MM2H used to be.

- resources.html: two-column cards for the free PDF area guides (a pop-up lists the areas; each opens
  its landing page in guides/, see tools/build_guides.py), the MM2H guide, popular comparisons, the
  all-projects map, YouTube videos, the calculator and one-to-one advice. Six site languages.
- Main menu: "MM2H 第二家园" is replaced by "Free Toolkit" on the static pages; the generated pages take
  it from the NAV lists. MM2H stays in the mobile menus, on this page and at mm2h.html.
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
import build_guides as G  # noqa: E402
import site_header as SH  # noqa: E402

E = lambda s: html.escape(str(s), quote=True)
SITE = 'https://keithnah.com'
WA = 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0'
waq = lambda m: WA % re.sub(r'\s', '+', '(KNRE) ' + m)
N = len(A.P)
LABEL = 'Free Toolkit'
NAV_TR = {"zh-CN": "免费资源", "zh-TW": "免費資源", "ms": "Kit Percuma", "ja": "無料ツールキット", "ko": "무료 툴킷"}

try:
    import opencc
    _cc = opencc.OpenCC('s2tw').convert
except ImportError:
    _cc = lambda s: s

# ---------- area guides offered in the pop-up ----------
GUIDES = G.guides()


def names(ids, n=3):
    ns = sorted((A.P[k]['name'] for k in ids), key=lambda s: s.lower())
    return ', '.join(ns[:n]) + ('…' if len(ns) > n else '')


# ---------- texts ----------
T = {
    'en': {
        'title': 'Free Toolkit', 'eyebrow': 'Free Toolkit',
        'lead': 'Where would you like to start?',
        'sub': 'Some buyers start from a city, some already have a project in mind, and some just want to understand the market. Guides, maps, comparisons and videos are sorted below.',
        'c1t': 'Area guides: every new launch in one area, in one file', 'c1d': 'Pick an area and download a free PDF of the projects for sale there: prices, psf, sizes, completion, rail stations and a map.', 'c1b': 'Choose an area', 'c1g': 'Free PDF',
        'c2t': 'MM2H guide (Malaysia My Second Home)', 'c2d': 'The tiers, the fixed deposit and what foreign buyers can purchase, explained on one page.', 'c2b': 'Read the guide', 'c2g': 'Free to read',
        'c3t': 'Popular project comparisons', 'c3d': 'Bukit Jalil, KL City Centre under RM1M, under RM500K and more: prices, psf and monthly instalments side by side in one tap.', 'c3b': 'Start comparing', 'c3g': 'View now',
        'c4t': 'Interactive map of every new launch', 'c4d': 'All %d projects on one map. Tap a pin to see the price and open the project page.' % N, 'c4b': 'Open the map', 'c4g': 'View now',
        'c5t': 'Market videos, one question each', 'c5d': 'Can foreigners buy, why Malaysia leads Southeast Asia, and project site visits, all on YouTube.', 'c5b': 'Watch on YouTube', 'c5g': 'Free to watch',
        'c6t': 'Monthly instalment calculator', 'c6d': 'Enter the price and down payment to see the monthly instalment, total interest and how much you can borrow.', 'c6b': 'Calculate now', 'c6g': 'Free tool',
        'c7t': 'One-to-one advice', 'c7d': 'Tell Keith your budget, preferred area and purpose, and he will shortlist the projects worth a closer look.', 'c7b': 'WhatsApp Keith', 'c7g': 'Free advice',
        'mt': 'Which area are you looking at?', 'ms': 'Pick an area to download its free PDF guide.',
        'mg': '{a} guide', 'mn': '{n} projects: {x}', 'mo': 'View online', 'mf': 'More areas are added as new projects launch.',
    },
    'zh-CN': {
        'title': '免费资源', 'eyebrow': '免费资源',
        'lead': '你想先从哪里开始？',
        'sub': '有人先看城市，有人心里已经有项目，也有人只想先了解市场。懒人包、地图、比较和影片，都分好类放在下面。',
        'c1t': '地区懒人包：一区的新项目，一份看完', 'c1d': '选一个地区，免费下载那一区在卖项目的 PDF 懒人包：价格、呎价、面积、竣工、轨道站和地图。', 'c1b': '选地区拿资料', 'c1g': '免费 PDF',
        'c2t': 'MM2H 第二家园指南', 'c2d': '三种等级、定期存款要求、外国人可以买什么，一页讲清楚。', 'c2b': '阅读指南', 'c2g': '免费阅读',
        'c3t': '热门项目比较', 'c3d': 'Bukit Jalil、KL City Centre RM1M 以下、RM500K 以下等热门组合，一键并排比较价格、呎价和月供。', 'c3b': '开始比较', 'c3g': '直接看',
        'c4t': '全马新楼盘互动地图', 'c4d': '%d 个项目标在同一张地图上，点一下就看到价格和项目页。' % N, 'c4b': '打开地图', 'c4g': '直接看',
        'c5t': '房市分析影片，一支讲一个问题', 'c5d': '外国人能不能买、为什么东南亚首选马来西亚、项目实地看房，都在 YouTube。', 'c5b': '去 YouTube 看', 'c5g': '免费观看',
        'c6t': '月供计算器', 'c6d': '输入房价和首付，马上算出月供、总利息和可贷款额。', 'c6b': '马上计算', 'c6g': '免费工具',
        'c7t': '一对一免费咨询', 'c7d': '告诉 Keith 你的预算、地区和用途，他帮你筛出值得细看的项目。', 'c7b': 'WhatsApp Keith', 'c7g': '免费咨询',
        'mt': '你在看哪个地区？', 'ms': '选一个地区，下载那一区的免费 PDF 懒人包。',
        'mg': '{a} 懒人包', 'mn': '一次看 {n} 个项目：{x}', 'mo': '先在线看', 'mf': '有新项目推出时，会陆续加入更多地区。',
    },
    'ms': {
        'title': 'Kit Percuma', 'eyebrow': 'Kit Percuma',
        'lead': 'Dari mana anda mahu bermula?',
        'sub': 'Ada pembeli bermula dengan bandar, ada yang sudah ada projek pilihan, dan ada yang mahu memahami pasaran dahulu. Panduan, peta, perbandingan dan video disusun di bawah.',
        'c1t': 'Panduan kawasan: semua projek baharu satu kawasan dalam satu fail', 'c1d': 'Pilih kawasan dan muat turun PDF percuma projek yang dijual di sana: harga, harga sk, saiz, tarikh siap, stesen rel dan peta.', 'c1b': 'Pilih kawasan', 'c1g': 'PDF percuma',
        'c2t': 'Panduan MM2H (Malaysia My Second Home)', 'c2d': 'Peringkat, simpanan tetap dan apa yang boleh dibeli oleh pembeli asing, diterangkan dalam satu halaman.', 'c2b': 'Baca panduan', 'c2g': 'Bacaan percuma',
        'c3t': 'Perbandingan projek popular', 'c3d': 'Bukit Jalil, KL City Centre bawah RM1M, bawah RM500K dan lain-lain: harga, harga sk dan ansuran bulanan sebelah-menyebelah dengan satu ketikan.', 'c3b': 'Mula membanding', 'c3g': 'Lihat sekarang',
        'c4t': 'Peta interaktif semua projek baharu', 'c4d': 'Kesemua %d projek dalam satu peta. Ketik pin untuk melihat harga dan membuka halaman projek.' % N, 'c4b': 'Buka peta', 'c4g': 'Lihat sekarang',
        'c5t': 'Video pasaran, satu soalan setiap satu', 'c5d': 'Bolehkah warga asing membeli, mengapa Malaysia pilihan utama di Asia Tenggara, dan lawatan tapak projek, semuanya di YouTube.', 'c5b': 'Tonton di YouTube', 'c5g': 'Tontonan percuma',
        'c6t': 'Kalkulator ansuran bulanan', 'c6d': 'Masukkan harga dan deposit untuk melihat ansuran bulanan, jumlah faedah dan jumlah pinjaman yang layak.', 'c6b': 'Kira sekarang', 'c6g': 'Alat percuma',
        'c7t': 'Nasihat satu-ke-satu', 'c7d': 'Beritahu Keith bajet, kawasan pilihan dan tujuan anda, dan dia akan menyenarai pendek projek yang patut dilihat.', 'c7b': 'WhatsApp Keith', 'c7g': 'Nasihat percuma',
        'mt': 'Kawasan mana yang anda lihat?', 'ms': 'Pilih kawasan untuk memuat turun panduan PDF percumanya.',
        'mg': 'Panduan {a}', 'mn': '{n} projek: {x}', 'mo': 'Lihat dalam talian', 'mf': 'Lebih banyak kawasan akan ditambah apabila projek baharu dilancarkan.',
    },
    'ja': {
        'title': '無料ツールキット', 'eyebrow': '無料ツールキット',
        'lead': 'どこから始めますか？',
        'sub': '都市から探す方、気になる物件がある方、まず市場を知りたい方。ガイド、地図、比較、動画を下にまとめました。',
        'c1t': 'エリアガイド：エリアの新築物件を1つの資料に', 'c1d': 'エリアを選ぶと、販売中物件の無料PDFをダウンロードできます：価格、単価、面積、完成時期、最寄り駅、地図。', 'c1b': 'エリアを選ぶ', 'c1g': '無料PDF',
        'c2t': 'MM2H ガイド（Malaysia My Second Home）', 'c2d': 'ランク、定期預金の条件、外国人が購入できる物件を1ページで解説。', 'c2b': 'ガイドを読む', 'c2g': '無料で読める',
        'c3t': '人気の物件比較', 'c3d': 'Bukit Jalil、KL City Centre RM1M以下、RM500K以下など。価格・平方フィート単価・月々の返済をワンタップで比較。', 'c3b': '比較を始める', 'c3g': 'すぐ見る',
        'c4t': '全新築物件のインタラクティブ地図', 'c4d': '%d件の物件を1つの地図に。ピンをタップすると価格と物件ページが見られます。' % N, 'c4b': '地図を開く', 'c4g': 'すぐ見る',
        'c5t': '市場解説動画、1本に1テーマ', 'c5d': '外国人は購入できるか、なぜ東南亜でマレーシアなのか、物件の現地見学など、YouTube で公開中。', 'c5b': 'YouTube で見る', 'c5g': '無料で見る',
        'c6t': '月々の返済計算機', 'c6d': '価格と頭金を入力すると、月々の返済額、総利息、借入可能額がすぐにわかります。', 'c6b': '計算する', 'c6g': '無料ツール',
        'c7t': '個別無料相談', 'c7d': '予算、希望エリア、目的を Keith に伝えれば、検討する価値のある物件を絞り込みます。', 'c7b': 'WhatsApp Keith', 'c7g': '無料相談',
        'mt': 'どのエリアをご覧ですか？', 'ms': 'エリアを選んで無料PDFガイドをダウンロード。',
        'mg': '{a} ガイド', 'mn': '{n}件の物件：{x}', 'mo': 'オンラインで見る', 'mf': '新しい物件の発売に合わせてエリアを追加していきます。',
    },
    'ko': {
        'title': '무료 툴킷', 'eyebrow': '무료 툴킷',
        'lead': '어디서부터 시작할까요?',
        'sub': '도시부터 보는 분, 이미 관심 프로젝트가 있는 분, 시장부터 알고 싶은 분. 가이드, 지도, 비교, 영상을 아래에 정리했습니다.',
        'c1t': '지역 가이드: 한 지역의 신규 분양을 한 파일로', 'c1d': '지역을 고르면 분양 중인 프로젝트의 무료 PDF를 받을 수 있습니다: 가격, 평방피트당 가격, 면적, 준공, 역, 지도.', 'c1b': '지역 선택', 'c1g': '무료 PDF',
        'c2t': 'MM2H 가이드 (Malaysia My Second Home)', 'c2d': '등급, 정기예금 조건, 외국인이 살 수 있는 부동산을 한 페이지로 설명합니다.', 'c2b': '가이드 읽기', 'c2g': '무료 열람',
        'c3t': '인기 프로젝트 비교', 'c3d': 'Bukit Jalil, KL City Centre RM1M 이하, RM500K 이하 등. 가격, 평방피트당 가격, 월 상환액을 한 번에 비교하세요.', 'c3b': '비교 시작', 'c3g': '바로 보기',
        'c4t': '전국 신규 분양 인터랙티브 지도', 'c4d': '%d개 프로젝트를 한 지도에. 핀을 누르면 가격과 프로젝트 페이지를 볼 수 있습니다.' % N, 'c4b': '지도 열기', 'c4g': '바로 보기',
        'c5t': '시장 분석 영상, 한 편에 한 질문', 'c5d': '외국인도 살 수 있는지, 왜 동남아에서 말레이시아인지, 현장 방문 영상까지 YouTube에 있습니다.', 'c5b': 'YouTube에서 보기', 'c5g': '무료 시청',
        'c6t': '월 상환액 계산기', 'c6d': '가격과 계약금을 입력하면 월 상환액, 총 이자, 대출 가능 금액을 바로 확인할 수 있습니다.', 'c6b': '지금 계산', 'c6g': '무료 도구',
        'c7t': '1:1 무료 상담', 'c7d': '예산, 원하는 지역, 목적을 Keith에게 알려주시면 살펴볼 만한 프로젝트를 추려드립니다.', 'c7b': 'WhatsApp Keith', 'c7g': '무료 상담',
        'mt': '어느 지역을 보고 계신가요?', 'ms': '지역을 골라 무료 PDF 가이드를 다운로드하세요.',
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
    '<a class="ar" href="guides/{s}.html"><span class="ar-pdf">PDF</span><span class="ar-t"><b data-a="{a}" data-n="{n}">{a} guide</b>'
    '<small data-x="{x}" data-n="{n}">{n} projects: {x}</small></span><svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>'.format(
        s=g['slug'], a=E(g['area']), n=g['n'], x=E(names(g['ids'])))
    for g in GUIDES)

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
.ar{display:grid;grid-template-columns:auto 1fr 22px;gap:14px;align-items:center;border:1px solid var(--line);border-radius:14px;padding:14px 18px;transition:border-color .2s,background .2s;}
.ar:hover{border-color:rgba(94,96,206,.45);background:#f7f6fd;} .ar-pdf{background:#efeefb;color:var(--gold);font-size:11px;font-weight:800;letter-spacing:.06em;padding:8px 9px;border-radius:9px;}
.ar-t b{display:block;font-size:16.5px;font-weight:800;line-height:1.3;} .ar-t small{color:var(--grey);font-size:12.5px;}
.ar svg{width:20px;height:20px;fill:none;stroke:var(--gold);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;}
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
<header>
  <a class="logo" href=""><img src="images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Keith Nah Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="{wa}" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
<main class="wrap">
  <section class="rh"><span class="eb" data-r="eyebrow">Free Toolkit</span><h1 data-r="title">Free Toolkit</h1>
    <p class="lead" data-r="lead">{lead}</p><p data-r="sub">{sub}</p></section>
  <section class="rg">{cards}</section>
</main>
<div class="rm" id="rmAreas" role="dialog" aria-modal="true" aria-labelledby="rmT"><div class="rm-box">
  <div class="rm-h"><div><h3 id="rmT" data-r="mt">{mt}</h3><p data-r="ms">{ms}</p></div><button type="button" class="rm-x" aria-label="Close">&times;</button></div>
  <div class="rm-l">{rows}</div>
  <div class="rm-f" data-r="mf">{mf}</div>
</div></div>
<footer>&copy; 2026 Keith Nah Real Estate. All rights reserved.</footer>
<script src="lead-tracker.js"></script>
{js}
</body>
</html>
'''.format(desc=E(desc), site=SITE, css=CSS, wa=E(waq('Hi Keith, I would like to explore more on Malaysia Property.')),
           lead=E(en['lead']), sub=E(en['sub']), cards=cards, mt=E(en['mt']), ms=E(en['ms']), rows=rows, mf=E(en['mf']), js=JS)
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

# ---------- home page: MM2H section (after the YouTube videos), linking to mm2h.html ----------
MM = {
    'mm_eb': ('Malaysia My Second Home', {'zh-CN': '马来西亚第二家园', 'ms': 'Malaysia My Second Home', 'ja': 'マレーシア・マイ・セカンドホーム', 'ko': '말레이시아 마이 세컨드 홈'}),
    'mm_h2': ('Live in Malaysia on a long-stay pass.', {'zh-CN': '用长期签证，住在马来西亚。', 'ms': 'Tinggal di Malaysia dengan pas jangka panjang.', 'ja': '長期滞在ビザでマレーシアに暮らす。', 'ko': '장기 체류 비자로 말레이시아에서 살기.'}),
    'mm_p': ('Malaysia My Second Home (MM2H) lets foreigners and their families live in Malaysia on a renewable pass of 5, 15 or 20 years. Many of Keith\'s clients combine it with buying a home here.',
             {'zh-CN': 'MM2H（马来西亚第二家园）让外国人和家人以 5、15 或 20 年可续签的签证住在马来西亚。很多 Keith 的客户会同时在这里买房。',
              'ms': 'Malaysia My Second Home (MM2H) membolehkan warga asing dan keluarga tinggal di Malaysia dengan pas 5, 15 atau 20 tahun yang boleh diperbaharui. Ramai pelanggan Keith menggabungkannya dengan membeli rumah di sini.',
              'ja': 'MM2H（マレーシア・マイ・セカンドホーム）は、外国人とその家族が5年・15年・20年の更新可能なビザでマレーシアに住める制度です。Keith のお客様の多くは、住宅購入と組み合わせています。',
              'ko': 'MM2H(말레이시아 마이 세컨드 홈)는 외국인과 가족이 5년, 15년 또는 20년 갱신 가능한 비자로 말레이시아에 살 수 있는 제도입니다. Keith의 많은 고객이 주택 구매와 함께 신청합니다.'}),
    'mm_fd': ('Fixed deposit', {'zh-CN': '定期存款', 'ms': 'Simpanan tetap', 'ja': '定期預金', 'ko': '정기예금'}),
    'mm_pp': ('Property from', {'zh-CN': '购房最低', 'ms': 'Hartanah dari', 'ja': '不動産購入', 'ko': '부동산 최소'}),
    'mm_vd': ('Visa', {'zh-CN': '签证', 'ms': 'Visa', 'ja': 'ビザ', 'ko': '비자'}),
    'mm_y5': ('5 years', {'zh-CN': '5 年', 'ms': '5 tahun', 'ja': '5年', 'ko': '5년'}),
    'mm_y15': ('15 years', {'zh-CN': '15 年', 'ms': '15 tahun', 'ja': '15年', 'ko': '15년'}),
    'mm_y20': ('20 years', {'zh-CN': '20 年', 'ms': '20 tahun', 'ja': '20年', 'ko': '20년'}),
    'mm_btn': ('Read the full MM2H guide', {'zh-CN': '阅读完整 MM2H 指南', 'ms': 'Baca panduan MM2H penuh', 'ja': 'MM2H ガイドを読む', 'ko': 'MM2H 가이드 전체 보기'}),
    'mm_ask': ('Ask Keith about MM2H', {'zh-CN': '咨询 Keith 关于 MM2H', 'ms': 'Tanya Keith tentang MM2H', 'ja': 'MM2H について Keith に相談', 'ko': 'MM2H에 대해 Keith에게 문의'}),
    'mm_note': ('Figures are a general guide to the current tiers; the government may update them.', {'zh-CN': '以上为现行等级的大致要求，政府可能会更新。', 'ms': 'Angka ialah panduan umum peringkat semasa; kerajaan boleh mengemas kininya.', 'ja': '現行ランクの目安です。政府により変更される場合があります。', 'ko': '현행 등급의 일반적인 기준이며 정부가 변경할 수 있습니다.'}),
}
TIERS = [('Silver', '#8e9aaf', 'USD 150,000', 'RM 600,000', 'mm_y5'), ('Gold', '#c9a227', 'USD 500,000', 'RM 1,000,000', 'mm_y15'),
         ('Platinum', '#5E60CE', 'USD 1,000,000', 'RM 2,000,000', 'mm_y20')]
t_ = lambda k: '<span data-i18n="%s">%s</span>' % (k, E(MM[k][0]))
tiers = ''.join('<div class="mmh-t" style="--tc:%s"><b>%s</b><dl><dt>%s</dt><dd>%s</dd><dt>%s</dt><dd>%s</dd><dt>%s</dt><dd>%s</dd></dl></div>' % (
    c, n, t_('mm_fd'), fd, t_('mm_pp'), pp, t_('mm_vd'), t_(y)) for n, c, fd, pp, y in TIERS)
MM_HTML = ('<!-- KN-MM2H:START -->\n<style>'
           '#mm2h-home{padding:100px 5vw;background:linear-gradient(160deg,#1d1b4f,#2b2973 70%%,#3b3c99);color:#fff;}'
           '.mmh{max-width:1220px;margin:0 auto;display:grid;grid-template-columns:1fr 1.15fr;gap:56px;align-items:center;}'
           '.mmh-logo{display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:6px;}.mmh-logo b{font-family:"Playfair Display",serif;font-size:clamp(52px,6vw,76px);line-height:1;letter-spacing:.02em;color:#fff;text-shadow:0 6px 30px rgba(94,96,206,.6);}.mmh-logo span{font-size:clamp(15px,1.6vw,19px);font-weight:700;letter-spacing:.06em;color:#1d1b4f;background:#b9b4ff;padding:8px 16px;border-radius:100px;}.mmh h2{font-size:clamp(28px,3.2vw,40px);color:#fff;margin:18px 0 16px;line-height:1.2;} .mmh p{opacity:.86;font-size:15.5px;font-weight:500;margin-bottom:28px;max-width:520px;}'
           '.mmh-b{display:flex;gap:12px;flex-wrap:wrap;} .mmh-b a{display:inline-flex;align-items:center;gap:8px;padding:14px 24px;border-radius:100px;font-weight:700;font-size:14px;letter-spacing:.02em;transition:transform .2s,background .2s;}'
           '.mmh-b a:hover{transform:translateY(-2px);} .mmh-go{background:#fff;color:#1d1b4f;} .mmh-wa{border:1px solid rgba(255,255,255,.35);color:#fff;} .mmh-wa:hover{background:rgba(255,255,255,.1);}'
           '.mmh-ts{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;} .mmh-t{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.14);border-top:4px solid var(--tc);border-radius:16px;padding:20px 18px;}'
           '.mmh-t>b{display:block;font-family:"Playfair Display",serif;font-size:22px;margin-bottom:12px;} .mmh-t dt{font-size:11px;letter-spacing:.1em;text-transform:uppercase;opacity:.65;margin-top:10px;} .mmh-t dd{font-size:15.5px;font-weight:700;}'
           '.mmh small{display:block;margin-top:14px;font-size:11.5px;opacity:.6;}'
           '@media(max-width:900px){#mm2h-home{padding:70px 20px;} .mmh{grid-template-columns:1fr;gap:32px;} .mmh-ts{grid-template-columns:1fr;} .mmh-t{display:grid;grid-template-columns:110px 1fr;align-items:center;} .mmh-t dl{display:grid;grid-template-columns:auto auto;gap:2px 12px;} .mmh-t dt{margin:0;align-self:center;}}'
           '</style>\n<section id="mm2h-home"><div class="mmh"><div>'
           '<div class="mmh-logo"><b>MM2H</b><span data-i18n="mm_eb">Malaysia My Second Home</span></div><h2 data-i18n="mm_h2">%s</h2><p data-i18n="mm_p">%s</p>'
           '<div class="mmh-b"><a class="mmh-go" href="mm2h.html"><span data-i18n="mm_btn">%s</span> &rarr;</a>'
           '<a class="mmh-wa" href="%s" target="_blank" rel="noopener" data-i18n="mm_ask">%s</a></div></div>'
           '<div><div class="mmh-ts">%s</div><small data-i18n="mm_note">%s</small></div></div></section>\n<!-- KN-MM2H:END -->\n') % (
    E(MM['mm_h2'][0]), E(MM['mm_p'][0]), E(MM['mm_btn'][0]), E(waq('Hi Keith, I would like to know more about MM2H.')), E(MM['mm_ask'][0]), tiers, E(MM['mm_note'][0]))
ix = open('index.html', encoding='utf-8').read()
ix = re.sub(r'<!-- KN-MM2H:START -->.*?<!-- KN-MM2H:END -->\n', '', ix, flags=re.S)
anchor = '<!-- ===================== FAQ'
if anchor not in ix:
    anchor = '<section id="faq">'
ix = ix.replace(anchor, MM_HTML + anchor, 1)
d0 = ix.index('const I18N = {') + len('const I18N = {')
for k, (en_, tr) in MM.items():
    tr = dict(tr)
    tr['zh-TW'] = _cc(tr['zh-CN'])
    entry = '\n  "%s": %s,' % (k, json.dumps(tr, ensure_ascii=False))
    ix = re.sub(r'\n  "%s": \{[^}]*\},' % k, '', ix)
    d0 = ix.index('const I18N = {') + len('const I18N = {')
    ix = ix[:d0] + entry + ix[d0:]
open('index.html', 'w', encoding='utf-8').write(ix)
print('home: MM2H section')

# ---------- credential badge (REN number + agency) on the home and About Keith pages ----------
REN_HTML = ('<p class="keith-ren"><span class="kr-ic" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 2.8 4.5 5.6v5.6c0 4.6 3.1 8.6 7.5 10 4.4-1.4 7.5-5.4 7.5-10V5.6z"/>'
            '<path d="m8.6 12.2 2.4 2.4 4.6-4.8"/></svg></span><span class="kr-a"><small>Registered Estate Negotiator</small><b>REN 60517</b></span>'
            '<span class="kr-sep" aria-hidden="true"></span><span class="kr-b"><small>Agency</small><b>IQI Global</b></span></p>')
REN_CSS = ('.keith-hero-copy p.keith-ren{display:inline-flex; align-items:center; gap:14px; margin:4px 0 18px; padding:10px 18px 10px 10px; border-radius:16px;'
           ' background:linear-gradient(135deg,#f3f1fa,#fff); border:1px solid rgba(94,96,206,.25); box-shadow:0 8px 22px rgba(29,27,79,.08); color:#1d1b4f; line-height:1.25; max-width:none;}'
           ' .keith-ren .kr-ic{width:40px; height:40px; flex-shrink:0; border-radius:12px; background:#5E60CE; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 12px rgba(94,96,206,.35);}'
           ' .keith-ren .kr-ic svg{width:22px; height:22px; fill:none; stroke:#fff; stroke-width:2; stroke-linecap:round; stroke-linejoin:round;}'
           ' .keith-ren small{display:block; font-size:10.5px; font-weight:600; letter-spacing:.1em; text-transform:uppercase; color:#6b6a85;}'
           ' .keith-ren b{display:block; font-size:17px; font-weight:800; letter-spacing:.02em; color:#1d1b4f;}'
           ' .keith-ren .kr-sep{width:1px; align-self:stretch; background:rgba(94,96,206,.25);}'
           ' @media(max-width:480px){.keith-hero-copy p.keith-ren{gap:10px; padding:8px 14px 8px 8px;} .keith-ren .kr-ic{width:34px; height:34px;} .keith-ren b{font-size:15px;} .keith-ren small{font-size:9.5px; letter-spacing:.06em;}}')
REN_TR = {'Registered Estate Negotiator': {'zh-CN': '注册房产经纪', 'ms': 'Perunding Hartanah Berdaftar', 'ja': '登録不動産ネゴシエーター', 'ko': '등록 부동산 중개인'},
          'Agency': {'zh-CN': '所属公司', 'ms': 'Agensi', 'ja': '所属会社', 'ko': '소속 회사'}}
for f in ('index.html', 'about-keith.html'):
    t = open(f, encoding='utf-8').read()
    o = t
    h = REN_HTML
    if 'const I18N = {' in t:   # the home page translates through data-i18n
        h = h.replace('<small>Registered Estate Negotiator</small>', '<small data-i18n="kr_l1">Registered Estate Negotiator</small>').replace(
            '<small>Agency</small>', '<small data-i18n="kr_l2">Agency</small>')
        for k, en_ in (('kr_l1', 'Registered Estate Negotiator'), ('kr_l2', 'Agency')):
            tr = dict(REN_TR[en_]); tr['zh-TW'] = _cc(tr['zh-CN'])
            t = re.sub(r'\n  "%s": \{[^}]*\},' % k, '', t)
            d0 = t.index('const I18N = {') + len('const I18N = {')
            t = t[:d0] + '\n  "%s": %s,' % (k, json.dumps(tr, ensure_ascii=False)) + t[d0:]
    t = re.sub(r'<p class="keith-ren">.*?</p>', lambda _: h, t, count=1, flags=re.S)
    t = re.sub(r'\.keith-hero-copy p\.keith-ren\{[^}]*\}(?: \.keith-ren [^\n]*)?', lambda _: REN_CSS, t, count=1)
    if t != o:
        open(f, 'w', encoding='utf-8').write(t)
for l in ['zh-CN', 'zh-TW', 'ms', 'ja', 'ko']:
    p = 'i18n-projects-%s.js' % l
    t = open(p, encoding='utf-8').read()
    m = 'window.KN_TR["%s"]=' % l
    a = t.index(m) + len(m)
    d, n = json.JSONDecoder().raw_decode(t[a:])
    ch = False
    for en_, tr in REN_TR.items():
        v = tr.get(l) or _cc(tr['zh-CN'])
        if d.get(en_) != v:
            d[en_] = v
            ch = True
    if ch:
        open(p, 'w', encoding='utf-8').write(t[:a] + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + t[a + n:])
print('credential badge updated')
