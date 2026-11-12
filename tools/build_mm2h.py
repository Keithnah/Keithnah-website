"""MM2H library and enquiry form.

- Every article in tools/mm2h_articles.json becomes its own page: mm2h/<slug>.html.
- mm2h.html gets an "MM2H Library" section (articles in two groups) and an MM2H enquiry form
  under the tier comparison. The form saves the enquiry in the KNRE Leads sheet and Telegram
  (through lead-tracker.js, as a Quick Enquiry marked "MM2H"), then offers WhatsApp.
PREVIEW: English only, not in build_all yet.
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
import site_header as SH

E = html.escape
A = json.load(open(os.path.join(HERE, 'mm2h_articles.json'), encoding='utf-8'))
GROUPS = [('guide', 'Understand MM2H', 'Tiers, costs, property rules and the steps, explained plainly.'),
          ('compare', 'MM2H vs other countries', 'How Malaysia compares with other long-stay and residency programmes.')]
WA = 'https://api.whatsapp.com/send/?phone=60102821568&type=phone_number&app_absent=0&text='

ART_CSS = '''
:root{--ink:#15142b;--grey:#5f5e74;--line:rgba(21,20,43,.09);--gold:#5E60CE;--bg:#F7F6FB;}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:Inter,sans-serif;background:var(--bg);color:var(--ink);line-height:1.7}a{color:inherit}
h1,h2{font-family:'Playfair Display',Georgia,serif;line-height:1.2}
.ma-top{background:linear-gradient(135deg,#1d1b4f,#3b3cb0);color:#fff;padding:120px 5vw 46px}
.ma-top .in{max-width:860px;margin:0 auto}.ma-cr{font-size:13px;opacity:.75}.ma-cr a{text-decoration:none}
.ma-tag{display:inline-block;margin:18px 0 12px;font-size:11.5px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;background:rgba(255,255,255,.14);padding:5px 12px;border-radius:999px}
.ma-top h1{font-size:clamp(28px,4.4vw,44px)}.ma-top p{margin-top:12px;font-size:17px;opacity:.85;max-width:720px}.ma-top small{display:block;margin-top:14px;opacity:.7;font-size:13px}
.ma{max-width:860px;margin:-26px auto 0;padding:0 5vw 60px;position:relative}
.ma-f{display:grid;grid-template-columns:repeat(4,1fr);background:#fff;border-radius:20px;box-shadow:0 18px 44px rgba(29,27,79,.12);overflow:hidden}
.ma-f div{padding:16px 18px;border-right:1px solid var(--line)}.ma-f div:last-child{border:0}.ma-f small{display:block;font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--grey)}
.ma-f b{font-size:15.5px}
.ma-s{display:grid;grid-template-columns:54px 1fr;gap:6px 18px;margin-top:38px}.ma-s i{font-style:normal;font:700 30px 'Playfair Display',Georgia,serif;color:#c9c6f2;line-height:1}
.ma-s h2{font-size:24px;margin-bottom:6px}.ma-s p{color:#33324a;font-size:16px}
.ma-k{margin-top:40px;background:#fff;border-left:5px solid var(--gold);border-radius:16px;padding:22px 24px;display:grid;grid-template-columns:56px 1fr;gap:16px;align-items:start}
.ma-k img{width:56px;height:56px;border-radius:50%;background:#15142b}.ma-k b{display:block;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin-bottom:4px}.ma-k p{font-size:15.5px}
.ma-src{margin-top:30px;font-size:13px;color:var(--grey)}.ma-src a{color:var(--gold)}.ma-src li{margin:3px 0 0 18px}
.ma-nt{margin-top:14px;font-size:12.5px;color:var(--grey)}
.ma-cta{margin-top:30px;display:flex;gap:10px;flex-wrap:wrap}.ma-cta a{flex:1 1 240px;text-align:center;padding:14px;border-radius:14px;font-weight:700;text-decoration:none}
.ma-cta .w{background:#25D366;color:#fff}.ma-cta .f{border:1.5px solid #d9d6ea;background:#fff}
.ma-rel{margin-top:40px}.ma-rel h3{font:700 20px 'Playfair Display',Georgia,serif;margin-bottom:10px}.ma-rel a{display:block;padding:12px 16px;background:#fff;border:1px solid var(--line);border-radius:12px;margin-bottom:8px;text-decoration:none;font-weight:600}
.ma-rel a:hover{border-color:var(--gold);color:var(--gold)}
footer{border-top:1px solid var(--line);padding:26px 5vw;font-size:13px;color:var(--grey);text-align:center}
@media(max-width:700px){.ma-f{grid-template-columns:1fr 1fr}.ma-f div:nth-child(2){border-right:0}.ma-f div:nth-child(-n+2){border-bottom:1px solid var(--line)}.ma-s{grid-template-columns:34px 1fr}.ma-s i{font-size:22px}}
'''


def article_page(a):
    grp = dict((g, t) for g, t, _ in GROUPS)[a['group']]
    facts = ''.join('<div><small>%s</small><b>%s</b></div>' % (E(k), E(v)) for k, v in a['facts'])
    secs = ''.join('<section class="ma-s"><i>%02d</i><div><h2>%s</h2><p>%s</p></div></section>' % (k + 1, E(h), E(p)) for k, (h, p) in enumerate(a['sections']))
    src = ''.join('<li><a href="%s" target="_blank" rel="noopener nofollow">%s</a></li>' % (E(u), E(n)) for n, u in a['sources'])
    rel = ''.join('<a href="%s.html">%s →</a>' % (x['slug'], E(x['title'])) for x in A if x['slug'] != a['slug'])
    wa = WA + 'Hi+Keith%2C+I+read+your+MM2H+article+and+have+a+question.'
    ld = json.dumps({'@context': 'https://schema.org', '@type': 'Article', 'headline': a['title'], 'description': a['desc'],
                     'author': {'@type': 'Person', 'name': 'Keith Nah'}, 'publisher': {'@type': 'Organization', 'name': 'Keith Nah Real Estate'},
                     'mainEntityOfPage': 'https://keithnah.com/mm2h/%s.html' % a['slug']}, ensure_ascii=False)
    page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Keith Nah</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://keithnah.com/mm2h/{slug}.html">
<meta property="og:type" content="article"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<link rel="icon" type="image/png" href="../images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{ld}</script>
<style>{css}</style>
</head>
<body>
<header>
  <a class="logo" href="../"><img src="../images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Keith Nah Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="{wa}" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
<div class="ma-top"><div class="in"><div class="ma-cr"><a href="../">Home</a> › <a href="../mm2h.html">MM2H</a> › {grp}</div>
<span class="ma-tag">{grp}</span><h1>{title}</h1><p>{desc}</p><small>By Keith Nah · {read} min read</small></div></div>
<main class="ma"><div class="ma-f">{facts}</div>{secs}
<div class="ma-k"><img src="../images/f304c8479b1fe873.png" alt=""><div><b>Keith's take</b><p>{take}</p></div></div>
<div class="ma-src"><b>Sources</b><ul>{src}</ul></div>
<p class="ma-nt">MM2H terms are set by the Malaysian government and change from time to time. This article is a guide, not immigration or tax advice; confirm the current rules with a licensed MM2H agent.</p>
<div class="ma-cta"><a class="w" href="{wa}" target="_blank" rel="noopener">Ask Keith on WhatsApp</a><a class="f" href="../mm2h.html#enquire">Fill in the MM2H enquiry form</a></div>
<div class="ma-rel"><h3>More from the MM2H library</h3>{rel}<a href="../mm2h.html#library">All MM2H articles →</a></div>
</main>
<footer></footer>
<script src="../lead-tracker.js"></script>
</body>
</html>
'''.format(title=E(a['title']), desc=E(a['desc']), slug=a['slug'], css=ART_CSS, ld=ld, wa=E(wa), grp=E(grp), read=a['read'],
           facts=facts, secs=secs, take=E(a['take']), src=src, rel=rel)
    return SH.apply(page, '../', 'mm2h.html')


LIB_CSS = '''<style>
.ml{max-width:1180px;margin:0 auto;padding:80px 5vw 20px}.ml .eb,.me .eb{display:block;font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:#5E60CE;font-weight:800}
.ml h2{font-family:'Playfair Display',Georgia,serif;font-size:clamp(28px,3.6vw,40px);line-height:1.2;margin:6px 0 8px}.ml .ld{color:#5f5e74;max-width:680px}
.ml-tabs{display:flex;gap:8px;margin:24px 0 18px;flex-wrap:wrap}.ml-tabs button{border:1.5px solid #dcd9ee;background:#fff;border-radius:999px;padding:10px 18px;font:700 14px Inter,sans-serif;color:#15142b;cursor:pointer}
.ml-tabs button.on{background:#15142b;border-color:#15142b;color:#fff}.ml-tabs button i{font-style:normal;opacity:.6;margin-left:6px}
.ml-g p.gd{color:#5f5e74;font-size:14px;margin-bottom:14px}
.ml-l{display:grid;grid-template-columns:1fr 1fr;gap:0 34px;border-top:1px solid rgba(21,20,43,.09)}
.ml-a{display:grid;grid-template-columns:46px 1fr 26px;gap:14px;align-items:center;padding:18px 4px;border-bottom:1px solid rgba(21,20,43,.09);text-decoration:none;color:#15142b;transition:background .2s}
.ml-a:hover{background:#f3f1ff}.ml-a i{font-style:normal;font:700 22px 'Playfair Display',Georgia,serif;color:#5E60CE}
.ml-a b{display:block;font-size:16px;line-height:1.35}.ml-a small{display:block;color:#5f5e74;font-size:13px;margin-top:3px}.ml-a span{color:#5E60CE;font-size:20px;transition:transform .2s}.ml-a:hover span{transform:translateX(4px)}
.me{max-width:1180px;margin:0 auto;padding:70px 5vw 90px}.me-in{display:grid;grid-template-columns:.9fr 1.1fr;gap:36px;background:#15142b;color:#fff;border-radius:28px;padding:40px;overflow:hidden}
.me-in h2{font-family:'Playfair Display',Georgia,serif;font-size:clamp(28px,3.4vw,38px);line-height:1.2;margin:6px 0 12px}.me-in .eb{color:#a9a7ff}.me-in>div:first-child p{color:rgba(255,255,255,.7);font-size:15px}
.me-in ul{margin:18px 0 0;padding:0;list-style:none}.me-in li{padding:8px 0 8px 28px;position:relative;color:rgba(255,255,255,.85);font-size:14.5px}.me-in li:before{content:"✓";position:absolute;left:0;color:#25D366;font-weight:800}
.me-f{background:#fff;color:#15142b;border-radius:20px;padding:24px;display:grid;grid-template-columns:1fr 1fr;gap:12px}
.me-f label{display:block;font-size:11.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#5f5e74;margin-bottom:5px}
.me-f input,.me-f select,.me-f textarea{width:100%;border:1.5px solid #dcd9ee;border-radius:12px;padding:11px 12px;font:500 14.5px Inter,sans-serif;color:#15142b;background:#fff}
.me-f input:focus,.me-f select:focus,.me-f textarea:focus{outline:0;border-color:#5E60CE}.me-f .full{grid-column:1/-1}.me-f .ph{display:grid;grid-template-columns:96px 1fr;gap:8px}
.me-f textarea{min-height:84px;resize:vertical}.me-f button{grid-column:1/-1;border:0;border-radius:14px;padding:15px;background:#5E60CE;color:#fff;font:700 15.5px Inter,sans-serif;cursor:pointer}
.me-f button:hover{background:#4a4cc0}.me-f .er{grid-column:1/-1;color:#c0392b;font-size:13px}.me-f .nt{grid-column:1/-1;font-size:12px;color:#5f5e74}
.me-ok{grid-column:1/-1;text-align:center;padding:20px 6px}.me-ok b{display:block;font:700 24px 'Playfair Display',Georgia,serif;margin-bottom:6px}.me-ok p{color:#5f5e74;font-size:14.5px}
.me-ok a{display:inline-block;margin-top:14px;background:#25D366;color:#fff;font-weight:700;padding:13px 22px;border-radius:14px;text-decoration:none}
@media(max-width:900px){.ml-l{grid-template-columns:1fr}.me-in{grid-template-columns:1fr;padding:26px}}
@media(max-width:520px){.me-f{grid-template-columns:1fr;padding:18px}.me{padding:50px 16px 70px}}
</style>'''


def library():
    tabs, panes = '', ''
    for k, (g, name, d) in enumerate(GROUPS):
        items = [a for a in A if a['group'] == g]
        tabs += '<button type="button" data-g="%s"%s>%s<i>%d</i></button>' % (g, ' class="on"' if k == 0 else '', E(name), len(items))
        lst = ''.join('<a class="ml-a" href="mm2h/%s.html"><i>%02d</i><div><b>%s</b><small>%s · %d min read</small></div><span>→</span></a>'
                      % (a['slug'], n + 1, E(a['title']), E((a['desc'][:120].rsplit(' ', 1)[0] + '…') if len(a['desc']) > 120 else a['desc']), a['read'])
                      for n, a in enumerate(items))
        panes += '<div class="ml-g" data-g="%s"%s><p class="gd">%s</p><div class="ml-l">%s</div></div>' % (g, '' if k == 0 else ' hidden', E(d), lst)
    return ('<section class="ml" id="library"><span class="eb">MM2H Library</span><h2>Read before you apply</h2>'
            '<p class="ld">Short, plain-English articles on how MM2H works, what it costs and how it compares with other countries. Written by Keith from what his clients ask.</p>'
            '<div class="ml-tabs">%s</div>%s</section>') % (tabs, panes)


def sel(name, label, opts):
    return '<div><label for="me_%s">%s</label><select id="me_%s" name="%s"><option value="">Choose</option>%s</select></div>' % (
        name, E(label), name, name, ''.join('<option>%s</option>' % E(o) for o in opts))


FORM = ('<section class="me" id="enquire"><div class="me-in"><div><span class="eb">MM2H enquiry</span><h2>Tell Keith about your MM2H plan</h2>'
        '<p>Share a few details and Keith will reply within a day with homes that meet your tier, the area that suits your family, and the next steps.</p>'
        '<ul><li>Homes that meet both the MM2H and the foreign buyer minimum</li><li>Introduction to a licensed MM2H agent for the application</li><li>Help with the purchase, from booking to keys</li></ul></div>'
        '<form class="me-f" id="meForm" novalidate>'
        '<div class="full"><label for="me_name">Full name *</label><input id="me_name" name="name" autocomplete="name" required></div>'
        '<div class="full"><label for="me_phone">WhatsApp number *</label><div class="ph"><input name="code" value="+60" aria-label="Country code" autocomplete="tel-country-code"><input id="me_phone" name="phone" type="tel" autocomplete="tel-national" required></div></div>'
        '<div class="full"><label for="me_email">Email</label><input id="me_email" name="email" type="email" autocomplete="email"></div>'
        '<div><label for="me_nat">Nationality</label><input id="me_nat" name="nat" autocomplete="country-name"></div>'
        + sel('age', 'Age of main applicant', ['21 to 24', '25 to 34', '35 to 49', '50 to 59', '60 or above'])
        + sel('who', 'Who is moving', ['Just me', 'Me and my partner', 'Family with children', 'Family with parents'])
        + sel('tier', 'Programme of interest', ['Not sure yet', 'Silver', 'Gold', 'Platinum', 'Johor Forest City SFZ', 'Sarawak S-MM2H', 'Sabah MM2H'])
        + sel('area', 'Preferred area', ['Not sure yet', 'Kuala Lumpur', 'Selangor', 'Penang', 'Johor Bahru', 'Sabah', 'Sarawak'])
        + sel('budget', 'Property budget', ['RM500,000 to RM600,000', 'RM600,000 to RM1 million', 'RM1 million to RM2 million', 'Above RM2 million'])
        + sel('when', 'When would you like to move', ['Within 6 months', '6 to 12 months', '1 to 2 years', 'Just exploring'])
        + '<div class="full"><label for="me_msg">Anything else Keith should know</label><textarea id="me_msg" name="msg"></textarea></div>'
        '<p class="er" role="alert"></p><button type="submit">Send my MM2H enquiry</button>'
        '<p class="nt">By sending, you agree to our <a href="privacy-policy.html">Privacy Policy</a>. Keith only uses your details to reply to this enquiry.</p></form></div></section>')

JS = r'''<script>(function(){
document.querySelectorAll(".ml-tabs button").forEach(function(b){b.addEventListener("click",function(){var g=b.getAttribute("data-g");
document.querySelectorAll(".ml-tabs button").forEach(function(x){x.classList.toggle("on",x===b);});document.querySelectorAll(".ml-g").forEach(function(p){p.hidden=p.getAttribute("data-g")!==g;});});});
var f=document.getElementById("meForm");if(!f)return;var L={nat:"Nationality",age:"Age",who:"Who is moving",tier:"Programme",area:"Preferred area",budget:"Property budget",when:"Timing",msg:"Notes"};
f.addEventListener("submit",function(ev){ev.preventDefault();var v=function(n){return (f.elements[n].value||"").trim();},er=f.querySelector(".er"),d=v("phone").replace(/[^0-9]/g,"");
if(!v("name")||d.length<6){er.textContent="Please add your name and WhatsApp number.";return;}er.textContent="";
var lines=["(KNRE) Hi Keith, I filled in the MM2H enquiry form on your website.","Name: "+v("name"),"WhatsApp: "+v("code")+" "+v("phone")];if(v("email"))lines.push("Email: "+v("email"));
["nat","age","who","tier","area","budget","when","msg"].forEach(function(n){if(v(n))lines.push(L[n]+": "+v(n));});var msg=lines.join("\n"),nm=v("name").replace(/[<>&"]/g,"");
if(typeof window.knLead==="function")window.knLead({type:"Quick Enquiry",button:"MM2H enquiry form",name:v("name"),code:v("code"),phone:v("phone"),email:v("email"),area:v("area"),look:"MM2H"+(v("tier")?": "+v("tier"):""),message:msg});
f.innerHTML='<div class="me-ok"><b>Thank you, '+nm+'</b><p>Keith has your MM2H enquiry and will reply on WhatsApp within a day. Want to start the chat now?</p><a target="_blank" rel="noopener" href="https://api.whatsapp.com/send/?phone=60102821568&type=phone_number&app_absent=0&text='+encodeURIComponent(msg)+'">Message Keith on WhatsApp</a></div>';});})();</script>'''

os.makedirs('mm2h', exist_ok=True)
keep = set()
for a in A:
    open('mm2h/%s.html' % a['slug'], 'w', encoding='utf-8').write(article_page(a))
    keep.add(a['slug'] + '.html')
for f in os.listdir('mm2h'):
    if f.endswith('.html') and f not in keep:
        os.remove(os.path.join('mm2h', f))

out = sys.argv[1] if len(sys.argv) > 1 else 'mm2h.html'
t = open('mm2h.html', encoding='utf-8').read()
t = re.sub(r'<!-- KN-MM2H:START -->.*?<!-- KN-MM2H:END -->\n?', '', t, flags=re.S)
i = t.index('<section class="mm2h-tiers">')
j = t.index('</section>', i) + len('</section>')
t = t[:j] + '\n<!-- KN-MM2H:START -->' + LIB_CSS + library() + FORM + JS + '<!-- KN-MM2H:END -->' + t[j:]
# the old intro said MM2H does not need a property purchase; since 2024 every federal tier does
t = t.replace("MM2H is separate from property ownership itself — it doesn't require buying real estate to qualify on its own, but combining the two is common among Keith's clients who want both a home and a long-stay pass in Kuala Lumpur.",
              "Since 2024 every federal tier also needs a residential property purchase above a minimum price, so choosing the tier and choosing the home go together. Keith helps clients match the two.")
open(out, 'w', encoding='utf-8').write(t)
print('mm2h: %d article page(s), library and enquiry form on %s' % (len(A), out))
