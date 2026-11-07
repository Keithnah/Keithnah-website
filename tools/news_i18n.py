"""Translations for the News page guides and the article and topic pages.

Sources, in order:
  1. tools/i18n/news_<lang>.json: guides, topic descriptions, corrected
     article text and page labels (aligned with tools/i18n/news_en.json)
  2. LABELS in tools/news_content.py: section and topic names
  3. the translation table already in blog.html (TR): article text
  4. the site menu translations in blog.html (DIC)
"""
import html
import json
import os
import re

from news_content import EXTRA_TR, LABELS

LANGS = ['zh-CN', 'zh-TW', 'ms', 'ta', 'ja', 'ko', 'ar']
HERE = os.path.dirname(os.path.abspath(__file__))


def T(s):
    """Text as the browser serialises it in innerHTML."""
    return html.escape(html.unescape(s), quote=False)


def _load_news():
    en = json.load(open(os.path.join(HERE, 'i18n', 'news_en.json'), encoding='utf-8'))
    out = {s: {} for s in en}
    for l in LANGS:
        path = os.path.join(HERE, 'i18n', 'news_%s.json' % l)
        if not os.path.exists(path):
            continue
        tr = json.load(open(path, encoding='utf-8'))
        assert len(tr) == len(en), (l, len(tr), len(en))
        for e, x in zip(en, tr):
            out[e][l] = x
    return out


NEWS = _load_news()

_blog = open('blog.html', encoding='utf-8').read()


def _obj(name):
    i = _blog.index('const %s = ' % name) + len('const %s = ' % name)
    return json.JSONDecoder().raw_decode(_blog[i:])[0]


PAGE_TR = _obj('TR')
DIC = _obj('DIC')

# Article stat labels are stored inside the popup's combined value+label markup
STAT = {}
for key, val in PAGE_TR.items():
    m = re.search(r'<span class="reader-stat-label">(.*?)</span>', key)
    if m and isinstance(val, dict):
        STAT[html.unescape(m.group(1))] = {l: html.unescape(re.sub(r'.*<span class="reader-stat-label">(.*?)</span>.*', r'\1', v, flags=re.S))
                                           for l, v in val.items()}


def tr(en):
    """{lang: translation} for an English string (plain text), or {}."""
    e = html.unescape(en)
    m = re.fullmatch(r'(\d{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{4})', e)
    if m:
        d, mo, y = int(m.group(1)), 'JanFebMarAprMayJunJulAugSepOctNovDec'.index(m.group(2)) // 3 + 1, m.group(3)
        cjk = '%s年%d月%d日' % (y, mo, d)
        return {'zh-CN': cjk, 'zh-TW': cjk, 'ja': cjk, 'ko': '%s년 %d월 %d일' % (y, mo, d), 'ms': e, 'ta': e, 'ar': e}
    for src in (EXTRA_TR.get(e), NEWS.get(e), LABELS.get(e)):
        if src:
            return dict(src)
    for key in (T(e), e):
        v = PAGE_TR.get(key)
        if isinstance(v, dict) and v:
            return {l: html.unescape(x) for l, x in v.items()}
    if e in STAT:
        return STAT[e]
    if e in DIC:
        return dict(DIC[e])
    return {}


def fmt(template_en, **parts):
    """Translate a template such as 'Read our {guide} guide.' with translated parts."""
    base = tr(template_en)
    out = {}
    for l in LANGS:
        s = base.get(l, template_en)
        for k, v in parts.items():
            s = s.replace('{%s}' % k, tr(v).get(l, v))
        out[l] = s
    return out


LANG_NAMES = [('en', 'English', 'gb'), ('zh-CN', '简体中文', 'cn'), ('zh-TW', '繁體中文', 'tw'), ('ms', 'Bahasa Malaysia', 'my'),
              ('ta', 'தமிழ்', 'in'), ('ja', '日本語', 'jp'), ('ko', '한국어', 'kr'), ('ar', 'العربية', 'sa')]


class Collector:
    """Collects the translatable text of one page. tt() returns the HTML to place in the page."""

    def __init__(self):
        self.items = []
        self.index = {}

    def add(self, en, translations=None):
        key = html.unescape(en)
        if key in self.index:
            return self.index[key]
        t = translations if translations is not None else tr(key)
        if not t:
            return None
        self.items.append(dict({'en': T(key)}, **{l: T(v) for l, v in t.items() if v}))
        self.index[key] = len(self.items) - 1
        return self.index[key]

    def tt(self, en, translations=None, tag='span'):
        i = self.add(en, translations)
        if i is None:
            return T(en)
        return '<%s data-t="%d">%s</%s>' % (tag, i, T(en), tag)

    def script(self):
        return '<script>var KN_T = %s;</script>' % json.dumps(self.items, ensure_ascii=False).replace('</', '<\\/')


MENU_CSS = r"""
.kn-lang{position:relative;}
.kn-lang-btn{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.35);border:1px solid rgba(17,17,17,0.15);color:#111;padding:8px 14px;border-radius:100px;font:600 12px 'Inter',sans-serif;cursor:pointer;white-space:nowrap;}
.kn-lang-menu{display:none;position:absolute;top:calc(100% + 8px);right:0;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 16px 40px rgba(17,17,17,0.14);min-width:210px;padding:8px;z-index:80;}
.kn-lang.open .kn-lang-menu{display:block;}
.kn-lang-menu button{display:flex;align-items:center;gap:10px;width:100%;text-align:left;padding:9px 12px;border:0;background:none;border-radius:8px;font:500 13.5px 'Inter',sans-serif;color:#111;cursor:pointer;white-space:nowrap;}
.kn-lang-menu button:hover{background:var(--bg);} .kn-lang-menu button.active{color:var(--gold);font-weight:700;}
.kn-flag{width:20px;height:15px;flex:0 0 20px;border-radius:2px;object-fit:cover;box-shadow:0 0 0 1px rgba(0,0,0,0.08);}
.hdr-right{display:flex;align-items:center;gap:10px;}
@media (hover:hover) and (pointer:fine){ .kn-lang::after{content:'';position:absolute;left:0;right:0;top:100%;height:12px;} }
html[dir=rtl] .art-body,html[dir=rtl] .topic-head,html[dir=rtl] .acard{text-align:right;}
"""


def menu_html(up='../'):
    items = ''.join('<button type="button" data-lang="%s"><img class="kn-flag" src="%simages/flags/%s.svg" alt="" width="20" height="15">%s</button>' % (
        c, up, f, html.escape(n)) for c, n, f in LANG_NAMES)
    return ('<div class="kn-lang" id="knLang"><button type="button" class="kn-lang-btn" aria-haspopup="true">'
            '<img class="kn-flag" src="%simages/flags/gb.svg" alt="" width="20" height="15"><span>English</span></button>'
            '<div class="kn-lang-menu" role="menu">%s</div></div>' % (up, items))


MENU_JS = r"""<script>
(function(){
  var NAMES = __NAMES__, box = document.getElementById('knLang');
  var hover = window.matchMedia && matchMedia('(hover:hover) and (pointer:fine)').matches;
  function apply(l){
    if(!NAMES[l]) l = 'en';
    document.documentElement.lang = l === 'en' ? 'en' : l;
    document.documentElement.dir = l === 'ar' ? 'rtl' : 'ltr';
    document.querySelectorAll('[data-t]').forEach(function(el){ var it = KN_T[+el.getAttribute('data-t')]; if(it) el.innerHTML = it[l] || it.en; });
    document.querySelectorAll('[data-date]').forEach(function(el){
      try{ el.textContent = new Date(el.getAttribute('data-date') + 'T12:00:00').toLocaleDateString(l === 'en' ? 'en-GB' : l, {day:'numeric', month:'short', year:'numeric'}); }catch(e){}
    });
    var b = box.querySelector('.kn-lang-btn'); b.querySelector('span').textContent = NAMES[l][0]; b.querySelector('img').src = b.querySelector('img').src.replace(/flags\/[a-z]+\.svg/, 'flags/' + NAMES[l][1] + '.svg');
    box.querySelectorAll('.kn-lang-menu button').forEach(function(x){ x.classList.toggle('active', x.getAttribute('data-lang') === l); });
  }
  var saved = 'en'; try{ saved = localStorage.getItem('kn_lang') || 'en'; }catch(e){}
  apply(saved);
  box.querySelector('.kn-lang-btn').addEventListener('click', function(e){ e.stopPropagation(); if(hover) box.classList.add('open'); else box.classList.toggle('open'); });
  if(hover){ box.addEventListener('mouseenter', function(){ box.classList.add('open'); }); box.addEventListener('mouseleave', function(){ box.classList.remove('open'); }); }
  box.querySelectorAll('.kn-lang-menu button').forEach(function(x){ x.addEventListener('click', function(){ var l = x.getAttribute('data-lang'); try{ localStorage.setItem('kn_lang', l); }catch(e){} apply(l); box.classList.remove('open'); }); });
  document.addEventListener('click', function(e){ if(!box.contains(e.target)) box.classList.remove('open'); });
  document.addEventListener('keydown', function(e){ if(e.key === 'Escape') box.classList.remove('open'); });
})();
</script>"""


def menu_js():
    return MENU_JS.replace('__NAMES__', json.dumps({c: [n, f] for c, n, f in LANG_NAMES}, ensure_ascii=False))
