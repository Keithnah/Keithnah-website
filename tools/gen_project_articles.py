"""Two articles for every project, written from the project's own data (tools/project_articles_auto.json).

Article 1: "<Project>: is it worth buying?" (what it is, location, layouts and prices, who it suits,
what to compare). Article 2: "<Project> layouts: which one fits you?" or, for a project with one
layout, "Living at <Project>: a neighbourhood guide".

Keith's rules: facts only from the project data; plain, neutral tone; downsides are not
exaggerated; no legal topics; no rental returns, yields or investment figures; none of the site's
banned words; no developer for the restricted projects. Projects with hand-written articles in
tools/project_articles.json are skipped. Texts use the site's project translations
(i18n-projects-<lang>.js); a text with no translation stays in English in that language.

Run by tools/build_all.py before build_project_articles.py, so new projects get their articles
automatically. The date each article first appeared is kept in tools/project_articles_dates.json.

    python3 tools/externalize.py in
    python3 tools/gen_project_articles.py
"""
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
sys.path.insert(0, HERE)
import build_area_pages as A  # noqa: E402
import i18n_pages as I18N  # noqa: E402

OUT = os.path.join(HERE, 'project_articles_auto.json')
DATES = os.path.join(HERE, 'project_articles_dates.json')
HAND = os.path.join(HERE, 'project_articles.json')
LG = ['zh-CN', 'ms', 'ja', 'ko']
ALL = ['en'] + LG
RESTRICTED = ['Aricia', 'Enlace Suites II', 'Ayanna', 'Est8', 'Lunar', 'Tangen', 'Aurum', 'Anya', 'Avantro', 'Luminar']
NO = re.compile(r'rebate|\bnett\b|package|commission|gallery|airbnb|klcc|guaranteed|\bgrr\b|short[- ]term|holiday let|yield|\breturns?\b|\broi\b|'
                r'rental income|appreciation|capital gain|profit|licen[cs]e|permit|\bspa\b|lawyer|legal|show unit|showroom', re.I)


def _load(lang):
    s = open('i18n-projects-%s.js' % lang, encoding='utf-8').read()
    key = 'window.KN_TR["%s"]=' % lang
    return json.JSONDecoder().raw_decode(s[s.index(key) + len(key):])[0]


KN = {l: _load(l) for l in LG}


def tr(en):
    """English project text -> {lang: text} with the site's translations (English where none)."""
    out = {'en': en}
    for l in LG:
        out[l] = KN[l].get(en) or I18N.data(en, l) or en
    return out


def T(en, zh, ms, ja, ko, **kw):
    """A sentence frame in the five written languages, filled with {name}-style values
    (each value either a plain string or a {lang: text} dict)."""
    frames = dict(zip(ALL, [en, zh, ms, ja, ko]))
    out = {}
    for l in ALL:
        vals = {k: (v.get(l, v['en']) if isinstance(v, dict) else v) for k, v in kw.items()}
        out[l] = frames[l].format(**vals)
    return out


def join(parts):
    """Join several {lang: text} pieces into one paragraph."""
    sep = {'en': ' ', 'zh-CN': '', 'ms': ' ', 'ja': '', 'ko': ' '}
    return {l: sep[l].join(p[l] for p in parts if p and p.get(l)) for l in ALL}


def lst(items):
    """A list of {lang: text} items joined with commas."""
    sep = {'en': ', ', 'zh-CN': '、', 'ms': ', ', 'ja': '、', 'ko': ', '}
    return {l: sep[l].join(x[l] for x in items) for l in ALL}


def lname(t):
    return re.sub(r'\s*\((?:show unit|showroom)\)', '', t, flags=re.I)


def ok(s):
    return bool(s) and not NO.search(s)


def sqft(s):
    m = re.search(r'([\d,]+)\s*(?:sq\s*ft|sqft|sf)', s or '', re.I)
    return int(m.group(1).replace(',', '')) if m else None


def maint_psf(ex):
    m = re.search(r'RM\s*([\d.]+)\s*psf', ex.get('Maintenance Fee', '') or '', re.I)
    return float(m.group(1)) if m else None


def article_one(i, p, date):
    name, (state, area) = p['name'], A.PLACES[i]
    ex = p.get('details_extra') or {}
    restricted = any(r.lower() in name.lower() for r in RESTRICTED)
    typ = tr(A.TYPE.get(i, 'Residential'))
    typ['en'] = typ['en'].lower()
    secs = []
    # 1. what it is
    facts = []
    if ex.get('Developer') and not restricted:
        facts.append(T('It is developed by {d}.', '发展商是 {d}。', 'Ia dibangunkan oleh {d}.', 'デベロッパーは {d} です。', '개발사는 {d}입니다.', d=re.sub(r'\s*\(.*?\)\s*$', '', ex['Developer'])))
    if ok(p.get('tenure')):
        facts.append(T('Tenure: {t}.', '地契：{t}。', 'Pegangan: {t}.', '土地権利：{t}。', '소유 형태: {t}.', t=tr(p['tenure'])))
    if ok(p.get('completion')):
        facts.append(T('Completion: {c}.', '完工：{c}。', 'Siap: {c}.', '完成：{c}。', '완공: {c}.', c=tr(p['completion'])))
    if ok(ex.get('Total Units')):
        facts.append(T('Units: {u}.', '单位：{u}。', 'Unit: {u}.', '戸数：{u}。', '세대: {u}.', u=tr(ex['Total Units'])))
    if ok(ex.get('Land Area')):
        facts.append(T('Land area: {a}.', '占地：{a}。', 'Keluasan tanah: {a}.', '敷地面積：{a}。', '부지 면적: {a}.', a=tr(ex['Land Area'])))
    secs.append({'h2': T('What {n} is', '{n} 是什么项目', 'Apa itu {n}', '{n} とは', '{n}는 어떤 프로젝트인가', n=name),
                 'paragraphs': [x for x in [tr(p['overview']) if ok(p['overview']) else None, join(facts) if facts else None] if x]})
    # 2. location
    near = [tr(a) for a in (p.get('amenities') or []) if ok(a)][:5]
    paras = [tr(p['loc_text'])] if ok(p.get('loc_text')) else []
    if near:
        paras.append(T('Places nearby include {l}.', '附近有：{l}。', 'Tempat berdekatan termasuk {l}.', '周辺には {l} があります。', '주변에는 {l} 등이 있습니다.', l=lst(near)))
    secs.append({'h2': T('Location and getting around', '地点和交通', 'Lokasi dan pengangkutan', '立地とアクセス', '위치와 교통'), 'paragraphs': paras})
    # 3. layouts and prices
    lays = p.get('layouts') or []
    k = len(lays)
    p1 = [T('{n} has {k} layouts, {s}, with {r}.' if k > 1 else '{n} has one layout, {s}, with {r}.',
            '{n} 有 {k} 种户型，面积 {s}，{r}。' if k > 1 else '{n} 只有一种户型，面积 {s}，{r}。',
            '{n} mempunyai {k} susun atur, {s}, dengan {r}.' if k > 1 else '{n} mempunyai satu susun atur, {s}, dengan {r}.',
            '{n} の間取りは {k} タイプ、広さは {s}、{r}。' if k > 1 else '{n} の間取りは1タイプ、広さは {s}、{r}。',
            '{n}에는 {k}가지 타입이 있으며 면적은 {s}, {r}입니다.' if k > 1 else '{n}는 단일 타입으로 면적은 {s}, {r}입니다.',
            n=name, k=k, s=tr(p['size']), r=tr(p['rooms']))]
    if ok(p.get('price')):
        p1.append(T('Prices: {p}.', '价格：{p}。', 'Harga: {p}.', '価格：{p}。', '가격: {p}.', p=tr(p['price'])))
    if ok(ex.get('Price per Sqft')):
        p1.append(T('Price per sqft: {x}.', '每平方尺价格：{x}。', 'Harga sekaki persegi: {x}.', '平方フィート単価：{x}。', '평방피트당 가격: {x}.', x=tr(ex['Price per Sqft'])))
    paras = [join(p1)]
    if k > 1:
        names = [tr('%s (%s)' % (lname(l['type']), l['size'])) if l.get('size') else tr(lname(l['type'])) for l in lays[:10]]
        paras.append(T('The layouts: {l}.', '户型包括：{l}。', 'Susun atur: {l}.', '間取り：{l}。', '타입: {l}.', l=lst(names)))
    secs.append({'h2': T('Layouts and prices', '户型和价格', 'Susun atur dan harga', '間取りと価格', '타입과 가격'), 'paragraphs': paras})
    # 4. who it suits
    fits = [f for f in (p.get('buyer_fit') or []) if ok(f['title']) and ok(f['desc'])][:3]
    if fits:
        secs.append({'h2': T('Who it suits', '适合哪些买家', 'Siapa yang sesuai', '向いている購入者', '어떤 구매자에게 맞을까'),
                     'paragraphs': [T('{t}: {d}', '{t}：{d}', '{t}: {d}', '{t}：{d}', '{t}: {d}', t=tr(f['title']), d=tr(f['desc'])) for f in fits]})
    # 5. what to compare
    cmp_ = []
    if ok(p.get('tenure')):
        cmp_.append(T('The tenure is {t}, so compare it with other projects you are looking at.', '地契是 {t}，可以和你在看的其他项目比较。',
                      'Pegangannya {t}, jadi bandingkan dengan projek lain yang anda lihat.', '土地権利は {t} なので、検討中の他のプロジェクトと比べてみてください。',
                      '소유 형태는 {t}이니 보고 있는 다른 프로젝트와 비교해 보세요.', t=tr(p['tenure'])))
    if ok(p.get('completion')):
        cmp_.append(T('Completion is {c}, so match it with when you need the home.', '完工期是 {c}，看看是否配合你需要入住的时间。',
                      'Siap {c}, jadi padankan dengan bila anda memerlukan rumah ini.', '完成は {c} なので、入居したい時期と合うか確認しましょう。',
                      '완공은 {c}이니 입주가 필요한 시기와 맞는지 확인하세요.', c=tr(p['completion'])))
    if ok(ex.get('Maintenance Fee')):
        cmp_.append(T('The maintenance fee is {m}.', '管理费是 {m}。', 'Yuran penyelenggaraan ialah {m}.', '管理費は {m} です。', '관리비는 {m}입니다.', m=tr(ex['Maintenance Fee'])))
    if ok(ex.get('Car Parks')):
        cmp_.append(T('Car parks: {c}.', '车位：{c}。', 'Tempat letak kereta: {c}.', '駐車場：{c}。', '주차: {c}.', c=tr(ex['Car Parks'])))
    paras = [join(cmp_)] if cmp_ else []
    myr = A.price_rm(p['price'])
    mins = {'Kuala Lumpur': (1000000, 'RM1 million', 'RM100 万', 'RM1 juta', '100万リンギット', '100만 링깃'), 'Selangor': (2000000, 'RM2 million', 'RM200 万', 'RM2 juta', '200万リンギット', '200만 링깃')}
    if state in mins and myr:
        mn = mins[state]
        if myr >= mn[0]:
            paras.append(T('Foreign buyers: the minimum price in {s} is {m}, and prices here start above it.', '外国买家：{s} 的最低购买价格是 {m}，这里的起价已经超过。',
                           'Pembeli asing: harga minimum di {s} ialah {m}, dan harga di sini bermula melebihinya.', '外国人購入者：{s} の最低価格は {m} で、ここの開始価格はそれを上回っています。',
                           '외국인 구매자: {s}의 최저 가격은 {m}이며, 이곳의 시작 가격은 이를 넘습니다.', s=state, m=dict(zip(ALL, mn[1:]))))
        else:
            paras.append(T('Foreign buyers: the minimum price in {s} is {m}. The entry units are below it, so check which units meet it before you book.',
                           '外国买家：{s} 的最低购买价格是 {m}。入门单位低于这个价格，下订前要先确认哪些单位达到门槛。',
                           'Pembeli asing: harga minimum di {s} ialah {m}. Unit permulaan di bawah paras ini, jadi semak unit yang mencapainya sebelum menempah.',
                           '外国人購入者：{s} の最低価格は {m} です。入門住戸はこれを下回るため、予約前に条件を満たす住戸を確認してください。',
                           '외국인 구매자: {s}의 최저 가격은 {m}입니다. 기본 세대는 이보다 낮으니 예약 전에 충족하는 세대를 확인하세요.', s=state, m=dict(zip(ALL, mn[1:]))))
    if paras:
        secs.append({'h2': T('What to compare before you decide', '决定前可以比较的地方', 'Apa yang perlu dibandingkan', '決める前に比較したい点', '결정 전에 비교할 점'), 'paragraphs': paras})
    stats = [{'value': re.sub(r'^From\s*', '', re.sub(r'\s*\(.*?\)', '', p['price'])), 'label': T('starting price', '起价', 'harga permulaan', '開始価格', '시작 가격')}] if ok(p.get('price')) else []
    stats.append({'value': p['size'], 'label': T('built-up size', '面积', 'keluasan binaan', '専有面積', '전용 면적')})
    stats.append({'value': str(k), 'label': T('layouts' if k > 1 else 'layout', '种户型', 'susun atur', '間取りタイプ', '타입')})
    return {
        'slug': '%s-is-it-worth-buying' % A.SLUG[i], 'project': A.SLUG[i], 'date': date, 'auto': True,
        'cat': T('Project Review', '项目分析', 'Ulasan Projek', 'プロジェクト分析', '프로젝트 분석'),
        'title': T('{n}: Is It Worth Buying? A Plain Guide', '{n} 值得买吗？项目简单分析', '{n}: Berbaloi Dibeli? Panduan Ringkas', '{n} は買い？わかりやすい物件ガイド', '{n}, 살 만할까? 쉬운 프로젝트 가이드', n=name),
        'intro': T('{n} is a {t} project in {a}, {s}. This guide covers what you get, the location, the layouts and prices, who it suits and what to compare before you decide.',
                   '{n} 是位于 {s} {a} 的{t}项目。这篇整理了项目内容、地点、户型和价格、适合哪些买家，以及决定前可以比较的地方。',
                   '{n} ialah projek {t} di {a}, {s}. Panduan ini merangkumi apa yang anda dapat, lokasi, susun atur dan harga, siapa yang sesuai dan apa yang perlu dibandingkan.',
                   '{n} は {s} の {a} にある{t}のプロジェクトです。内容、立地、間取りと価格、向いている購入者、決める前に比較したい点をまとめました。',
                   '{n}는 {s} {a}에 있는 {t} 프로젝트입니다. 프로젝트 내용, 위치, 타입과 가격, 어떤 구매자에게 맞는지, 결정 전에 비교할 점을 정리했습니다.',
                   n=name, t=typ, a=area, s=state),
        'sections': [s for s in secs if s['paragraphs']], 'stats': stats,
        'takeaway': T('If {n} fits your plan, I can send you the latest price list, the units still available and the floor plans. WhatsApp me and I will reply personally.',
                      '如果 {n} 符合你的计划，我可以发给你最新价格表、剩余单位和户型图。WhatsApp 我，我会亲自回复。',
                      'Jika {n} sesuai dengan rancangan anda, saya boleh hantar senarai harga terkini, unit yang masih ada dan pelan lantai. WhatsApp saya dan saya akan membalas sendiri.',
                      '{n} が計画に合うなら、最新の価格表、空き住戸、間取り図をお送りします。WhatsApp をいただければ、私が直接お返事します。',
                      '{n}가 계획에 맞는다면 최신 가격표, 남은 세대, 평면도를 보내 드리겠습니다. WhatsApp 주시면 제가 직접 답변드립니다.', n=name),
        'sources': []}


def article_two(i, p, date):
    name, (state, area) = p['name'], A.PLACES[i]
    ex = p.get('details_extra') or {}
    lays = [l for l in (p.get('layouts') or []) if l.get('type')]
    mp = maint_psf(ex)
    if len(lays) > 1:
        sizes = [x for x in (sqft(l.get('size')) for l in lays) if x]
        secs = []
        for l in lays[:6]:
            bits = []
            if ok(l.get('rooms')):
                bits.append(T('{r}.', '{r}。', '{r}.', '{r}。', '{r}.', r=tr(l['rooms'])))
            if ok(l.get('desc')):
                bits.append(tr(l['desc']))
            sq = sqft(l.get('size'))
            if mp and sq:
                bits.append(T('Maintenance fee: about RM{m} a month.', '管理费每月约 RM{m}。', 'Yuran penyelenggaraan: kira-kira RM{m} sebulan.', '管理費は月約 RM{m}。', '관리비는 월 약 RM{m}입니다.', m='{:,}'.format(int(round(sq * mp)))))
            if bits:
                secs.append({'h2': T('{t}: {s}', '{t}：{s}', '{t}: {s}', '{t}：{s}', '{t}: {s}', t=tr(lname(l['type'])), s=tr(l.get('size', ''))), 'paragraphs': [join(bits)]})
        last = [T('Choose a smaller layout for a lower entry price, or a larger one for more space and rooms. Whichever you choose, check the exact unit, floor and price before you book.',
                  '想要较低的入场价，可以选小户型；想要更大的空间和更多房间，就选大户型。不管选哪个，下订前都要确认实际单位、楼层和价格。',
                  'Pilih susun atur kecil untuk harga permulaan lebih rendah, atau yang lebih besar untuk ruang dan bilik lebih banyak. Apa pun pilihan anda, semak unit, tingkat dan harga sebenar sebelum menempah.',
                  '手頃な価格なら小さめの間取り、広さと部屋数なら大きめの間取りがおすすめです。どれを選んでも、予約前に実際の住戸、階、価格を確認してください。',
                  '낮은 진입 가격을 원하면 작은 타입, 더 넓은 공간과 방을 원하면 큰 타입을 고르세요. 어떤 타입이든 예약 전에 실제 세대, 층, 가격을 확인하세요.')]
        if len(lays) > 6:
            last.insert(0, T('Other layouts: {l}.', '其他户型：{l}。', 'Susun atur lain: {l}.', 'その他の間取り：{l}。', '기타 타입: {l}.', l=lst([tr('%s (%s)' % (lname(l['type']), l.get('size', ''))) for l in lays[6:]])))
        secs.append({'h2': T('Which one to choose', '怎么选', 'Mana satu yang patut dipilih', 'どれを選ぶか', '어떤 타입을 고를까'), 'paragraphs': [join(last)]})
        rng = ('%s – %s sqft' % ('{:,}'.format(min(sizes)), '{:,}'.format(max(sizes)))) if sizes else p['size']
        stats = [{'value': str(len(lays)), 'label': T('layouts', '种户型', 'susun atur', '間取りタイプ', '타입')}]
        if sizes:
            stats += [{'value': '{:,} sqft'.format(min(sizes)), 'label': T('smallest layout', '最小户型', 'susun atur terkecil', '最小の間取り', '가장 작은 타입')},
                      {'value': '{:,} sqft'.format(max(sizes)), 'label': T('largest layout', '最大户型', 'susun atur terbesar', '最大の間取り', '가장 큰 타입')}]
        return {
            'slug': '%s-layouts-which-one-fits-you' % A.SLUG[i], 'project': A.SLUG[i], 'date': date, 'auto': True,
            'cat': T('Layout Guide', '户型比较', 'Panduan Susun Atur', '間取り比較', '타입 비교'),
            'title': T('{n} Layouts: Which One Fits You?', '{n} 户型怎么选？哪个适合你', 'Susun Atur {n}: Mana Satu Sesuai untuk Anda?', '{n} の間取り比較：どれがあなたに合う？', '{n} 타입 비교: 어떤 타입이 나에게 맞을까?', n=name),
            'intro': T('{n} has {k} layouts, from {r}. Here is a side-by-side look at each type, its rooms and, where it is published, the monthly maintenance fee.',
                       '{n} 有 {k} 种户型，面积从 {r}。这篇把每个户型的面积、房间和管理费（有公布的话）放在一起比较。',
                       '{n} mempunyai {k} susun atur, dari {r}. Ini perbandingan setiap jenis, biliknya dan, jika diterbitkan, yuran penyelenggaraan bulanan.',
                       '{n} には {r} の {k} タイプの間取りがあります。各タイプの部屋数と、公表されている場合は毎月の管理費を並べて比較します。',
                       '{n}에는 {r}의 {k}가지 타입이 있습니다. 각 타입의 방 구성과, 공개된 경우 월 관리비를 나란히 비교합니다.',
                       n=name, k=len(lays), r=rng),
            'sections': secs, 'stats': stats,
            'takeaway': T('The right layout depends on how you will use the home. Tell me your plan and I will suggest the layout and floor that fit, with the latest prices.',
                          '选哪个户型，要看你打算怎么用这个家。告诉我你的计划，我帮你建议合适的户型和楼层，并附上最新价格。',
                          'Susun atur yang sesuai bergantung pada cara anda menggunakan rumah ini. Beritahu saya rancangan anda dan saya akan cadangkan susun atur dan tingkat yang sesuai, dengan harga terkini.',
                          'どの間取りが合うかは住まいの使い方次第です。計画を教えていただければ、合う間取りと階を最新価格とともにご提案します。',
                          '어떤 타입이 맞는지는 집을 어떻게 쓸지에 달려 있습니다. 계획을 알려 주시면 맞는 타입과 층을 최신 가격과 함께 추천해 드리겠습니다.'),
            'sources': []}
    # one layout: a neighbourhood guide
    secs = []
    if ok(p.get('loc_text')):
        secs.append({'h2': T('Getting around', '交通', 'Pengangkutan', 'アクセス', '교통'), 'paragraphs': [tr(p['loc_text'])]})
    near = [tr(a) for a in (p.get('amenities') or []) if ok(a)]
    if near:
        secs.append({'h2': T('Places nearby', '附近有什么', 'Tempat berdekatan', '周辺の施設', '주변 시설'),
                     'paragraphs': [T('Around {n} you will find {l}.', '{n} 附近有：{l}。', 'Di sekitar {n} terdapat {l}.', '{n} の周辺には {l} があります。', '{n} 주변에는 {l} 등이 있습니다.', n=name, l=lst(near[:8]))]})
    if lays:
        l = lays[0]
        bits = [T('Every home at {n} is {t}, {s}, with {r}.', '{n} 的单位都是 {t}，面积 {s}，{r}。', 'Setiap rumah di {n} ialah {t}, {s}, dengan {r}.', '{n} の住戸はすべて {t}、{s}、{r}。', '{n}의 모든 세대는 {t}, {s}, {r}입니다.',
                  n=name, t=tr(lname(l['type'])), s=tr(l.get('size', p['size'])), r=tr(l.get('rooms') or p['rooms']))]
        if ok(l.get('desc')):
            bits.append(tr(l['desc']))
        secs.append({'h2': T('The home', '单位介绍', 'Rumahnya', '住戸について', '세대 소개'), 'paragraphs': [join(bits)]})
    pts = [tr(s) for s in ((p.get('selling_points') or []) + (p.get('points') or [])) if ok(s)][:3]
    if pts:
        secs.append({'h2': T('Facilities and highlights', '设施和亮点', 'Kemudahan dan tarikan', '施設と特徴', '시설과 특징'), 'paragraphs': pts})
    fits = [f for f in (p.get('buyer_fit') or []) if ok(f['title']) and ok(f['desc'])][:3]
    if fits:
        secs.append({'h2': T('Who will enjoy living here', '适合住在这里的人', 'Siapa yang akan suka tinggal di sini', 'こんな方に向いています', '이곳에 살기 좋은 분'),
                     'paragraphs': [T('{t}: {d}', '{t}：{d}', '{t}: {d}', '{t}：{d}', '{t}: {d}', t=tr(f['title']), d=tr(f['desc'])) for f in fits]})
    return {
        'slug': '%s-neighbourhood-guide' % A.SLUG[i], 'project': A.SLUG[i], 'date': date, 'auto': True,
        'cat': T('Neighbourhood Guide', '生活圈指南', 'Panduan Kejiranan', '周辺ガイド', '생활권 가이드'),
        'title': T('Living at {n}: A Neighbourhood Guide', '住在 {n}：生活圈指南', 'Tinggal di {n}: Panduan Kejiranan', '{n} の暮らし：周辺ガイド', '{n}에서의 생활: 생활권 가이드', n=name),
        'intro': T('What is it like to live at {n} in {a}? Here is a guide to getting around, the places nearby, the home itself and who will enjoy living here.',
                   '住在 {a} 的 {n} 是怎样的？这篇介绍交通、附近的地方、单位本身，以及适合住在这里的人。',
                   'Bagaimana rasanya tinggal di {n} di {a}? Ini panduan tentang pengangkutan, tempat berdekatan, rumahnya dan siapa yang akan suka tinggal di sini.',
                   '{a} の {n} での暮らしはどんなもの？アクセス、周辺の施設、住戸、向いている方をご紹介します。',
                   '{a}의 {n}에서의 생활은 어떨까요? 교통, 주변 시설, 세대, 그리고 이곳에 살기 좋은 분을 소개합니다.', n=name, a=area),
        'sections': secs,
        'stats': [{'value': p['size'], 'label': T('built-up size', '面积', 'keluasan binaan', '専有面積', '전용 면적')},
                  {'value': area, 'label': T('area', '地区', 'kawasan', 'エリア', '지역')},
                  {'value': re.sub(r'^From\s*', '', re.sub(r'\s*\(.*?\)', '', p['price'])), 'label': T('starting price', '起价', 'harga permulaan', '開始価格', '시작 가격')}],
        'takeaway': T('If you would like to see {n} or the area around it, WhatsApp me and I will arrange a viewing or a video tour.',
                      '想看看 {n} 或附近环境，WhatsApp 我，我帮你安排看房或视频导览。',
                      'Jika anda ingin melihat {n} atau kawasan sekitarnya, WhatsApp saya dan saya akan aturkan lawatan atau lawatan video.',
                      '{n} や周辺を見てみたい方は WhatsApp でご連絡ください。内覧やビデオツアーを手配します。',
                      '{n}나 주변을 보고 싶으시면 WhatsApp 주세요. 방문이나 영상 투어를 준비해 드리겠습니다.', n=name),
        'sources': []}


def main():
    hand = {a['project'] for a in (json.load(open(HAND, encoding='utf-8')) if os.path.exists(HAND) else [])}
    dates = json.load(open(DATES, encoding='utf-8')) if os.path.exists(DATES) else {}
    today = datetime.date.today().strftime('%d %b %Y').lstrip('0')
    arts = []
    for i, p in enumerate(A.P):
        slug = A.SLUG.get(i)
        if not slug or slug in hand or not os.path.exists('property/%s.html' % slug):
            continue
        d = dates.setdefault(slug, today)
        arts += [article_one(i, p, d), article_two(i, p, d)]
    json.dump(arts, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(dates, open(DATES, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    print('auto project articles: %d for %d projects' % (len(arts), len(arts) // 2))


if __name__ == '__main__':
    main()
