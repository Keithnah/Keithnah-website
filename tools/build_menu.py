"""Drop-down sub-menus in the main menu of every page.

Each main menu item (View Projects, Compare Projects, News, Free Toolkit, About Keith) gets a list
of sub-pages that opens on hover (computers) and shows indented in the phone menu. The Calculator
item leaves the main menu (it is under Free Toolkit). Sub-menu labels follow the visitor's
language. Run by tools/build_all.py before float_wa.py (which copies the menu into the phone menu).
"""
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
DIRS = ['', 'article', 'area', 'best', 'developer', 'guides', 'mm2h', 'notes', 'property', 'station', 'topic', 'vs']
WA = 'https://api.whatsapp.com/send/?phone=60102821568&text=%28KNRE%29+Hi+Keith%2C+I+would+like+to+explore+more+on+Malaysia+Property.&type=phone_number&app_absent=0'

L = {  # key: [en, zh-CN, zh-TW, ms, ja, ko]
    'browse': ['Browse Projects', '浏览项目', '瀏覽項目', 'Semak Imbas Projek', '物件を探す', '프로젝트 둘러보기'],
    'all': ['All Project List', '全部项目列表', '全部項目列表', 'Senarai Semua Projek', '全物件リスト', '전체 프로젝트 목록'],
    'short': ['Project Shortlist', '帮我挑项目', '幫我挑項目', 'Senarai Pendek Projek', 'おすすめ物件診断', '프로젝트 추천'],
    'dev': ['Search by Developer', '按发展商搜索', '按發展商搜尋', 'Cari Mengikut Pemaju', 'デベロッパーから探す', '개발사별 검색'],
    'station': ['Search by Station', '按地铁站搜索', '按捷運站搜尋', 'Cari Mengikut Stesen', '駅から探す', '역별 검색'],
    'tag': ['Search by Tag', '按标签搜索', '按標籤搜尋', 'Cari Mengikut Tag', 'タグから探す', '태그별 검색'],
    'state': ['Search by State', '按州属搜索', '按州屬搜尋', 'Cari Mengikut Negeri', '州から探す', '주별 검색'],
    'best': ['Best New Launches', '精选新盘', '精選新盤', 'Projek Baharu Terbaik', 'おすすめ新築物件', '추천 신규 분양'],
    'map': ['Project Map', '项目地图', '項目地圖', 'Peta Projek', '物件マップ', '프로젝트 지도'],
    'cmp': ['Compare Side by Side', '并排比较', '並排比較', 'Banding Sebelah-menyebelah', '並べて比較', '나란히 비교'],
    'popular': ['Popular Comparisons', '热门比较', '熱門比較', 'Perbandingan Popular', '人気の比較', '인기 비교'],
    'vs': ['Project vs Project', '项目对决', '項目對決', 'Projek lawan Projek', '物件 vs 物件', '프로젝트 vs 프로젝트'],
    'journal': ['The Journal', '房产资讯', '房產資訊', 'Jurnal', 'ジャーナル', '저널'],
    'notes': ["Keith's Market Notes", 'Keith 每日市场短评', 'Keith 每日市場短評', 'Nota Pasaran Keith', 'Keith のマーケットノート', 'Keith의 마켓 노트'],
    'data': ['Market Data', '市场数据', '市場數據', 'Data Pasaran', 'マーケットデータ', '마켓 데이터'],
    'guide': ['Buying Guide', '买房指南', '買房指南', 'Panduan Membeli', '購入ガイド', '구매 가이드'],
    'foreign': ['Foreign Buyers', '外国买家', '外國買家', 'Pembeli Asing', '外国人購入者', '외국인 구매자'],
    'fcheck': ['Can I Buy? State Check', '我可以买吗？州属查询', '我可以買嗎？州屬查詢', 'Boleh Saya Beli? Semak Negeri', '購入できる？州別チェック', '구매 가능할까? 주별 확인'],
    'fproj': ['Projects for Foreign Buyers', '外国人必看项目', '外國人必看項目', 'Projek untuk Pembeli Asing', '外国人向け物件', '외국인 추천 프로젝트'],
    'fcost': ['Costs & Taxes', '费用和税务', '費用和稅務', 'Kos & Cukai', '費用と税金', '비용 및 세금'],
    'fsteps': ['How Buying Works', '购买流程', '購買流程', 'Cara Membeli', '購入の流れ', '구매 절차'],
    'videos': ['Videos', '视频', '影片', 'Video', '動画', '동영상'],
    'kit': ['All Free Tools', '全部免费工具', '全部免費工具', 'Semua Alat Percuma', '無料ツール一覧', '모든 무료 도구'],
    'calc': ['Loan Calculator', '房贷计算器', '房貸計算器', 'Kalkulator Pinjaman', 'ローン計算機', '대출 계산기'],
    'quiz': ['Find My Home Quiz', '帮我找房问答', '幫我找房問答', 'Kuiz Cari Rumah', 'おうち探し診断', '내 집 찾기 퀴즈'],
    'mm2h': ['MM2H Guide', 'MM2H 第二家园', 'MM2H 第二家園', 'Panduan MM2H', 'MM2H ガイド', 'MM2H 가이드'],
    'lib': ['MM2H Library', 'MM2H 文章库', 'MM2H 文章庫', 'Perpustakaan MM2H', 'MM2H ライブラリー', 'MM2H 라이브러리'],
    'areas': ['Area Guides', '地区指南', '地區指南', 'Panduan Kawasan', 'エリアガイド', '지역 가이드'],
    'about': ['Meet Keith', '认识 Keith', '認識 Keith', 'Kenali Keith', 'Keith について', 'Keith 소개'],
    'enq': ['Quick Enquiry', '快速咨询', '快速諮詢', 'Pertanyaan Pantas', 'かんたんお問い合わせ', '빠른 문의'],
    'mm2henq': ['MM2H Enquiry', 'MM2H 咨询', 'MM2H 諮詢', 'Pertanyaan MM2H', 'MM2H のお問い合わせ', 'MM2H 문의'],
    'h2h': ['Compare All Projects', '比较全部项目', '比較全部項目', 'Bandingkan Semua Projek', '全物件を比較', '전체 프로젝트 비교'],
    'faq': ['Common FAQ', '常见问题', '常見問題', 'Soalan Lazim', 'よくある質問', '자주 묻는 질문'],
    'blogs': ['Blogs', '文章', '文章', 'Blog', 'ブログ', '블로그'],
    'fareas': ['Free Area Guide Download', '免费地区指南下载', '免費地區指南下載', 'Muat Turun Panduan Kawasan Percuma', '無料エリアガイドをダウンロード', '무료 지역 가이드 다운로드'],
    'fmm2h': ['Free MM2H Guide', '免费 MM2H 指南', '免費 MM2H 指南', 'Panduan MM2H Percuma', '無料 MM2H ガイド', '무료 MM2H 가이드'],
    'fwatch': ['Free to Watch', '免费观看视频', '免費觀看影片', 'Tonton Percuma', '無料で動画を見る', '무료 영상 보기'],
    'fcalc': ['Free Calculator', '免费计算器', '免費計算器', 'Kalkulator Percuma', '無料計算ツール', '무료 계산기'],
    'fadvice': ['Free One-to-One Advice', '免费一对一咨询', '免費一對一諮詢', 'Nasihat Percuma Satu-ke-Satu', '無料の個別相談', '무료 1:1 상담'],
    'contact': ['Contact Keith', '联系 Keith', '聯絡 Keith', 'Hubungi Keith', 'Keith に連絡', 'Keith에게 연락'],
 'wa': ['WhatsApp Keith', 'WhatsApp Keith', 'WhatsApp Keith', 'WhatsApp Keith', 'WhatsApp で相談', 'WhatsApp 문의'],
}
MENU = {
    'projects.html': [('browse', 'projects.html#projSearch'), ('map', 'projects.html#projectMap'), ('all', 'projects.html#projGrid'), ('state', 'projects.html#projGrid'),
                      ('best', 'best/index.html'), ('dev', 'developer/index.html'), ('station', 'station/index.html'), ('tag', 'projects.html#tagSection')],
    'compare.html': [('h2h', 'compare.html#cmpFilters'), ('vs', 'vs/index.html'), ('popular', 'compare.html#popular')],
    'foreign-buyers.html': [('fcheck', 'foreign-buyers.html#check'), ('fproj', 'foreign-buyers.html#projects'), ('fcost', 'foreign-buyers.html#costs'),
                            ('fsteps', 'foreign-buyers.html#steps'), ('mm2h', 'mm2h.html'), ('faq', 'foreign-buyers.html#faq')],
    'blog.html': [('notes', 'market-notes.html'), ('guide', 'blog.html#buying-guide'), ('data', 'market-data.html'), ('faq', 'blog.html#faq'), ('blogs', 'blog.html#blog')],
    'resources.html': [('fareas', 'resources.html#guides'), ('fmm2h', 'mm2h.html'), ('fwatch', 'https://www.youtube.com/@KeithNahRealEstate/videos'), ('fcalc', 'calculator.html'), ('fadvice', WA)],
    'about-keith.html': [('contact', 'about-keith.html#quickEnquiry')],
}


# ---- "Search by State" flyout: states on the left, areas (KL by zone) on the right ----
import sys, urllib.parse, collections
sys.path.insert(0, HERE)
from build_proj_layout import ZONES, T as ZT
_pm = re.search(r'window\.KN_PLACES = (\[.*?\]);', open('projects.html', encoding='utf-8').read(), re.S)
PLACES = json.loads(_pm.group(1)) if _pm else []
ST_ORDER = ["Kuala Lumpur", "Selangor", "Penang", "Johor", "Melaka", "Sabah", "Terengganu", "Kelantan"]
ST = {  # [en, zh-CN, zh-TW, ms, ja, ko]
    'Kuala Lumpur': ['Kuala Lumpur', '吉隆坡', '吉隆坡', 'Kuala Lumpur', 'クアラルンプール', '쿠알라룸푸르'],
    'Selangor': ['Selangor', '雪兰莪', '雪蘭莪', 'Selangor', 'セランゴール', '슬랑오르'],
    'Penang': ['Penang', '槟城', '檳城', 'Pulau Pinang', 'ペナン', '페낭'],
    'Johor': ['Johor', '柔佛', '柔佛', 'Johor', 'ジョホール', '조호르'],
    'Melaka': ['Melaka', '马六甲', '馬六甲', 'Melaka', 'マラッカ', '믈라카'],
    'Sabah': ['Sabah', '沙巴', '沙巴', 'Sabah', 'サバ', '사바'],
    'Terengganu': ['Terengganu', '登嘉楼', '登嘉樓', 'Terengganu', 'トレンガヌ', '트렝가누'],
    'Kelantan': ['Kelantan', '吉兰丹', '吉蘭丹', 'Kelantan', 'クランタン', '클란탄'],
}
ALLOF = ['All {s}', '全部{s}', '全部{s}', 'Semua {s}', '{s}のすべて', '{s} 전체']
ZL = {z: [ZT[l][z] for l in ['en', 'zh-CN', 'zh-TW', 'ms', 'ja', 'ko']] for z in {q[0] for v in ZONES.values() for q in v} | {'other'}}


def _esc(x):
    return x.replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')


def _slug(x):
    return re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', x.lower().replace('&', 'and')))


def area_href(prefix, st, a):
    """An area with its own landing page links there; otherwise to the filtered project list."""
    if os.path.exists(os.path.join(ROOT, 'area', _slug(a) + '.html')):
        return prefix + 'area/' + _slug(a) + '.html'
    return prefix + 'projects.html#' + urllib.parse.quote(st + '/' + a)


def flyout(prefix):
    cnt = collections.Counter(s for s, a in PLACES)
    acnt = collections.Counter((s, a) for s, a in PLACES)
    states = [x for x in ST_ORDER if cnt[x]] + sorted(x for x in cnt if x not in ST_ORDER)
    h = lambda q: prefix + 'projects.html#' + urllib.parse.quote(q)
    left, right = '', ''
    for i, st in enumerate(states):
        on = ' on' if i == 0 else ''
        name = ST.get(st, [st] * 6)[0]
        left += '<a class="knm-fs%s" data-fs="%d" href="%s"><span data-kst="%s">%s</span><em>%d</em></a>' % (on, i, h(st), _esc(st), _esc(name), cnt[st])
        areas = sorted({a for s, a in PLACES if s == st}, key=lambda a: (-acnt[(st, a)], a))
        if st in ZONES:
            zof = {a: z for z, lst in ZONES[st] for a in lst}
            groups = [(z, [a for a in areas if zof.get(a, 'other') == z]) for z in [q[0] for q in ZONES[st]] + ['other']]
            groups = [g for g in groups if g[1]]
            if len(groups) == 1 and groups[0][0] == 'other':
                groups = [(None, areas)]
        else:
            groups = [(None, areas)]
        cols = ''
        for z, lst in groups:
            head = ('<a class="knm-fz" href="%s" data-kz="%s">%s</a>' % (h(st + '/zone:' + z), z, _esc(ZL[z][0]))) if z else ''
            cols += '<div class="knm-col%s">%s%s</div>' % ('' if z else ' knm-one', head, ''.join(
                '<a class="knm-fa" href="%s">%s<em>%d</em></a>' % (area_href(prefix, st, a), _esc(a), acnt[(st, a)]) for a in lst))
        right += ('<div class="knm-fp%s" data-fp="%d"><a class="knm-fall" href="%s"><span data-kall="%s">%s</span> (%d) →</a><div class="knm-cols">%s</div></div>'
                  % (on, i, h(st), _esc(st), ALLOF[0].replace('{s}', _esc(ST.get(st, [st])[0])), cnt[st], cols))
    return '<div class="knm-fly"><div class="knm-fl">%s</div><div class="knm-fr">%s</div></div>' % (left, right)

CSS = ('<style id="kn-submenu-css">'
       'html{scroll-padding-top:96px}'  # menu links to #sections: keep the section title below the fixed header
       '.knm-g{position:relative;display:inline-flex;align-items:center}.knm-c{display:inline-block;width:6px;height:6px;margin:0 0 3px 7px;pointer-events:none;'
       'border-right:1.6px solid currentColor;border-bottom:1.6px solid currentColor;transform:rotate(45deg);opacity:.75;transition:transform .2s}'
       'header .knm-g>a{margin-right:0!important}.knm-g:hover .knm-c,.knm-g:focus-within .knm-c{transform:translateY(3px) rotate(225deg)}#knMnav .knm-c{display:none}'
       '.knm-d{position:absolute;top:100%;left:50%;transform:translate(-50%,8px);min-width:230px;padding:10px;background:#fff;border-radius:16px;'
       'box-shadow:0 18px 40px rgba(20,18,60,.18);border:1px solid rgba(21,20,43,.08);opacity:0;visibility:hidden;transition:opacity .18s,transform .18s,visibility .18s;z-index:1000}'
       '.knm-d:before{content:"";position:absolute;left:0;right:0;top:-14px;height:14px}'
       '.knm-g:hover .knm-d,.knm-g:focus-within .knm-d{opacity:1;visibility:visible;transform:translate(-50%,4px)}'
       'header nav .knm-d a,.knm-d a{display:block!important;margin:0!important;padding:10px 14px!important;border-radius:10px;color:#15142b!important;font-size:14px!important;'
       'font-weight:600!important;letter-spacing:0!important;text-transform:none!important;white-space:nowrap;text-decoration:none!important;opacity:1!important}'
       '.knm-d a:after{display:none!important}.knm-d a:hover{background:#f1efff;color:#5E60CE!important}'
       '#knMnav .knm-g{display:block}#knMnav .knm-d{position:static;transform:none;opacity:1;visibility:visible;background:none;box-shadow:none;border:0;padding:0 0 6px;min-width:0}'
       '#knMnav .knm-d a{color:rgba(255,255,255,.78)!important;font-size:14.5px!important;font-weight:500!important;padding:9px 4px 9px 18px!important;border-bottom:0!important;border-radius:0}'
       '#knMnav .knm-d a:hover{background:none;color:#fff!important}nav.nw-jump{display:flex!important}.kn-links a.knm-ms{padding-left:22px!important;font-size:14.5px!important;opacity:.8;border-bottom:0!important}'
       '#knDrawer .kn-links a:not(.knm-ms){color:#b9b4ff!important;font-weight:600}#knDrawer .kn-links a.knm-ms{color:#fff!important}'
       '#knMnav .kn-mlinks>a,#knMnav .kn-mlinks>.knm-g>a{color:#b9b4ff!important;font-weight:600}#knMnav .knm-d a{color:#fff!important}'
       '.knm-st{display:flex;align-items:center}.knm-st>a{flex:1}.knm-ar{width:7px;height:7px;margin:0 12px 0 4px;border-right:1.6px solid #15142b;border-top:1.6px solid #15142b;transform:rotate(45deg);flex:0 0 auto;pointer-events:none}'
       '.knm-st:hover>a{background:#f1efff;color:#5E60CE!important}'
       '.knm-fly{position:absolute;left:calc(100% + 8px);top:0;width:720px;display:flex;background:#fff;border-radius:16px;box-shadow:0 18px 40px rgba(20,18,60,.18);'
       'border:1px solid rgba(21,20,43,.08);opacity:0;visibility:hidden;transition:opacity .15s,visibility .15s;text-align:left}'
       '.knm-fly:before{content:"";position:absolute;left:-14px;top:0;bottom:0;width:14px}'
       '.knm-st:hover .knm-fly,.knm-st:focus-within .knm-fly{opacity:1;visibility:visible}'
       '.knm-fl{width:200px;flex:0 0 200px;padding:10px;border-right:1px solid #eeecf6}'
       'header nav .knm-d a.knm-fs{display:flex!important;justify-content:space-between;align-items:center;gap:8px}'
       '.knm-d a em{font-style:normal;font-size:11.5px;color:#8b8aa0;font-weight:600}a.knm-fs.on{background:#f1efff;color:#5E60CE!important}'
       '.knm-fr{flex:1;padding:14px 16px 16px;max-height:min(560px,72vh);overflow:auto}.knm-fp{display:none}.knm-fp.on{display:block}'
       'header nav .knm-d a.knm-fall{display:inline-block!important;color:#5E60CE!important;font-size:13px!important;padding:6px 10px!important;margin-bottom:6px!important}'
       '.knm-cols{display:block}.knm-col{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:2px 14px;padding-bottom:8px;margin-bottom:6px;border-bottom:1px solid #f0eef8}.knm-col:last-child{border-bottom:0;margin-bottom:0}.knm-col .knm-fz{grid-column:1/-1}'
       'header nav .knm-d a.knm-fz{font-size:11px!important;font-weight:700!important;letter-spacing:.12em!important;text-transform:uppercase!important;color:#a0782c!important;padding:10px 10px 6px!important;white-space:normal!important;line-height:1.4}'
       'header nav .knm-d a.knm-fa{display:flex!important;justify-content:space-between;gap:8px;font-weight:650!important;color:#15142b!important;white-space:normal;font-size:14.5px!important}'
       '#knMnav .knm-fly,#knMnav .knm-ar{display:none!important}'
       '@media(max-width:1349px){.knm-fly{display:none!important}}'
       # light lavender menus, selected item in solid site purple
       'header .knm-d,header .knm-fly{background:linear-gradient(160deg,#F7F6FF 0%,#ECEBFB 100%)!important;border-color:#DEDCF7!important}'
       'header .knm-fl{background:rgba(94,96,206,.08)!important;border-right-color:#DEDCF7!important;border-radius:16px 0 0 16px}'
       'header .knm-d a:hover,header .knm-st:hover>a,header a.knm-fs.on{background:#5E60CE!important;color:#fff!important}'
       'header a.knm-fs.on em,header .knm-d a:hover em{color:rgba(255,255,255,.8)!important}header .knm-col{border-bottom-color:#DEDCF7!important}'
       '</style>')

JS = ('<script id="kn-submenu-js">(function(){var ST=__ST__,ZL=__ZL__,AO=__AO__,T=%s,LG=["en","zh-CN","zh-TW","ms","ja","ko"];function f(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}'
      'var i=Math.max(0,LG.indexOf(l));document.querySelectorAll("[data-km]").forEach(function(a){var v=T[a.getAttribute("data-km")];if(v)a.textContent=v[i];});'
      'document.querySelectorAll("[data-kst]").forEach(function(a){var v=ST[a.getAttribute("data-kst")];if(v)a.textContent=v[i];});'
      'document.querySelectorAll("[data-kz]").forEach(function(a){var v=ZL[a.getAttribute("data-kz")];if(v)a.textContent=v[i];});'
      'document.querySelectorAll("[data-kall]").forEach(function(a){var v=ST[a.getAttribute("data-kall")];a.textContent=AO[i].replace("{s}",v?v[i]:a.getAttribute("data-kall"));});}f();'
      'document.addEventListener("mouseover",function(e){var s=e.target.closest&&e.target.closest(".knm-fs");if(!s)return;var fly=s.closest(".knm-fly"),k=s.getAttribute("data-fs");'
      'fly.querySelectorAll(".knm-fs").forEach(function(x){x.classList.toggle("on",x===s);});fly.querySelectorAll(".knm-fp").forEach(function(x){x.classList.toggle("on",x.getAttribute("data-fp")===k);});});'
      'document.addEventListener("DOMContentLoaded",function(){["knSetLang","setLanguage"].forEach(function(n){var s=window[n];if(typeof s==="function")window[n]=function(){var r=s.apply(this,arguments);f();return r;};});f();});})();</script>'
      ) % json.dumps({k: v for k, v in L.items()}, ensure_ascii=False)
JS = JS.replace('__ST__', json.dumps(ST, ensure_ascii=False)).replace('__ZL__', json.dumps(ZL, ensure_ascii=False)).replace('__AO__', json.dumps(ALLOF, ensure_ascii=False))


def sub(prefix, items):
    out = ''
    for k, href in items:
        full = href if href.startswith('http') else prefix + href
        ext = ' target="_blank" rel="noopener"' if href.startswith('http') else ''
        link = '<a class="knm-s" href="%s"%s data-km="%s">%s</a>' % (full.replace('&', '&amp;'), ext, k, L[k][0])
        out += ('<div class="knm-st">%s<i class="knm-ar" aria-hidden="true"></i>%s</div>' % (link, flyout(prefix))) if k == 'state' else link
    return '<div class="knm-d">%s</div>' % out


def fix(t, prefix):
    h0 = t.find('<header')
    if h0 < 0:
        return t
    h1 = t.find('</header>', h0)
    head = t[h0:h1]
    m = re.search(r'<nav>(.*?)</nav>', head, re.S)
    if not m:
        return t
    nav = m.group(1)
    nav = re.sub(r'<div class="knm-g">(<a\b.*?</a>)(?:<span class="knm-c"[^>]*></span>)?<div class="knm-d">.*?</div><!--/knm-g--></div>', r'\1', nav, flags=re.S)  # undo an earlier run
    nav = re.sub(r'<div class="knm-g">(<a\b.*?</a>)(?:<span class="knm-c"[^>]*></span>)?<div class="knm-d">(?:(?!<div).)*?</div></div>', r'\1', nav, flags=re.S)  # older runs (no nested divs)
    nav = re.sub(r'\s*<a\b[^>]*href="(?:\.\./)*calculator\.html"[^>]*>.*?</a>', '', nav, flags=re.S)  # Calculator moves to Free Toolkit
    # Foreign Buyers: a main menu item just before News
    nav = re.sub(r'\s*<a\b[^>]*href="(?:\.\./|/)*foreign-buyers\.html"[^>]*>.*?</a>', '', nav, flags=re.S)
    fb = '<a href="%sforeign-buyers.html" data-km="foreign"%s>Foreign Buyers</a>' % (prefix, ' class="active"' if 'foreign-buyers.html' in t[:t.find('<header')] and 'rel="canonical" href="https://keithnah.com/foreign-buyers.html"' in t else '')
    nav = re.sub(r'(\s*)(<a\b[^>]*href="(?:\.\./|/)*blog\.html")', lambda m: m.group(1) + fb + m.group(1) + m.group(2), nav, count=1)

    def group(a):
        href = re.search(r'href="([^"]*)"', a.group(0)).group(1)
        key = href.split('/')[-1].split('#')[0]
        if key not in MENU:
            return a.group(0)
        return '<div class="knm-g">%s<span class="knm-c" aria-hidden="true"></span>%s<!--/knm-g--></div>' % (a.group(0), sub(prefix, MENU[key]))
    nav = re.sub(r'<a\b[^>]*>.*?</a>', group, nav, flags=re.S)
    head = head[:m.start(1)] + nav + head[m.end(1):]
    t = t[:h0] + head + t[h1:]
    t = re.sub(r'<style id="kn-submenu-css">.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<script id="kn-submenu-js">.*?</script>', '', t, flags=re.S)
    t = t.replace('</head>', CSS + '</head>', 1).replace('</body>', JS + '</body>', 1)
    # the phone menu on the main pages copies every menu link: show the sub-pages indented
    t = re.sub(r"(?: if\(a\.classList\.contains\('knm-s'\)\) c\.className='knm-ms';)+", "", t)
    t = t.replace("var c=document.createElement('a'); c.href=h; c.textContent=a.textContent;",
                  "var c=document.createElement('a'); c.href=h; c.textContent=a.textContent; if(a.classList.contains('knm-s')) c.className='knm-ms';")
    t = t.replace("document.querySelectorAll('header nav a').forEach(function(a){\n", "document.querySelectorAll('header nav a').forEach(function(a){ if(a.closest('.knm-fly'))return;\n")
    t = t.replace("forEach(function(a){ if(a.closest('.knm-fly'))return; if(a.closest('.knm-fly'))return;", "forEach(function(a){ if(a.closest('.knm-fly'))return;")
    t = t.replace("if(h==='resources.html'){ var m2=document.createElement('a');", "if(false){ var m2=document.createElement('a');")
    return t


n = 0
for d in DIRS:
    for f in sorted(glob.glob(os.path.join(d, '*.html') if d else '*.html')):
        t = open(f, encoding='utf-8').read()
        t2 = fix(t, '/' if f == '404.html' else ('../' if d else ''))
        if t2 != t:
            open(f, 'w', encoding='utf-8').write(t2)
            n += 1
print('menu: sub-menus on %d page(s)' % n)
