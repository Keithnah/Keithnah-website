"""Keith's award and event photos on about-keith.html, just above "Watch Before You Buy".

Top row: two award collages, No. 1 = Year 2025, No. 2 = Year 2024. Below: event photos.
Photos are in images/keith/ (from Keith's Drive folder "PERSONAL PHOTO FOR WEB").
Texts in six languages, swapped in the browser (kn_lang). Safe to run again (KN-PHOTOS markers).

    python3 tools/build_about_photos.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)

LG = ['en', 'zh-CN', 'zh-TW', 'ms', 'ja', 'ko']
T = {
    'eb': ['Awards & Milestones', '荣誉与里程碑', '榮譽與里程碑', 'Anugerah & Pencapaian', '受賞と実績', '수상과 성과'],
    'h2': ['Recognition along the way', '一路走来的肯定', '一路走來的肯定', 'Pengiktirafan sepanjang perjalanan', 'これまでの評価', '지금까지의 인정'],
    'y25': ['Year 2025', '2025 年', '2025 年', 'Tahun 2025', '2025年', '2025년'],
    'y24': ['Year 2024', '2024 年', '2024 年', 'Tahun 2024', '2024年', '2024년'],
    'c25': ['Monthly sales awards, 2025', '2025 年每月销售奖项', '2025 年每月銷售獎項', 'Anugerah jualan bulanan, 2025', '2025年 月間セールス賞', '2025년 월간 판매 수상'],
    'c24': ['Monthly sales awards, central region, 2024', '2024 年中区每月销售奖项', '2024 年中區每月銷售獎項', 'Anugerah jualan bulanan, wilayah tengah, 2024', '2024年 中部地域 月間セールス賞', '2024년 중부 지역 월간 판매 수상'],
    'p1': ['Million Dollar Achievers Club 2024, Diamond', 'Million Dollar Achievers Club 2024 钻石级', 'Million Dollar Achievers Club 2024 鑽石級', 'Million Dollar Achievers Club 2024, Diamond', 'Million Dollar Achievers Club 2024 ダイヤモンド', 'Million Dollar Achievers Club 2024 다이아몬드'],
    'p2': ['Top Performance 2024', '2024 年最佳表现', '2024 年最佳表現', 'Prestasi Terbaik 2024', '2024年 トップパフォーマンス', '2024년 최우수 실적'],
    'p3': ['IQI Prestige Award night', 'IQI Prestige Award 颁奖礼', 'IQI Prestige Award 頒獎禮', 'Malam IQI Prestige Award', 'IQI Prestige Award 授賞式', 'IQI Prestige Award 시상식'],
    'p4': ['Sharing with the team', '和团队分享', '和團隊分享', 'Berkongsi dengan pasukan', 'チームへのシェア', '팀과의 공유'],
    'p5': ['With the Bricksmen team', '和 Bricksmen 团队', '和 Bricksmen 團隊', 'Bersama pasukan Bricksmen', 'Bricksmen チームと', 'Bricksmen 팀과 함께'],
}
TOP = [('awards-2025', 'y25', 'c25', '1'), ('awards-2024', 'y24', 'c24', '2')]
PHOTOS = [('million-dollar-achievers-2024', 'p1'), ('top-performance-2024', 'p2'), ('iqi-prestige-award', 'p3'),
          ('congratulations-speech', 'p4'), ('bricksmen-team', 'p5')]

CSS = ('.kph{padding:84px 6vw 70px;background:#F9F8F6}.kph-in{max-width:1180px;margin:0 auto}.kph .section-head{text-align:center;margin-bottom:34px}'
       '.kph-top{display:grid;grid-template-columns:1fr 1fr;gap:22px}.kph-card{position:relative;display:block;background:#fff;border:1px solid #DEDCF7;border-radius:22px;overflow:hidden;box-shadow:0 14px 34px rgba(29,27,79,.08)}'
       '.kph-card img{display:block;width:100%;aspect-ratio:1/1;object-fit:cover}.kph-head{display:flex;align-items:center;padding:14px 16px}.kph-yr{display:inline-flex;align-items:center;gap:8px;background:#5E60CE;color:#fff;'
       'font:700 13px Inter,sans-serif;letter-spacing:.06em;text-transform:uppercase;padding:8px 14px;border-radius:99px;box-shadow:0 6px 16px rgba(29,27,79,.25)}'
       '.kph-yr b{display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;background:#fff;color:#5E60CE;font-size:12px}'
       '.kph-cap{display:block;padding:14px 18px;font:600 14px Inter,sans-serif;color:#15142b}'
       '.kph-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:16px;margin-top:22px}.kph-ph{grid-column:span 2;position:relative;display:block;border-radius:18px;overflow:hidden;background:#fff;border:1px solid #DEDCF7}'
       '.kph-ph:nth-child(4),.kph-ph:nth-child(5){grid-column:span 3}.kph-ph img{display:block;width:100%;height:260px;object-fit:cover;object-position:center 30%;transition:transform .4s}'
       '.kph-ph:hover img,.kph-card:hover img{transform:scale(1.03)}.kph-card img{transition:transform .4s}'
       '.kph-ph span{position:absolute;left:0;right:0;bottom:0;padding:26px 14px 12px;font:600 13px Inter,sans-serif;color:#fff;background:linear-gradient(transparent,rgba(21,20,43,.8))}'
       '@media(max-width:820px){.kph{padding:56px 16px 48px}.kph-top{grid-template-columns:1fr;gap:16px}.kph-grid{grid-template-columns:1fr 1fr;gap:10px}'
       '.kph-ph,.kph-ph:nth-child(4),.kph-ph:nth-child(5){grid-column:span 1}.kph-ph:nth-child(5){grid-column:span 2}.kph-ph img{height:200px}}')

JS = ('<script>(function(){var T=%s,LG=%s;function f(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}var i=Math.max(0,LG.indexOf(l));'
      'document.querySelectorAll("[data-kph]").forEach(function(el){var v=T[el.getAttribute("data-kph")];if(v)el.textContent=v[i];});}f();'
      'document.addEventListener("DOMContentLoaded",function(){["knSetLang","setLanguage"].forEach(function(n){var s=window[n];if(typeof s==="function")window[n]=function(){var r=s.apply(this,arguments);f();return r;};});f();});})();</script>'
      ) % (json.dumps(T, ensure_ascii=False), json.dumps(LG))


def tx(k, tag='span', cls=''):
    return '<%s%s data-kph="%s">%s</%s>' % (tag, (' class="%s"' % cls) if cls else '', k, T[k][0], tag)


def block():
    top = ''.join('<a class="kph-card" href="images/keith/%s.jpg" target="_blank" rel="noopener"><span class="kph-head"><span class="kph-yr"><b>%s</b>%s</span></span>'
                  '<img src="images/keith/%s.jpg" alt="Keith Nah sales awards %s" loading="lazy">%s</a>' % (
                      f, n, tx(y), f, T[y][0][-4:], tx(c, 'span', 'kph-cap')) for f, y, c, n in TOP)
    grid = ''.join('<a class="kph-ph" href="images/keith/%s.jpg" target="_blank" rel="noopener"><img src="images/keith/%s.jpg" alt="Keith Nah: %s" loading="lazy">%s</a>' % (
        f, f, T[k][0], tx(k)) for f, k in PHOTOS)
    return ('<!-- KN-PHOTOS:START --><style>%s</style><section class="kph"><div class="kph-in"><div class="section-head">%s%s<div class="hairline"></div></div>'
            '<div class="kph-top">%s</div><div class="kph-grid">%s</div></div></section>%s<!-- KN-PHOTOS:END -->\n') % (
        CSS, tx('eb', 'span', 'eyebrow'), tx('h2', 'h2'), top, grid, JS)


p = 'about-keith.html'
s = open(p, encoding='utf-8').read()
s = re.sub(r'<!-- KN-PHOTOS:START -->.*?<!-- KN-PHOTOS:END -->\n?', '', s, flags=re.S)
anchor = '<!-- ===================== YOUTUBE ===================== -->'
assert anchor in s
s = s.replace(anchor, block() + anchor, 1)
open(p, 'w', encoding='utf-8').write(s)
print('about photos: %d top + %d photos' % (len(TOP), len(PHOTOS)))
