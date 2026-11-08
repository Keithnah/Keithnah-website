"""The main site header (menu, language and currency switchers) for generated pages.

Used by tools/build_area_pages.py and tools/build_list_pages.py so the area
guides and best-of lists look and behave like the main pages: same fonts,
the language choice (saved as kn_lang, shared with the rest of the site) and
the currency choice (kn_currency; prices marked data-price-myr are converted).
"""
import html
import re

E = lambda s: html.escape(s, quote=True)
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,700'
         '&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">')
NAV = [('', 'Home'), ('projects.html', 'View Projects'), ('compare.html', 'Compare Projects'), ('blog.html', 'News'),
       ('calculator.html', 'Calculator'), ('resources.html', 'Free Resources'), ('about-keith.html', 'About Keith')]
LANGS = [('en', 'gb', 'English'), ('zh-CN', 'cn', '简体中文'), ('zh-TW', 'tw', '繁體中文'), ('ms', 'my', 'Bahasa Malaysia'),
         ('ja', 'jp', '日本語'), ('ko', 'kr', '한국어')]
CURS = [('MYR', 'my', 'Malaysian Ringgit'), ('USD', 'us', 'US Dollar'), ('SGD', 'sg', 'Singapore Dollar'),
        ('CNY', 'cn', 'Chinese Yuan'), ('JPY', 'jp', 'Japanese Yen'), ('KRW', 'kr', 'Korean Won')]
NAV_TR = {
 "Home": {
  "zh-CN": "首页",
  "zh-TW": "首頁",
  "ms": "Utama",
  "ta": "முகப்பு",
  "ja": "ホーム",
  "ko": "홈",
  "ar": "الرئيسية"
 },
 "News": {
  "zh-CN": "新闻",
  "zh-TW": "新聞",
  "ms": "Berita",
  "ta": "செய்திகள்",
  "ja": "ニュース",
  "ko": "뉴스",
  "ar": "الأخبار"
 },
 "View Projects": {
  "zh-CN": "查看项目",
  "zh-TW": "查看項目",
  "ms": "Lihat Projek",
  "ta": "திட்டங்களைப் பார்க்க",
  "ja": "物件を見る",
  "ko": "프로젝트 보기",
  "ar": "عرض المشاريع"
 },
 "Compare Projects": {
  "zh-CN": "项目比较",
  "zh-TW": "項目比較",
  "ms": "Banding Projek",
  "ta": "திட்டங்களை ஒப்பிடுக",
  "ja": "物件を比較",
  "ko": "프로젝트 비교",
  "ar": "مقارنة المشاريع"
 },
 "Calculator": {
  "zh-CN": "计算器",
  "zh-TW": "計算機",
  "ms": "Kalkulator",
  "ta": "கணிப்பான்",
  "ja": "計算ツール",
  "ko": "계산기",
  "ar": "الحاسبة"
 },
 "Free Resources": {
  "zh-CN": "免费资源",
  "zh-TW": "免費資源",
  "ms": "Sumber Percuma",
  "ja": "無料リソース",
  "ko": "무료 자료"
 },
 "About Keith": {
  "zh-CN": "关于 KEITH",
  "zh-TW": "關於 KEITH",
  "ms": "Tentang Keith",
  "ta": "Keith பற்றி",
  "ja": "Keithについて",
  "ko": "Keith 소개",
  "ar": "عن كيث"
 }
}

CSS = """
header{position:sticky;top:0;z-index:50;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:16px 3vw;background:#5E60CE;color:#fff;border-bottom:1px solid rgba(0,0,0,.12);box-shadow:0 2px 18px rgba(17,17,17,.08);font-family:'Inter',sans-serif;font-weight:600;-webkit-font-smoothing:antialiased;}
header .logo{font-family:'Playfair Display',serif;display:flex;align-items:center;gap:11px;color:#fff;flex-shrink:0;}
header .logo img{width:42px;height:42px;border-radius:50%;object-fit:contain;}
header .logo span{display:flex;flex-direction:column;line-height:1.15;}
header .logo b{font-family:'Playfair Display',serif;font-weight:800;font-size:21px;color:#fff;white-space:nowrap;}
header .logo small{font-family:'Playfair Display',serif;font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:rgba(255,255,255,.8);font-weight:500;white-space:nowrap;}
header nav{display:flex;gap:clamp(20px,2.3vw,32px);margin:0;flex-wrap:nowrap;}
header nav a{font-size:15px;font-weight:500;position:relative;padding-bottom:4px;white-space:nowrap;color:#fff;text-decoration:none!important;}
header nav a.active{font-weight:700;}
header nav a::after{content:'';position:absolute;left:0;bottom:0;width:0;height:1.5px;background:#fff;transition:width .3s;}
header nav a:hover::after,header nav a.active::after{width:100%;}
.nav-right{display:flex;align-items:center;gap:8px;flex-shrink:0;}
.kn-sw{position:relative;}
.kn-sel{display:flex;align-items:center;gap:6px;font:600 12px 'Inter',sans-serif;letter-spacing:.02em;cursor:pointer;background:rgba(255,255,255,.35);border:1px solid rgba(17,17,17,.15);color:#111;padding:8px 11px;border-radius:100px;white-space:nowrap;}
.kn-sel svg{width:13px;height:13px;stroke:#111;fill:none;stroke-width:1.6;}
.kn-menu{display:none;position:absolute;top:calc(100% + 8px);right:0;background:#fff;border:1px solid rgba(17,17,17,.08);border-radius:12px;box-shadow:0 16px 40px rgba(17,17,17,.14);padding:8px;z-index:80;min-width:210px;}
.kn-menu.cur{min-width:275px;}
.kn-menu.open{display:block;}
.kn-menu a{display:flex;align-items:center;gap:10px;white-space:nowrap;padding:9px 14px;font:500 13px 'Inter',sans-serif;color:#111;border-radius:8px;cursor:pointer;}
.kn-menu a:hover{background:#F9F8F6;} .kn-menu a.active{color:#5E60CE;font-weight:700;}
.kn-flag{width:20px;height:15px;flex:0 0 20px;border-radius:2px;object-fit:cover;box-shadow:0 0 0 1px rgba(0,0,0,.08);}
header .wa-btn{display:flex;align-items:center;gap:8px;background:#25D366;color:#fff!important;padding:11px 16px;border-radius:100px;font:600 12px 'Inter',sans-serif;white-space:nowrap;margin:0;}
header .wa-btn:hover{box-shadow:0 8px 20px rgba(37,211,102,.4);}
header .kn-burger{margin-left:0;}
@media(max-width:1349px){header nav,.nav-right .kn-sw{display:none;} header .kn-burger{display:block;}}
@media(max-width:560px){header .wa-btn{display:none!important;}}
main .wa-btn{white-space:normal;max-width:100%;text-align:center;justify-content:center;}
#knMnav .kn-msub{margin:22px 0 8px;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:#a9a6d6;}
#knMnav .kn-mchips{display:flex;flex-wrap:wrap;gap:8px;}
#knMnav .kn-mchips button{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.2);color:#fff;border-radius:999px;padding:8px 14px;font-size:13px;cursor:pointer;}
#knMnav .kn-mchips button.on{background:#fff;color:#1d1b4f;}
"""

JS = """<script>
(function(){
var NT=%s, LN=%s, CN=%s;
var RATE={MYR:1,USD:0.21,SGD:0.285,CNY:1.52,JPY:31.5,KRW:290}, SYM={MYR:'RM',USD:'US$',SGD:'S$',CNY:'CN\\u00a5',JPY:'JP\\u00a5',KRW:'\\u20a9'};window.KN_RATE=RATE;window.KN_SYM=SYM;
function get(k,d){try{return localStorage.getItem(k)||d}catch(e){return d}}
function put(k,v){try{localStorage.setItem(k,v)}catch(e){}}
function navText(lang){document.querySelectorAll('[data-nav]').forEach(function(el){var k=el.getAttribute('data-nav');el.textContent=(lang!=='en'&&NT[k]&&NT[k][lang])||k;});}
var FROM={'en':'From ','zh-CN':'\u8d77\u4ef7 ','zh-TW':'\u8d77\u50f9 ','ms':'Dari ','ta':'\u0ba4\u0bca\u0b9f\u0b95\u0bcd\u0b95\u0bae\u0bcd ','ja':'','ko':'','ar':'\u0645\u0646 '};
function pt(lang){var T=window.KN_PT||[];document.querySelectorAll('[data-pt]').forEach(function(el){if(!el.hasAttribute('data-en'))el.setAttribute('data-en',el.textContent);
 var r=T[+el.getAttribute('data-pt')]||{};el.textContent=(lang!=='en'&&r[lang])||el.getAttribute('data-en');});}
window.knSetLang=function(l){if(!LN[l])l='en';put('kn_lang',l);document.documentElement.setAttribute('lang',l);pt(l);var lab=document.getElementById('knLangLab');if(lab)lab.textContent=LN[l]||'English';
 document.querySelectorAll('#knLangMenu a').forEach(function(a){a.classList.toggle('active',a.getAttribute('data-v')===l)});
 document.documentElement.setAttribute('dir',l==='ar'?'rtl':'ltr');navText(l);if(window.knSetCur)knSetCur(get('kn_currency','MYR'));mark();close();};
function fmt(v,c){var x=v*(RATE[c]||1),s=SYM[c]||c;return '~'+s+' '+(x>=1e6?(x/1e6).toFixed(2)+'M':Math.round(x/1e3)+'K');}
window.knSetCur=function(c){put('kn_currency',c);var lab=document.getElementById('knCurLab');if(lab)lab.textContent=c;
 document.querySelectorAll('#knCurMenu a').forEach(function(a){a.classList.toggle('active',a.getAttribute('data-v')===c)});
 document.querySelectorAll('[data-price-myr]').forEach(function(el){if(!el.hasAttribute('data-orig'))el.setAttribute('data-orig',el.innerHTML);
  el.innerHTML=c==='MYR'?el.getAttribute('data-orig'):((get('kn_lang','en') in FROM)?FROM[get('kn_lang','en')]:'From ')+fmt(parseFloat(el.getAttribute('data-price-myr')),c)+({'ja':' から','ko':'부터'}[get('kn_lang','en')]||'');});if(c==='MYR')pt(get('kn_lang','en'));mark();close();try{document.dispatchEvent(new CustomEvent('kncur',{detail:c}))}catch(e){}};
window.knTog=function(id,e){e.stopPropagation();var m=document.getElementById(id),o=!m.classList.contains('open');close();m.classList.toggle('open',o);};
function close(){document.querySelectorAll('.kn-menu.open').forEach(function(m){m.classList.remove('open')});}
document.addEventListener('click',close);
function mark(){var l=get('kn_lang','en'),c=get('kn_currency','MYR');document.querySelectorAll('#knMnav .kn-mchips button').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-v')===l||b.getAttribute('data-v')===c)});}
function drawer(){var p=document.querySelector('#knMnav .kn-mlinks');if(!p||document.querySelector('#knMnav .kn-msub'))return;
 var h='<div class="kn-msub">Language</div><div class="kn-mchips">';for(var k in LN)h+='<button type="button" data-v="'+k+'" onclick="knSetLang(this.getAttribute(\\'data-v\\'))">'+LN[k]+'</button>';
 h+='</div><div class="kn-msub">Currency</div><div class="kn-mchips">';for(var c in CN)h+='<button type="button" data-v="'+c+'" onclick="knSetCur(this.getAttribute(\\'data-v\\'))">'+c+'</button>';
 p.insertAdjacentHTML('afterend',h+'</div>');}
document.addEventListener('DOMContentLoaded',function(){drawer();knSetLang(get('kn_lang','en'));});
})();
</script>"""


def js():
    import json
    return JS % (json.dumps(NAV_TR, ensure_ascii=False), json.dumps({k: n for k, f, n in LANGS}, ensure_ascii=False),
                 json.dumps({c: n for c, f, n in CURS}))


def header(root, active, wa):
    nav = ''.join('<a href="%s%s"%s>%s</a>' % (root, h, ' class="active"' if h == active else '',
                                               ('<span data-nav="%s">%s</span>' % (E(t), E(t))) if t in NAV_TR else E(t)) for h, t in NAV)
    langs = ''.join('<a data-v="%s" onclick="knSetLang(\'%s\')"><img class="kn-flag" src="%simages/flags/%s.svg" alt="" width="20" height="15">%s</a>' % (c, c, root, f, n) for c, f, n in LANGS)
    curs = ''.join('<a data-v="%s" onclick="knSetCur(\'%s\')"><img class="kn-flag" src="%simages/flags/%s.svg" alt="" width="20" height="15">%s — %s</a>' % (c, c, root, f, c, n) for c, f, n in CURS)
    return ('<header>\n  <a class="logo" href="%s"><img src="%simages/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Keith Nah Real Estate</small></span></a>\n'
            '  <nav>%s</nav>\n  <div class="nav-right">\n'
            '    <div class="kn-sw"><span class="kn-sel" onclick="knTog(\'knLangMenu\',event)"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.5 4 5.7 4 9s-1.5 6.5-4 9c-2.5-2.5-4-5.7-4-9s1.5-6.5 4-9z"/></svg><span id="knLangLab">English</span></span><div class="kn-menu" id="knLangMenu">%s</div></div>\n'
            '    <div class="kn-sw"><span class="kn-sel" onclick="knTog(\'knCurMenu\',event)"><svg viewBox="0 0 24 24"><circle cx="8" cy="8" r="5"/><circle cx="16" cy="16" r="5"/></svg><span id="knCurLab">MYR</span></span><div class="kn-menu cur" id="knCurMenu">%s</div></div>\n'
            '    <a class="wa-btn" href="%s" target="_blank" rel="noopener">WhatsApp Keith</a>\n  <!--kn-burger-->\n  </div>\n</header>') % (root, root, nav, langs, curs, wa)


def price_tag(text, myr):
    """A starting price that the currency switcher can convert."""
    return ('<span data-price-myr="%d">%s</span>' % (myr, text)) if myr else text


def apply(page, root, active, wa=None):
    import i18n_pages
    page = i18n_pages.translate(page)
    """Swap a generated page's simple header for the main one and add its CSS and script."""
    if wa is None:
        wa = re.search(r'<header>.*?<a class="wa-btn" href="([^"]+)"', page, re.S).group(1)
    page = re.sub(r'<header>.*?</header>', lambda _: header(root, active, wa), page, count=1, flags=re.S)
    page = re.sub(r'<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2[^"]*" rel="stylesheet">', lambda _: FONTS, page, count=1)
    page = page.replace('</style>\n</head>', CSS + '</style>\n</head>', 1)
    return page.replace('</body>', js() + '\n</body>', 1)
