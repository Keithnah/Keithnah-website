"""Project landing pages: the focused, one-project layout for Keith's best choices for foreign buyers.

Run by tools/build_all.py right after build_project_pages.py: for EVERY project (new ones too) it
replaces property/<slug>.html with this layout, keeping the head of the generated page (title,
canonical, structured data, social tags). Per-project extras (hook, curated points, notes) are
optional and live in tools/i18n/landing.json "projects"; a project without them still gets the layout.

The page: a split cover (photo left, details right on a light background), a two-row sticky header
(Back to home website, language, currency / logo, the project's own sections, WhatsApp), then
Overview, Key points, Project details, Layouts, Price, Location, Foreign buyers, FAQ and nearby
projects. Project data is translated with the site's project translations (tools/i18n_pages.py);
the page's own texts come from tools/i18n/landing.json (en, zh-CN, ms, ja, ko; zh-TW by OpenCC).
Facts come only from the project data and the notes in landing.json. Nothing is invented.

    python3 tools/externalize.py in
    python3 tools/build_landing.py                 (all landing pages)
    python3 tools/build_landing.py maba-suitez OUT (one page to OUT, for a preview)
    python3 tools/externalize.py out
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
import float_wa as FW  # noqa: E402
import i18n_pages as I18N  # noqa: E402
import site_header as SH  # noqa: E402

E = lambda s: html.escape(str(s), quote=True)
WA = 'https://api.whatsapp.com/send/?phone=60102821568&text=%s&type=phone_number&app_absent=0'
waq = lambda m: WA % re.sub(r'\s', '+', '(KNRE) ' + m).replace('&', '%26')
LG = ['en', 'zh-CN', 'zh-TW', 'ms', 'ja', 'ko']
try:
    import opencc
    _cc = opencc.OpenCC('s2tw').convert
except ImportError:
    _cc = lambda s: s
TX = json.load(open(os.path.join(HERE, 'i18n', 'landing.json'), encoding='utf-8'))
LANDING = TX['projects']
FOREIGN_MIN = {'Kuala Lumpur': (1000000, 'm1'), 'Selangor': (2000000, 'm2')}
BANNED = re.compile(r'rebate|nett|package|commission|sales gallery|airbnb|klcc|guaranteed rental|\bgrr\b', re.I)


def six(v):
    """[en, zh-CN, ms, ja, ko] -> the six site languages."""
    return [v[0], v[1], _cc(v[1]), v[2], v[3], v[4]]


UI = {k: six(v) for k, v in TX['ui'].items()}


def proj_index(slug):
    for i, s in A.SLUG.items():
        if s == slug:
            return i
    raise SystemExit('no project with slug %s' % slug)


def page(slug, root='../', head_src=None):
    i = proj_index(slug)
    p = A.P[i]
    L = LANDING.get(slug, {})
    T = dict(UI)                       # this page's texts: {key: [6 languages]}
    name = p['name']
    st, area = A.PLACES[i]
    ex = p.get('details_extra') or {}
    photo = root + A.PHOTO[i] if A.PHOTO.get(i) else ''
    r = lambda k, tag='span', cls='', extra='': '<%s%s data-r="%s"%s>%s</%s>' % (tag, (' class="%s"' % cls) if cls else '', k, extra, E(T[k][0]), tag)
    rn = lambda k, tag='span', cls='': '<%s%s data-r="%s" data-n="%s">%s</%s>' % (tag, (' class="%s"' % cls) if cls else '', k, E(name), E(T[k][0].replace('{n}', name)), tag)
    w = lambda m: E(waq(m % name if '%s' in m else m))
    wa_price = w("Hi Keith, I'd like the latest price list for %s.")
    chat = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 3.5A11 11 0 0 0 3.2 17.1L2 22l5-1.3A11 11 0 1 0 20.5 3.5z"/></svg>'

    def wbtn(key, msg, cls='lp-wa', t=None):
        txt = T[key][0].replace('{t}', t) if t else T[key][0]
        return '<a class="%s" href="%s" target="_blank" rel="noopener" data-cta="lp">%s<span data-r="%s"%s>%s</span></a>' % (
            cls, w(msg), chat, key, (' data-t="%s"' % E(t)) if t else '', E(txt))

    myr = A.price_rm(p['price'])
    price_html = SH.price_tag(E(p['price']), int(myr)) if myr else E(p['price'])
    mo = ''
    if head_src:
        m = re.search(r'data-mo>([^<]+)<', head_src) or re.search(r'<div class="lp-mo">.*?<b>([^<]*)</b>', head_src, re.S)
        mo = m.group(1) if m else ''

    # ---- texts that belong to this project
    if L.get('hook'):
        T['hook'] = six(L['hook'])
    five_custom = L.get('five')
    if five_custom:
        for n, (tt, dd) in enumerate(five_custom):
            T['f%dt' % n], T['f%dd' % n] = six(tt), six(dd)
    for n, (num, lab) in enumerate(L.get('nums', [])):
        T['num%d' % n] = six(lab)
    for k, v in (L.get('fit') or {}).items():
        T['fit:' + k] = six(v)
    if L.get('developer'):
        T['dev'] = six(L['developer'])
    if L.get('foreign'):
        T['fb'] = six(L['foreign'])
    else:
        mn = FOREIGN_MIN.get(st)
        if mn:
            key = 'fb_por' if not myr else ('fb_ok' if myr >= mn[0] else 'fb_low')
            T['fb'] = [T[key][j].replace('{p}', re.sub(r'^From\s*', '', p['price'])).replace('{m}', T[mn[1]][j]).replace('{s}', st) for j in range(6)]

    nav = [('overview', 'nav_overview'), ('five', 'nav_five'), ('details', 'nav_details'), ('layouts', 'nav_layouts'), ('price', 'nav_price'), ('view', 'nav_view'),
           ('location', 'nav_location'), ('video', 'nav_video'), ('foreign', 'nav_foreign'), ('faq', 'nav_faq')]
    import build_project_pages as BP   # the Video Tour block of the project pages (tools/project_videos.json)
    vblk = BP.video_block(name, name)
    if vblk:
        vblk = vblk.replace('<section class="blk" id="video"><h2>Video Tour</h2>',
                            '<section class="lp-sec" id="video"><span class="lp-eb" data-r="nav_video">Video</span><h2 data-r="h_video">%s</h2>' % E(T['h_video'][0]), 1)
    else:
        nav = [x for x in nav if x[0] != 'video']
    if not T.get('fb'):
        nav = [x for x in nav if x[0] != 'foreign']
    view = view_block(p, L, T, r, rn, root, lays=p.get('layouts') or [], ex=ex, w=w, chat=chat)
    if not view:
        nav = [x for x in nav if x[0] != 'view']
    navh = ''.join('<a href="#%s" data-r="%s">%s</a>' % (k, t, E(T[t][0])) for k, t in nav)
    crumbs = ('<a href="{r}" data-r="home">Home</a><i>›</i><a href="{r}projects.html">Projects</a><i>›</i><a href="{r}area/{s}.html">{st}</a><i>›</i>'
              '<a href="{r}area/{a}.html">{ar}</a><i>›</i><b>{n}</b>').format(r=root, s=A.slug(st), st=E(st), a=A.slug(area), ar=E(area), n=E(name))
    badges = ''.join('<span class="lp-bd%s">%s</span>' % (c, E(v)) for c, v in ((' dark', p.get('status')), ('', area), ('', A.TYPE.get(i, 'Residential'))) if v)
    facts = [('f_from', re.sub(r'^From\s*', '', p['price'])), ('f_size', p['size']), ('f_type', p['rooms']), ('f_ten', p['tenure']), ('f_comp', p['completion'])]
    factsh = ''.join('<div>%s<b>%s</b></div>' % (r(a, 'small'), E(b)) for a, b in facts if b)
    nums = ''.join('<div><b>%s</b>%s</div>' % (E(num), r('num%d' % n, 'small')) for n, (num, _) in enumerate(L.get('nums', [])))

    if five_custom:
        five = ''.join('<li><span>%02d</span><div>%s%s</div></li>' % (n + 1, r('f%dt' % n, 'h3'), r('f%dd' % n, 'p')) for n in range(len(five_custom)))
        h_five = 'h_five5'
    else:
        pts = []
        for s in (p.get('selling_points') or []) + (p.get('points') or []):
            if s not in pts and not BANNED.search(s):
                pts.append(s)
        five = ''.join('<li><span>%02d</span><div><h3>%s</h3></div></li>' % (n + 1, E(s)) for n, s in enumerate(pts[:5]))
        h_five = 'h_five'

    rows = [('Project Name', name), ('Location', p['loc']), ('Property Type', A.TYPE.get(i, 'Residential')), ('Tenure', p['tenure']), ('Status', p.get('status', '')),
            ('Starting Price', p['price']), ('Size', p['size']), ('Bedrooms', p['rooms']), ('Completion', p['completion'])] + [(k, v) for k, v in ex.items() if k not in ('Address',)]
    details = ''.join('<tr><th scope="row">%s</th><td>%s</td></tr>' % (E(a), E(b)) for a, b in rows if b and not BANNED.search(str(b)))
    fits = ''.join('<div><b>%s</b><p>%s</p></div>' % (E(f['title']), E(f['desc'])) for f in p.get('buyer_fit') or [] if not BANNED.search(f['title'] + f['desc']))

    lays = p.get('layouts') or []
    short = lambda t: re.sub(r'\s+—.*', '', t)
    tabs = ''.join('<button type="button" class="lp-tab%s" data-t="%d">%s<small>%s</small></button>' % (
        ' on' if n == 0 else '', n, E(short(l['type'])), E(l['size'])) for n, l in enumerate(lays))
    panes = ''
    for n, l in enumerate(lays):
        units = (L.get('units') or {}).get(l['type'])
        img = ('<img src="%s%s" alt="%s %s floor plan" loading="lazy">' % (root, E(l['img']), E(name), E(l['type']))) if l.get('img') else r('lay_noimg', 'p', 'lp-noimg')
        fit = r('fit:' + l['type'], 'p', 'lp-fit') if ('fit:' + l['type']) in T else ''
        panes += ('<div class="lp-pane%s" data-p="%d"><div class="lp-plan">%s</div><div class="lp-pd"><span class="lp-eb">%s</span><h3>%s</h3><dl><div>%s<dd>%s</dd></div>'
                  '<div>%s<dd>%s</dd></div>%s</dl><p>%s</p>%s%s</div></div>') % (
            ' on' if n == 0 else '', n, img, E(l.get('tag', '')), E(l['type']), r('lay_size', 'dt'), E(l['size']), r('lay_layout', 'dt'), E(l['rooms']),
            ('<div>%s<dd>%d</dd></div>' % (r('lay_units', 'dt'), units)) if units else '', E(l.get('desc', '')), fit,
            wbtn('ask_lay', 'Hi Keith, which %s units are still available at %%s?' % short(l['type']), t=short(l['type'])))

    plist = ''.join('<div>%s<b>%s</b></div>' % (r(k), E(ex[f])) for k, f in (('psf', 'Price per Sqft'), ('maint', 'Maintenance Fee'), ('park', 'Car Parks')) if ex.get(f))
    amen = ''.join('<li>%s</li>' % E(a) for a in p.get('amenities') or [] if not BANNED.search(a))
    dev = ex.get('Developer', '')
    faqs = [('q_where', p['loc_text']), ('q_size', '%s · %s' % (p['size'], p['rooms'])), ('q_price', p['price']), ('q_ten', p['tenure']),
            ('q_dev', '' if L.get('developer') else dev), ('q_comp', p['completion']), ('q_maint', ex.get('Maintenance Fee', ''))]
    faqh = ''.join('<details><summary data-r="%s" data-n="%s">%s</summary><p>%s</p></details>' % (q, E(name), E(T[q][0].replace('{n}', name)), E(a)) for q, a in faqs if a)
    if L.get('developer'):
        faqh += '<details><summary data-r="q_dev">%s</summary>%s</details>' % (E(T['q_dev'][0]), r('dev', 'p'))
    if T.get('fb'):
        faqh += '<details><summary data-r="q_fb" data-n="%s">%s</summary>%s</details>' % (E(name), E(T['q_fb'][0].replace('{n}', name)), r('fb', 'p'))
    nearby = ''.join('<a class="lp-nb" href="%s.html"><img src="%s%s" alt=""><b>%s</b><small>%s</small></a>' % (
        A.SLUG.get(k, A.slug(A.P[k]['name'])), root, E(A.PHOTO.get(k, '')), E(A.P[k]['name']), E(A.P[k]['price'])) for k in (p.get('nearby') or [])[:3] if k < len(A.P))
    maps = 'https://www.google.com/maps/search/?api=1&query=' + re.sub(r'\s', '+', '%s, %s' % (name, p['loc']))

    head = DEFAULT_HEAD.format(title=E('%s | Keith Nah' % name), desc=E(p['overview'][:155]), root=root)
    if head_src:
        keep = re.findall(r'<title>.*?</title>|<meta\b[^>]*>|<link\b[^>]*rel="(?:canonical|icon|alternate|preconnect|stylesheet)"[^>]*>|<script type="application/ld\+json">.*?</script>', head_src.split('</head>')[0], re.S)
        keep = [k for k in keep if 'fonts.googleapis.com/css2' not in k and 'charset=' not in k and 'name="viewport"' not in k]
        if keep:
            head = '\n'.join(keep) + '\n<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">'

    body = BODY.format(
        root=root, name=E(name), photo=E(photo), crumbs=crumbs, badges=badges, hook=r('hook', 'p', 'hA-hook') if 'hook' in T else '', loc=E(p['loc']),
        price=price_html, mo=E(mo), wa_price=wa_price, chat=chat, factsh=factsh, navh=navh, overview=E(p['overview']),
        nums=('<div class="lp-nums">%s</div>' % nums) if nums else '', five=five, details=details, fits=('<div class="lp-fits">%s</div>' % fits) if fits else '',
        tabs=tabs, panes=panes, plist=plist, loc_text=E(p['loc_text']), amen=amen, maps=E(maps), nearby=nearby,
        wb_list=wbtn('req_list', 'Hi Keith, please send me the latest price list for %s.'), wb_units=wbtn('chk_units', 'Hi Keith, which units are still available at %s?', 'lp-wa lp-wa2'),
        wb_view=wbtn('view', "Hi Keith, I'd like to book a viewing or a video tour of %s."),
        fb=('<section class="lp-sec" id="foreign"><div class="lp-fb">%s<h2 data-r="h_fb">%s</h2>%s%s<a class="lp-link" href="%sforeign-buyers.html" data-r="fb_link">%s</a></div></section>' % (
            r('nav_foreign', 'span', 'lp-eb'), E(T['h_fb'][0]), r('fb', 'p'), wbtn('fb_btn', 'Hi Keith, I am a foreign buyer. Which units at %s meet the minimum price?'), root, E(T['fb_link'][0]))) if T.get('fb') else '',
        faqh=faqh, video=vblk, layouts=('<section class="lp-sec" id="layouts">%s<h2 data-r="h_lay">%s</h2><div class="lp-tabs">%s</div>%s</section>' % (
            r('nav_layouts', 'span', 'lp-eb'), E(T['h_lay'][0]), tabs, panes)) if lays else '',
        **{k: v for k, v in dict(
            t_back=r('back'), t_home=r('home', 'em', 'lp-hs'), t_cta=r('cta_bar'), t_tag=('<span class="hA-tag">%s</span>' % r('tag')) if slug in BEST_SLUGS else '', t_sp=r('sp', 'small'), t_mo=r('mo'), t_moch=r('mo_ch'), t_wal=r('wa_list'), t_cmp=r('cmp'),
            t_ebo=r('nav_overview', 'span', 'lp-eb'), t_hab=rn('h_about', 'h2'), t_eb5=r('eb_five', 'span', 'lp-eb'), t_h5=r(h_five, 'h2'), t_ebd=r('eb_det', 'span', 'lp-eb'), t_hdet=rn('h_det', 'h2'),
            t_ebp=r('nav_price', 'span', 'lp-eb'), t_hp=r('h_price', 'h2'), t_sp2=r('sp', 'small'), t_pnote=r('p_note', 'p'), t_calc=r('calc', 'a', 'lp-map', ' href="%scalculator.html"' % root),
            t_ebl=r('nav_location', 'span', 'lp-eb'), t_maps=r('maps'), t_ebf=r('nav_faq', 'span', 'lp-eb'), t_hfaq=rn('h_faq', 'h2'), t_more=r('more_h', 'h2'),
            t_lc=r('l_cmp'), t_la=r('l_all'), t_lf=r('l_fb'), t_lk=r('l_calc')).items()})
    if L.get('developer'):
        body = body.replace('<!--DEV-->', '<div class="lp-dev">%s%s</div>' % (r('eb_dev', 'span', 'lp-eb'), r('dev', 'p')))
    body = body.replace('<!--VIEW-->', view, 1)
    body = body.replace('<!--NEWS-->', news_block(slug, name, area, T, r, rn, root), 1)
    if not plist:
        body = body.replace('<div class="lp-plist"></div>', '')
    js = JS % (json.dumps(T, ensure_ascii=False), json.dumps(LG))
    out = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n%s\n'
           '<style>\n%s\n</style>\n<style id="kn-float">%s</style>\n</head>\n<body>\n%s\n%s\n%s\n</body>\n</html>\n') % (
        head,
        CSS, FW.FLOAT_CSS, body, FW.float_html(wa_price), js)
    I18N.USE_KN[0] = True
    out = I18N.translate(out)
    return out.replace('</body>', SH.js() + '\n</body>', 1)



def view_block(p, L, T, r, rn, root, lays, ex, w, chat):
    """Keith's view: who it suits / does not suit, things to know, an investment calculator and a
    pre-booking checklist. Only for projects with a "view" entry in landing.json (facts from the
    project data; nothing invented)."""
    V = L.get('view')
    if not V:
        return ''
    def lst(key, cls):
        out = ''
        for n, v in enumerate(V.get(key) or []):
            T['v:%s%d' % (key, n)] = six(v)
            out += '<li>%s</li>' % r('v:%s%d' % (key, n))
        return ('<ul class="%s">%s</ul>' % (cls, out)) if out else ''
    suits, nots, trade, verify = lst('suits', 'lp-ok'), lst('not', 'lp-no'), lst('trade', 'lp-tr'), lst('verify', 'lp-ck')
    calc = ''
    inv = V.get('inv')
    if inv and lays:
        opts = ''
        for n, l in enumerate(lays):
            m = re.search(r'([\d,]+)\s*sq', l['size'])
            if not m:
                continue
            sq = int(m.group(1).replace(',', ''))
            pr = (inv.get('prices') or {}).get(l['type'])
            est = 0 if pr else 1
            pr = pr or int(round(sq * inv['psf_low'], -3))
            opts += '<option value="%d" data-sq="%d" data-est="%d">%s · %s</option>' % (pr, sq, est, E(l['type']), E(l['size']))
        f = lambda k, v, step: '<label>%s<input type="number" data-v="%s" value="%s" step="%s" min="0"></label>' % (r(k), k, v, step)
        calc = ('<div class="lp-inv" data-mp="%s"><h3 data-r="v_inv">%s</h3>%s<div class="lp-invf"><label>%s<select data-v="lay">%s</select></label>%s%s%s%s</div>'
                '<p class="lp-est" hidden>%s</p><div class="lp-invo"><div>%s<b data-o="inst"></b></div><div>%s<b data-o="maint"></b></div><div class="t">%s<b data-o="cost"></b></div></div></div>') % (
            inv['maint_psf'], E(T['v_inv'][0]), r('v_inv_p', 'p'), r('v_lay'), opts, f('v_price', '', 1000), f('v_loan', inv['loan'], 5), f('v_rate', inv['rate'], 0.05), f('v_yrs', inv['years'], 1),
            r('v_est'), r('v_inst', 'small'), r('v_maint', 'small'), r('v_cost', 'small'))
    return ('<section class="lp-sec" id="view">%s%s<div class="lp-v2"><div class="lp-vc">%s%s</div><div class="lp-vc">%s%s</div></div>'
            '<div class="lp-vc lp-vt">%s%s</div>%s<div class="lp-vc lp-vk">%s%s<div class="lp-row"><a class="lp-wa" href="%s" target="_blank" rel="noopener" data-cta="lp">%s%s</a></div></div></section>') % (
        r('nav_view', 'span', 'lp-eb'), rn('h_view', 'h2'), r('v_suits', 'h3'), suits, r('v_not', 'h3'), nots, r('v_trade', 'h3'), trade, calc, r('v_check', 'h3'), verify,
        w("Hi Keith, before I book %s, can you check the unit, car park, APDL date and maintenance fee for me?"), chat, r('v_wa'))



def _six_any(d):
    """{lang: text} (any of the six, English required) -> the six site languages."""
    zh = d.get('zh-CN')
    tw = d.get('zh-TW') or (_cc(zh) if zh else None)
    return [d.get('en'), zh or d['en'], tw or d['en'], d.get('ms') or d['en'], d.get('ja') or d['en'], d.get('ko') or d['en']]


def related(slug, name, area, n=6):
    """News and articles about this project: its own articles first, then market notes and News
    articles that name the project, then ones about its area. [(kind, {lang: title}, href, date)]"""
    import datetime
    import note_links as NL
    out = []
    try:
        arts = json.load(open(os.path.join(HERE, 'project_articles.json'), encoding='utf-8'))
    except (OSError, ValueError):
        arts = []
    for a in arts:
        if a['project'] == slug:
            out.append((0, 'art', a['title'], 'article/%s.html' % a['slug'], a['date']))
    has = lambda text, ph: re.search(r'(?<![A-Za-z])%s(?![A-Za-z])' % re.escape(ph), text, re.I) is not None
    en = lambda d: d.get('en', '') if isinstance(d, dict) else (d or '')
    projs = NL.projects()
    for nt in NL.notes():
        text = ' '.join(en(nt.get(k)) for k in ('title', 'body', 'take'))
        sc = 1 if has(text, name) else (2 if slug in [p['slug'] for p in NL.related(nt, projs)] else 0)
        if sc:
            out.append((sc, 'note', nt['title'], nt['_page'], nt['date']))
    try:
        import news_pages as NP
        for aid, a in NP.ARTICLES.items():
            text = html.unescape(' '.join([a['title'], a['intro']] + [p for x in a['sections'] for p in x['paragraphs']]))
            sc = 1 if has(text, name) else (2 if area and has(html.unescape(a['title']), area) else 0)
            if sc:
                t = dict(NP.I.tr(a['title']) or {}, en=html.unescape(a['title']))
                out.append((sc, 'blog', t, 'article/%s.html' % NP.ART_SLUGS[aid], NP.iso(a['date'])))
    except Exception:
        pass
    def day(d):
        for f in ('%Y-%m-%d', '%d %b %Y'):
            try:
                return datetime.datetime.strptime(d, f).date()
            except ValueError:
                pass
        return datetime.date(2000, 1, 1)
    out.sort(key=lambda x: (x[0], -day(x[4]).toordinal()))
    return [(k, t, h, day(d)) for _, k, t, h, d in out[:n]]


def news_block(slug, name, area, T, r, rn, root):
    items = related(slug, name, area)
    if not items:
        return ''
    cards = ''
    for n, (kind, title, href, d) in enumerate(items):
        T['rel%d' % n] = _six_any(title)
        cards += '<a class="lp-nw" href="%s%s"><small>%s · %s</small>%s<span data-r="read">%s</span></a>' % (
            root, href, r('k_' + kind), d.strftime('%d %b %Y'), r('rel%d' % n, 'h3'), E(T['read'][0]))
    return '<section class="lp-sec" id="news">%s%s<div class="lp-nws">%s</div></section>' % (r('eb_news', 'span', 'lp-eb'), rn('h_news', 'h2'), cards)


DEFAULT_HEAD = '''<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" type="image/png" href="{root}images/f304c8479b1fe873.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">'''

CSS = open(os.path.join(HERE, 'landing.css'), encoding='utf-8').read()

LANGS_MENU = [('en', 'gb', 'English'), ('zh-CN', 'cn', '简体中文'), ('zh-TW', 'tw', '繁體中文'), ('ms', 'my', 'Bahasa Malaysia'), ('ja', 'jp', '日本語'), ('ko', 'kr', '한국어')]
CURS_MENU = [('MYR', 'my', 'Malaysian Ringgit'), ('USD', 'us', 'US Dollar'), ('SGD', 'sg', 'Singapore Dollar'), ('CNY', 'cn', 'Chinese Yuan'), ('JPY', 'jp', 'Japanese Yen'), ('KRW', 'kr', 'Korean Won')]
_lm = ''.join('<a data-v="%s" onclick="knSetLang(\'%s\')"><img src="{root}images/flags/%s.svg" alt="" width="20" height="15">%s</a>' % (c, c, f, n) for c, f, n in LANGS_MENU)
_cm = ''.join('<a data-v="%s" onclick="knSetCur(\'%s\')"><img src="{root}images/flags/%s.svg" alt="" width="20" height="15"><b>%s</b> %s</a>' % (c, c, f, c, n) for c, f, n in CURS_MENU)

BODY = ('<!-- class="hamburger": this page has its own menu -->\n'
        '<header class="lp-head" id="lpBar"><div class="lp-util"><a class="lp-home" href="{root}">&larr; {t_back}{t_home}</a><div class="lp-sws">'
        '<div class="lp-sw"><button type="button" class="lp-sel" onclick="knTog(\'knLangMenu\',event)"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.5 4 5.7 4 9s-1.5 6.5-4 9c-2.5-2.5-4-5.7-4-9s1.5-6.5 4-9z"/></svg><span id="knLangLab">English</span></button>'
        '<div class="lp-menu kn-menu" id="knLangMenu">' + _lm.replace('{', '{{').replace('}', '}}').replace('{{root}}', '{root}') + '</div></div>'
        '<div class="lp-sw"><button type="button" class="lp-sel" onclick="knTog(\'knCurMenu\',event)"><svg viewBox="0 0 24 24"><circle cx="8" cy="8" r="5"/><circle cx="16" cy="16" r="5"/></svg><span id="knCurLab">MYR</span></button>'
        '<div class="lp-menu kn-menu cur" id="knCurMenu">' + _cm.replace('{', '{{').replace('}', '}}').replace('{{root}}', '{root}') + '</div></div></div></div>'
        '<div class="lp-bar"><a class="lp-logo" href="{root}"><img src="{root}images/f304c8479b1fe873.png" alt="Keith Nah logo"><span><b>Keith Nah 鈞晖</b><small>Malaysia Real Estate</small></span></a>'
        '<nav class="lp-nav">{navh}</nav><a class="lp-cta" href="{wa_price}" target="_blank" rel="noopener" data-cta="lp">{t_cta}</a></div><div class="lp-chips">{navh}</div></header>\n<main>\n'
        '<div class="hA"><div class="hA-r" style="background-image:url(\'{photo}\')" role="img" aria-label="{name}">{t_tag}</div>\n'
        '<div class="hA-l"><nav class="lp-crumb" aria-label="Breadcrumb">{crumbs}</nav><div class="lp-bds">{badges}</div><h1>{name}</h1>{hook}<p class="hA-loc">{loc}</p>\n'
        '<div class="hA-p">{t_sp}<b>{price}</b></div><div class="lp-mo">{t_mo}<b>{mo}</b><a href="{root}calculator.html">{t_moch}</a></div>\n'
        '<div class="lp-btns"><a class="lp-wa" href="{wa_price}" target="_blank" rel="noopener" data-cta="lp">{chat}{t_wal}</a><a class="lp-out" href="{root}compare.html">{t_cmp}</a></div></div></div>\n'
        '<div class="lp-top"><div class="lp-facts">{factsh}</div></div>\n'
        '<section class="lp-sec" id="overview">{t_ebo}{t_hab}<p>{overview}</p>{nums}</section>\n'
        '<section class="lp-sec" id="five">{t_eb5}{t_h5}<ol class="lp-five">{five}</ol></section>\n'
        '<section class="lp-sec" id="details">{t_ebd}{t_hdet}<div class="pi"><div class="pi-head">Project Information</div><table>{details}</table></div>{fits}</section>\n'
        '{layouts}\n'
        '<section class="lp-sec" id="price">{t_ebp}{t_hp}<div class="lp-price"><div class="lp-pbox">{t_sp2}<b>{price}</b>{t_pnote}<div class="lp-row">{wb_list}</div></div>\n'
        '<div class="lp-plist">{plist}{t_calc}</div></div><div class="lp-row">{wb_units}</div></section>\n<!--VIEW-->'
        '<section class="lp-sec" id="location">{t_ebl}<h2>{loc}</h2><div class="lp-loc"><div><p>{loc_text}</p><a class="lp-map" href="{maps}" target="_blank" rel="noopener">{t_maps}</a><div class="lp-row">{wb_view}</div></div><ul>{amen}</ul></div></section>\n'
        '{video}\n{fb}\n<section class="lp-sec" id="faq">{t_ebf}{t_hfaq}<div class="lp-faq">{faqh}</div><!--DEV--></section>\n<!--NEWS-->\n'
        '<section class="lp-more">{t_more}<div class="lp-nbs">{nearby}</div><div class="lp-links"><a href="{root}compare.html">{t_lc}</a><a href="{root}projects.html">{t_la}</a>'
        '<a href="{root}foreign-buyers.html">{t_lf}</a><a href="{root}calculator.html">{t_lk}</a></div></section>\n</main>\n'
        '<footer class="lp-foot">&copy; 2026 Keith Nah Real Estate &middot; <a href="{root}">keithnah.com</a></footer>')

JS = '''<script>(function(){var T=%s,LG=%s;
function lang(){var l='en';try{l=localStorage.getItem('kn_lang')||'en'}catch(e){}return LG.indexOf(l)<0?'en':l;}
function apply(){var i=LG.indexOf(lang());document.querySelectorAll('[data-r]').forEach(function(el){var v=T[el.getAttribute('data-r')];if(!v)return;
var s=v[i]||v[0];if(el.hasAttribute('data-n'))s=s.replace('{n}',el.getAttribute('data-n'));if(el.hasAttribute('data-t'))s=s.replace('{t}',el.getAttribute('data-t'));el.textContent=s;});}
document.addEventListener('click',function(e){var t=e.target.closest('.lp-tab');if(!t)return;var k=t.getAttribute('data-t');document.querySelectorAll('.lp-tab').forEach(function(x){x.classList.toggle('on',x===t);});
document.querySelectorAll('.lp-pane').forEach(function(x){x.classList.toggle('on',x.getAttribute('data-p')===k);});});
document.addEventListener('DOMContentLoaded',function(){var s=window.knSetLang;if(typeof s==='function')window.knSetLang=function(){var r=s.apply(this,arguments);apply();return r;};apply();});
apply();
function inv(){var b=document.querySelector('.lp-inv');if(!b)return;var q=function(k){return b.querySelector('[data-v="'+k+'"]')},o=function(k,v){b.querySelector('[data-o="'+k+'"]').textContent='RM'+Math.round(v).toLocaleString('en-US')};
var sel=q('lay'),mp=parseFloat(b.getAttribute('data-mp'));function pick(){var op=sel.options[sel.selectedIndex];q('v_price').value=op.value;b.querySelector('.lp-est').hidden=op.getAttribute('data-est')!=='1';calc();}
function calc(){var op=sel.options[sel.selectedIndex],P=+q('v_price').value||0,L=P*(+q('v_loan').value||0)/100,i=(+q('v_rate').value||0)/1200,n=(+q('v_yrs').value||0)*12;
var m=n?(i?L*i/(1-Math.pow(1+i,-n)):L/n):0,mt=(+op.getAttribute('data-sq'))*mp;o('inst',m);o('maint',mt);o('cost',m+mt);}
sel.addEventListener('change',pick);b.querySelectorAll('input').forEach(function(x){x.addEventListener('input',calc)});pick();}
inv();})();</script>'''


def _best_names():
    """The "Foreign buyer best choice" project names, read from tools/build_foreign.py without running it."""
    import ast
    src = open(os.path.join(HERE, 'build_foreign.py'), encoding='utf-8').read()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(getattr(t, 'id', '') == 'BEST' for t in node.targets):
            return [n for _, names in ast.literal_eval(node.value) for n in names]
    return []


def slugs():
    idx = {p['name']: i for i, p in enumerate(A.P)}
    return [A.SLUG[idx[n]] for n in _best_names() if idx.get(n) is not None and idx[n] in A.SLUG]


BEST_SLUGS = set(slugs())   # the "Foreign buyer best choice" tag shows only on these

if __name__ == '__main__':
    if len(sys.argv) > 2:
        slug, out = sys.argv[1], sys.argv[2]
        src = open('property/%s.html' % slug, encoding='utf-8').read() if os.path.exists('property/%s.html' % slug) else None
        open(out, 'w', encoding='utf-8').write(page(slug, head_src=src))
        print('landing page:', out)
    else:
        done = []
        for s in sorted(set(A.SLUG.values())):
            f = 'property/%s.html' % s
            if not os.path.exists(f):
                continue
            src = open(f, encoding='utf-8').read()
            open(f, 'w', encoding='utf-8').write(page(s, head_src=src))
            done.append(s)
        print('landing pages: %d (%s)' % (len(done), ', '.join(done)))
