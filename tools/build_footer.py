"""One footer for every page: brand, REN, social icons, and links to the main sections.

Replaces the <footer>...</footer> of every English page (the language copies are rendered from
them). Labels are switched to the visitor's language by a small script, like the rest of the site.
Run by tools/build_all.py; safe to run again.
"""
import glob
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
DIRS = ['', 'article', 'area', 'best', 'developer', 'guides', 'notes', 'property', 'station', 'topic', 'vs']
WA = 'https://wa.me/60102821568?text=' + 'Hi%20Keith%2C%20I%20would%20like%20to%20explore%20more%20on%20Malaysia%20Property.'
LANGS = ['en', 'zh-CN', 'zh-TW', 'ms', 'ja', 'ko']

T = {  # key: [en, zh-CN, zh-TW, ms, ja, ko]
    'tag': ['Premium Kuala Lumpur real estate — KL City Centre, TRX, Bukit Bintang, Bangsar and beyond.',
            '吉隆坡优质房产 — KL City Centre、TRX、Bukit Bintang、Bangsar 及更多地区。',
            '吉隆坡優質房產 — KL City Centre、TRX、Bukit Bintang、Bangsar 及更多地區。',
            'Hartanah premium Kuala Lumpur — KL City Centre, TRX, Bukit Bintang, Bangsar dan sekitarnya.',
            'クアラルンプールの上質な不動産 — KL City Centre、TRX、Bukit Bintang、Bangsar など。',
            '쿠알라룸푸르 프리미엄 부동산 — KL City Centre, TRX, Bukit Bintang, Bangsar 등.'],
    'h_ex': ['Explore', '浏览', '瀏覽', 'Teroka', '探す', '둘러보기'],
    'h_in': ['Insights', '市场资讯', '市場資訊', 'Wawasan', 'インサイト', '인사이트'],
    'h_ar': ['Popular Areas', '热门地区', '熱門地區', 'Kawasan Popular', '人気エリア', '인기 지역'],
    'h_ab': ['About', '关于', '關於', 'Tentang', '概要', '소개'],
    'projects': ['All Projects', '全部项目', '全部項目', 'Semua Projek', 'すべての物件', '전체 프로젝트'],
    'quiz': ['Find My Home', '帮我找房', '幫我找房', 'Cari Rumah Saya', 'おうち探し', '내 집 찾기'],
    'compare': ['Compare Projects', '项目对比', '項目對比', 'Bandingkan Projek', '物件を比較', '프로젝트 비교'],
    'calc': ['Loan Calculator', '房贷计算器', '房貸計算器', 'Kalkulator Pinjaman', 'ローン計算機', '대출 계산기'],
    'mm2h': ['MM2H Guide', 'MM2H 指南', 'MM2H 指南', 'Panduan MM2H', 'MM2H ガイド', 'MM2H 가이드'],
    'notes': ['Market Notes', '每日市场短评', '每日市場短評', 'Nota Pasaran', 'マーケットノート', '마켓 노트'],
    'data': ['Market Data', '市场数据', '市場數據', 'Data Pasaran', 'マーケットデータ', '마켓 데이터'],
    'journal': ['The Journal', '房产资讯', '房產資訊', 'Jurnal', 'ジャーナル', '저널'],
    'best': ['Best New Launches', '精选新盘', '精選新盤', 'Projek Baharu Terbaik', 'おすすめ新築物件', '추천 신규 분양'],
    'kit': ['Free Toolkit', '免费工具包', '免費工具包', 'Kit Percuma', '無料ツールキット', '무료 툴킷'],
    'about': ['About Keith', '关于 Keith', '關於 Keith', 'Tentang Keith', 'Keith について', 'Keith 소개'],
    'wa': ['WhatsApp Keith', 'WhatsApp Keith', 'WhatsApp Keith', 'WhatsApp Keith', 'Keith に WhatsApp', 'Keith에게 WhatsApp'],
    'priv': ['Privacy Policy', '隐私政策', '隱私權政策', 'Dasar Privasi', 'プライバシーポリシー', '개인정보 처리방침'],
    'terms': ['Terms of Use', '使用条款', '使用條款', 'Terma Penggunaan', '利用規約', '이용약관'],
    'copy': ['© 2026 Keith Nah Real Estate. All rights reserved.', '© 2026 Keith Nah Real Estate. 版权所有。',
             '© 2026 Keith Nah Real Estate. 版權所有。', '© 2026 Keith Nah Real Estate. Hak cipta terpelihara.',
             '© 2026 Keith Nah Real Estate. All rights reserved.', '© 2026 Keith Nah Real Estate. 모든 권리 보유.'],
    'loc': ['Kuala Lumpur, Malaysia', '马来西亚 吉隆坡', '馬來西亞 吉隆坡', 'Kuala Lumpur, Malaysia',
            'マレーシア・クアラルンプール', '말레이시아 쿠알라룸푸르'],
}
AREAS = [('KL City Centre', 'area/kl-city-centre.html'), ('Bukit Bintang', 'area/bukit-bintang.html'), ('TRX', 'area/trx.html'),
         ('Bangsar', 'area/bangsar.html'), ('Penang', 'area/penang.html'), ('Johor Bahru', 'area/jb-city-centre.html')]
COLS = [('h_ex', [('projects', 'projects.html'), ('quiz', 'find-my-home.html'), ('compare', 'compare.html'),
                  ('calc', 'calculator.html'), ('mm2h', 'mm2h.html')]),
        ('h_in', [('notes', 'market-notes.html'), ('data', 'market-data.html'), ('journal', 'blog.html'), ('best', 'best/index.html'), ('kit', 'resources.html')]),
        ('h_ar', None),
        ('h_ab', [('about', 'about-keith.html'), ('wa', WA), ('priv', 'privacy-policy.html'), ('terms', 'terms-of-use.html')])]

FB = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M13.5 21v-7.5h2.5l.4-3h-2.9V8.6c0-.9.3-1.5 1.5-1.5h1.6V4.4c-.3 0-1.2-.1-2.3-.1-2.3 0-3.8 1.4-3.8 3.9v2.3H8v3h2.5V21h3z"/></svg>'
YT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.8 1.8C5.8 19 12 19 12 19s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8zM10 15V9l5.2 3L10 15z"/></svg>'
IG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 7.3A4.7 4.7 0 1 0 16.7 12 4.7 4.7 0 0 0 12 7.3zm0 7.7a3 3 0 1 1 3-3 3 3 0 0 1-3 3zm6-7.9a1.1 1.1 0 1 1-1.1-1.1A1.1 1.1 0 0 1 18 7.1zM21 8a5.4 5.4 0 0 0-1.5-3.8A5.4 5.4 0 0 0 15.7 2.7C14.2 2.6 9.8 2.6 8.3 2.7A5.4 5.4 0 0 0 4.5 4.2 5.4 5.4 0 0 0 3 8c-.1 1.5-.1 6.5 0 8a5.4 5.4 0 0 0 1.5 3.8 5.4 5.4 0 0 0 3.8 1.5c1.5.1 5.9.1 7.4 0a5.4 5.4 0 0 0 3.8-1.5A5.4 5.4 0 0 0 21 16c.1-1.5.1-6.5 0-8zm-2 9.7a3 3 0 0 1-1.7 1.7c-1.2.5-4 .4-5.3.4s-4.1.1-5.3-.4A3 3 0 0 1 5 17.7c-.5-1.2-.4-4-.4-5.3s-.1-4.1.4-5.3A3 3 0 0 1 6.7 5.4C7.9 4.9 10.7 5 12 5s4.1-.1 5.3.4A3 3 0 0 1 19 7.1c.5 1.2.4 4 .4 5.3s.1 4.1-.4 5.3z"/></svg>'

CSS = ('<style>footer.knf{background:#080808!important;color:rgba(255,255,255,.5)!important;padding:56px 5vw 30px!important;text-align:left!important;'
       'border:0!important;font-family:Inter,system-ui,sans-serif;font-size:13px;margin:0}'
       '.knf a{text-decoration:none}.knf-top{max-width:1180px;margin:0 auto;display:flex;justify-content:space-between;flex-wrap:wrap;gap:40px;'
       'padding-bottom:40px;border-bottom:1px solid rgba(255,255,255,.08)}'
       '.knf-logo{font-family:"Playfair Display",Georgia,serif;font-size:20px;color:#fff;display:flex;align-items:center;gap:10px}'
       '.knf-logo img{width:34px;height:34px;border-radius:50%;object-fit:contain}.knf-logo em{color:#5E60CE;font-style:italic}'
       '.knf-tag{font-size:12px;max-width:270px;color:rgba(255,255,255,.4);margin:14px 0 0;line-height:1.6}'
       '.knf-ren{font-size:11px;color:rgba(255,255,255,.35);margin:10px 0 0;letter-spacing:.04em}'
       '.knf-so{display:flex;gap:12px;margin-top:20px}.knf-so a{width:42px;height:42px;border-radius:50%;display:flex;align-items:center;'
       'justify-content:center;color:#fff;transition:transform .2s,box-shadow .2s}.knf-so a svg{width:21px;height:21px}'
       '.knf-so a:hover{transform:translateY(-3px);box-shadow:0 8px 18px rgba(0,0,0,.45)}.knf-fb{background:#1877F2}.knf-yt{background:#FF0000}'
       '.knf-ig{background:radial-gradient(circle at 30% 107%,#fdf497 0%,#fd5949 45%,#d6249f 60%,#285AEB 90%)}'
       '.knf-col h5{font-size:11px;text-transform:uppercase;letter-spacing:.14em;color:#fff;margin:0 0 16px;font-weight:700}'
       '.knf-col a{display:block;font-size:13px;margin-bottom:10px;color:rgba(255,255,255,.5);transition:color .3s}.knf-col a:hover{color:#8f91ff}'
       '.knf-bot{max-width:1180px;margin:24px auto 0;display:flex;justify-content:space-between;font-size:11px;letter-spacing:.04em;flex-wrap:wrap;gap:10px}'
       '@media(max-width:700px){.knf-top{display:grid;grid-template-columns:1fr 1fr;gap:28px 20px}.knf-top>div:first-child{grid-column:1/-1}}</style>')


def footer(pre):
    def lnk(k, href):
        full = href if href.startswith('http') else pre + href
        ext = ' target="_blank" rel="noopener"' if href.startswith('http') else ''
        return '<a href="%s"%s data-kf="%s">%s</a>' % (html.escape(full), ext, k, html.escape(T[k][0]))
    cols = []
    for h, items in COLS:
        body = ''.join('<a href="%s%s">%s</a>' % (pre, u, n) for n, u in AREAS) if items is None else ''.join(lnk(k, u) for k, u in items)
        cols.append('<div class="knf-col"><h5 data-kf="%s">%s</h5>%s</div>' % (h, T[h][0], body))
    tr = {k: v for k, v in T.items()}
    js = ('<script>(function(){var T=%s,L=%s;function f(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}var i=L.indexOf(l);if(i<0)i=0;'
          'document.querySelectorAll("[data-kf]").forEach(function(x){var v=T[x.getAttribute("data-kf")];if(v)x.textContent=v[i];});}f();'
          'document.addEventListener("DOMContentLoaded",function(){var s=window.setLanguage;if(typeof s==="function")window.setLanguage=function(){var r=s.apply(this,arguments);f();return r;};f();});})();</script>'
          ) % (json.dumps(tr, ensure_ascii=False), json.dumps(LANGS))
    return '<footer class="knf">' + CSS + ('<div class="knf-top"><div><div class="knf-logo"><img src="%simages/f304c8479b1fe873.png" alt="Keith Nah logo" width="34" height="34" loading="lazy">'
            '<span>Keith Nah 鈞晖 <em>| Real Estate</em></span></div><p class="knf-tag" data-kf="tag">%s</p><p class="knf-ren">REN 60517 · IQI Global</p>'
            '<div class="knf-so"><a class="knf-fb" href="https://www.facebook.com/KeithNahRealEstate" target="_blank" rel="noopener" aria-label="Facebook">%s</a>'
            '<a class="knf-yt" href="https://www.youtube.com/@KeithNahRealEstate" target="_blank" rel="noopener" aria-label="YouTube">%s</a>'
            '<a class="knf-ig" href="https://www.instagram.com/keithnah_/" target="_blank" rel="noopener" aria-label="Instagram">%s</a></div></div>'
            '%s</div><div class="knf-bot"><span data-kf="copy">%s</span><span data-kf="loc">%s</span></div>%s</footer>'
            ) % (pre, html.escape(T['tag'][0]), FB, YT, IG, ''.join(cols), html.escape(T['copy'][0]), T['loc'][0], js)


NESTED = {'compare.html'}
# Dark sections right above the (dark) footer look odd: make them light.
LIGHT_CTA = {'calculator.html', 'about-keith.html'}
LIGHT_CTA_CSS = ('<style id="kn-light-cta">.calc-cta,.keith-contact{background:#F3F1FF!important;color:#1a1a2e!important}'
                 '.calc-cta h2,.keith-contact h2{color:#121212!important}.keith-contact h2 span{color:#5E60CE!important}'
                 '.calc-cta p,.keith-contact p,.keith-contact .scan-caption{color:#555!important}.keith-contact .eyebrow{color:#5E60CE!important}'
                 '.keith-contact .btn-outline{color:#121212!important;border-color:rgba(18,18,18,.25)!important}'
                 '.keith-contact .btn-outline:hover{background:#121212!important;color:#fff!important}'
                 '.keith-contact .scan-frame{box-shadow:0 8px 24px rgba(30,30,80,.10)}</style>')

n = 0
for d in DIRS:
    for f in sorted(glob.glob(os.path.join(d, '*.html') if d else '*.html')):
        t = open(f, encoding='utf-8').read()
        if '<footer' not in t:
            continue
        new = footer('/' if f == '404.html' else ('../' if d else ''))
        if f in NESTED:  # the old footer sat inside the page's content box: put the new one at the end of the page
            t2 = re.sub(r'<footer\b[^>]*>.*?</footer>', '', t, count=1, flags=re.S)
            t2 = re.sub(r'(</div><!-- /kn-wrap -->)?\s*</body>', '</div><!-- /kn-wrap -->' + new + '\n</body>', t2, count=1)  # the content box is never closed
        else:
            t2 = re.sub(r'<footer\b[^>]*>.*?</footer>', lambda m: new, t, count=1, flags=re.S)
        t2 = re.sub(r'<style id="kn-light-cta">.*?</style>', '', t2, flags=re.S)
        if f in LIGHT_CTA:
            t2 = t2.replace('</head>', LIGHT_CTA_CSS + '</head>', 1)
        if t2 != t:
            open(f, 'w', encoding='utf-8').write(t2)
            n += 1
print('footer: %d page(s) updated' % n)
