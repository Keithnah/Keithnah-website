"""New page tops (kn_hero.py design B) for Projects, Compare, Foreign Buyers, News, Free Toolkit and every developer page.

Runs late in build_all (after the pages are generated, before build_menu.py). Safe to run twice: the block it adds sits
between <!-- KNB:START --> and <!-- KNB:END -->. On compare.html and projects.html (edited in place by other tools) the
old top stays in the file and is hidden with CSS, so those tools keep finding it."""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
sys.path.insert(0, HERE)
import kn_hero as K  # noqa: E402

L = K.L
WA = 'https://api.whatsapp.com/send/?phone=60102821568&text=%28KNRE%29+Hi+Keith%2C+I+would+like+to+ask+about+a+project.&type=phone_number&app_absent=0'
IDX = json.load(open(os.path.join(HERE, 'project_index.json'), encoding='utf-8'))
N_PROJ = len(IDX)
N_STATES = len({p['state'] for p in IDX if p.get('state')})
N_DEV = len([f for f in glob.glob('developer/*.html') if not f.endswith('index.html')])
N_STN = len(json.load(open(os.path.join(HERE, 'stations.json'), encoding='utf-8'))['stations'])
N_VS = len([f for f in glob.glob('vs/*.html') if not f.endswith('index.html')])
try:
    FQ = json.load(open(os.path.join(HERE, 'faq_topics.json'), encoding='utf-8'))
    N_FAQ = len({i for t in FQ['topics'] for i in t['ids']})
except (OSError, ValueError):
    N_FAQ = 0
try:
    N_NOTES = len(json.load(open(os.path.join(HERE, 'market_notes.json'), encoding='utf-8')))
except (OSError, ValueError):
    N_NOTES = 0
N_ART = open('articles.html', encoding='utf-8').read().count('class="article-card"') if os.path.exists('articles.html') else 0


def proj_images(n=3, status=None):
    """Photos of projects from the map data in projects.html (newest launches first when asked)."""
    t = open('projects.html', encoding='utf-8').read()
    m = re.search(r'<!-- KN-MAP:START -->.*?var P=', t, re.S)
    if not m:
        return []
    P, _ = json.JSONDecoder().raw_decode(t[m.end():])
    pick = [p for p in P if p.get('i') and (not status or p.get('s') == status)] or [p for p in P if p.get('i')]
    return [p['i'] for p in pick[:n]]


SKY = 'images/18c3c17601a2ba81.jpg'
U = lambda k: 'images/understand/%s.jpg' % k
X = {
    'home': L('Home', '首页', 'Laman Utama', 'ホーム', '홈'),
    'projects': L('Projects', '项目', 'Projek', '物件', '프로젝트'),
    'compare': L('Compare', '比较', 'Banding', '比較', '비교'),
    'news': L('News', '新闻', 'Berita', 'ニュース', '뉴스'),
    'toolkit': L('Free Toolkit', '免费工具', 'Alat Percuma', '無料ツール', '무료 도구'),
    'n_proj': L('Projects', '个项目', 'Projek', '物件', '프로젝트'),
    'n_states': L('States', '个州属', 'Negeri', '州', '개 주'),
    'n_dev': L('Developers', '家发展商', 'Pemaju', 'デベロッパー', '개발사'),
    'n_stn': L('Rail stations mapped', '个车站上地图', 'Stesen rel dipetakan', '地図上の駅', '지도에 표시된 역'),
    'wa': L('WhatsApp Keith', 'WhatsApp Keith', 'WhatsApp Keith', 'WhatsApp で相談', 'WhatsApp 문의'),
    'find': L('Find my home', '帮我找房', 'Cari rumah saya', '住まい探し', '내 집 찾기'),
}


def block(page, html_, extra_css=''):
    return '<!-- KNB:START -->%s%s%s<!-- KNB:END -->' % (K.CSS, extra_css, html_)


def strip_old(t):
    return re.sub(r'<!-- KNB:START -->.*?<!-- KNB:END -->', '', t, flags=re.S)


def write(f, t, tx):
    t = re.sub(r'<script data-knb>.*?</script>', '', t, flags=re.S)
    t = t.replace('</body>', tx.script().replace('<script>', '<script data-knb>', 1) + '\n</body>', 1)
    open(f, 'w', encoding='utf-8').write(t)


done = []

# ---------------- Projects ----------------
f = 'projects.html'
t = strip_old(open(f, encoding='utf-8').read())
tx = K.Tx()
left = (K.crumbs([(tx('home', X['home']), 'index.html'), (tx('projects', X['projects']), None)]) +
        tx('p_eb', L('Full portfolio', '全部项目', 'Portfolio penuh', '全物件', '전체 포트폴리오'), 'span', 'knb-eb') +
        '<h1>%s <em>%s</em></h1>' % (tx('p_h1a', L('Every project,', '所有项目，', 'Setiap projek,', 'すべての物件を、', '모든 프로젝트를')), tx('p_h1b', L('one place.', '一站看齐。', 'satu tempat.', 'ひとつの場所で。', '한곳에서.'))) +
        '<p>%s</p>' % tx('p_lead', L('{n} active and completed projects, organised by state and area, with prices, layouts and the nearest stations.',
                                      '{n} 个在售和已完工项目，按州属和地区整理，附价格、户型和最近的车站。',
                                      '{n} projek aktif dan siap, disusun mengikut negeri dan kawasan, dengan harga, pelan lantai dan stesen terdekat.',
                                      '販売中・完成済みの {n} 件の物件を、州とエリア別に、価格・間取り・最寄り駅とともに整理。',
                                      '판매 중이거나 완공된 {n}개 프로젝트를 주와 지역별로, 가격·평면도·가까운 역과 함께 정리했습니다.'), n=N_PROJ) +
        K.pills([(tx('p_b1', L('Search projects', '搜索项目', 'Cari projek', '物件を検索', '프로젝트 검색')), '#projSearch'),
                 (tx('p_b2', L('All project list', '全部项目列表', 'Senarai semua projek', '全物件リスト', '전체 프로젝트 목록')), '#projGrid'),
                 (tx('p_b3', L('Project map', '项目地图', 'Peta projek', '物件マップ', '프로젝트 지도')), 'map.html'),
                 (tx('p_b4', L('Station map', '车站地图', 'Peta stesen', '駅マップ', '역 지도')), 'station-map.html'),
                 (tx('p_b5', L('Best new launches', '最佳新盘', 'Projek baharu terbaik', '注目の新築', '추천 신규 분양')), 'best/index.html'),
                 (tx('p_b6', L('By developer', '按发展商', 'Mengikut pemaju', 'デベロッパー別', '개발사별')), 'developer/index.html')]))
stats = K.stats_html([(N_PROJ, tx('n_proj', X['n_proj'])), (N_STATES, tx('n_states', X['n_states'])), (N_DEV, tx('n_dev', X['n_dev'])), (N_STN, tx('n_stn', X['n_stn']))])
hide = '<style>.proj-hero>.eyebrow,.proj-hero>h1,.proj-hero>p{display:none!important}.proj-hero{padding-top:34px!important;min-height:0!important}</style>'
t = t.replace('<section class="proj-hero">', block(f, K.hero(left, proj_images(3, 'New Launch'), stats), hide) + '<section class="proj-hero">', 1)
write(f, t, tx); done.append(f)

# ---------------- Compare ----------------
f = 'compare.html'
t = strip_old(open(f, encoding='utf-8').read())
tx = K.Tx()
left = (K.crumbs([(tx('home', X['home']), 'index.html'), (tx('compare', X['compare']), None)]) +
        tx('c_eb', L('Compare projects', '项目比较', 'Bandingkan projek', '物件を比較', '프로젝트 비교'), 'span', 'knb-eb') +
        '<h1>%s <em>%s</em></h1>' % (tx('c_h1a', L('Compare projects,', '项目比较，', 'Bandingkan projek,', '物件を', '프로젝트를')), tx('c_h1b', L('side by side.', '一目了然。', 'bersebelahan.', '並べて比較。', '나란히 비교.'))) +
        '<p>%s</p>' % tx('c_lead', L('Pick up to three projects and see price, size, tenure, completion and location in one table, or open a ready-made head-to-head.',
                                      '最多选三个项目，在同一个表里比较价格、面积、地契、完工日期和地点，或直接打开现成的一对一比较。',
                                      'Pilih sehingga tiga projek dan lihat harga, saiz, pegangan, siap dan lokasi dalam satu jadual, atau buka perbandingan bersemuka yang sedia ada.',
                                      '最大3件の物件を選び、価格・広さ・権利形態・完成時期・立地を1つの表で比較。用意された1対1比較も開けます。',
                                      '최대 3개 프로젝트를 골라 가격, 면적, 소유 형태, 완공 시기, 위치를 한 표에서 비교하거나, 미리 만든 1:1 비교를 열어 보세요.')) +
        K.pills([(tx('c_b1', L('Start comparing', '开始比较', 'Mula bandingkan', '比較を始める', '비교 시작')), '#cmpFilters'),
                 (tx('c_b2', L('Head-to-head pages', '一对一比较页', 'Halaman bersemuka', '1対1比較ページ', '1:1 비교 페이지')), 'vs/index.html'),
                 (tx('c_b3', L('Popular comparisons', '热门比较', 'Perbandingan popular', '人気の比較', '인기 비교')), '#popular'),
                 (tx('find', X['find']), 'find-my-home.html')]))
stats = K.stats_html([(N_PROJ, tx('c_s1', L('Projects to compare', '个可比较项目', 'Projek untuk dibanding', '比較できる物件', '비교 가능한 프로젝트'))),
                      (N_VS, tx('c_s2', L('Head-to-head pages', '个一对一比较', 'Halaman bersemuka', '1対1比較', '1:1 비교'))),
                      (3, tx('c_s3', L('Projects at a time', '个项目同时比较', 'Projek serentak', '同時に比較', '한 번에 비교'))),
                      (N_STATES, tx('n_states', X['n_states']))])
hide = '<style>.cmp-hero{display:none!important}</style>'
t = t.replace('<section class="cmp-hero">', block(f, K.hero(left, [SKY, U('glance'), U('transport')], stats), hide) + '<section class="cmp-hero">', 1)
write(f, t, tx); done.append(f)

# ---------------- Foreign Buyers (regenerated by build_foreign.py) ----------------
f = 'foreign-buyers.html'
t = open(f, encoding='utf-8').read()
m = re.search(r'<section class="fh">(.*?)</section>', t, re.S)
if m and 'KNB:START' not in t:
    tx = K.Tx()
    left = K.crumbs([(tx('home', X['home']), 'index.html'), (tx('fb', L('Foreign Buyers', '外国买家', 'Pembeli Asing', '外国人購入者', '외국인 구매자')), None)]) + m.group(1)
    stats = K.stats_html([(N_PROJ, tx('n_proj', X['n_proj'])), (13, tx('n_states', X['n_states'])),
                          ('12', tx('f_s3', L('Topics on Malaysia', '个马来西亚主题', 'Topik tentang Malaysia', 'マレーシアのトピック', '말레이시아 주제'))),
                          ('6', tx('f_s4', L('Languages', '种语言', 'Bahasa', '言語', '개 언어')))])
    hero_ = block(f, K.hero(left, [U('glance'), U('people'), U('places')], stats))
    w = re.search(r'<main class="wrap">\s*$', t[:m.start()])
    if w:   # put the full-width top before <main class="wrap">
        t = t[:w.start()] + hero_ + '<main class="wrap">' + t[m.end():]
    else:
        t = t[:m.start()] + hero_ + t[m.end():]
    write(f, t, tx); done.append(f)

# ---------------- Free Toolkit (regenerated by build_resources.py) ----------------
f = 'resources.html'
t = open(f, encoding='utf-8').read()
m = re.search(r'<section class="rh">(.*?)</section>', t, re.S)
if m and 'KNB:START' not in t:
    tx = K.Tx()
    inner = m.group(1)
    inner = re.sub(r'<h1 data-r="title">.*?</h1>\s*<p class="lead" data-r="lead">(.*?)</p>',
                   lambda x: '<h1>%s <em>%s</em></h1>' % (tx('r_h1a', L('Where would you like', '你想从', 'Di mana anda mahu', 'どこから', '어디서부터')),
                                                          tx('r_h1b', L('to start?', '哪里开始？', 'bermula?', '始めますか？', '시작할까요?'))), inner, count=1, flags=re.S)
    left = (K.crumbs([(tx('home', X['home']), 'index.html'), (tx('toolkit', X['toolkit']), None)]) + inner +
            K.pills([(tx('r_b1', L('Understand Malaysia', '了解马来西亚', 'Fahami Malaysia', 'マレーシアを知る', '말레이시아 이해하기')), 'understand/'),
                     (tx('r_b2', L('Free area guide download', '免费地区指南下载', 'Muat turun panduan kawasan percuma', '無料エリアガイド', '무료 지역 가이드 다운로드')), '#guides'),
                     (tx('r_b3', L('Free MM2H guide', '免费 MM2H 指南', 'Panduan MM2H percuma', '無料 MM2H ガイド', '무료 MM2H 가이드')), 'mm2h.html'),
                     (tx('r_b4', L('Free calculator', '免费计算器', 'Kalkulator percuma', '無料計算ツール', '무료 계산기')), 'calculator.html'),
                     (tx('r_b5', L('Free one-to-one advice', '免费一对一咨询', 'Nasihat percuma satu-ke-satu', '無料の個別相談', '무료 1:1 상담')), WA)]))
    stats = K.stats_html([(N_PROJ, tx('n_proj', X['n_proj'])), ('12', tx('f_s3', L('Topics on Malaysia', '个马来西亚主题', 'Topik tentang Malaysia', 'マレーシアのトピック', '말레이시아 주제'))),
                          (N_FAQ, tx('r_s3', L('Questions answered', '个问题解答', 'Soalan dijawab', '回答済みの質問', '답변된 질문'))),
                          ('6', tx('f_s4', L('Languages', '种语言', 'Bahasa', '言語', '개 언어')))])
    hero_ = block(f, K.hero(left, [U('glance'), U('schools'), U('places')], stats))
    w = re.search(r'<main class="wrap">\s*$', t[:m.start()])
    if w:   # put the full-width top before <main class="wrap">
        t = t[:w.start()] + hero_ + '<main class="wrap">' + t[m.end():]
    else:
        t = t[:m.start()] + hero_ + t[m.end():]
    write(f, t, tx); done.append(f)

# ---------------- News hub (regenerated by build_news_split.py) ----------------
f = 'blog.html'
t = open(f, encoding='utf-8').read()
m = re.search(r'<section class="journal-hero">(.*?)</section>', t, re.S)
if m and 'KNB:START' not in t:
    tx = K.Tx()
    inner = m.group(1)
    nav = re.search(r'<nav class="nw-jump.*?</nav>', inner, re.S)
    navh = nav.group(0) if nav else ''
    inner = inner.replace(navh, '')
    left = K.crumbs([(tx('home', X['home']), 'index.html'), (tx('news', X['news']), None)]) + inner
    stats = K.stats_html([(N_NOTES, tx('b_s1', L('Market notes', '篇市场短评', 'Nota pasaran', 'マーケットノート', '마켓 노트'))),
                          (N_ART, tx('b_s2', L('Articles', '篇文章', 'Artikel', '記事', '기사'))),
                          (N_FAQ, tx('r_s3', L('Questions answered', '个问题解答', 'Soalan dijawab', '回答済みの質問', '답변된 질문'))),
                          ('6', tx('f_s4', L('Languages', '种语言', 'Bahasa', '言語', '개 언어')))])
    fix = '<style>.knb .knb-below nav.nw-jump.nw-tabs{margin-top:60px!important}</style>'
    t = t[:m.start()] + block(f, K.hero(left, [SKY, U('transport'), U('malls')], stats, navh), fix) + t[m.end():]
    write(f, t, tx); done.append(f)

# ---------------- Developer pages (regenerated by build_hubs.py) ----------------
n_dev = 0
for f in sorted(glob.glob('developer/*.html')):
    if f.endswith('index.html'):
        continue
    t = open(f, encoding='utf-8').read()
    m = re.search(r'<section class="hero">(.*?)</section>', t, re.S)
    if not m or 'KNB:START' in t:
        continue
    tx = K.Tx()
    inner = m.group(1)
    inner = re.sub(r'^<div class="w">|</div>$', '', inner.strip())
    dvs = re.search(r'<div class="dvs">.*</div>', inner, re.S)
    stats = dvs.group(0) if dvs else ''
    left = inner.replace(stats, '') if stats else inner
    name = re.search(r'<nav class="crumb".*?<span>([^<]*)</span></nav>', left, re.S)
    first_state = re.search(r'id="(st-[a-z-]+)"', t)
    left += K.pills([(tx('d_b1', L('See the projects', '查看项目', 'Lihat projek', '物件を見る', '프로젝트 보기')), '#' + first_state.group(1) if first_state else '#'),
                     (tx('d_b2', L('Compare projects', '比较项目', 'Bandingkan projek', '物件を比較', '프로젝트 비교')), '../compare.html'),
                     (tx('d_b3', L('All developers', '全部发展商', 'Semua pemaju', 'デベロッパー一覧', '전체 개발사')), 'index.html'),
                     (tx('wa', X['wa']), WA)])
    body = t[m.end():]
    imgs = []
    for s in re.findall(r'src="(\.\./images/[0-9a-f]{16}\.(?:webp|jpg|png))"', body):
        if s not in imgs:
            imgs.append(s)
    imgs = imgs[:3] or ['../' + SKY, '../' + U('glance'), '../' + U('transport')]
    t = t[:m.start()] + block(f, K.hero(left, imgs, stats)) + t[m.end():]
    write(f, t, tx)
    n_dev += 1
print('page tops: %s, %d developer pages' % (', '.join(done), n_dev))
