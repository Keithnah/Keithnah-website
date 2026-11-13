"""View Projects layout helpers on projects.html (idempotent):

1. KL zones in the location filter: City Centre / West / South / North & East, each with a count.
2. When a state (or KL zone) is chosen, the grid is split into sections per area, each showing the
   first few projects and a "Show all" button plus a link to the area page.
4. Sort: A-Z (default), price low-high, price high-low, completion (earliest first).
5. Mobile: a sticky row of location chips that scrolls sideways, and "Show more" after 12 projects.
6. The project map zooms to the chosen state, zone or area.

Everything runs in the browser on top of the existing cards; the cards stay in A-Z order in the HTML.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# KL areas by zone. Areas not listed fall into "Other areas".
ZONES = [
    ('centre', ['KL City Centre', 'Bukit Bintang', 'TRX', 'Chow Kit', 'Titiwangsa', 'Jalan Ipoh', 'Pudu', 'Imbi']),
    ('west', ['Bangsar', 'Bangsar South', 'Damansara Heights', 'Mont Kiara', 'Sri Hartamas', 'Desa ParkCity', 'Segambut', 'Kepong', 'Bukit Tunku']),
    ('south', ['Bukit Jalil', 'Taman Desa', 'Kuchai Lama', 'OUG', 'Sri Petaling', 'Seputeh', 'Mid Valley', 'Old Klang Road', 'Sungai Besi']),
    ('ne', ['Ampang', 'Cheras', 'Setapak', 'Wangsa Maju', 'Sentul', 'Jalan Kuching', 'Taman Melawati']),
]

T = {
    'en': {'centre': 'City Centre', 'west': 'West KL', 'south': 'South KL', 'ne': 'North & East KL', 'other': 'Other areas',
           'sort': 'Sort by', 'az': 'Name (A–Z)', 'plh': 'Price: low to high', 'phl': 'Price: high to low', 'comp': 'Completion: soonest first',
           'all': 'Show all {n}', 'less': 'Show fewer', 'more': 'Show more ({n} left)', 'guide': 'Area guide →', 'n1': '1 project', 'n': '{n} projects',
           'allm': 'All Malaysia', 'zone': 'Zones'},
    'zh-CN': {'centre': '市中心', 'west': '吉隆坡西区', 'south': '吉隆坡南区', 'ne': '吉隆坡东北区', 'other': '其他地区',
              'sort': '排序', 'az': '名称（A–Z）', 'plh': '价格：低到高', 'phl': '价格：高到低', 'comp': '完工：最早的在前',
              'all': '查看全部 {n} 个', 'less': '收起', 'more': '显示更多（还有 {n} 个）', 'guide': '地区指南 →', 'n1': '1 个项目', 'n': '{n} 个项目',
              'allm': '全马来西亚', 'zone': '分区'},
    'ms': {'centre': 'Pusat Bandar', 'west': 'KL Barat', 'south': 'KL Selatan', 'ne': 'KL Utara & Timur', 'other': 'Kawasan lain',
           'sort': 'Susun ikut', 'az': 'Nama (A–Z)', 'plh': 'Harga: rendah ke tinggi', 'phl': 'Harga: tinggi ke rendah', 'comp': 'Siap: paling awal dahulu',
           'all': 'Lihat semua {n}', 'less': 'Tunjuk kurang', 'more': 'Tunjuk lagi ({n} lagi)', 'guide': 'Panduan kawasan →', 'n1': '1 projek', 'n': '{n} projek',
           'allm': 'Seluruh Malaysia', 'zone': 'Zon'},
    'ja': {'centre': '都心部', 'west': 'KL 西部', 'south': 'KL 南部', 'ne': 'KL 北部・東部', 'other': 'その他のエリア',
           'sort': '並べ替え', 'az': '名前（A–Z）', 'plh': '価格：安い順', 'phl': '価格：高い順', 'comp': '完成：早い順',
           'all': 'すべて表示（{n}件）', 'less': '閉じる', 'more': 'さらに表示（残り{n}件）', 'guide': 'エリアガイド →', 'n1': '1件', 'n': '{n}件',
           'allm': 'マレーシア全体', 'zone': 'エリア区分'},
    'ko': {'centre': '도심', 'west': 'KL 서부', 'south': 'KL 남부', 'ne': 'KL 북부·동부', 'other': '기타 지역',
           'sort': '정렬', 'az': '이름 (A–Z)', 'plh': '가격: 낮은 순', 'phl': '가격: 높은 순', 'comp': '완공: 빠른 순',
           'all': '전체 보기 ({n}개)', 'less': '접기', 'more': '더 보기 ({n}개 남음)', 'guide': '지역 가이드 →', 'n1': '프로젝트 1개', 'n': '프로젝트 {n}개',
           'allm': '말레이시아 전체', 'zone': '구역'},
}
import opencc
_cc = opencc.OpenCC('s2tw').convert
T['zh-TW'] = {k: _cc(v) for k, v in T['zh-CN'].items()}

CSS = r'''
.sb-zone{display:flex;justify-content:space-between;align-items:center;gap:10px;width:100%;border:0;background:none;padding:9px 10px;margin-top:4px;border-radius:8px;font:700 12.5px 'Inter',sans-serif;color:#111;cursor:pointer;text-align:start;letter-spacing:.02em}
.sb-zone em{font-style:normal;font-size:11px;color:var(--grey);font-weight:600}
.sb-zone:hover{background:var(--bg)}.sb-zone.active{background:#F1F0FB;color:var(--gold)}
.sb-zg .sb-area{padding-inline-start:22px}
.pl-bar{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px 16px;margin:0 0 20px;font:500 13px 'Inter',sans-serif;color:var(--grey)}
.pl-bar .sb-count{margin:0}.pl-bar label{margin-inline-start:auto;white-space:nowrap}.pl-bar select{font:600 13px 'Inter',sans-serif;color:#111;border:1px solid var(--line);border-radius:10px;padding:8px 30px 8px 12px;background:#fff;cursor:pointer}
.pl-h{grid-column:1/-1;display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:14px 0 -8px;padding-bottom:10px;border-bottom:1px solid var(--line)}
.pl-h:first-child{margin-top:0}
.pl-h h3{font:700 clamp(20px,2.2vw,26px) 'Playfair Display',Georgia,serif;margin:0;color:#111}
.pl-h h3 small{font:600 12.5px 'Inter',sans-serif;color:var(--grey);margin-inline-start:10px;letter-spacing:.02em}
.pl-h h3 i{font:700 10.5px 'Inter',sans-serif;font-style:normal;text-transform:uppercase;letter-spacing:.12em;color:var(--gold);display:block;margin-bottom:4px}
.pl-h a{font:600 13px 'Inter',sans-serif;color:var(--gold)}.pl-h a:hover{text-decoration:underline}
.pl-x{grid-column:1/-1;display:flex;justify-content:center;margin:-4px 0 8px}
.pl-x button,.pl-more button{border:1.5px solid var(--gold);background:#fff;color:var(--gold);font:700 13.5px 'Inter',sans-serif;padding:11px 22px;border-radius:999px;cursor:pointer}
.pl-x button:hover,.pl-more button:hover{background:var(--gold);color:#fff}
.pl-more{display:flex;justify-content:center;margin:26px 0 0}
.proj-card.pl-hide{display:none!important}
.pl-chips{display:none}
@media(max-width:900px){
  .sb{display:none!important}
  .pl-chips{display:block;position:sticky;top:70px;z-index:40;background:var(--bg,#fafaf7);margin:0 -16px 12px;padding:10px 0 8px;box-shadow:0 8px 14px -12px rgba(0,0,0,.25)}
  .pl-row{display:flex;gap:8px;overflow-x:auto;padding:0 16px;scrollbar-width:none;-webkit-overflow-scrolling:touch}
  .pl-row::-webkit-scrollbar{display:none}
  .pl-row+.pl-row{margin-top:8px}
  .pl-c{flex:0 0 auto;border:1px solid var(--line);background:#fff;color:#222;font:600 13px 'Inter',sans-serif;padding:8px 14px;border-radius:999px;white-space:nowrap;cursor:pointer}
  .pl-c em{font-style:normal;font-size:11px;color:var(--grey);margin-inline-start:6px}
  .pl-c.z{border-style:dashed}
  .pl-c.on{background:var(--gold);border-color:var(--gold);color:#fff}.pl-c.on em{color:rgba(255,255,255,.8)}
  .pl-bar{margin:0 0 14px}
  .pl-h{margin-top:8px}
}
'''

JS = r'''(function(){
var ZONES=%(zones)s,T=%(t)s;
var box=document.getElementById('sbBox'),grid=document.getElementById('projGrid');if(!box||!grid)return;
document.querySelectorAll('.sb-zg').forEach(function(g){g.querySelectorAll('.sb-area').forEach(function(b){g.parentNode.insertBefore(b,g);});g.remove();});
var oc=document.querySelector('.pl-bar #sbCount');if(oc){var ob=oc.parentNode;ob.parentNode.insertBefore(oc,ob);}
document.querySelectorAll('[data-pl],.pl-h,.pl-x').forEach(function(x){x.remove();});
grid.querySelectorAll('.pl-hide').forEach(function(c){c.classList.remove('pl-hide');});
var KL='Kuala Lumpur',ZOF={};ZONES.forEach(function(z){z[1].forEach(function(a){ZOF[a]=z[0];});});
function zoneOf(a){return ZOF[a]||'other';}
function lg(){var l='en';try{l=localStorage.getItem('kn_lang')||document.documentElement.lang||'en'}catch(e){}return T[l]?l:'en';}
function t(k,n){var s=(T[lg()][k]||T.en[k]);return n==null?s:s.replace('{n}',n);}
function slug(x){return x.toLowerCase().replace(/&/g,'and').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');}
var LP=(location.pathname.match(/^\/(zh-tw|zh|ms|ja|ko)\//)||[,''])[1],root=LP?'/'+LP+'/':'';
var cards=[].slice.call(grid.querySelectorAll('.proj-card'));
var ORDER=cards.slice();
var MOB=function(){return window.matchMedia('(max-width:900px)').matches;};
function D(c){var P=typeof PROJECT_DETAILS!=='undefined'?PROJECT_DETAILS:null;return (P&&P[+c.getAttribute('data-idx')])||{};}
function price(c){var p=String(D(c).price||''),m=p.replace(/,/g,'').match(/RM\s*([\d.]+)\s*(mil|million|m|k)?/i);if(!m)return null;var v=parseFloat(m[1]),u=(m[2]||'').toLowerCase();if(u==='k')v*=1e3;else if(u)v*=1e6;return v;}
function comp(c){var s=String(D(c).completion||'');if(/^completed/i.test(s))return 0;var y=s.match(/\b(20[2-4]\d)\b/);if(!y)return null;var q=s.match(/Q([1-4])\s*20/i),mo=s.match(/\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+20/i);
var f=q?(+q[1]-1)/4:(mo?'janfebmaraprmayjunjulaugsepoctnovdec'.indexOf(mo[1].toLowerCase())/36:0.99);return +y[1]+f;}
/* ---------- 1. KL zones in the side filter ---------- */
var klBox=box.querySelector('.sb-state[data-state="'+KL+'"] .sb-areas');
if(klBox){var allBtn=klBox.querySelector('.sb-area[data-area="All"]'),guide=klBox.querySelector('.sb-guide'),groups={};
  klBox.querySelectorAll('.sb-area:not([data-area="All"])').forEach(function(b){var z=zoneOf(b.getAttribute('data-area'));(groups[z]=groups[z]||[]).push(b);});
  ZONES.map(function(z){return z[0];}).concat(['other']).forEach(function(z){if(!groups[z])return;
    var g=document.createElement('div');g.className='sb-zg';g.setAttribute('data-pl','');g.setAttribute('data-zone',z);
    var n=groups[z].reduce(function(s,b){return s+(+(b.querySelector('em')||{}).textContent||0);},0);
    var zb=document.createElement('button');zb.type='button';zb.className='sb-zone';zb.setAttribute('data-zone',z);zb.innerHTML='<span></span><em>'+n+'</em>';g.appendChild(zb);
    groups[z].forEach(function(b){g.appendChild(b);});klBox.insertBefore(g,guide||null);});
  if(allBtn)klBox.insertBefore(allBtn,klBox.firstChild);}
/* ---------- state ---------- */
var S={s:'All',a:'All',z:null,sort:'az',open:{},shown:12};
function readSide(){var cur=box.querySelector('.sb-state.current');if(!cur||box.querySelector('.sb-all.active'))return ['All','All'];var a=cur.querySelector('.sb-area.active');return [cur.getAttribute('data-state'),a?a.getAttribute('data-area'):'All'];}
function visible(){return cards.filter(function(c){return c.style.display!=='none';});}
/* ---------- 4. sort bar ---------- */
var bar=document.createElement('div');bar.className='pl-bar';bar.setAttribute('data-pl','');
bar.innerHTML='<label><span></span> <select><option value="az"></option><option value="plh"></option><option value="phl"></option><option value="comp"></option></select></label>';
var sel=bar.querySelector('select'),cnt=document.getElementById('sbCount');if(cnt){cnt.parentNode.insertBefore(bar,cnt);bar.insertBefore(cnt,bar.firstChild);}else grid.parentNode.insertBefore(bar,grid);
sel.addEventListener('change',function(){S.sort=sel.value;S.shown=12;layout();});
function sorted(list){if(S.sort==='az')return list.slice().sort(function(a,b){return ORDER.indexOf(a)-ORDER.indexOf(b);});
  var f=S.sort==='comp'?comp:price,dir=S.sort==='phl'?-1:1;
  return list.slice().sort(function(a,b){var x=f(a),y=f(b);if(x==null&&y==null)return ORDER.indexOf(a)-ORDER.indexOf(b);if(x==null)return 1;if(y==null)return -1;return x===y?ORDER.indexOf(a)-ORDER.indexOf(b):(x-y)*dir;});}
/* ---------- 5. mobile chips ---------- */
var chips=document.createElement('div');chips.className='pl-chips';chips.setAttribute('data-pl','');box.parentNode.insertBefore(chips,box);
function chip(label,n,on,act,extra){return '<button type="button" class="pl-c'+(on?' on':'')+(extra||'')+'" data-act="'+act+'">'+label+(n!=null?'<em>'+n+'</em>':'')+'</button>';}
function drawChips(){var st=[].slice.call(box.querySelectorAll('.sb-state')),h='<div class="pl-row">'+chip(t('allm'),cards.length,S.s==='All','all|');
  st.forEach(function(x){var s=x.getAttribute('data-state');h+=chip(x.querySelector('.sb-name').textContent,(x.querySelector('.sb-head em')||{}).textContent,S.s===s,'state|'+s);});h+='</div>';
  if(S.s!=='All'){var x=box.querySelector('.sb-state[data-state="'+S.s+'"]');if(x){h+='<div class="pl-row">'+chip(x.querySelector('.sb-area[data-area="All"] span').textContent,null,S.a==='All'&&!S.z,'state|'+S.s);
    x.querySelectorAll('.sb-zone').forEach(function(z){h+=chip(t(z.getAttribute('data-zone')),z.querySelector('em').textContent,S.z===z.getAttribute('data-zone'),'zone|'+z.getAttribute('data-zone'),' z');});
    x.querySelectorAll('.sb-area:not([data-area="All"])').forEach(function(b){var a=b.getAttribute('data-area');h+=chip(a,(b.querySelector('em')||{}).textContent,S.a===a,'area|'+a);});h+='</div>';}}
  chips.innerHTML=h;var on=chips.querySelectorAll('.pl-c.on');on.forEach(function(c){var r=c.parentNode;r.scrollLeft=Math.max(0,c.offsetLeft-r.offsetWidth/2+c.offsetWidth/2);});}
chips.addEventListener('click',function(e){var b=e.target.closest('.pl-c');if(!b)return;var p=b.getAttribute('data-act').split('|');
  if(p[0]==='all')box.querySelector('.sb-all').click();
  else if(p[0]==='state')box.querySelector('.sb-state[data-state="'+p[1]+'"] .sb-area[data-area="All"]').click();
  else if(p[0]==='area')box.querySelector('.sb-state[data-state="'+S.s+'"] .sb-area[data-area="'+p[1].replace(/"/g,'\\"')+'"]').click();
  else if(p[0]==='zone')showZone(p[1]);
  setTimeout(function(){var y=grid.getBoundingClientRect().top+window.pageYOffset-150;if(window.pageYOffset>y)window.scrollTo({top:y,behavior:'smooth'});},30);});
/* ---------- zone filter ---------- */
function showZone(z){if(typeof window.knShowArea==='function')window.knShowArea(KL,'All');var n=0;
  cards.forEach(function(c){var ok=c.getAttribute('data-state')===KL&&zoneOf(c.getAttribute('data-area'))===z;c.style.display=ok?'flex':'none';if(ok)n++;});
  box.querySelectorAll('.sb-area').forEach(function(b){b.classList.remove('active');});
  box.querySelectorAll('.sb-zone').forEach(function(b){b.classList.toggle('active',b.getAttribute('data-zone')===z);});
  var cur=document.getElementById('sbCurrent');if(cur)cur.textContent=(box.querySelector('.sb-state[data-state="'+KL+'"] .sb-name')||{}).textContent+' › '+t(z);
  var c=document.getElementById('sbCount');if(c)c.textContent=(n===1?t('n1'):t('n',n))+' · '+t(z);
  S.s=KL;S.a='All';S.z=z;S.open={};S.shown=12;layout();}
/* ---------- 2. sections per area + 5. show more + 6. map ---------- */
function clear(){grid.querySelectorAll('.pl-h,.pl-x').forEach(function(x){x.remove();});cards.forEach(function(c){c.classList.remove('pl-hide');});var m=document.querySelector('.pl-more');if(m)m.remove();}
function layout(){clear();var vis=visible(),lim=MOB()?4:6;
  if(S.s!=='All'&&S.a==='All'&&vis.length){var by={},areas=[];vis.forEach(function(c){var a=c.getAttribute('data-area');if(!by[a]){by[a]=[];areas.push(a);}by[a].push(c);});
    var zi=function(a){var z=zoneOf(a),i=ZONES.map(function(q){return q[0];}).indexOf(z);return S.s===KL?(i<0?9:i):0;};
    areas.sort(function(a,b){return zi(a)-zi(b)||by[b].length-by[a].length||(a<b?-1:1);});
    if(areas.length>1){var frag=document.createDocumentFragment(),lastZ=null;
      areas.forEach(function(a){var list=sorted(by[a]),z=S.s===KL?zoneOf(a):null,h=document.createElement('div');h.className='pl-h';
        h.innerHTML='<h3>'+(z&&z!==lastZ&&!S.z?'<i>'+t(z)+'</i>':'')+a.replace(/</g,'&lt;')+'<small>'+(list.length===1?t('n1'):t('n',list.length))+'</small></h3><a href="'+root+'area/'+slug(a)+'.html">'+t('guide')+'</a>';lastZ=z;
        frag.appendChild(h);list.forEach(function(c,i){if(i>=lim&&!S.open[a])c.classList.add('pl-hide');frag.appendChild(c);});
        if(list.length>lim){var x=document.createElement('div');x.className='pl-x';x.innerHTML='<button type="button">'+(S.open[a]?t('less'):t('all',list.length))+'</button>';
          x.firstChild.onclick=function(){S.open[a]=!S.open[a];layout();if(!S.open[a])h.scrollIntoView({behavior:'smooth',block:'start'});};frag.appendChild(x);}});
      cards.filter(function(c){return vis.indexOf(c)<0;}).forEach(function(c){frag.appendChild(c);});grid.appendChild(frag);drawChips();zoom(vis);return;}}
  var frag2=document.createDocumentFragment(),list2=sorted(vis);list2.forEach(function(c){frag2.appendChild(c);});
  cards.filter(function(c){return vis.indexOf(c)<0;}).forEach(function(c){frag2.appendChild(c);});grid.appendChild(frag2);
  if(MOB()&&list2.length>S.shown){list2.forEach(function(c,i){if(i>=S.shown)c.classList.add('pl-hide');});
    var m=document.createElement('div');m.className='pl-more';m.setAttribute('data-pl','');m.innerHTML='<button type="button">'+t('more',list2.length-S.shown)+'</button>';
    m.firstChild.onclick=function(){S.shown+=12;layout();};grid.parentNode.insertBefore(m,grid.nextSibling);}
  drawChips();zoom(S.s==='All'?null:vis);}
var lastZoom='';
function zoom(vis){var m=window.KN_MAP,P=window.KN_MAP_P;if(!m||!P||!window.L)return;var b=[];
  if(vis){var names={};vis.forEach(function(c){var n=c.querySelector('h3');if(n)names[n.textContent.trim()]=1;});P.forEach(function(p){if(names[p.n])b.push([p.lat,p.lng]);});}
  else P.forEach(function(p){b.push([p.lat,p.lng]);});
  var key=JSON.stringify(b);if(!b.length||key===lastZoom)return;lastZoom=key;
  try{if(b.length===1)m.setView(b[0],15);else m.fitBounds(b,{padding:[40,40],maxZoom:15});}catch(e){}}
/* ---------- hooks ---------- */
function sync(){var r=readSide();S.s=r[0];S.a=r[1];S.z=null;S.open={};S.shown=12;box.querySelectorAll('.sb-zone').forEach(function(b){b.classList.remove('active');});layout();}
box.addEventListener('click',function(e){var z=e.target.closest('.sb-zone');if(z){showZone(z.getAttribute('data-zone'));box.classList.remove('open');return;}
  if(e.target.closest('.sb-all,.sb-area'))setTimeout(sync,0);});
document.addEventListener('click',function(e){if(e.target.closest('.ptag,#tagSection .ts-opt,#tsClear,.ts-chip,#psGo'))setTimeout(function(){S.s='All';S.a='All';S.z=null;S.shown=12;layout();},10);},true);
function hashZone(){var h='';try{h=decodeURIComponent((location.hash||'').slice(1));}catch(e){}var m=h.match(/^Kuala Lumpur\/zone:(\w+)$/);if(!m)return false;showZone(m[1]);setTimeout(function(){grid.scrollIntoView({behavior:'smooth',block:'start'});},80);return true;}
window.addEventListener('hashchange',function(){setTimeout(function(){if(!hashZone())sync();},120);});
function texts(){bar.querySelector('span').textContent=t('sort');['az','plh','phl','comp'].forEach(function(k,i){sel.options[i].textContent=t(k);});
  box.querySelectorAll('.sb-zone').forEach(function(b){b.querySelector('span').textContent=t(b.getAttribute('data-zone'));});}
['setLanguage','knSetLang'].forEach(function(fn){var f=window[fn];if(typeof f==='function')window[fn]=function(){var r=f.apply(this,arguments);try{texts();if(S.z)showZone(S.z);else layout();}catch(err){}return r;};});
var mq=window.matchMedia('(max-width:900px)');if(mq.addEventListener)mq.addEventListener('change',function(){layout();});
texts();setTimeout(function(){if(!hashZone())sync();},150);
})();'''


def main():
    p = 'projects.html'
    s = open(p, encoding='utf-8').read()
    # Let the layout script reach the project map (the map block is rebuilt by build_area_pages.py)
    m = re.search(r'<!-- KN-MAP:START -->.*?<!-- KN-MAP:END -->', s, re.S)
    assert m, 'map block missing'
    blk = m.group(0)
    if 'window.KN_MAP=m' not in blk:
        blk2 = re.sub(r'(var m=L\.map\("kmap",\{[^}]*\}\);)', r'\1window.KN_MAP=m;window.KN_MAP_P=P;', blk, count=1)
        assert blk2 != blk, 'map init not found'
        s = s.replace(blk, blk2, 1)
    s = re.sub(r'<!-- KN-PLAY:START -->.*?<!-- KN-PLAY:END -->\n?', '', s, flags=re.S)
    js = JS % {'zones': json.dumps(ZONES), 't': json.dumps(T, ensure_ascii=False)}
    block = '<!-- KN-PLAY:START --><style>%s</style><script>%s</script><!-- KN-PLAY:END -->\n' % (CSS.strip(), js)
    i = s.index('<!-- KN-AREAS:JS:END -->') + len('<!-- KN-AREAS:JS:END -->\n')
    s = s[:i] + block + s[i:]
    open(p, 'w', encoding='utf-8').write(s)
    print('projects layout: %d KL zones, sort, sections, mobile chips, map zoom' % len(ZONES))


if __name__ == '__main__':
    main()
