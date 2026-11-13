"""Market data page (market-data.html): starting prices and entry price per sq ft by state and area,
worked out from the new launch projects on this site. Six languages; run by tools/build_all.py.
Also adds a link to it on every area page.

Entry price per sq ft = the published starting price (gross) / the smallest unit size. It is a rough
guide to how areas compare, not a transaction price or a valuation.
"""
import collections
import html
import json
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
sys.path.insert(0, HERE)
import hubs_data as HB
import site_header as SH

src = open('projects.html', encoding='utf-8').read()
i = src.index('const PROJECT_DETAILS = ')
P = json.JSONDecoder().raw_decode(src[src.index('=', i) + 1:].lstrip())[0]
IDX = json.load(open(os.path.join(HERE, 'project_index.json'), encoding='utf-8'))
E = html.escape

T = {  # en, zh-CN, ms, ja, ko (zh-TW from zh-CN)
 'eb': ['Market Data', '市场数据', 'Data Pasaran', 'マーケットデータ', '마켓 데이터'],
 'h1': ['New Launch Prices by Area', '各地区新盘价格', 'Harga Projek Baharu Mengikut Kawasan', 'エリア別の新築物件価格', '지역별 신규 분양 가격'],
 'p': ['Starting prices and entry price per sq ft of the {n} new launch projects on this site, by state and area. Updated with every project change.',
       '本网站 {n} 个新楼盘的起价和入门每平方尺价格，按州属和地区整理，项目资料一更新就会同步更新。',
       'Harga permulaan dan harga masuk setiap kaki persegi bagi {n} projek baharu di laman ini, mengikut negeri dan kawasan. Dikemas kini setiap kali projek berubah.',
       '当サイトの新築 {n} 物件の最低価格と1平方フィートあたりの入口価格を、州・エリア別にまとめました。物件情報の更新に合わせて自動で更新されます。',
       '이 사이트의 신규 분양 {n}개 프로젝트의 시작가와 평방피트당 진입 가격을 주와 지역별로 정리했습니다. 프로젝트 정보가 바뀔 때마다 업데이트됩니다.'],
 'tile': ['median entry psf · {n} projects', '入门每平方尺中位数 · {n} 个项目', 'median psf masuk · {n} projek', '入口価格（平方フィート）中央値 · {n} 物件', '진입 psf 중앙값 · {n}개 프로젝트'],
 'c1': ['Entry price per sq ft by area', '各地区入门每平方尺价格', 'Harga masuk setiap kaki persegi mengikut kawasan', 'エリア別・1平方フィートあたりの入口価格', '지역별 평방피트당 진입 가격'],
 'c1p': ["Median of each project's published starting price divided by its smallest unit. Areas with at least 2 priced projects.",
         '每个项目公布的起价除以最小单位面积，再取中位数。只列出至少有 2 个已定价项目的地区。',
         'Median harga permulaan yang diterbitkan bagi setiap projek dibahagi dengan unit terkecilnya. Kawasan dengan sekurang-kurangnya 2 projek berharga.',
         '各物件の公表最低価格を最小ユニットの面積で割った値の中央値。価格のある物件が2件以上のエリアのみ。',
         '각 프로젝트의 공개 시작가를 가장 작은 유닛 면적으로 나눈 값의 중앙값. 가격이 있는 프로젝트가 2개 이상인 지역만.'],
 'c2': ['All states and areas', '所有州属和地区', 'Semua negeri dan kawasan', 'すべての州とエリア', '모든 주와 지역'],
 'c2p': ["Starting prices are the developers' published gross prices.", '起价为发展商公布的总价。', 'Harga permulaan ialah harga kasar yang diterbitkan oleh pemaju.', '最低価格はデベロッパーが公表した総額です。', '시작가는 개발사가 공개한 총액 기준입니다.'],
 'th1': ['Area', '地区', 'Kawasan', 'エリア', '지역'], 'th2': ['Projects', '项目', 'Projek', '物件数', '프로젝트'],
 'th3': ['Lowest start', '最低起价', 'Harga mula terendah', '最低価格', '최저 시작가'], 'th4': ['Median start', '起价中位数', 'Median harga mula', '最低価格の中央値', '시작가 중앙값'],
 'th5': ['Entry psf', '入门 psf', 'psf masuk', '入口 psf', '진입 psf'], 'th6': ['Freehold', '永久地契', 'Pegangan bebas', 'フリーホールド', '프리홀드'],
 'th7': ['Ready by 2027', '2027 年前完工', 'Siap menjelang 2027', '2027年までに完成', '2027년까지 완공'],
 'note': ['%s',
          '入门每平方尺价格只适合用来比较地区，不是成交价，也不是估价。价格会变动，最新价格表请问 Keith。',
          'Harga masuk setiap kaki persegi ialah panduan kasar untuk membandingkan kawasan, bukan harga transaksi atau penilaian. Harga berubah; tanya Keith untuk senarai harga terkini.',
          '入口価格はエリアを比べるための目安で、成約価格や査定額ではありません。価格は変わるため、最新の価格表は Keith にお問い合わせください。',
          '진입 가격은 지역을 비교하기 위한 대략적인 기준이며 실거래가나 감정가가 아닙니다. 가격은 변동되므로 최신 가격표는 Keith에게 문의하세요.'],
 'cta': ['Ask Keith about an area', '向 Keith 询问地区', 'Tanya Keith tentang kawasan', 'エリアについて Keith に相談', 'Keith에게 지역 문의하기'],
 'link': ['How does {a} compare with other areas? See new launch prices in every area →', '{a} 和其他地区比较如何？查看各地区新盘价格 →',
          'Bagaimana {a} berbanding kawasan lain? Lihat harga projek baharu di setiap kawasan →', '{a} は他のエリアと比べてどう？全エリアの新築価格を見る →',
          '{a}는 다른 지역과 비교하면 어떨까요? 모든 지역의 신규 분양 가격 보기 →'],
}
import opencc
_cc = opencc.OpenCC('s2tw').convert
LANGS = ['en', 'zh-CN', 'zh-TW', 'ms', 'ja', 'ko']
TT = {k: [v[0], v[1], _cc(v[1]), v[2], v[3], v[4]] for k, v in T.items()}


def kd(k, **f):
    s = TT[k][0]
    for a, b in f.items():
        s = s.replace('{%s}' % a, str(b))
    return '<span data-kd="%s"%s>%s</span>' % (k, ''.join(' data-%s="%s"' % (a, E(str(b))) for a, b in f.items()), E(s))


KDJS = ('<script>(function(){var T=%s,L=%s;function f(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}var i=Math.max(0,L.indexOf(l));'
        'document.querySelectorAll("[data-kd]").forEach(function(x){var s=(T[x.getAttribute("data-kd")]||[])[i];if(!s)return;'
        'x.textContent=s.replace(/\\{(\\w+)\\}/g,function(m,k){return x.getAttribute("data-"+k)||m;});});}f();'
        'document.addEventListener("DOMContentLoaded",function(){var s=window.knSetLang;if(typeof s==="function")window.knSetLang=function(){var r=s.apply(this,arguments);f();return r;};f();});})();</script>'
        ) % (json.dumps(TT, ensure_ascii=False), json.dumps(LANGS))

AREA_PAGES = {os.path.basename(f)[:-5] for f in os.listdir('area')}

rows = []
for k, p in enumerate(P):
    pr = HB.price(p.get('price'))
    sizes = [int(x.replace(',', '')) for x in re.findall(r'(\d[\d,]{2,})\s*(?:–|-|sq)', (p.get('size') or '') + ' sq')]
    sz = min(sizes) if sizes else None
    y = re.search(r'(20\d\d)', p.get('completion') or '')
    rows.append({'n': p['name'], 'slug': IDX[k]['slug'], 'state': IDX[k]['state'], 'area': IDX[k]['area'], 'price': pr,
                 'psf': round(pr / sz) if pr and sz and sz >= 300 else None, 'fh': 'freehold' in (p.get('tenure') or '').lower(),
                 'ready': p.get('status') == 'Completed' or (bool(y) and int(y.group(1)) <= 2027)})


def summary(rs):
    ps = [r['psf'] for r in rs if r['psf']]
    pr = [r['price'] for r in rs if r['price']]
    return {'n': len(rs), 'psf': round(st.median(ps)) if ps else None, 'lo': min(pr) if pr else None,
            'med': round(st.median(pr)) if pr else None, 'fh': round(100 * sum(r['fh'] for r in rs) / len(rs)),
            'ready': sum(r['ready'] for r in rs), 'np': len(ps)}


by_state = collections.defaultdict(list)
for r in rows:
    by_state[r['state']].append(r)
states = sorted(by_state, key=lambda s: -len(by_state[s]))
ALL = summary(rows)


def money(v):
    return HB.rm(v) if v else '–'


tiles = ''.join('<div class="md-t"><small>%s</small><b>%s</b>%s</div>'
                % (E(s), ('RM%s' % format(summary(by_state[s])['psf'], ',')) if summary(by_state[s])['psf'] else '–', kd('tile', n=len(by_state[s])))
                for s in states[:4])

# bar chart: areas with 2+ projects that have an entry psf
areas = collections.defaultdict(list)
for r in rows:
    areas[(r['state'], r['area'])].append(r)
bars = sorted([(a, summary(v)) for a, v in areas.items() if summary(v)['np'] >= 2], key=lambda x: -x[1]['psf'])
top = max(s['psf'] for _, s in bars)
chart = ''.join('<div class="md-b"><span class="l">%s<small>%s</small></span><span class="tr"><i style="width:%.1f%%"></i></span><b>RM%s</b></div>'
                % (E(a[1]), E(a[0]), 100 * s['psf'] / top, format(s['psf'], ',')) for a, s in bars)

table = ''
for s in states:
    sub = sorted(((a, v) for (st_, a), v in areas.items() if st_ == s), key=lambda x: -len(x[1]))
    S = summary(by_state[s])
    table += ('<tr class="st"><td>%s</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%d%%</td><td>%d</td></tr>'
              % (E(s), S['n'], money(S['lo']), money(S['med']), ('RM%s' % format(S['psf'], ',')) if S['psf'] else '–', S['fh'], S['ready']))
    for a, v in sub:
        A = summary(v)
        slug = HB.slugify(a)
        name = '<a href="area/%s.html">%s</a>' % (slug, E(a)) if slug in AREA_PAGES else E(a)
        table += ('<tr><td>%s</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%d%%</td><td>%d</td></tr>'
                  % (name, A['n'], money(A['lo']), money(A['med']), ('RM%s' % format(A['psf'], ',')) if A['psf'] else '–', A['fh'], A['ready']))

CSS = '''
:root{--ink:#15142b;--grey:#5f5e74;--line:rgba(21,20,43,.09);--gold:#5E60CE;--bg:#F7F6FB;}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:Inter,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6}a{color:inherit;text-decoration:none}
h1,h2{font-family:'Playfair Display',Georgia,serif;line-height:1.2}
.md{max-width:1080px;margin:0 auto;padding:120px 5vw 70px}
.md-h{text-align:center;margin-bottom:28px}.md-h .eb{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);font-weight:800}
.md-h h1{font-size:clamp(30px,4.6vw,46px);margin:8px 0 10px}.md-h p{color:var(--grey);max-width:680px;margin:0 auto}
.md-ts{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-bottom:22px}
.md-t{background:#fff;border:1px solid var(--line);border-radius:20px;padding:18px 20px;box-shadow:0 10px 30px rgba(29,27,79,.06)}
.md-t small{display:block;font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--grey)}
.md-t b{display:block;font-size:30px;font-weight:800;color:var(--ink);margin:4px 0 0}.md-t span{font-size:12.5px;color:var(--grey)}
.md-c{background:#fff;border:1px solid var(--line);border-radius:24px;padding:26px;margin-bottom:22px;box-shadow:0 10px 30px rgba(29,27,79,.06)}
.md-c h2{font-size:24px;margin-bottom:4px}.md-c>p{color:var(--grey);font-size:13.5px;margin-bottom:18px}
.md-b{display:grid;grid-template-columns:190px 1fr 86px;align-items:center;gap:12px;padding:7px 0;border-bottom:1px solid #f1f0f7}
.md-b .l{font-weight:700;font-size:14px;line-height:1.25}.md-b .l small{display:block;font-weight:500;color:var(--grey);font-size:11.5px}
.md-b .tr{height:14px;background:#efeefb;border-radius:100px;overflow:hidden}.md-b .tr i{display:block;height:100%;border-radius:100px;background:linear-gradient(90deg,#5E60CE,#9a98f0)}
.md-b b{text-align:right;font-size:14px}
.md-tb{overflow-x:auto}.md-tb table{width:100%;border-collapse:collapse;font-size:13.5px;min-width:640px}
.md-tb th{text-align:left;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--grey);padding:10px 10px;border-bottom:2px solid var(--line)}
.md-tb td{padding:9px 10px;border-bottom:1px solid #f1f0f7}.md-tb td:first-child{padding-left:22px}.md-tb tr.st td{background:#f6f5ff;font-weight:800}.md-tb tr.st td:first-child{padding-left:10px}
.md-tb td a{color:var(--gold);font-weight:600}.md-tb td:not(:first-child),.md-tb th:not(:first-child){text-align:right}
.md-n{font-size:12.5px;color:var(--grey);margin-top:14px}
.md-cta{text-align:center;margin-top:26px}.md-cta a{display:inline-block;background:#25D366;color:#fff;font-weight:700;padding:14px 26px;border-radius:14px;box-shadow:0 10px 24px rgba(37,211,102,.3)}
@media(max-width:600px){.md-b{grid-template-columns:110px 1fr 70px;gap:8px}.md-c{padding:18px}}
'''

page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Malaysia New Launch Prices by Area: Entry Price per sq ft | Keith Nah</title>
<meta name="description" content="Starting prices, entry price per sq ft and freehold share of new launch condos by state and area in Malaysia, from %d projects.">
<link rel="canonical" href="https://keithnah.com/market-data.html">
<link rel="icon" type="image/png" href="images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
<style>%s</style>
</head>
<body>
<header>
  <a class="logo" href="./"><img src="images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Malaysia Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="https://api.whatsapp.com/send/?phone=60102821568&amp;type=phone_number&amp;app_absent=0" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
<main class="md">
  <div class="md-h"><span class="eb">%s</span><h1>%s</h1>
  <p>%s</p></div>
  <div class="md-ts">%s</div>
  <section class="md-c"><h2>%s</h2><p>%s</p>%s</section>
  <section class="md-c"><h2>%s</h2><p>%s</p>
  <div class="md-tb"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>
  <p class="md-n">%s</p></section>
  <div class="md-cta"><a href="https://api.whatsapp.com/send/?phone=60102821568&amp;type=phone_number&amp;app_absent=0" target="_blank" rel="noopener">%s</a></div>
</main>
<footer></footer>
%s
</body>
</html>
''' % (len(rows), CSS, kd('eb'), kd('h1'), kd('p', n=len(rows)), tiles, kd('c1'), kd('c1p'), chart, kd('c2'), kd('c2p'),
       ''.join('<th>%s</th>' % kd('th%d' % j) for j in range(1, 8)), table, kd('note'), kd('cta'), KDJS)
open('market-data.html', 'w', encoding='utf-8').write(SH.apply(page, '', 'blog.html'))

# a Market Data panel on the News page, right after Keith's Market Notes
NT = {'eb': ['Market Data', '市场数据', 'Data Pasaran', 'マーケットデータ', '마켓 데이터'],
      'h': ['New launch prices, area by area', '各地区新盘价格一览', 'Harga projek baharu, kawasan demi kawasan', 'エリアごとの新築価格', '지역별 신규 분양 가격'],
      'p': ['Median entry price per sq ft of the new launches on this site, worked out from developers\' published starting prices.',
            '根据发展商公布的起价，算出本网站新楼盘每平方尺入门价格的中位数。',
            'Median harga masuk setiap kaki persegi projek baharu di laman ini, dikira daripada harga permulaan yang diterbitkan pemaju.',
            'デベロッパー公表の最低価格から算出した、当サイト掲載の新築物件の1平方フィートあたり入口価格の中央値。',
            '개발사가 공개한 시작가로 계산한 이 사이트 신규 분양의 평방피트당 진입 가격 중앙값.'],
      'js': ['Prices by area', '各地区价格', 'Harga mengikut kawasan', 'エリア別の価格', '지역별 가격'],
      'b': ['See all areas →', '查看所有地区 →', 'Lihat semua kawasan →', 'すべてのエリアを見る →', '모든 지역 보기 →']}
for k, v in NT.items():
    TT['nd_' + k] = [v[0], v[1], _cc(v[1]), v[2], v[3], v[4]]
KDJS = ('<script>(function(){var T=%s,L=%s;function f(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}var i=Math.max(0,L.indexOf(l));'
        'document.querySelectorAll("[data-kd]").forEach(function(x){var s=(T[x.getAttribute("data-kd")]||[])[i];if(!s)return;'
        'x.textContent=s.replace(/\\{(\\w+)\\}/g,function(m,k){return x.getAttribute("data-"+k)||m;});});}f();'
        'document.addEventListener("DOMContentLoaded",function(){var s=window.knSetLang;if(typeof s==="function")window.knSetLang=function(){var r=s.apply(this,arguments);f();return r;};f();});})();</script>'
        ) % (json.dumps(TT, ensure_ascii=False), json.dumps(LANGS))
top6 = bars[:6]
nd_tiles = ''.join('<a class="nd-t" href="market-data.html"><small>%s</small><b>RM%s</b><span>%s</span></a>' % (E(s), format(summary(by_state[s])['psf'], ','), kd('tile', n=len(by_state[s])))
                   for s in states[:4] if summary(by_state[s])['psf'])
nd_bars = ''.join('<div class="nd-b"><span>%s</span><i><em style="width:%.1f%%"></em></i><b>RM%s</b></div>' % (E(a[1]), 100 * s['psf'] / top, format(s['psf'], ',')) for a, s in top6)
ND = ('<!-- KN-ND:START --><style>.nd{max-width:1180px;margin:0 auto;padding:30px 5vw 50px}.nd-in{background:#fff;border:1px solid rgba(21,20,43,.08);border-radius:26px;padding:30px;'
      'box-shadow:0 18px 44px rgba(29,27,79,.08);display:grid;grid-template-columns:1fr 1.1fr;gap:30px;align-items:center}'
      '.nd-h small{display:block;font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:#5E60CE;font-weight:800}.nd-h h2{font-family:"Playfair Display",Georgia,serif;font-size:clamp(26px,3vw,34px);line-height:1.2;margin:6px 0 10px}'
      '.nd-h p{color:#5f5e74;font-size:14.5px;margin:0 0 16px}.nd-ts{display:grid;grid-template-columns:1fr 1fr;gap:10px}.nd-t{display:block;background:#f6f5ff;border-radius:16px;padding:14px 16px;text-decoration:none;color:#15142b}'
      '.nd-t small{display:block;font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#5f5e74}.nd-t b{display:block;font-size:24px;font-weight:800}.nd-t span{font-size:12px;color:#5f5e74}'
      '.nd-b{display:grid;grid-template-columns:130px 1fr 74px;gap:10px;align-items:center;padding:7px 0;font-size:14px}.nd-b span{font-weight:700}.nd-b i{height:12px;background:#efeefb;border-radius:99px;overflow:hidden}'
      '.nd-b em{display:block;height:100%%;border-radius:99px;background:linear-gradient(90deg,#5E60CE,#9a98f0)}.nd-b b{text-align:right}'
      '.nd a.nd-go{display:inline-block;margin-top:14px;color:#5E60CE;font-weight:700;text-decoration:none}@media(max-width:900px){.nd-in{grid-template-columns:1fr;padding:22px}.nd-b{grid-template-columns:100px 1fr 66px}}</style>'
      '<section class="nd" id="market-data"><div class="nd-in"><div class="nd-h">%s<h2>%s</h2><p>%s</p><div class="nd-ts">%s</div></div>'
      '<div>%s<a class="nd-go" href="market-data.html">%s</a></div></div></section>%s<!-- KN-ND:END -->') % (
    '<small>%s</small>' % kd('nd_eb'), kd('nd_h'), kd('nd_p'), nd_tiles, nd_bars, kd('nd_b'), KDJS)
b = open('blog.html', encoding='utf-8').read()
b = re.sub(r'<!-- KN-ND:START -->.*?<!-- KN-ND:END -->', '', b, flags=re.S)
i_faq = b.find('<section class="nw-sec nf-sec" id="faq"')
b = b[:i_faq] + ND + '\n' + b[i_faq:] if i_faq > 0 else b.replace('<!-- KN-NOTES:END -->', '<!-- KN-NOTES:END -->' + ND, 1)
# a "Market Data" button after "Buying Guide" among the buttons at the top of the News page
b = re.sub(r'<!-- KN-NDJ:START -->.*?<!-- KN-NDJ:END -->', '', b, flags=re.S)
JB = ('<!-- KN-NDJ:START --><a class="nw-jump-btn" href="#market-data"><span class="nw-jump-ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'
      '<path d="M4 20V10M10 20V4M16 20v-8M22 20H2"/></svg></span><span class="nw-jump-txt"><b>%s</b><small>%s</small></span><span class="nw-jump-arrow" aria-hidden="true">&darr;</span></a><!-- KN-NDJ:END -->') % (kd('nd_eb'), kd('nd_js'))
m = re.search(r'<a class="nw-jump-btn" href="#buying-guide">.*?</a>', b, re.S)
if m:
    b = b[:m.end()] + JB + b[m.end():]
open('blog.html', 'w', encoding='utf-8').write(b)

# a link from every area page
LINK = ('<!-- KN-MD:START --><style>.kn-mdl{max-width:1100px;margin:10px auto 34px;padding:0 5vw}.kn-mdl a{display:block;padding:16px 20px;border-radius:16px;'
        'background:#F3F1FF;color:#3b3cb0;font-weight:700;font-size:15px;text-decoration:none;border:1px solid rgba(94,96,206,.18)}.kn-mdl a:hover{background:#e9e6ff}</style>'
        '<div class="kn-mdl"><a href="../market-data.html">%s</a></div>%s<!-- KN-MD:END -->')
na = 0
for f in sorted(os.listdir('area')):
    if not f.endswith('.html'):
        continue
    p = os.path.join('area', f)
    t = open(p, encoding='utf-8').read()
    t2 = re.sub(r'<!-- KN-MD:START -->.*?<!-- KN-MD:END -->', '', t, flags=re.S)
    h = re.search(r'<h1[^>]*>(.*?)</h1>', t2, re.S)
    name = re.sub(r'<[^>]+>', '', h.group(1)).strip() if h else ''
    name = re.sub(r'^New (Launch )?(Condos?|Projects?|Homes?) in |\s*\(?\d{4}\)?$|^New Launches? in ', '', name).strip() or f[:-5]
    t2 = re.sub(r'(<footer\b)', lambda m: LINK % (kd('link', a=name), KDJS) + m.group(1), t2, count=1)
    if t2 != t:
        open(p, 'w', encoding='utf-8').write(t2)
        na += 1
print('market data: %d projects, %d states, %d areas in chart; link on %d area page(s)' % (len(rows), len(states), len(bars), na))
