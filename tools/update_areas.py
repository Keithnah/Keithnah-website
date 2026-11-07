"""View Projects: filter by state, then area (the Location list on the left).

Works out each project's state and area from its location, then rewrites
projects.html: the card labels and data-state / data-area attributes, the
Location list, the Area box in the search form, and the filter script.
Also writes tools/project_places.json for the project page generator.

Run from the repository root:
    python3 tools/update_areas.py
    python3 tools/build_project_pages.py
Safe to run again.
"""
import html
import json
import re
from collections import OrderedDict

PAGE = 'projects.html'
STATES = ['Kuala Lumpur', 'Selangor', 'Penang', 'Johor', 'Melaka', 'Sabah', 'Terengganu', 'Kelantan']

# Old area names (used in links such as projects.html#Petaling%20Jaya) -> state[/area]
OLD_LINKS = {'Bukit Bintang': 'Kuala Lumpur/Bukit Bintang', 'KL City Centre': 'Kuala Lumpur/KL City Centre',
             'TRX & Merdeka Maybank': 'Kuala Lumpur/TRX', 'KL City': 'Kuala Lumpur', 'Bukit Jalil': 'Kuala Lumpur/Bukit Jalil',
             'Petaling Jaya': 'Selangor', 'Penang': 'Penang', 'Johor': 'Johor', 'Melaka': 'Melaka'}

# Project name -> (state, area) where the rules below would get it wrong
OVERRIDE = {'MABA Suitez': ('Kuala Lumpur', 'KL City Centre')}


try:
    ADDED = json.load(open('tools/new_projects/places.json', encoding='utf-8'))  # written by tools/add_projects.py
except (OSError, ValueError):
    ADDED = {}


def place(p):
    if p['name'] in OVERRIDE:
        return OVERRIDE[p['name']]
    if p['name'] in ADDED:
        return tuple(ADDED[p['name']])
    tag, l = p['tag'], p['loc'].lower()
    if tag in ('Bukit Bintang', 'KL City Centre', 'Bukit Jalil'):
        return 'Kuala Lumpur', tag
    if tag == 'TRX & Merdeka Maybank':
        return 'Kuala Lumpur', 'TRX'
    if tag in ('KL City', 'Petaling Jaya'):
        for key, area in [('damansara heights', 'Damansara Heights'), ('bangsar', 'Bangsar'), ('taman desa', 'Taman Desa'),
                          ('jalan ampang', 'KL City Centre')]:
            if key in l:
                return 'Kuala Lumpur', area
        for key, area in [('bandar sri damansara', 'Bandar Sri Damansara'), ('kwasa', 'Kwasa Damansara'), ('subang', 'Subang Jaya'), ('ara damansara', 'Ara Damansara'),
                          ('damansara perdana', 'Damansara Perdana'), ('damansara damai', 'Damansara Damai')]:
            if key in l:
                return 'Selangor', area
        return 'Selangor', 'Petaling Jaya'
    if tag == 'Penang':
        for key, area in [('batu kawan', 'Batu Kawan'), ('gelugor', 'Gelugor'), ('george town', 'George Town'),
                          ('bayan lepas', 'Bayan Lepas'), ('paya terubong', 'Paya Terubong'), ('tanjung bungah', 'Tanjung Bungah')]:
            if key in l:
                return 'Penang', area
        return 'Penang', 'Penang Island'
    if tag == 'Johor':
        return 'Johor', 'Kebun Teh' if 'kebun teh' in l else 'JB City Centre'
    if tag == 'Melaka':
        return 'Melaka', 'Melaka City'
    raise ValueError('No state for %s (%s)' % (p['name'], tag))


UI = {
    'en': {'loc': 'Location', 'all': 'All Malaysia', 'filter': 'Filter by location', 'allof': 'All {s}',
           'show': 'Showing <b>{n}</b> projects in <b>{l}</b>', 'show1': 'Showing <b>1</b> project in <b>{l}</b>',
           'st': {}},
    'zh-CN': {'loc': '地区', 'all': '全马', 'filter': '按地区筛选', 'allof': '全部{s}', 'show': '{l}：共 <b>{n}</b> 个项目', 'show1': '{l}：共 <b>1</b> 个项目',
              'st': {'Kuala Lumpur': '吉隆坡', 'Selangor': '雪兰莪', 'Penang': '槟城', 'Johor': '柔佛', 'Melaka': '马六甲', 'Sabah': '沙巴', 'Terengganu': '登嘉楼', 'Kelantan': '吉兰丹'}},
    'zh-TW': {'loc': '地區', 'all': '全馬', 'filter': '按地區篩選', 'allof': '全部{s}', 'show': '{l}：共 <b>{n}</b> 個項目', 'show1': '{l}：共 <b>1</b> 個項目',
              'st': {'Kuala Lumpur': '吉隆坡', 'Selangor': '雪蘭莪', 'Penang': '檳城', 'Johor': '柔佛', 'Melaka': '馬六甲', 'Sabah': '沙巴', 'Terengganu': '登嘉樓', 'Kelantan': '吉蘭丹'}},
    'ms': {'loc': 'Lokasi', 'all': 'Seluruh Malaysia', 'filter': 'Tapis ikut lokasi', 'allof': 'Semua {s}',
           'show': 'Menunjukkan <b>{n}</b> projek di <b>{l}</b>', 'show1': 'Menunjukkan <b>1</b> projek di <b>{l}</b>',
           'st': {'Penang': 'Pulau Pinang'}},
    'ta': {'loc': 'இடம்', 'all': 'முழு மலேசியா', 'filter': 'இடத்தின்படி வடிகட்டு', 'allof': 'அனைத்து {s}',
           'show': '<b>{l}</b>: <b>{n}</b> திட்டங்கள்', 'show1': '<b>{l}</b>: <b>1</b> திட்டம்',
           'st': {'Kuala Lumpur': 'கோலாலம்பூர்', 'Selangor': 'சிலாங்கூர்', 'Penang': 'பினாங்கு', 'Johor': 'ஜொகூர்', 'Melaka': 'மலாக்கா', 'Sabah': 'சபா', 'Terengganu': 'திரங்கானு', 'Kelantan': 'கிளந்தான்'}},
    'ja': {'loc': 'エリア', 'all': 'マレーシア全域', 'filter': 'エリアで絞り込む', 'allof': '{s}すべて',
           'show': '<b>{l}</b>：<b>{n}</b>件のプロジェクト', 'show1': '<b>{l}</b>：<b>1</b>件のプロジェクト',
           'st': {'Kuala Lumpur': 'クアラルンプール', 'Selangor': 'セランゴール', 'Penang': 'ペナン', 'Johor': 'ジョホール', 'Melaka': 'マラッカ', 'Sabah': 'サバ', 'Terengganu': 'トレンガヌ', 'Kelantan': 'クランタン'}},
    'ko': {'loc': '지역', 'all': '말레이시아 전체', 'filter': '지역별 필터', 'allof': '{s} 전체',
           'show': '<b>{l}</b>: 프로젝트 <b>{n}</b>개', 'show1': '<b>{l}</b>: 프로젝트 <b>1</b>개',
           'st': {'Kuala Lumpur': '쿠알라룸푸르', 'Selangor': '셀랑오르', 'Penang': '페낭', 'Johor': '조호르', 'Melaka': '말라카', 'Sabah': '사바', 'Terengganu': '트렝가누', 'Kelantan': '클란탄'}},
    'ar': {'loc': 'الموقع', 'all': 'كل ماليزيا', 'filter': 'التصفية حسب الموقع', 'allof': 'كل {s}',
           'show': 'عرض <b>{n}</b> مشروعًا في <b>{l}</b>', 'show1': 'عرض مشروع <b>1</b> في <b>{l}</b>',
           'st': {'Kuala Lumpur': 'كوالالمبور', 'Selangor': 'سلانغور', 'Penang': 'بينانغ', 'Johor': 'جوهور', 'Melaka': 'ملاكا', 'Sabah': 'صباح', 'Terengganu': 'ترغكانو', 'Kelantan': 'كلنتن'}},
}
E = lambda s: html.escape(s, quote=True)
PIN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0114 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>'
CHEV = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>'

CSS = '''
/* KN-AREAS:CSS:START */
#projFilters{display:none!important;}
.proj-wrap.kn-areas{display:grid;grid-template-columns:260px minmax(0,1fr);gap:36px;align-items:start;max-width:1320px;}
.proj-wrap.kn-areas > :not(.sb){grid-column:2;}
.sb{grid-column:1;grid-row:1 / span 20;position:sticky;top:96px;}
.sb-toggle{display:none;}
.sb-panel{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 10px 12px;max-height:calc(100vh - 120px);overflow:auto;}
.sb-title{font:700 17px 'Inter',sans-serif;margin:0 10px 10px;color:#111;}
.sb-all,.sb-area{display:flex;justify-content:space-between;align-items:center;gap:10px;width:100%;border:0;background:none;padding:9px 10px;border-radius:8px;font:500 13px 'Inter',sans-serif;color:#444;cursor:pointer;text-align:start;}
.sb-all{font-weight:600;color:#111;padding:10px;}
.sb-all:hover,.sb-area:hover,.sb-head:hover{background:var(--bg);}
.sb-all.active,.sb-area.active{background:#F1F0FB;color:var(--gold);font-weight:700;}
.sb-head{display:flex;align-items:center;gap:8px;width:100%;border:0;background:none;padding:11px 10px;border-radius:8px;cursor:pointer;font:600 13px 'Inter',sans-serif;letter-spacing:.04em;color:#222;text-align:start;}
.sb-chev svg{width:12px;height:12px;color:var(--grey);transition:transform .2s;display:block;}
html[dir=rtl] .sb-chev svg{transform:scaleX(-1);}
.sb-name{flex:1;text-transform:uppercase;} .sb-head em,.sb-all em,.sb-area em{font-style:normal;font-size:11px;color:var(--grey);font-weight:600;}
.sb-plus{width:14px;height:14px;position:relative;flex:0 0 14px;}
.sb-plus::before,.sb-plus::after{content:"";position:absolute;left:0;right:0;top:6px;height:2px;background:#111;border-radius:2px;transition:transform .2s;}
.sb-plus::after{transform:rotate(90deg);}
.sb-state.open .sb-plus::after{transform:rotate(0deg);} .sb-state.open .sb-chev svg{transform:rotate(90deg);}
.sb-state.current > .sb-head{color:var(--gold);}
.sb-areas{display:none;padding:2px 0 8px;padding-inline-start:28px;}
.sb-state.open .sb-areas{display:block;}
.sb-count{grid-column:2;margin:0 0 18px;font:500 13.5px 'Inter',sans-serif;color:var(--grey);}
.sb-count b{color:#111;}
@media(max-width:900px){
  .proj-wrap.kn-areas{display:block;}
  .sb{position:sticky;top:70px;z-index:40;margin:0 0 14px;}
  .sb-toggle{display:flex;align-items:center;gap:10px;width:100%;border:1px solid var(--line);background:#fff;border-radius:12px;padding:13px 16px;font:600 14px 'Inter',sans-serif;color:#111;cursor:pointer;box-shadow:0 6px 18px rgba(17,17,17,.06);}
  .sb-toggle svg{width:16px;height:16px;color:var(--gold);flex:0 0 16px;} .sb-toggle b{margin-inline-start:auto;color:var(--gold);font-weight:700;text-align:end;}
  .sb-panel{display:none;margin-top:8px;max-height:62vh;box-shadow:0 16px 40px rgba(0,0,0,.14);}
  .sb.open .sb-panel{display:block;}
}
/* KN-AREAS:CSS:END */
'''

JS = r'''<!-- KN-AREAS:JS:START -->
<script>
(function(){
  var PLACES = __PLACES__, UI = __UI__, OLD = __OLD__;
  var box = document.getElementById('sbBox'); if(!box) return;
  var cur = ['All', 'All'];
  function L(){ var l = (typeof currentLang !== 'undefined' && currentLang) || document.documentElement.lang || 'en'; return UI[l] || UI.en; }
  function st(s){ return L().st[s] || s; }
  function label(s, a){ return s === 'All' ? L().all : (a === 'All' ? st(s) : st(s) + ' › ' + a); }
  function texts(){
    var u = L();
    box.querySelector('.sb-title').textContent = u.loc;
    box.querySelector('.sb-toggle span').textContent = u.filter;
    box.querySelector('.sb-all span').textContent = u.all;
    box.querySelectorAll('.sb-state').forEach(function(s){ var n = s.getAttribute('data-state');
      s.querySelector('.sb-name').textContent = st(n);
      s.querySelector('.sb-area[data-area="All"] span').textContent = u.allof.replace('{s}', st(n)); });
  }
  function ui(s, a, n){
    cur = [s, a];
    box.querySelector('.sb-all').classList.toggle('active', s === 'All');
    box.querySelectorAll('.sb-state').forEach(function(x){ var me = x.getAttribute('data-state') === s; x.classList.toggle('current', me);
      if(me) x.classList.add('open');
      x.querySelectorAll('.sb-area').forEach(function(b){ b.classList.toggle('active', me && b.getAttribute('data-area') === a); }); });
    document.getElementById('sbCurrent').textContent = label(s, a);
    var c = document.getElementById('sbCount');
    if(n == null){ c.innerHTML = ''; return; }
    var u = L(); c.innerHTML = (n === 1 ? u.show1 : u.show).replace('{n}', n).replace('{l}', label(s, a).replace(/</g, '&lt;'));
  }
  function show(s, a){
    var all = document.querySelector('.proj-filter-btn[data-tag="All"]'); if(all) all.click();  // clears any tag selection
    var n = 0;
    document.querySelectorAll('.proj-card').forEach(function(c){
      var ok = s === 'All' || (c.getAttribute('data-state') === s && (a === 'All' || c.getAttribute('data-area') === a));
      c.style.display = ok ? 'flex' : 'none'; if(ok) n++;
    });
    var e = document.getElementById('projEmpty'); if(e) e.style.display = n ? 'none' : 'block';
    ui(s, a, n);
    var sel = document.getElementById('psArea'); if(sel) sel.value = s === 'All' ? 'All' : (a === 'All' ? s : s + '/' + a);
  }
  window.knShowArea = show;
  box.addEventListener('click', function(e){
    var t;
    if((t = e.target.closest('#sbToggle'))){ box.classList.toggle('open'); return; }
    if((t = e.target.closest('.sb-all'))){ box.querySelectorAll('.sb-state').forEach(function(x){ x.classList.remove('open'); }); show('All', 'All'); box.classList.remove('open'); return; }
    if((t = e.target.closest('.sb-head'))){ var x = t.parentNode; x.classList.toggle('open'); t.setAttribute('aria-expanded', x.classList.contains('open')); return; }
    if((t = e.target.closest('.sb-area'))){ show(t.closest('.sb-state').getAttribute('data-state'), t.getAttribute('data-area')); box.classList.remove('open'); return; }
  });
  document.addEventListener('click', function(e){ if(box.classList.contains('open') && !box.contains(e.target)) box.classList.remove('open'); });
  // Choosing a tag shows projects from every area
  document.addEventListener('click', function(e){ if(e.target.closest('.ptag,#tagSection .ts-opt,#tsClear,.ts-chip')) setTimeout(function(){ ui('All', 'All', null); }, 0); }, true);
  // Links such as projects.html#Selangor/Kwasa%20Damansara or the old #Petaling%20Jaya
  function fromHash(){
    var h = decodeURIComponent((location.hash || '').replace(/^#/, '')); if(!h || h === 'tagSection') return;
    h = OLD[h] || h; var p = h.split('/'), s = p[0], a = p[1] || 'All';
    if(STATES.indexOf(s) < 0) return;
    show(s, a); setTimeout(function(){ document.getElementById('projGrid').scrollIntoView({behavior:'smooth', block:'start'}); }, 150);
  }
  var STATES = __STATES__;
  var f = window.setLanguage; if(typeof f === 'function'){ window.setLanguage = function(){ var r = f.apply(this, arguments); try{ texts(); ui(cur[0], cur[1], cur[0] === 'All' && !document.getElementById('sbCount').innerHTML ? null : visible()); }catch(err){} return r; }; }
  function visible(){ var n = 0; document.querySelectorAll('.proj-card').forEach(function(c){ if(c.style.display !== 'none') n++; }); return n; }
  texts(); ui('All', 'All', null);
  window.addEventListener('hashchange', fromHash); setTimeout(fromHash, 50);
})();
</script>
<!-- KN-AREAS:JS:END -->
'''


def sort_key(name):
    return re.sub(r'[^a-z0-9 ]', '', name.lower())


def sort_cards(text, card_open, grid_start, grid_end, P):
    """Reorder the cards between grid_start and grid_end by project name."""
    g = text.index(grid_start) + len(grid_start)
    e = text.index(grid_end, g)
    body = text[g:e]
    starts = [m.start() for m in re.finditer(card_open, body)]
    lead = body[:starts[0]]
    blocks = [body[a:b] for a, b in zip(starts, starts[1:] + [len(body)])]
    tail = ''
    if not blocks[-1].endswith('\n'):
        pass
    blocks = [b if b.endswith('\n') else b + '\n' for b in blocks]
    idx = lambda b: int(re.search(r'data-idx="(\d+)"', b).group(1))
    blocks.sort(key=lambda b: sort_key(P[idx(b)]['name']))
    out = lead + ''.join(blocks)
    if not body.endswith('\n'):
        out = out.rstrip('\n')
    return text[:g] + out + text[e:]


def main():
    src = open(PAGE, encoding='utf-8').read()
    i = src.index('const PROJECT_DETAILS = ') + len('const PROJECT_DETAILS = ')
    P = json.JSONDecoder().raw_decode(src[i:])[0]
    places = [list(place(p)) for p in P]
    tree = OrderedDict((s, {}) for s in STATES)
    for s, a in places:
        tree[s][a] = tree[s].get(a, 0) + 1
    for s in tree:
        tree[s] = OrderedDict(sorted(tree[s].items(), key=lambda kv: (-kv[1], kv[0])))

    # 1) Cards: data-state, data-area and the label
    def card(m):
        k = int(m.group(2))
        s, a = places[k]
        head = re.sub(r' data-state="[^"]*" data-area="[^"]*"', '', m.group(0))
        return head.replace(' data-idx="%d"' % k, ' data-state="%s" data-area="%s" data-idx="%d"' % (E(s), E(a), k), 1)
    src, n = re.subn(r'<div class="proj-card" data-tag="([^"]*)"(?: data-state="[^"]*" data-area="[^"]*")? data-idx="(\d+)"', card, src)
    assert n == len(P), n

    def lab(m):
        k = int(m.group(1))
        return re.sub(r'<span class="proj-tag">.*?</span>', '<span class="proj-tag">%s</span>' % E(places[k][1]), m.group(0), count=1)
    src, n = re.subn(r'data-idx="(\d+)" onclick="openDetailModal\(\1\)">.*?<span class="proj-tag">.*?</span>', lab, src, flags=re.S)
    assert n == len(P), n

    # 1b) Cards in alphabetical order (View Projects and Compare)
    src = sort_cards(src, r'<div class="proj-card"', '<div class="proj-grid" id="projGrid">', '  </div></div>\n  </div>', P)
    cmp = open('compare.html', encoding='utf-8').read()
    cmp = sort_cards(cmp, r'<div class="cmp-card"', '<div class="cmp-grid" id="cmpGrid">\n', '  </div>\n    <div class="cmp-empty"', P)
    open('compare.html', 'w', encoding='utf-8').write(cmp)

    # 2) The Location list
    acc = '<button type="button" class="sb-all active"><span>All Malaysia</span><em>%d</em></button>' % len(P)
    for s in STATES:
        acc += ('<div class="sb-state" data-state="%s"><button type="button" class="sb-head" aria-expanded="false">'
                '<span class="sb-chev">%s</span><span class="sb-name">%s</span><em>%d</em><span class="sb-plus" aria-hidden="true"></span></button>'
                '<div class="sb-areas"><button type="button" class="sb-area" data-area="All"><span>All %s</span></button>%s</div></div>') % (
            E(s), CHEV, E(s), sum(tree[s].values()), E(s),
            ''.join('<button type="button" class="sb-area" data-area="%s"><span>%s</span><em>%d</em></button>' % (E(a), E(a), c) for a, c in tree[s].items()))
    side = ('<!-- KN-AREAS:SIDE:START --><aside class="sb" id="sbBox"><button type="button" class="sb-toggle" id="sbToggle">%s<span>Filter by location</span>'
            '<b id="sbCurrent">All Malaysia</b></button><div class="sb-panel"><p class="sb-title">Location</p>%s</div></aside>'
            '<p class="sb-count" id="sbCount" aria-live="polite"></p><!-- KN-AREAS:SIDE:END -->') % (PIN, acc)
    src = re.sub(r'  <!-- KN-AREAS:SIDE:START -->.*?<!-- KN-AREAS:SIDE:END -->\n', '', src, flags=re.S)
    src = re.sub(r'<div class="proj-wrap(?: kn-areas)?">\n', lambda _: '<div class="proj-wrap kn-areas">\n  ' + side + '\n', src, count=1)

    # 3) Area box in the search form: states and their areas
    opts = '<option value="All">Anywhere</option>' + ''.join(
        '<optgroup label="%s"><option value="%s">All %s</option>%s</optgroup>' % (
            E(s), E(s), E(s), ''.join('<option value="%s/%s">%s</option>' % (E(s), E(a), E(a)) for a in tree[s])) for s in STATES)
    src, n = re.subn(r'(<select id="psArea">).*?(</select>)', lambda m: m.group(1) + opts + m.group(2), src, count=1, flags=re.S)
    assert n == 1
    old = "if(area!=='All'&&p.tag!==area)continue;"
    new = "if(area!=='All'){var kp=(window.KN_PLACES||[])[i]||[];if(area.indexOf('/')<0?kp[0]!==area:(kp[0]+'/'+kp[1])!==area)continue;}"
    src = src.replace(old, new)
    assert new in src
    old = "      setArea(area);\n"
    new = "      if(window.knShowArea){var pa=area.split('/');window.knShowArea(area==='All'?'All':pa[0],pa[1]||'All');}else setArea(area);\n"
    src = src.replace(old, new)
    assert new in src

    # 4) CSS and script
    src = re.sub(r'\n/\* KN-AREAS:CSS:START \*/.*?/\* KN-AREAS:CSS:END \*/\n', '', src, flags=re.S)
    src = src.replace('</style>', CSS + '</style>', 1)
    src = re.sub(r'<!-- KN-AREAS:JS:START -->.*?<!-- KN-AREAS:JS:END -->\n', '', src, flags=re.S)
    js = (JS.replace('__PLACES__', json.dumps(places, ensure_ascii=False)).replace('__UI__', json.dumps(UI, ensure_ascii=False))
          .replace('__OLD__', json.dumps(OLD_LINKS)).replace('__STATES__', json.dumps(STATES)))
    js = js.replace('<script>\n(function(){', '<script>\nwindow.KN_PLACES = %s;\n(function(){' % json.dumps(places, ensure_ascii=False), 1)
    src = src.replace('<script src="lead-tracker.js"></script>', js + '<script src="lead-tracker.js"></script>', 1)
    open(PAGE, 'w', encoding='utf-8').write(src)
    json.dump(places, open('tools/project_places.json', 'w', encoding='utf-8'), ensure_ascii=False)
    for s in STATES:
        print(s, sum(tree[s].values()), dict(tree[s]))


if __name__ == '__main__':
    main()
