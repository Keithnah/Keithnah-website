"""Home page "Articles" cards (#articles in index.html): translated in all six languages and linked
to each article's own page.

The cards are written by hand in index.html (category, date, title, excerpt). This script looks each
card up in the News articles (tools/news_pages.py), links it to article/<slug>.html, and adds the
article's own translations (tools/news_i18n.py), so the cards follow the visitor's language like the
rest of the page. Dates are shown in the visitor's language too. Safe to run again.

    python3 tools/externalize.py in
    python3 tools/build_home_articles.py
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
import news_pages as NP  # noqa: E402

LG = ['zh-CN', 'zh-TW', 'ms', 'ja', 'ko']
U = lambda s: html.unescape(s).strip()


def tr(text, fallback=None):
    t = NP.I.tr(U(text)) or (fallback() if fallback else {}) or {}
    return {l: t.get(l) for l in LG if t.get(l)}


def main():
    s = open('index.html', encoding='utf-8').read()
    m = re.search(r'<section id="articles">.*?</section>', s, re.S)
    sec = m.group(0)
    sec = re.sub(r'<script id="kn-home-art">.*?</script>', '', sec, flags=re.S)
    by_title = {U(a['title']): k for k, a in NP.ARTICLES.items()}
    T = {}

    def card(cm):
        whole = cm.group(0)
        title = re.search(r'<h3[^>]*>(.*?)</h3>', whole, re.S).group(1)
        aid = by_title.get(U(re.sub(r'<[^>]+>', '', title)))
        n = len(T) // 4
        cat = re.search(r'<span class="article-prev-cat"[^>]*>(.*?)</span>', whole, re.S).group(1)
        exc = re.search(r'<p[^>]*>(.*?)</p>', whole, re.S).group(1)
        T['c%d' % n] = tr(cat)
        T['t%d' % n] = tr(title)
        T['p%d' % n] = tr(exc, (lambda: NP.tr_excerpt(NP.ARTICLES[aid]['intro'])) if aid else None)
        T['d%d' % n] = {}
        out = re.sub(r'<span class="article-prev-cat"[^>]*>', '<span class="article-prev-cat" data-ha="c%d">' % n, whole, count=1)
        out = re.sub(r'<h3[^>]*>', '<h3 data-ha="t%d">' % n, out, count=1)
        out = re.sub(r'<p[^>]*>', '<p data-ha="p%d">' % n, out, count=1)
        dm = re.search(r'<span class="article-prev-date"[^>]*>(.*?)</span>', out, re.S)
        if dm and aid:
            out = out.replace(dm.group(0), '<span class="article-prev-date" data-date="%s">%s</span>' % (NP.iso(NP.ARTICLES[aid]['date']), dm.group(1)), 1)
        if aid:
            out = re.sub(r'href="[^"]*"', 'href="article/%s.html"' % NP.ART_SLUGS[aid], out, count=1)
        return out

    sec = re.sub(r'<a class="article-prev-card".*?</a>', card, sec, flags=re.S)
    T = {k: v for k, v in T.items() if v}
    js = ('<script id="kn-home-art">(function(){var T=%s;function cur(){var l="en";try{l=localStorage.getItem("kn_lang")||"en"}catch(e){}return l;}'
          'function f(){var l=cur();document.querySelectorAll("#articles [data-ha]").forEach(function(el){var k=el.getAttribute("data-ha");'
          'if(!el.hasAttribute("data-en"))el.setAttribute("data-en",el.innerHTML);var v=T[k]&&T[k][l];el.innerHTML=(l!=="en"&&v)?v:el.getAttribute("data-en");});'
          'document.querySelectorAll("#articles [data-date]").forEach(function(el){try{el.textContent=new Date(el.getAttribute("data-date")+"T12:00:00").toLocaleDateString(l==="en"?"en-GB":l,{day:"numeric",month:"short",year:"numeric"});}catch(e){}});}'
          'f();document.addEventListener("DOMContentLoaded",function(){["setLanguage","knSetLang"].forEach(function(n){var s=window[n];if(typeof s==="function")window[n]=function(){var r=s.apply(this,arguments);f();return r;};});f();});})();</script>'
          ) % json.dumps(T, ensure_ascii=False).replace('</', '<\\/')
    sec = sec[:-len('</section>')] + js + '</section>'
    s = s[:m.start()] + sec + s[m.end():]
    open('index.html', 'w', encoding='utf-8').write(s)
    print('home articles: %d cards, %d translated texts' % (len(re.findall(r'class="article-prev-card"', sec)), len(T)))


if __name__ == '__main__':
    main()
