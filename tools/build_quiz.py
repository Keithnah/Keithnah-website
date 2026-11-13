"""'Find my home' (find-my-home.html): five quick questions, then the best-matching projects,
and one tap sends the answers and the shortlist to Keith on WhatsApp.

Matching uses only the published project details (price, state, bedrooms, tenure, status and
completion, rail tags). Texts in all 6 languages; the language copies are made by
tools/build_lang_pages.js. Run by tools/build_all.py after the project pages.
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.chdir(ROOT)
import hubs_data as HB
import site_header as SH

E = lambda s: html.escape(str(s if s is not None else ''), quote=True)
src = open('projects.html', encoding='utf-8').read()


def js_json(name):
    i = src.index('const %s = ' % name) if ('const %s = ' % name) in src else src.index('var %s = ' % name)
    i = src.index('=', i) + 1
    return json.JSONDecoder().raw_decode(src[i:].lstrip())[0]


P = js_json('PROJECT_DETAILS')
TAGS = js_json('KN_TAGS')
IDX = json.load(open(os.path.join(HERE, 'project_index.json'), encoding='utf-8'))


def rooms(s):
    s = (s or '').lower()
    nums = [int(x) for x in re.findall(r'(\d)(?:\+\d)?', s)]
    lo = 0 if 'studio' in s else (min(nums) if nums else None)
    hi = max(nums) if nums else (0 if 'studio' in s else None)
    return lo, hi


def photo(i):
    try:
        t = open('property/%s.html' % IDX[i]['slug'], encoding='utf-8').read()
        m = re.search(r'og:image" content="https://keithnah\.com/([^"]+)"', t)
        return m.group(1) if m else ''
    except OSError:
        return ''


data = []
for i, p in enumerate(P):
    lo, hi = rooms(p.get('rooms'))
    comp = str(p.get('completion') or '')
    y = re.search(r'(20\d\d)', comp)
    tg = ' '.join(TAGS[i]).lower() if i < len(TAGS) else ''
    data.append({'n': p['name'], 's': IDX[i]['slug'], 'st': IDX[i]['state'], 'a': IDX[i]['area'], 'loc': p.get('loc', ''),
                 'p': HB.price(p.get('price')), 'pt': p.get('price', ''), 'fh': 'freehold' in (p.get('tenure') or '').lower(),
                 'r0': lo, 'r1': hi, 'ready': (p.get('status') == 'Completed') or (bool(y) and int(y.group(1)) <= 2027),
                 'rail': bool(re.search(r'near (mrt|lrt|ktm|monorail|rts|brt)', tg)), 'img': photo(i),
                 'ten': (p.get('tenure') or '').split(' (')[0], 'stat': p.get('status', '')})

T = {
 'en': {'eb': 'Find my home', 'h1': 'Find your home in 3 minutes', 'p': 'Answer five quick questions and see the new launches that fit you best, then send the shortlist to Keith in one tap.',
        'step': 'Question {n} of 5', 'back': '← Back', 'again': 'Start again',
        'q1': 'What is the home for?', 'q1a': 'To live in', 'q1b': 'To invest and rent out', 'q1c': 'Both',
        'q2': 'What is your budget?', 'q2a': 'Under RM500K', 'q2b': 'RM500K – RM800K', 'q2c': 'RM800K – RM1.2M', 'q2d': 'RM1.2M – RM2M', 'q2e': 'Above RM2M',
        'q3': 'Where would you like to buy?', 'any': 'Anywhere', 'q4': 'How many bedrooms?', 'q4a': 'Studio or 1', 'q4b': '2', 'q4c': '3 or more',
        'q5': 'What matters most?', 'q5a': 'Near an MRT / LRT station', 'q5b': 'Freehold', 'q5c': 'Ready soon (by 2027)', 'q5d': 'Lowest price',
        'res': 'Your best matches', 'resp': 'Based on your answers. Prices are gross starting prices as published and may change.',
        'none': 'No project fits every answer, so here are the closest ones.', 'send': 'Send my shortlist to Keith on WhatsApp',
        'all': 'See all projects', 'view': 'View project →',
        'w_budget': 'Within budget', 'w_over': 'Slightly above budget', 'w_area': 'In your area', 'w_rooms': 'Has your bedrooms',
        'w_rail': 'Near rail', 'w_fh': 'Freehold', 'w_ready': 'Ready by 2027'},
 'zh-CN': {'eb': '帮我找房', 'h1': '3 分钟找到适合你的房子', 'p': '回答 5 个简单问题，马上看到最适合你的新楼盘，再一键把清单发给 Keith。',
           'step': '第 {n} 题，共 5 题', 'back': '← 上一题', 'again': '重新开始',
           'q1': '买房的用途是？', 'q1a': '自住', 'q1b': '投资出租', 'q1c': '两者都有',
           'q2': '你的预算是？', 'q2a': 'RM50 万以下', 'q2b': 'RM50 万 – RM80 万', 'q2c': 'RM80 万 – RM120 万', 'q2d': 'RM120 万 – RM200 万', 'q2e': 'RM200 万以上',
           'q3': '想在哪里买？', 'any': '都可以', 'q4': '需要几间房？', 'q4a': '单间或 1 房', 'q4b': '2 房', 'q4c': '3 房或以上',
           'q5': '你最看重什么？', 'q5a': '靠近 MRT / LRT 站', 'q5b': '永久地契', 'q5c': '很快可入住（2027 年前）', 'q5d': '价格最低',
           'res': '最适合你的项目', 'resp': '根据你的回答整理。价格为公布的总价起价，可能会变动。',
           'none': '没有项目完全符合所有条件，以下是最接近的项目。', 'send': '把清单 WhatsApp 给 Keith',
           'all': '查看全部项目', 'view': '查看项目 →',
           'w_budget': '符合预算', 'w_over': '略高于预算', 'w_area': '在你选的地区', 'w_rooms': '有你要的房型',
           'w_rail': '靠近轨道交通', 'w_fh': '永久地契', 'w_ready': '2027 年前完工'},
 'ms': {'eb': 'Cari rumah saya', 'h1': 'Cari rumah anda dalam 3 minit', 'p': 'Jawab lima soalan ringkas dan lihat projek baharu yang paling sesuai, kemudian hantar senarai pendek kepada Keith dengan satu sentuhan.',
        'step': 'Soalan {n} daripada 5', 'back': '← Kembali', 'again': 'Mula semula',
        'q1': 'Rumah ini untuk apa?', 'q1a': 'Untuk didiami', 'q1b': 'Untuk pelaburan dan disewa', 'q1c': 'Kedua-duanya',
        'q2': 'Berapa bajet anda?', 'q2a': 'Bawah RM500K', 'q2b': 'RM500K – RM800K', 'q2c': 'RM800K – RM1.2J', 'q2d': 'RM1.2J – RM2J', 'q2e': 'Melebihi RM2J',
        'q3': 'Di mana anda mahu membeli?', 'any': 'Mana-mana', 'q4': 'Berapa bilik tidur?', 'q4a': 'Studio atau 1', 'q4b': '2', 'q4c': '3 atau lebih',
        'q5': 'Apa paling penting?', 'q5a': 'Dekat stesen MRT / LRT', 'q5b': 'Pegangan bebas', 'q5c': 'Siap tidak lama lagi (menjelang 2027)', 'q5d': 'Harga paling rendah',
        'res': 'Padanan terbaik anda', 'resp': 'Berdasarkan jawapan anda. Harga ialah harga permulaan kasar yang diterbitkan dan boleh berubah.',
        'none': 'Tiada projek memenuhi semua jawapan, jadi ini yang paling hampir.', 'send': 'Hantar senarai pendek kepada Keith di WhatsApp',
        'all': 'Lihat semua projek', 'view': 'Lihat projek →',
        'w_budget': 'Dalam bajet', 'w_over': 'Sedikit melebihi bajet', 'w_area': 'Di kawasan anda', 'w_rooms': 'Ada bilik yang anda mahu',
        'w_rail': 'Dekat rel', 'w_fh': 'Pegangan bebas', 'w_ready': 'Siap menjelang 2027'},
 'ja': {'eb': 'おうち探し', 'h1': '3分であなたに合う家を探す', 'p': '5つの簡単な質問に答えると、あなたに合う新築物件がすぐにわかります。候補リストはワンタップで Keith に送れます。',
        'step': '質問 {n} / 5', 'back': '← 戻る', 'again': 'やり直す',
        'q1': '家の用途は？', 'q1a': '自分で住む', 'q1b': '投資・賃貸', 'q1c': '両方',
        'q2': 'ご予算は？', 'q2a': '50万リンギ未満', 'q2b': '50万〜80万リンギ', 'q2c': '80万〜120万リンギ', 'q2d': '120万〜200万リンギ', 'q2e': '200万リンギ超',
        'q3': 'どこで買いたいですか？', 'any': 'どこでも', 'q4': '寝室はいくつ？', 'q4a': 'スタジオまたは1', 'q4b': '2', 'q4c': '3以上',
        'q5': '一番重視することは？', 'q5a': 'MRT / LRT 駅の近く', 'q5b': 'フリーホールド', 'q5c': 'すぐ入居できる（2027年まで）', 'q5d': '価格が一番安い',
        'res': 'あなたにぴったりの物件', 'resp': '回答をもとに選びました。価格は公表された総額の最低価格で、変わることがあります。',
        'none': 'すべての条件に合う物件がないため、近いものを表示しています。', 'send': '候補リストを WhatsApp で Keith に送る',
        'all': 'すべての物件を見る', 'view': '物件を見る →',
        'w_budget': '予算内', 'w_over': '予算を少し超える', 'w_area': 'ご希望のエリア', 'w_rooms': 'ご希望の間取りあり',
        'w_rail': '駅の近く', 'w_fh': 'フリーホールド', 'w_ready': '2027年までに完成'},
 'ko': {'eb': '내 집 찾기', 'h1': '3분 만에 나에게 맞는 집 찾기', 'p': '간단한 질문 5개에 답하면 가장 잘 맞는 신규 분양을 바로 보여 드리고, 후보 목록을 한 번에 Keith에게 보낼 수 있습니다.',
        'step': '질문 {n} / 5', 'back': '← 이전', 'again': '다시 시작',
        'q1': '집의 용도는?', 'q1a': '실거주', 'q1b': '투자·임대', 'q1c': '둘 다',
        'q2': '예산은?', 'q2a': '50만 링깃 미만', 'q2b': '50만 – 80만 링깃', 'q2c': '80만 – 120만 링깃', 'q2d': '120만 – 200만 링깃', 'q2e': '200만 링깃 초과',
        'q3': '어디에서 사고 싶으세요?', 'any': '어디든', 'q4': '침실은 몇 개?', 'q4a': '스튜디오 또는 1개', 'q4b': '2개', 'q4c': '3개 이상',
        'q5': '가장 중요한 것은?', 'q5a': 'MRT / LRT 역 근처', 'q5b': '자유보유', 'q5c': '곧 입주 가능 (2027년까지)', 'q5d': '가장 낮은 가격',
        'res': '가장 잘 맞는 프로젝트', 'resp': '답변을 바탕으로 골랐습니다. 가격은 공개된 총액 시작가이며 바뀔 수 있습니다.',
        'none': '모든 조건에 맞는 프로젝트가 없어 가장 가까운 곳을 보여 드립니다.', 'send': '후보 목록을 WhatsApp으로 Keith에게 보내기',
        'all': '전체 프로젝트 보기', 'view': '프로젝트 보기 →',
        'w_budget': '예산 내', 'w_over': '예산을 조금 초과', 'w_area': '원하는 지역', 'w_rooms': '원하는 침실 수',
        'w_rail': '역 근처', 'w_fh': '자유보유', 'w_ready': '2027년까지 완공'},
}
import opencc
_cc = opencc.OpenCC('s2tw').convert
for _l in T:
    T[_l]['p_from'] = HB.T[_l]['p_from']
T['zh-TW'] = {k: _cc(v) for k, v in T['zh-CN'].items()}
STATES = []
for d in data:
    if d['st'] and d['st'] not in STATES:
        STATES.append(d['st'])
order = ['Kuala Lumpur', 'Selangor', 'Penang', 'Johor']
STATES = [s for s in order if s in STATES] + sorted(s for s in STATES if s not in order)

CSS = '''
:root{--ink:#15142b;--grey:#5f5e74;--line:rgba(21,20,43,.09);--gold:#5E60CE;--bg:#F7F6FB;}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:Inter,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6}a{color:inherit;text-decoration:none}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif;line-height:1.2}
.fq{max-width:860px;margin:0 auto;padding:120px 5vw 70px}
.fq-h{text-align:center;margin-bottom:26px}.fq-h .eb{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);font-weight:800}
.fq-h h1{font-size:clamp(30px,4.6vw,46px);margin:8px 0 10px}.fq-h p{color:var(--grey);max-width:620px;margin:0 auto}
.fq-card{background:#fff;border-radius:26px;box-shadow:0 24px 60px rgba(29,27,79,.12);padding:30px;border:1px solid var(--line)}
.fq-bar{height:8px;background:#efeefb;border-radius:100px;overflow:hidden;margin-bottom:10px}.fq-bar i{display:block;height:100%;background:linear-gradient(90deg,#5E60CE,#9a98f0);border-radius:100px;transition:width .35s ease}
.fq-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;font-size:13px;font-weight:700;color:var(--grey)}
.fq-top button{all:unset;cursor:pointer;color:var(--gold);font-weight:700}.fq-top button[hidden]{display:none}
.fq-q h2{font-size:clamp(22px,3vw,30px);margin-bottom:18px}
.fq-opts{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.fq-o{all:unset;box-sizing:border-box;cursor:pointer;display:flex;align-items:center;gap:12px;padding:18px;border-radius:18px;border:2px solid #ebe9f7;background:#fbfaff;font-weight:700;font-size:15.5px;transition:all .2s}
.fq-o:hover,.fq-o:focus-visible{border-color:var(--gold);background:#f3f1fa;transform:translateY(-2px)}.fq-o.on{border-color:var(--gold);background:#5E60CE;color:#fff}
.fq-o em{font-style:normal;font-size:24px;width:40px;height:40px;border-radius:12px;background:#fff;display:flex;align-items:center;justify-content:center;flex:0 0 40px;box-shadow:0 2px 6px rgba(0,0,0,.06)}
.fq-q{animation:fqIn .3s ease}@keyframes fqIn{from{opacity:0;transform:translateX(16px)}to{opacity:1;transform:none}}
.fq-res h2{font-size:clamp(24px,3vw,32px);margin-bottom:6px}.fq-res>p{color:var(--grey);font-size:13.5px;margin-bottom:16px}
.fq-note{background:#fff7e0;color:#7a5200;border-radius:12px;padding:10px 14px;font-size:13.5px;font-weight:600;margin-bottom:14px}
.fq-list{display:grid;gap:14px}.fq-it{display:grid;grid-template-columns:150px 1fr;gap:16px;background:#fbfaff;border:1px solid var(--line);border-radius:18px;overflow:hidden;transition:box-shadow .2s}
.fq-it:hover{box-shadow:0 12px 28px rgba(29,27,79,.1)}.fq-it img{width:100%;height:100%;min-height:120px;object-fit:cover;display:block;background:#eee}
.fq-it div{padding:14px 16px 14px 0}.fq-it h3{font-size:19px}.fq-it small{display:block;color:var(--grey);font-size:12.5px;margin:2px 0 6px}
.fq-it b.pr{color:var(--gold);font-size:14px}.fq-why{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}.fq-why span{font-size:11.5px;font-weight:700;background:#e9f9ef;color:#1f7a45;padding:3px 9px;border-radius:100px}
.fq-why span.w{background:#fff3d6;color:#8a5a00}.fq-it .vw{display:inline-block;margin-top:8px;font-size:13px;font-weight:700;color:var(--gold)}
.fq-act{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px}.fq-act a,.fq-act button{all:unset;box-sizing:border-box;cursor:pointer;text-align:center;padding:14px 20px;border-radius:14px;font-weight:700;font-size:14.5px}
.fq-act .wa{background:#25D366;color:#fff;flex:1 1 280px;box-shadow:0 10px 24px rgba(37,211,102,.3)}.fq-act .wa:hover{background:#1ebe5a}
.fq-act .gh{border:1.5px solid #d9d6ea;color:#1d1b4f}.fq-act .gh:hover{border-color:var(--gold);color:var(--gold)}
footer{border-top:1px solid var(--line);padding:26px 5vw;font-size:13px;color:var(--grey);text-align:center}
@media(max-width:600px){.fq-card{padding:20px}.fq-it{grid-template-columns:110px 1fr}.fq-it div{padding:12px 12px 12px 0}}
'''

JS = r'''<script>(function(){var D=%s,T=%s,ST=%s,WA="https://api.whatsapp.com/send/?phone=60102821568&type=phone_number&app_absent=0&text=";
function lg(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}return T[l]?l:"en";}
var A={},step=0,box=document.getElementById("fqBox");
var Q=[["q1",[["live","🏡","q1a"],["invest","📈","q1b"],["both","🤝","q1c"]]],
 ["q2",[["0-500000","💰","q2a"],["500000-800000","💰","q2b"],["800000-1200000","💎","q2c"],["1200000-2000000","💎","q2d"],["2000000-99000000","👑","q2e"]]],
 ["q3",ST.map(function(s){return [s,"📍",null,s];}).concat([["any","🗺️","any"]])],
 ["q4",[["1","🛏️","q4a"],["2","🛏️","q4b"],["3","🏠","q4c"]]],
 ["q5",[["rail","🚆","q5a"],["fh","📜","q5b"],["ready","🔑","q5c"],["value","🏷️","q5d"]]]];
function t(k){var l=lg();return (T[l]&&T[l][k])||T.en[k]||k;}
function e(s){var d=document.createElement("div");d.textContent=s;return d.innerHTML;}
function pr(s){var m=/^From (RM[\d,.]+(?: mil)?) \(Gross\)$/.exec(s||"");return m?t("p_from").replace("{p}",m[1]):s;}
function draw(){if(step>=Q.length)return result();var q=Q[step];
 box.innerHTML='<div class="fq-bar"><i style="width:'+(step/Q.length*100)+'%%"></i></div><div class="fq-top"><span>'+e(t("step").replace("{n}",step+1))+'</span><button type="button" id="fqBack"'+(step?'':' hidden')+'>'+e(t("back"))+'</button></div>'+
 '<div class="fq-q"><h2>'+e(t(q[0]))+'</h2><div class="fq-opts">'+q[1].map(function(o){return '<button type="button" class="fq-o'+(A[q[0]]===o[0]?' on':'')+'" data-v="'+e(o[0])+'"><em>'+o[1]+'</em><span>'+e(o[3]||t(o[2]))+'</span></button>';}).join("")+'</div></div>';
 box.querySelectorAll(".fq-o").forEach(function(b){b.addEventListener("click",function(){A[q[0]]=b.getAttribute("data-v");step++;draw();window.scrollTo({top:box.getBoundingClientRect().top+pageYOffset-110,behavior:"smooth"});});});
 var bk=document.getElementById("fqBack");if(bk)bk.addEventListener("click",function(){step--;draw();});}
function score(){var b=A.q2.split("-").map(Number),lo=b[0],hi=b[1],r=+A.q4;
 return D.map(function(d){var s=0,w=[];
  if(d.p){if(d.p>=lo*0.85&&d.p<=hi){s+=4;w.push(["w_budget",0]);}else if(d.p>hi&&d.p<=hi*1.15){s+=1;w.push(["w_over",1]);}else s-=4;}else s-=2;
  if(A.q3!=="any"){if(d.st===A.q3){s+=3;w.push(["w_area",0]);}else s-=3;}
  if(d.r0!=null&&d.r1!=null&&((r===3&&d.r1>=3)||(r<3&&d.r0<=r&&d.r1>=r))){s+=2;w.push(["w_rooms",0]);}
  if(d.rail){s+=(A.q5==="rail"?2:0)+(A.q1!=="live"?1:0);w.push(["w_rail",0]);}
  if(d.fh){s+=A.q5==="fh"?2:0.5;w.push(["w_fh",0]);}
  if(d.ready){s+=A.q5==="ready"?2:0;if(A.q5==="ready")w.push(["w_ready",0]);}
  return {d:d,s:s,w:w};}).sort(function(a,b){return b.s-a.s||(A.q5==="value"?(a.d.p||9e9)-(b.d.p||9e9):0)||((a.d.p||9e9)-(b.d.p||9e9));});}
function result(){var R=score(),top=R.slice(0,5),full=top.length&&top[0].s>=8;
 if(A.q5==="value")top.sort(function(a,b){return (a.d.p||9e9)-(b.d.p||9e9);});
 box.innerHTML='<div class="fq-bar"><i style="width:100%%"></i></div><div class="fq-res"><h2>'+e(t("res"))+'</h2><p>'+e(t("resp"))+'</p>'+(full?'':'<div class="fq-note">'+e(t("none"))+'</div>')+
 '<div class="fq-list">'+top.map(function(x){var d=x.d;return '<a class="fq-it" href="property/'+d.s+'.html">'+(d.img?'<img src="'+d.img+'" alt="'+e(d.n)+'" loading="lazy">':'<i></i>')+'<div><h3>'+e(d.n)+'</h3><small>'+e(d.loc)+'</small><b class="pr">'+e(pr(d.pt))+'</b><div class="fq-why">'+x.w.map(function(w){return '<span'+(w[1]?' class="w"':'')+'>'+e(t(w[0]))+'</span>';}).join("")+'</div><span class="vw">'+e(t("view"))+'</span></div></a>';}).join("")+'</div>'+
 '<div class="fq-act"><a class="wa" id="fqWa" target="_blank" rel="noopener">'+e(t("send"))+'</a><button type="button" class="gh" id="fqAgain">'+e(t("again"))+'</button><a class="gh" href="projects.html">'+e(t("all"))+'</a></div></div>';
 var lab=function(qi,v){var o=Q[qi][1].filter(function(o){return o[0]===v;})[0];return o?(o[3]||T.en[o[2]]):v;};
 var msg="(KNRE) Hi Keith, I used Find My Home on your website.\nFor: "+lab(0,A.q1)+"\nBudget: "+lab(1,A.q2)+"\nArea: "+lab(2,A.q3)+"\nBedrooms: "+lab(3,A.q4)+"\nMost important: "+lab(4,A.q5)+"\nMy shortlist: "+top.map(function(x){return x.d.n;}).join(", ");
 document.getElementById("fqWa").href=WA+encodeURIComponent(msg);
 document.getElementById("fqAgain").addEventListener("click",function(){A={};step=0;draw();});
 try{if(window.gtag)gtag("event","quiz_complete",{budget:A.q2,area:A.q3,purpose:A.q1});}catch(z){}}
function labels(){document.querySelectorAll("[data-fq]").forEach(function(el){el.textContent=t(el.getAttribute("data-fq"));});draw();}
labels();document.addEventListener("DOMContentLoaded",function(){var s=window.knSetLang;if(typeof s==="function"){window.knSetLang=function(){var r=s.apply(this,arguments);labels();return r;};}labels();});
})();</script>'''

en = T['en']
page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Find My Home: New Launch Match in 3 Minutes | Keith Nah</title>
<meta name="description" content="Answer five quick questions on budget, area, bedrooms and what matters most, and see the new launch projects in Malaysia that fit you best.">
<link rel="canonical" href="https://keithnah.com/find-my-home.html">
<meta property="og:type" content="website">
<meta property="og:title" content="Find your home in 3 minutes | Keith Nah">
<meta property="og:description" content="Five quick questions, then the new launches that fit you best.">
<meta property="og:url" content="https://keithnah.com/find-my-home.html">
<link rel="icon" type="image/png" href="images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
<style>%s</style>
</head>
<body>
<header>
  <a class="logo" href="./"><img src="images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Malaysia Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="https://api.whatsapp.com/send/?phone=60102821568&amp;text=%%28KNRE%%29+Hi+Keith%%2C+I+am+looking+for+a+new+home.&amp;type=phone_number&amp;app_absent=0" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
<main class="fq">
  <div class="fq-h"><span class="eb" data-fq="eb">%s</span><h1 data-fq="h1">%s</h1><p data-fq="p">%s</p></div>
  <div class="fq-card" id="fqBox"></div>
</main>
<footer>&copy; 2026 Keith Nah Real Estate · <a href="projects.html">All projects</a> · <a href="privacy-policy.html">Privacy Policy</a></footer>
<script src="lead-tracker.js"></script>
%s
</body>
</html>
''' % (CSS, E(en['eb']), E(en['h1']), E(en['p']), JS % (json.dumps(data, ensure_ascii=False), json.dumps(T, ensure_ascii=False), json.dumps(STATES)))
open('find-my-home.html', 'w', encoding='utf-8').write(SH.apply(page, '', 'projects.html'))
print('find my home: %d projects, %d states' % (len(data), len(STATES)))


# ---------- entry points: a link under the home hero buttons and under the projects search ----------
LINK = {'en': ('Not sure where to start?', 'Find your home in 3 minutes →'),
        'zh-CN': ('不知道从哪里开始？', '3 分钟帮你找房 →'),
        'ms': ('Tidak pasti mahu mula di mana?', 'Cari rumah anda dalam 3 minit →'),
        'ja': ('どこから探せばいいか迷ったら', '3分でおうち探し →'),
        'ko': ('어디서부터 시작할지 모르겠다면?', '3분 만에 내 집 찾기 →')}
LINK['zh-TW'] = tuple(_cc(x) for x in LINK['zh-CN'])


def entry(cls):
    return ('<!-- KN-QUIZ:START --><style>.kq{display:flex;justify-content:center;flex-wrap:wrap;gap:6px 10px;align-items:center;'
            'font:500 15px Inter,sans-serif;margin:%s;}.kq span{opacity:.75;}.kq a{display:inline-flex;align-items:center;padding:8px 16px;'
            'border-radius:999px;background:#5E60CE;color:#fff;font-weight:700;text-decoration:none;transition:transform .2s,box-shadow .2s,background .2s;}'
            '.kq a:hover{background:#4a4cc0;transform:translateY(-2px);box-shadow:0 8px 20px rgba(94,96,206,.35);}</style>'
            '<div class="kq %s"><span data-kq="0">%s</span><a href="find-my-home.html" data-kq="1">%s</a></div>'
            '<script>(function(){var L=%s;function f(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}var t=L[l]||L.en;'
            'document.querySelectorAll("[data-kq]").forEach(function(x){x.textContent=t[+x.getAttribute("data-kq")];});}f();'
            'document.addEventListener("DOMContentLoaded",function(){var s=window.setLanguage;if(typeof s==="function")window.setLanguage=function(){var r=s.apply(this,arguments);f();return r;};f();});})();</script>'
            '<!-- KN-QUIZ:END -->') % ('-36px 0 40px' if cls == 'kq-home' else '18px 0 0', cls, html.escape(LINK['en'][0]), html.escape(LINK['en'][1]),
                                       json.dumps(LINK, ensure_ascii=False))


def put(page, anchor, block):
    t = open(page, encoding='utf-8').read()
    t = re.sub(r'<!-- KN-QUIZ:START -->.*?<!-- KN-QUIZ:END -->', '', t, flags=re.S)
    i = t.index(anchor) + len(anchor)
    open(page, 'w', encoding='utf-8').write(t[:i] + block + t[i:])


# home page: no link (Keith's choice); remove an old one if present
_h = open('index.html', encoding='utf-8').read()
_h2 = re.sub(r'<!-- KN-QUIZ:START -->.*?<!-- KN-QUIZ:END -->', '', _h, flags=re.S)
if _h2 != _h:
    open('index.html', 'w', encoding='utf-8').write(_h2)
put('projects.html', '  </form>', entry('kq-proj'))
print('find-my-home.html written, entry link on the projects page')
