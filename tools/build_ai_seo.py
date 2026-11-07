"""Help search engines and AI assistants find and understand the site.

Writes robots.txt (names the AI crawlers we welcome), llms.txt (a plain
summary of the site for AI assistants), the IndexNow key file, and
structured data (JSON-LD) on the Home, About Keith and News pages.
Run from the repository root after the other build scripts:
    python3 tools/build_ai_seo.py
Safe to run again.
"""
import glob
import html
import json
import re

SITE = 'https://keithnah.com'
INDEXNOW_KEY = '7c1f4b9e2d8a4f63a5e0b6d91c3e8f27'  # public by design: IndexNow checks it at /<key>.txt
WHATSAPP = '+60102821568'
SAME_AS = ['https://www.youtube.com/@KeithNahRealEstate', 'https://www.instagram.com/keithnah_/']
LOGO = SITE + '/images/f304c8479b1fe873.png'

AI_BOTS = ['Googlebot', 'Bingbot', 'Google-Extended', 'GPTBot', 'OAI-SearchBot', 'ChatGPT-User',
           'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Perplexity-User', 'Applebot', 'Applebot-Extended']


def U(s):
    return html.unescape(s)


def meta(path):
    t = open(path, encoding='utf-8').read()
    title = U(re.search(r'<title>(.*?)</title>', t, re.S).group(1)).strip()
    d = re.search(r'<meta name="description" content="(.*?)"', t, re.S)
    return t, title, U(d.group(1)).strip() if d else ''


def robots():
    out = ['# Keith Nah Real Estate: search engines and AI assistants are welcome to read and cite this site.', '']
    for b in AI_BOTS:
        out += ['User-agent: %s' % b, 'Allow: /', '']
    out += ['User-agent: *', 'Allow: /', 'Disallow: /tools/', '', 'Sitemap: %s/sitemap.xml' % SITE, '']
    open('robots.txt', 'w', encoding='utf-8').write('\n'.join(out))


def llms():
    projects = {}
    for f in sorted(glob.glob('property/*.html')):
        t, title, desc = meta(f)
        area = re.search(r'<span class="badge alt">(.*?)</span>', t)
        area = U(area.group(1)) if area else 'Other'
        name = title.split(' | ')[0]
        projects.setdefault(area, []).append('- [%s](%s/%s): %s' % (name, SITE, f, desc.split(' See floor plans')[0].replace('Completion Completed', 'Completed')))
    topics = []
    for f in sorted(glob.glob('topic/*.html')):
        t, title, desc = meta(f)
        topics.append('- [%s](%s/%s): %s' % (title.split(':')[0], SITE, f, re.sub(r' \d+ articles? by Keith Nah\.$', '', desc)))
    arts = []
    for f in sorted(glob.glob('article/*.html')):
        t, title, desc = meta(f)
        arts.append('- [%s](%s/%s)' % (title.replace(' | Keith Nah', ''), SITE, f))
    lines = [
        '# Keith Nah Real Estate',
        '',
        '> Keith Nah (鈞晖) is a property consultant in Malaysia who helps local and international buyers choose new-launch '
        'condominiums and homes, mainly in Kuala Lumpur (KL City Centre, TRX, Bukit Bintang, Bangsar, Bukit Jalil), with '
        'projects also in Selangor, Penang and Johor. Buyers pay no agent fee on new launches. Each project page lists '
        'price, sizes, bedrooms, tenure, completion date and floor plans. Contact: WhatsApp %s.' % WHATSAPP,
        '',
        'The site is available in English, 简体中文, 繁體中文, Bahasa Malaysia, தமிழ், 日本語, 한국어 and العربية. '
        'Prices are indicative; buyers should confirm current figures with Keith.',
        '',
        '## Main pages',
        '- [Home](%s/): who Keith is, featured projects and 47 common buyer questions' % SITE,
        '- [All projects](%s/projects.html): every project, searchable by area, price, type and tag' % SITE,
        '- [Compare projects](%s/compare.html): side-by-side comparison' % SITE,
        '- [Buying guides, FAQ and news](%s/blog.html): buying a new property, buying a subsale home, rules for foreign buyers' % SITE,
        '- [Loan calculator](%s/calculator.html)' % SITE,
        '- [MM2H explained](%s/mm2h.html): Malaysia My Second Home tiers, requirements and costs' % SITE,
        '- [About Keith](%s/about-keith.html)' % SITE,
        '',
        '## Projects',
    ]
    for area in sorted(projects):
        lines += ['', '### %s' % area] + projects[area]
    lines += ['', '## Topics'] + topics + ['', '## Articles'] + arts
    lines += ['', '## Optional', '- [YouTube: Keith Nah Real Estate](%s): project walkthroughs and drone videos' % SAME_AS[0],
              '- [Instagram](%s)' % SAME_AS[1], '- [Sitemap](%s/sitemap.xml)' % SITE, '']
    open('llms.txt', 'w', encoding='utf-8').write('\n'.join(lines))


def put_ld(path, data):
    t = open(path, encoding='utf-8').read()
    block = '<!-- KN-LD:START --><script type="application/ld+json">%s</script><!-- KN-LD:END -->' % (
        json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
    if '<!-- KN-LD:START -->' in t:
        t = re.sub(r'<!-- KN-LD:START -->.*?<!-- KN-LD:END -->', lambda _: block, t, flags=re.S)
    else:
        t = t.replace('</head>', block + '\n</head>', 1)
    open(path, 'w', encoding='utf-8').write(t)


def faq_items(page, pattern):
    t = open(page, encoding='utf-8').read()
    out = []
    for q, a in re.findall(pattern, t, re.S):
        q, a = U(re.sub(r'<[^>]+>', '', q)).strip(), U(re.sub(r'<[^>]+>', '', a)).strip()
        out.append({'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}})
    return out


def structured_data():
    person = {'@type': 'Person', '@id': SITE + '/#keith', 'name': 'Keith Nah', 'alternateName': '鈞晖',
              'jobTitle': 'Property Consultant', 'url': SITE + '/about-keith.html', 'image': LOGO, 'sameAs': SAME_AS,
              'worksFor': {'@id': SITE + '/#agency'}}
    agency = {'@type': 'RealEstateAgent', '@id': SITE + '/#agency', 'name': 'Keith Nah Real Estate', 'url': SITE + '/',
              'logo': LOGO, 'image': LOGO, 'telephone': WHATSAPP, 'founder': {'@id': SITE + '/#keith'}, 'sameAs': SAME_AS,
              'description': 'Property consultant for new-launch condominiums and homes in Malaysia, mainly Kuala Lumpur '
                             '(KL City Centre, TRX, Bukit Bintang, Bangsar, Bukit Jalil), plus Selangor, Penang and Johor. '
                             'No agent fee for buyers on new launches.',
              'address': {'@type': 'PostalAddress', 'addressLocality': 'Kuala Lumpur', 'addressCountry': 'MY'},
              'areaServed': [{'@type': 'City', 'name': 'Kuala Lumpur'}, {'@type': 'State', 'name': 'Selangor'},
                             {'@type': 'State', 'name': 'Penang'}, {'@type': 'State', 'name': 'Johor'}],
              'contactPoint': {'@type': 'ContactPoint', 'telephone': WHATSAPP, 'contactType': 'sales',
                               'url': 'https://wa.me/60102821568'}}
    website = {'@type': 'WebSite', '@id': SITE + '/#website', 'name': 'Keith Nah Real Estate', 'url': SITE + '/',
               'publisher': {'@id': SITE + '/#agency'},
               'inLanguage': ['en', 'zh-CN', 'zh-TW', 'ms', 'ta', 'ja', 'ko', 'ar']}
    home_faq = faq_items('index.html', r'data-i18n="faq_q\d+">(.*?)<span class="faq-icon">.*?<p data-i18n="faq_a\d+">(.*?)</p>')
    assert len(home_faq) >= 30, len(home_faq)
    put_ld('index.html', {'@context': 'https://schema.org', '@graph': [agency, person, website,
                          {'@type': 'FAQPage', '@id': SITE + '/#faq', 'mainEntity': home_faq}]})
    put_ld('about-keith.html', {'@context': 'https://schema.org', '@graph': [
        dict(person, description='Property consultant and content creator helping local and international buyers choose '
                                 'new launches in Kuala Lumpur, with drone footage, site walkthroughs and pricing breakdowns.'),
        agency, {'@type': 'ProfilePage', 'url': SITE + '/about-keith.html', 'mainEntity': {'@id': SITE + '/#keith'}}]})
    guide_faq = faq_items('blog.html', r'<details class="bg-faq"><summary>(.*?)</summary><p>(.*?)</p></details>')
    put_ld('blog.html', {'@context': 'https://schema.org', '@graph': [
        {'@type': 'CollectionPage', 'name': 'Malaysia Property Buying Guides, FAQ and News', 'url': SITE + '/blog.html',
         'publisher': {'@id': SITE + '/#agency'}},
        {'@type': 'FAQPage', 'mainEntity': guide_faq}]})
    put_ld('projects.html', {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'Malaysia New Launch Projects',
                             'url': SITE + '/projects.html', 'publisher': {'@type': 'RealEstateAgent', 'name': 'Keith Nah Real Estate', 'url': SITE + '/'}})
    return len(home_faq), len(guide_faq)


if __name__ == '__main__':
    robots()
    llms()
    open('%s.txt' % INDEXNOW_KEY, 'w').write(INDEXNOW_KEY)
    n = structured_data()
    print('robots.txt, llms.txt, IndexNow key and structured data written (FAQ: %d home, %d guides)' % n)
