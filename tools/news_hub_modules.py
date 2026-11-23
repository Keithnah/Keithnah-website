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
    'kd_h': L('Timeline for buyers', '买家时间表', '買家時間表', 'Garis masa untuk pembeli', '購入者のためのタイムライン', '구매자를 위한 타임라인'),
    'kd_today': L('Today', '今天', '今天', 'Hari ini', '今日', '오늘'),
    'kd_n': L('Target dates can move; Keith updates this timeline when they do.', '目标日期可能更改，Keith 会随时更新这个时间表。', '目標日期可能更改，Keith 會隨時更新這個時間表。',
              'Tarikh sasaran boleh berubah; Keith akan mengemas kini senarai ini.', '目標日は変わることがあります。変更があれば Keith が更新します。', '목표 날짜는 바뀔 수 있으며, 바뀌면 Keith가 업데이트합니다.'),
    'ar_e': L('By area', '按地区看新闻', '按地區看新聞', 'Mengikut kawasan', 'エリア別', '지역별'),
    'ar_h': L('News where you are looking', '你关注地区的新闻', '你關注地區的新聞', 'Berita di kawasan pilihan anda', '気になるエリアのニュース', '관심 지역 뉴스'),
    'ar_g': L('area guide and projects →', '地区指南和项目 →', '地區指南和項目 →', 'panduan kawasan dan projek →', 'エリアガイドとプロジェクト →', '지역 가이드와 프로젝트 →'),
    'tl_e': L('Tools', '工具区', '工具區', 'Alat', 'ツール', '도구'),
    'tl_h': L('Work out your numbers', '算一算你的数字', '算一算你的數字', 'Kira angka anda', '数字を確認する', '숫자 계산해 보기'),
    'open': L('Open →', '打开 →', '打開 →', 'Buka →', '開く →', '열기 →'),
}
# Timeline of key dates: (date for the countdown, day label, year, area, kind, title, note, colour). Past items fade and show "Done".
TIMELINE = [
    ('2026-12-12', L('12 Dec', '12月12日', '12月12日', '12 Dis', '12月12日', '12월 12일'), '2026', 'Malaysia', 'rail',
     L('ECRL passenger services begin', 'ECRL 东海岸铁路客运开通', 'ECRL 東海岸鐵路客運開通', 'Perkhidmatan penumpang ECRL bermula', 'ECRL 旅客運行開始', 'ECRL 여객 운행 시작'),
     L('Gombak to Kuantan, Kuala Terengganu and Kota Bharu. Target date, subject to final safety approval.', '鹅唛通往关丹、瓜拉登嘉楼和哥打巴鲁。目标日期，仍需最终安全批准。', '鵝嘜通往關丹、瓜拉登嘉樓和哥打巴魯。目標日期，仍需最終安全批准。',
       'Gombak ke Kuantan, Kuala Terengganu dan Kota Bharu. Tarikh sasaran, tertakluk kepada kelulusan keselamatan akhir.', 'ゴンバックからクアンタン、クアラ・トレンガヌ、コタバルへ。目標日で、最終的な安全承認が条件です。', '곰박에서 콴탄, 쿠알라 트렝가누, 코타바루까지. 목표일이며 최종 안전 승인이 필요합니다.'), '#0b8f6b'),
    ('2027-01-01', L('1 Jan', '1月1日', '1月1日', '1 Jan', '1月1日', '1월 1일'), '2027', 'Malaysia', 'tax',
     L('First-home stamp duty: proposed extension', '首购印花税豁免：建议延长', '首購印花稅豁免：建議延長', 'Duti setem rumah pertama: cadangan lanjutan', '初回購入の印紙税免除：延長案', '첫 주택 인지세 면제: 연장안'),
     L('Budget 2027 proposes the exemption for SPAs signed from 2027 to 2030. Not law until passed.', '2027 年财政预算案建议豁免适用于 2027 至 2030 年签的买卖合约，通过前还不是法律。', '2027 年財政預算案建議豁免適用於 2027 至 2030 年簽的買賣合約，通過前還不是法律。',
       'Belanjawan 2027 mencadangkan pengecualian bagi SPA ditandatangani dari 2027 hingga 2030. Belum menjadi undang-undang sehingga diluluskan.', '2027年度予算案は2027〜2030年に締結する売買契約への免除を提案。成立するまでは法律ではありません。', '2027년 예산안은 2027~2030년에 체결하는 매매계약에 면제를 제안했습니다. 통과 전까지는 법이 아닙니다.'), '#e8590c'),
    ('2027-01-21', L('21 Jan', '1月21日', '1月21日', '21 Jan', '1月21日', '1월 21일'), '2027', 'Malaysia', 'rates',
     L('Bank Negara: first OPR meeting of 2027', '国行 2027 年首次议息会议', '國行 2027 年首次議息會議', 'Bank Negara: mesyuarat OPR pertama 2027', 'マレーシア中銀：2027年最初の OPR 会合', '중앙은행: 2027년 첫 OPR 회의'),
     L('The OPR has been 2.75% since July 2025.', '隔夜政策利率自 2025 年 7 月起为 2.75%。', '隔夜政策利率自 2025 年 7 月起為 2.75%。', 'OPR kekal 2.75% sejak Julai 2025.', 'OPR は2025年7月から2.75%です。', 'OPR은 2025년 7월부터 2.75%입니다.'), '#5E60CE'),
    ('2027-02-01', L('Feb', '2月', '2月', 'Feb', '2月', '2월'), '2027', 'Johor', 'rail',
     L('RTS Link Johor Bahru–Singapore opens', '新山—新加坡 RTS 通车', '新山—新加坡 RTS 通車', 'RTS Link Johor Bahru–Singapura dibuka', 'ジョホールバル–シンガポール RTS 開業', '조호르바루–싱가포르 RTS 개통'),
     L('Bukit Chagar to Woodlands North. Target month.', 'Bukit Chagar 至 Woodlands North。目标月份。', 'Bukit Chagar 至 Woodlands North。目標月份。', 'Bukit Chagar ke Woodlands North. Bulan sasaran.', 'Bukit Chagar から Woodlands North まで。目標の月です。', 'Bukit Chagar에서 Woodlands North까지. 목표 월입니다.'), '#9333ea'),
    ('2028-01-01', L('Jan', '1月', '1月', 'Jan', '1月', '1월'), '2028', 'Selangor', 'rail',
     L('ECRL Phase 2 towards Port Klang', 'ECRL 第二阶段通往巴生港口', 'ECRL 第二階段通往巴生港口', 'ECRL Fasa 2 ke Pelabuhan Klang', 'ECRL 第2期、ポートクラン方面へ', 'ECRL 2단계, 포트 클랑 방향'),
     L('Serendah, Puncak Alam and Kapar stations. Target.', '士毛月、本地阿南和加埔设站。目标。', '士毛月、本地阿南和加埔設站。目標。', 'Stesen Serendah, Puncak Alam dan Kapar. Sasaran.', 'スレンダ、プンチャック・アラム、カパーに駅。目標です。', '스렌다, 푼착 알람, 카파르 역. 목표입니다.'), '#0b8f6b'),
]
KIND_TX = {'rail': L('Rail', '铁路', '鐵路', 'Rel', '鉄道', '철도'), 'tax': L('Tax', '税务', '稅務', 'Cukai', '税金', '세금'), 'rates': L('Rates', '利率', '利率', 'Kadar', '金利', '금리')}
AREA_TX = {'Malaysia': L('Malaysia', '马来西亚', '馬來西亞', 'Malaysia', 'マレーシア', '말레이시아'), 'Johor': L('Johor', '柔佛', '柔佛', 'Johor', 'ジョホール', '조호르'), 'Selangor': L('Selangor', '雪兰莪', '雪蘭莪', 'Selangor', 'セランゴール', '슬랑오르')}
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
    items = ''.join('<li class="tl-i" data-d="%s" style="--c:%s"><div class="tl-dot"></div><div class="tl-when"><b>%s</b><span>%s</span><em class="tl-cd"></em></div>'
                    '<div class="tl-card"><div class="tl-tags"><i>%s</i><i class="k">%s</i></div><h3>%s</h3><p>%s</p></div></li>' % (
        iso, c, span('kd%dd' % k, d), y, span('kd%da' % k, AREA_TX[a]), span('kd%dk' % k, KIND_TX[kd]), span('kd%dh' % k, h), span('kd%ds' % k, sn))
        for k, (iso, d, y, a, kd, h, sn, c) in enumerate(TIMELINE))
    CD = json.dumps({'days': L('in {n} days', '还有 {n} 天', '還有 {n} 天', 'lagi {n} hari', 'あと{n}日', '{n}일 남음'), 'day1': L('tomorrow', '明天', '明天', 'esok', '明日', '내일'),
                     'months': L('in {n} months', '还有 {n} 个月', '還有 {n} 個月', 'lagi {n} bulan', 'あと{n}か月', '{n}개월 남음'), 'done': L('Done', '已过', '已過', 'Selesai', '終了', '지남'),
                     'today0': L('today', '今天', '今天', 'hari ini', '今日', '오늘')}, ensure_ascii=False)
    dates = ('<section class="tl-sec" id="key-dates"><div class="nh-w"><div class="tl-head"><div><span class="nh-eb">%s</span><h2 class="nh-h2" style="margin-bottom:0">%s</h2></div>'
             '<span class="tl-now"><i></i>%s · <b></b></span></div><ol class="tl">%s</ol><p class="tl-note">%s</p></div></section>'
             '<script>(function(){var C=%s;function lg(){var l="en";try{l=document.documentElement.getAttribute("data-page-lang")||localStorage.getItem("kn_lang")||"en"}catch(e){}return C.done[l]?l:"en";}'
             'function go(){var l=lg(),now=new Date();document.querySelectorAll(".tl-i").forEach(function(li){var d=new Date(li.getAttribute("data-d")+"T00:00:00+08:00"),days=Math.ceil((d-now)/864e5),e=li.querySelector(".tl-cd");'
             'li.classList.toggle("past",days<0);e.textContent=days<0?C.done[l]:days==0?C.today0[l]:days==1?C.day1[l]:days<60?C.days[l].replace("{n}",days):C.months[l].replace("{n}",Math.round(days/30.4));});'
             'var n=document.querySelector(".tl-now b");if(n)try{n.textContent=now.toLocaleDateString(l,{day:"numeric",month:"short",year:"numeric"})}catch(x){n.textContent=now.toDateString()}}'
             'go();var w=window.knSetLang;if(typeof w==="function"){window.knSetLang=function(){var r=w.apply(this,arguments);go();return r;};}})();</script>') % (u('kd_e'), u('kd_h'), u('kd_today'), items, u('kd_n'), CD)
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
.tl-sec{position:relative;overflow:hidden;isolation:isolate;padding:56px 0 50px;margin-top:40px;background:radial-gradient(600px 300px at 90% 10%,rgba(94,96,206,.20),transparent 65%),radial-gradient(520px 300px at 5% 100%,rgba(186,170,255,.30),transparent 65%),linear-gradient(180deg,#f1effc,#f6f4fb)}
.tl-sec:before{content:"";position:absolute;inset:0;z-index:-1;background-image:radial-gradient(rgba(94,96,206,.14) 1.2px,transparent 1.4px);background-size:24px 24px;-webkit-mask-image:linear-gradient(90deg,transparent,#000 60%);mask-image:linear-gradient(90deg,transparent,#000 60%)}
.tl-head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap}.tl-now{display:inline-flex;align-items:center;gap:8px;background:#fff;border-radius:100px;padding:8px 14px;font:700 13px Inter,sans-serif;color:#1d1b4f;box-shadow:0 6px 16px rgba(29,27,79,.08)}
.tl-now i{width:9px;height:9px;border-radius:50%;background:#22c55e;box-shadow:0 0 0 0 rgba(34,197,94,.6);animation:tlp 1.8s infinite}@keyframes tlp{70%{box-shadow:0 0 0 9px rgba(34,197,94,0)}100%{box-shadow:0 0 0 0 rgba(34,197,94,0)}}
.tl{list-style:none;margin:30px 0 0;padding:0;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:16px;position:relative}
.tl:before{content:"";position:absolute;left:0;right:0;top:9px;height:3px;border-radius:3px;background:linear-gradient(90deg,#5E60CE,#a9abff 70%,rgba(169,171,255,.25))}
.tl-i{position:relative;padding-top:30px}.tl-dot{position:absolute;top:0;left:0;width:21px;height:21px;border-radius:50%;background:#fff;border:5px solid var(--c);box-shadow:0 4px 10px rgba(29,27,79,.18)}
.tl-when b{display:block;font:700 26px/1.1 'Playfair Display',serif;color:#15142b}.tl-when span{font:700 13px Inter,sans-serif;color:#77768c;letter-spacing:.08em}
.tl-cd{display:inline-block;margin-left:8px;font:700 11.5px Inter,sans-serif;font-style:normal;color:#fff;background:var(--c);padding:3px 8px;border-radius:100px;vertical-align:2px}
.tl-card{margin-top:12px;background:#fff;border-radius:18px;padding:16px;border-top:4px solid var(--c);box-shadow:0 12px 28px rgba(29,27,79,.08);min-height:150px}
.tl-tags{display:flex;gap:6px;flex-wrap:wrap}.tl-tags i{font:700 10.5px Inter,sans-serif;font-style:normal;letter-spacing:.1em;text-transform:uppercase;color:#55546b;background:#f3f1fa;padding:3px 8px;border-radius:100px}.tl-tags i.k{color:var(--c)}
.tl-card h3{font:700 16.5px/1.3 'Playfair Display',serif;color:#15142b;margin:10px 0 6px}.tl-card p{font-size:13px;line-height:1.55;color:#55546b;margin:0}
.tl-i.past{opacity:.45}.tl-note{color:#77768c;font-size:12.5px;margin-top:16px}
@media(max-width:1000px){.tl{grid-template-columns:1fr;gap:0;padding-left:34px}.tl:before{left:9px;right:auto;top:0;bottom:0;width:3px;height:auto;background:linear-gradient(180deg,#5E60CE,#a9abff 70%,rgba(169,171,255,.25))}.tl-i{padding:0 0 22px}.tl-dot{left:-34px;top:2px}.tl-card{min-height:0}}
@media(max-width:1000px){.nh-proj,.nh-list{grid-template-columns:1fr 1fr}.nh-dates,.nh-tools{grid-template-columns:1fr}.nh-week{grid-template-columns:1fr}}
@media(max-width:560px){.nh-list{grid-template-columns:1fr}.nh-proj{gap:10px}.nh-proj b{font-size:15px}.nh-proj span{padding:10px}.nh-lead{padding:22px}}
</style>'''
