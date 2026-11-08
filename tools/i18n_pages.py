"""Translate the generated area guides and best-of list pages into the site's languages.

The pages are written in English. translate(page) finds each piece of visible
text in <main> and the footer, looks it up (exact text, project data such as
"2 – 3 Bedrooms", or a sentence pattern such as "There are 12 projects on this
list: ..."), wraps it in <span data-pt="i"> and embeds the translations, so the
language switcher in tools/site_header.py can swap them in the browser.

Translations live in tools/i18n/pages_<lang>.json, keyed by the ids in EN below
(list pages use '<slug>.t', '<slug>.h', '<slug>.i'; area intros 'intro.<place>').
A missing translation simply stays in English. When you add a list or area,
add its texts to each language file (python3 tools/i18n_pages.py lists what is missing).
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
LANGS = ['zh-CN', 'zh-TW', 'ms', 'ta', 'ja', 'ko', 'ar']

UI = {
    'ui.home': 'Home', 'ui.bestlists': 'Best new launch lists', 'ui.projects': 'Projects', 'ui.malaysia': 'Malaysia',
    'ui.compare': 'Compare at a glance', 'ui.project': 'Project', 'ui.area': 'Area', 'ui.startprice': 'Starting price',
    'ui.size': 'Size', 'ui.tenure': 'Tenure', 'ui.completion': 'Completion', 'ui.bedrooms': 'Bedrooms',
    'ui.totalunits': 'Total units', 'ui.frompsf': 'From psf', 'ui.largest': 'Largest unit', 'ui.startingfrom': 'Starting from',
    'ui.freehold': 'Freehold', 'ui.about': 'About this list', 'ui.more': 'More lists', 'ui.notsure': 'Not sure which one fits you?',
    'ui.notsure_p': 'Send Keith your budget and needs, and he will shortlist the right projects and units.',
    'ui.wa': 'WhatsApp Keith', 'ui.allprojects': 'All projects', 'ui.privacy': 'Privacy Policy', 'ui.terms': 'Terms of Use',
    'ui.alllists': 'All lists →', 'ui.otherstates': 'Other states',
    'ui.note_list': 'Prices are gross starting prices as published and may change. Lists are generated from the project details on this site; confirm the latest prices, units and terms with Keith before deciding.',
    'ui.note_area': 'Prices are gross starting prices as published and may change. Confirm the latest prices, units and terms with Keith before deciding.',
    'ui.area_cta_p': 'Tell Keith your budget and needs, and he will shortlist the right units for you.',
    'ui.index_t': 'Best New Launch Lists',
    'ui.index_i': 'Shortcuts to the projects that match what you are looking for: budget, freehold, near rail, dual key, studios, completion date and more. Every list updates automatically.',
    'faq.q1': 'How many projects are on this list?', 'faq.q2': 'How is this list made?',
    'faq.a2': 'It is built from the published details of every project on keithnah.com and updates automatically when projects are added or prices change. Prices are gross starting prices.',
    'faq.q3': 'What is the lowest starting price on this list?', 'faq.q4': 'Can Keith help me choose between these projects?',
    'faq.a4': 'Yes. WhatsApp Keith with your budget, preferred area and whether you will live in or rent out the unit, and he will shortlist the best fits and share the latest prices and available units.',
    'afaq.a3c': 'The projects Keith lists here are leasehold. Ask Keith about freehold options nearby.',
    'afaq.a5b': 'Yes, subject to the state minimum purchase price for foreigners and state consent. The threshold differs by state and property type; Keith can confirm it for each project.',
    'fm.kl': 'RM1 million for most residential property types', 'fm.sel': 'RM2 million',
    # View Projects block
    'qp.eyebrow': 'Shortcuts · updated {y}', 'qp.sub': 'Ready-made shortlists by budget, freehold, MRT and LRT, layout and completion date. New projects join the right lists automatically.',
    'qp.Budget': 'Budget', 'qp.Freehold': 'Freehold', 'qp.Transit': 'Transit', 'qp.Layout': 'Layout', 'qp.Completion': 'Completion',
    'qp.New': 'New', 'qp.Value': 'Value', 'qp.Lifestyle': 'Lifestyle',
    'qp.l1': 'Under RM500K', 'qp.l2': 'Under RM800K', 'qp.l3': 'Freehold under RM1M near rail', 'qp.l4': 'Near an MRT station',
    'qp.l5': '3-bedroom units', 'qp.l6': 'Dual key units', 'qp.l7': 'Ready to move in', 'qp.l8': 'Latest new launches',
    'qp.l9': 'Lowest psf in KL', 'qp.l10': 'Near international schools', 'qp.l11': 'Freehold in KL', 'qp.l12': 'Sea view & waterfront',
}
UI.update({"pp.price": "Starting Price", "pp.compare": "Compare projects", "pp.highlights": "Top Highlights", "pp.details": "Project Details", "pp.info": "Project Information", "pp.name": "Project Name", "pp.dev": "Developer", "pp.loc": "Location", "pp.ptype": "Property Type", "pp.status": "Status", "pp.fac": "Facilities", "pp.featured": "Featured in these lists", "pp.tap": "Tap a tag to see every project that matches it.", "pp.near": "Nearby Projects", "pp.arts": "Related Articles", "pp.g1": "This project", "pp.g2": "Location & landmarks", "pp.g3": "Transit", "pp.g4": "Tenure & status", "pp.g5": "Price & unit type", "pp.g6": "Area & developer", "pp.ask": "Ask for the latest price, available units and the full floor plans.", "pp.note": "Prices, sizes and availability are indicative and subject to change. Confirm current figures with Keith before making decisions.", "pp.wa": "WhatsApp Keith About This Project", "pp.t1": "Residential", "pp.t2": "Serviced Apartment", "pp.t3": "Commercial Suites", "pp.k1": "Title", "pp.k2": "Total Units", "pp.k3": "Land Area", "pp.k4": "Car Parks", "pp.k5": "Security", "pp.k6": "Maintenance Fee", "pp.k7": "Lifts", "pp.k8": "Price per Sqft", "pp.k9": "Furnishing", "pp.k10": "Price Guide", "pp.k11": "Launch", "pp.k12": "Ceiling Height", "pp.k13": "Maintenance", "pp.k14": "Unit Mix", "pp.k15": "Building Height", "pp.k16": "Certification", "pp.k17": "Units per Floor", "pp.k18": "Number of Units", "pp.k19": "Number of Floors", "pp.v1": "Multi-tier security", "pp.v2": "Multi-Tier Security", "pp.v3": "Floor plan on request"})
# Sentence patterns: {x} is any text; groups named in TRG are translated too (and must be translatable).
TPL = {
    'tpl.h1year': '{h} ({y})', 'tpl.updated_n': 'Updated {y} · {n} projects', 'tpl.updated': 'Updated {y}',
    'tpl.nproj': '{n} projects', 'tpl.nprojarrow': '{n} projects →', 'tpl.viewall': 'View all {n} lists →',
    'tpl.of': '{a} of {n}', 'tpl.a1': 'There are {n} projects on this list: {names}.', 'tpl.a3': 'About {p} (gross), at {name}.',
    'tpl.area_h1': 'New Launch Condos in {place} ({y})',
    'tpl.area_hero_low': '{intro} Keith Nah currently lists {n} projects here, starting from about {p} (gross). Compare starting prices, sizes, tenure and completion dates below, then open any project for its floor plans.',
    'tpl.area_hero': '{intro} Keith Nah currently lists {n} projects here. Compare starting prices, sizes, tenure and completion dates below, then open any project for its floor plans.',
    'tpl.projects_in': 'Projects in {place}', 'tpl.buying': 'Buying in {place}: common questions',
    'tpl.aq1': 'How many new launch projects are there in {place}?', 'tpl.aa1': 'Keith currently lists {n} projects in {place}: {names}.',
    'tpl.aq2': 'What is the lowest starting price for a new property in {place}?',
    'tpl.aa2': 'The lowest published starting price is about {p} (gross) at {name}. Prices change with each phase and unit; ask Keith for the latest figures.',
    'tpl.aq3': 'Are there freehold projects in {place}?', 'tpl.aa3a': 'Yes. Freehold projects here include {names}.',
    'tpl.aa3b': 'Yes, all {n} projects listed here are freehold.',
    'tpl.aq4': 'When will the new projects in {place} be completed?',
    'tpl.aa4a': 'Expected completion ranges from {a} to {b}, depending on the project. Some projects complete a set number of months after the advertising permit (APDL).',
    'tpl.aa4b': 'Expected completion for the listed projects is around {a}.',
    'tpl.aq5': 'Can foreigners buy property in {place}?',
    'tpl.aa5a': 'Yes. Foreign buyers in {state} must meet the state minimum purchase price, currently {fm}, and need state consent.',
    'tpl.other_areas': 'Other areas in {state}', 'tpl.all_of': 'All of {state}', 'tpl.areas_in': 'Areas in {state}',
    'tpl.popular': 'Popular lists with {place} projects', 'tpl.area_cta': 'Looking for a home or investment in {place}?',
    'tpl.card_status': '{place} · {st}',
    'tpl.pp_about': 'About {name}',
    'tpl.pp_plans': '{name} Floor Plans & Unit Types',
    'tpl.pp_who': 'Who Should Consider {name}?',
    'tpl.pp_pop': 'Popular Searches for {name}',
    'tpl.pp_take': "Want Keith's take on {name}?"
}
TRG = {'h': 'exact', 'intro': 'exact', 'fm': 'exact', 'st': 'status'}
STATUS = {'Under Construction', 'New Launch', 'Coming Soon', 'Completed'}

# Words in project data (bedrooms, tenure, completion, price) when there is no exact translation.
WORDS = {
    'zh-CN': [('Bedrooms', '卧室'), ('Bedroom', '卧室'), ('Bathrooms', '浴室'), ('Bathroom', '浴室'), ('Beds', '卧室'), ('Rooms', '房'), ('Study', '书房'),
              ('Dual-Key avail.', '可选双钥匙'), ('Dual Key available', '可选双钥匙'), ('incl. Dual Key', '含双钥匙'), ('Dual Key', '双钥匙'), ('Studio', '单间'), ('Suite', '套房'), ('Type', '户型'),
              ('Leasehold', '租赁地契'), ('Freehold', '永久地契'), ('Commercial title under HDA', '商业地契，受 HDA 保障'), ('years', '年'), ('yrs from VP', '年（自交屋起）'),
              ('to', '至'), ('until', '至'), ('expires', '到期'), ('expiring', '到期'),
              ('months after APDL', '个月（自 APDL 起）'), ('Months After APDL', '个月（自 APDL 起）'), ('months from SPA', '个月（自签约起）'), ('years from SPA date', '年（自签约起）'), ('years from SPA', '年（自签约起）'),
              ('Completed', '已完工'), ('refurbished', '翻新'), ('tentatively', '暂定'), ('Targeted', '目标'), ('End of', '年底'), ('Phase', '阶段'), ('Tower', '大楼'), ('months', '个月'),
              ('Est.', '预计'), ('Under Construction', '施工中'), ('New Launch', '新开盘'), ('Coming Soon', '即将推出'),
              ('Condovillas from', '公寓别墅起价'), ('ParkHomes from', 'ParkHomes 起价'), ('From', '起价'), ('(Gross)', '（总价）'), ('(est.)', '（预估）'), ('sqft', '平方英尺'), ('mil', '百万')],
    'zh-TW': [('Bedrooms', '臥室'), ('Bedroom', '臥室'), ('Bathrooms', '浴室'), ('Bathroom', '浴室'), ('Beds', '臥室'), ('Rooms', '房'), ('Study', '書房'),
              ('Dual-Key avail.', '可選雙鑰匙'), ('Dual Key available', '可選雙鑰匙'), ('incl. Dual Key', '含雙鑰匙'), ('Dual Key', '雙鑰匙'), ('Studio', '單間'), ('Suite', '套房'), ('Type', '戶型'),
              ('Leasehold', '租賃地契'), ('Freehold', '永久地契'), ('Commercial title under HDA', '商業地契，受 HDA 保障'), ('years', '年'), ('yrs from VP', '年（自交屋起）'),
              ('to', '至'), ('until', '至'), ('expires', '到期'), ('expiring', '到期'),
              ('months after APDL', '個月（自 APDL 起）'), ('Months After APDL', '個月（自 APDL 起）'), ('months from SPA', '個月（自簽約起）'), ('years from SPA date', '年（自簽約起）'), ('years from SPA', '年（自簽約起）'),
              ('Completed', '已完工'), ('refurbished', '翻新'), ('tentatively', '暫定'), ('Targeted', '目標'), ('End of', '年底'), ('Phase', '階段'), ('Tower', '大樓'), ('months', '個月'),
              ('Est.', '預計'), ('Under Construction', '施工中'), ('New Launch', '新開盤'), ('Coming Soon', '即將推出'),
              ('Condovillas from', '公寓別墅起價'), ('ParkHomes from', 'ParkHomes 起價'), ('From', '起價'), ('(Gross)', '（總價）'), ('(est.)', '（預估）'), ('sqft', '平方英尺'), ('mil', '百萬')],
    'ms': [('Bedrooms', 'Bilik Tidur'), ('Bedroom', 'Bilik Tidur'), ('Bathrooms', 'Bilik Mandi'), ('Bathroom', 'Bilik Mandi'), ('Beds', 'Bilik Tidur'), ('Rooms', 'Bilik'), ('Study', 'Bilik Belajar'),
           ('Dual-Key avail.', 'Dual Key tersedia'), ('Dual Key available', 'Dual Key tersedia'), ('incl. Dual Key', 'termasuk Dual Key'), ('Suite', 'Suite'), ('Type', 'Jenis'),
           ('Leasehold', 'Pajakan'), ('Freehold', 'Pegangan Bebas'), ('Commercial title under HDA', 'Hakmilik komersial di bawah HDA'), ('years', 'tahun'), ('yrs from VP', 'tahun dari VP'),
           ('until', 'hingga'), ('expires', 'tamat'), ('expiring', 'tamat'), ('to', 'hingga'),
           ('months after APDL', 'bulan selepas APDL'), ('Months After APDL', 'bulan selepas APDL'), ('months from SPA', 'bulan dari SPA'), ('years from SPA date', 'tahun dari tarikh SPA'), ('years from SPA', 'tahun dari SPA'),
           ('Completed', 'Siap'), ('refurbished', 'diubah suai'), ('tentatively', 'dijangka'), ('Targeted', 'Sasaran'), ('End of', 'Hujung'), ('Phase', 'Fasa'), ('Tower', 'Menara'), ('months', 'bulan'),
           ('Est.', 'Anggaran'), ('Under Construction', 'Sedang Dibina'), ('New Launch', 'Pelancaran Baharu'), ('Coming Soon', 'Akan Datang'),
           ('Condovillas from', 'Condovilla dari'), ('ParkHomes from', 'ParkHomes dari'), ('From', 'Dari'), ('(Gross)', '(Kasar)'), ('(est.)', '(anggaran)'), ('sqft', 'kaki persegi'), ('mil', 'juta')],
    'ta': [('Bedrooms', 'படுக்கையறை'), ('Bedroom', 'படுக்கையறை'), ('Bathrooms', 'குளியலறை'), ('Bathroom', 'குளியலறை'), ('Beds', 'படுக்கையறை'), ('Rooms', 'அறைகள்'), ('Study', 'படிப்பறை'),
           ('Dual-Key avail.', 'Dual Key உள்ளது'), ('Dual Key available', 'Dual Key உள்ளது'), ('incl. Dual Key', 'Dual Key உட்பட'), ('Type', 'வகை'),
           ('Leasehold', 'குத்தகை (Leasehold)'), ('Freehold', 'சுதந்திர உரிமை (Freehold)'), ('Commercial title under HDA', 'HDA கீழ் வணிக உரிமம்'), ('years', 'ஆண்டுகள்'), ('yrs from VP', 'ஆண்டுகள் (VP முதல்)'),
           ('until', 'வரை'), ('expires', 'முடிவு'), ('expiring', 'முடிவு'), ('to', 'வரை'),
           ('months after APDL', 'மாதங்கள் (APDL பிறகு)'), ('Months After APDL', 'மாதங்கள் (APDL பிறகு)'), ('months from SPA', 'மாதங்கள் (SPA முதல்)'), ('years from SPA date', 'ஆண்டுகள் (SPA தேதி முதல்)'), ('years from SPA', 'ஆண்டுகள் (SPA முதல்)'),
           ('Completed', 'முடிக்கப்பட்டது'), ('refurbished', 'புதுப்பிப்பு'), ('tentatively', 'தற்காலிகமாக'), ('Targeted', 'இலக்கு'), ('End of', 'இறுதி'), ('Phase', 'கட்டம்'), ('Tower', 'கோபுரம்'), ('months', 'மாதங்கள்'),
           ('Est.', 'மதிப்பீடு'), ('Under Construction', 'கட்டுமானத்தில்'), ('New Launch', 'புதிய வெளியீடு'), ('Coming Soon', 'விரைவில்'),
           ('Condovillas from', 'Condovillas தொடக்கம்'), ('ParkHomes from', 'ParkHomes தொடக்கம்'), ('From', 'தொடக்கம்'), ('(Gross)', '(மொத்தம்)'), ('(est.)', '(மதிப்பீடு)'), ('sqft', 'சதுர அடி'), ('mil', 'மில்லியன்')],
    'ja': [('Bedrooms', 'ベッドルーム'), ('Bedroom', 'ベッドルーム'), ('Bathrooms', 'バスルーム'), ('Bathroom', 'バスルーム'), ('Beds', 'ベッドルーム'), ('Rooms', '部屋'), ('Study', '書斎'),
           ('Dual-Key avail.', 'デュアルキーあり'), ('Dual Key available', 'デュアルキーあり'), ('incl. Dual Key', 'デュアルキー含む'), ('Dual Key', 'デュアルキー'), ('Studio', 'スタジオ'), ('Suite', 'スイート'), ('Type', 'タイプ'),
           ('Leasehold', 'リースホールド'), ('Freehold', 'フリーホールド'), ('Commercial title under HDA', 'HDA適用の商業用タイトル'), ('years', '年'), ('yrs from VP', '年（引渡しから）'),
           ('until', 'まで'), ('expires', '満了'), ('expiring', '満了'), ('to', '～'),
           ('months after APDL', 'か月（APDL取得後）'), ('Months After APDL', 'か月（APDL取得後）'), ('months from SPA', 'か月（SPA締結から）'), ('years from SPA date', '年（SPA締結日から）'), ('years from SPA', '年（SPA締結から）'),
           ('Completed', '完成済み'), ('refurbished', '改装'), ('tentatively', '暫定'), ('Targeted', '目標'), ('End of', '年末'), ('Phase', 'フェーズ'), ('Tower', 'タワー'), ('months', 'か月'),
           ('Est.', '予定'), ('Under Construction', '建設中'), ('New Launch', '新規販売'), ('Coming Soon', '近日発売'),
           ('Condovillas from', 'コンドヴィラ'), ('ParkHomes from', 'パークホーム'), ('From', ''), ('(Gross)', '～（総額）'), ('(est.)', '（概算）'), ('sqft', '平方フィート'), ('mil', '百万')],
    'ko': [('Bedrooms', '침실'), ('Bedroom', '침실'), ('Bathrooms', '욕실'), ('Bathroom', '욕실'), ('Beds', '침실'), ('Rooms', '룸'), ('Study', '서재'),
           ('Dual-Key avail.', '듀얼키 가능'), ('Dual Key available', '듀얼키 가능'), ('incl. Dual Key', '듀얼키 포함'), ('Dual Key', '듀얼키'), ('Studio', '스튜디오'), ('Suite', '스위트'), ('Type', '타입'),
           ('Leasehold', '리스홀드'), ('Freehold', '프리홀드'), ('Commercial title under HDA', 'HDA 적용 상업용 소유권'), ('years', '년'), ('yrs from VP', '년(입주 기준)'),
           ('until', '까지'), ('expires', '만료'), ('expiring', '만료'), ('to', '~'),
           ('months after APDL', '개월(APDL 이후)'), ('Months After APDL', '개월(APDL 이후)'), ('months from SPA', '개월(SPA 체결 기준)'), ('years from SPA date', '년(SPA 체결일 기준)'), ('years from SPA', '년(SPA 체결 기준)'),
           ('Completed', '완공'), ('refurbished', '리모델링'), ('tentatively', '잠정'), ('Targeted', '목표'), ('End of', '말'), ('Phase', '단계'), ('Tower', '타워'), ('months', '개월'),
           ('Est.', '예상'), ('Under Construction', '건설 중'), ('New Launch', '신규 분양'), ('Coming Soon', '분양 예정'),
           ('Condovillas from', '콘도빌라'), ('ParkHomes from', '파크홈'), ('From', ''), ('(Gross)', '부터 (총액)'), ('(est.)', '(추정)'), ('sqft', '평방피트'), ('mil', '백만')],
    'ar': [('Bedrooms', 'غرف نوم'), ('Bedroom', 'غرفة نوم'), ('Bathrooms', 'حمامات'), ('Bathroom', 'حمام'), ('Beds', 'غرف نوم'), ('Rooms', 'غرف'), ('Study', 'مكتب'),
           ('Dual-Key avail.', 'مع خيار المفتاح المزدوج'), ('Dual Key available', 'مع خيار المفتاح المزدوج'), ('incl. Dual Key', 'يشمل المفتاح المزدوج'), ('Dual Key', 'مفتاح مزدوج'), ('Studio', 'استوديو'), ('Suite', 'جناح'), ('Type', 'النوع'),
           ('Leasehold', 'إيجار طويل الأجل'), ('Freehold', 'تملك حر'), ('Commercial title under HDA', 'سند تجاري بموجب HDA'), ('years', 'سنة'), ('yrs from VP', 'سنة من التسليم'),
           ('until', 'حتى'), ('expires', 'ينتهي'), ('expiring', 'ينتهي'), ('to', 'إلى'),
           ('months after APDL', 'شهرًا بعد APDL'), ('Months After APDL', 'شهرًا بعد APDL'), ('months from SPA', 'شهرًا من توقيع SPA'), ('years from SPA date', 'سنوات من تاريخ SPA'), ('years from SPA', 'سنوات من SPA'),
           ('Completed', 'مكتمل'), ('refurbished', 'تم التجديد'), ('tentatively', 'مبدئيًا'), ('Targeted', 'المستهدف'), ('End of', 'نهاية'), ('Phase', 'المرحلة'), ('Tower', 'البرج'), ('months', 'شهرًا'),
           ('Est.', 'متوقع'), ('Under Construction', 'قيد الإنشاء'), ('New Launch', 'إطلاق جديد'), ('Coming Soon', 'قريبًا'),
           ('Condovillas from', 'شقق فلل من'), ('ParkHomes from', 'ParkHomes من'), ('From', 'من'), ('(Gross)', '(إجمالي)'), ('(est.)', '(تقديري)'), ('sqft', 'قدم مربع'), ('mil', 'مليون')],
}


def _load():
    tr = {}
    for l in LANGS:
        p = os.path.join(HERE, 'i18n', 'pages_%s.json' % l)
        tr[l] = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
    return tr


def _kn_tr():
    out = {}
    root = os.path.dirname(HERE)
    for l in LANGS:
        p = os.path.join(root, 'i18n-projects-%s.js' % l)
        try:
            t = open(p, encoding='utf-8').read()
            m = 'window.KN_TR["%s"]=' % l
            out[l] = json.JSONDecoder().raw_decode(t[t.index(m) + len(m):])[0]
        except (OSError, ValueError):
            out[l] = {}
    return out


TR = _load()
KN = _kn_tr()
EN = dict(UI)
_REV = {}          # id -> English; list and area texts are added by register()
try:
    EN.update(json.load(open(os.path.join(HERE, 'i18n', 'pages_en.json'), encoding='utf-8')))
except (OSError, ValueError):
    pass
TPL_RX = []
for _id, _en in TPL.items():
    rx = re.escape(_en).replace('projects', 'projects?')
    rx = re.sub(r'\\\{(\w+)\\\}', lambda m: '(?P<%s>%s)' % (m.group(1), r'[\d,]+' if m.group(1) in ('n', 'y', 'a', 'b') else '.+?'), rx)
    TPL_RX.append((_id, re.compile('^%s$' % rx, re.S)))
DATA = set()
USE_KN = [False]   # project pages: also look up the site's project translations (i18n-projects-*.js)


def register(ids):
    """ids: {id: English text} for lists and area intros, plus project data values in DATA."""
    EN.update(ids)
    _REV.clear()


def save_en():
    """Write every English text id to tools/i18n/pages_en.json (read by builds that do not make the lists)."""
    json.dump(EN, open(os.path.join(HERE, 'i18n', 'pages_en.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)


def _exact(en, lang):
    for k, v in EN.items():
        if v == en:
            t = TR[lang].get(k)
            if t:
                return t
    return None


def exact(en, lang):
    if not _REV:
        for k, v in EN.items():
            _REV.setdefault(v, k)
    k = _REV.get(en)
    return TR[lang].get(k) if k else None


def data(en, lang):
    if en in KN[lang]:
        return KN[lang][en]
    out = en
    for a, b in WORDS[lang]:
        out = re.sub(r'(?<![A-Za-z])%s(?![A-Za-z])' % re.escape(a), lambda _: b, out)
    out = re.sub(r'\s{2,}', ' ', out).strip()
    return out if out != en else None


def one(en, lang, raw=None):
    t = exact(en, lang)
    if t:
        return t
    if raw is not None and USE_KN[0]:
        k = KN[lang].get(raw) or KN[lang].get(en) or KN[lang].get(html.escape(en, quote=False))
        if k:
            return html.unescape(re.sub(r'<[^>]+>', '', k))
    if en in DATA:
        return data(en, lang)
    for tid, rx in TPL_RX:
        m = rx.match(en)
        if not m or not TR[lang].get(tid):
            continue
        vals = m.groupdict()
        ok = True
        for g, how in TRG.items():
            if g in vals:
                v = exact(vals[g], lang) if how == 'exact' else (data(vals[g], lang) if vals[g] in STATUS else None)
                if v is None:
                    ok = False
                    break
                vals[g] = v
        if not ok:
            continue
        try:
            return TR[lang][tid].format(**vals)
        except (KeyError, IndexError):
            continue
    return None


def translate(page):
    """Wrap translatable text in <main> and <footer> and embed the translations."""
    rows = []

    def node(m):
        raw = m.group(2)
        en = html.unescape(raw).strip()
        if not en or not re.search(r'[A-Za-z]{2}', en):
            return m.group(0)
        row = {}
        for l in LANGS:
            t = one(en, l, raw.strip())
            if t:
                row[l] = t
        if not row:
            return m.group(0)
        rows.append(row)
        lead = raw[:len(raw) - len(raw.lstrip())]
        tail = raw[len(raw.rstrip()):]
        return '%s%s<kn-t data-pt="%d">%s</kn-t>%s' % (m.group(1), lead, len(rows) - 1, raw.strip(), tail)

    def region(m):
        return re.sub(r'(>)([^<>]+)(?=<)', node, m.group(0))

    page = re.sub(r'<main[\s>].*?</main>', region, page, count=1, flags=re.S)
    page = re.sub(r'<footer>.*?</footer>', region, page, count=1, flags=re.S)
    if rows:
        page = page.replace('</body>', '<script>window.KN_PT=%s;</script>\n</body>' % json.dumps(rows, ensure_ascii=False).replace('</', '<\\/'), 1)
    return page


def merge_projects_page(strings):
    """Add the View Projects block's texts {English: id-or-(id, vals)} to the i18n-projects-*.js files."""
    root = os.path.dirname(HERE)
    for l in LANGS:
        p = os.path.join(root, 'i18n-projects-%s.js' % l)
        t = open(p, encoding='utf-8').read()
        m = 'window.KN_TR["%s"]=' % l
        a = t.index(m) + len(m)
        d, n = json.JSONDecoder().raw_decode(t[a:])
        changed = False
        for en, (tid, vals) in strings.items():
            src = TR[l].get(tid)
            if not src:
                continue
            v = html.escape(src.format(**vals), quote=False)
            if d.get(en) != v:
                d[en] = v
                changed = True
        if changed:
            open(p, 'w', encoding='utf-8').write(t[:a] + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + t[a + n:])


if __name__ == '__main__':
    import sys
    sys.path.insert(0, HERE)
    import build_list_pages as L
    import build_area_pages as A
    ids = dict(UI)
    ids.update(TPL)
    for s, t, h, i, _, _ in L.LISTS:
        ids.update({s + '.t': t, s + '.h': h, s + '.i': i})
    ids.update({'intro.' + k: v for k, v in A.INTRO.items()})
    for l in LANGS:
        miss = [k for k in ids if k not in TR[l]]
        print(l, 'missing %d' % len(miss), miss[:8])
