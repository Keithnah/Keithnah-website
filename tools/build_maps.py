"""map.html (every project on one map) and station-map.html (projects around each rail station).

Data: the project map data in projects.html (KN-MAP block, written by build_area_pages.py), states from
tools/project_index.json and rail stations from tools/stations.json. Page tops use kn_hero.py.
Distances are straight lines; the walk time is an estimate (distance x 1.3 at 80 m a minute)."""
import html
import json
import os
import re
import sys
from urllib.parse import quote_plus

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
sys.path.insert(0, HERE)
import kn_hero as K  # noqa: E402
import site_header as SH  # noqa: E402

E = lambda s: html.escape(str(s), quote=True)
L = K.L
SITE = 'https://keithnah.com/'
WA = 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0'

t = open('projects.html', encoding='utf-8').read()
m = re.search(r'<!-- KN-MAP:START -->.*?var P=', t, re.S)
P, _ = json.JSONDecoder().raw_decode(t[m.end():])
IDX = {p['name']: p for p in json.load(open(os.path.join(HERE, 'project_index.json'), encoding='utf-8'))}
for p in P:
    p['st'] = (IDX.get(p['n']) or {}).get('state', '')
    mm = re.search(r'([\d.]+)\s*([MK])', p.get('p') or '')
    p['v'] = round(float(mm.group(1)) * (1e6 if mm.group(2) == 'M' else 1e3)) if mm else 0
ST = json.load(open(os.path.join(HERE, 'stations.json'), encoding='utf-8'))['stations']
GUIDES = {}
for f in sorted(os.listdir('station')):
    if f.endswith('.html') and f != 'index.html':
        GUIDES[f[:-5]] = 'station/' + f
for s in ST:
    key = re.sub(r'[^a-z0-9]+', '-', s['n'].lower()).strip('-')
    g = next((v for k, v in GUIDES.items() if k.startswith(key + '-')), '')
    if g:
        s['g'] = g
import math


def _d(a, b, c, d):
    x, y = math.radians(c - a), math.radians(d - b)
    h = math.sin(x / 2) ** 2 + math.cos(math.radians(a)) * math.cos(math.radians(c)) * math.sin(y / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


N_1KM = sum(1 for p in P if any(_d(p['lat'], p['lng'], s['lat'], s['lng']) <= 1000 for s in ST))
LC = {'MRT': '#0b8f6b', 'LRT': '#e8590c', 'Monorail': '#6aa531', 'KTM': '#2563eb', 'RTS': '#9333ea'}

UI = {
    'search_p': L('Search a project, area or state', '搜索项目、地区或州属', 'Cari projek, kawasan atau negeri', '物件・エリア・州で検索', '프로젝트, 지역, 주 검색'),
    'all_states': L('All states', '全部州属', 'Semua negeri', 'すべての州', '전체 주'),
    'any_status': L('Any status', '全部状态', 'Semua status', 'すべての状況', '전체 상태'),
    'any_price': L('Any price', '任何价格', 'Semua harga', 'すべての価格', '전체 가격'),
    'p_a': L('Under RM500k', 'RM50 万以下', 'Bawah RM500k', 'RM50万未満', 'RM50만 미만'),
    'p_b': L('RM500k – 1M', 'RM50 万至 100 万', 'RM500k – 1J', 'RM50万〜100万', 'RM50만~100만'),
    'p_c': L('Above RM1M', 'RM100 万以上', 'Atas RM1J', 'RM100万以上', 'RM100만 이상'),
    'shown': L('projects shown', '个项目', 'projek dipaparkan', '件を表示', '개 프로젝트 표시'),
    'fit': L('Fit all', '显示全部', 'Tunjuk semua', '全体を表示', '전체 보기'),
    'me': L('Near me', '我附近', 'Berhampiran saya', '現在地周辺', '내 주변'),
    'rail': L('Stations', '车站', 'Stesen', '駅', '역'),
    'from': L('From', '起价', 'Dari', '価格', '시작가'),
    'por': L('Price on request', '价格请询问', 'Harga atas permintaan', '価格はお問い合わせ', '가격 문의'),
    'view': L('View project →', '查看项目 →', 'Lihat projek →', '物件を見る →', '프로젝트 보기 →'),
    'nearest': L('Nearest stations', '最近的车站', 'Stesen terdekat', '最寄り駅', '가까운 역'),
    'by_state': L('Browse by state', '按州属浏览', 'Lihat mengikut negeri', '州別に見る', '주별 보기'),
    'projs': L('projects', '个项目', 'projek', '件', '개 프로젝트'),
    'all_st': L('All stations', '全部车站', 'Semua stesen', 'すべての駅', '전체 역'),
    'all_lines': L('All lines', '全部路线', 'Semua laluan', 'すべての路線', '전체 노선'),
    'search_s': L('Search a station or project', '搜索车站或项目', 'Cari stesen atau projek', '駅・物件で検索', '역 또는 프로젝트 검색'),
    'within': L('projects within {r}, straight line', '个项目在 {r} 内（直线距离）', 'projek dalam {r}, garis lurus', '件（{r} 以内・直線距離）', '개 프로젝트 ({r} 이내, 직선거리)'),
    'walk': L('about {m} min walk', '步行约 {m} 分钟', 'kira-kira {m} min berjalan', '徒歩約 {m} 分', '도보 약 {m}분'),
    'none': L('No projects in this range yet. Try a wider circle.', '这个范围内暂时没有项目，试试更大的范围。', 'Belum ada projek dalam julat ini. Cuba bulatan lebih besar.', 'この範囲にはまだ物件がありません。範囲を広げてください。', '이 범위에는 아직 프로젝트가 없습니다. 범위를 넓혀 보세요.'),
    'station': L('station', '站', 'stesen', '駅', '역'),
    'guide': L('Station guide →', '车站指南 →', 'Panduan stesen →', '駅ガイド →', '역 가이드 →'),
    'top': L('Stations with the most projects nearby', '附近项目最多的车站', 'Stesen dengan paling banyak projek berhampiran', '周辺に物件が多い駅', '주변 프로젝트가 많은 역'),
    'project': L('Project', '项目', 'Projek', '物件', '프로젝트'),
    'note': L('Distances are straight lines from the station; walking routes are longer. Station positions come from OpenStreetMap.',
              '距离是从车站算起的直线距离，实际步行路线会更长。车站位置来自 OpenStreetMap。',
              'Jarak ialah garis lurus dari stesen; laluan berjalan kaki lebih panjang. Kedudukan stesen daripada OpenStreetMap.',
              '距離は駅からの直線距離で、実際の徒歩ルートはもっと長くなります。駅の位置は OpenStreetMap によります。',
              '거리는 역에서의 직선거리이며 실제 도보 경로는 더 깁니다. 역 위치는 OpenStreetMap 기준입니다.'),
}
UIJ = json.dumps(UI, ensure_ascii=False)

MCSS = '''<style>
.mx{max-width:1240px;margin:0 auto;padding:0 5vw}.msec{padding:56px 0 30px}
.mwrap{display:grid;grid-template-columns:minmax(0,1fr) 380px;gap:16px;height:min(700px,82vh)}
.mbox{position:relative;isolation:isolate;z-index:0;height:100%;border-radius:24px;overflow:hidden;box-shadow:0 24px 60px rgba(29,27,79,.18);border:1px solid rgba(21,20,43,.08);background:#eef0f4}#map{position:absolute;inset:0;z-index:1}
.mside{display:flex;flex-direction:column;min-height:0;background:#fff;border-radius:24px;box-shadow:0 18px 44px rgba(29,27,79,.12);border:1px solid rgba(21,20,43,.08);overflow:hidden}
.mtop{padding:16px;border-bottom:1px solid #eeedf6;display:flex;flex-direction:column;gap:10px}.mlist{flex:1;min-height:0;overflow:auto;padding:10px 12px 14px}
.mside input{width:100%;border:1.5px solid rgba(94,96,206,.35);border-radius:100px;padding:11px 16px;font:500 14.5px Inter,sans-serif;outline:0;background:#fff;color:#15142b}
.msel{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}.msel select{width:100%;border:1px solid rgba(21,20,43,.14);border-radius:12px;padding:9px 6px;font:600 12.5px Inter,sans-serif;background:#fff;color:#15142b}
.mrow{display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap}.mcount{font:600 13px Inter,sans-serif;color:#55546b}.mcount b{color:#5E60CE;font-size:15px}
.mtools{display:flex;gap:6px;flex-wrap:wrap}.mtools button{background:#f3f1fa;border:0;border-radius:100px;padding:7px 11px;font:700 12px Inter,sans-serif;cursor:pointer;color:#15142b}.mtools button.on{background:#1d1b4f;color:#fff}
.mc{display:flex;align-items:center;gap:10px;padding:8px;border-radius:14px;cursor:pointer;border:1.5px solid transparent;margin-bottom:4px}.mc:hover{background:#f6f5fd}.mc.on{border-color:#5E60CE;background:#f3f1fa}
.mc img{width:84px;height:66px;object-fit:cover;border-radius:11px;flex:0 0 84px;background:#eee}.mc b{display:block;font:700 14.5px 'Playfair Display',serif;color:#15142b;line-height:1.25}.mc small{display:block;color:#55546b;font-size:12px;margin:2px 0}.mc em{font-style:normal;font-weight:800;color:#5E60CE;font-size:13px}
.chips{display:flex;flex-wrap:wrap;gap:6px}.chips button{border:1px solid rgba(21,20,43,.14);background:#fff;border-radius:100px;padding:6px 11px;font:700 12.5px Inter,sans-serif;cursor:pointer;color:#15142b}.chips button.on{background:#1d1b4f;color:#fff;border-color:#1d1b4f}
.seg{display:flex;background:#f1efff;border-radius:100px;padding:4px}.seg button{flex:1;border:0;background:none;color:#3d3fb0;border-radius:100px;padding:7px 10px;font:700 12.5px Inter,sans-serif;cursor:pointer}.seg button.on{background:#5E60CE;color:#fff}
.sli{display:flex;align-items:center;gap:10px;padding:10px 8px;border-radius:12px;cursor:pointer;border-bottom:1px solid #f1f0f7}.sli:hover{background:#f6f5fd}.sli i{flex:0 0 12px;width:12px;height:12px;border-radius:50%}.sli b{flex:1;font:700 14.5px 'Playfair Display',serif;color:#15142b}.sli small{font:700 12px Inter,sans-serif;color:#5E60CE}
.sdet h3{font:700 24px 'Playfair Display',serif;color:#15142b;margin:6px 0 2px}.sdet .bk{border:0;background:#f1efff;border-radius:100px;padding:7px 12px;cursor:pointer;font:700 12.5px Inter,sans-serif;color:#5E60CE;margin-bottom:6px}.sdet .eb2{display:block;font:700 12px Inter,sans-serif;letter-spacing:.2em;text-transform:uppercase}
.sdet .gd{display:inline-block;margin-top:6px;color:#5E60CE;font-weight:700;font-size:13px}
.kpin{display:inline-block;transform:translate(-50%,-100%);background:#fff;color:#1d1b4f;font:800 11.5px Inter,sans-serif;padding:5px 9px;border-radius:100px;border:2px solid #5E60CE;white-space:nowrap;box-shadow:0 6px 14px rgba(29,27,79,.25)}.kpin.on{background:#5E60CE;color:#fff}
.marker-cluster{background:rgba(94,96,206,.28)!important;border-radius:50%!important}.marker-cluster div{border-radius:50%!important;width:30px!important;height:30px!important;margin:5px!important;line-height:30px!important;text-align:center;background:#5E60CE!important;color:#fff!important;font:800 13px Inter,sans-serif!important}
.kpop{width:240px;font-family:Inter,sans-serif}.kpop img{width:100%;height:128px;object-fit:cover;border-radius:12px}.kpop b{display:block;font:700 17px 'Playfair Display',serif;margin:8px 0 2px;color:#15142b}.kpop small{display:block;color:#55546b}
.kpop em{display:block;font-style:normal;font-weight:800;color:#5E60CE;margin:4px 0}.kpop .nr{border-top:1px dashed #e3e1f2;margin-top:8px;padding-top:8px;font-size:12.5px;color:#2f2e45}.kpop .nr b{font:700 12px Inter,sans-serif;margin:0 0 3px}
.kpop a.go{display:block;text-align:center;background:#5E60CE;color:#fff!important;border-radius:100px;padding:9px;font-weight:700;margin-top:10px}.leaflet-popup-content-wrapper{border-radius:18px!important}
.sgrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:22px 0 10px}.sgrid a{display:block;background:linear-gradient(135deg,#1d1b4f,#34318a);color:#fff;border-radius:18px;padding:18px}.sgrid b{display:block;font:700 19px 'Playfair Display',serif;color:#fff}.sgrid small{color:#c9caff;font-weight:600}
.sgrid i{display:inline-block;font:800 11px Inter,sans-serif;font-style:normal;padding:3px 8px;border-radius:100px;margin-bottom:10px;color:#fff}
.h2x{font:700 clamp(24px,3vw,34px) 'Playfair Display',serif;color:#15142b;margin-top:38px}.mnote{font-size:12.5px;color:#77768c;margin-top:12px}
.srow{display:block;padding:12px 0;border-top:1px solid #eeedf6}.srow b{font:700 15px 'Playfair Display',serif;color:#15142b}.srow small{display:block;color:#55546b;font-size:12.5px;margin:2px 0 6px}
.bar{height:6px;border-radius:100px;background:#eeedfb;overflow:hidden}.bar i{display:block;height:100%;border-radius:100px;background:linear-gradient(90deg,#5E60CE,#a9abff)}
.stn{display:inline-block;transform:translate(-50%,-50%);width:16px;height:16px;border-radius:50%;background:#fff;border:4px solid;box-shadow:0 3px 10px rgba(0,0,0,.3)}
.legend{position:absolute;z-index:500;left:16px;bottom:16px;background:#fff;border-radius:14px;padding:10px 12px;font:600 12px Inter,sans-serif;box-shadow:0 8px 22px rgba(29,27,79,.15)}.legend span{display:inline-flex;align-items:center;gap:5px;margin-right:10px}.legend i{width:10px;height:10px;border-radius:50%;display:inline-block}
@media(max-width:900px){.mwrap{grid-template-columns:minmax(0,1fr);height:auto}.mbox{height:62vh;border-radius:18px}.mside{max-height:72vh}.sgrid{grid-template-columns:1fr 1fr}.legend{display:none}}
</style>'''

BASE_JS = '''var PF=window.KN_PF||"",P=%s,ST=%s,LC=%s,UI=%s;function lg(){var l="en";try{l=document.documentElement.getAttribute("data-page-lang")||localStorage.getItem("kn_lang")||"en"}catch(e){}return UI.fit[l]?l:"en";}
function u(k){return UI[k][lg()]||UI[k].en;}function dist(a,b,c,d){var R=6371000,x=(c-a)*Math.PI/180,y=(d-b)*Math.PI/180,s=Math.sin(x/2)*Math.sin(x/2)+Math.cos(a*Math.PI/180)*Math.cos(c*Math.PI/180)*Math.sin(y/2)*Math.sin(y/2);return 2*R*Math.asin(Math.sqrt(s));}
function near(p,n){return ST.map(function(s){return {s:s,d:dist(p.lat,p.lng,s.lat,s.lng)}}).sort(function(a,b){return a.d-b.d}).slice(0,n);}function fm(d){return d<1000?Math.round(d/10)*10+" m":(d/1000).toFixed(1)+" km";}
function pr(p){return p.p?u("from")+" "+p.p:u("por");}function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]});}
var map=L.map("map",{zoomControl:false,scrollWheelZoom:false}).setView([3.13,101.66],11);L.control.zoom({position:"bottomright"}).addTo(map);map.on("focus click",function(){map.scrollWheelZoom.enable();});
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,attribution:"&copy; OpenStreetMap"}).addTo(map);
var _w=window.knSetLang;if(typeof _w==="function"){window.knSetLang=function(){var r=_w.apply(this,arguments);try{relang();}catch(e){}return r;};}'''

PM_JS = '''var cl=L.markerClusterGroup({showCoverageOnHover:false,maxClusterRadius:48}),MK=[],rail=L.layerGroup();
function band(v){return !v?"":v<5e5?"a":v<1e6?"b":"c";}
function pop(p){var nn=near(p,2).filter(function(x){return x.d<2500}).map(function(x){return '<span style="color:'+LC[x.s.l]+'">&#9679;</span> '+esc(x.s.n)+' '+x.s.l+' · '+fm(x.d)}).join("<br>");
return '<div class="kpop"><img src="'+PF+p.i+'" alt=""><b>'+esc(p.n)+'</b><small>'+esc(p.a)+', '+esc(p.st)+' · '+esc(p.s)+'</small><em>'+pr(p)+'</em>'+(nn?'<div class="nr"><b>'+u("nearest")+'</b>'+nn+'</div>':'')+'<a class="go" href="'+PF+p.u+'">'+u("view")+'</a></div>';}
P.forEach(function(p,i){var m=L.marker([p.lat,p.lng],{icon:L.divIcon({className:"",html:'<span class="kpin" id="k'+i+'">'+(p.p?p.p.replace("RM ","RM"):"RM ?")+'</span>',iconSize:[0,0]})});
m.bindPopup(function(){return pop(p)},{maxWidth:260});m.on("click",function(){hl(i,true)});MK[i]=m;});
ST.forEach(function(s){L.circleMarker([s.lat,s.lng],{radius:5,color:"#fff",weight:2,fillColor:LC[s.l],fillOpacity:1}).bindTooltip(s.n+" "+s.l).addTo(rail);});map.addLayer(cl);
var states={},stat={};P.forEach(function(p){if(p.st)states[p.st]=(states[p.st]||0)+1;stat[p.s]=(stat[p.s]||0)+1});var SK=Object.keys(states).sort(function(a,b){return states[b]-states[a]});
function selects(){var a=fS.value,b=fT.value,c=fP.value;fS.innerHTML='<option value="">'+u("all_states")+'</option>'+SK.map(function(s){return '<option value="'+s+'">'+s+' ('+states[s]+')</option>'}).join("");
fT.innerHTML='<option value="">'+u("any_status")+'</option>'+Object.keys(stat).map(function(s){return '<option value="'+s+'">'+s+'</option>'}).join("");
fP.innerHTML='<option value="">'+u("any_price")+'</option><option value="a">'+u("p_a")+'</option><option value="b">'+u("p_b")+'</option><option value="c">'+u("p_c")+'</option>';fS.value=a;fT.value=b;fP.value=c;
q.placeholder=u("search_p");fit.textContent="⤢ "+u("fit");me.textContent="◎ "+u("me");rl.textContent="🚆 "+u("rail");nlab.textContent=u("shown");sgh.textContent=u("by_state");
sg.innerHTML=SK.map(function(s){return '<a href="#mapsec" data-s="'+s+'"><b>'+s+'</b><small>'+states[s]+' '+u("projs")+' →</small></a>'}).join("");}
function ok(p){var s=q.value.toLowerCase();return (!s||(p.n+" "+p.a+" "+p.st).toLowerCase().indexOf(s)>=0)&&(!fS.value||p.st==fS.value)&&(!fT.value||p.s==fT.value)&&(!fP.value||band(p.v)==fP.value);}
function hl(i,scroll){document.querySelectorAll(".kpin.on,.mc.on").forEach(function(x){x.classList.remove("on")});var k=document.getElementById("k"+i);if(k)k.classList.add("on");var c=document.querySelector('.mc[data-i="'+i+'"]');if(c){c.classList.add("on");if(scroll)c.scrollIntoView({behavior:"smooth",block:"nearest"});}}
function draw(fitb){cl.clearLayers();var h="",n=0,bb=[];P.forEach(function(p,i){if(!ok(p))return;n++;cl.addLayer(MK[i]);bb.push([p.lat,p.lng]);h+='<div class="mc" data-i="'+i+'"><img src="'+PF+p.i+'" loading="lazy" alt=""><div><b>'+esc(p.n)+'</b><small>'+esc(p.a)+'</small><em>'+pr(p)+'</em></div></div>';});
car.innerHTML=h;ncount.textContent=n;if(fitb!==false&&bb.length){if(!fS.value&&!q.value&&innerWidth<760)map.setView([3.12,101.66],11);else map.fitBounds(bb,{padding:[60,60],maxZoom:14});}}
function relang(){selects();draw(false);}
[q,fS,fT,fP].forEach(function(e){e.addEventListener(e.tagName=="INPUT"?"input":"change",function(){draw()})});
car.onclick=function(e){var c=e.target.closest(".mc");if(!c)return;var i=+c.dataset.i;hl(i);cl.zoomToShowLayer(MK[i],function(){MK[i].openPopup()});};
sg.onclick=function(e){var a=e.target.closest("a");if(!a)return;fS.value=a.dataset.s;draw();};
fit.onclick=function(){fS.value=fT.value=fP.value="";q.value="";draw()};me.onclick=function(){map.locate({setView:true,maxZoom:14})};
rl.onclick=function(){if(map.hasLayer(rail)){map.removeLayer(rail);rl.classList.remove("on")}else{map.addLayer(rail);rl.classList.add("on")}};selects();draw();'''

SM_JS = '''var LN="",R=1000,ring=null,sel=-1,sl=L.layerGroup().addTo(map),PM=[];
P.forEach(function(p,j){PM[j]=L.circleMarker([p.lat,p.lng],{radius:5,color:"#fff",weight:1.5,fillColor:"#5E60CE",fillOpacity:.85}).bindTooltip(p.n).on("click",function(){showP(j)}).addTo(map);});
function inR(s){return P.map(function(p,j){return {p:p,j:j,d:dist(p.lat,p.lng,s.lat,s.lng)}}).filter(function(x){return x.d<=R}).sort(function(a,b){return a.d-b.d});}
var LINES=Object.keys(LC).filter(function(l){return ST.some(function(s){return s.l==l})});
function chips(){cL.innerHTML='<button data-v=""'+(LN?'':' class="on"')+'>'+u("all_lines")+'</button>'+LINES.map(function(l){return '<button data-v="'+l+'"'+(LN==l?' class="on"':'')+'><span style="color:'+LC[l]+'">&#9679;</span> '+l+'</button>'}).join("");
lg_.innerHTML=LINES.map(function(l){return '<span><i style="background:'+LC[l]+'"></i>'+l+'</span>'}).join("")+'<span><i style="background:#5E60CE"></i>'+u("project")+'</span>';q.placeholder=u("search_s");toph.textContent=u("top");mnote.textContent=u("note");}
function drawS(){chips();sl.clearLayers();var qq=q.value.toLowerCase();ST.forEach(function(s,i){if(LN&&s.l!=LN)return;
if(qq&&s.n.toLowerCase().indexOf(qq)<0&&!inR(s).some(function(x){return x.p.n.toLowerCase().indexOf(qq)>=0}))return;
L.marker([s.lat,s.lng],{icon:L.divIcon({className:"",html:'<span class="stn" style="border-color:'+LC[s.l]+'"></span>',iconSize:[0,0]})}).bindTooltip(s.n+" "+s.l+" · "+inR(s).length+" "+u("projs")).on("click",function(){showS(i)}).addTo(sl);});
var all=ST.map(function(s,i){return {s:s,i:i,n:inR(s).length}}).filter(function(x){return (!LN||x.s.l==LN)&&(!qq||x.s.n.toLowerCase().indexOf(qq)>=0||inR(x.s).some(function(y){return y.p.n.toLowerCase().indexOf(qq)>=0}))}).sort(function(a,b){return b.n-a.n||a.s.n.localeCompare(b.s.n)});
if(sel<0)sp.innerHTML=all.map(function(x){return '<div class="sli" data-i="'+x.i+'"><i style="background:'+LC[x.s.l]+'"></i><b>'+esc(x.s.n)+' <span style="font:600 11px Inter;color:#77768c">'+x.s.l+'</span></b><small>'+x.n+'</small></div>'}).join("");
var tp=ST.map(function(s,i){return {s:s,i:i,n:inR(s).length}}).sort(function(a,b){return b.n-a.n}).slice(0,8);
topst.innerHTML=tp.map(function(x){return '<a href="#mapsec" data-i="'+x.i+'"><i style="background:'+LC[x.s.l]+'">'+x.s.l+'</i><b>'+esc(x.s.n)+'</b><small>'+x.n+' '+u("projs")+' · '+fm(R)+' →</small></a>'}).join("");}
function reset(){sel=-1;if(ring)map.removeLayer(ring);PM.forEach(function(m){m.setStyle({fillOpacity:.85,radius:5})});drawS();}
function showS(i){sel=i;var s=ST[i],ps=inR(s);if(ring)map.removeLayer(ring);ring=L.circle([s.lat,s.lng],{radius:R,color:LC[s.l],weight:2,dashArray:"6 6",fillColor:LC[s.l],fillOpacity:.07}).addTo(map);
map.fitBounds(ring.getBounds(),{padding:[30,30]});PM.forEach(function(m){m.setStyle({fillOpacity:.25,radius:4})});ps.forEach(function(x){PM[x.j].setStyle({fillOpacity:1,radius:8})});
sp.innerHTML='<div class="sdet"><button class="bk" type="button">← '+u("all_lines")+'</button><span class="eb2" style="color:'+LC[s.l]+'">'+s.l+' '+u("station")+'</span><h3>'+esc(s.n)+'</h3><small style="color:#55546b">'+ps.length+' '+u("within").replace("{r}",fm(R))+'</small>'+(s.g?'<br><a class="gd" href="'+PF+s.g+'">'+u("guide")+'</a>':'')+
ps.map(function(x){return '<a class="srow" href="'+PF+x.p.u+'"><b>'+esc(x.p.n)+'</b><small>'+esc(x.p.a)+' · '+fm(x.d)+' · '+u("walk").replace("{m}",Math.max(1,Math.round(x.d*1.3/80)))+' · '+pr(x.p)+'</small><div class="bar"><i style="width:'+Math.max(6,100-x.d/R*100)+'%"></i></div></a>'}).join("")+(ps.length?'':'<p style="margin-top:14px;color:#77768c">'+u("none")+'</p>')+'</div>';
sp.scrollTop=0;sp.querySelector(".bk").onclick=reset;}
function showP(j){var p=P[j];L.popup().setLatLng([p.lat,p.lng]).setContent('<div class="kpop"><img src="'+PF+p.i+'" alt=""><b>'+esc(p.n)+'</b><em>'+pr(p)+'</em><div class="nr"><b>'+u("nearest")+'</b>'+near(p,3).map(function(x){return '<span style="color:'+LC[x.s.l]+'">&#9679;</span> '+esc(x.s.n)+' '+x.s.l+' · '+fm(x.d)}).join("<br>")+'</div><a class="go" href="'+PF+p.u+'">'+u("view")+'</a></div>').openOn(map);}
cL.onclick=function(e){var b=e.target.closest("button");if(!b)return;LN=b.dataset.v;drawS();};
cR.onclick=function(e){var b=e.target.closest("button");if(!b)return;R=+b.dataset.v;cR.querySelectorAll("button").forEach(function(x){x.classList.toggle("on",x===b)});drawS();if(sel>=0)showS(sel);};
q.oninput=function(){sel=-1;drawS();};sp.onclick=function(e){var a=e.target.closest(".sli");if(a)showS(+a.dataset.i);};topst.onclick=function(e){var a=e.target.closest("a");if(a)showS(+a.dataset.i);};function relang(){drawS();if(sel>=0)showS(sel);}drawS();'''

LEAF = ('<link rel="stylesheet" href="vendor/leaflet/leaflet.css"><link rel="stylesheet" href="vendor/leaflet/MarkerCluster.css">'
        '<script src="vendor/leaflet/leaflet.js"></script><script src="vendor/leaflet/leaflet.markercluster.js"></script>')


def shell(rel, title, desc, body, ld, img, js):
    url = SITE + rel
    page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s">
<meta property="og:type" content="website">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:url" content="%s">
<meta property="og:image" content="%s">
<link rel="icon" type="image/png" href="images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@500;700&display=swap" rel="stylesheet">
<script type="application/ld+json">%s</script>
%s
<style>
:root{--ink:#15142b;--grey:#55546b;--line:rgba(21,20,43,.1);--gold:#5E60CE;--bg:#F9F8F6}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:Inter,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6}a{color:inherit;text-decoration:none}
footer{border-top:1px solid var(--line);padding:26px 5vw;font-size:13px;color:var(--grey);text-align:center}footer a{color:var(--gold)}
</style>
</head>
<body>
<header>
  <a class="logo" href="./"><img src="images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Malaysia Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="%s" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
<main>%s</main>
<footer>&copy; 2026 Keith Nah Real Estate · <a href="projects.html">All projects</a> · <a href="map.html">Project map</a> · <a href="station-map.html">Station map</a> · <a href="privacy-policy.html">Privacy Policy</a></footer>
<script src="lead-tracker.js"></script>
%s
</body>
</html>
''' % (E(title), E(desc), url, E(title), E(desc), url, SITE + img, json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'), K.CSS + MCSS + LEAF,
       E(WA % quote_plus('(KNRE) Hi Keith, I am looking at your project map and would like to ask about a project.')), body, js)
    page = SH.apply(page, '', 'projects.html')
    open(rel, 'w', encoding='utf-8').write(page)
    return url


X_HOME = L('Home', '首页', 'Laman Utama', 'ホーム', '홈')
X_PROJ = L('Projects', '项目', 'Projek', '物件', '프로젝트')
data = json.dumps(P, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
base = BASE_JS % (data, json.dumps(ST, ensure_ascii=False, separators=(',', ':')), json.dumps(LC), UIJ)
imgs = [p['i'] for p in P if p.get('i') and p.get('s') == 'New Launch'][:3] or [p['i'] for p in P if p.get('i')][:3]

# ---- map.html ----
tx = K.Tx()
left = (K.crumbs([(tx('home', X_HOME), './'), (tx('proj', X_PROJ), 'projects.html'), (tx('pm', L('Project map', '项目地图', 'Peta projek', '物件マップ', '프로젝트 지도')), None)]) +
        tx('pm_eb', L('Project map', '项目地图', 'Peta projek', '物件マップ', '프로젝트 지도'), 'span', 'knb-eb') +
        '<h1>%s <em>%s</em></h1>' % (tx('pm_h1a', L('See every project', '所有项目，', 'Lihat setiap projek', 'すべての物件を', '모든 프로젝트를')), tx('pm_h1b', L('on the map.', '尽在地图上。', 'di peta.', '地図で見る。', '지도에서 보기.'))) +
        '<p>%s</p>' % tx('pm_lead', L('Drag, zoom and tap a price tag. Filter by state, status and budget, and see the nearest rail stations for each project.',
                                       '拖动、放大，点价格标签就能看项目。可按州属、状态和预算筛选，还能看到每个项目最近的车站。',
                                       'Seret, zum dan ketik tanda harga. Tapis mengikut negeri, status dan bajet, dan lihat stesen rel terdekat bagi setiap projek.',
                                       'ドラッグやズームをして、価格タグをタップ。州・状況・予算で絞り込み、各物件の最寄り駅も確認できます。',
                                       '드래그하고 확대해서 가격 태그를 누르세요. 주, 상태, 예산으로 걸러 보고, 프로젝트마다 가까운 역도 확인할 수 있습니다.')) +
        K.pills([(tx('pm_b1', L('Open the map', '打开地图', 'Buka peta', '地図を開く', '지도 열기')), '#mapsec'),
                 (tx('pm_b2', L('Station map', '车站地图', 'Peta stesen', '駅マップ', '역 지도')), 'station/index.html#mapsec'),
                 (tx('pm_b3', L('All project list', '全部项目列表', 'Senarai semua projek', '全物件リスト', '전체 프로젝트 목록')), 'projects.html#projGrid'),
                 (tx('pm_b4', L('Find my home', '帮我找房', 'Cari rumah saya', '住まい探し', '내 집 찾기')), 'find-my-home.html')]))
n_states = len({p['st'] for p in P if p['st']})
stats = K.stats_html([(len(P), tx('s1', L('Projects on the map', '个项目在地图上', 'Projek di peta', '地図上の物件', '지도 위 프로젝트'))), (n_states, tx('s2', L('States', '个州属', 'Negeri', '州', '개 주'))),
                      (len(ST), tx('s3', L('Rail stations', '个车站', 'Stesen rel', '駅', '개 역'))), (N_1KM, tx('s4', L('Projects within 1 km of a station', '个项目离车站 1 公里内', 'Projek dalam 1 km dari stesen', '駅から1km以内の物件', '역 1km 이내 프로젝트')))])
body = K.hero(left, imgs, stats) + '''<section class="msec" id="mapsec"><div class="mx"><div class="mwrap"><div class="mbox"><div id="map"></div></div>
<aside class="mside"><div class="mtop"><input id="q" type="search" aria-label="Search"><div class="msel"><select id="fS" aria-label="State"></select><select id="fT" aria-label="Status"></select><select id="fP" aria-label="Price"></select></div>
<div class="mrow"><div class="mcount"><b id="ncount"></b> <span id="nlab"></span></div><div class="mtools"><button type="button" id="fit"></button><button type="button" id="me"></button><button type="button" id="rl"></button></div></div></div><div class="mlist" id="car"></div></aside></div>
<h2 class="h2x" id="sgh"></h2><div class="sgrid" id="sg"></div></div></section>'''
title = 'Project Map: %d Malaysia New Launches on One Map | Keith Nah' % len(P)
desc = 'Every project Keith lists on one map of Malaysia, with prices, status and the nearest MRT, LRT and KTM stations. Filter by state, status and budget.'
ld = {'@context': 'https://schema.org', '@graph': [{'@type': 'WebPage', 'name': 'Project map', 'description': desc, 'url': SITE + 'map.html'},
      {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE}, {'@type': 'ListItem', 'position': 2, 'name': 'Projects', 'item': SITE + 'projects.html'},
                                                      {'@type': 'ListItem', 'position': 3, 'name': 'Project map', 'item': SITE + 'map.html'}]}]}
u1 = shell('map.html', title, desc, body, ld, imgs[0] if imgs else 'images/18c3c17601a2ba81.jpg', '<script>%s\n%s</script>%s' % (base, PM_JS, tx.script()))

# ---- station-map.html ----
tx = K.Tx()
cnt = {}
for s in ST:
    cnt[s['l']] = cnt.get(s['l'], 0) + 1
left = (K.crumbs([(tx('home', X_HOME), './'), (tx('proj', X_PROJ), 'projects.html'), (tx('sm', L('Station map', '车站地图', 'Peta stesen', '駅マップ', '역 지도')), None)]) +
        tx('sm_eb', L('Station map', '车站地图', 'Peta stesen', '駅マップ', '역 지도'), 'span', 'knb-eb') +
        '<h1>%s <em>%s</em></h1>' % (tx('sm_h1a', L('Live near', '住在', 'Tinggal dekat', '駅の近くに', '역 가까이')), tx('sm_h1b', L('the rail.', '车站旁。', 'rel.', '住む。', '살기.'))) +
        '<p>%s</p>' % tx('sm_lead', L('Pick a station and see every project within walking distance, nearest first. Tap a project to see its closest stations.',
                                       '选一个车站，就能看到步行范围内的所有项目，由近到远排列。点项目可以看它最近的车站。',
                                       'Pilih stesen dan lihat setiap projek dalam jarak berjalan kaki, yang terdekat dahulu. Ketik projek untuk melihat stesen terdekatnya.',
                                       '駅を選ぶと、徒歩圏内の物件が近い順に表示されます。物件をタップすると最寄り駅がわかります。',
                                       '역을 고르면 걸어갈 수 있는 거리의 프로젝트가 가까운 순으로 나옵니다. 프로젝트를 누르면 가까운 역을 볼 수 있습니다.')) +
        K.pills([(tx('sm_b1', L('Open the station map', '打开车站地图', 'Buka peta stesen', '駅マップを開く', '역 지도 열기')), '#mapsec'),
                 (tx('sm_b2', L('Project map', '项目地图', 'Peta projek', '物件マップ', '프로젝트 지도')), 'map.html'),
                 (tx('sm_b3', L('Station guides', '车站指南', 'Panduan stesen', '駅ガイド', '역 가이드')), 'station/index.html'),
                 (tx('sm_b4', L('Find my home', '帮我找房', 'Cari rumah saya', '住まい探し', '내 집 찾기')), 'find-my-home.html')]))
stats = K.stats_html([(len(ST), tx('t1', L('Stations', '个车站', 'Stesen', '駅', '개 역'))), (cnt.get('MRT', 0), tx('t2', L('MRT stations', '个 MRT 站', 'Stesen MRT', 'MRT 駅', 'MRT 역'))),
                      (cnt.get('LRT', 0), tx('t3', L('LRT stations', '个 LRT 站', 'Stesen LRT', 'LRT 駅', 'LRT 역'))), (cnt.get('KTM', 0), tx('t4', L('KTM stations', '个 KTM 站', 'Stesen KTM', 'KTM 駅', 'KTM 역')))])
SM_BODY = '''<section class="msec" id="mapsec"><div class="mx"><div class="mwrap"><div class="mbox"><div id="map"></div><div class="legend" id="lg_"></div></div>
<aside class="mside"><div class="mtop"><input id="q" type="search" aria-label="Search"><div class="chips" id="cL"></div><div class="seg" id="cR"><button type="button" data-v="500">500 m</button><button type="button" data-v="1000" class="on">1 km</button><button type="button" data-v="1500">1.5 km</button></div></div><div class="mlist" id="sp"></div></aside></div><p class="mnote" id="mnote"></p>
<h2 class="h2x" id="toph"></h2><div class="sgrid" id="topst"></div></div></section>'''
body = K.hero(left, ['images/understand/transport.jpg', 'images/18c3c17601a2ba81.jpg', 'images/understand/glance.jpg'], stats) + SM_BODY
title = 'Station Map: New Condos Near MRT, LRT and KTM Stations | Keith Nah'
desc = 'Pick an MRT, LRT, Monorail or KTM station and see the new projects within 500 m, 1 km or 1.5 km, nearest first, with prices and walking times.'
ld = {'@context': 'https://schema.org', '@graph': [{'@type': 'WebPage', 'name': 'Station map', 'description': desc, 'url': SITE + 'station-map.html'},
      {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE}, {'@type': 'ListItem', 'position': 2, 'name': 'Projects', 'item': SITE + 'projects.html'},
                                                      {'@type': 'ListItem', 'position': 3, 'name': 'Station map', 'item': SITE + 'station-map.html'}]}]}
u2 = shell('station-map.html', title, desc, body, ld, 'images/understand/transport.jpg', '<script>%s\n%s</script>%s' % (base, SM_JS, tx.script()))

# ---- the station map inside Browse by Station (station/index.html, rebuilt by build_hubs.py) ----
f = 'station/index.html'
if os.path.exists(f):
    st = open(f, encoding='utf-8').read()
    st = re.sub(r'<!-- KN-STMAP:START -->.*?<!-- KN-STMAP:END -->', '', st, flags=re.S)
    tx2 = K.Tx()
    head = ('<div class="mx" style="margin-bottom:14px">%s<h2 class="h2x" style="margin-top:0">%s</h2><p style="color:#55546b;max-width:760px">%s</p></div>' % (
        tx2('sm_eb', L('Station map', '车站地图', 'Peta stesen', '駅マップ', '역 지도'), 'span', 'eb2" style="display:block;font:600 13px Inter,sans-serif;letter-spacing:.28em;text-transform:uppercase;color:#5E60CE'),
        tx2('sm_h', L('Pick a station on the map', '在地图上选一个车站', 'Pilih stesen di peta', '地図で駅を選ぶ', '지도에서 역 고르기')),
        tx2('sm_lead', L('Pick a station and see every project within walking distance, nearest first. Tap a project to see its closest stations.',
                         '选一个车站，就能看到步行范围内的所有项目，由近到远排列。点项目可以看它最近的车站。',
                         'Pilih stesen dan lihat setiap projek dalam jarak berjalan kaki, yang terdekat dahulu. Ketik projek untuk melihat stesen terdekatnya.',
                         '駅を選ぶと、徒歩圏内の物件が近い順に表示されます。物件をタップすると最寄り駅がわかります。',
                         '역을 고르면 걸어갈 수 있는 거리의 프로젝트가 가까운 순으로 나옵니다. 프로젝트를 누르면 가까운 역을 볼 수 있습니다.'))))
    sec = (SM_BODY.replace('<section class="msec" id="mapsec"><div class="mx">', '<section class="msec" id="mapsec" style="padding-top:34px">' + head + '<div class="mx">', 1))
    blk = ('<!-- KN-STMAP:START -->' + K.CSS.replace('<style id="knb-css">', '<style>') + MCSS + LEAF.replace('href="vendor/', 'href="../vendor/').replace('src="vendor/', 'src="../vendor/') + sec +
           '<script>window.KN_PF="../";</script><script>%s\n%s</script>%s<!-- KN-STMAP:END -->' % (base, SM_JS, tx2.script()))
    i = st.find('</section>', st.find('<main>'))
    if i > 0:
        st = st[:i + len('</section>')] + blk + st[i + len('</section>'):]
        open(f, 'w', encoding='utf-8').write(st)

# ---- sitemap ----
if os.path.exists('sitemap.xml'):
    import datetime
    sm = open('sitemap.xml', encoding='utf-8').read()
    for u in (u1, u2):
        if '<loc>%s</loc>' % u not in sm:
            sm = sm.replace('</urlset>', '  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.7</priority>\n  </url>\n</urlset>' % (u, datetime.date.today().isoformat()))
    open('sitemap.xml', 'w', encoding='utf-8').write(sm)
print('maps: map.html (%d projects), station-map.html (%d stations)' % (len(P), len(ST)))
