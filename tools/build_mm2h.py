"""MM2H page extras (mm2h.html): tier checker, regional programmes, projects that meet each tier's
property minimum, how it works, costs to budget and FAQ. Inserted after the tier comparison.

Figures are the published programme terms as reported in 2026 (federal tiers, Johor Forest City
SFZ, Sarawak S-MM2H). Sabah's terms changed recently, so the page sends readers to Keith for the
current Sabah figures instead of stating them. PREVIEW: English only, not in build_all yet.
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
import hubs_data as HB

E = html.escape
src = open('projects.html', encoding='utf-8').read()
i = src.index('const PROJECT_DETAILS = ')
P = json.JSONDecoder().raw_decode(src[src.index('=', i) + 1:].lstrip())[0]
IDX = json.load(open(os.path.join(HERE, 'project_index.json'), encoding='utf-8'))


def photo(slug):
    f = 'property/%s.html' % slug
    m = re.search(r'og:image" content="https://keithnah\.com/([^"]+)"', open(f, encoding='utf-8').read()) if os.path.exists(f) else None
    return m.group(1) if m else ''


PR = []
for k, p in enumerate(P):
    v = HB.price(p.get('price'))
    if v:
        PR.append({'n': p['name'], 's': IDX[k]['slug'], 'p': v, 'a': '%s, %s' % (IDX[k]['area'], IDX[k]['state']),
                   'st': IDX[k]['state'], 'img': photo(IDX[k]['slug'])})
PR.sort(key=lambda x: x['p'])

TIERS = [('Silver', 600000, 'USD 150,000', '5 years'), ('Gold', 1000000, 'USD 500,000', '15 years'), ('Platinum', 2000000, 'USD 1,000,000', '20 years')]


def tier_projects(lo, hi):
    return [x for x in PR if lo <= x['p'] < hi]


cards = ''
for k, (name, lo, fd, yrs) in enumerate(TIERS):
    hi = TIERS[k + 1][1] if k + 1 < len(TIERS) else 10 ** 12
    lst = [x for x in PR if x['p'] >= lo]
    band = tier_projects(lo, hi)
    pick = (band or lst)[:4]
    items = ''.join('<a class="mx-p" href="property/%s.html"><img src="%s" alt="%s" loading="lazy"><span><b>%s</b><small>%s</small><em>From %s</em></span></a>'
                    % (x['s'], x['img'], E(x['n']), E(x['n']), E(x['a']), HB.rm(x['p'])) for x in pick)
    cards += ('<div class="mx-tc"><div class="mx-th %s"><b>%s</b><span>Property from %s</span></div>'
              '<p><b>%d</b> project%s on this site start%s at %s or more.</p><div class="mx-ps">%s</div></div>'
              % (name.lower(), name, HB.rm(lo), len(lst), '' if len(lst) == 1 else 's', 's' if len(lst) == 1 else '', HB.rm(lo), items))

FAQ = [
    ('Do I have to buy property to get MM2H?',
     'Yes, for the Silver, Gold and Platinum tiers. Since the 2024 changes, each tier needs a fixed deposit and a residential property purchase above a minimum price: RM600,000 for Silver, RM1 million for Gold and RM2 million for Platinum.'),
    ('Can I sell the property later?',
     'The property bought for MM2H generally has to be kept for 10 years. Check the current holding rule with a licensed MM2H agent before you buy.'),
    ('Can I work in Malaysia on MM2H?',
     'Only the Platinum tier allows you to work, invest and run a business. Silver and Gold pass holders cannot take up employment in Malaysia.'),
    ('How long do I need to stay in Malaysia each year?',
     'The federal tiers ask for a minimum stay of about 90 days a year, and Sarawak asks for 30 days a year in Sarawak. These rules have changed before, so confirm the current minimum when you apply.'),
    ('Is the foreign buyer minimum price the same as the MM2H minimum?',
     'Not always. Each state sets its own minimum price for foreign buyers, and in many areas it is higher than the Silver tier minimum. Keith checks both limits for the area you want before you shortlist.'),
    ('Who handles the application?',
     'Applications go through a licensed MM2H agent approved by the Ministry of Tourism, Arts and Culture (MOTAC). Keith helps with the property side: the shortlist, the purchase and the timing with your MM2H approval.'),
]
faq_html = ''.join('<details class="mx-q"><summary>%s</summary><p>%s</p></details>' % (E(q), E(a)) for q, a in FAQ)
faq_ld = json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
    {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ]}, ensure_ascii=False)

CSS = '''<style>
.mx{max-width:1180px;margin:0 auto;padding:70px 5vw 10px}.mx h2{font-family:'Playfair Display',Georgia,serif;font-size:clamp(28px,3.6vw,40px);line-height:1.2;margin:6px 0 10px;text-align:center}
.mx .eb{display:block;text-align:center;font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--gold,#5E60CE);font-weight:800}
.mx .ld{text-align:center;color:#5f5e74;max-width:680px;margin:0 auto 26px}
.mx-ck{background:#fff;border:1px solid rgba(21,20,43,.09);border-radius:26px;box-shadow:0 24px 60px rgba(29,27,79,.10);padding:28px;display:grid;grid-template-columns:1fr 1fr;gap:26px}
.mx-f label{display:block;font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#5f5e74;margin:0 0 8px}
.mx-f .op{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px}.mx-f .op button{border:1.5px solid #dcd9ee;background:#fff;border-radius:999px;padding:9px 14px;font:600 13.5px Inter,sans-serif;color:#15142b;cursor:pointer}
.mx-f .op button.on{background:#5E60CE;border-color:#5E60CE;color:#fff}
.mx-r{background:#f6f5ff;border-radius:20px;padding:22px}.mx-r h3{font-family:'Playfair Display',Georgia,serif;font-size:26px;margin:0 0 6px}.mx-r p{color:#5f5e74;font-size:14px;margin:0 0 12px}
.mx-r ul{margin:0 0 14px;padding-left:18px;font-size:14px}.mx-r li{margin:4px 0}.mx-r .no{color:#a33}.mx-r a.w{display:block;text-align:center;background:#25D366;color:#fff;font-weight:700;padding:13px;border-radius:14px;text-decoration:none;margin-top:10px}
.mx-r a.l{display:inline-block;color:#5E60CE;font-weight:700;font-size:14px;text-decoration:none}
.mx-g{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}
.mx-c{background:#fff;border:1px solid rgba(21,20,43,.09);border-radius:20px;padding:22px}.mx-c small{font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#5E60CE}
.mx-c h3{font-family:'Playfair Display',Georgia,serif;font-size:21px;margin:4px 0 8px}.mx-c p{font-size:13.5px;color:#5f5e74;margin:0 0 10px}.mx-c ul{margin:0;padding-left:18px;font-size:13.5px}.mx-c li{margin:3px 0}
.mx-tg{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.mx-tc{background:#fff;border:1px solid rgba(21,20,43,.09);border-radius:20px;overflow:hidden}
.mx-th{padding:16px 20px;color:#fff}.mx-th b{display:block;font-size:20px}.mx-th span{font-size:13px;opacity:.85}.mx-th.silver{background:linear-gradient(120deg,#7b8494,#a9b1bd)}
.mx-th.gold{background:linear-gradient(120deg,#b8862b,#e0b65a)}.mx-th.platinum{background:linear-gradient(120deg,#2c2c4a,#5E60CE)}
.mx-tc>p{padding:14px 20px 4px;margin:0;font-size:14px;color:#5f5e74}.mx-ps{padding:6px 14px 16px}
.mx-p{display:grid;grid-template-columns:64px 1fr;gap:10px;align-items:center;padding:8px 6px;border-radius:12px;text-decoration:none;color:#15142b}.mx-p:hover{background:#f6f5ff}
.mx-p img{width:64px;height:48px;object-fit:cover;border-radius:8px;background:#eee}.mx-p b{display:block;font-size:14px;line-height:1.25}.mx-p small{display:block;font-size:11.5px;color:#5f5e74}.mx-p em{font-style:normal;font-size:12.5px;font-weight:700;color:#5E60CE}
.mx-st{counter-reset:s;display:grid;grid-template-columns:repeat(5,1fr);gap:14px}.mx-st div{background:#fff;border:1px solid rgba(21,20,43,.09);border-radius:18px;padding:18px}
.mx-st div:before{counter-increment:s;content:counter(s);display:inline-flex;width:30px;height:30px;border-radius:50%;background:#5E60CE;color:#fff;font-weight:800;align-items:center;justify-content:center;margin-bottom:8px}
.mx-st b{display:block;font-size:15px}.mx-st span{font-size:13px;color:#5f5e74}
.mx-q{background:#fff;border:1px solid rgba(21,20,43,.09);border-radius:16px;padding:16px 20px;margin-bottom:10px}.mx-q summary{font-weight:700;cursor:pointer}.mx-q p{margin:10px 0 0;color:#5f5e74;font-size:14px}
.mx-nt{font-size:12.5px;color:#5f5e74;text-align:center;max-width:760px;margin:18px auto 0}
@media(max-width:900px){.mx-ck{grid-template-columns:1fr}.mx-tg{grid-template-columns:1fr}.mx-st{grid-template-columns:1fr 1fr}}
@media(max-width:520px){.mx-st{grid-template-columns:1fr}.mx-ck{padding:18px}}
</style>'''

JS = r'''<script>(function(){var PR=%s,A={age:null,fd:null,pb:null,work:null};
var box=document.getElementById("mxR");function e(s){var d=document.createElement("div");d.textContent=s;return d.innerHTML;}
function rm(v){return v>=1e6?"RM"+(v/1e6).toFixed(2).replace(/\.?0+$/,"")+"M":"RM"+Math.round(v/1e3)+"K";}
var T=[["Platinum",1000000,2000000,25,"USD 1,000,000","RM2 million","20-year pass, renewable. You may work, invest and run a business."],
["Gold",500000,1000000,25,"USD 500,000","RM1 million","15-year pass, renewable. No employment."],
["Silver",150000,600000,25,"USD 150,000","RM600,000","5-year pass, renewable. No employment."]];
function draw(){if(A.age===null||A.fd===null||A.pb===null||A.work===null){box.innerHTML='<h3>Your result</h3><p>Answer the four questions to see which MM2H route fits you.</p>';return;}
var fit=null;for(var i=0;i<T.length;i++){var t=T[i];if(A.fd>=t[1]&&A.pb>=t[2]&&A.age>=t[3]&&(A.work==="no"||t[0]==="Platinum")){fit=t;break;}}
var sfz=A.age>=21&&A.fd>=(A.age>=50?32000:65000)&&A.pb>=500000&&A.work==="no";
var h="",lo=0,msg="";
if(fit){lo=fit[2];h='<h3>MM2H '+fit[0]+'</h3><p>Based on your answers, the '+fit[0]+' tier is the best fit.</p><ul><li>Fixed deposit: '+fit[4]+'</li><li>Property: from '+fit[5]+', kept for 10 years</li><li>'+fit[6]+'</li></ul>';msg=fit[0];}
else if(sfz){lo=500000;h='<h3>Johor Forest City SFZ</h3><p>The federal tiers do not fit yet, but the Forest City special zone may.</p><ul><li>Fixed deposit: '+(A.age>=50?'USD 32,000 (age 50+)':'USD 65,000 (age 21 to 49)')+'</li><li>Property: Forest City home from the developer, from RM500,000</li><li>10-year pass, renewable</li></ul>';msg="Forest City SFZ";}
else{h='<h3>Not yet</h3><p>Your answers do not meet a tier yet.</p><ul>'+(A.work==="yes"?'<li>Working in Malaysia needs the Platinum tier: USD 1,000,000 deposit and RM2 million property.</li>':'')+(A.age<25?'<li>Silver, Gold and Platinum start at age 25; Forest City SFZ from 21.</li>':'')+'<li>The lowest federal tier, Silver, needs USD 150,000 and a property from RM600,000.</li></ul>';msg="not sure yet";}
if(lo){var m=PR.filter(function(x){return x.p>=lo&&x.p<=Math.max(lo,A.pb);});if(!m.length)m=PR.filter(function(x){return x.p>=lo;});
h+='<p><b>'+m.length+'</b> project'+(m.length===1?'':'s')+' on this site fit this property level'+(msg==="Forest City SFZ"?' (Forest City needs its own developer project; ask Keith)':'')+'.</p>'+m.slice(0,3).map(function(x){return '<a class="mx-p" href="property/'+x.s+'.html"><img src="'+x.img+'" alt="" loading="lazy"><span><b>'+e(x.n)+'</b><small>'+e(x.a)+'</small><em>From '+rm(x.p)+'</em></span></a>';}).join("");}
var txt="(KNRE) Hi Keith, I used the MM2H checker on your website. Result: "+msg+". Age: "+A.agel+", deposit: "+A.fdl+", property budget: "+A.pbl+", want to work: "+A.work+".";
h+='<a class="w" target="_blank" rel="noopener" href="https://api.whatsapp.com/send/?phone=60102821568&type=phone_number&app_absent=0&text='+encodeURIComponent(txt)+'">Ask Keith about my MM2H plan</a>';
box.innerHTML=h;}
document.querySelectorAll(".mx-f .op").forEach(function(g){g.addEventListener("click",function(ev){var b=ev.target.closest("button");if(!b)return;
g.querySelectorAll("button").forEach(function(x){x.classList.toggle("on",x===b);});var k=g.getAttribute("data-k"),v=b.getAttribute("data-v");A[k]=k==="work"?v:+v;A[k+"l"]=b.textContent;draw();
if(typeof gtag==="function"&&A.age!==null&&A.fd!==null&&A.pb!==null&&A.work!==null)gtag("event","mm2h_check");});});draw();})();</script>'''


def opts(k, items):
    return '<div class="op" data-k="%s">%s</div>' % (k, ''.join('<button type="button" data-v="%s">%s</button>' % (v, E(t)) for v, t in items))


BLOCK = '''<!-- KN-MM2H:START -->%s
<section class="mx" id="checker"><span class="eb">Quick check</span><h2>Which MM2H route fits you?</h2>
<p class="ld">Four questions, then the tier that fits and projects on this site at that property level. A guide only: a licensed MM2H agent confirms eligibility.</p>
<div class="mx-ck"><div class="mx-f">
<label>Your age</label>%s<label>Money you can place in a fixed deposit</label>%s<label>Property budget</label>%s<label>Do you need to work or run a business in Malaysia?</label>%s
</div><div class="mx-r" id="mxR"></div></div></section>

<section class="mx"><span class="eb">Where you live</span><h2>Four MM2H programmes</h2>
<p class="ld">The federal programme covers most of Malaysia. Johor's Forest City zone, Sarawak and Sabah run their own versions with different rules.</p>
<div class="mx-g">
<div class="mx-c"><small>Federal MM2H</small><h3>Kuala Lumpur, Selangor, Penang, Johor and more</h3><p>Silver, Gold and Platinum tiers.</p><ul><li>Deposit USD 150,000 to USD 1,000,000</li><li>Property from RM600,000 to RM2 million</li><li>Pass of 5, 15 or 20 years</li></ul></div>
<div class="mx-c"><small>Special Financial Zone</small><h3>Johor Forest City</h3><p>Near Singapore, the lowest entry point.</p><ul><li>Deposit USD 65,000 (age 21 to 49) or USD 32,000 (50+)</li><li>Forest City home from the developer, from RM500,000</li><li>10-year pass, about 90 days a year</li></ul></div>
<div class="mx-c"><small>S-MM2H</small><h3>Sarawak</h3><p>Sarawak's own programme, run by the state.</p><ul><li>Main applicant aged 30 or above</li><li>Deposit RM500,000 with a bank in Sarawak</li><li>At least 30 days a year in Sarawak</li></ul></div>
<div class="mx-c"><small>Sabah MM2H</small><h3>Sabah and Kota Kinabalu</h3><p>Sabah runs its own stream, and its terms were updated recently.</p><ul><li>Deposit and income levels set by the state</li><li>Ask Keith for the current Sabah figures before you plan</li></ul></div>
</div></section>

<section class="mx"><span class="eb">Projects</span><h2>Homes that meet each tier</h2>
<p class="ld">New launches on this site at or above each tier's property minimum, by starting price. Your state's foreign buyer minimum may be higher.</p>
<div class="mx-tg">%s</div></section>

<section class="mx"><span class="eb">How it works</span><h2>From first chat to your pass</h2>
<div class="mx-st"><div><b>Pick your tier and area</b><span>Budget, family and how you want to live.</span></div><div><b>Apply through a licensed agent</b><span>A MOTAC-licensed MM2H agent files the application.</span></div>
<div><b>Approval in principle</b><span>You receive the conditional approval letter.</span></div><div><b>Deposit and property</b><span>Open the fixed deposit and buy the home; Keith handles the property side.</span></div>
<div><b>Pass endorsed</b><span>Your MM2H pass goes into your passport.</span></div></div></section>

<section class="mx"><span class="eb">Budget</span><h2>Costs beyond the deposit</h2>
<div class="mx-g">
<div class="mx-c"><h3>Programme fees</h3><p>One-off participation fees and pass fees per family member, set by tier.</p></div>
<div class="mx-c"><h3>Stamp duty and legal fees</h3><p>Foreign buyers pay a higher stamp duty rate. Work it out in the <a href="calculator.html">calculator</a>.</p></div>
<div class="mx-c"><h3>State approval</h3><p>Foreign purchases need state consent, and each state sets its own minimum price for foreign buyers.</p></div>
<div class="mx-c"><h3>10-year hold</h3><p>Plan for a home you are happy to keep for 10 years, or one that rents well while you are away.</p></div>
</div></section>

<section class="mx"><span class="eb">FAQ</span><h2>MM2H questions buyers ask</h2><div style="max-width:820px;margin:0 auto">%s</div>
<p class="mx-nt">Programme terms are set by the Malaysian federal and state governments and change from time to time. This page is a guide, not immigration advice; confirm the current rules with a licensed MM2H agent.</p></section>
<script type="application/ld+json">%s</script>
%s<!-- KN-MM2H:END -->''' % (CSS, opts('age', [(21, '21 to 24'), (25, '25 to 49'), (50, '50 or above')]),
                          opts('fd', [(30000, 'Under USD 65,000'), (65000, 'USD 65,000 to 149,999'), (150000, 'USD 150,000 to 499,999'), (500000, 'USD 500,000 to 999,999'), (1000000, 'USD 1 million or more')]),
                          opts('pb', [(450000, 'Under RM500,000'), (500000, 'RM500,000 to 599,999'), (600000, 'RM600,000 to 999,999'), (1000000, 'RM1M to RM1.99M'), (2000000, 'RM2 million or more')]),
                          opts('work', [('no', 'No'), ('yes', 'Yes')]), cards, faq_html, faq_ld,
                          JS % json.dumps([{k: x[k] for k in ('n', 's', 'p', 'a', 'img')} for x in PR], ensure_ascii=False))

out = sys.argv[1] if len(sys.argv) > 1 else 'mm2h.html'
t = open('mm2h.html', encoding='utf-8').read()
t = re.sub(r'<!-- KN-MM2H:START -->.*?<!-- KN-MM2H:END -->', '', t, flags=re.S)
i = t.index('<section class="mm2h-tiers">')
j = t.index('</section>', i) + len('</section>')
t = t[:j] + '\n' + BLOCK + t[j:]
# the old intro said MM2H does not need a property purchase; since 2024 every federal tier does
t = t.replace("MM2H is separate from property ownership itself — it doesn't require buying real estate to qualify on its own, but combining the two is common among Keith's clients who want both a home and a long-stay pass in Kuala Lumpur.",
              "Since 2024 every federal tier also needs a residential property purchase above a minimum price, so choosing the tier and choosing the home go together. Keith helps clients match the two.")
open(out, 'w', encoding='utf-8').write(t)
print('mm2h: extras added (%d priced projects)' % len(PR))
