"""Build the data, cards, filters, presets and comparison extras of compare.html.

Everything comes from PROJECT_DETAILS in projects.html, so the compare page never
goes stale: price, psf, monthly instalment, maintenance fee, units, car parks,
nearest rail station, developer, title and buyer eligibility. It also writes
the state / area filter chips, the "popular comparisons" presets, best-value
badges, share link (compare.html?p=slug,slug), print and a map of the selection.
Safe to run again: every generated part sits between markers or is rebuilt.
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

E = lambda s: html.escape(str(s if s is not None else ''), quote=True)
PATH = os.path.join(ROOT, 'compare.html')
s = open(PATH, encoding='utf-8').read()


def raw_json(text, key):
    i = text.index(key)
    i = text.index('=', i) + 1
    j = len(text[:i]) + (len(text[i:]) - len(text[i:].lstrip()))
    v, n = json.JSONDecoder().raw_decode(text[j:])
    return v, j, j + n


OLD, a0, a1 = raw_json(s, 'const PROJECTS = ')
OLD = {p['name']: p for p in OLD}
PHOTO_OLD = dict((n, src) for src, n in re.findall(r'<img class="cmp-card-photo" src="([^"]+)" alt="([^"]*)"', s))
PHOTO_OLD = {html.unescape(n): v for n, v in PHOTO_OLD.items()}
DEF_ICON = next(iter(OLD.values()))['icon'] if OLD else ''

RAIL = re.compile(r'\b(MRT|LRT|KTM|ERL|Monorail|BRT|RTS)\b')


def num(t):
    return float(t.replace(',', ''))


def first_rm(t):
    m = re.search(r'RM\s?([\d,]+(?:\.\d+)?)', t or '')
    return num(m.group(1)) if m else None


def sizes(t):
    v = [num(x) for x in re.findall(r'\d[\d,]*(?:\.\d+)?', (t or '').replace('sqft', '')) if num(x) >= 200]
    return (min(v), max(v)) if v else (None, None)


def instal(price, down=0.10, rate=0.04, years=35):
    loan, r, n = price * (1 - down), rate / 12, years * 12
    return loan * r / (1 - (1 + r) ** -n)


def clean_price(p):
    return re.sub(r'\s*\((?:Gross|gross)\)', '', p or '').strip() or 'Price on Request'


rows = []
for k, p in enumerate(A.P):
    d = p.get('details_extra') or {}
    st, area = A.PLACES[k]
    price = A.price_rm(p.get('price'))
    lo, hi = sizes(p.get('size'))
    psf_txt = d.get('Price per Sqft') or ''
    psf = first_rm(psf_txt)
    psf_est = False
    if not psf and price and lo:
        psf, psf_est = round(price / lo), True
    maint_txt = d.get('Maintenance Fee') or d.get('Maintenance') or ''
    maint = first_rm(maint_txt)
    units_txt = d.get('Total Units') or d.get('Number of Units') or ''
    um = re.search(r'(\d[\d,]*)\s*(?:units|residences|homes)', units_txt, re.I) or re.search(r'^(\d[\d,]*)', units_txt)
    units = int(num(um.group(1))) if um else None
    rail = next((x for x in (p.get('amenities') or []) + (p.get('points') or []) if RAIL.search(x)), '')
    years = [int(y) for y in re.findall(r'\b(20[2-4]\d)\b', p.get('completion') or '')]
    done = (p.get('status') or '').lower() == 'completed'
    old = OLD.get(p['name'], {})
    rows.append({
        'name': p['name'], 'slug': A.SLUG.get(k, A.slug(p['name'])), 'state': st, 'area': area,
        'type': A.TYPE.get(k) or old.get('type') or 'Residential',
        'tenure': p.get('tenure') or '', 'status': p.get('status') or '', 'completion': p.get('completion') or '',
        'price': clean_price(p.get('price')), 'size': p.get('size') or '', 'rooms': p.get('rooms') or '',
        'loc': p.get('loc') or '', 'dev': d.get('Developer') or '', 'title': d.get('Title') or '',
        'maint': maint_txt, 'units': units_txt, 'cars': d.get('Car Parks') or d.get('Car Park') or '',
        'rail': rail, 'elig': d.get('Eligibility') or d.get('Foreign Ownership') or '',
        'psfTxt': ('≈ RM%s psf' % format(int(psf), ',')) if psf_est else re.sub(r'^From (about )?', '', re.sub(r'\s*\((?:Gross|gross)\)', '', psf_txt)),
        # numbers used for the "best" badges (all in MYR)
        'nPrice': price, 'nPsf': psf, 'nMo': round(instal(price)) if price else None, 'nSize': hi,
        'nMaint': maint, 'nUnits': units, 'nYear': 0 if done else (min(years) if years else None),
        'icon': old.get('icon') or DEF_ICON, 'grad': old.get('grad') or '#1c1a17,#3a3226',
        'photo': PHOTO_OLD.get(p['name']) or A.PHOTO.get(k) or '',
        'll': (A.COORDS.get(p['name']) or [None, None])[:2],
        'url': 'property/%s.html' % A.SLUG.get(k, A.slug(p['name'])),
    })

rows.sort(key=lambda r: re.sub(r'[^a-z0-9 ]', '', r['name'].lower()))   # projects are listed A-Z
IDX = {r['name']: i for i, r in enumerate(rows)}

# ---------- cards ----------
STATUS_CLS = {'completed': 'status-completed', 'under construction': 'status-construction'}
cards = []
for i, r in enumerate(rows):
    photo = ('<img class="cmp-card-photo" src="%s" alt="%s" loading="lazy">' % (E(r['photo']), E(r['name']))) if r['photo'] else ''
    cards.append(
        '  <div class="cmp-card" data-idx="%d" onclick="toggleSelect(%d)" data-search="%s">\n'
        '    <div class="cmp-card-media" style="background:linear-gradient(135deg,%s);">\n'
        '      %s\n      <div class="cmp-card-icon">%s</div>\n'
        '      <span class="cmp-card-status %s">%s</span>\n    </div>\n'
        '    <div class="cmp-card-body">\n      <span class="cmp-card-tag">%s</span>\n      <h4>%s</h4>\n'
        '      <p class="cmp-card-loc">%s</p>\n      <div class="cmp-card-foot">\n        <strong>%s</strong>\n'
        '        <button class="cmp-add-btn" tabindex="-1">+ Add</button>\n      </div>\n    </div>\n  </div>\n' % (
            i, i, E(' '.join([r['name'], r['area'], r['state'], r['loc']]).lower()), r['grad'], photo, r['icon'],
            STATUS_CLS.get(r['status'].lower(), 'status-comingsoon'), E(r['status']), E(r['area']), E(r['name']),
            E(r['loc']), E(r['price'])))
g0 = s.index('<div class="cmp-grid" id="cmpGrid">') + len('<div class="cmp-grid" id="cmpGrid">')
g1 = s.index('<div class="cmp-empty" id="cmpEmpty">', g0)
s = s[:g0] + '\n' + ''.join(cards) + '\n    ' + s[g1:]

# ---------- state / area filter chips ----------
states = {}
for r in rows:
    states.setdefault(r['state'], {}).setdefault(r['area'], 0)
    states[r['state']][r['area']] += 1
order = [x for x in A.STATES if x in states] + sorted(x for x in states if x not in A.STATES)
chips = ['      <div class="cmp-filter-btn active" data-tag="All">All Projects</div>']
subs = []
for st in order:
    chips.append('      <div class="cmp-filter-btn" data-state="%s">%s <em>(%d)</em></div>' % (E(st), E(st), sum(states[st].values())))
    if len(states[st]) > 1:
        subs.append('      <div class="cmp-sub" data-for="%s">%s</div>' % (E(st), ''.join(
            '<div class="cmp-filter-btn cmp-sub-btn" data-area="%s">%s <em>(%d)</em></div>' % (E(ar), E(ar), n)
            for ar, n in sorted(states[st].items(), key=lambda x: (-x[1], x[0])))))
f0 = s.index('<div class="cmp-filter-wrap" id="cmpFilters">')
f1 = s.index('<div class="cmp-bar" id="cmpBar">', f0)
f1 = s.rindex('</div>', f0, f1) + len('</div>')
s = s[:f0] + '<div class="cmp-filter-wrap" id="cmpFilters">\n' + '\n'.join(chips) + '\n    </div>\n' \
    '    <div class="cmp-subs" id="cmpSubs">\n' + '\n'.join(subs) + '\n    </div>' + s[f1:]

# ---------- popular comparison presets ----------


def cheapest(ok, n=3):
    c = sorted((r for r in rows if ok(r) and r['nPrice']), key=lambda r: r['nPrice'])[:n]
    return [r['name'] for r in c]


PRESETS = [
    ('Bukit Jalil trio', ['The Kingswoodz', 'The Queenswoodz', 'The Vividz']),
    ('KL City Centre under RM1M', cheapest(lambda r: r['area'] == 'KL City Centre' and (r['nPrice'] or 9e9) < 1e6)),
    ('Freehold near MRT/LRT', cheapest(lambda r: r['tenure'].lower().startswith('freehold') and re.search(r'\b(MRT|LRT)\b', r['rail']))),
    ('Johor Bahru near RTS Link', cheapest(lambda r: r['state'] == 'Johor' and 'RTS' in r['rail'])),
    ('Kwasa Damansara MRT', cheapest(lambda r: r['area'] == 'Kwasa Damansara')),
    ('Penang best value', cheapest(lambda r: r['state'] == 'Penang')),
]
pre = []
for label, names in PRESETS:
    ids = [IDX[n] for n in names if n in IDX]
    if len(ids) < 2:
        continue
    pre.append('<button type="button" class="cmp-preset" data-p="%s"><div class="t">%s</div><div class="s">%s</div></button>' % (
        ','.join(map(str, ids)), E(label), E(' · '.join(re.sub(r'^The ', '', rows[i]['name']) for i in ids))))
PRE_HTML = ('<!-- KN-CMP-PRESETS:START --><div class="cmp-presets"><div class="cmp-presets-head"><h3>Popular comparisons</h3>'
            '<p>One tap to compare popular combinations.</p></div><div class="cmp-preset-row">%s</div></div><!-- KN-CMP-PRESETS:END -->\n    ') % ''.join(pre)
s = re.sub(r'<!-- KN-CMP-PRESETS:START -->.*?<!-- KN-CMP-PRESETS:END -->\n\s*', '', s, flags=re.S)
s = s.replace('<div class="cmp-search-row">', PRE_HTML + '<div class="cmp-search-row">', 1)

# ---------- hero ----------
HERO = "Side-by-side comparison of Keith's new launch projects across Malaysia."
s = re.sub(r'(<section class="cmp-hero">.*?<h1>Compare Projects</h1>\s*<p>).*?(</p>)', lambda m: m.group(1) + HERO + m.group(2), s, count=1, flags=re.S)

# ---------- data ----------
DATA = [{k: v for k, v in r.items() if k != 'photo'} for r in rows]
s2, b0, b1 = raw_json(s, 'const PROJECTS = ')
s = s[:b0] + json.dumps(DATA, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + s[b1:]

# ---------- labels for the comparison table (per language) ----------
LBL = {
    'en': {'dev': 'Developer', 'type': 'Type', 'tenure': 'Tenure', 'title': 'Title', 'status': 'Status', 'completion': 'Completion',
           'price': 'Starting price', 'psf': 'Price psf', 'mo': 'Est. monthly (35 yrs)', 'size': 'Size', 'rooms': 'Bedrooms',
           'maint': 'Maintenance fee', 'units': 'Total units', 'cars': 'Car parks', 'rail': 'Nearest rail', 'area': 'Area',
           'elig': 'Buyer eligibility', 'low': 'Lowest', 'large': 'Largest', 'early': 'Earliest', 'few': 'Most exclusive',
           'pm': '/ month', 'moNote': '10% down, 4% p.a. Estimate only.', 'share': 'Copy share link', 'copied': 'Link copied!',
           'print': 'Print / Save PDF', 'map': 'Where they are', 'mapNote': 'Pins show approximate locations.', 'view': 'View project',
           'best': 'Best value is marked for each row.', 'calc': 'Open calculator', 'ready': 'Ready'},
    'zh-CN': {'dev': '发展商', 'type': '类型', 'tenure': '产权', 'title': '地契', 'status': '状态', 'completion': '竣工',
              'price': '起价', 'psf': '每平方尺价格', 'mo': '预计月供（35 年）', 'size': '面积', 'rooms': '卧室',
              'maint': '管理费', 'units': '总单位', 'cars': '停车位', 'rail': '最近轨道站', 'area': '地区',
              'elig': '购买资格', 'low': '最低', 'large': '最大', 'early': '最早', 'few': '最低密度',
              'pm': '/ 月', 'moNote': '首付 10%，年利率 4%，仅供参考。', 'share': '复制分享链接', 'copied': '链接已复制！',
              'print': '打印 / 保存 PDF', 'map': '项目位置', 'mapNote': '地图标记为大约位置。', 'view': '查看项目',
              'best': '每一行的最佳数值已标出。', 'calc': '打开计算器', 'ready': '现房'},
    'ms': {'dev': 'Pemaju', 'type': 'Jenis', 'tenure': 'Pegangan', 'title': 'Hak milik', 'status': 'Status', 'completion': 'Siap',
           'price': 'Harga permulaan', 'psf': 'Harga sk', 'mo': 'Anggaran bulanan (35 thn)', 'size': 'Saiz', 'rooms': 'Bilik tidur',
           'maint': 'Yuran penyelenggaraan', 'units': 'Jumlah unit', 'cars': 'Tempat letak kereta', 'rail': 'Stesen rel terdekat', 'area': 'Kawasan',
           'elig': 'Kelayakan pembeli', 'low': 'Terendah', 'large': 'Terbesar', 'early': 'Terawal', 'few': 'Paling eksklusif',
           'pm': '/ bulan', 'moNote': 'Deposit 10%, 4% setahun. Anggaran sahaja.', 'share': 'Salin pautan', 'copied': 'Pautan disalin!',
           'print': 'Cetak / Simpan PDF', 'map': 'Lokasi projek', 'mapNote': 'Pin menunjukkan lokasi anggaran.', 'view': 'Lihat projek',
           'best': 'Nilai terbaik ditandakan bagi setiap baris.', 'calc': 'Buka kalkulator', 'ready': 'Sedia'},
    'ja': {'dev': 'デベロッパー', 'type': 'タイプ', 'tenure': '保有形態', 'title': '権利種別', 'status': 'ステータス', 'completion': '完成',
           'price': '最低価格', 'psf': '平方フィート単価', 'mo': '月々の返済目安（35年）', 'size': '面積', 'rooms': 'ベッドルーム',
           'maint': '管理費', 'units': '総戸数', 'cars': '駐車場', 'rail': '最寄り駅', 'area': 'エリア',
           'elig': '購入資格', 'low': '最安', 'large': '最大', 'early': '最も早い', 'few': '最も希少',
           'pm': '/ 月', 'moNote': '頭金10%、年利4%。目安です。', 'share': '共有リンクをコピー', 'copied': 'コピーしました！',
           'print': '印刷 / PDF保存', 'map': '所在地', 'mapNote': 'ピンはおおよその位置です。', 'view': 'プロジェクトを見る',
           'best': '各行のベスト値に印が付いています。', 'calc': '計算機を開く', 'ready': '完成済み'},
    'ko': {'dev': '개발사', 'type': '유형', 'tenure': '소유 형태', 'title': '권리 유형', 'status': '상태', 'completion': '준공',
           'price': '시작 가격', 'psf': '평방피트당 가격', 'mo': '예상 월 상환액 (35년)', 'size': '면적', 'rooms': '침실',
           'maint': '관리비', 'units': '총 세대수', 'cars': '주차', 'rail': '가장 가까운 역', 'area': '지역',
           'elig': '구매 자격', 'low': '최저', 'large': '최대', 'early': '가장 빠름', 'few': '가장 희소',
           'pm': '/ 월', 'moNote': '계약금 10%, 연 4%. 참고용 추정치입니다.', 'share': '공유 링크 복사', 'copied': '링크가 복사되었습니다!',
           'print': '인쇄 / PDF 저장', 'map': '위치', 'mapNote': '핀은 대략적인 위치입니다.', 'view': '프로젝트 보기',
           'best': '각 행의 최고 값이 표시됩니다.', 'calc': '계산기 열기', 'ready': '입주 가능'},
}
try:
    import opencc
    _cc = opencc.OpenCC('s2tw')
    LBL['zh-TW'] = {k: _cc.convert(v) for k, v in LBL['zh-CN'].items()}
except ImportError:
    LBL['zh-TW'] = dict(LBL['zh-CN'])

CSS = '''/* KN-CMP:START */
  .cmp-subs{margin:-8px 0 22px;} .cmp-sub{display:none; flex-wrap:wrap; gap:8px; padding:12px 14px; background:var(--bg); border-radius:10px;}
  .cmp-sub.show{display:flex;} .cmp-filter-btn em{font-style:normal;} .cmp-sub-btn{font-size:12px; padding:6px 13px; background:#fff;}
  .cmp-presets{margin:0 0 22px; padding:18px 18px 16px; border-radius:12px; background:linear-gradient(135deg,#f3f1fa,#fbfaf7); border:1px solid rgba(94,96,206,.15);}
  .cmp-presets-head{display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; margin-bottom:12px;}
  .cmp-presets-head h3{font-size:18px;} .cmp-presets-head p{font-size:12.5px; color:var(--grey); font-weight:500;}
  .cmp-preset-row{display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:10px;}
  .cmp-preset{all:unset; box-sizing:border-box; cursor:pointer; background:#fff; border:1px solid var(--line); border-radius:10px; padding:11px 14px; transition:all .25s var(--ease); min-width:0;}
  .cmp-preset:hover,.cmp-preset:focus-visible{border-color:var(--gold); box-shadow:0 6px 18px rgba(94,96,206,.15); transform:translateY(-1px);}
  .cmp-preset .t{display:block; font-size:13.5px; color:var(--ink); margin-bottom:3px;}
  .cmp-preset .s{display:block; font-size:11.5px; color:var(--grey); font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
  .cmp-table td.best{background:#eef7f0;} .cmp-best{display:inline-block; margin-top:6px; font-size:10.5px; font-weight:800; letter-spacing:.04em; text-transform:uppercase; color:#1f7a3d; background:#d7f0de; border-radius:100px; padding:2px 8px;}
  .cmp-best:before{content:"\\2605 ";}
  .cmp-table td small{display:block; color:var(--grey); font-size:11px; font-weight:500; margin-top:3px;}
  .cmp-table td a.cmp-mini{color:var(--gold); font-size:11.5px; font-weight:700;}
  .cmp-th-name a{color:inherit;} .cmp-th-name a:hover{color:var(--gold);}
  .cmp-note{padding:0 28px; font-size:12px; color:var(--grey); font-weight:500;}
  .cmp-map-wrap{padding:6px 28px 4px;} .cmp-map-wrap h4{font-size:17px; margin-bottom:10px;}
  #cmpMap{height:300px; border-radius:12px; overflow:hidden; border:1px solid var(--line); background:#eef0f4; z-index:0;}
  .cmp-map-wrap p{font-size:11.5px; color:var(--grey); margin-top:6px; font-weight:500;}
  .cmpn{background:#5E60CE; color:#fff; font:800 13px Inter,sans-serif; width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:3px solid #fff; box-shadow:0 2px 8px rgba(17,17,17,.35);}
  .cmp-th-num{display:inline-flex; width:20px; height:20px; border-radius:50%; background:#5E60CE; color:#fff; font-size:11px; font-weight:800; align-items:center; justify-content:center; margin-right:6px; vertical-align:2px;}
  .cmp-actions{display:flex; gap:10px; justify-content:center; flex-wrap:wrap;}
  .cmp-actions .btn-line{background:#fff; color:var(--ink); border:1px solid var(--line);} .cmp-actions .btn-line:hover{border-color:var(--gold); color:var(--gold);}
  @media(max-width:700px){ .cmp-preset-row{grid-template-columns:1fr 1fr;} .cmp-preset{padding:10px 11px;} .cmp-note,.cmp-map-wrap{padding-left:16px; padding-right:16px;} #cmpMap{height:240px;} }
  @media print{
    body > *:not(#cmpModalOverlay){display:none !important;}
    .cmp-modal-overlay{position:static !important; display:block !important; background:none !important; padding:0 !important; opacity:1 !important; visibility:visible !important;}
    .cmp-modal{max-height:none !important; overflow:visible !important; box-shadow:none !important; transform:none !important; width:100% !important; max-width:none !important;}
    .cmp-modal-head-right,.cmp-th-remove,.cmp-actions,.cmp-map-wrap{display:none !important;}
    .cmp-table td.best{-webkit-print-color-adjust:exact; print-color-adjust:exact;}
  }
/* KN-CMP:END */
'''
s = re.sub(r'(<style id="kn-cmp">\n)?/\* KN-CMP:START \*/.*?/\* KN-CMP:END \*/\n(</style>\n)?', '', s, flags=re.S)
s = s.replace('</head>', '<style id="kn-cmp">\n' + CSS + '</style>\n</head>', 1)

JS = r'''<!-- KN-CMP:START -->
<script>
(function(){
  var LBL = __LBL__;
  function lang(){ var l = (typeof currentLang !== 'undefined' && currentLang) ? currentLang : 'en'; return LBL[l] ? l : 'en'; }
  function T(k){ return LBL[lang()][k] || LBL.en[k]; }
  function esc(v){ return escapeHtml(v == null ? '' : v); }
  function rm(n){ return 'RM ' + Math.round(n).toLocaleString('en-US'); }
  var ROWS = [
    {k:'dev'}, {k:'type'}, {k:'tenure'}, {k:'title'}, {k:'status'},
    {k:'completion', n:'nYear', best:'min', b:'early'},
    {k:'price', n:'nPrice', best:'min', b:'low'},
    {k:'psf', v:'psfTxt', n:'nPsf', best:'min', b:'low'},
    {k:'mo', n:'nMo', best:'min', b:'low', fmt:function(p){ return p.nMo ? rm(p.nMo) + ' ' + T('pm') : ''; }},
    {k:'size', n:'nSize', best:'max', b:'large'}, {k:'rooms'},
    {k:'maint', n:'nMaint', best:'min', b:'low'},
    {k:'units', n:'nUnits', best:'min', b:'few'},
    {k:'cars'}, {k:'rail'},
    {k:'area', fmt:function(p){ return p.area + ', ' + p.state; }},
    {k:'elig', opt:true}
  ];
  function val(p, r){ if(r.fmt) return r.fmt(p); return p[r.v || r.k] || ''; }
  function bestSet(r){
    if(!r.best) return [];
    var nums = selectedIdx.map(function(i){ var v = PROJECTS[i][r.n]; return (v === null || v === undefined) ? null : v; });
    var have = nums.filter(function(v){ return v !== null; });
    if(have.length < 2) return [];
    var b = r.best === 'min' ? Math.min.apply(null, have) : Math.max.apply(null, have);
    if(have.every(function(v){ return v === b; })) return [];
    return nums.map(function(v){ return v === b; });
  }
  window.renderTable = function(){
    var table = document.getElementById('cmpTable');
    document.getElementById('cmpModalTitle').textContent = 'Compare Projects (' + selectedIdx.length + ' / 3 Selected)';
    var names = selectedIdx.map(function(i){ return PROJECTS[i].name; });
    var namesText = names.length < 3 ? names.join(' and ') : names.slice(0, -1).join(', ') + ' and ' + names[names.length - 1];
    var wa = document.getElementById('cmpWaLink');
    if(wa) wa.href = 'https://api.whatsapp.com/send/?phone=60102821568&text=' + encodeURIComponent('(KNRE) Hi Keith, I\'m comparing ' + namesText + ' and would like your advice on which fits me best. ' + shareUrl()) + '&type=phone_number&app_absent=0';
    var h = '<colgroup><col class="label-col">' + selectedIdx.map(function(){ return '<col>'; }).join('') + '</colgroup><thead><tr><th></th>';
    selectedIdx.forEach(function(idx, n){
      var p = PROJECTS[idx];
      var img = document.querySelector('.cmp-card[data-idx="' + idx + '"] .cmp-card-photo');
      var media = img ? '<img class="cmp-th-photo" src="' + img.getAttribute('src') + '" alt="' + esc(p.name) + '">' : '<div class="cmp-th-icon">' + p.icon + '</div>';
      h += '<th><div class="cmp-th-media" style="background:linear-gradient(135deg,' + (p.grad || '#1c1a17,#3a3226') + ')">' + media
        + '<div class="cmp-th-remove" onclick="removeFromCompare(' + idx + ')">&times;</div></div>'
        + '<span class="cmp-th-name"><span class="cmp-th-num">' + (n + 1) + '</span><a href="' + p.url + '">' + esc(p.name) + '</a></span>'
        + '<span class="cmp-th-price">' + esc(p.price) + '</span></th>';
    });
    h += '</tr></thead><tbody>';
    ROWS.forEach(function(r){
      var vals = selectedIdx.map(function(i){ return val(PROJECTS[i], r); });
      if(vals.every(function(v){ return !v; })) return;
      var best = bestSet(r);
      var same = vals.every(function(v){ return v === vals[0]; });
      h += '<tr><td class="label">' + esc(T(r.k)) + '</td>';
      vals.forEach(function(v, j){
        var p = PROJECTS[selectedIdx[j]], cls = [];
        if(highlightOn && !same) cls.push('diff');
        if(best[j]) cls.push('best');
        var cell = '<div>' + (v ? esc(v) : '—') + '</div>';
        if(r.k === 'mo' && v) cell += '<small>' + esc(T('moNote')) + '</small><div><a class="cmp-mini" href="calculator.html?price=' + Math.round(p.nPrice) + '&down=10&rate=4&years=35">' + esc(T('calc')) + ' →</a></div>';
        if(best[j]) cell += '<div><span class="cmp-best">' + esc(T(r.b)) + '</span></div>';
        h += '<td class="' + cls.join(' ') + '">' + cell + '</td>';
      });
      h += '</tr>';
    });
    table.innerHTML = h + '</tbody>';
    var note = document.getElementById('cmpBestNote'); if(note) note.textContent = T('best');
    setActions();
    drawMap();
  };

  // ---- share link, print, extra buttons ----
  function shareUrl(){
    return location.origin + location.pathname + '?p=' + selectedIdx.map(function(i){ return PROJECTS[i].slug; }).join(',');
  }
  function setActions(){
    var s = document.getElementById('cmpShare'), pr = document.getElementById('cmpPrint');
    if(s && !s.dataset.busy) s.textContent = T('share');
    if(pr) pr.textContent = T('print');
    var mh = document.getElementById('cmpMapHead'), mn = document.getElementById('cmpMapNote');
    if(mh) mh.textContent = T('map'); if(mn) mn.textContent = T('mapNote');
    try{ history.replaceState(null, '', '?p=' + selectedIdx.map(function(i){ return PROJECTS[i].slug; }).join(',')); }catch(e){}
  }
  function setup(){
    var cta = document.querySelector('.cmp-modal-cta'), wa = document.getElementById('cmpWaLink');
    if(!cta || document.getElementById('cmpShare')) return;
    var wrap = document.querySelector('.cmp-table-wrap');
    var note = document.createElement('p'); note.className = 'cmp-note'; note.id = 'cmpBestNote';
    wrap.parentNode.insertBefore(note, wrap.nextSibling);
    var mw = document.createElement('div'); mw.className = 'cmp-map-wrap';
    mw.innerHTML = '<h4 id="cmpMapHead"></h4><div id="cmpMap"></div><p id="cmpMapNote"></p>';
    note.parentNode.insertBefore(mw, note.nextSibling);
    var act = document.createElement('div'); act.className = 'cmp-actions';
    wa.parentNode.insertBefore(act, wa); act.appendChild(wa);
    var sh = document.createElement('button'); sh.type = 'button'; sh.className = 'btn btn-line'; sh.id = 'cmpShare';
    sh.onclick = function(){
      var u = shareUrl();
      function done(){ sh.dataset.busy = 1; sh.textContent = T('copied'); setTimeout(function(){ delete sh.dataset.busy; sh.textContent = T('share'); }, 2200); }
      if(navigator.share && /Mobi|Android|iPhone/i.test(navigator.userAgent)){ navigator.share({title:document.title, url:u}).catch(function(){}); return; }
      if(navigator.clipboard) navigator.clipboard.writeText(u).then(done, function(){ prompt('', u); });
      else prompt('', u);
    };
    var pr = document.createElement('button'); pr.type = 'button'; pr.className = 'btn btn-line'; pr.id = 'cmpPrint';
    pr.onclick = function(){ window.print(); };
    act.appendChild(sh); act.appendChild(pr);
  }

  // ---- map of the selected projects (Leaflet is loaded the first time it is needed) ----
  var map = null, layer = null, loading = false;
  function loadLeaflet(cb){
    if(window.L && L.map) return cb();
    if(loading) return; loading = true;
    var c = document.createElement('link'); c.rel = 'stylesheet'; c.href = 'vendor/leaflet/leaflet.css'; document.head.appendChild(c);
    var j = document.createElement('script'); j.src = 'vendor/leaflet/leaflet.js'; j.onload = function(){ loading = false; cb(); }; document.head.appendChild(j);
  }
  function drawMap(){
    var el = document.getElementById('cmpMap'); if(!el) return;
    var pts = selectedIdx.map(function(i, n){ var p = PROJECTS[i]; return p.ll && p.ll[0] ? {p:p, n:n + 1} : null; }).filter(Boolean);
    el.parentNode.style.display = pts.length ? '' : 'none';
    if(!pts.length) return;
    loadLeaflet(function(){
      if(!map){
        map = L.map(el, {scrollWheelZoom:false, dragging:!L.Browser.mobile, tap:false});
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom:19, attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(map);
      }
      if(layer) map.removeLayer(layer);
      layer = L.layerGroup().addTo(map);
      var b = [];
      pts.forEach(function(x, j){
        var ll = x.p.ll.slice();
        pts.slice(0, j).forEach(function(y){ if(Math.abs(y.ll[0] - ll[0]) < 1e-4 && Math.abs(y.ll[1] - ll[1]) < 1e-4){ ll[0] += 0.0018 * Math.cos(j * 2.1); ll[1] += 0.0018 * Math.sin(j * 2.1); } });
        x.ll = ll;
        var ic = L.divIcon({className:'', html:'<div class="cmpn">' + x.n + '</div>', iconSize:[28,28], iconAnchor:[14,14]});
        L.marker(x.ll, {icon:ic, title:x.p.name}).addTo(layer)
          .bindTooltip(x.n + '. ' + x.p.name, {direction:j % 2 ? 'bottom' : 'top', offset:[0, j % 2 ? 12 : -12], permanent:pts.length <= 3})
          .bindPopup('<b>' + esc(x.p.name) + '</b><br>' + esc(x.p.area) + '<br><a href="' + x.p.url + '">' + esc(T('view')) + ' →</a>');
        b.push(x.ll);
      });
      setTimeout(function(){
        map.invalidateSize();
        if(b.length === 1) map.setView(b[0], 14); else map.fitBounds(b, {padding:[50,50], maxZoom:15});
      }, 60);
    });
  }

  // ---- state / area filters ----
  var fState = '', fArea = '';
  window.applyFilters = function(){
    var q = ((document.getElementById('cmpSearch') || {}).value || '').toLowerCase().trim(), n = 0;
    document.querySelectorAll('.cmp-card').forEach(function(card){
      var p = PROJECTS[+card.getAttribute('data-idx')];
      var ok = (card.getAttribute('data-search') || '').indexOf(q) > -1 && (!fState || p.state === fState) && (!fArea || p.area === fArea);
      card.style.display = ok ? '' : 'none'; if(ok) n++;
    });
    var e = document.getElementById('cmpEmpty'); if(e) e.style.display = n ? 'none' : 'block';
  };
  var fw = document.getElementById('cmpFilters'), subs = document.getElementById('cmpSubs');
  if(fw){
    var nf = fw.cloneNode(true); fw.parentNode.replaceChild(nf, fw);   // drop the old tag-based click handler
    nf.addEventListener('click', function(e){
      var b = e.target.closest('.cmp-filter-btn'); if(!b) return;
      nf.querySelectorAll('.cmp-filter-btn').forEach(function(x){ x.classList.remove('active'); });
      b.classList.add('active');
      fState = b.getAttribute('data-state') || ''; fArea = '';
      subs.querySelectorAll('.cmp-sub').forEach(function(s){ s.classList.toggle('show', s.getAttribute('data-for') === fState); s.querySelectorAll('.cmp-filter-btn').forEach(function(x){ x.classList.remove('active'); }); });
      applyFilters();
    });
  }
  var se = document.getElementById('cmpSearch'); if(se) se.addEventListener('input', function(){ applyFilters(); });
  if(subs) subs.addEventListener('click', function(e){
    var b = e.target.closest('.cmp-sub-btn'); if(!b) return;
    var on = b.classList.contains('active');
    b.parentNode.querySelectorAll('.cmp-filter-btn').forEach(function(x){ x.classList.remove('active'); });
    if(!on) b.classList.add('active');
    fArea = on ? '' : b.getAttribute('data-area');
    applyFilters();
  });

  // ---- presets and ?p= share links ----
  function compare(ids){
    selectedIdx.length = 0;
    ids.forEach(function(i){ if(PROJECTS[i] && selectedIdx.length < 3 && selectedIdx.indexOf(i) < 0) selectedIdx.push(i); });
    renderSelection();
    if(selectedIdx.length >= 2) openModal();
  }
  document.querySelectorAll('.cmp-preset').forEach(function(b){
    b.addEventListener('click', function(){ compare(b.getAttribute('data-p').split(',').map(Number)); });
  });
  setup();
  var _close = window.closeModal;
  window.closeModal = function(){ _close.apply(this, arguments); try{ history.replaceState(null, '', location.pathname); }catch(e){} };
  var _setLang = window.setLanguage;
  if(typeof _setLang === 'function') window.setLanguage = function(){
    var r = _setLang.apply(this, arguments);
    if(document.getElementById('cmpModalOverlay').classList.contains('open')) renderTable();
    return r;
  };
  var q = (location.search.match(/[?&]p=([^&]+)/) || [])[1];
  if(q){
    var want = decodeURIComponent(q).split(',');
    var ids = want.map(function(sl){ for(var i = 0; i < PROJECTS.length; i++) if(PROJECTS[i].slug === sl) return i; return -1; }).filter(function(i){ return i > -1; });
    window.addEventListener('load', function(){ compare(ids); });
  }
})();
</script>
<!-- KN-CMP:END -->
'''.replace('__LBL__', json.dumps(LBL, ensure_ascii=False))
s = re.sub(r'<!-- KN-CMP:START -->.*?<!-- KN-CMP:END -->\n', '', s, flags=re.S)
anchor = '  renderSelection();\n</script>\n'
assert anchor in s
s = s.replace(anchor, anchor + JS, 1)
open(PATH, 'w', encoding='utf-8').write(s)

# ---------- translations of the static texts (KN_TR) ----------
STATIC = {
    HERO: {'zh-CN': '并排比较 Keith 在全马来西亚的新楼盘项目。', 'ms': 'Perbandingan sebelah-menyebelah projek pelancaran baharu Keith di seluruh Malaysia.',
           'ja': 'マレーシア全国の Keith の新築プロジェクトを並べて比較。', 'ko': '말레이시아 전역의 Keith 신규 분양 프로젝트를 나란히 비교하세요.'},
    'Popular comparisons': {'zh-CN': '热门比较', 'ms': 'Perbandingan popular', 'ja': '人気の比較', 'ko': '인기 비교'},
    'One tap to compare popular combinations.': {'zh-CN': '一键比较热门组合。', 'ms': 'Satu ketikan untuk membandingkan gabungan popular.',
                                                 'ja': 'ワンタップで人気の組み合わせを比較。', 'ko': '한 번의 탭으로 인기 조합을 비교하세요.'},
    'Bukit Jalil trio': {'zh-CN': 'Bukit Jalil 三大项目', 'ms': 'Trio Bukit Jalil', 'ja': 'Bukit Jalil 3物件', 'ko': 'Bukit Jalil 3개 단지'},
    'KL City Centre under RM1M': {'zh-CN': 'KL City Centre RM1M 以下', 'ms': 'KL City Centre bawah RM1M', 'ja': 'KL City Centre RM1M以下', 'ko': 'KL City Centre RM1M 이하'},
    'Freehold near MRT/LRT': {'zh-CN': '永久地契 · 近 MRT/LRT', 'ms': 'Pegangan bebas berhampiran MRT/LRT', 'ja': '自由保有 · MRT/LRT 近く', 'ko': '자유보유 · MRT/LRT 인근'},
    'Johor Bahru near RTS Link': {'zh-CN': 'Johor Bahru 近 RTS Link', 'ms': 'Johor Bahru berhampiran RTS Link', 'ja': 'Johor Bahru RTS Link 近く', 'ko': 'Johor Bahru RTS Link 인근'},
    'Penang best value': {'zh-CN': 'Penang 高性价比', 'ms': 'Penang nilai terbaik', 'ja': 'Penang コスパ重視', 'ko': 'Penang 가성비'},
}
for l in ['zh-CN', 'zh-TW', 'ms', 'ja', 'ko']:
    p = os.path.join(ROOT, 'i18n-projects-%s.js' % l)
    t = open(p, encoding='utf-8').read()
    m = 'window.KN_TR["%s"]=' % l
    a = t.index(m) + len(m)
    d, n = json.JSONDecoder().raw_decode(t[a:])
    ch = False
    for en, v in STATIC.items():
        tr = v.get(l) or (LBL['zh-TW'].__class__ and _cc.convert(v['zh-CN']) if l == 'zh-TW' and '_cc' in globals() else None)
        key = html.escape(en, quote=False)
        val = html.escape(tr, quote=False)
        if tr and d.get(key) != val:
            d[key] = val
            ch = True
    if ch:
        open(p, 'w', encoding='utf-8').write(t[:a] + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + t[a + n:])

print('compare: %d projects, %d presets, %d states' % (len(rows), len(pre), len(order)))
