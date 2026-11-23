"""Extra modules for the News hub (blog.html): This week, New on the site, Key dates, By area, Tools.
Used by build_news_split.py. Text in six languages is switched in the browser (data-nhx keys)."""
import glob, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import note_links  # noqa: E402

LANGS = ['en', 'zh-CN', 'zh-TW', 'ms', 'ja', 'ko']
E = lambda s: html.escape(str(s), quote=True)
TX = {}   # key -> {lang: text}


def L(en, zh, tw, ms, ja, ko):
    return dict(zip(LANGS, [en, zh, tw, ms, ja, ko]))


def span(key, d):
    TX[key] = d
    return '<span data-nhx="%s">%s</span>' % (key, E(d['en']))


UI = {
    'wk_e': L('This week', '本周重点', '本週重點', 'Minggu ini', '今週のポイント', '이번 주'),
    'wk_h': L('What moved the market', '本周市场动态', '本週市場動態', 'Apa yang menggerakkan pasaran', '今週の市場の動き', '이번 주 시장 움직임'),
    'wk_r': L("Read Keith's take →", '看 Keith 的分析 →', '看 Keith 的分析 →', 'Baca pandangan Keith →', 'Keith の解説を読む →', 'Keith의 분석 보기 →'),
    'wk_all': L('All market notes →', '全部市场短评 →', '全部市場短評 →', 'Semua nota pasaran →', 'マーケットノート一覧 →', '마켓 노트 전체 보기 →'),
    'np_e': L('New on the site', '新盘动态', '新盤動態', 'Baharu di laman', '新着プロジェクト', '새로 추가된 프로젝트'),
    'np_h': L('Latest projects added', '最新加入的项目', '最新加入的項目', 'Projek terbaru ditambah', '最近追加したプロジェクト', '최근 추가된 프로젝트'),
    'np_all': L('See all projects →', '查看全部项目 →', '查看全部項目 →', 'Lihat semua projek →', 'すべてのプロジェクト →', '전체 프로젝트 보기 →'),
    'por': L('Price on Request', '价格请询问', '價格請洽詢', 'Harga atas permintaan', '価格はお問い合わせ', '가격 문의'),
    'kd_e': L('Key dates', '重要日期', '重要日期', 'Tarikh penting', '重要な日程', '주요 일정'),
    'kd_h': L('Coming up for buyers', '买家要留意的日子', '買家要留意的日子', 'Akan datang untuk pembeli', '購入者が注目する予定', '구매자가 주목할 일정'),
    'kd_n': L('Target dates can move; Keith updates this list when they do.', '目标日期可能更改，Keith 会随时更新。', '目標日期可能更改，Keith 會隨時更新。',
              'Tarikh sasaran boleh berubah; Keith akan mengemas kini senarai ini.', '目標日は変わることがあります。変更があれば Keith が更新します。', '목표 날짜는 바뀔 수 있으며, 바뀌면 Keith가 업데이트합니다.'),
    'ar_e': L('By area', '按地区看新闻', '按地區看新聞', 'Mengikut kawasan', 'エリア別', '지역별'),
    'ar_h': L('News where you are looking', '你关注地区的新闻', '你關注地區的新聞', 'Berita di kawasan pilihan anda', '気になるエリアのニュース', '관심 지역 뉴스'),
    'ar_g': L('area guide and projects →', '地区指南和项目 →', '地區指南和項目 →', 'panduan kawasan dan projek →', 'エリアガイドとプロジェクト →', '지역 가이드와 프로젝트 →'),
    'tl_e': L('Tools', '工具区', '工具區', 'Alat', 'ツール', '도구'),
    'tl_h': L('Work out your numbers', '算一算你的数字', '算一算你的數字', 'Kira angka anda', '数字を確認する', '숫자 계산해 보기'),
    'open': L('Open →', '打开 →', '打開 →', 'Buka →', '開く →', '열기 →'),
}
DATES = [
    (L('12 Dec 2026', '2026年12月12日', '2026年12月12日', '12 Dis 2026', '2026年12月12日', '2026년 12월 12일'), 'Malaysia',
     L('ECRL passenger services begin (target)', 'ECRL 东海岸铁路客运开通（目标）', 'ECRL 東海岸鐵路客運開通（目標）', 'Perkhidmatan penumpang ECRL bermula (sasaran)', 'ECRL 旅客運行開始（目標）', 'ECRL 여객 운행 시작 (목표)'),
     L('East Coast Rail Link to Gombak; subject to final approvals.', '东海岸铁路连接鹅唛，仍需最终批准。', '東海岸鐵路連接鵝嘜，仍需最終批准。', 'Laluan Rel Pantai Timur ke Gombak; tertakluk kepada kelulusan akhir.',
       '東海岸鉄道でゴンバックへ。最終承認が条件です。', '동해안 철도, 곰박까지. 최종 승인이 필요합니다.')),
    (L('21 Jan 2027', '2027年1月21日', '2027年1月21日', '21 Jan 2027', '2027年1月21日', '2027년 1월 21일'), 'Malaysia',
     L('Bank Negara: first OPR meeting of 2027', '国行 2027 年首次议息会议', '國行 2027 年首次議息會議', 'Bank Negara: mesyuarat OPR pertama 2027', 'マレーシア中銀：2027年最初の OPR 会合', '중앙은행: 2027년 첫 OPR 회의'),
     L('The OPR has been 2.75% since July 2025.', '隔夜政策利率自 2025 年 7 月起为 2.75%。', '隔夜政策利率自 2025 年 7 月起為 2.75%。', 'OPR kekal 2.75% sejak Julai 2025.', 'OPR は 2025 年 7 月から 2.75% です。', 'OPR은 2025년 7월부터 2.75%입니다.')),
    (L('Feb 2027', '2027年2月', '2027年2月', 'Feb 2027', '2027年2月', '2027년 2월'), 'Johor',
     L('RTS Link Johor Bahru–Singapore opens (target)', '新山—新加坡 RTS 通车（目标）', '新山—新加坡 RTS 通車（目標）', 'RTS Link Johor Bahru–Singapura dibuka (sasaran)', 'ジョホールバル–シンガポール RTS 開業（目標）', '조호르바루–싱가포르 RTS 개통 (목표)'),
     L('Bukit Chagar to Woodlands North.', 'Bukit Chagar 至 Woodlands North。', 'Bukit Chagar 至 Woodlands North。', 'Bukit Chagar ke Woodlands North.', 'Bukit Chagar から Woodlands North まで。', 'Bukit Chagar에서 Woodlands North까지.')),
]
AREA_TX = {'Malaysia': L('Malaysia', '马来西亚', '馬來西亞', 'Malaysia', 'マレーシア', '말레이시아'), 'Johor': L('Johor', '柔佛', '柔佛', 'Johor', 'ジョホール', '조호르')}
AREAS = [('Kuala Lumpur', 'area/kuala-lumpur.html'), ('Selangor', 'area/selangor.html'), ('Penang', 'area/penang.html'), ('Johor', 'area/johor.html')]
TOOLS = [('calculator.html', 'M4 3h16v18H4zM8 7h8M8 11h2M12 11h2M8 15h2M12 15h2M8 19h8',
          L('Loan & cost calculator', '贷款与费用计算器', '貸款與費用計算器', 'Kalkulator pinjaman & kos', 'ローンと費用の計算', '대출·비용 계산기'),
          L('Monthly instalment, stamp duty and legal fees for any price.', '任何价格的每月供款、印花税和律师费。', '任何價格的每月供款、印花稅和律師費。', 'Ansuran bulanan, duti setem dan yuran guaman untuk sebarang harga.',
            'どの価格でも月々の返済額、印紙税、弁護士費用がわかります。', '어떤 가격이든 월 상환액, 인지세, 변호사 비용을 계산합니다.')),
         ('foreign-buyers.html#check', 'M12 3a9 9 0 100 18 9 9 0 000-18zM3 12h18M12 3c3 3 3 15 0 18',
          L('Foreign buyer minimum price', '外国人最低购买价', '外國人最低購買價', 'Harga minimum pembeli asing', '外国人の最低購入価格', '외국인 최저 구매 가격'),
          L('Check the minimum price for foreigners in each state.', '查看各州外国人的最低购买价格。', '查看各州外國人的最低購買價格。', 'Semak harga minimum untuk warga asing di setiap negeri.',
            '州ごとの外国人の最低購入価格を確認できます。', '주별 외국인 최저 구매 가격을 확인하세요.')),
         ('find-my-home.html', 'M11 4a7 7 0 100 14 7 7 0 000-14zM21 21l-4.3-4.3',
          L('Find my home', '帮我找房', '幫我找房', 'Cari rumah saya', '住まい探し', '내 집 찾기'),
          L('Answer a few questions and get a shortlist of projects.', '回答几个问题，得到适合你的项目清单。', '回答幾個問題，得到適合你的項目清單。', 'Jawab beberapa soalan dan dapatkan senarai pendek projek.',
            'いくつかの質問に答えると、候補のプロジェクトが見つかります。', '몇 가지 질문에 답하면 추천 프로젝트 목록을 받을 수 있습니다.'))]
CUT = {'en': 240, 'ms': 240, 'ko': 140, 'ja': 110, 'zh-CN': 100, 'zh-TW': 100}


def lead_text(body, lang):
    s = (body.get(lang) or body.get('en', '')) if isinstance(body, dict) else body
    s = re.sub(r'\s+', ' ', s.split('\n\n')[0]).strip()
    n = CUT.get(lang, 240)
    return s if len(s) <= n else s[:n].rstrip(' ,.;，。') + '…'


def tx_dict(d):
    return {l: (d.get(l) or d.get('en', '')) for l in LANGS} if isinstance(d, dict) else {l: d for l in LANGS}


def photo(slug):
    try:
        s = open(os.path.join(ROOT, 'property', slug + '.html'), encoding='utf-8').read()
        m = re.search(r'og:image" content="https://keithnah\.com/([^"]+)"', s)
        return m.group(1) if m else ''
    except OSError:
        return ''


def price_tx(p):
    p = (p or '').strip()
    m = re.match(r'From (RM[\d,.]+(?:\s*(?:mil|million|k))?)$', p)
    if m:
        v = m.group(1)
        return L(p, v + ' 起', v + ' 起', 'Dari ' + v, v + '〜', v + '부터')
    if not p or 'request' in p.lower():
        return UI['por']
    return {l: p for l in LANGS}


def new_projects(n=4):
    idx = {p['name']: p['slug'] for p in json.load(open(os.path.join(HERE, 'project_index.json'), encoding='utf-8'))}
    files = sorted([f for f in glob.glob(os.path.join(HERE, 'new_projects', '*.json')) if not f.endswith('places.json')],
                   key=lambda f: int((re.search(r'batch-(\d+)', f) or re.search(r'()', f)).group(1) or 0), reverse=True)
    out = []
    for f in files:
        try:
            d = json.load(open(f, encoding='utf-8'))
        except ValueError:
            continue
        for p in (d if isinstance(d, list) else d.get('projects', [])):
            if p.get('name') in idx and p['name'] not in [x['name'] for x in out] and os.path.exists(os.path.join(ROOT, 'property', idx[p['name']] + '.html')):
                out.append(dict(p, slug=idx[p['name']]))
        if len(out) >= n:
            break
    return out[:n]


def build():
    TX.clear()
    ns = note_links.notes()
    u = lambda k: span(k, UI[k])
    # 1 This week
    week = ''
    if ns:
        n0 = ns[0]
        lead = ('<a class="nh-lead" href="%s"><small>%s · %s</small><b>%s</b><p>%s</p><em>%s</em></a>' % (
            n0['_page'], span('w0a', tx_dict(n0['area'])), E(n0['date']), span('w0t', tx_dict(n0['title'])),
            span('w0p', {l: lead_text(n0['body'], l) for l in LANGS}), u('wk_r')))
        heads = ''.join('<a href="%s"><small>%s · %s</small><b>%s</b></a>' % (
            n['_page'], span('w%da' % k, tx_dict(n['area'])), E(n['date']), span('w%dt' % k, tx_dict(n['title']))) for k, n in enumerate(ns[1:4], 1))
        week = ('<section class="nh-sec" id="this-week"><div class="nh-w"><span class="nh-eb">%s</span><h2 class="nh-h2">%s</h2>'
                '<div class="nh-week">%s<div class="nh-heads">%s</div></div><div class="nh-more"><a href="market-notes.html">%s</a></div></div></section>') % (
            u('wk_e'), u('wk_h'), lead, heads, u('wk_all'))
    # 3 New on the site
    cards = ''
    for k, p in enumerate(new_projects()):
        cards += '<a href="property/%s.html"><img src="%s" alt="%s" loading="lazy" width="400" height="300"><span><small>%s</small><b>%s</b><em>%s</em></span></a>' % (
            p['slug'], E(photo(p['slug'])), E(p['name']), E(p.get('loc') or p.get('area', '')), E(p['name']), span('np%d' % k, price_tx(p.get('price_short') or p.get('price'))))
    launch = ('<section class="nh-sec" id="new-projects"><div class="nh-w"><span class="nh-eb">%s</span><h2 class="nh-h2">%s</h2><div class="nh-proj">%s</div>'
              '<div class="nh-more"><a href="projects.html">%s</a></div></div></section>') % (u('np_e'), u('np_h'), cards, u('np_all')) if cards else ''
    # 4 Key dates
    rows = ''.join('<div><b>%s</b><span><i>%s</i>%s<small>%s</small></span></div>' % (
        span('kd%dd' % k, d), span('kd%da' % k, AREA_TX[a]), span('kd%dh' % k, h), span('kd%ds' % k, s)) for k, (d, a, h, s) in enumerate(DATES))
    dates = ('<section class="nh-sec" id="key-dates"><div class="nh-w"><span class="nh-eb">%s</span><h2 class="nh-h2">%s</h2><div class="nh-dates">%s</div>'
             '<p class="nh-note">%s</p></div></section>') % (u('kd_e'), u('kd_h'), rows, u('kd_n'))
    # 5 By area
    tabs = panes = ''
    for k, (a, href) in enumerate(AREAS):
        mine = [n for n in ns if (n['area'].get('en') if isinstance(n['area'], dict) else n['area']) == a][:4]
        tabs += '<button type="button" role="tab" aria-selected="%s" class="%s" data-a="%d">%s</button>' % ('true' if k == 0 else 'false', 'on' if k == 0 else '', k, E(a))
        lst = ''.join('<a href="%s"><small>%s</small><b>%s</b></a>' % (n['_page'], E(n['date']), span('a%d_%d' % (k, j), tx_dict(n['title']))) for j, n in enumerate(mine))
        panes += '<div class="nh-pane" data-p="%d"%s><div class="nh-list">%s</div><a class="nh-guide" href="%s">%s %s</a></div>' % (
            k, '' if k == 0 else ' hidden', lst, href, E(a), u('ar_g'))
    area = ('<section class="nh-sec" id="by-area"><div class="nh-w"><span class="nh-eb">%s</span><h2 class="nh-h2">%s</h2><div class="nh-tabs" role="tablist">%s</div>%s</div></section>') % (
        u('ar_e'), u('ar_h'), tabs, panes)
    # 7 Tools
    tools = ('<section class="nh-sec" id="tools"><div class="nh-w"><span class="nh-eb">%s</span><h2 class="nh-h2">%s</h2><div class="nh-tools">%s</div></div></section>') % (
        u('tl_e'), u('tl_h'), ''.join(
            '<a href="%s"><span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="%s"/></svg></span>'
            '<b>%s</b><small>%s</small><em>%s</em></a>' % (h, ic, span('t%dn' % k, n), span('t%dd' % k, d), u('open')) for k, (h, ic, n, d) in enumerate(TOOLS)))
    script = ('<script>(function(){var T=%s;function lg(){var l="en";try{l=document.documentElement.getAttribute("data-page-lang")||localStorage.getItem("kn_lang")||"en"}catch(e){}return l;}'
              'function go(){var l=lg();document.querySelectorAll("[data-nhx]").forEach(function(e){var d=T[e.getAttribute("data-nhx")];if(d&&(d[l]||d.en))e.textContent=d[l]||d.en;});}'
              'go();document.addEventListener("DOMContentLoaded",go);var w=window.knSetLang;if(typeof w==="function"){window.knSetLang=function(){var r=w.apply(this,arguments);go();return r;};}'
              'document.querySelectorAll(".nh-tabs button").forEach(function(b){b.onclick=function(){document.querySelectorAll(".nh-tabs button").forEach(function(x){var on=x===b;x.classList.toggle("on",on);x.setAttribute("aria-selected",on)});'
              'document.querySelectorAll(".nh-pane").forEach(function(p){p.hidden=p.getAttribute("data-p")!==b.getAttribute("data-a")});};});})();</script>') % json.dumps(TX, ensure_ascii=False, separators=(',', ':'))
    return CSS + week + dates + area, tools, script   # 'New on the site' (launch) removed at Keith's request


CSS = '''<style>
.nh-sec{padding:46px 0 10px}.nh-w{max-width:1240px;margin:0 auto;padding:0 5vw}.nh-eb{display:block;font:700 12px Inter,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:#5E60CE}
.nh-h2{font:700 clamp(26px,3.4vw,38px) 'Playfair Display',serif;margin:8px 0 18px;color:#15142b}
.nh-week{display:grid;grid-template-columns:1.4fr 1fr;gap:18px}.nh-lead{display:block;background:#1d1b4f;color:#fff;border-radius:22px;padding:30px 32px;box-shadow:0 18px 40px rgba(29,27,79,.18)}
.nh-lead small{color:#c9caff;font:700 12px Inter,sans-serif;letter-spacing:.08em;text-transform:uppercase}.nh-lead b{display:block;font:700 clamp(22px,2.6vw,30px) 'Playfair Display',serif;margin:10px 0 12px;line-height:1.25;color:#fff}
.nh-lead p{color:#dcdcf2;font-size:15.5px;line-height:1.7}.nh-lead em{display:inline-block;margin-top:16px;font-style:normal;font-weight:700;color:#fff;background:#5E60CE;padding:10px 18px;border-radius:100px}
.nh-heads{display:flex;flex-direction:column;gap:12px}.nh-heads a,.nh-list a{display:block;background:#fff;border:1px solid rgba(21,20,43,.1);border-radius:16px;padding:16px 18px;transition:border-color .2s,box-shadow .2s}
.nh-heads a:hover,.nh-list a:hover{border-color:#5E60CE;box-shadow:0 12px 26px rgba(29,27,79,.08)}.nh-heads small,.nh-list small{color:#5E60CE;font:700 12px Inter,sans-serif}.nh-heads b,.nh-list b{display:block;font:700 16.5px 'Playfair Display',serif;color:#15142b;margin-top:4px;line-height:1.35}
.nh-proj{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.nh-proj a{display:block;background:#fff;border:1px solid rgba(21,20,43,.1);border-radius:18px;overflow:hidden;transition:transform .2s,box-shadow .2s}
.nh-proj a:hover{transform:translateY(-3px);box-shadow:0 16px 32px rgba(29,27,79,.12)}.nh-proj img{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;background:#eee}.nh-proj span{display:block;padding:12px 14px 14px}
.nh-proj small{color:#55546b;font-size:12.5px}.nh-proj b{display:block;font:700 17px 'Playfair Display',serif;color:#15142b;margin:2px 0 4px}.nh-proj em{font-style:normal;color:#5E60CE;font-weight:700;font-size:13.5px}
.nh-more{text-align:center;margin-top:18px}.nh-more a{color:#5E60CE;font-weight:700}
.nh-dates{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.nh-dates>div{display:flex;gap:14px;background:#fff;border:1px solid rgba(21,20,43,.1);border-radius:18px;padding:18px}
.nh-dates b{flex:0 0 96px;background:#eeedfb;color:#3d3fb0;border-radius:14px;display:flex;align-items:center;justify-content:center;text-align:center;font:800 15px Inter,sans-serif;padding:10px;line-height:1.25}
.nh-dates span{font-weight:700;color:#15142b;font-size:15px;line-height:1.4}.nh-dates i{display:block;font-style:normal;color:#5E60CE;font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;margin-bottom:4px}.nh-dates small{display:block;color:#55546b;font-weight:500;font-size:13px;margin-top:4px}
.nh-note{color:#77768c;font-size:12.5px;margin-top:10px}
.nh-tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}.nh-tabs button{background:#fff;border:1px solid rgba(21,20,43,.14);border-radius:100px;padding:9px 18px;font:700 14px Inter,sans-serif;cursor:pointer;color:#15142b}.nh-tabs button.on{background:#1d1b4f;color:#fff;border-color:#1d1b4f}
.nh-list{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.nh-guide{display:inline-block;margin-top:14px;color:#5E60CE;font-weight:700}
.nh-tools{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:30px}.nh-tools a{display:flex;flex-direction:column;background:linear-gradient(135deg,#5E60CE,#7c7ee6);color:#fff;border-radius:20px;padding:22px;box-shadow:0 14px 30px rgba(94,96,206,.25);transition:transform .2s}
.nh-tools a:hover{transform:translateY(-3px)}.nh-tools .ic{width:46px;height:46px;border-radius:13px;background:rgba(255,255,255,.18);display:flex;align-items:center;justify-content:center}.nh-tools svg{width:24px;height:24px}
.nh-tools b{font:700 19px 'Playfair Display',serif;margin:14px 0 6px;color:#fff}.nh-tools small{color:#e6e6fb;font-size:14px;line-height:1.5}.nh-tools em{margin-top:14px;font-style:normal;font-weight:700}
@media(max-width:1000px){.nh-proj,.nh-list{grid-template-columns:1fr 1fr}.nh-dates,.nh-tools{grid-template-columns:1fr}.nh-week{grid-template-columns:1fr}}
@media(max-width:560px){.nh-list{grid-template-columns:1fr}.nh-proj{gap:10px}.nh-proj b{font-size:15px}.nh-proj span{padding:10px}.nh-lead{padding:22px}}
</style>'''
