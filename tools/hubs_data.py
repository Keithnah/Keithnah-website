"""Groups behind the developer, station and head-to-head comparison pages.

compute(P, SLUGS, PLACES) works only from the published project details:
  developers  brands with 2+ projects (one-project pages would be too thin to help anyone)
  stations    rail stations named in 2+ projects' location details (MRT, LRT, Monorail, KTM, RTS)
  pairs       two projects in the same area whose starting prices are within 35%
tools/build_project_pages.py saves the result to tools/hubs.json and links to the pages;
tools/build_hubs.py writes developer/, station/ and vs/. Texts for all 6 languages are in T.
"""
import json
import re
import collections

SITE = 'https://keithnah.com'
# brand names as they appear in the Developer field -> page name
BRANDS = [('exsim', 'Exsim'), ('pavilion', 'Pavilion'), ('ta global', 'TA Global'), ('kerjaya', 'Kerjaya'), ('chin hin', 'Chin Hin'),
          ('oxley', 'Oxley'), ('paramount', 'Paramount'), ('eco world', 'EcoWorld'), ('ecoworld', 'EcoWorld'), ('sunway', 'Sunway'),
          ('sp setia', 'SP Setia'), ('mah sing', 'Mah Sing'), ('uoa', 'UOA'), ('ioi', 'IOI'), ('gamuda', 'Gamuda'), ('sime darby', 'Sime Darby'),
          ('uem', 'UEM Sunrise'), ('tropicana', 'Tropicana'), ('avaland', 'Avaland'), ('skyworld', 'SkyWorld'), ('ijm', 'IJM'), ('ytl', 'YTL'),
          ('mrcb', 'MRCB'), ('symphony', 'Symphony Life'), ('astaka', 'Astaka'), ('crest', 'Crest Builder'), ('brdb', 'BRDB')]
LINES = ['MRT', 'LRT', 'Monorail', 'KTM', 'RTS']
STOP = {'The', 'A', 'An', 'Near', 'To', 'And', 'From', 'Walk', 'Minutes', 'Direct', 'Two', 'Upcoming', 'New', 'Future', 'Planned', 'Nearby', 'Dual',
        'Its', 'With', 'By', 'Sited', 'Located', 'Situated', 'Kuala', "Lumpur's", 'Lumpur', 'Via', 'At', 'Of', 'Linked', 'Connected', 'Beside',
        'Above', 'Next', 'Both', 'Three', 'Several', 'Existing', 'Proposed', 'Is', 'In'}
NOT_STATIONS = {'Mutiara'}   # the Penang Mutiara Line is a line, not a station
STATION_RE = re.compile(r"((?:[A-Z][A-Za-z'&\-]*\s){1,4})(MRT|LRT|Monorail|KTM|RTS)\b")


def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower().replace('&', 'and').replace("'", '')).strip('-')


def price(s):
    """Starting price in RM from texts like 'From RM691,000 (Gross)', 'RM 803.5K', 'RM 1.016M'."""
    m = re.search(r'RM\s?([\d,]+(?:\.\d+)?)\s*([KkMm])?', s or '')
    if not m:
        return None
    v = float(m.group(1).replace(',', ''))
    u = (m.group(2) or '').upper()
    v = v * 1e3 if u == 'K' else v * 1e6 if u == 'M' else v
    return int(v) if v >= 50000 else None


def rm(v):
    return 'RM%.2fM' % (v / 1e6) if v >= 1e6 else 'RM%dK' % round(v / 1e3)


def text(p):
    return ' '.join(str(p.get(k) or '') for k in ('loc_text', 'overview', 'points', 'selling_points'))


def brand(p):
    d = str((p.get('details_extra') or {}).get('Developer', '')).lower()
    for k, name in BRANDS:
        if k in d:
            return name
    return ''


def stations_of(p):
    out = collections.OrderedDict()
    for m in STATION_RE.finditer(text(p)):
        w = m.group(1).split()
        while w and w[0] in STOP:
            w = w[1:]
        if w and w[0] == 'KL' and not (len(w) >= 3 and w[1:3] == ['City', 'Centre']):
            w = w[1:]
        name = ' '.join(w)
        if not name or name in NOT_STATIONS:
            continue
        out.setdefault(name, set()).add(m.group(2))
    return out


def walk_note(p, station):
    """'5-minute walk' / 'about 300 m' if the project's description says so, else ''."""
    for sent in re.split(r'(?<=[.;])\s+', text(p)):
        if station in sent:
            m = re.search(r'(\d{1,2})[- ]?(?:minute|min)s?\b', sent, re.I)
            if m:
                return {'k': 'w_min', 'n': m.group(1)}
            m = re.search(r'(\d{2,4})\s?(?:m|metres|meters)\b', sent)
            if m:
                return {'k': 'w_m', 'n': m.group(1)}
    return {'k': 'w_near'}


def compute(P, SLUGS, PLACES):
    place = lambda i: PLACES[i] if i < len(PLACES) else ('', P[i].get('tag', ''))
    # developers
    dev = collections.defaultdict(list)
    for i, p in enumerate(P):
        b = brand(p)
        if b:
            dev[b].append(i)
    developers = {b: sorted(ix, key=lambda i: P[i]['name'].lower()) for b, ix in dev.items() if len(ix) >= 2}
    # stations
    st = collections.defaultdict(lambda: {'lines': set(), 'ix': set()})
    for i, p in enumerate(P):
        for name, lines in stations_of(p).items():
            st[name]['lines'] |= lines
            st[name]['ix'].add(i)
    stations = {}
    for name, d in st.items():
        if len(d['ix']) >= 2:
            lines = [l for l in LINES if l in d['lines']]
            label = '%s %s' % (name, ' & '.join(lines))
            stations[name] = {'label': label, 'slug': slugify(label), 'lines': lines,
                              'ix': sorted(d['ix'], key=lambda i: P[i]['name'].lower())}
    # head-to-head pairs: same area, prices within 35%, closest first, at most 3 per project
    cand = []
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            if place(i)[1] != place(j)[1]:
                continue
            a, b = price(P[i].get('price')), price(P[j].get('price'))
            if a and b and max(a, b) / min(a, b) <= 1.35:
                cand.append((max(a, b) / min(a, b), i, j))
    cand.sort()
    used = collections.Counter()
    pairs = []
    for _, i, j in cand:
        if used[i] >= 3 or used[j] >= 3:
            continue
        a, b = sorted([i, j], key=lambda k: P[k]['name'].lower())   # A–Z in the title and address
        used[i] += 1
        used[j] += 1
        pairs.append({'a': a, 'b': b, 'slug': '%s-vs-%s' % (SLUGS[a], SLUGS[b]), 'area': place(i)[1], 'state': place(i)[0]})
    pairs.sort(key=lambda x: (x['area'].lower(), P[x['a']]['name'].lower(), P[x['b']]['name'].lower()))
    return {
        'developers': {b: {'slug': slugify(b), 'ix': ix} for b, ix in sorted(developers.items(), key=lambda x: x[0].lower())},
        'stations': {k: dict(v) for k, v in sorted(stations.items(), key=lambda x: x[1]['label'].lower())},
        'pairs': pairs,
    }


# ---------- texts in every site language ({x} = filled in) ----------
T = {
    'en': {
        'home': 'Home', 'projects': 'Projects', 'all': 'All', 'n_proj': '{n} projects', 'cta_wa': 'WhatsApp Keith', 'view': 'View project →',
        'st_projects': 'projects', 'st_states': 'states', 'st_low': 'lowest starting price', 'st_fh': 'freehold projects', 'st_lines': 'rail lines',
        'dev_crumb': 'Developers', 'dev_eb': 'Developer · updated {y}', 'dev_h1': '{d} New Launch Projects ({y})',
        'dev_p': 'Every {d} project Keith Nah currently lists, in {places}: starting prices, tenure and completion dates in one place. Tap a project for floor plans, or ask Keith which one fits your budget.',
        'dev_all': 'All {d} projects', 'faq_dev': '{d}: common questions',
        'dq1': 'How many {d} projects are there in {y}?', 'da1': 'Keith currently lists {n} {d} projects in {places}.',
        'dq2': 'Which {d} project has the lowest starting price?', 'da2': 'The lowest published starting price is about {p} (gross), at {name}. Prices change by phase and unit; ask Keith for the latest.',
        'dq3': 'Are {d} projects freehold?', 'da3': '{f} of the {n} {d} projects listed here are freehold.',
        'dev_cta': 'Comparing {d} projects?', 'cta_p': 'Tell Keith your budget and area, and he will shortlist the right units.',
        'dev_idx_h1': 'New Launch Projects by Developer ({y})', 'dev_idx_p': 'Developers with more than one project on keithnah.com, each with all their projects on one page.',
        'stn_crumb': 'Near a station', 'stn_eb': 'Near {lines} · updated {y}', 'stn_h1': 'New Condos Near {s} ({y})',
        'stn_p': 'New launch projects whose published location details mention {s}. Walking times are as described by each project; check the route before you buy.',
        'stn_list': 'Projects near {s}', 'stn_other': 'Other stations', 'stn_cta': 'Want to live near the rail?',
        'stn_cta_p': 'Keith can shortlist units within walking distance of the line you use every day.',
        'stn_idx_h1': 'New Condos Near MRT, LRT & Monorail Stations ({y})', 'stn_idx_p': 'Stations named in the location details of two or more new launch projects.',
        'w_min': '{n}-minute walk to the station', 'w_m': 'About {n} m to the station', 'w_near': 'Near the station',
        'vs_crumb': 'Compare', 'vs_eb': 'Side by side · {a}', 'vs_h1': '{A} vs {B}: Which One Fits You?',
        'vs_p': 'Two new launch projects in {a}, with every published difference side by side.',
        'vs_key': 'Key differences', 'vs_same': 'Same in both', 'vs_full': 'Full comparison',
        'vs_note': '✓ = better on that point for most buyers. Prices are gross starting prices as published and may change; confirm the latest with Keith.',
        'vs_suit': 'Which one suits you?', 'vs_choose': 'Choose {x} if…', 'vs_more': 'More comparisons', 'vs_cta': 'Still deciding?',
        'vs_cta_p': 'Ask Keith which project and unit type suits your budget and plans.',
        'vs_idx_h1': 'Project Comparisons, Side by Side ({y})', 'vs_idx_p': 'Two similar new launch projects in the same area, every published difference side by side.',
        'r_price': 'you want the lower entry price', 'r_fh': 'you prefer freehold', 'r_units': 'you prefer a lower-density project with fewer units',
        'r_done': 'you want the earlier completion', 'r_mf': 'you want lower maintenance fees', 'r_none': 'you prefer its location or layouts; compare the floor plans',
        'd_price': '{x} starts about {d} lower ({p1} vs {p2}, gross).', 'd_fh': '{x} is freehold; {y} is leasehold.',
        'd_units': '{x} has fewer units ({u1} vs {u2}).', 'd_done': '{x} is expected to complete earlier ({c1} vs {c2}).',
        'd_mf': '{x} has the lower maintenance fee ({m1} vs {m2}).', 'd_none': 'The published details are very similar; the difference is mostly in location and layouts.',
        'row_price': 'Starting price', 'row_size': 'Unit sizes', 'row_rooms': 'Bedrooms', 'row_tenure': 'Tenure', 'row_units': 'Total units',
        'row_lifts': 'Lifts', 'row_upf': 'Units per floor', 'row_mf': 'Maintenance', 'row_done': 'Completion', 'row_status': 'Status',
        'row_dev': 'Developer', 'row_loc': 'Location',
        'b_devlink': 'All {n} {d} projects →', 'b_near': 'Nearest stations', 'b_cmp': 'Compare {x} with…',
        'b_dev_h': 'Browse by developer', 'b_dev_p': 'Every project from the same developer on one page.',
        'b_stn_h': 'Near a station', 'b_stn_p': 'New launches within reach of an MRT, LRT, Monorail, KTM or RTS station.',
        'b_vs_h': 'Popular head-to-head comparisons', 'b_vs_p': 'Two similar projects, every published difference side by side.',
        'b_area_stn': 'Stations in {a}', 'b_area_vs': 'Compare projects in {a}', 'b_all': 'See all →',
    },
    'zh-CN': {
        'home': '首页', 'projects': '项目', 'all': '全部', 'n_proj': '{n} 个项目', 'cta_wa': 'WhatsApp Keith', 'view': '查看项目 →',
        'st_projects': '个项目', 'st_states': '个州属', 'st_low': '最低起价', 'st_fh': '个永久地契项目', 'st_lines': '条路线',
        'dev_crumb': '发展商', 'dev_eb': '发展商 · {y} 更新', 'dev_h1': '{d} 新楼盘项目（{y}）',
        'dev_p': 'Keith Nah 目前列出的所有 {d} 项目，分布在 {places}：起价、地契和完工日期一目了然。点击项目查看平面图，或问 Keith 哪个最适合你的预算。',
        'dev_all': '{d} 全部项目', 'faq_dev': '{d} 常见问题',
        'dq1': '{y} 年有多少个 {d} 项目？', 'da1': 'Keith 目前在 {places} 列出 {n} 个 {d} 项目。',
        'dq2': '哪个 {d} 项目起价最低？', 'da2': '目前公布的最低起价约 {p}（总价），在 {name}。价格会随期数和单位变化，最新价格请问 Keith。',
        'dq3': '{d} 的项目是永久地契吗？', 'da3': '这里列出的 {n} 个 {d} 项目中，有 {f} 个是永久地契。',
        'dev_cta': '在比较 {d} 的项目？', 'cta_p': '告诉 Keith 你的预算和地区，他会帮你挑选合适的单位。',
        'dev_idx_h1': '按发展商看新楼盘（{y}）', 'dev_idx_p': '在 keithnah.com 有两个以上项目的发展商，每家的所有项目都整理在同一页。',
        'stn_crumb': '车站附近', 'stn_eb': '{lines} 附近 · {y} 更新', 'stn_h1': '{s} 附近的新楼盘（{y}）',
        'stn_p': '项目公布的位置资料中提到 {s} 的新楼盘。步行时间以各项目的说明为准，买房前请自己走一趟确认。',
        'stn_list': '{s} 附近的项目', 'stn_other': '其他车站', 'stn_cta': '想住在轨道交通旁？',
        'stn_cta_p': 'Keith 可以帮你挑选步行就能到你每天搭的路线的单位。',
        'stn_idx_h1': 'MRT、LRT 和单轨站附近的新楼盘（{y}）', 'stn_idx_p': '在两个以上新楼盘的位置资料中被提到的车站。',
        'w_min': '步行 {n} 分钟到车站', 'w_m': '距离车站约 {n} 米', 'w_near': '靠近车站',
        'vs_crumb': '比较', 'vs_eb': '并排比较 · {a}', 'vs_h1': '{A} vs {B}：哪个更适合你？',
        'vs_p': '{a} 的两个新楼盘，所有公布的差别并排列出。',
        'vs_key': '主要差别', 'vs_same': '两者相同', 'vs_full': '完整比较',
        'vs_note': '✓ = 对大多数买家来说在这一点较占优。价格为公布的总价起价，可能会变动，最新价格请向 Keith 确认。',
        'vs_suit': '哪个适合你？', 'vs_choose': '选 {x}，如果…', 'vs_more': '更多比较', 'vs_cta': '还在考虑？',
        'vs_cta_p': '问 Keith 哪个项目和房型最适合你的预算和计划。',
        'vs_idx_h1': '项目并排比较（{y}）', 'vs_idx_p': '同一地区、价位相近的两个新楼盘，所有公布的差别并排列出。',
        'r_price': '你想要较低的入场价', 'r_fh': '你偏好永久地契', 'r_units': '你喜欢单位较少、密度较低的项目',
        'r_done': '你想早点完工', 'r_mf': '你想要较低的管理费', 'r_none': '你更喜欢它的位置或房型，可以比较平面图',
        'd_price': '{x} 起价低约 {d}（{p1} 对 {p2}，总价）。', 'd_fh': '{x} 是永久地契；{y} 是租赁地契。',
        'd_units': '{x} 的单位较少（{u1} 对 {u2}）。', 'd_done': '{x} 预计较早完工（{c1} 对 {c2}）。',
        'd_mf': '{x} 的管理费较低（{m1} 对 {m2}）。', 'd_none': '两者公布的资料非常接近，差别主要在位置和房型。',
        'row_price': '起价', 'row_size': '面积', 'row_rooms': '房间', 'row_tenure': '地契', 'row_units': '总单位',
        'row_lifts': '电梯', 'row_upf': '每层单位', 'row_mf': '管理费', 'row_done': '完工', 'row_status': '状态',
        'row_dev': '发展商', 'row_loc': '位置',
        'b_devlink': '{d} 全部 {n} 个项目 →', 'b_near': '附近车站', 'b_cmp': '{x} 和这些项目比较',
        'b_dev_h': '按发展商浏览', 'b_dev_p': '同一发展商的所有项目，整理在同一页。',
        'b_stn_h': '车站附近', 'b_stn_p': '靠近 MRT、LRT、单轨、KTM 或 RTS 车站的新楼盘。',
        'b_vs_h': '热门项目对比', 'b_vs_p': '两个相近的项目，所有公布的差别并排列出。',
        'b_area_stn': '{a} 的车站', 'b_area_vs': '比较 {a} 的项目', 'b_all': '查看全部 →',
    },
    'ms': {
        'home': 'Utama', 'projects': 'Projek', 'all': 'Semua', 'n_proj': '{n} projek', 'cta_wa': 'WhatsApp Keith', 'view': 'Lihat projek →',
        'st_projects': 'projek', 'st_states': 'negeri', 'st_low': 'harga permulaan terendah', 'st_fh': 'projek pegangan bebas', 'st_lines': 'laluan rel',
        'dev_crumb': 'Pemaju', 'dev_eb': 'Pemaju · dikemas kini {y}', 'dev_h1': 'Projek Baharu {d} ({y})',
        'dev_p': 'Semua projek {d} yang disenaraikan oleh Keith Nah, di {places}: harga permulaan, pegangan dan tarikh siap di satu tempat. Buka projek untuk pelan lantai, atau tanya Keith mana yang sesuai dengan bajet anda.',
        'dev_all': 'Semua projek {d}', 'faq_dev': '{d}: soalan lazim',
        'dq1': 'Berapa banyak projek {d} pada {y}?', 'da1': 'Keith kini menyenaraikan {n} projek {d} di {places}.',
        'dq2': 'Projek {d} manakah yang harga permulaannya paling rendah?', 'da2': 'Harga permulaan terendah yang diterbitkan ialah kira-kira {p} (kasar), di {name}. Harga berubah mengikut fasa dan unit; tanya Keith untuk harga terkini.',
        'dq3': 'Adakah projek {d} berpegangan bebas?', 'da3': '{f} daripada {n} projek {d} di sini berpegangan bebas.',
        'dev_cta': 'Membandingkan projek {d}?', 'cta_p': 'Beritahu Keith bajet dan kawasan anda, dan dia akan menyenarai pendek unit yang sesuai.',
        'dev_idx_h1': 'Projek Baharu Mengikut Pemaju ({y})', 'dev_idx_p': 'Pemaju yang mempunyai lebih daripada satu projek di keithnah.com, setiap satu dengan semua projeknya dalam satu halaman.',
        'stn_crumb': 'Berhampiran stesen', 'stn_eb': 'Berhampiran {lines} · dikemas kini {y}', 'stn_h1': 'Kondo Baharu Berhampiran {s} ({y})',
        'stn_p': 'Projek baharu yang butiran lokasinya menyebut {s}. Masa berjalan kaki adalah seperti yang dinyatakan oleh setiap projek; semak laluannya sebelum membeli.',
        'stn_list': 'Projek berhampiran {s}', 'stn_other': 'Stesen lain', 'stn_cta': 'Mahu tinggal berhampiran rel?',
        'stn_cta_p': 'Keith boleh menyenarai pendek unit yang dekat dengan laluan yang anda guna setiap hari.',
        'stn_idx_h1': 'Kondo Baharu Berhampiran Stesen MRT, LRT & Monorel ({y})', 'stn_idx_p': 'Stesen yang disebut dalam butiran lokasi dua atau lebih projek baharu.',
        'w_min': '{n} minit berjalan kaki ke stesen', 'w_m': 'Kira-kira {n} m ke stesen', 'w_near': 'Berhampiran stesen',
        'vs_crumb': 'Bandingkan', 'vs_eb': 'Sebelah-menyebelah · {a}', 'vs_h1': '{A} vs {B}: Mana Lebih Sesuai?',
        'vs_p': 'Dua projek baharu di {a}, dengan setiap perbezaan yang diterbitkan sebelah-menyebelah.',
        'vs_key': 'Perbezaan utama', 'vs_same': 'Sama untuk kedua-dua', 'vs_full': 'Perbandingan penuh',
        'vs_note': '✓ = lebih baik pada perkara itu bagi kebanyakan pembeli. Harga ialah harga permulaan kasar yang diterbitkan dan boleh berubah; sahkan dengan Keith.',
        'vs_suit': 'Mana yang sesuai untuk anda?', 'vs_choose': 'Pilih {x} jika…', 'vs_more': 'Lagi perbandingan', 'vs_cta': 'Masih membuat keputusan?',
        'vs_cta_p': 'Tanya Keith projek dan jenis unit mana yang sesuai dengan bajet dan rancangan anda.',
        'vs_idx_h1': 'Perbandingan Projek Sebelah-Menyebelah ({y})', 'vs_idx_p': 'Dua projek baharu yang serupa di kawasan yang sama, setiap perbezaan sebelah-menyebelah.',
        'r_price': 'anda mahu harga masuk yang lebih rendah', 'r_fh': 'anda lebih suka pegangan bebas', 'r_units': 'anda lebih suka projek berkepadatan rendah dengan unit lebih sedikit',
        'r_done': 'anda mahu siap lebih awal', 'r_mf': 'anda mahu yuran penyelenggaraan lebih rendah', 'r_none': 'anda lebih suka lokasi atau susun aturnya; bandingkan pelan lantai',
        'd_price': '{x} bermula kira-kira {d} lebih rendah ({p1} berbanding {p2}, kasar).', 'd_fh': '{x} berpegangan bebas; {y} pajakan.',
        'd_units': '{x} mempunyai unit lebih sedikit ({u1} berbanding {u2}).', 'd_done': '{x} dijangka siap lebih awal ({c1} berbanding {c2}).',
        'd_mf': '{x} mempunyai yuran penyelenggaraan lebih rendah ({m1} berbanding {m2}).', 'd_none': 'Butiran yang diterbitkan sangat serupa; perbezaannya kebanyakannya pada lokasi dan susun atur.',
        'row_price': 'Harga permulaan', 'row_size': 'Saiz unit', 'row_rooms': 'Bilik tidur', 'row_tenure': 'Pegangan', 'row_units': 'Jumlah unit',
        'row_lifts': 'Lif', 'row_upf': 'Unit setiap tingkat', 'row_mf': 'Penyelenggaraan', 'row_done': 'Siap', 'row_status': 'Status',
        'row_dev': 'Pemaju', 'row_loc': 'Lokasi',
        'b_devlink': 'Semua {n} projek {d} →', 'b_near': 'Stesen terdekat', 'b_cmp': 'Bandingkan {x} dengan…',
        'b_dev_h': 'Lihat mengikut pemaju', 'b_dev_p': 'Semua projek daripada pemaju yang sama dalam satu halaman.',
        'b_stn_h': 'Berhampiran stesen', 'b_stn_p': 'Projek baharu berhampiran stesen MRT, LRT, Monorel, KTM atau RTS.',
        'b_vs_h': 'Perbandingan popular', 'b_vs_p': 'Dua projek yang serupa, setiap perbezaan sebelah-menyebelah.',
        'b_area_stn': 'Stesen di {a}', 'b_area_vs': 'Bandingkan projek di {a}', 'b_all': 'Lihat semua →',
    },
    'ja': {
        'home': 'ホーム', 'projects': '物件', 'all': 'すべて', 'n_proj': '{n} 件', 'cta_wa': 'WhatsApp Keith', 'view': '物件を見る →',
        'st_projects': '件', 'st_states': '州', 'st_low': '最低価格', 'st_fh': 'フリーホールド物件', 'st_lines': '路線',
        'dev_crumb': 'デベロッパー', 'dev_eb': 'デベロッパー · {y}年更新', 'dev_h1': '{d} の新築プロジェクト（{y}年）',
        'dev_p': 'Keith Nah が掲載している {d} の全プロジェクト（{places}）。価格、権利形態、完成時期をまとめて確認できます。物件を開いて間取りを見るか、予算に合う物件を Keith にご相談ください。',
        'dev_all': '{d} の全プロジェクト', 'faq_dev': '{d}：よくある質問',
        'dq1': '{y}年の {d} のプロジェクトはいくつ？', 'da1': 'Keith は現在、{places} で {d} のプロジェクトを {n} 件掲載しています。',
        'dq2': '最も価格が低い {d} のプロジェクトは？', 'da2': '公表されている最低価格は約 {p}（総額）で、{name} です。価格は期や住戸で変わるため、最新情報は Keith にご確認ください。',
        'dq3': '{d} のプロジェクトはフリーホールド？', 'da3': '掲載中の {d} のプロジェクト {n} 件のうち、{f} 件がフリーホールドです。',
        'dev_cta': '{d} の物件を比較中ですか？', 'cta_p': 'ご予算とエリアを Keith に伝えていただければ、合う住戸を選んでお送りします。',
        'dev_idx_h1': 'デベロッパー別の新築プロジェクト（{y}年）', 'dev_idx_p': 'keithnah.com に複数のプロジェクトがあるデベロッパー。各社の全物件を1ページにまとめています。',
        'stn_crumb': '駅の近く', 'stn_eb': '{lines} の近く · {y}年更新', 'stn_h1': '{s} 近くの新築コンド（{y}年）',
        'stn_p': '公表された立地情報に {s} が記載されている新築プロジェクトです。徒歩時間は各物件の説明によるもので、購入前にご自身でご確認ください。',
        'stn_list': '{s} 近くの物件', 'stn_other': 'ほかの駅', 'stn_cta': '駅の近くに住みたいですか？',
        'stn_cta_p': '毎日使う路線から歩ける住戸を Keith がお選びします。',
        'stn_idx_h1': 'MRT・LRT・モノレール駅近くの新築コンド（{y}年）', 'stn_idx_p': '2件以上の新築プロジェクトの立地情報に記載されている駅です。',
        'w_min': '駅まで徒歩 {n} 分', 'w_m': '駅まで約 {n} m', 'w_near': '駅の近く',
        'vs_crumb': '比較', 'vs_eb': '並べて比較 · {a}', 'vs_h1': '{A} vs {B}：あなたに合うのはどっち？',
        'vs_p': '{a} の2つの新築プロジェクトを、公表されている違いすべてを並べて比較します。',
        'vs_key': '主な違い', 'vs_same': '共通点', 'vs_full': '全項目の比較',
        'vs_note': '✓ = 多くの購入者にとってその点で有利。価格は公表された総額の最低価格で、変わることがあります。最新情報は Keith にご確認ください。',
        'vs_suit': 'どちらが合う？', 'vs_choose': '{x} がおすすめの人', 'vs_more': 'ほかの比較', 'vs_cta': 'まだ迷っていますか？',
        'vs_cta_p': 'ご予算と計画に合う物件と間取りを Keith にご相談ください。',
        'vs_idx_h1': 'プロジェクト比較（{y}年）', 'vs_idx_p': '同じエリアの似た新築プロジェクト2件を、公表されている違いすべてで比較します。',
        'r_price': '入りやすい価格を重視する', 'r_fh': 'フリーホールドを希望する', 'r_units': '戸数が少なく密度の低い物件を好む',
        'r_done': '早い完成を希望する', 'r_mf': '管理費を抑えたい', 'r_none': '立地や間取りが好み（間取り図を比べてください）',
        'd_price': '{x} の方が約 {d} 安く始まります（{p1} 対 {p2}、総額）。', 'd_fh': '{x} はフリーホールド、{y} はリースホールドです。',
        'd_units': '{x} の方が戸数が少ない（{u1} 対 {u2}）。', 'd_done': '{x} の方が完成予定が早い（{c1} 対 {c2}）。',
        'd_mf': '{x} の方が管理費が低い（{m1} 対 {m2}）。', 'd_none': '公表されている内容はよく似ており、違いは主に立地と間取りです。',
        'row_price': '最低価格', 'row_size': '広さ', 'row_rooms': '寝室', 'row_tenure': '権利形態', 'row_units': '総戸数',
        'row_lifts': 'エレベーター', 'row_upf': '1フロアの戸数', 'row_mf': '管理費', 'row_done': '完成', 'row_status': '状況',
        'row_dev': 'デベロッパー', 'row_loc': '所在地',
        'b_devlink': '{d} の全 {n} 件を見る →', 'b_near': '最寄り駅', 'b_cmp': '{x} とほかの物件を比較',
        'b_dev_h': 'デベロッパー別に見る', 'b_dev_p': '同じデベロッパーの物件を1ページにまとめています。',
        'b_stn_h': '駅の近く', 'b_stn_p': 'MRT・LRT・モノレール・KTM・RTS 駅の近くの新築物件。',
        'b_vs_h': '人気の比較', 'b_vs_p': '似た2物件の違いをすべて並べて比較。',
        'b_area_stn': '{a} の駅', 'b_area_vs': '{a} の物件を比較', 'b_all': 'すべて見る →',
    },
    'ko': {
        'home': '홈', 'projects': '프로젝트', 'all': '전체', 'n_proj': '{n}개 프로젝트', 'cta_wa': 'WhatsApp Keith', 'view': '프로젝트 보기 →',
        'st_projects': '개 프로젝트', 'st_states': '개 주', 'st_low': '최저 시작가', 'st_fh': '개 자유보유 프로젝트', 'st_lines': '개 노선',
        'dev_crumb': '개발사', 'dev_eb': '개발사 · {y} 업데이트', 'dev_h1': '{d} 신규 분양 프로젝트 ({y})',
        'dev_p': 'Keith Nah가 소개하는 {d}의 모든 프로젝트({places}). 시작가, 소유 형태, 완공 시기를 한곳에서 확인하세요. 프로젝트를 눌러 평면도를 보거나 예산에 맞는 곳을 Keith에게 문의하세요.',
        'dev_all': '{d} 전체 프로젝트', 'faq_dev': '{d}: 자주 묻는 질문',
        'dq1': '{y}년 {d} 프로젝트는 몇 개인가요?', 'da1': 'Keith는 현재 {places}에서 {d} 프로젝트 {n}개를 소개하고 있습니다.',
        'dq2': '시작가가 가장 낮은 {d} 프로젝트는?', 'da2': '공개된 최저 시작가는 약 {p}(총액)이며 {name}입니다. 가격은 단계와 세대에 따라 달라지니 최신 가격은 Keith에게 문의하세요.',
        'dq3': '{d} 프로젝트는 자유보유인가요?', 'da3': '여기 소개된 {d} 프로젝트 {n}개 중 {f}개가 자유보유입니다.',
        'dev_cta': '{d} 프로젝트를 비교 중이신가요?', 'cta_p': '예산과 지역을 Keith에게 알려주시면 맞는 세대를 골라 드립니다.',
        'dev_idx_h1': '개발사별 신규 분양 프로젝트 ({y})', 'dev_idx_p': 'keithnah.com에 프로젝트가 2개 이상인 개발사로, 각 개발사의 모든 프로젝트를 한 페이지에 모았습니다.',
        'stn_crumb': '역 근처', 'stn_eb': '{lines} 근처 · {y} 업데이트', 'stn_h1': '{s} 근처 신규 콘도 ({y})',
        'stn_p': '공개된 위치 정보에 {s}가 언급된 신규 분양 프로젝트입니다. 도보 시간은 각 프로젝트의 설명 기준이니 구매 전 직접 확인하세요.',
        'stn_list': '{s} 근처 프로젝트', 'stn_other': '다른 역', 'stn_cta': '역세권에 살고 싶으신가요?',
        'stn_cta_p': '매일 이용하는 노선에서 걸어갈 수 있는 세대를 Keith가 골라 드립니다.',
        'stn_idx_h1': 'MRT·LRT·모노레일 역 근처 신규 콘도 ({y})', 'stn_idx_p': '2개 이상의 신규 분양 프로젝트 위치 정보에 언급된 역입니다.',
        'w_min': '역까지 도보 {n}분', 'w_m': '역까지 약 {n}m', 'w_near': '역 근처',
        'vs_crumb': '비교', 'vs_eb': '나란히 비교 · {a}', 'vs_h1': '{A} vs {B}: 어느 쪽이 맞을까?',
        'vs_p': '{a}의 두 신규 분양 프로젝트를 공개된 모든 차이와 함께 나란히 비교합니다.',
        'vs_key': '주요 차이점', 'vs_same': '공통점', 'vs_full': '전체 비교',
        'vs_note': '✓ = 대부분의 구매자에게 그 항목에서 유리. 가격은 공개된 총액 시작가이며 바뀔 수 있으니 Keith에게 확인하세요.',
        'vs_suit': '어느 쪽이 맞을까요?', 'vs_choose': '이런 분께 {x}', 'vs_more': '더 많은 비교', 'vs_cta': '아직 고민 중이신가요?',
        'vs_cta_p': '예산과 계획에 맞는 프로젝트와 세대 유형을 Keith에게 문의하세요.',
        'vs_idx_h1': '프로젝트 나란히 비교 ({y})', 'vs_idx_p': '같은 지역의 비슷한 신규 분양 프로젝트 두 곳을 공개된 모든 차이로 비교합니다.',
        'r_price': '더 낮은 진입 가격을 원하는 분', 'r_fh': '자유보유를 선호하는 분', 'r_units': '세대 수가 적은 저밀도 단지를 선호하는 분',
        'r_done': '더 빠른 완공을 원하는 분', 'r_mf': '관리비를 낮추고 싶은 분', 'r_none': '위치나 평면이 마음에 드는 분 (평면도를 비교해 보세요)',
        'd_price': '{x}의 시작가가 약 {d} 낮습니다 ({p1} vs {p2}, 총액).', 'd_fh': '{x}는 자유보유, {y}는 임차보유입니다.',
        'd_units': '{x}의 세대 수가 더 적습니다 ({u1} vs {u2}).', 'd_done': '{x}가 더 일찍 완공될 예정입니다 ({c1} vs {c2}).',
        'd_mf': '{x}의 관리비가 더 낮습니다 ({m1} vs {m2}).', 'd_none': '공개된 내용은 매우 비슷하며, 차이는 주로 위치와 평면에 있습니다.',
        'row_price': '시작가', 'row_size': '면적', 'row_rooms': '침실', 'row_tenure': '소유 형태', 'row_units': '총 세대수',
        'row_lifts': '엘리베이터', 'row_upf': '층당 세대수', 'row_mf': '관리비', 'row_done': '완공', 'row_status': '상태',
        'row_dev': '개발사', 'row_loc': '위치',
        'b_devlink': '{d} 프로젝트 {n}개 모두 보기 →', 'b_near': '가까운 역', 'b_cmp': '{x}와 비교하기',
        'b_dev_h': '개발사별 보기', 'b_dev_p': '같은 개발사의 모든 프로젝트를 한 페이지에.',
        'b_stn_h': '역 근처', 'b_stn_p': 'MRT·LRT·모노레일·KTM·RTS 역 근처의 신규 분양.',
        'b_vs_h': '인기 비교', 'b_vs_p': '비슷한 두 프로젝트의 모든 차이를 나란히.',
        'b_area_stn': '{a}의 역', 'b_area_vs': '{a} 프로젝트 비교', 'b_all': '전체 보기 →',
    },
}
VALS = {
    'en': {'v_Freehold': 'Freehold', 'v_Leasehold': 'Leasehold', 'v_Under Construction': 'Under Construction', 'v_Coming Soon': 'Coming Soon',
           'v_Completed': 'Completed', 'v_New Launch': 'New Launch', 'v_Price on Request': 'Price on Request', 'p_from': 'From {p} (Gross)', 'p_gross': '{p} (Gross)'},
    'zh-CN': {'v_Freehold': '永久地契', 'v_Leasehold': '租赁地契', 'v_Under Construction': '建设中', 'v_Coming Soon': '即将推出',
              'v_Completed': '已完工', 'v_New Launch': '新推出', 'v_Price on Request': '价格请询问', 'p_from': '起价 {p}（总价）', 'p_gross': '{p}（总价）'},
    'ms': {'v_Freehold': 'Pegangan bebas', 'v_Leasehold': 'Pajakan', 'v_Under Construction': 'Dalam pembinaan', 'v_Coming Soon': 'Akan datang',
           'v_Completed': 'Siap', 'v_New Launch': 'Pelancaran baharu', 'v_Price on Request': 'Harga atas permintaan', 'p_from': 'Dari {p} (kasar)', 'p_gross': '{p} (kasar)'},
    'ja': {'v_Freehold': 'フリーホールド', 'v_Leasehold': 'リースホールド', 'v_Under Construction': '建設中', 'v_Coming Soon': '近日公開',
           'v_Completed': '完成済み', 'v_New Launch': '新規販売', 'v_Price on Request': '価格はお問い合わせ', 'p_from': '{p} から（総額）', 'p_gross': '{p}（総額）'},
    'ko': {'v_Freehold': '자유보유', 'v_Leasehold': '임차보유', 'v_Under Construction': '공사 중', 'v_Coming Soon': '출시 예정',
           'v_Completed': '완공', 'v_New Launch': '신규 분양', 'v_Price on Request': '가격 문의', 'p_from': '{p}부터 (총액)', 'p_gross': '{p} (총액)'},
}
for _l, _v in VALS.items():
    T[_l].update(_v)


def val(s, tag='span', cls=''):
    """A project value (tenure, status, price) in the visitor's language when it is one we know."""
    import html as _h
    s = (s or '').strip()
    base = s.split(' (')[0] if s.startswith(('Freehold', 'Leasehold')) else s
    if 'v_' + base in T['en']:
        return tx('v_' + base, tag=tag, cls=cls)
    m = re.match(r'^From (RM[\d,.]+(?: mil)?) \(Gross\)$', s)
    if m:
        return tx('p_from', tag=tag, cls=cls, p=m.group(1))
    m = re.match(r'^(RM[\d,.]+ ?[–-] ?RM[\d,.]+|RM[\d,.]+) \(Gross\)$', s)
    if m:
        return tx('p_gross', tag=tag, cls=cls, p=m.group(1))
    return '<%s%s>%s</%s>' % (tag, (' class="%s"' % cls) if cls else '', _h.escape(s, quote=False), tag)


try:
    import opencc
    _cc = opencc.OpenCC('s2tw').convert
    T['zh-TW'] = {k: _cc(v) for k, v in T['zh-CN'].items()}
except Exception:
    T['zh-TW'] = dict(T['zh-CN'])

# Swaps every [data-hb] text for the visitor's language; data-hv holds the values for {x}.
JS = ('<script>(function(){var T=%s;function lg(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}return T[l]?l:"en";}'
      'function go(){var l=lg();document.querySelectorAll("[data-hb]").forEach(function(e){var s=T[l][e.getAttribute("data-hb")]||T.en[e.getAttribute("data-hb")];if(!s)return;'
      'var v={};try{v=JSON.parse(e.getAttribute("data-hv")||"{}")}catch(z){}s=s.replace(/\\{(\\w+)\\}/g,function(m,k){return v[k]!=null?v[k]:m;});'
      'if(e.hasAttribute("data-hbh"))e.innerHTML=s;else e.textContent=s;});}'
      'go();document.addEventListener("DOMContentLoaded",function(){var s=window.knSetLang;if(typeof s==="function"&&!s.__hb){var w=function(){var r=s.apply(this,arguments);go();return r;};w.__hb=1;window.knSetLang=w;}go();});})();</script>')


def js():
    return JS % json.dumps(T, ensure_ascii=False).replace('</', '<\\/')


def tx(key, tag='span', cls='', attrs='', **v):
    """An element whose text is T[lang][key] with v filled in; English is written into the HTML."""
    import html as _h
    s = T['en'][key]
    for k, val in v.items():
        s = s.replace('{%s}' % k, str(val))
    extra = attrs
    attrs = ' data-hb="%s"' % key
    if v:
        attrs += " data-hv='%s'" % _h.escape(json.dumps({k: str(val) for k, val in v.items()}, ensure_ascii=False), quote=True).replace("'", '&#x27;')
    if cls:
        attrs += ' class="%s"' % cls
    attrs += (' ' + extra) if extra else ''
    return '<%s%s>%s</%s>' % (tag, attrs, _h.escape(s, quote=False), tag)


CSS = ('.hb-chips{display:flex;flex-wrap:wrap;gap:10px}.hb-chip{display:inline-flex;align-items:center;gap:8px;background:#fff;border:1px solid rgba(21,20,43,.12);'
       'border-radius:100px;padding:9px 15px;font:700 13.5px Inter,sans-serif;color:#15142b;transition:all .2s}.hb-chip:hover{border-color:#5E60CE;color:#5E60CE}'
       '.hb-chip b{color:#5E60CE;font-weight:700}.hb-sub{font:800 11px Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#6b6a85;margin:18px 0 10px}'
       '.hb-vs{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}.hb-vs a{display:block;background:#fff;border:1px solid rgba(21,20,43,.1);'
       'border-radius:16px;padding:15px 17px;font:700 15px Inter,sans-serif;color:#15142b;transition:all .2s}.hb-vs a:hover{border-color:#5E60CE;box-shadow:0 10px 24px rgba(29,27,79,.08)}'
       '.hb-vs a small{display:block;color:#5E60CE;font-size:11px;letter-spacing:.1em;text-transform:uppercase;margin-bottom:4px}'
       '.hb-wrap{max-width:1240px;margin:0 auto;padding:34px 5vw}.hb-wrap h2{font:700 clamp(24px,3vw,30px) "Playfair Display",Georgia,serif;margin-bottom:6px;color:#111}'
       '.hb-wrap p.hb-p{color:#5f5e74;margin-bottom:16px;font:500 14.5px Inter,sans-serif}.hb-devlink{margin-left:10px;color:#5E60CE;font-weight:700;white-space:nowrap}')
