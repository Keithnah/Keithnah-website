"""Keith's numbers and client countries on the home page (About section) and on about-keith.html.

- Home #about: 5 years of experience, RM100M+ personal sales, YouTube followers, and a slowly sliding
  row of the countries Keith's clients come from (flag + name), like the Free Toolkit row.
- about-keith.html: the stats band on a light background (5 tiles) with the same sliding country row.
Texts in six languages, swapped in the browser (kn_lang) like the other generated blocks.
Safe to run again (blocks between KN-ABS markers are replaced).
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)

LG = ['en', 'zh-CN', 'zh-TW', 'ms', 'ja', 'ko']
T = {
    'years': ['Years of experience', '年经验', '年經驗', 'Tahun pengalaman', '年の経験', '년 경력'],
    'sales': ['Personal sales achieved', '个人销售额', '個人銷售額', 'Jualan peribadi dicapai', '個人販売実績', '개인 판매 실적'],
    'clients': ['Clients from 9 countries', '客户来自 9 个国家', '客戶來自 9 個國家', 'Pelanggan dari 9 negara', '9か国のお客様', '9개국 고객'],
    'my': ['Malaysia', '马来西亚', '馬來西亞', 'Malaysia', 'マレーシア', '말레이시아'],
    'sg': ['Singapore', '新加坡', '新加坡', 'Singapura', 'シンガポール', '싱가포르'],
    'cn': ['China', '中国', '中國', 'China', '中国', '중국'],
    'tw': ['Taiwan', '台湾', '台灣', 'Taiwan', '台湾', '대만'],
    'hk': ['Hong Kong', '香港', '香港', 'Hong Kong', '香港', '홍콩'],
    'bn': ['Brunei', '文莱', '汶萊', 'Brunei', 'ブルネイ', '브루나이'],
    'us': ['United States', '美国', '美國', 'Amerika Syarikat', 'アメリカ', '미국'],
    'gb': ['United Kingdom', '英国', '英國', 'United Kingdom', 'イギリス', '영국'],
    'ae': ['Dubai', '迪拜', '杜拜', 'Dubai', 'ドバイ', '두바이'],
}
COUNTRIES = ['my', 'sg', 'cn', 'tw', 'hk', 'bn', 'us', 'gb', 'ae']   # flag files in images/flags/ (ae = UAE flag for Dubai)
JS = ('<script>(function(){var T=%s,LG=%s;function f(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}var i=Math.max(0,LG.indexOf(l));'
      'document.querySelectorAll("[data-kab]").forEach(function(el){var v=T[el.getAttribute("data-kab")];if(v)el.textContent=v[i];});}f();'
      'document.addEventListener("DOMContentLoaded",function(){["knSetLang","setLanguage"].forEach(function(n){var s=window[n];if(typeof s==="function")window[n]=function(){var r=s.apply(this,arguments);f();return r;};});f();});})();</script>'
      ) % (json.dumps(T, ensure_ascii=False), json.dumps(LG))


def marquee(cls):
    chips = ''.join('<span class="kab-c"><img src="images/flags/%s.svg" alt="" width="24" height="18"><span data-kab="%s">%s</span></span>' % (c, c, T[c][0]) for c in COUNTRIES)
    return ('<div class="kab-m %s"><span class="kab-l" data-kab="clients">%s</span><div class="kab-v"><div class="kab-r">%s%s</div></div></div>' % (
        cls, T['clients'][0], chips, chips.replace('<span class="kab-c">', '<span class="kab-c" aria-hidden="true">')))


MQ_CSS = ('.kab-m{display:flex;flex-direction:column;gap:10px;min-width:0}.kab-l{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:#6b6a85;font-weight:700}'
          '.kab-v{overflow:hidden;-webkit-mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent);mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent)}'
          '.kab-r{display:flex;gap:10px;width:max-content;animation:kabSlide 40s linear infinite}.kab-v:hover .kab-r{animation-play-state:paused}@keyframes kabSlide{to{transform:translateX(calc(-50% - 5px))}}'
          '.kab-c{display:inline-flex;align-items:center;gap:8px;background:#fff;border:1px solid #DEDCF7;color:#15142b;font-size:13px;font-weight:600;padding:6px 14px 6px 8px;border-radius:99px;white-space:nowrap}'
          '.kab-c img{border-radius:3px;box-shadow:0 0 0 1px rgba(0,0,0,.08)}@media(prefers-reduced-motion:reduce){.kab-r{animation:none}.kab-v{overflow-x:auto}}')


def put(t, start, end, block):
    t = re.sub(re.escape(start) + r'.*?' + re.escape(end), '', t, flags=re.S)
    return t


# ---------- home page ----------
ix = open('index.html', encoding='utf-8').read()
ix = re.sub(r'<!-- KN-ABS:START -->.*?<!-- KN-ABS:END -->', '', ix, flags=re.S)
ix = re.sub(r'<style id="kab-css">.*?</style>', '', ix, flags=re.S)
ix = re.sub(r'<script id="kab-js">.*?</script>', '', ix, flags=re.S)
m = re.search(r'<div class="ab-stats">(?:(?!</div></div>).)*?<div class="ab-stat"><b>1000\+</b><span data-i18n="stat_label">[^<]*</span></div></div>', ix, re.S)
yt = '<div class="ab-stat"><b>1000+</b><span data-i18n="stat_label">YouTube Followers</span></div>'
home = ('<!-- KN-ABS:START --><div class="ab-stats"><div class="ab-stat"><b>5</b><span data-kab="years">%s</span></div><div class="ab-stat"><b>RM100M+</b><span data-kab="sales">%s</span></div>%s</div>%s<!-- KN-ABS:END -->'
        % (T['years'][0], T['sales'][0], yt, marquee('kab-home')))
if m:
    ix = ix[:m.start()] + home + ix[m.end():]
else:   # already rebuilt once: put the block back where the stats were
    ix = ix.replace('<p data-i18n="about_p">', '<p data-i18n="about_p">', 1)
    i = ix.index('</p>', ix.index('data-i18n="about_p"')) + 4
    ix = ix[:i] + home + ix[i:]
ix = ix.replace('</head>', '<style id="kab-css">%s#about .ab-stats{display:grid!important;grid-template-columns:repeat(3,auto);justify-content:start;gap:12px}'
                '#about .ab-stat{display:flex;flex-direction:column;padding:14px 18px!important}#about .ab-stat b{margin:0!important;font-size:26px!important}'
                '#about .kab-home{margin:4px 0 18px;max-width:640px}@media(max-width:900px){#about .ab-stats{justify-content:center}#about .kab-home{margin:4px auto 18px;align-items:center}}</style>\n</head>' % MQ_CSS, 1)
ix = ix.replace('</body>', JS.replace('<script>', '<script id="kab-js">', 1) + '\n</body>', 1)
open('index.html', 'w', encoding='utf-8').write(ix)

# ---------- about-keith.html ----------
ak = open('about-keith.html', encoding='utf-8').read()
ak = re.sub(r'<style id="kab-css">.*?</style>', '', ak, flags=re.S)
ak = re.sub(r'<script id="kab-js">.*?</script>', '', ak, flags=re.S)
tiles = ('<div class="stats-inner kab-5"><div class="stat-tile"><h3>5</h3><span data-kab="years">%s</span></div><div class="stat-tile"><h3>RM100M+</h3><span data-kab="sales">%s</span></div>'
         '<div class="stat-tile"><h3>100+</h3><span>Projects Across Malaysia</span></div><div class="stat-tile"><h3>0%%</h3><span>Agent Fee To Buyers</span></div>'
         '<div class="stat-tile"><h3>1000+</h3><span>YouTube Followers</span></div></div>%s') % (T['years'][0], T['sales'][0], marquee('kab-about'))
ak = re.sub(r'<section class="keith-stats"[^>]*>.*?</section>', lambda _: '<section class="keith-stats kab-light" style="padding:0;">\n  <!-- KN-ABS:START -->%s<!-- KN-ABS:END -->\n</section>' % tiles, ak, count=1, flags=re.S)
ak = ak.replace('</head>', '<style id="kab-css">%s.keith-stats.kab-light{background:linear-gradient(160deg,#F7F6FF 0%%,#ECEBFB 100%%)!important;border-top:1px solid #DEDCF7;border-bottom:1px solid #DEDCF7}'
                '.kab-light .stats-inner.kab-5{grid-template-columns:repeat(5,1fr)!important}.kab-light .stat-tile{border-color:#DEDCF7!important}'
                '.kab-light .stat-tile h3{color:#5E60CE!important}.kab-light .stat-tile span{color:#5f5e74!important}'
                '.kab-about{align-items:center;padding:22px 5vw 30px;border-top:1px solid #DEDCF7}.kab-about .kab-v{max-width:1180px;width:100%%}'
                '@media(max-width:900px){.kab-light .stats-inner.kab-5{grid-template-columns:repeat(2,1fr)!important}.kab-light .stats-inner.kab-5 .stat-tile:last-child{grid-column:1/-1}}</style>\n</head>' % MQ_CSS, 1)
ak = ak.replace('</body>', JS.replace('<script>', '<script id="kab-js">', 1) + '\n</body>', 1)
open('about-keith.html', 'w', encoding='utf-8').write(ak)
print('about stats: home + about-keith.html, %d countries' % len(COUNTRIES))
