"""Saved projects: a heart on every project card and project page; the list opens from a
"Saved" button and goes to Keith on WhatsApp in one tap, or to the compare page.

Writes assets/kn-saved.js (project names, prices, photos by slug, plus the script) and adds it
to every English page (the language copies are rendered from them). The list is kept in the
visitor's own browser (localStorage "kn_saved"), nothing is sent anywhere until they tap WhatsApp.
Run by tools/build_all.py after build_footer; safe to run again.
"""
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
sys.path.insert(0, HERE)
import hubs_data as HB

DIRS = ['', 'article', 'area', 'best', 'developer', 'guides', 'notes', 'property', 'station', 'topic', 'vs']
src = open('projects.html', encoding='utf-8').read()
i = src.index('const PROJECT_DETAILS = ')
P = json.JSONDecoder().raw_decode(src[src.index('=', i) + 1:].lstrip())[0]
IDX = json.load(open(os.path.join(HERE, 'project_index.json'), encoding='utf-8'))


def photo(slug):
    f = 'property/%s.html' % slug
    if os.path.exists(f):
        m = re.search(r'og:image" content="https://keithnah\.com/([^"]+)"', open(f, encoding='utf-8').read())
        if m:
            return m.group(1)
    return ''


D = {}
for k, p in enumerate(P):
    s = IDX[k]['slug']
    pr = HB.price(p.get('price'))
    D[s] = [p['name'], pr or 0, '%s, %s' % (IDX[k]['area'], IDX[k]['state']), photo(s)]
NAMES = {p['name']: IDX[k]['slug'] for k, p in enumerate(P)}

T = {
    'en': {'saved': 'Saved', 'title': 'My saved projects', 'sub': 'Saved on this device. Send the list to Keith for the latest prices and floor plans.',
           'empty': 'Tap the heart on any project to save it here.', 'wa': 'Send my list to Keith on WhatsApp', 'cmp': 'Compare these side by side',
           'save': 'Save', 'savedb': 'Saved', 'from': 'From {p}', 'por': 'Price on request', 'rm': 'Remove', 'close': 'Close',
           'msg': '(KNRE) Hi Keith, these are the projects I saved on your website:'},
    'zh-CN': {'saved': '已收藏', 'title': '我的收藏项目', 'sub': '收藏保存在这部设备上。把清单发给 Keith，获取最新价格和户型图。',
              'empty': '按任何项目上的爱心，就会收藏在这里。', 'wa': '把清单 WhatsApp 给 Keith', 'cmp': '对比这些项目',
              'save': '收藏', 'savedb': '已收藏', 'from': '{p} 起', 'por': '价格请询问', 'rm': '移除', 'close': '关闭',
              'msg': '(KNRE) Hi Keith, these are the projects I saved on your website:'},
    'ms': {'saved': 'Disimpan', 'title': 'Projek yang saya simpan', 'sub': 'Disimpan pada peranti ini. Hantar senarai kepada Keith untuk harga dan pelan lantai terkini.',
           'empty': 'Tekan ikon hati pada mana-mana projek untuk menyimpannya di sini.', 'wa': 'Hantar senarai kepada Keith di WhatsApp', 'cmp': 'Bandingkan projek ini',
           'save': 'Simpan', 'savedb': 'Disimpan', 'from': 'Dari {p}', 'por': 'Harga atas permintaan', 'rm': 'Buang', 'close': 'Tutup',
           'msg': '(KNRE) Hi Keith, these are the projects I saved on your website:'},
    'ja': {'saved': '保存済み', 'title': '保存した物件', 'sub': 'この端末に保存されています。リストを Keith に送ると、最新の価格と間取り図が届きます。',
           'empty': '物件のハートを押すと、ここに保存されます。', 'wa': 'リストを WhatsApp で Keith に送る', 'cmp': 'これらの物件を比較',
           'save': '保存', 'savedb': '保存済み', 'from': '{p} から', 'por': '価格はお問い合わせ', 'rm': '削除', 'close': '閉じる',
           'msg': '(KNRE) Hi Keith, these are the projects I saved on your website:'},
    'ko': {'saved': '저장됨', 'title': '저장한 프로젝트', 'sub': '이 기기에 저장됩니다. 목록을 Keith에게 보내면 최신 가격과 평면도를 받을 수 있습니다.',
           'empty': '프로젝트의 하트를 누르면 여기에 저장됩니다.', 'wa': '목록을 WhatsApp으로 Keith에게 보내기', 'cmp': '이 프로젝트들 비교하기',
           'save': '저장', 'savedb': '저장됨', 'from': '{p}부터', 'por': '가격 문의', 'rm': '삭제', 'close': '닫기',
           'msg': '(KNRE) Hi Keith, these are the projects I saved on your website:'},
}
import opencc
_cc = opencc.OpenCC('s2tw').convert
T['zh-TW'] = {k: (v if k == 'msg' else _cc(v)) for k, v in T['zh-CN'].items()}

CSS = ('.kv-h{position:absolute;top:12px;right:12px;z-index:5;width:40px;height:40px;border-radius:50%;border:0;background:rgba(255,255,255,.93);'
       'display:flex;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(0,0,0,.18);cursor:pointer;padding:0;transition:transform .15s}'
       '.kv-h:hover{transform:scale(1.08)}.kv-h svg,.kv-sv svg,.kv-pill svg{width:21px;height:21px;fill:none;stroke:#15142b;stroke-width:2}'
       '.kv-h.on svg,.kv-sv.on svg{fill:#ff3b5c;stroke:#ff3b5c}.kv-h.pop svg{animation:kvPop .35s}@keyframes kvPop{50%{transform:scale(1.35)}}'
       '.kv-sv{display:inline-flex;align-items:center;gap:8px;padding:12px 20px;border-radius:999px;border:1.5px solid #d9d6ea;background:#fff;'
       'font:700 14px Inter,sans-serif;color:#15142b;cursor:pointer}.kv-sv.on{border-color:#ff3b5c;color:#ff3b5c}'
       '.kv-pill{position:fixed;left:20px;bottom:24px;z-index:61;display:none;align-items:center;gap:8px;background:#15142b;color:#fff;border:0;cursor:pointer;'
       'font:700 14px Inter,sans-serif;padding:12px 18px;border-radius:999px;box-shadow:0 10px 30px rgba(0,0,0,.3)}.kv-pill.show{display:flex}'
       '.kv-pill svg{width:18px;height:18px;fill:#ff3b5c;stroke:#ff3b5c}.kv-pill i{font-style:normal;background:#ff3b5c;border-radius:999px;padding:1px 8px;font-size:12px}'
       '.kv-bg{position:fixed;inset:0;background:rgba(10,10,30,.45);z-index:9998;display:none}.kv-bg.show{display:block}'
       '.kv-d{position:fixed;right:0;top:0;bottom:0;width:min(400px,100%);background:#fff;z-index:9999;box-shadow:-20px 0 60px rgba(0,0,0,.2);display:flex;'
       'flex-direction:column;font-family:Inter,sans-serif;color:#15142b;transform:translateX(105%);transition:transform .3s ease}.kv-d.show{transform:none}'
       '.kv-d .hd{display:flex;justify-content:space-between;align-items:center;padding:22px 22px 10px}.kv-d h3{font:700 24px "Playfair Display",Georgia,serif;margin:0}'
       '.kv-d .x{border:0;background:none;font-size:30px;line-height:1;color:#999;cursor:pointer}.kv-d p.s{margin:0 22px 10px;color:#5f5e74;font-size:13px;line-height:1.5}'
       '.kv-l{flex:1;overflow:auto;padding:0 22px}.kv-e{color:#5f5e74;font-size:14px;padding:30px 0;text-align:center}'
       '.kv-i{display:grid;grid-template-columns:84px 1fr 30px;gap:12px;align-items:center;padding:12px 0;border-bottom:1px solid #eee}'
       '.kv-i img{width:84px;height:64px;object-fit:cover;border-radius:10px;background:#eee}.kv-i a{color:inherit;text-decoration:none}'
       '.kv-i b{display:block;font-size:15px;line-height:1.3}.kv-i small{color:#5f5e74;font-size:12px;display:block}.kv-i em{font-style:normal;color:#5E60CE;font-weight:700;font-size:13px}'
       '.kv-i button{border:0;background:none;cursor:pointer;padding:0}.kv-i button svg{width:22px;height:22px;fill:#ff3b5c;stroke:#ff3b5c}'
       '.kv-a{padding:16px 22px 22px;display:grid;gap:10px}.kv-a a{text-align:center;padding:14px;border-radius:14px;font-weight:700;font-size:14.5px;text-decoration:none}'
       '.kv-a .w{background:#25D366;color:#fff;box-shadow:0 10px 24px rgba(37,211,102,.3)}.kv-a .c{border:1.5px solid #d9d6ea;color:#15142b}.kv-a .c[hidden]{display:none}'
       '@media(max-width:600px){.kv-pill{left:14px;bottom:18px;padding:11px 15px}}')

JS = r'''(function(){var D=%s,N=%s,T=%s,CSS=%s;
var H='<svg viewBox="0 0 24 24"><path d="M12 21s-7.5-4.6-9.5-9.2C1 8.2 3.4 4.5 7 4.5c2 0 3.4 1.1 5 3 1.6-1.9 3-3 5-3 3.6 0 6 3.7 4.5 7.3C19.5 16.4 12 21 12 21z"/></svg>';
var LP=(location.pathname.match(/^\/(zh-tw|zh|ms|ja|ko)\//)||[,""])[1],root=LP?"/"+LP+"/":"/";
function lg(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}return T[l]?l:"en";}
function t(k){return T[lg()][k]||T.en[k];}
function get(){try{return (JSON.parse(localStorage.getItem("kn_saved")||"[]")||[]).filter(function(s){return D[s];});}catch(e){return [];}}
function put(a){try{localStorage.setItem("kn_saved",JSON.stringify(a));}catch(e){}}
function has(s){return get().indexOf(s)>-1;}
function toggle(s){var a=get(),i=a.indexOf(s);if(i>-1)a.splice(i,1);else{a.unshift(s);if(typeof gtag==="function")gtag("event","save_project",{project:D[s][0]});}put(a);sync();}
function e(x){var d=document.createElement("div");d.textContent=x;return d.innerHTML;}
function money(v){return v>=1e6?"RM"+(v/1e6).toFixed(2).replace(/\.?0+$/,"")+"M":"RM"+Math.round(v/1e3)+"K";}
var pill,bg,dr;
function ui(){var st=document.createElement("style");st.setAttribute("data-kv","");st.textContent=CSS;document.head.appendChild(st);
pill=document.createElement("button");pill.type="button";pill.className="kv-pill";pill.onclick=open;document.body.appendChild(pill);
bg=document.createElement("div");bg.className="kv-bg";bg.onclick=close;document.body.appendChild(bg);
dr=document.createElement("aside");dr.className="kv-d";dr.setAttribute("aria-label","Saved projects");document.body.appendChild(dr);}
function open(){draw();bg.classList.add("show");dr.classList.add("show");}
function close(){bg.classList.remove("show");dr.classList.remove("show");}
function draw(){var a=get();
var list=a.length?a.map(function(s){var d=D[s];return '<div class="kv-i"><a href="'+root+'property/'+s+'.html">'+(d[3]?'<img src="/'+d[3]+'" alt="" loading="lazy">':'<img alt="">')+'</a><a href="'+root+'property/'+s+'.html"><b>'+e(d[0])+'</b><small>'+e(d[2])+'</small><em>'+(d[1]?e(t("from").replace("{p}",money(d[1]))):e(t("por")))+'</em></a><button type="button" data-rm="'+s+'" aria-label="'+e(t("rm"))+'">'+H+'</button></div>';}).join(""):'<div class="kv-e">'+e(t("empty"))+'</div>';
var msg=t("msg")+"\n"+a.map(function(s,i){return (i+1)+". "+D[s][0]+" - https://keithnah.com/property/"+s+".html";}).join("\n");
dr.innerHTML='<div class="hd"><h3>'+e(t("title"))+'</h3><button type="button" class="x" aria-label="'+e(t("close"))+'">&times;</button></div><p class="s">'+e(t("sub"))+'</p><div class="kv-l">'+list+'</div>'+
(a.length?'<div class="kv-a"><a class="w" target="_blank" rel="noopener" href="https://api.whatsapp.com/send/?phone=60102821568&type=phone_number&app_absent=0&text='+encodeURIComponent(msg)+'">'+e(t("wa"))+'</a><a class="c" href="'+root+'compare.html?p='+a.slice(0,4).join(",")+'"'+(a.length<2?' hidden':'')+'>'+e(t("cmp"))+'</a></div>':'');
dr.querySelector(".x").onclick=close;dr.querySelectorAll("[data-rm]").forEach(function(b){b.onclick=function(){toggle(b.getAttribute("data-rm"));draw();};});
var w=dr.querySelector(".kv-a .w");if(w)w.addEventListener("click",function(){if(typeof gtag==="function")gtag("event","generate_lead",{method:"saved_list",count:a.length});});}
function sync(){var n=get().length;pill.innerHTML=H+e(t("saved"))+' <i>'+n+'</i>';pill.classList.toggle("show",n>0);
document.querySelectorAll("[data-kv]").forEach(function(b){var on=has(b.getAttribute("data-kv"));b.classList.toggle("on",on);b.setAttribute("aria-pressed",on);
if(b.classList.contains("kv-sv")){var tx=" "+t(on?"savedb":"save");if(b.lastChild.textContent!==tx)b.lastChild.textContent=tx;}else b.setAttribute("aria-label",t(on?"savedb":"save"));});}
function heart(s,cls){var b=document.createElement("button");b.type="button";b.className=cls;b.setAttribute("data-kv",s);b.innerHTML=H+(cls==="kv-sv"?" ":"");if(cls==="kv-sv")b.appendChild(document.createTextNode(""));
b.addEventListener("click",function(ev){ev.preventDefault();ev.stopPropagation();toggle(s);b.classList.add("pop");setTimeout(function(){b.classList.remove("pop")},400);});return b;}
function cards(){var P=typeof PROJECT_DETAILS!=="undefined"?PROJECT_DETAILS:null;document.querySelectorAll(".proj-card[data-idx]").forEach(function(c){if(c.querySelector(".kv-h"))return;
var p=P&&P[+c.getAttribute("data-idx")],s=p&&N[p.name],m=c.querySelector(".proj-media")||c;if(!s)return;if(getComputedStyle(m).position==="static")m.style.position="relative";m.appendChild(heart(s,"kv-h"));});sync();}
function page(){var m=location.pathname.match(/\/property\/([a-z0-9-]+)\.html$/);if(!m||!D[m[1]])return;var h=document.querySelector("h1");if(!h||document.querySelector(".kv-sv"))return;
var c=document.querySelector(".ctas");if(c)c.appendChild(heart(m[1],"kv-sv"));else h.insertAdjacentElement("afterend",heart(m[1],"kv-sv"));}
function start(){document.querySelectorAll(".kv-h,.kv-sv,.kv-pill,.kv-bg,.kv-d,style[data-kv]").forEach(function(x){x.remove();});ui();page();cards();sync();var g=document.getElementById("projGrid");if(g)new MutationObserver(function(){cards();}).observe(g,{childList:true,subtree:true});
var s=window.knSetLang;if(typeof s==="function")window.knSetLang=function(){var r=s.apply(this,arguments);sync();if(dr.classList.contains("show"))draw();return r;};
document.addEventListener("keydown",function(ev){if(ev.key==="Escape")close();});}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",start);else start();})();'''

body = JS % (json.dumps(D, ensure_ascii=False, separators=(',', ':')), json.dumps(NAMES, ensure_ascii=False, separators=(',', ':')),
             json.dumps(T, ensure_ascii=False, separators=(',', ':')), json.dumps(CSS))
os.makedirs('assets', exist_ok=True)
open('assets/kn-saved.js', 'w', encoding='utf-8').write(body)
v = hashlib.sha1(body.encode('utf-8')).hexdigest()[:10]

n = 0
for d in DIRS:
    for f in sorted(glob.glob(os.path.join(d, '*.html') if d else '*.html')):
        if f == '404.html':
            continue
        t = open(f, encoding='utf-8').read()
        tag = '<script src="%sassets/kn-saved.js?v=%s" defer></script>' % ('../' if d else '', v)
        t2 = re.sub(r'<script src="(?:\.\./)?assets/kn-saved\.js\?v=[0-9a-f]+" defer></script>', '', t)
        t2 = t2.replace('</body>', tag + '\n</body>', 1)
        if t2 != t:
            open(f, 'w', encoding='utf-8').write(t2)
            n += 1
print('saved projects: %d projects, script on %d page(s)' % (len(D), n))
