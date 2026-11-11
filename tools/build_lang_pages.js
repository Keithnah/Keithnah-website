/* Build a real, crawlable copy of every page in each site language: /zh/, /zh-tw/, /ms/, /ja/, /ko/.

The English pages translate themselves in the browser (kn_lang). Search engines only index what is
in the HTML, so this renders each English page in Chromium with the language set, cleans up the
parts scripts rebuild on load (maps), points links at the same language, and saves the result.
Every version gets hreflang alternates and a self canonical; the sitemap lists them all.
Only pages whose English source (or the shared project translations) changed are rendered again.

    node tools/build_lang_pages.js          (run by tools/build_all.py)
    node tools/build_lang_pages.js --all    (render everything again)
*/
const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const SITE = 'https://keithnah.com';
const LANGS = { 'zh-CN': 'zh', 'zh-TW': 'zh-tw', ms: 'ms', ja: 'ja', ko: 'ko' };
const HREFLANG = { en: 'en', 'zh-CN': 'zh-Hans', 'zh-TW': 'zh-Hant', ms: 'ms', ja: 'ja', ko: 'ko' };
const DIRS = ['', 'article', 'area', 'best', 'guides', 'property', 'topic'];
const CACHE = path.join(__dirname, 'lang_pages_cache.json');
const VERSION = '1';
const ALL = process.argv.includes('--all');
const ONLY = (process.argv.find(a => a.startsWith('--only=')) || '').slice(7);

/* Runs first on every page (English and translated). The page language comes from the URL:
   a translated page saves its language, an English page sends a visitor who chose another language
   to that version, and choosing a language anywhere (every switcher saves kn_lang) opens that version. */
const HEAD_JS = `<script id="kn-lang-url">(function(){var M=${JSON.stringify(LANGS)},R=/^\\/(zh|zh-tw|ms|ja|ko)(\\/.*)$/,p=location.pathname,m=p.match(R),P=document.documentElement.getAttribute('data-page-lang')||'en',en=m?m[2]:p;
function u(l){return (l==='en'?'':'/'+M[l])+en+location.search+location.hash;}window.knLangUrl=u;
var S=Storage.prototype.setItem;function go(l){if(window.KN_RENDER||l===P||(l!=='en'&&!M[l]))return;location.href=u(l);}
Storage.prototype.setItem=function(k,v){S.apply(this,arguments);if(k==='kn_lang'&&this===window.localStorage)go(String(v));};
if(P!=='en')['pushState','replaceState'].forEach(function(n){var f=history[n];history[n]=function(s,t,x){if(x!=null&&!/^[a-z]+:|^\\//i.test(String(x)))x=new URL(String(x),location.href).href;return f.call(this,s,t,x);};});
try{if(P!=='en')S.call(localStorage,'kn_lang',P);else if(!window.KN_RENDER){var s=localStorage.getItem('kn_lang');if(s&&M[s])location.replace(u(s));}}catch(e){}})();</script>`;

function pages() {
  const out = [];
  for (const d of DIRS) {
    const dir = path.join(ROOT, d);
    for (const f of fs.readdirSync(dir).sort()) if (f.endsWith('.html')) out.push(d ? d + '/' + f : f);
  }
  return out;
}
const sha = s => crypto.createHash('sha1').update(s).digest('hex').slice(0, 16);

/* Add the head script and hreflang/canonical tags to an English page (idempotent). */
function tagEnglish(rel) {
  const p = path.join(ROOT, rel);
  let t = fs.readFileSync(p, 'utf8');
  const o = t;
  t = t.replace(/<script id="kn-lang-url">[\s\S]*?<\/script>\n?/, '').replace(/<!-- KN-HREFLANG -->[\s\S]*?<!-- \/KN-HREFLANG -->\n?/, '');
  t = t.replace(/<head([^>]*)>/i, m => m + '\n' + HEAD_JS + '\n' + altTags(rel, 'en'));
  if (t !== o) fs.writeFileSync(p, t);
  return t;
}
function urlFor(rel, l) {
  const pth = rel === 'index.html' ? '/' : '/' + rel;
  return SITE + (l === 'en' ? '' : '/' + LANGS[l]) + pth;
}
function altTags(rel, self) {
  let h = '<!-- KN-HREFLANG -->';
  for (const l of ['en', ...Object.keys(LANGS)]) h += `<link rel="alternate" hreflang="${HREFLANG[l]}" href="${urlFor(rel, l)}">`;
  h += `<link rel="alternate" hreflang="x-default" href="${urlFor(rel, 'en')}">`;
  if (self !== 'en') h += `<link rel="canonical" href="${urlFor(rel, self)}">`;
  return h + '<!-- /KN-HREFLANG -->';
}

function serve() {
  const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.ico': 'image/x-icon' };
  return new Promise(res => {
    const s = http.createServer((q, r) => {
      let u = decodeURIComponent(q.url.split('?')[0]);
      if (u.endsWith('/')) u += 'index.html';
      const f = path.join(ROOT, u);
      if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end(); }
      const ext = path.extname(f);
      if (/\.(jpg|png|webp|gif|mp4)$/.test(ext)) { r.writeHead(204); return r.end(); } // images are not needed to render text
      r.writeHead(200, { 'Content-Type': types[ext] || 'application/octet-stream' });
      fs.createReadStream(f).pipe(r);
    }).listen(0, '127.0.0.1', () => res(s));
  });
}

async function render(ctx, base, rel, lang, all) {
  const page = await ctx.newPage();
  await page.addInitScript(l => { window.KN_RENDER = 1; try { localStorage.setItem('kn_lang', l); localStorage.setItem('kn_currency', 'MYR'); } catch (e) {} }, lang);
  await page.route(/^https?:\/\/(?!127\.0\.0\.1)/, r => r.abort()); // stay offline: fonts, analytics, video embeds
  await page.goto(base + '/' + rel, { waitUntil: 'load' });
  await page.waitForTimeout(250);
  const html = await page.evaluate(([rel, lang, dirName, all, site]) => {
    const src = new DOMParser().parseFromString(window.__KN_SRC__ || '', 'text/html');
    // Maps are drawn by script on load: put back the empty container from the English source.
    document.querySelectorAll('.leaflet-container').forEach(el => {
      const o = el.id && src.getElementById(el.id);
      if (o) el.replaceWith(document.importNode(o, true));
    });
    const enUrl = new URL(site + '/' + rel);
    const prefix = '/' + dirName;
    document.querySelectorAll('a[href]').forEach(a => {
      const h = a.getAttribute('href');
      if (!h || /^(mailto:|tel:|javascript:|data:)/i.test(h)) return;
      if (h.startsWith('#')) { a.setAttribute('href', prefix + enUrl.pathname.replace(/\/index\.html$/, '/') + h); return; }
      let u; try { u = new URL(h, enUrl); } catch (e) { return; }
      if (u.origin !== site) return;
      let p = u.pathname; if (p.endsWith('/')) p += 'index.html';
      const key = p.slice(1);
      if (!all.includes(key)) return;
      a.setAttribute('href', prefix + (key === 'index.html' ? '/' : '/' + key) + u.search + u.hash);
    });
    document.documentElement.setAttribute('lang', lang);
    document.documentElement.setAttribute('data-page-lang', lang);
    document.querySelectorAll('link[rel="canonical"]').forEach(l => l.remove());
    const og = document.querySelector('meta[property="og:url"]');
    if (og) og.setAttribute('content', site + prefix + enUrl.pathname.replace(/\/index\.html$/, '/'));
    // Title and description in the page language: from the translated heading and first paragraph.
    const clean = s => (s || '').replace(/\s+/g, ' ').trim();
    const hx = document.querySelector('main h1, h1');
    let h1 = '';
    if (hx) { const c = hx.cloneNode(true); c.querySelectorAll('[aria-hidden="true"]').forEach(e => e.remove()); c.querySelectorAll('br').forEach(e => e.replaceWith(' ')); h1 = clean(c.textContent); if (/^(zh|ja)/.test(lang)) h1 = h1.replace(/([\u3000-\u9fff\uff00-\uffef]) (?=[\u3000-\u9fff\uff00-\uffef])/g, '$1'); }
    if (h1 && lang !== 'en') document.title = h1 + ' | Keith Nah';
    const md = document.querySelector('meta[name="description"]');
    const para = [...document.querySelectorAll('main p, section p, .hero p')].map(e => clean(e.textContent)).find(s => s.length > 40 && !/[a-z]{4,} [a-z]{4,} [a-z]{4,}/i.test(s) || (lang === 'ms' && s.length > 60));
    if (md && para) md.setAttribute('content', para.length > 160 ? para.slice(0, 157) + '…' : para);
    ['og:title', 'twitter:title'].forEach(k => { const m = document.querySelector('meta[property="' + k + '"],meta[name="' + k + '"]'); if (m && h1) m.setAttribute('content', document.title); });
    ['og:description', 'twitter:description'].forEach(k => { const m = document.querySelector('meta[property="' + k + '"],meta[name="' + k + '"]'); if (m && para) m.setAttribute('content', md ? md.getAttribute('content') : para); });
    const doc = document.documentElement.outerHTML;
    return '<!DOCTYPE html>\n' + doc;
  }, [rel, lang, LANGS[lang], all, SITE]);
  await page.close();
  return html;
}

(async () => {
  const all = pages().filter(r => !ONLY || r === ONLY);
  const src = {};
  for (const r of all) src[r] = tagEnglish(r);
  const shared = sha(VERSION + HEAD_JS + fs.readdirSync(ROOT).filter(f => /^i18n-projects-.*\.js$/.test(f)).sort().map(f => fs.readFileSync(path.join(ROOT, f), 'utf8')).join('') + fs.readFileSync(__filename, 'utf8'));
  let cache = {};
  try { cache = JSON.parse(fs.readFileSync(CACHE, 'utf8')); } catch (e) {}
  const todo = all.filter(r => ALL || cache[r] !== sha(shared + src[r]) || Object.values(LANGS).some(d => !fs.existsSync(path.join(ROOT, d, r))));
  const server = await serve();
  const base = 'http://127.0.0.1:' + server.address().port;
  const browser = await chromium.launch();
  // A fresh context for every page: each has its own localStorage, so languages never mix.
  async function newCtx() {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await ctx.route(base + '/**', async r => {
    const u = new URL(r.request().url());
    const rel = decodeURIComponent(u.pathname).replace(/^\//, '').replace(/(^|\/)$/, '$1index.html');
    if (src[rel] && r.request().resourceType() === 'document') {
      const t = src[rel].replace(/<head([^>]*)>/i, m => m + '<script>window.__KN_SRC__=' + JSON.stringify(src[rel]).replace(/</g, '\\u003c') + ';</script>');
      return r.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: t });
    }
    return r.continue();
  });
  return ctx;
  }
  const allPages = pages();
  const jobs = [];
  for (const r of todo) for (const l of Object.keys(LANGS)) jobs.push([r, l]);
  let done = 0, fail = 0;
  async function worker() {
    while (jobs.length) {
      const [r, l] = jobs.shift();
      try {
        const ctx = await newCtx();
        let h;
        try { h = await render(ctx, base, r, l, allPages); } finally { await ctx.close(); }
        h = h.split(base + '/').join('/').split(base).join('');
        h = h.replace(/<script>window\.__KN_SRC__=[\s\S]*?;<\/script>/, '');
        h = h.replace(/<!-- KN-HREFLANG -->[\s\S]*?<!-- \/KN-HREFLANG -->/, altTags(r, l));
        h = h.replace(/<head([^>]*)>/i, m => m + '<base href="/' + (path.dirname(r) === '.' ? '' : path.dirname(r) + '/') + '">');
        const out = path.join(ROOT, LANGS[l], r);
        fs.mkdirSync(path.dirname(out), { recursive: true });
        fs.writeFileSync(out, h);
        done++;
      } catch (e) { fail++; console.error('failed', l, r, e.message.split('\n')[0]); }
    }
  }
  await Promise.all(Array.from({ length: 6 }, worker));
  await browser.close(); server.close();
  if (!fail) for (const r of todo) cache[r] = sha(shared + src[r]);
  if (!ONLY) {
    for (const k of Object.keys(cache)) if (!src[k]) delete cache[k];
    // remove translated copies of pages that no longer exist
    for (const d of Object.values(LANGS)) for (const sub of DIRS) {
      const dir = path.join(ROOT, d, sub);
      if (!fs.existsSync(dir)) continue;
      for (const f of fs.readdirSync(dir)) if (f.endsWith('.html') && !src[sub ? sub + '/' + f : f]) fs.unlinkSync(path.join(dir, f));
    }
    sitemap(all);
  }
  fs.writeFileSync(CACHE, JSON.stringify(cache, null, 0));
  console.log(`language pages: ${todo.length} page(s) x ${Object.keys(LANGS).length} languages rendered, ${fail} failed`);
  if (fail) process.exit(1);
})();

/* Add every language version to sitemap.xml next to its English page. */
function sitemap(all) {
  const p = path.join(ROOT, 'sitemap.xml');
  let t = fs.readFileSync(p, 'utf8');
  t = t.replace(/\s*<url><loc>https:\/\/keithnah\.com\/(zh|zh-tw|ms|ja|ko)\/[\s\S]*?<\/url>/g, '');
  t = t.replace(/(\s*)<url>\s*<loc>([^<]+)<\/loc>([\s\S]*?)<\/url>/g, (m, sp, loc, rest) => {
    const rel = loc.replace(SITE + '/', '') || 'index.html';
    if (!all.includes(rel)) return m;
    const lm = (rest.match(/<lastmod>[^<]+<\/lastmod>/) || [''])[0];
    return m + Object.keys(LANGS).map(l => `${sp}<url><loc>${urlFor(rel, l)}</loc>${lm}</url>`).join('');
  });
  fs.writeFileSync(p, t);
}
