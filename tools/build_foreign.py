"""Build foreign-buyers.html: buying property in Malaysia as a foreigner.

- A state checker (pills; the card shows the minimum price for strata and landed homes, the stamp
  duty on transfer and state consent), modelled on the quick checks foreign buyers ask first.
- Costs, the buying steps, MM2H (links to mm2h.html and the MM2H library) and an FAQ.
Texts are in T per language; the page swaps them in the browser like resources.html.
Run by tools/build_all.py before build_menu.py (which adds "Foreign Buyers" to the main menu).
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
import build_area_pages as A  # noqa: E402
import site_header as SH  # noqa: E402
from build_proj_layout import ZONES  # noqa: E402

E = lambda s: html.escape(str(s), quote=True)
SITE = 'https://keithnah.com'
WA = 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0'
waq = lambda m: WA % re.sub(r'\s', '+', '(KNRE) ' + m)
LANGS = ['en', 'zh-CN', 'zh-TW', 'ms', 'ja', 'ko']
try:
    import opencc
    _cc = opencc.OpenCC('s2tw').convert
except ImportError:
    _cc = lambda s: s

# ---------- foreign-buyer minimum prices (a general guide; states revise them) ----------
# key, project state, Penang zone, strata min, landed min (None = ask Keith)
CHECK = [('kl', 'Kuala Lumpur', None, 1000000, 1000000),
         ('sel', 'Selangor', None, 2000000, 2000000),
         ('pgi', 'Penang', 'island', 1000000, 3000000),
         ('pgm', 'Penang', 'mainland', 500000, None),
         ('jhr', 'Johor', None, 1000000, 1000000),
         ('mlk', 'Melaka', None, 500000, 1000000),
         ('sbh', 'Sabah', None, 600000, 1000000)]
PG_ZONE = {a: z for z, lst in ZONES.get('Penang', []) for a in lst}


def check_key(state, area):
    for k, st, zone, *_ in CHECK:
        if st == state and (zone is None or PG_ZONE.get(area, 'mainland') == zone):
            return k
    return None


def prices(s):
    s = (s or '').replace(',', '')
    out = []
    for m in re.finditer(r'RM\s*([\d.]+)\s*(k|m|mil|million)?\b(?!\s*(?:psf|per\s*s))', s, re.I):
        v = float(m.group(1)); u = (m.group(2) or '').lower()
        v = v * 1000 if u == 'k' else v * 1e6 if u in ('m', 'mil', 'million') else v
        if v >= 50000:
            out.append(v)
    return out


MINS = {k: smin for k, _, _, smin, _ in CHECK}
OK, LARGER = [], []
for i, p in enumerate(A.P):
    st, area = A.PLACES[i]
    k = check_key(st, area)
    ps = prices(p['price'])
    if not k or not ps:
        continue
    if min(ps) >= MINS[k]:
        OK.append((k, min(ps), i))
    elif max(ps) >= MINS[k]:
        LARGER.append((k, min(ps), i))
OK.sort(key=lambda x: ([c[0] for c in CHECK].index(x[0]), x[1]))
LARGER.sort(key=lambda x: ([c[0] for c in CHECK].index(x[0]), x[1]))
COUNT = {k: sum(1 for x in OK if x[0] == k) for k, *_ in CHECK}

# ---------- texts ----------
T = {'en': {
    'title': 'Buying Property in Malaysia as a Foreigner', 'eyebrow': 'Foreign Buyers',
    'lead': 'Yes, foreigners can buy property in Malaysia, freehold included.',
    'sub': 'Each state sets a minimum price, the purchase needs state consent and stamp duty is charged at a flat rate. Check your state below, then ask Keith to confirm the unit you like.',
    'b_check': 'Check your state', 'b_wa': 'Ask Keith on WhatsApp',
    'f1t': 'Freehold or leasehold', 'f1d': 'Foreigners can own both, with a strata or individual title in their own name.',
    'f2t': 'Minimum price by state', 'f2d': 'From RM500,000 to RM2 million or more, depending on the state and property type.',
    'f3t': '8% stamp duty', 'f3d': 'A flat rate on the transfer for foreign buyers from 1 January 2026.',
    'f4t': 'State consent', 'f4d': 'Your lawyer applies for it after you sign. It adds a few weeks to a few months.',
    'ck_eb': 'Quick check', 'ck_h': 'Can you buy property in Malaysia?', 'ck_p': 'Pick a state to see the minimum price for foreign buyers.',
    'ck_strata': 'Minimum price (strata: condo, serviced apartment)', 'ck_landed': 'Minimum price (landed)', 'ck_landed_s': 'Minimum price (strata-titled landed only)',
    'ck_stamp': 'Stamp duty on transfer', 'ck_stamp_v': '8% flat', 'ck_consent': 'State authority consent', 'ck_consent_v': 'Required',
    'ck_ask': 'Ask Keith', 'ck_go': 'Ask Keith which units qualify here →', 'ck_see': 'See the {n} projects that qualify', 'ck_none': 'No project on this site meets the minimum yet. Ask Keith about larger units.',
    'ck_note': 'A general guide to the current minimums. States revise them and some set different levels by district or title; Bumiputera lots and low-cost or affordable homes cannot be sold to foreigners. Keith confirms the figure for each unit before you book.',
    'n_kl': 'Kuala Lumpur is where most foreign buyers start: KL City Centre, Bukit Bintang and TRX have the widest choice above the minimum.',
    'n_sel': 'Selangor has one of the highest minimums, so most condos here are below it. Foreign buyers usually look at Kuala Lumpur or at larger homes.',
    'n_pgi': 'On Penang Island the minimum is RM1 million for strata homes and RM3 million for landed homes.',
    'n_pgm': 'Seberang Perai (Batu Kawan, Butterworth, Bukit Mertajam) has a lower strata minimum than the island.',
    'n_jhr': 'Johor Bahru is popular with Singapore-based buyers ahead of the RTS Link to Woodlands.',
    'n_mlk': 'Melaka has one of the lower strata minimums in Peninsular Malaysia.',
    'n_sbh': 'Sabah sets its own rules for foreign buyers; Kota Kinabalu is the main market.',
    's_kl': 'Kuala Lumpur', 's_sel': 'Selangor', 's_pgi': 'Penang Island', 's_pgm': 'Penang Mainland', 's_jhr': 'Johor', 's_mlk': 'Melaka', 's_sbh': 'Sabah',
    'pj_eb': 'Must-see for foreign buyers', 'pj_h': 'Projects foreign buyers can consider',
    'pj_p': 'Every project below has a starting price at or above the foreign-buyer minimum of its state. The list updates itself as projects and prices change.',
    'pj_all': 'All states', 'pj_from': 'From', 'pj_more': 'Larger units may qualify', 'pj_more_p': 'The entry units here are below the minimum, but bigger units or penthouses are priced above it.',
    'pj_note': 'Prices are gross starting prices as published. A unit must still meet the minimum on its own, so ask Keith which units qualify.',
    'fh': 'Freehold', 'lh': 'Leasehold',
    'co_eb': 'Costs', 'co_h': 'What it costs to buy and sell',
    'co1t': 'Stamp duty on the transfer', 'co1d': '8% of the price for foreign buyers (permanent residents excluded), on instruments of transfer from 1 January 2026.',
    'co2t': 'Stamp duty on the loan', 'co2d': '0.5% of the loan amount, if you take a Malaysian housing loan.',
    'co3t': 'Legal fees and state consent', 'co3d': 'Lawyer fees follow a set scale. The state consent fee and processing differ by state; Keith gets you the exact figures.',
    'co4t': 'Selling later (RPGT)', 'co4d': 'Real property gains tax for non-citizens: 30% if you sell within 5 years, 10% from the 6th year.', 'co4l': 'See the full RPGT rate table →',
    'co_note': 'A general guide, not tax or legal advice. Rates are set by the government and can change; your lawyer confirms them for your purchase.',
    'st_eb': 'Step by step', 'st_h': 'How buying works for a foreigner',
    'st1t': 'Shortlist', 'st1d': 'Tell Keith your budget, the state and whether you will live in it or rent it out. He shortlists units that clear the minimum.',
    'st2t': 'View and book', 'st2d': 'View in person or by video call, then reserve the unit with a booking fee.',
    'st3t': 'Sign the SPA', 'st3d': 'Sign the sale and purchase agreement and pay the down payment. Signing can be arranged while you are overseas.',
    'st4t': 'State consent', 'st4d': 'Your lawyer applies to the state authority for consent to the foreign purchase.',
    'st5t': 'Loan or cash', 'st5d': 'Pay in cash or apply for a loan. Some Malaysian banks lend to foreigners, usually with a lower financing margin than for locals.',
    'st6t': 'Keys and title', 'st6d': 'For a new launch, payments follow the construction stages until vacant possession and the keys.',
    'mm_eb': 'Malaysia My Second Home', 'mm_h': 'Want to live here too? Look at MM2H',
    'mm_p': 'Buying a home does not give you a visa. MM2H is a separate long-stay pass of 5, 15 or 20 years, and each tier has its own minimum property price on top of the state minimum.',
    'mm_fd': 'Fixed deposit', 'mm_pp': 'Property from', 'mm_vd': 'Visa', 'mm_y5': '5 years', 'mm_y15': '15 years', 'mm_y20': '20 years',
    'mm_btn': 'Read the MM2H guide', 'mm_lib': 'MM2H and property: two minimum prices', 'mm_lib2': 'All MM2H articles',
    'fq_eb': 'FAQ', 'fq_h': 'Questions foreign buyers ask Keith',
    'q1': 'Can foreigners buy property in Malaysia?', 'a1': 'Yes. Foreigners can buy freehold and leasehold homes if the price meets the state minimum and the state gives consent. Bumiputera lots, low-cost and affordable housing are not open to foreigners.',
    'q2': 'Is there a minimum price?', 'a2': 'Yes, each state sets one, for example RM1 million in Kuala Lumpur and RM2 million in Selangor. Use the checker above, and ask Keith to confirm the exact figure for the unit you like.',
    'q3': 'Can I get a housing loan as a foreigner?', 'a3': 'Some Malaysian banks do lend to foreigners. The financing margin is usually lower than for Malaysians and depends on your income, country and the bank. Keith can introduce you to bankers who handle foreign buyers.',
    'q4': 'Does buying a home give me a visa?', 'a4': 'No. A property purchase on its own does not come with residency. If you want to live in Malaysia, look at MM2H, which is a separate application.',
    'q5': 'Can I buy without coming to Malaysia?', 'a5': 'Much of it can be done remotely: video viewings, booking online and signing documents overseas with your lawyer. Many buyers still visit once before or after booking.',
    'q6': 'Can I rent the unit out?', 'a6': 'Yes. You can rent your home out on a normal tenancy. Rental income earned in Malaysia is taxable; non-residents are taxed at a flat rate.',
    'q7': 'What taxes do I pay when I sell?', 'a7': 'Real property gains tax for non-citizens is 30% on the gain if you sell within 5 years and 10% from the 6th year.',
    'q8': 'Which states are not listed?', 'a8': 'Terengganu, Kelantan, Sarawak and other states set their own rules. WhatsApp Keith and he will check the current position for the project you are looking at.',
    'cta_h': 'Not sure if a unit qualifies?', 'cta_p': 'Send Keith the project and unit, or just your budget and state. He will confirm the minimum, the costs and which units you can buy.',
    'disc': 'This page is a general guide for foreign buyers, not legal or tax advice. Minimum prices, stamp duty and consent rules are set by the federal and state governments and change from time to time.',
}, 'zh-CN': {
    'title': '外国人在马来西亚买房', 'eyebrow': '外国买家',
    'lead': '可以，外国人可以在马来西亚买房，永久地契也可以。',
    'sub': '每个州都有最低价格门槛，购买需要州政府批准，印花税按固定税率计算。先在下面查你的州属，再请 Keith 确认你看中的单位。',
    'b_check': '查你的州属', 'b_wa': 'WhatsApp 问 Keith',
    'f1t': '永久或租赁地契', 'f1d': '外国人两种都可以拥有，分层地契或独立地契都可以写在自己名下。',
    'f2t': '各州最低价格', 'f2d': '从 RM500,000 到 RM200 万或以上，视州属和房产类型而定。',
    'f3t': '8% 印花税', 'f3d': '2026 年 1 月 1 日起，外国买家的转让印花税为固定 8%。',
    'f4t': '州政府批准', 'f4d': '签约后由律师申请，需要几个星期到几个月。',
    'ck_eb': '快速查询', 'ck_h': '你可以在马来西亚买房吗？', 'ck_p': '选一个州属，看外国买家的最低价格。',
    'ck_strata': '最低价格（分层：公寓、服务式公寓）', 'ck_landed': '最低价格（有地房产）', 'ck_landed_s': '最低价格（仅限分层地契有地房产）',
    'ck_stamp': '转让印花税', 'ck_stamp_v': '固定 8%', 'ck_consent': '州政府批准', 'ck_consent_v': '需要',
    'ck_ask': '问 Keith', 'ck_go': '问 Keith 这里哪些单位符合 →', 'ck_see': '查看符合条件的 {n} 个项目', 'ck_none': '本站暂时没有项目达到最低价格，可以问 Keith 较大的单位。',
    'ck_note': '以上为现行最低价格的大致参考。各州会调整，有些州按地区或地契类型设不同门槛；土著保留单位和低价、可负担房屋不能卖给外国人。下订前 Keith 会为每个单位确认实际门槛。',
    'n_kl': '吉隆坡是大部分外国买家的首选：KL City Centre、Bukit Bintang 和 TRX 达到门槛的选择最多。',
    'n_sel': '雪兰莪的门槛是最高之一，这里大部分公寓都低于门槛，外国买家通常看吉隆坡或较大的房子。',
    'n_pgi': '槟岛的分层房产门槛为 RM100 万，有地房产为 RM300 万。',
    'n_pgm': '威省（Batu Kawan、Butterworth、Bukit Mertajam）的分层房产门槛比槟岛低。',
    'n_jhr': '新山很受在新加坡工作的买家欢迎，RTS 轻快铁即将连接兀兰。',
    'n_mlk': '马六甲的分层房产门槛是半岛较低的之一。',
    'n_sbh': '沙巴对外国买家有自己的规定，亚庇是主要市场。',
    's_kl': '吉隆坡', 's_sel': '雪兰莪', 's_pgi': '槟岛', 's_pgm': '威省', 's_jhr': '柔佛', 's_mlk': '马六甲', 's_sbh': '沙巴',
    'pj_eb': '外国人必看项目', 'pj_h': '外国买家可以考虑的项目',
    'pj_p': '以下每个项目的起价都达到所在州的外国买家最低价格。项目和价格更新时，列表会自动更新。',
    'pj_all': '全部州属', 'pj_from': '起价', 'pj_more': '较大单位可能符合', 'pj_more_p': '这些项目的入门单位低于门槛，但较大的单位或顶层单位价格高于门槛。',
    'pj_note': '价格为公布的总起价。每个单位本身都必须达到门槛，请问 Keith 哪些单位符合。',
    'fh': '永久地契', 'lh': '租赁地契',
    'co_eb': '费用', 'co_h': '买房和卖房的费用',
    'co1t': '转让印花税', 'co1d': '外国买家（不包括永久居民）为房价的 8%，适用于 2026 年 1 月 1 日起的转让文件。',
    'co2t': '贷款印花税', 'co2d': '如果在马来西亚申请房贷，为贷款额的 0.5%。',
    'co3t': '律师费和州政府批准', 'co3d': '律师费按规定的收费表计算。州政府批准的费用和流程各州不同，Keith 会给你实际数字。',
    'co4t': '将来出售（产业盈利税 RPGT）', 'co4d': '非公民：5 年内出售为盈利的 30%，第 6 年起为 10%。', 'co4l': '查看完整 RPGT 税率表 →',
    'co_note': '以上为一般参考，不是税务或法律意见。税率由政府制定，可能会变，你的律师会为你的交易确认。',
    'st_eb': '一步一步', 'st_h': '外国人买房的流程',
    'st1t': '筛选项目', 'st1d': '告诉 Keith 你的预算、州属，以及自住还是出租。他会筛出达到门槛的单位。',
    'st2t': '看房和下订', 'st2d': '亲自看房或视频看房，然后付订金保留单位。',
    'st3t': '签买卖合约', 'st3d': '签买卖合约（SPA）并付首期。人在国外也可以安排签约。',
    'st4t': '州政府批准', 'st4d': '律师向州政府申请外国人购买的批准。',
    'st5t': '贷款或现金', 'st5d': '可以现金付款或申请贷款。部分马来西亚银行愿意贷款给外国人，贷款成数通常比本地人低。',
    'st6t': '交钥匙和地契', 'st6d': '新楼盘按施工进度付款，直到交屋拿钥匙。',
    'mm_eb': '马来西亚第二家园', 'mm_h': '也想住在这里？看看 MM2H',
    'mm_p': '买房本身不会给你签证。MM2H 是另外申请的 5、15 或 20 年长期签证，每个等级除了州属门槛之外，还有自己的最低购房价格。',
    'mm_fd': '定期存款', 'mm_pp': '购房最低', 'mm_vd': '签证', 'mm_y5': '5 年', 'mm_y15': '15 年', 'mm_y20': '20 年',
    'mm_btn': '阅读 MM2H 指南', 'mm_lib': 'MM2H 和房产：两个最低价格', 'mm_lib2': '全部 MM2H 文章',
    'fq_eb': '常见问题', 'fq_h': '外国买家常问 Keith 的问题',
    'q1': '外国人可以在马来西亚买房吗？', 'a1': '可以。只要价格达到州属最低价格并获得州政府批准，外国人可以买永久地契和租赁地契的房子。土著保留单位、低价和可负担房屋不开放给外国人。',
    'q2': '有最低价格吗？', 'a2': '有，每个州都有，例如吉隆坡 RM100 万、雪兰莪 RM200 万。可以用上面的查询，再请 Keith 确认你看中单位的实际门槛。',
    'q3': '外国人可以申请房贷吗？', 'a3': '部分马来西亚银行愿意贷款给外国人。贷款成数通常比马来西亚人低，要看你的收入、国家和银行。Keith 可以介绍处理外国买家的银行经理。',
    'q4': '买房会给我签证吗？', 'a4': '不会。单单买房不包括居留权。如果想住在马来西亚，可以看 MM2H，那是另外的申请。',
    'q5': '不来马来西亚也可以买吗？', 'a5': '大部分可以远程完成：视频看房、网上下订、和律师安排在国外签文件。很多买家还是会在下订前后来看一次。',
    'q6': '可以出租吗？', 'a6': '可以，按一般租约出租。在马来西亚赚的租金收入需要缴税，非居民按固定税率计算。',
    'q7': '出售时要缴什么税？', 'a7': '非公民的产业盈利税：5 年内出售为盈利的 30%，第 6 年起为 10%。',
    'q8': '哪些州没有列出？', 'a8': '登嘉楼、吉兰丹、砂拉越等州有自己的规定。WhatsApp Keith，他会为你看的项目查最新规定。',
    'cta_h': '不确定单位符不符合？', 'cta_p': '把项目和单位发给 Keith，或者只说预算和州属。他会确认门槛、费用和你可以买哪些单位。',
    'disc': '本页为外国买家的一般参考，不是法律或税务意见。最低价格、印花税和批准规定由联邦和州政府制定，会不时更改。',
}}
T['zh-TW'] = {k: _cc(v) for k, v in T['zh-CN'].items()}
T.update(json.load(open(os.path.join(HERE, 'i18n', 'foreign.json'), encoding='utf-8')))  # ms, ja, ko

# calculator links and WhatsApp buttons with a short description: key -> [en, zh-CN, ms, ja, ko]
NEW = {
    'co1l': ['Work out stamp duty and legal fees →', '计算印花税和律师费 →', 'Kira duti setem dan yuran guaman →', '印紙税と弁護士費用を計算する →', '인지세와 변호사 비용 계산하기 →'],
    'co_cal': ['All free calculators: loan, stamp duty, rental yield, RPGT', '全部免费计算器：房贷、印花税、租金回报、RPGT', 'Semua kalkulator percuma: pinjaman, duti setem, hasil sewa, RPGT', '無料計算ツール一覧：ローン、印紙税、利回り、RPGT', '모든 무료 계산기: 대출, 인지세, 임대 수익률, RPGT'],
    'w1d': ['Found a unit you like? Send Keith the project name and he will confirm the minimum price and whether it is open to foreign buyers.',
            '看中一个单位？把项目名字发给 Keith，他会确认门槛，以及这个单位是否开放给外国买家。',
            'Jumpa unit yang anda suka? Hantar nama projek kepada Keith dan dia akan mengesahkan harga minimum serta sama ada ia dibuka kepada pembeli asing.',
            '気になる住戸がありますか？物件名を Keith に送れば、最低価格と外国人が購入できるかを確認します。',
            '마음에 드는 세대가 있나요? 프로젝트 이름을 Keith에게 보내면 최저 가격과 외국인 구매 가능 여부를 확인해 드립니다.'],
    'w1b': ['Check a unit with Keith', '请 Keith 查单位', 'Semak unit dengan Keith', 'Keith に住戸を確認', 'Keith에게 세대 확인'],
    'w2d': ['Keith can prepare a full cost sheet for the unit you like: price, 8% stamp duty, legal fees, loan costs and the first year of maintenance.',
            'Keith 可以为你看中的单位准备一份完整的费用表：房价、8% 印花税、律师费、贷款费用和第一年的管理费。',
            'Keith boleh menyediakan helaian kos penuh untuk unit pilihan anda: harga, duti setem 8%, yuran guaman, kos pinjaman dan penyelenggaraan tahun pertama.',
            'Keith が気になる住戸の費用明細を作成します：価格、8% の印紙税、弁護士費用、ローン費用、初年度の管理費。',
            'Keith가 마음에 드는 세대의 전체 비용표를 만들어 드립니다: 가격, 8% 인지세, 변호사 비용, 대출 비용, 첫해 관리비.'],
    'w2b': ['Get my full cost sheet', '索取完整费用表', 'Dapatkan helaian kos penuh', '費用明細をもらう', '전체 비용표 받기'],
    'w3d': ['Buying from overseas? Keith arranges video viewings and works with lawyers and bankers who handle foreign buyers.',
            '人在国外？Keith 可以安排视频看房，并配合熟悉外国买家的律师和银行。',
            'Membeli dari luar negara? Keith mengatur tontonan video dan bekerjasama dengan peguam serta pegawai bank yang mengendalikan pembeli asing.',
            '海外から購入しますか？Keith がビデオ見学を手配し、外国人購入者に慣れた弁護士や銀行と連携します。',
            '해외에서 구매하시나요? Keith가 영상 방문을 준비하고 외국인 구매자를 담당하는 변호사, 은행과 함께 진행합니다.'],
    'w3b': ['Book a video viewing', '预约视频看房', 'Tempah tontonan video', 'ビデオ見学を予約', '영상 방문 예약'],
    'w4d': ['Planning MM2H and a home together? Keith checks both minimum prices, the MM2H tier and the state, before you shortlist.',
            '想同时申请 MM2H 和买房？Keith 会在你挑项目前，先帮你核对 MM2H 等级和州属两个门槛。',
            'Merancang MM2H dan rumah serentak? Keith menyemak kedua-dua harga minimum, peringkat MM2H dan negeri, sebelum anda membuat senarai pendek.',
            'MM2H と住宅購入を一緒に考えていますか？候補を絞る前に、Keith が MM2H ランクと州の2つの最低価格を確認します。',
            'MM2H와 주택 구매를 함께 계획하시나요? 후보를 고르기 전에 Keith가 MM2H 등급과 주의 두 가지 최저 가격을 확인해 드립니다.'],
    'w4b': ['Ask about MM2H and property', '咨询 MM2H 和买房', 'Tanya tentang MM2H dan hartanah', 'MM2H と不動産について相談', 'MM2H와 부동산 문의'],
}
NEW.update({
    'bs_eb': ['Foreign buyer best choice', '外国买家精选', 'Pilihan terbaik pembeli asing', '外国人購入者向けおすすめ', '외국인 구매자 추천'],
    'bs_h': ["Keith's best choices for foreign buyers", 'Keith 为外国买家精选的项目', 'Pilihan terbaik Keith untuk pembeli asing', 'Keith が選ぶ外国人購入者向け物件', 'Keith가 고른 외국인 구매자 추천 프로젝트'],
    'bs_p': ['Picked by Keith in the addresses foreign buyers ask about most: KL City Centre, Bukit Bintang, TRX, Damansara Heights and Petaling Jaya. Keith confirms which units meet the minimum price before you book.',
             'Keith 在外国买家最常问的地点挑选：KL City Centre、Bukit Bintang、TRX、Damansara Heights 和 Petaling Jaya。下订前 Keith 会确认哪些单位达到门槛。',
             'Dipilih oleh Keith di lokasi yang paling kerap ditanya pembeli asing: KL City Centre, Bukit Bintang, TRX, Damansara Heights dan Petaling Jaya. Keith mengesahkan unit mana yang mencapai harga minimum sebelum anda menempah.',
             '外国人購入者から特に質問の多いエリア（KL City Centre、Bukit Bintang、TRX、Damansara Heights、Petaling Jaya）から Keith が選びました。予約前に、最低価格を満たす住戸を Keith が確認します。',
             '외국인 구매자가 가장 많이 묻는 지역(KL City Centre, Bukit Bintang, TRX, Damansara Heights, Petaling Jaya)에서 Keith가 골랐습니다. 예약 전에 최저 가격을 충족하는 세대를 Keith가 확인해 드립니다.'],
    'pj_from': ['From', '起价', 'Dari', '価格', '분양가'],
    'bs_por': ['Price on request', '价格请询问', 'Harga atas permintaan', '価格はお問い合わせ', '가격 문의'],
    'bs_landed': ['ParkHomes (landed) from', 'ParkHomes 有地住宅起价', 'ParkHomes (atas tanah) dari', 'ParkHomes（土地付き）', 'ParkHomes(단독) 최저'],
    'w5d': ['Want the latest prices and available units for these projects? Keith sends you the price list and the units open to foreign buyers.',
            '想知道这些项目的最新价格和剩余单位？Keith 会把价格表和开放给外国买家的单位发给你。',
            'Mahu harga terkini dan unit yang masih ada untuk projek ini? Keith menghantar senarai harga dan unit yang dibuka kepada pembeli asing.',
            'これらの物件の最新価格と空き住戸を知りたいですか？Keith が価格表と外国人が購入できる住戸をお送りします。',
            '이 프로젝트들의 최신 가격과 남은 세대가 궁금하신가요? Keith가 가격표와 외국인에게 열린 세대를 보내 드립니다.'],
    'w5b': ['Get prices for these projects', '索取这些项目的价格', 'Dapatkan harga projek ini', 'これらの物件の価格をもらう', '이 프로젝트 가격 받기'],
})
for _k, _v in NEW.items():
    for _l, _s in zip(['en', 'zh-CN', 'ms', 'ja', 'ko'], _v):
        T[_l][_k] = _s
    T['zh-TW'][_k] = _cc(_v[1])
for l in LANGS:   # languages not translated yet show English
    T.setdefault(l, T['en'])
en = T['en']


def r(k, tag='span', cls=''):
    return '<%s%s data-r="%s">%s</%s>' % (tag, (' class="%s"' % cls) if cls else '', k, E(en[k]), tag)


def money(v):
    return 'RM%s' % format(int(v), ',') if v else None


SV = lambda s: s and '<svg viewBox="0 0 24 24">%s</svg>' % s
IC = {'f1': '<path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>', 'f2': '<path d="M4 19h16M7 16V9m5 7V5m5 11v-4"/>',
      'f3': '<path d="M6 3h9l3 3v15H6z"/><path d="M9 12h6M9 16h6M9 8h3"/>', 'f4': '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>'}
facts = ''.join('<div class="fx"><i>%s</i><div>%s%s</div></div>' % (SV(IC[f]), r(f + 't', 'b'), r(f + 'd', 'p')) for f in ['f1', 'f2', 'f3', 'f4'])

pills = ''.join('<button type="button" class="pl%s" data-k="%s">%s</button>' % (' on' if i == 0 else '', k, r('s_' + k)) for i, (k, *_) in enumerate(CHECK))
CK = {k: {'s': money(s), 'l': money(l), 'n': COUNT[k]} for k, _, _, s, l in CHECK}
k0 = CHECK[0][0]
LANDED_S = ['kl', 'sel']   # these states: the landed minimum is for strata-titled landed homes
wa_state = {k: waq("Hi Keith, I am a foreign buyer looking at %s. Which units meet the minimum price?" % T['en']['s_' + k]) for k, *_ in CHECK}
ask = r('ck_ask')
card = ('<div class="ck-card"><h3 id="ckName">%s</h3><p class="ck-n" id="ckNote" data-r="n_%s">%s</p><dl>'
        '<div><dt>%s</dt><dd id="ckS">%s</dd></div><div><dt>%s</dt><dd id="ckL">%s</dd></div>'
        '<div><dt>%s</dt><dd>%s</dd></div><div><dt>%s</dt><dd>%s</dd></div></dl>'
        '<a class="ck-go" id="ckGo" href="%s" target="_blank" rel="noopener" data-r="ck_go">%s</a></div>') % (
    E(en['s_' + k0]), k0, E(en['n_' + k0]), r('ck_strata'), CK[k0]['s'] or ask, '<span id="ckLl" data-r="%s">%s</span>' % (('ck_landed_s', E(en['ck_landed_s'])) if k0 in LANDED_S else ('ck_landed', E(en['ck_landed']))), CK[k0]['l'] or ask,
    r('ck_stamp'), r('ck_stamp_v'), r('ck_consent'), r('ck_consent_v'), E(wa_state[k0]), E(en['ck_go']))


def pcard(k, v, i):
    p = A.P[i]
    st, area = A.PLACES[i]
    href = 'property/%s.html' % A.SLUG.get(i, A.slug(p['name']))
    img = ('<img src="%s" alt="%s" loading="lazy">' % (E(A.PHOTO[i]), E(p['name']))) if A.PHOTO.get(i) else '<i class="noimg"></i>'
    ten = 'fh' if (p.get('tenure') or '').lower().startswith('freehold') else 'lh'
    return ('<a class="pc" data-k="%s" href="%s"><span class="pc-i">%s<em data-r="%s">%s</em></span><span class="pc-b"><b>%s</b><small>%s, %s</small>'
            '<span class="pc-p"><span data-r="pj_from">%s</span> %s</span></span></a>') % (
        k, href, img, ten, E(en[ten]), E(p['name']), E(area), E(st), E(en['pj_from']), SH.price_tag(money(v), int(v)))


grid = ''.join(pcard(*x) for x in OK)

# ---------- Keith's best choices for foreign buyers (FB_BEST=0 hides the section) ----------
SHOW_BEST = os.environ.get('FB_BEST', '1') == '1'
BEST = [('KL City Centre', ['Clouthaus', 'The Conlay', 'MABA Suitez']),
        ('Bukit Bintang', ['Pavilion Square', 'Orion Residence']),
        ('TRX', ['Golden Crown Residence']),
        ('Damansara Heights', ['Imperial Residence Pavilion Damansara Heights', 'Royal Suites Pavilion Damansara Heights']),
        ('Petaling Jaya', ['Zenia @ ParkCity Damansara'])]
_IDX = {p['name']: i for i, p in enumerate(A.P)}


def bcard(name, area):
    i = _IDX[name]
    p = A.P[i]
    href = 'property/%s.html' % A.SLUG.get(i, A.slug(p['name']))
    img = ('<img src="%s" alt="%s" loading="lazy">' % (E(A.PHOTO[i]), E(p['name']))) if A.PHOTO.get(i) else '<i class="noimg"></i>'
    ten = 'fh' if (p.get('tenure') or '').lower().startswith('freehold') else 'lh'
    ps = prices(p['price'])
    if name.startswith('Zenia'):   # Keith picked the landed ParkHomes
        price = '<span data-r="bs_landed">%s</span> %s' % (E(en['bs_landed']), SH.price_tag('RM2,500,000', 2500000))
    elif ps:
        price = '<span data-r="pj_from">%s</span> %s' % (E(en['pj_from']), SH.price_tag(money(min(ps)), int(min(ps))))
    else:
        price = '<span data-r="bs_por">%s</span>' % E(en['bs_por'])
    return ('<a class="pc" href="%s"><span class="pc-i">%s<em data-r="%s">%s</em></span><span class="pc-b"><i class="bs-a">%s</i><b>%s</b><small>%s</small>'
            '<span class="pc-p">%s</span></span></a>') % (href, img, ten, E(en[ten]), E(area), E(p['name']), E(p.get('size') or ''), price)


best = '<div class="pg bs-pg">%s</div>' % ''.join(bcard(n, a) for a, names in BEST for n in names)
more = ''.join('<a class="chip" data-k="%s" href="property/%s.html">%s<em>%s</em></a>' % (
    k, A.SLUG.get(i, A.slug(A.P[i]['name'])), E(A.P[i]['name']), E(A.PLACES[i][1])) for k, v, i in LARGER)
fpills = '<button type="button" class="pl on" data-f="all">%s</button>' % r('pj_all') + ''.join(
    '<button type="button" class="pl" data-f="%s">%s <em>%d</em></button>' % (k, r('s_' + k), COUNT[k]) for k, *_ in CHECK if COUNT[k])

RPGT_LINK = '<a class="co-a" href="calculator.html?tab=rpgt#rpgt_table" data-r="co4l">%s</a>' % E(en['co4l'])
COST_LINK = '<a class="co-a" href="calculator.html?tab=cost" data-r="co1l">%s</a>' % E(en['co1l'])
costs = ''.join('<div class="co"><b data-r="co%dt">%s</b><p data-r="co%dd">%s</p>%s</div>' % (n, E(en['co%dt' % n]), n, E(en['co%dd' % n]), {1: COST_LINK, 4: RPGT_LINK}.get(n, '')) for n in range(1, 5))
WAQ = {1: 'Hi Keith, I am a foreign buyer. Can you check if this unit meets the minimum price: ',
       2: 'Hi Keith, I am a foreign buyer. Please send me a full cost sheet for the unit I like.',
       3: 'Hi Keith, I am buying from overseas. Can we book a video viewing?',
       4: 'Hi Keith, I am planning MM2H and buying a home. Can you check both minimum prices for me?',
       5: "Hi Keith, I am a foreign buyer. Please send me the latest prices and available units for your best choices for foreign buyers."}
def wcta(n):
    return ('<div class="wcta"><p data-r="w%dd">%s</p><a class="bt bt-w" href="%s" target="_blank" rel="noopener" data-cta="fb%d">%s<span data-r="w%db">%s</span></a></div>'
            % (n, E(en['w%dd' % n]), E(waq(WAQ[n])), n, CHAT, n, E(en['w%db' % n])))
steps = ''.join('<li><span>%d</span><div><b data-r="st%dt">%s</b><p data-r="st%dd">%s</p></div></li>' % (n, n, E(en['st%dt' % n]), n, E(en['st%dd' % n])) for n in range(1, 7))
TIERS = [('Silver', '#8e9aaf', 'USD 150,000', 'RM 600,000', 'mm_y5'), ('Gold', '#c9a227', 'USD 500,000', 'RM 1,000,000', 'mm_y15'),
         ('Platinum', '#5E60CE', 'USD 1,000,000', 'RM 2,000,000', 'mm_y20')]
tiers = ''.join('<div class="mt" style="--tc:%s"><b>%s</b><dl><dt>%s</dt><dd>%s</dd><dt>%s</dt><dd>%s</dd><dt>%s</dt><dd>%s</dd></dl></div>' % (
    c, n, r('mm_fd'), fd, r('mm_pp'), pp, r('mm_vd'), r(y)) for n, c, fd, pp, y in TIERS)
faq = ''.join('<details><summary data-r="q%d">%s</summary><p data-r="a%d">%s</p></details>' % (n, E(en['q%d' % n]), n, E(en['a%d' % n])) for n in range(1, 9))
FAQ_LD = json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
    {'@type': 'Question', 'name': en['q%d' % n], 'acceptedAnswer': {'@type': 'Answer', 'text': en['a%d' % n]}} for n in range(1, 9)]}, ensure_ascii=False)
CHAT = svg_wa = '<svg viewBox="0 0 24 24"><path d="M20.5 3.5A11 11 0 0 0 3.2 17.1L2 22l5-1.3A11 11 0 1 0 20.5 3.5z"/></svg>'
wa_main = waq('Hi Keith, I am a foreign buyer. Can you check which projects I can buy?')

CSS = '''
:root{--bg:#F9F8F6;--ink:#111;--grey:#5A5A5A;--line:rgba(17,17,17,0.08);--gold:#5E60CE;--deep:#1d1b4f;--soft:#f3f1fa;}
*{box-sizing:border-box;margin:0;padding:0;} body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6;}
a{color:inherit;text-decoration:none;} img{display:block;max-width:100%;} button{font:inherit;}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif;line-height:1.25;}
.wrap{max-width:1180px;margin:0 auto;padding:0 5vw;}
.eb{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);font-weight:700;display:block;}
.fh{padding:64px 0 30px;} .fh h1{font-size:clamp(32px,5vw,54px);margin:8px 0 14px;max-width:900px;} .fh .lead{font-size:19px;font-weight:700;margin-bottom:6px;} .fh p{color:var(--grey);max-width:800px;font-size:15.5px;}
.btns{display:flex;gap:12px;flex-wrap:wrap;margin-top:24px;} .bt{display:inline-flex;align-items:center;gap:8px;padding:13px 24px;border-radius:100px;font-weight:700;font-size:14.5px;transition:transform .2s,background .2s;}
.bt:hover{transform:translateY(-2px);} .bt-p{background:var(--gold);color:#fff;} .bt-p:hover{background:var(--deep);} .bt-w{background:#25d366;color:#fff;} .bt svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;}
.fxs{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding:10px 0 50px;} .fx{background:#fff;border:1px solid var(--line);border-radius:18px;padding:20px;display:flex;flex-direction:column;gap:10px;}
.fx i{width:40px;height:40px;border-radius:11px;background:var(--soft);display:flex;align-items:center;justify-content:center;} .fx svg{width:20px;height:20px;fill:none;stroke:var(--gold);stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;}
.fx b{font-size:16px;font-weight:800;display:block;} .fx p{font-size:13.5px;color:var(--grey);}
.sec{padding:56px 0;} .sec h2{font-size:clamp(26px,3.6vw,38px);margin:6px 0 10px;} .sec>p,.sec .sp{color:var(--grey);max-width:780px;font-size:15px;}
.ck{background:linear-gradient(160deg,#1d1b4f,#2b2973 70%,#3b3c99);color:#fff;border-radius:28px;padding:48px 44px;margin:10px 0;}
.ck .eb{color:#b9b4ff;} .ck h2{color:#fff;} .ck .sp{color:rgba(255,255,255,.75);}
.pls{display:flex;flex-wrap:wrap;gap:10px;margin:24px 0;} .pl{all:unset;cursor:pointer;padding:10px 18px;border-radius:100px;font-weight:700;font-size:14px;border:1px solid rgba(255,255,255,.25);color:#fff;transition:background .2s;}
.pl:hover{background:rgba(255,255,255,.1);} .pl.on{background:#fff;color:var(--deep);border-color:#fff;} .pl em{font-style:normal;opacity:.6;margin-left:4px;font-size:12.5px;}
.ck-card{background:#fff;color:var(--ink);border-radius:20px;padding:28px;} .ck-card h3{font-size:28px;} .ck-n{color:var(--grey);font-size:14.5px;margin:6px 0 18px;}
.ck-card dl{display:grid;grid-template-columns:1fr 1fr;gap:12px;} .ck-card dl>div{background:var(--soft);border-radius:14px;padding:16px 18px;}
.ck-card dt{font-size:12.5px;color:var(--grey);font-weight:600;} .ck-card dd{font-size:24px;font-weight:800;color:var(--deep);margin-top:2px;}
.ck-go{display:inline-block;margin-top:18px;font-weight:700;color:var(--gold);} .ck-go:hover{text-decoration:underline;}
.ck small{display:block;margin-top:16px;font-size:12px;color:rgba(255,255,255,.65);max-width:900px;}
.fp .pl{border-color:var(--line);color:var(--ink);background:#fff;} .fp .pl.on{background:var(--gold);color:#fff;border-color:var(--gold);}
.pg{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px;} .pc{background:#fff;border:1px solid var(--line);border-radius:18px;overflow:hidden;transition:transform .25s,box-shadow .25s;display:flex;flex-direction:column;}
.pc:hover{transform:translateY(-3px);box-shadow:0 16px 36px rgba(29,27,79,.12);} .pc-i{position:relative;display:block;aspect-ratio:4/3;overflow:hidden;background:var(--soft);} .pc-i img{position:absolute;inset:0;width:100%!important;height:100%!important;max-width:none;object-fit:cover;}
.pc-i em{z-index:1;position:absolute;left:10px;top:10px;background:rgba(29,27,79,.85);color:#fff;font-style:normal;font-size:11px;font-weight:700;padding:4px 9px;border-radius:100px;}
.pc-b{padding:14px 16px 16px;display:flex;flex-direction:column;gap:2px;} .pc-b b{font-size:15.5px;line-height:1.3;} .pc-b small{color:var(--grey);font-size:12.5px;} .pc-p{margin-top:6px;font-weight:800;color:var(--gold);font-size:14.5px;}
.noimg{display:block;width:100%;height:100%;}
.more{margin-top:30px;background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px;} .more b{font-size:16px;} .more p{font-size:13.5px;color:var(--grey);margin:4px 0 12px;}
.chips{display:flex;flex-wrap:wrap;gap:8px;} .chip{border:1px solid var(--line);border-radius:100px;padding:7px 14px;font-size:13.5px;font-weight:600;} .chip:hover{border-color:var(--gold);color:var(--gold);} .chip em{font-style:normal;color:var(--grey);font-weight:400;margin-left:6px;font-size:12px;}
.note{font-size:12.5px;color:var(--grey);margin-top:14px;}
.cos{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-top:22px;} .co{background:#fff;border:1px solid var(--line);border-left:4px solid var(--gold);border-radius:14px;padding:20px 22px;} .co b{font-size:16.5px;} .co-a{display:inline-block;margin-top:8px;font-size:13.5px;font-weight:700;color:var(--gold);} .co-a:hover{text-decoration:underline;} .co p{color:var(--grey);font-size:14px;margin-top:4px;}
.steps{list-style:none;display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:22px;} .steps li{background:#fff;border:1px solid var(--line);border-radius:16px;padding:20px;display:flex;gap:14px;}
.steps span{flex:0 0 36px;height:36px;border-radius:50%;background:var(--gold);color:#fff;font-weight:800;display:flex;align-items:center;justify-content:center;} .steps b{font-size:16px;} .steps p{color:var(--grey);font-size:13.5px;margin-top:2px;}
.mm{background:#fff;border:1px solid var(--line);border-radius:28px;padding:44px;display:grid;grid-template-columns:1fr 1.1fr;gap:40px;align-items:center;}
.mm-logo{font-family:'Playfair Display',serif;font-size:58px;font-weight:700;color:var(--deep);line-height:1;} .mm p{color:var(--grey);font-size:15px;margin:10px 0 18px;}
.mm-l{display:flex;flex-direction:column;gap:8px;} .mm-l a{font-weight:700;color:var(--gold);} .mm-l a:hover{text-decoration:underline;}
.mts{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;} .mt{background:var(--soft);border-top:4px solid var(--tc);border-radius:14px;padding:18px 16px;} .mt>b{font-family:'Playfair Display',serif;font-size:21px;display:block;margin-bottom:8px;}
.mt dt{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--grey);margin-top:8px;} .mt dd{font-weight:800;font-size:15px;}
.faq{margin-top:20px;display:flex;flex-direction:column;gap:10px;max-width:900px;} .faq details{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 20px;}
.faq summary{font-weight:700;font-size:16px;cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:12px;} .faq summary:after{content:"+";color:var(--gold);font-size:22px;line-height:1;} .faq details[open] summary:after{content:"\\2212";}
.faq p{color:var(--grey);font-size:14.5px;margin-top:10px;}
.co-all{display:flex;align-items:center;gap:14px;margin-top:18px;padding:16px 20px;background:linear-gradient(135deg,#5E60CE,#7b7de0);color:#fff;border-radius:16px;font-weight:700;font-size:15.5px;box-shadow:0 10px 26px rgba(94,96,206,.28);transition:transform .2s,box-shadow .2s;}.co-all:hover{transform:translateY(-2px);box-shadow:0 16px 34px rgba(94,96,206,.38);} .co-all span{flex:1;}.co-all i{flex:0 0 44px;height:44px;border-radius:12px;background:rgba(255,255,255,.18);display:flex;align-items:center;justify-content:center;}.co-all svg{width:22px;height:22px;fill:none;stroke:#fff;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;} .co-all .co-ar{flex:0 0 22px;transition:transform .2s;} .co-all:hover .co-ar{transform:translateX(4px);}.wcta{display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap;background:#fff;border:1px solid rgba(37,211,102,.35);border-left:4px solid #25d366;border-radius:16px;padding:18px 22px;margin-top:22px;}.wcta p{flex:1 1 320px;color:var(--ink);font-size:14.5px;font-weight:500;margin:0;} .wcta .bt{flex:0 0 auto;}.bs-g{margin-top:28px;} .bs-g h3{font-family:'Inter',sans-serif;font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);font-weight:800;margin-bottom:12px;display:flex;align-items:center;gap:10px;} .bs-g h3:after{content:'';flex:1;height:1px;background:var(--line);} .bs-pg{grid-template-columns:repeat(3,minmax(0,1fr));margin-top:24px;} .bs-a{font-style:normal;font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);} @media(max-width:640px){.bs-pg{grid-template-columns:1fr 1fr;}}.cta{background:var(--deep);color:#fff;border-radius:28px;padding:44px;text-align:center;margin:20px 0 30px;} .cta h2{color:#fff;} .cta p{color:rgba(255,255,255,.75);max-width:640px;margin:8px auto 20px;}
.disc{font-size:12px;color:var(--grey);padding-bottom:60px;max-width:900px;}
footer{border-top:1px solid var(--line);padding:26px 5vw;font-size:13px;color:var(--grey);text-align:center;}
@media(max-width:980px){.fxs{grid-template-columns:repeat(2,1fr);} .pg{grid-template-columns:repeat(2,minmax(0,1fr));} .steps{grid-template-columns:1fr 1fr;} .mm{grid-template-columns:1fr;}}
@media(max-width:640px){.fh{padding:40px 0 20px;} .fxs{grid-template-columns:1fr 1fr;gap:10px;} .fx{padding:14px;} .fx p{font-size:12.5px;}
 .ck{padding:30px 18px;border-radius:22px;} .ck-card{padding:20px;} .ck-card dl{grid-template-columns:1fr;} .ck-card dd{font-size:21px;}
 .pg{gap:12px;} .pc-b{padding:10px 12px 12px;} .pc-b b{font-size:14px;} .cos,.steps{grid-template-columns:1fr;} .mm{padding:26px 20px;} .mts{grid-template-columns:1fr;} .mm-logo{font-size:46px;} .cta{padding:32px 20px;} .sec{padding:40px 0;}}
'''

JS = '''<script>(function(){var T=%s,CK=%s,WA=%s,LS=%s;
function lang(){var l='en';try{l=localStorage.getItem('kn_lang')||'en'}catch(e){}return T[l]?l:'en';}
var cur='%s';
function show(){var L=T[lang()],c=CK[cur];document.getElementById('ckName').textContent=L['s_'+cur];var n=document.getElementById('ckNote');n.setAttribute('data-r','n_'+cur);n.textContent=L['n_'+cur];
var ll=document.getElementById('ckLl'),lk=LS.indexOf(cur)>-1?'ck_landed_s':'ck_landed';ll.setAttribute('data-r',lk);ll.textContent=L[lk];document.getElementById('ckS').textContent=c.s||L.ck_ask;document.getElementById('ckL').textContent=c.l||L.ck_ask;
document.getElementById('ckGo').href=WA[cur];}
function apply(){var L=T[lang()];document.querySelectorAll('[data-r]').forEach(function(el){var v=L[el.getAttribute('data-r')];if(v)el.textContent=v;});show();
document.title=L.title+' | Keith Nah';}
function filt(k){document.querySelectorAll('.fp .pl').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-f')===k);});
document.querySelectorAll('.pc[data-k],.chip[data-k]').forEach(function(a){a.style.display=(k==='all'||a.getAttribute('data-k')===k)?'':'none';});
var m=document.querySelector('.more');if(m)m.style.display=(k==='all'||m.querySelector('.chip[data-k="'+k+'"]'))?'':'none';}
document.addEventListener('click',function(e){var p=e.target.closest('.ck .pl');if(p){cur=p.getAttribute('data-k');document.querySelectorAll('.ck .pl').forEach(function(b){b.classList.toggle('on',b===p);});show();return;}
var f=e.target.closest('.fp .pl');if(f){filt(f.getAttribute('data-f'));return;}
});
document.addEventListener('DOMContentLoaded',function(){var s=window.knSetLang;if(typeof s==='function')window.knSetLang=function(){var r=s.apply(this,arguments);apply();return r;};apply();});
apply();})();</script>''' % (json.dumps(T, ensure_ascii=False), json.dumps(CK), json.dumps(wa_state), json.dumps(LANDED_S), k0)

desc = 'Can foreigners buy property in Malaysia? Minimum prices by state, 8% stamp duty, state consent, costs, MM2H and how buying works.'
page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Buying Property in Malaysia as a Foreigner | Keith Nah</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{site}/foreign-buyers.html">
<meta property="og:title" content="Buying Property in Malaysia as a Foreigner | Keith Nah"><meta property="og:description" content="{desc}"><meta property="og:url" content="{site}/foreign-buyers.html"><meta property="og:image" content="{site}/images/res/area-guides.jpg">
<link rel="icon" type="image/png" href="images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{faqld}</script>
<style>{css}</style>
</head>
<body>
<header>
  <a class="logo" href="./"><img src="images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Malaysia Real Estate</small></span></a>
  <nav></nav>
  <a class="wa-btn" href="{wa}" target="_blank" rel="noopener">WhatsApp Keith</a>
</header>
<main class="wrap">
  <section class="fh">{eb}<h1 data-r="title">{title}</h1>{lead}{sub}
    <div class="btns"><a class="bt bt-p" href="#check">{bcheck}</a><a class="bt bt-w" href="{wa}" target="_blank" rel="noopener">{chat}{bwa}</a></div></section>
  <section class="fxs">{facts}</section>
  <section class="ck" id="check">{ckeb}<h2 data-r="ck_h">{ckh}</h2>{ckp}<div class="pls">{pills}</div>{card}{cknote}</section>
  {w1}
  <section class="sec" id="costs">{coeb}<h2 data-r="co_h">{coh}</h2><div class="cos">{costs}</div>{conote}<a class="co-all" href="calculator.html"><i><svg viewBox="0 0 24 24"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 11h2M12 11h2M16 11h0M8 15h2M12 15h2M8 18h2M12 18h2M16 15v3"/></svg></i><span data-r="co_cal">{cocal}</span><svg class="co-ar" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>{w2}</section>
  <section class="sec" id="steps">{steb}<h2 data-r="st_h">{sth}</h2><ol class="steps">{steps}</ol>{w3}</section>
  {bestsec}
  <section class="sec" id="mm2h"><div class="mm"><div><div class="mm-logo">MM2H</div>{mmeb}<h2 data-r="mm_h">{mmh}</h2>{mmp}
    <div class="mm-l"><a href="mm2h.html">{mmbtn} &rarr;</a><a href="mm2h/mm2h-property-rules-foreign-buyers.html">{mmlib} &rarr;</a><a href="mm2h.html#library">{mmlib2} &rarr;</a></div></div>
    <div class="mts">{tiers}</div></div></section>
  <div class="wrap0">{w4}</div>
  <section class="sec" id="faq">{fqeb}<h2 data-r="fq_h">{fqh}</h2><div class="faq">{faq}</div></section>
  <section class="cta"><h2 data-r="cta_h">{ctah}</h2>{ctap}<a class="bt bt-w" href="{wa}" target="_blank" rel="noopener">{chat}{bwa}</a></section>
  {disc}
</main>
<footer>&copy; 2026 Keith Nah Real Estate. All rights reserved.</footer>
<script src="lead-tracker.js"></script>
{js}
</body>
</html>
'''.format(desc=E(desc), site=SITE, faqld=FAQ_LD, css=CSS, wa=E(wa_main), chat=CHAT, eb=r('eyebrow', 'span', 'eb'), title=E(en['title']),
           lead=r('lead', 'p', 'lead'), sub=r('sub', 'p'), bcheck=r('b_check'), bwa=r('b_wa'), facts=facts,
           ckeb=r('ck_eb', 'span', 'eb'), ckh=E(en['ck_h']), ckp=r('ck_p', 'p', 'sp'), pills=pills, card=card, cknote=r('ck_note', 'small'),
           pjeb=r('pj_eb', 'span', 'eb'), pjh=E(en['pj_h']), pjp=r('pj_p', 'p', 'sp'), fpills=fpills, grid=grid,
           more=('<div class="more">%s%s<div class="chips">%s</div></div>' % (r('pj_more', 'b'), r('pj_more_p', 'p'), more)) if more else '',
           pjnote=r('pj_note', 'p', 'note'), w1=wcta(1), w2=wcta(2), w3=wcta(3), w4=wcta(4), bestsec=('<section class="sec" id="best">%s<h2 data-r="bs_h">%s</h2>%s%s%s</section>' % (r('bs_eb', 'span', 'eb'), E(en['bs_h']), r('bs_p', 'p', 'sp'), best, wcta(5))) if SHOW_BEST else '', cocal=E(en['co_cal']), coeb=r('co_eb', 'span', 'eb'), coh=E(en['co_h']), costs=costs, conote=r('co_note', 'p', 'note'),
           steb=r('st_eb', 'span', 'eb'), sth=E(en['st_h']), steps=steps, mmeb=r('mm_eb', 'span', 'eb'), mmh=E(en['mm_h']), mmp=r('mm_p', 'p'),
           mmbtn=r('mm_btn'), mmlib=r('mm_lib'), mmlib2=r('mm_lib2'), tiers=tiers, fqeb=r('fq_eb', 'span', 'eb'), fqh=E(en['fq_h']), faq=faq,
           ctah=E(en['cta_h']), ctap=r('cta_p', 'p'), disc=r('disc', 'p', 'disc'), js=JS)
open(os.environ.get('FB_OUT', 'foreign-buyers.html'), 'w', encoding='utf-8').write(SH.apply(page, '', 'foreign-buyers.html'))

if os.path.exists('sitemap.xml') and not os.environ.get('FB_OUT'):
    sm = open('sitemap.xml', encoding='utf-8').read()
    if '/foreign-buyers.html<' not in sm:
        import datetime as _dt
        sm = sm.replace('</urlset>', '  <url>\n    <loc>%s/foreign-buyers.html</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n</urlset>' % (
            SITE, _dt.date.today().isoformat()))
        open('sitemap.xml', 'w', encoding='utf-8').write(sm)
print('foreign-buyers: written')

# ---------- home page: "Foreign buyer best choice" sliding row in place of Featured Projects ----------
# Same motion as the Free Toolkit row (tools/build_resources.py): a seamless CSS marquee moving at the
# same speed (about 32 px a second), paused on hover. FB_HOME=1 writes it into index.html (or into
# FB_HOME_OUT for a preview copy); until Keith approves, the home page is left as it is.
HOME_T = {k: [T[l][k] for l in LANGS] for k in ('bs_eb', 'bs_h', 'fh', 'lh', 'pj_from', 'bs_por', 'bs_landed')}
HOME_T['hp'] = ['Picked by Keith in the addresses foreign buyers ask about most, from KL City Centre and TRX to Damansara Heights.',
                'Keith 在外国买家最常问的地点挑选，从 KL City Centre、TRX 到 Damansara Heights。',
                'Keith 在外國買家最常問的地點挑選，從 KL City Centre、TRX 到 Damansara Heights。',
                'Dipilih oleh Keith di lokasi yang paling kerap ditanya pembeli asing, dari KL City Centre dan TRX hingga Damansara Heights.',
                '外国人購入者から特に質問の多いエリアから Keith が選びました。KL City Centre、TRX から Damansara Heights まで。',
                '외국인 구매자가 가장 많이 묻는 지역에서 Keith가 골랐습니다. KL City Centre, TRX부터 Damansara Heights까지.']
HOME_T['all'] = ['See the Foreign Buyers guide →', '查看外国买家指南 →', '查看外國買家指南 →', 'Lihat panduan Pembeli Asing →', '外国人購入ガイドを見る →', '외국인 구매 가이드 보기 →']
HOME_T['view'] = ['View project', '查看项目', '查看項目', 'Lihat projek', '物件を見る', '프로젝트 보기']


def hcard(name, area):
    i = _IDX[name]
    p = A.P[i]
    ten = 'fh' if (p.get('tenure') or '').lower().startswith('freehold') else 'lh'
    ps = prices(p['price'])
    if name.startswith('Zenia'):
        price = '<span data-fbh="bs_landed">%s</span> %s' % (E(en['bs_landed']), SH.price_tag('RM2,500,000', 2500000))
    elif ps:
        price = '<span data-fbh="pj_from">%s</span> %s' % (E(en['pj_from']), SH.price_tag(money(min(ps)), int(min(ps))))
    else:
        price = '<span data-fbh="bs_por">%s</span>' % E(en['bs_por'])
    img = ('<img src="%s" alt="%s" loading="lazy">' % (E(A.PHOTO[i]), E(p['name']))) if A.PHOTO.get(i) else ''
    return ('<a class="fbh-c" href="property/%s.html"><span class="fbh-i">%s<i data-fbh="%s">%s</i></span><span class="fbh-b"><span class="fbh-a">%s</span>'
            '<b>%s</b><small>%s</small><span class="fbh-p">%s</span><em><span data-fbh="view">%s</span> &rarr;</em></span></a>') % (
        A.SLUG.get(i, A.slug(p['name'])), img, ten, E(en[ten]), E(area), E(p['name']), E(p.get('size') or ''), price, E(HOME_T['view'][0]))


hcards = ''.join(hcard(n, a) for a, names in BEST for n in names)
NB = sum(len(v) for _, v in BEST)
DUR = round(NB * 352 / 32)   # same speed as the Free Toolkit row: 5 cards of 330px + 22px gap in 55 s
HOME_HTML = ('<!-- KN-FB-HOME:START -->\n<style>'
             '#projects.fbh{padding:90px 0 80px;overflow:hidden}.fbh-h{max-width:1220px;margin:0 auto 30px;padding:0 5vw;display:flex;justify-content:space-between;align-items:end;gap:20px;flex-wrap:wrap}'
             '.fbh-h .eyebrow{display:block;margin-bottom:8px}.fbh-h h2{font-family:"Playfair Display",serif;font-size:clamp(28px,3.6vw,42px);line-height:1.15;margin:0}'
             '.fbh-h p{color:var(--grey,#5A5A5A);font-size:15px;margin-top:10px;max-width:640px}.fbh-h a{color:var(--gold,#5E60CE);font-weight:700;font-size:14.5px;text-decoration:none;white-space:nowrap}'
             '.fbh-v{overflow:hidden;-webkit-mask-image:linear-gradient(90deg,transparent,#000 4%%,#000 96%%,transparent);mask-image:linear-gradient(90deg,transparent,#000 4%%,#000 96%%,transparent)}'
             '.fbh-r{display:flex;gap:22px;width:max-content;padding:6px 0 18px;animation:fbhSlide %ds linear infinite}.fbh-v:hover .fbh-r,.fbh-v:focus-within .fbh-r{animation-play-state:paused}'
             '@keyframes fbhSlide{to{transform:translateX(calc(-50%% - 11px))}}'
             '.fbh-c{flex:0 0 330px;background:#fff;border-radius:22px;overflow:hidden;text-decoration:none;color:#15142b;box-shadow:0 14px 34px rgba(29,27,79,.09);border:1px solid rgba(21,20,43,.06);transition:transform .3s,box-shadow .3s}'
             '.fbh-c:hover{transform:translateY(-6px);box-shadow:0 22px 46px rgba(29,27,79,.16)}.fbh-i{position:relative;display:block;height:200px;background:#f3f1fa}'
             '.fbh-i img{display:block;width:100%%;height:100%%;object-fit:cover}.fbh-i i{position:absolute;left:12px;top:12px;background:rgba(29,27,79,.85);color:#fff;font-style:normal;font-size:11px;font-weight:700;padding:4px 10px;border-radius:99px}'
             '.fbh-b{display:flex;flex-direction:column;gap:4px;padding:16px 20px 20px}.fbh-a{font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--gold,#5E60CE)}'
             '.fbh-b b{font:700 19px/1.3 "Playfair Display",serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.fbh-b small{font-size:13px;color:#5f5e74}'
             '.fbh-p{font-weight:800;color:#15142b;font-size:15px;margin-top:6px}.fbh-b em{font-style:normal;font-weight:700;font-size:14px;color:var(--gold,#5E60CE);margin-top:6px}'
             '@media(max-width:600px){.fbh-c{flex-basis:270px}.fbh-i{height:160px}#projects.fbh{padding:64px 0 56px}}@media(prefers-reduced-motion:reduce){.fbh-r{animation:none}.fbh-v{overflow-x:auto}}'
             '</style>\n<section id="projects" class="fbh"><div class="fbh-h"><div><span class="eyebrow" data-fbh="bs_eb">%s</span><h2 data-fbh="bs_h">%s</h2><p data-fbh="hp">%s</p></div>'
             '<a href="foreign-buyers.html#best" data-fbh="all">%s</a></div><div class="fbh-v"><div class="fbh-r">%s%s</div></div></section>\n'
             '<script>(function(){var T=%s,LG=["en","zh-CN","zh-TW","ms","ja","ko"];function f(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}var i=Math.max(0,LG.indexOf(l));'
             'document.querySelectorAll("[data-fbh]").forEach(function(el){var v=T[el.getAttribute("data-fbh")];if(v)el.textContent=v[i];});}f();'
             'document.addEventListener("DOMContentLoaded",function(){["knSetLang","setLanguage"].forEach(function(n){var s=window[n];if(typeof s==="function")window[n]=function(){var r=s.apply(this,arguments);f();return r;};});f();});})();</script>\n'
             '<!-- KN-FB-HOME:END -->\n') % (
    DUR, E(en['bs_eb']), E(en['bs_h']), E(HOME_T['hp'][0]), E(HOME_T['all'][0]), hcards,
    hcards.replace('<a class="fbh-c"', '<a class="fbh-c" aria-hidden="true" tabindex="-1"'), json.dumps(HOME_T, ensure_ascii=False))

if os.environ.get('FB_HOME') == '1':
    ix = open('index.html', encoding='utf-8').read()
    if '<!-- KN-FB-HOME:START -->' in ix:
        ix = re.sub(r'<!-- KN-FB-HOME:START -->.*?<!-- KN-FB-HOME:END -->\n', lambda _: HOME_HTML, ix, flags=re.S)
    else:   # first run: the old Featured Projects slider goes
        a = ix.index('<!-- ===================== FEATURED PROJECTS ===================== -->')
        b = ix.index('</section>', ix.index('id="miniTrack"')) + len('</section>\n')
        ix = ix[:a] + HOME_HTML + ix[b:]
    open(os.environ.get('FB_HOME_OUT', 'index.html'), 'w', encoding='utf-8').write(ix)
    print('foreign-buyers: home best-choice row, %d projects, %ds loop' % (NB, DUR))
