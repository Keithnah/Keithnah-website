"""Content for the News page sections built by tools/build_news_page.py.

Edit the text here, then run:
    python3 tools/build_news_page.py

Figures follow the rules as at 2026. Check them again when a Budget or
state rule changes, and keep them in line with calculator.html.
"""

AS_AT = 'November 2026'

GUIDES = [
    {
        'id': 'new-property',
        'tab': 'Buying New Property',
        'tab_sub': 'New launches and under-construction projects bought from a developer',
        'title': 'Buying a new property in Malaysia',
        'short': ('A new launch follows a fixed legal route. You pay a booking fee, sign the developer\'s statutory '
                  'Sale and Purchase Agreement (SPA) with 10% paid, then your bank pays the developer in stages as '
                  'the building goes up. The developer must hand over within 36 months for a condo (24 months for '
                  'landed), or pay you late-delivery damages, and must fix defects for 24 months after handover.'),
        'numbers': [
            ('Sale and Purchase Agreement', 'Statutory form under the Housing Development Act: Schedule H for strata (condos), Schedule G for landed. The developer cannot change its terms against you.'),
            ('Paid when you sign the SPA', '10% of the price, including the booking fee you already paid'),
            ('Booking fee', 'Usually 2% to 3%, credited towards the 10%'),
            ('Handover deadline', '36 months for strata, 24 months for landed, counted from the SPA date'),
            ('Late delivery damages (LAD)', '10% a year of the purchase price, counted from the date you paid the booking fee'),
            ('Defect liability period', '24 months from vacant possession; the developer must repair within 30 days of your written notice'),
            ('Before you get the keys', 'A Certificate of Completion and Compliance (CCC), plus connected water and electricity'),
            ('If something goes wrong', 'The Tribunal for Homebuyer Claims hears claims of up to RM50,000 for a small filing fee'),
        ],
        'stages': [
            ('Shortlist and check', [
                'Check the developer\'s licence and advertising permit numbers, which must appear on every advertisement, on the housing ministry\'s website.',
                'Confirm the land title: residential, or commercial. Serviced apartments on commercial land usually pay commercial rates for utilities and assessment tax.',
                'Compare the price per sq ft and maintenance fee with completed projects nearby, and look up the developer\'s past projects and delivery record.',
                'Ask for the full price list, the rebates, and what is included: car parks, built-in fittings and legal fee promotions.',
            ]),
            ('Book and arrange the loan', [
                'Sign the booking form and pay the booking fee. Read the refund terms first: some developers keep part of the fee if you cancel.',
                'Apply to two or three banks at the same time. Banks look at your debt service ratio (monthly debts against income).',
                'Bank Negara caps the loan at 70% for your third and later home loans; first and second homes can usually go up to 90%.',
                'Prepare your IC or passport, latest salary slips or tax returns, and three to six months of bank statements.',
            ]),
            ('Sign the SPA and loan agreement', [
                'Sign the SPA within the time stated on your booking form, and pay the balance up to 10% of the price.',
                'Check the unit number, size, car park bays, payment schedule and delivery date in the SPA before you sign.',
                'Sign the loan agreement with the bank\'s lawyer. Loan stamp duty is 0.5% of the loan amount.',
                'Developers often pay the SPA legal fees in their promotions; the loan legal fees are usually yours.',
            ]),
            ('Pay in stages during construction', [
                'The developer bills by construction stage, as set out in the SPA payment schedule.',
                'Your bank releases each payment directly to the developer once the architect certifies the stage.',
                'You pay interest only on the amount released so far, so instalments start small and rise as the building goes up.',
                'Keep every progress bill and payment receipt: you will need them for the final stages and any claim.',
            ]),
            ('Vacant possession and handover', [
                'The developer sends a notice of vacant possession once the CCC is issued and water and electricity are connected.',
                'Pay the final amounts due, then collect your keys and the handover documents.',
                'Inspect the unit carefully on the day, photograph every defect and submit a written defects list.',
                'Maintenance fees, sinking fund, utilities and (once issued) assessment tax start from vacant possession.',
            ]),
            ('After you get the keys', [
                'For 24 months the developer must repair defects you report in writing, within 30 days of your notice.',
                'If they do not, you may repair it yourself after giving notice and claim the cost, or go to the Tribunal for Homebuyer Claims.',
                'For condos, the Joint Management Body runs the building until the strata titles are issued and the Management Corporation takes over.',
                'Claim late delivery damages if the handover came after the deadline in your SPA.',
            ]),
        ],
        'faq': [
            ('Do I get my booking fee back if I cancel?', 'It depends on the booking form. Before the SPA is signed, many developers refund the fee in full or keep a small administration charge. Read the cancellation terms before you pay, and keep the receipt.'),
            ('How much can I claim for late delivery?', 'Late delivery damages are 10% a year of the purchase price, counted from the date you paid the booking fee until vacant possession. For a RM800,000 condo delivered three months late, that is about RM20,000.'),
            ('How long is the defect liability period?', '24 months from vacant possession. Report defects in writing; the developer must repair them within 30 days of your notice.'),
            ('Where can I complain about a developer?', 'Start with a written complaint to the developer. If that fails, file a claim with the Tribunal for Homebuyer Claims (up to RM50,000) or complain to the housing ministry. Larger claims go to court.'),
            ('Should I buy a new launch or a subsale unit?', 'A new launch usually costs less upfront and you pay in stages, but you wait two to four years and rely on the developer. A subsale unit is ready now and you can inspect it, but you pay more upfront and take it as it is. Many investors like new launches for capital growth, and subsale units for immediate rental income.'),
        ],
    },
    {
        'id': 'subsale',
        'tab': 'Buying Subsale Property',
        'tab_sub': 'Completed homes bought from an existing owner',
        'title': 'Buying a subsale property in Malaysia',
        'short': ('A subsale is a completed home bought from its current owner. Most of the risk is settled before you '
                  'pay anything: check the title, the owner\'s arrears and the condition of the unit first. You then '
                  'pay an earnest deposit (usually 2% to 3%) to hold the unit, sign the SPA with 10% paid, and the '
                  'lawyers complete the sale in about three months.'),
        'numbers': [
            ('Earnest deposit', 'Usually 2% to 3% with your offer letter, topped up to 10% when you sign the SPA'),
            ('Completion period', 'Usually 3 months from the SPA (or from the date consent is given), plus a 1-month extension with late-payment interest, commonly 8% a year'),
            ('Stamp duty on transfer', 'Malaysians and PRs: 1% on the first RM100,000, 2% up to RM500,000, 3% up to RM1,000,000 and 4% above, on the higher of the price or market value. Foreigners: flat 8% on residential from 1 Jan 2026'),
            ('Stamp duty on the loan', '0.5% of the loan amount'),
            ('RPGT retention', 'Your lawyer holds back 3% of the price (7% if the seller is not a Malaysian citizen) and pays it to LHDN within 60 days'),
            ('State consent', 'Needed for leasehold titles or titles with a restriction in interest, and for foreign buyers; it can add weeks or months'),
            ('Agent commission', 'Up to 3% of the price, normally paid by the seller'),
            ('Check before you offer', 'Title search, caveats and charges, maintenance and assessment arrears, tenancy and the unit\'s condition'),
        ],
        'stages': [
            ('Check before you make an offer', [
                'Ask a lawyer for a land title search: owner\'s name, title type, any bank charge, caveats and restrictions such as Bumiputera or Malay Reserve status.',
                'Ask whether an individual strata title has been issued. Without it, the transfer needs the developer\'s consent and takes longer.',
                'Check arrears: maintenance and sinking fund, quit rent, assessment tax and utility bills. Agree in writing that the seller clears them.',
                'Inspect the unit in daylight: leaks, cracks, water pressure, wiring and any renovation that may need approval.',
            ]),
            ('Make an offer and pay the deposit', [
                'Write the offer letter with the price, what furniture is included, the completion period and "subject to loan approval".',
                'Pay the earnest deposit, usually 2% to 3%, to the agent or lawyer as stakeholder, not directly to the seller.',
                'Apply for your loan now. The bank will send a valuer, and the loan is based on the lower of price or valuation.',
                'If the valuation comes in low, you pay the difference in cash or renegotiate.',
            ]),
            ('Sign the SPA', [
                'Sign the SPA, usually within two to three weeks of the offer, and pay the balance up to 10% of the price.',
                'Your lawyer stamps the SPA and files the RPGT forms with LHDN.',
                'Your lawyer holds back 3% of the price (7% if the seller is not a citizen) for the seller\'s RPGT.',
                'Legal fees follow the Solicitors\' Remuneration Order scale. Use our calculator to estimate them.',
            ]),
            ('Consent and loan documents', [
                'Where needed, your lawyer applies for state consent or the developer\'s or management\'s consent to transfer.',
                'Sign the loan agreement. Your bank gives an undertaking to pay the balance on completion.',
                'Pay the stamp duty on the Memorandum of Transfer and on the loan.',
                'If the seller still has a loan, your bank pays it off directly and the rest goes to the seller.',
            ]),
            ('Completion', [
                'The balance of the price must be paid within the completion period, usually 3 months plus a 1-month extension.',
                'If the bank pays late, interest is usually charged at around 8% a year for the extension period.',
                'Your lawyer registers the transfer (Form 14A) and the bank\'s charge (Form 16A) at the land office. Registration can take a few months.',
            ]),
            ('Getting the keys', [
                'The seller hands over vacant possession and the keys once the full price is paid.',
                'Take meter readings and transfer water, electricity and internet accounts to your name.',
                'Register with the management office and update the names for quit rent and assessment tax.',
                'Keep your stamped documents and the final title safe: you need them when you sell.',
            ]),
        ],
        'faq': [
            ('How much deposit do I pay for a subsale property?', 'Usually 2% to 3% as an earnest deposit with your offer, then the balance up to 10% when you sign the SPA. The other 90% is paid on completion, usually through your bank loan.'),
            ('How long does a subsale take?', 'About three months from the SPA to completion, plus a one-month extension if needed. Titles that need state or developer consent can take longer.'),
            ('Why does my lawyer hold back 3% for LHDN?', 'The law requires the buyer to retain part of the price so the seller\'s Real Property Gains Tax is covered: 3% for Malaysian sellers and 7% for non-citizen sellers. It is paid to LHDN within 60 days and counts towards the seller\'s tax.'),
            ('What should I check before buying a subsale property?', 'The title (owner, charges, caveats and restrictions), whether a strata title has been issued, the owner\'s arrears, any tenancy, and the condition of the unit, including approvals for renovations.'),
            ('Who pays the agent\'s commission?', 'Normally the seller. The legal maximum is 3% of the price. If you appoint your own agent to find a property, agree the fee in writing first.'),
        ],
    },
    {
        'id': 'foreign-buyers',
        'tab': 'Foreigners Buying Property',
        'tab_sub': 'Rules, costs and steps for non-Malaysian buyers',
        'title': 'Foreigners buying property in Malaysia',
        'short': ('Foreigners can own freehold and leasehold homes in Malaysia, but only above a minimum price set by '
                  'each state, and every purchase needs state consent. From 1 January 2026, residential transfers to '
                  'non-citizens pay a flat 8% stamp duty. Banks usually lend 50% to 70% of the price.'),
        'numbers': [
            ('Who counts as a foreign buyer', 'Anyone who is not a Malaysian citizen. Permanent residents pay local stamp duty rates; check whether your state\'s threshold and consent rules apply to you'),
            ('Minimum purchase price', 'Set by each state: Kuala Lumpur RM1,000,000; Selangor RM2,000,000; Johor RM1,000,000 for strata and RM2,000,000 for landed; Penang varies by island, mainland and property type'),
            ('What you cannot buy', 'Malay Reserve land, Bumiputera lots, low- and medium-cost housing, and units below the state\'s minimum price'),
            ('State consent', 'Required for every foreign purchase; a transfer without it is void. Lawyers apply after the SPA, and fees and time vary by state'),
            ('Stamp duty on transfer', 'Flat 8% on residential property from 1 Jan 2026, plus 0.5% on the loan'),
            ('Home loan', 'Typically 50% to 70% of the price, depending on the bank and the country your income comes from'),
            ('Rental income tax', 'Non-residents pay a flat 30% on Malaysian rental income and file a yearly return'),
            ('RPGT when you sell', '30% of the gain within 5 years, 10% from the 6th year; the buyer holds back 7% of the price'),
        ],
        'stages': [
            ('Confirm you are eligible', [
                'Check the minimum price for the state and property type you want. Prices quoted before rebates may not count.',
                'Make sure the unit is not on Malay Reserve land, a Bumiputera lot or low- or medium-cost housing.',
                'Ask whether the developer or the title needs extra approval for foreign buyers.',
            ]),
            ('Budget and financing', [
                'Budget around 10% to 12% on top of the price: 8% stamp duty, legal fees, consent fees and loan costs.',
                'Ask banks that lend to your nationality for a pre-approval: usually 50% to 70% of the price.',
                'Prepare your passport, proof of income (salary slips, employment letter or tax returns), bank statements and a credit report from your home country.',
                'Keep records of the money you send into Malaysia: you will need them to send sale proceeds home later.',
            ]),
            ('Book and sign the SPA', [
                'Pay the booking fee (new launch) or earnest deposit (subsale).',
                'Sign the SPA, usually stated as subject to state consent, and pay the balance up to 10%.',
                'You can sign through a lawyer or with a power of attorney if you are overseas.',
            ]),
            ('Get state consent', [
                'Your lawyer applies to the state authority once the SPA is signed.',
                'It can take from a few weeks to several months, depending on the state.',
                'The completion period in the SPA usually starts only once consent is granted.',
            ]),
            ('Completion and transfer', [
                'Pay the balance of the price, through your bank loan or funds sent from overseas.',
                'Pay the 8% stamp duty on the transfer. Your lawyer registers the property in your name.',
                'Collect the keys and set up utilities and the management account.',
            ]),
            ('Owning, renting and selling', [
                'Pay maintenance fees, sinking fund, quit rent and assessment tax every year.',
                'If you rent it out, check the building\'s rules on short stays, and declare the rental income: non-residents pay 30% on it.',
                'When you sell, RPGT is 30% of the gain within 5 years and 10% from the 6th year. Holding longer saves tax.',
            ]),
        ],
        'faq': [
            ('What is the minimum price for foreigners?', 'It depends on the state: RM1,000,000 in Kuala Lumpur, RM2,000,000 in Selangor, and in Johor RM1,000,000 for strata and RM2,000,000 for landed. Penang sets different limits for the island, the mainland and each property type. Always confirm the current rule before you book.'),
            ('How much stamp duty do foreigners pay?', 'A flat 8% of the price on residential property transferred from 1 January 2026 (Malaysians pay 1% to 4% in tiers). There is also 0.5% stamp duty on a loan.'),
            ('Do permanent residents count as foreigners?', 'For stamp duty, Malaysian PRs pay local rates. For minimum prices and consent, rules differ by state, so check with your lawyer before you book.'),
            ('Can foreigners get a home loan in Malaysia?', 'Yes. Several banks lend to foreigners, usually 50% to 70% of the price, depending on your nationality, income source and credit history.'),
            ('How much RPGT do foreigners pay when selling?', '30% of the gain if you sell within 5 years, and 10% from the 6th year. The buyer\'s lawyer holds back 7% of the price for LHDN.'),
        ],
    },
]

# Blog topics: what buyers are trying to decide. An article can sit in several topics.
# Each topic gets its own landing page at topic/<slug>.html.
# (name, article ids, landing page description, related guide id or None)
TOPICS = [
    ('Foreign Buyer Rules', ['a4', 'a5', 'a6', 'a10', 'a11', 'a15', 'a19'],
     'Who can buy, the minimum price in each state, state consent and what foreigners pay to own property in Malaysia.', 'foreign-buyers'),
    ('Costs, Tax & Stamp Duty', ['a19', 'a11', 'a15', 'a4'],
     'Stamp duty, legal fees, RPGT and the running costs to budget for before and after you buy.', 'subsale'),
    ('Loan & Financing', ['a15', 'a4'],
     'How much banks lend, the documents they ask for and what changes when your income is outside Malaysia.', 'foreign-buyers'),
    ('Rental Yield & Airbnb', ['a3', 'a24', 'a27', 'a18', 'a16'],
     'What rents and yields look like in practice, and how long stays compare with short stays and Airbnb rules.', None),
    ('Market Outlook', ['a1', 'a20', 'a9', 'a2'],
     'Where the Malaysian property market is heading and how KL compares with Johor Bahru and Singapore.', None),
    ('Investment Strategy', ['a1', 'a2', 'a3', 'a16', 'a20', 'a24', 'a9'],
     'How to choose between areas, project types and rental plans when the goal is long-term return.', None),
    ('Area Guides', ['a2', 'a12', 'a13', 'a14', 'a17', 'a18', 'a21', 'a22'],
     'Neighbourhood guides to the parts of Kuala Lumpur and the Klang Valley buyers ask about most.', None),
    ('Kuala Lumpur', ['a1', 'a2', 'a3', 'a12', 'a13', 'a14', 'a16', 'a17', 'a18', 'a25', 'a26'],
     'Everything on Kuala Lumpur: KL City Centre, TRX, Bukit Bintang, Bangsar, Mont Kiara and Bukit Jalil.', None),
    ('TRX & Merdeka 118', ['a2', 'a14', 'a25', 'a26'],
     'Malaysia\'s new financial district and the Menara Merdeka 118 precinct: what is there and what it means for buyers.', None),
    ('Selangor & Petaling Jaya', ['a21', 'a22', 'a23'],
     'Petaling Jaya, Kwasa Damansara and ParkCity: the Selangor addresses gaining attention.', None),
    ('New Launch Reviews', ['a16', 'a23', 'a25', 'a26', 'a28', 'a30', 'a31'],
     'Keith\'s take on new launches: location, layouts, pricing and who each project suits.', 'new-property'),
    ('Luxury & Branded Residences', ['a16', 'a25', 'a23', 'a26'],
     'Branded residences, private lift lobbies and prime addresses, and whether the premium is worth paying.', 'new-property'),
    ('Transit & Infrastructure', ['a7', 'a8', 'a29', 'a14'],
     'MRT, LRT and the RTS Link: how new transport changes property values and rental demand.', None),
    ('Expat Living', ['a13', 'a18', 'a4'],
     'The neighbourhoods expats choose, what they look for and what that means for landlords.', None),
    ('Penang', ['a27', 'a28', 'a29', 'a30', 'a31'],
     'New launches, the LRT, short-stay rules and the waterfront projects shaping Penang\'s market.', None),
    ('Johor & Singapore Buyers', ['a6', 'a7', 'a8', 'a9'],
     'The RTS Link, Johor Bahru prices and why Singaporeans are buying across the causeway.', 'foreign-buyers'),
    ('MM2H', ['a5'],
     'The Malaysia My Second Home programme and what it means for buying property here.', 'foreign-buyers'),
]

# Labels shown on the page, translated for the site's languages.
LABELS = {
    'Investment Strategy': {'zh-CN': '投资策略', 'zh-TW': '投資策略', 'ms': 'Strategi Pelaburan', 'ta': 'முதலீட்டு உத்தி', 'ja': '投資戦略', 'ko': '투자 전략', 'ar': 'استراتيجية الاستثمار'},
    'Kuala Lumpur': {'zh-CN': '吉隆坡', 'zh-TW': '吉隆坡', 'ms': 'Kuala Lumpur', 'ta': 'கோலாலம்பூர்', 'ja': 'クアラルンプール', 'ko': '쿠알라룸푸르', 'ar': 'كوالالمبور'},
    'TRX & Merdeka 118': {'zh-CN': 'TRX 与默迪卡118', 'zh-TW': 'TRX 與默迪卡118', 'ms': 'TRX & Merdeka 118', 'ta': 'TRX & மெர்டேகா 118', 'ja': 'TRXとムルデカ118', 'ko': 'TRX 및 메르데카 118', 'ar': 'TRX وميرديكا 118'},
    'Selangor & Petaling Jaya': {'zh-CN': '雪兰莪与八打灵再也', 'zh-TW': '雪蘭莪與八打靈再也', 'ms': 'Selangor & Petaling Jaya', 'ta': 'சிலாங்கூர் & பெட்டாலிங் ஜெயா', 'ja': 'セランゴールとペタリンジャヤ', 'ko': '셀랑고르 및 페탈링자야', 'ar': 'سيلانغور وبيتالينغ جايا'},
    'Luxury & Branded Residences': {'zh-CN': '豪宅与品牌住宅', 'zh-TW': '豪宅與品牌住宅', 'ms': 'Kediaman Mewah & Berjenama', 'ta': 'ஆடம்பர & பிராண்டட் குடியிருப்புகள்', 'ja': '高級・ブランドレジデンス', 'ko': '럭셔리 및 브랜드 레지던스', 'ar': 'المساكن الفاخرة وذات العلامات التجارية'},
    'Expat Living': {'zh-CN': '外籍人士生活', 'zh-TW': '外籍人士生活', 'ms': 'Kehidupan Ekspatriat', 'ta': 'வெளிநாட்டவர் வாழ்க்கை', 'ja': '駐在員の暮らし', 'ko': '외국인 거주 생활', 'ar': 'حياة المغتربين'},
    'Latest Property News & Insights': {'zh-CN': '最新房产新闻与洞察', 'zh-TW': '最新房產新聞與洞察', 'ms': 'Berita & Pandangan Hartanah Terkini', 'ta': 'சமீபத்திய சொத்து செய்திகள் & கருத்துகள்', 'ja': '最新の不動産ニュースと考察', 'ko': '최신 부동산 뉴스 및 인사이트', 'ar': 'أحدث أخبار ورؤى العقارات'},
    'Filter by topic': {'zh-CN': '按主题筛选', 'zh-TW': '按主題篩選', 'ms': 'Tapis mengikut topik', 'ta': 'தலைப்பின்படி வடிகட்டு', 'ja': 'トピックで絞り込む', 'ko': '주제별 보기', 'ar': 'تصفية حسب الموضوع'},
    'Step-by-step guides': {'zh-CN': '分步指南', 'zh-TW': '分步指南', 'ms': 'Panduan langkah demi langkah', 'ta': 'படிப்படியான வழிகாட்டிகள்', 'ja': 'ステップ別ガイド', 'ko': '단계별 가이드', 'ar': 'أدلة خطوة بخطوة'},
    '47 answers': {'zh-CN': '47 个解答', 'zh-TW': '47 個解答', 'ms': '47 jawapan', 'ta': '47 பதில்கள்', 'ja': '47の回答', 'ko': '47개 답변', 'ar': '47 إجابة'},
    'Articles by topic': {'zh-CN': '按主题浏览文章', 'zh-TW': '按主題瀏覽文章', 'ms': 'Artikel mengikut topik', 'ta': 'தலைப்பு வாரியான கட்டுரைகள்', 'ja': 'トピック別の記事', 'ko': '주제별 기사', 'ar': 'مقالات حسب الموضوع'},
    'Buying Guide': {'zh-CN': '购房指南', 'zh-TW': '購房指南', 'ms': 'Panduan Membeli', 'ta': 'வாங்கும் வழிகாட்டி', 'ja': '購入ガイド', 'ko': '구매 가이드', 'ar': 'دليل الشراء'},
    'FAQ': {'zh-CN': '常见问题', 'zh-TW': '常見問題', 'ms': 'Soalan Lazim', 'ta': 'அடிக்கடி கேட்கப்படும் கேள்விகள்', 'ja': 'よくある質問', 'ko': '자주 묻는 질문', 'ar': 'الأسئلة الشائعة'},
    'Blog': {'zh-CN': '博客', 'zh-TW': '部落格', 'ms': 'Blog', 'ta': 'வலைப்பதிவு', 'ja': 'ブログ', 'ko': '블로그', 'ar': 'المدونة'},
    'Buying property in Malaysia, step by step.': {'zh-CN': '在马来西亚买房，一步一步来。', 'zh-TW': '在馬來西亞買房，一步一步來。', 'ms': 'Membeli hartanah di Malaysia, langkah demi langkah.', 'ta': 'மலேசியாவில் சொத்து வாங்குவது, படிப்படியாக.', 'ja': 'マレーシアでの不動産購入をステップごとに。', 'ko': '말레이시아 부동산 구매, 단계별로.', 'ar': 'شراء عقار في ماليزيا خطوة بخطوة.'},
    'Pick the guide that matches your purchase. Each one covers the key numbers, the six stages and the questions buyers ask most.': {'zh-CN': '选择适合您的指南。每份指南都包含关键数字、六个阶段和买家最常问的问题。', 'zh-TW': '選擇適合您的指南。每份指南都包含關鍵數字、六個階段和買家最常問的問題。', 'ms': 'Pilih panduan yang sesuai dengan pembelian anda. Setiap panduan merangkumi angka utama, enam peringkat dan soalan yang paling kerap ditanya.', 'ta': 'உங்கள் வாங்குதலுக்கு ஏற்ற வழிகாட்டியைத் தேர்ந்தெடுக்கவும்.', 'ja': 'ご自身の購入に合うガイドを選んでください。主要な数字、6つのステップ、よくある質問をまとめています。', 'ko': '구매 유형에 맞는 가이드를 선택하세요. 핵심 수치, 6단계, 자주 묻는 질문을 담았습니다.', 'ar': 'اختر الدليل المناسب لعملية الشراء الخاصة بك.'},
    'Short answer': {'zh-CN': '简短回答', 'zh-TW': '簡短回答', 'ms': 'Jawapan ringkas', 'ta': 'சுருக்கமான பதில்', 'ja': '要点', 'ko': '요약', 'ar': 'الإجابة المختصرة'},
    'Key numbers at a glance': {'zh-CN': '关键数字一览', 'zh-TW': '關鍵數字一覽', 'ms': 'Angka utama', 'ta': 'முக்கிய எண்கள்', 'ja': '主要な数字', 'ko': '핵심 수치 한눈에 보기', 'ar': 'أهم الأرقام'},
    'Six stages, start to finish': {'zh-CN': '六个阶段，从头到尾', 'zh-TW': '六個階段，從頭到尾', 'ms': 'Enam peringkat, dari awal hingga akhir', 'ta': 'ஆறு நிலைகள், தொடக்கம் முதல் முடிவு வரை', 'ja': '最初から最後までの6ステップ', 'ko': '처음부터 끝까지 6단계', 'ar': 'ست مراحل من البداية إلى النهاية'},
    'Questions buyers ask': {'zh-CN': '买家常问的问题', 'zh-TW': '買家常問的問題', 'ms': 'Soalan pembeli', 'ta': 'வாங்குபவர்கள் கேட்கும் கேள்விகள்', 'ja': '購入者からの質問', 'ko': '구매자들이 묻는 질문', 'ar': 'أسئلة المشترين'},
    'Stuck on a step? Ask Keith directly.': {'zh-CN': '卡在某个步骤？直接问 Keith。', 'zh-TW': '卡在某個步驟？直接問 Keith。', 'ms': 'Tersekat pada satu langkah? Tanya Keith terus.', 'ta': 'ஒரு படியில் சிக்கியுள்ளீர்களா? Keith-இடம் நேரடியாகக் கேளுங்கள்.', 'ja': '途中で迷ったら、Keithに直接ご相談ください。', 'ko': '막히는 단계가 있나요? Keith에게 직접 물어보세요.', 'ar': 'هل توقفت عند خطوة؟ اسأل Keith مباشرة.'},
    'WhatsApp Keith': {'zh-CN': 'WhatsApp Keith', 'zh-TW': 'WhatsApp Keith', 'ms': 'WhatsApp Keith', 'ta': 'WhatsApp Keith', 'ja': 'WhatsApp Keith', 'ko': 'WhatsApp Keith', 'ar': 'WhatsApp Keith'},
    'Common Questions': {'zh-CN': '常见问题', 'zh-TW': '常見問題', 'ms': 'Soalan Lazim', 'ta': 'பொதுவான கேள்விகள்', 'ja': 'よくある質問', 'ko': '자주 묻는 질문', 'ar': 'أسئلة شائعة'},
    'Answers to what buyers ask Keith most often.': {'zh-CN': '买家最常问 Keith 的问题解答。', 'zh-TW': '買家最常問 Keith 的問題解答。', 'ms': 'Jawapan kepada soalan yang paling kerap ditanya kepada Keith.', 'ta': 'வாங்குபவர்கள் Keith-இடம் அடிக்கடி கேட்கும் கேள்விகளுக்கான பதில்கள்.', 'ja': '購入者からKeithによく寄せられる質問への回答です。', 'ko': '구매자들이 Keith에게 가장 자주 묻는 질문에 대한 답변입니다.', 'ar': 'إجابات عن أكثر ما يسأله المشترون لـ Keith.'},
    'Show all questions': {'zh-CN': '显示全部问题', 'zh-TW': '顯示全部問題', 'ms': 'Tunjuk semua soalan', 'ta': 'அனைத்து கேள்விகளையும் காட்டு', 'ja': 'すべての質問を表示', 'ko': '모든 질문 보기', 'ar': 'عرض كل الأسئلة'},
    'Show fewer questions': {'zh-CN': '收起问题', 'zh-TW': '收起問題', 'ms': 'Tunjuk kurang soalan', 'ta': 'குறைவான கேள்விகளைக் காட்டு', 'ja': '質問を閉じる', 'ko': '질문 접기', 'ar': 'عرض أسئلة أقل'},
    'Choose a topic based on what you are trying to decide as a buyer.': {'zh-CN': '根据您作为买家想做的决定，选择一个主题。', 'zh-TW': '根據您作為買家想做的決定，選擇一個主題。', 'ms': 'Pilih topik berdasarkan perkara yang anda ingin putuskan sebagai pembeli.', 'ta': 'வாங்குபவராக நீங்கள் எடுக்க விரும்பும் முடிவின் அடிப்படையில் ஒரு தலைப்பைத் தேர்ந்தெடுக்கவும்.', 'ja': '購入者として決めたいことに合わせて、トピックを選んでください。', 'ko': '구매자로서 결정하려는 내용에 맞춰 주제를 선택하세요.', 'ar': 'اختر موضوعًا بناءً على ما تحاول أن تقرره كمشترٍ.'},
    'All categories': {'zh-CN': '全部分类', 'zh-TW': '全部分類', 'ms': 'Semua kategori', 'ta': 'அனைத்து வகைகள்', 'ja': 'すべてのカテゴリー', 'ko': '전체 카테고리', 'ar': 'كل الفئات'},
    'Foreign Buyer Rules': {'zh-CN': '外国买家规定', 'zh-TW': '外國買家規定', 'ms': 'Peraturan Pembeli Asing', 'ta': 'வெளிநாட்டு வாங்குபவர் விதிகள்', 'ja': '外国人購入ルール', 'ko': '외국인 구매 규정', 'ar': 'قواعد المشترين الأجانب'},
    'Costs, Tax & Stamp Duty': {'zh-CN': '费用、税务与印花税', 'zh-TW': '費用、稅務與印花稅', 'ms': 'Kos, Cukai & Duti Setem', 'ta': 'செலவுகள், வரி & முத்திரை வரி', 'ja': '費用・税金・印紙税', 'ko': '비용, 세금 및 인지세', 'ar': 'التكاليف والضرائب ورسوم الدمغة'},
    'Loan & Financing': {'zh-CN': '贷款与融资', 'zh-TW': '貸款與融資', 'ms': 'Pinjaman & Pembiayaan', 'ta': 'கடன் & நிதி', 'ja': 'ローンと資金調達', 'ko': '대출 및 금융', 'ar': 'القروض والتمويل'},
    'Rental Yield & Airbnb': {'zh-CN': '租金回报与 Airbnb', 'zh-TW': '租金回報與 Airbnb', 'ms': 'Hasil Sewa & Airbnb', 'ta': 'வாடகை வருவாய் & Airbnb', 'ja': '賃貸利回りとAirbnb', 'ko': '임대 수익률 및 에어비앤비', 'ar': 'العائد الإيجاري وAirbnb'},
    'Market Outlook': {'zh-CN': '市场展望', 'zh-TW': '市場展望', 'ms': 'Tinjauan Pasaran', 'ta': 'சந்தை கண்ணோட்டம்', 'ja': '市場見通し', 'ko': '시장 전망', 'ar': 'توقعات السوق'},
    'Area Guides': {'zh-CN': '地区指南', 'zh-TW': '地區指南', 'ms': 'Panduan Kawasan', 'ta': 'பகுதி வழிகாட்டிகள்', 'ja': 'エリアガイド', 'ko': '지역 가이드', 'ar': 'أدلة المناطق'},
    'New Launch Reviews': {'zh-CN': '新盘评测', 'zh-TW': '新盤評測', 'ms': 'Ulasan Projek Baharu', 'ta': 'புதிய திட்ட மதிப்புரைகள்', 'ja': '新規物件レビュー', 'ko': '신규 분양 리뷰', 'ar': 'مراجعات المشاريع الجديدة'},
    'Transit & Infrastructure': {'zh-CN': '交通与基础设施', 'zh-TW': '交通與基礎設施', 'ms': 'Pengangkutan & Infrastruktur', 'ta': 'போக்குவரத்து & உள்கட்டமைப்பு', 'ja': '交通とインフラ', 'ko': '교통 및 인프라', 'ar': 'النقل والبنية التحتية'},
    'Penang': {'zh-CN': '槟城', 'zh-TW': '檳城', 'ms': 'Pulau Pinang', 'ta': 'பினாங்கு', 'ja': 'ペナン', 'ko': '페낭', 'ar': 'بينانغ'},
    'Johor & Singapore Buyers': {'zh-CN': '柔佛与新加坡买家', 'zh-TW': '柔佛與新加坡買家', 'ms': 'Johor & Pembeli Singapura', 'ta': 'ஜொகூர் & சிங்கப்பூர் வாங்குபவர்கள்', 'ja': 'ジョホールとシンガポールの購入者', 'ko': '조호르 및 싱가포르 구매자', 'ar': 'جوهور ومشترو سنغافورة'},
    'MM2H': {'zh-CN': '第二家园 MM2H', 'zh-TW': '第二家園 MM2H', 'ms': 'MM2H', 'ta': 'MM2H', 'ja': 'MM2H', 'ko': 'MM2H', 'ar': 'MM2H'},
    'Buying New Property': {'zh-CN': '购买新房', 'zh-TW': '購買新房', 'ms': 'Membeli Hartanah Baharu', 'ta': 'புதிய சொத்து வாங்குதல்', 'ja': '新築物件の購入', 'ko': '신규 부동산 구매', 'ar': 'شراء عقار جديد'},
    'Buying Subsale Property': {'zh-CN': '购买二手房', 'zh-TW': '購買二手房', 'ms': 'Membeli Hartanah Subsale', 'ta': 'மறுவிற்பனை சொத்து வாங்குதல்', 'ja': '中古物件の購入', 'ko': '재판매 부동산 구매', 'ar': 'شراء عقار مستعمل'},
    'Foreigners Buying Property': {'zh-CN': '外国人购房', 'zh-TW': '外國人購房', 'ms': 'Warga Asing Membeli Hartanah', 'ta': 'வெளிநாட்டவர் சொத்து வாங்குதல்', 'ja': '外国人の不動産購入', 'ko': '외국인 부동산 구매', 'ar': 'شراء الأجانب للعقار'},
    'New launches and under-construction projects bought from a developer': {'zh-CN': '向发展商购买的新盘与在建项目', 'zh-TW': '向發展商購買的新盤與在建項目', 'ms': 'Projek baharu dan dalam pembinaan yang dibeli daripada pemaju', 'ta': 'டெவலப்பரிடமிருந்து வாங்கும் புதிய திட்டங்கள்', 'ja': 'デベロッパーから購入する新規・建設中の物件', 'ko': '개발사에서 구매하는 신규 분양 및 건설 중 프로젝트', 'ar': 'مشاريع جديدة وقيد الإنشاء تُشترى من المطوّر'},
    'Completed homes bought from an existing owner': {'zh-CN': '向现有屋主购买的已完工房产', 'zh-TW': '向現有屋主購買的已完工房產', 'ms': 'Rumah siap yang dibeli daripada pemilik sedia ada', 'ta': 'தற்போதைய உரிமையாளரிடமிருந்து வாங்கும் முடிந்த வீடுகள்', 'ja': '既存のオーナーから購入する完成済み物件', 'ko': '기존 소유자에게서 구매하는 완공 주택', 'ar': 'منازل مكتملة تُشترى من مالكها الحالي'},
    'Rules, costs and steps for non-Malaysian buyers': {'zh-CN': '非马来西亚买家的规定、费用与步骤', 'zh-TW': '非馬來西亞買家的規定、費用與步驟', 'ms': 'Peraturan, kos dan langkah untuk pembeli bukan warganegara', 'ta': 'மலேசியர் அல்லாத வாங்குபவர்களுக்கான விதிகள், செலவுகள் மற்றும் படிகள்', 'ja': '外国人購入者向けのルール・費用・手順', 'ko': '외국인 구매자를 위한 규정, 비용 및 절차', 'ar': 'القواعد والتكاليف والخطوات للمشترين غير الماليزيين'},
}


# ---------- Extra articles written for the site (tools/i18n/news_extra_src.json) ----------
import json as _json
import os as _os

EXTRA_SRC = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'i18n', 'news_extra_src.json'), encoding='utf-8'))


def _en(o):
    if isinstance(o, dict) and 'en' in o:
        return o['en']
    if isinstance(o, dict):
        return {k: _en(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_en(v) for v in o]
    return o


def _pairs(o, out):
    """Every {en, lang...} text in the extra articles, as {en: {lang: text}}."""
    if isinstance(o, dict) and 'en' in o:
        out[o['en']] = {k: v for k, v in o.items() if k != 'en'}
    elif isinstance(o, dict):
        for v in o.values():
            _pairs(v, out)
    elif isinstance(o, list):
        for v in o:
            _pairs(v, out)
    return out


EXTRA_ARTICLES = {k: {f: _en(v) for f, v in a.items() if f not in ('topics', 'card')} for k, a in EXTRA_SRC.items()}
EXTRA_CARDS = {k: a['card']['en'] for k, a in EXTRA_SRC.items()}
EXTRA_TR = _pairs(EXTRA_SRC, {})
for _k, _a in EXTRA_SRC.items():
    for _tp in TOPICS:
        if _tp[0] in _a['topics'] and _k not in _tp[1]:
            _tp[1].insert(0, _k)
