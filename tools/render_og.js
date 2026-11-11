/* Draw the 1200x630 share images (link previews on WhatsApp, Facebook, Telegram...).
   Called by tools/build_og.py with a JSON list of jobs: {out, eb, t, sub, imgs, vs}. */
const fs = require('fs');
const path = require('path');
const http = require('http');
const { chromium } = require('playwright');
const ROOT = path.resolve(__dirname, '..');
const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const esc = s => String(s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function card(o, base) {
  const len = o.t.length;
  const size = o.vs ? (len > 44 ? 48 : 58) : (len > 70 ? 44 : len > 50 ? 50 : len > 32 ? 58 : 66);
  return `<html><head><link href="https://fonts.googleapis.com/css2?family=Inter:wght@600;800&family=Playfair+Display:wght@700&display=swap" rel="stylesheet"><style>
*{margin:0;padding:0;box-sizing:border-box}body{width:1200px;height:630px;font-family:Inter,Arial,sans-serif;overflow:hidden;position:relative;background:#1d1b4f}
.bg{position:absolute;inset:0;display:flex}.bg img{flex:1;min-width:0;height:100%;object-fit:cover}
.sh{position:absolute;inset:0;background:linear-gradient(90deg,rgba(17,15,52,.95) 0%,rgba(17,15,52,.84) 48%,rgba(17,15,52,.2) 100%)}
.sh.vs{background:linear-gradient(0deg,rgba(17,15,52,.96) 0%,rgba(17,15,52,.6) 55%,rgba(17,15,52,.12) 100%)}
.c{position:absolute;left:64px;top:56px;right:${o.vs ? '64px' : '420px'};bottom:118px;display:flex;flex-direction:column;justify-content:${o.vs ? 'flex-end' : 'center'}}
.eb{display:inline-block;align-self:flex-start;background:#5E60CE;color:#fff;font:800 18px Inter;letter-spacing:.14em;text-transform:uppercase;padding:8px 16px;border-radius:100px;margin-bottom:22px;max-width:100%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
h1{font:700 ${size}px/1.13 'Playfair Display',Georgia,serif;color:#fff;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}
.sub{margin-top:18px;font:800 28px Inter;color:#ffd166}
.ft{position:absolute;left:0;right:0;bottom:0;height:96px;background:#fff;display:flex;align-items:center;padding:0 64px;gap:18px}
.ft img{width:58px;height:58px;border-radius:50%}.ft b{font:700 26px 'Playfair Display',serif;color:#111}.ft span{font:600 20px Inter;color:#5E60CE;margin-left:auto}
.vsb{position:absolute;left:50%;top:140px;transform:translateX(-50%);width:110px;height:110px;border-radius:50%;background:#5E60CE;color:#fff;font:700 40px 'Playfair Display';display:flex;align-items:center;justify-content:center;border:6px solid #fff}
</style></head><body><div class="bg">${o.imgs.map(i => `<img src="${base}/${i}">`).join('')}</div><div class="sh ${o.vs ? 'vs' : ''}"></div>${o.vs ? '<div class="vsb">VS</div>' : ''}
<div class="c"><span class="eb">${esc(o.eb)}</span><h1>${esc(o.t)}</h1>${o.sub ? `<div class="sub">${esc(o.sub)}</div>` : ''}</div>
<div class="ft"><img src="${base}/images/f304c8479b1fe873.png"><b>Keith Nah 鈞晖</b><span>keithnah.com · WhatsApp Keith</span></div></body></html>`;
}

(async () => {
  const server = await new Promise(res => {
    const s = http.createServer((q, r) => {
      const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
      if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end(); }
      r.writeHead(200); fs.createReadStream(f).pipe(r);
    }).listen(0, '127.0.0.1', () => res(s));
  });
  const base = 'http://127.0.0.1:' + server.address().port;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  let n = 0;
  for (const o of jobs) {
    await page.setContent(card(o, base), { waitUntil: 'networkidle', timeout: 20000 }).catch(() => {});
    await page.evaluate(() => document.fonts && document.fonts.ready);
    fs.mkdirSync(path.dirname(path.join(ROOT, o.out)), { recursive: true });
    await page.screenshot({ path: path.join(ROOT, o.out), type: 'jpeg', quality: 82 });
    n++;
  }
  await browser.close(); server.close();
  console.log(n);
})();
