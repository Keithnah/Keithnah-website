"""The page-top design (Keith's choice "B": text on the left, three photos on the right, a stats card on the photos,
light lavender background). Used by build_heroes.py (main pages, developer pages) and build_maps.py.

Texts written here switch language in the browser through data-khx keys (see script())."""
import html
import json

LANGS = ['en', 'zh-CN', 'zh-TW', 'ms', 'ja', 'ko']
E = lambda s: html.escape(str(s), quote=True)
try:
    import opencc
    _cc = opencc.OpenCC('s2tw').convert
except Exception:
    _cc = lambda s: s


def L(en, zh, ms, ja, ko):
    return {'en': en, 'zh-CN': zh, 'zh-TW': _cc(zh), 'ms': ms, 'ja': ja, 'ko': ko}


class Tx:
    """Collects the texts one page uses, so the page carries only its own dictionary."""
    def __init__(self):
        self.d = {}

    def __call__(self, key, d, tag='span', cls='', **fmt):
        d = {l: v.format(**fmt) if fmt else v for l, v in d.items()}
        self.d[key] = d
        return '<%s data-khx="%s"%s>%s</%s>' % (tag, key, (' class="%s"' % cls) if cls else '', E(d['en']), tag)

    def script(self):
        return ('<script>(function(){var T=%s;function lg(){var l="en";try{l=document.documentElement.getAttribute("data-page-lang")||localStorage.getItem("kn_lang")||"en"}catch(e){}return l;}'
                'function go(){var l=lg();document.querySelectorAll("[data-khx]").forEach(function(e){var d=T[e.getAttribute("data-khx")];if(d&&(d[l]||d.en))e.textContent=d[l]||d.en;});}'
                'go();document.addEventListener("DOMContentLoaded",go);var w=window.knSetLang;if(typeof w==="function"){window.knSetLang=function(){var r=w.apply(this,arguments);go();return r;};}})();</script>'
                ) % json.dumps(self.d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


CSS = '''<style id="knb-css">
.knb{position:relative;overflow:hidden;isolation:isolate;padding:118px 0 70px;font-family:Inter,sans-serif;background:radial-gradient(700px 420px at 92% 18%,rgba(94,96,206,.20),transparent 65%),radial-gradient(620px 380px at 8% 95%,rgba(186,170,255,.30),transparent 65%),radial-gradient(500px 300px at 45% 0%,rgba(255,214,231,.35),transparent 70%),linear-gradient(180deg,#f1effc 0%,#f6f4fb 60%,#F9F8F6 100%)}
.knb:before{content:"";position:absolute;inset:0;z-index:-1;background-image:radial-gradient(rgba(94,96,206,.16) 1.2px,transparent 1.4px);background-size:26px 26px;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 55%);mask-image:linear-gradient(90deg,transparent 0,#000 55%)}
.knb:after{content:"";position:absolute;z-index:-1;left:0;right:0;bottom:0;height:1px;background:linear-gradient(90deg,transparent,rgba(94,96,206,.25),transparent)}
.knb *{box-sizing:border-box}.knb-in{max-width:1240px;margin:0 auto;padding:0 5vw;display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:56px;align-items:center}.knb-in>div{min-width:0}
.knb .knb-cr,.knb nav.crumb{display:flex;flex-wrap:wrap;gap:8px;font:600 13px Inter,sans-serif;color:#77768c;margin:0 0 18px;padding:0;background:none}.knb .knb-cr a,.knb nav.crumb a{color:#5E60CE}.knb .knb-cr i{font-style:normal;opacity:.5}
.knb .knb-eb,.knb .eb,.knb .eyebrow{display:block;font:600 13px Inter,sans-serif!important;letter-spacing:.28em!important;text-transform:uppercase;color:#5E60CE!important;margin:0;background:none!important;padding:0!important}
.knb h1{font:700 clamp(36px,4.2vw,58px)/1.08 'Playfair Display',serif!important;color:#111!important;margin:14px 0 16px!important;letter-spacing:-.01em;text-align:left!important;max-width:none}
.knb h1 em,.knb h1>span:not([data-khx]){font-style:italic;color:#5E60CE!important}
.knb-in>div:first-child>p{font-size:clamp(15.5px,1.4vw,17.5px)!important;line-height:1.7!important;color:#4a4960!important;max-width:680px;margin:0 0 10px!important;text-align:left!important}
.knb-pl{display:flex;flex-wrap:wrap;gap:10px;margin-top:24px}.knb-pl a,.knb .btns a{display:inline-flex;align-items:center;gap:8px;font:700 14.5px Inter,sans-serif;padding:12px 18px;border-radius:14px;background:#fff;border:1px solid rgba(94,96,206,.25);color:#15142b;box-shadow:0 6px 16px rgba(29,27,79,.05);text-decoration:none;transition:transform .2s}
.knb-pl a:after{content:"\\2192";color:#5E60CE}.knb-pl a:first-child{background:#5E60CE;color:#fff;border-color:#5E60CE}.knb-pl a:first-child:after{color:#fff}.knb-pl a:hover{transform:translateY(-2px)}
.knb .btns{display:flex;flex-wrap:wrap;gap:10px;margin-top:24px}
.knb-ph{position:relative;display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);grid-template-rows:1fr 1fr;gap:12px;height:440px}
.knb-ph img{display:block;min-width:0;min-height:0;width:100%;height:100%;object-fit:cover;border-radius:22px;box-shadow:0 18px 40px rgba(29,27,79,.14);background:#e9e8f3}.knb-ph img:first-child{grid-row:1/3}
.knb-sc{position:absolute;left:-36px;bottom:-30px;max-width:calc(100% + 20px);background:#fff;border-radius:20px;padding:18px 22px;display:grid;grid-template-columns:1fr 1fr;gap:14px 28px;box-shadow:0 22px 50px rgba(29,27,79,.18);border:1px solid rgba(94,96,206,.12)}
.knb-sc>div,.knb-sc .dvs>div{background:none!important;border:0!important;padding:0!important;box-shadow:none!important;margin:0!important}
.knb-sc b{display:block;font:700 26px/1.1 'Playfair Display',serif!important;color:#5E60CE!important}.knb-sc small{display:block;font:600 11px Inter,sans-serif!important;letter-spacing:.14em;text-transform:uppercase;color:#55546b!important;margin-top:5px}
.knb-sc .dvs{display:contents!important}.knb-sc .aw b{font-size:18px!important}
.knb-below{max-width:1240px;margin:34px auto 0;padding:0 5vw}
@media(max-width:900px){.knb{padding:100px 0 80px}.knb-in{grid-template-columns:minmax(0,1fr);gap:30px}.knb-ph{height:300px}.knb-sc{left:12px;right:12px;bottom:-46px;max-width:none}}
@media(max-width:480px){.knb-sc{padding:14px 16px;gap:10px 18px}.knb-sc b{font-size:21px!important}}
</style>'''


def crumbs(items):
    """items: [(label_html, href or None)]"""
    return '<div class="knb-cr">' + '<i>/</i>'.join(('<a href="%s">%s</a>' % (h, n)) if h else '<span>%s</span>' % n for n, h in items) + '</div>'


def pills(items):
    return '<div class="knb-pl">' + ''.join('<a href="%s"%s>%s</a>' % (h, ' target="_blank" rel="noopener"' if h.startswith('http') else '', n) for n, h in items) + '</div>'


def stats_html(stats):
    return ''.join('<div><b>%s</b><small>%s</small></div>' % s for s in stats)


def hero(left, imgs, stats_inner, below=''):
    """left: the text column (crumbs, eyebrow, h1, paragraphs, pills). imgs: 3 image paths. stats_inner: the stats card content."""
    imgs = (list(imgs) + list(imgs))[:3] if imgs else []
    ph = ''.join('<img src="%s" alt="" %s decoding="async" width="900" height="600">' % (E(s), 'fetchpriority="high"' if i == 0 else 'loading="lazy"') for i, s in enumerate(imgs))
    return ('<!-- KNB-HERO --><section class="knb"><div class="knb-in"><div>%s</div><div class="knb-ph">%s<div class="knb-sc">%s</div></div></div>%s</section>' % (
        left, ph, stats_inner, ('<div class="knb-below">%s</div>' % below) if below else ''))
