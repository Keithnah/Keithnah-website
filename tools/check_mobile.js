/* Phone check, run at the end of tools/build_all.py: opens the main pages at phone width and fails
   when a page is wider than the screen (which pushes the menu button off to the side) or has no
   visible menu button. Every change to the site must keep the phone version working.

    node tools/check_mobile.js            (exit code 1 when a page fails)
*/
const { chromium, devices } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const PAGES = ['index.html', 'projects.html', 'compare.html', 'about-keith.html', 'foreign-buyers.html', 'blog.html', 'calculator.html', 'resources.html', 'mm2h.html',
  'property/maba-suitez.html', 'property/centrix.html', 'property/pavilion-square.html', 'property/the-queenswoodz.html', 'area/kuala-lumpur.html', 'zh/index.html', 'zh/property/maba-suitez.html'];
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'application/javascript', '.svg': 'image/svg+xml', '.css': 'text/css', '.json': 'application/json' };
const srv = http.createServer((q, r) => { let p = decodeURIComponent(q.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html';
  fs.readFile(path.join(ROOT, p), (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' }); r.end(d); }); });
(async () => {
  await new Promise(res => srv.listen(0, res));
  const port = srv.address().port, b = await chromium.launch(), bad = [];
  const c = await b.newContext({ ...devices['Pixel 7'] });
  await c.addInitScript(() => { window.KN_RENDER = 1; });
  for (const u of PAGES) {
    if (!fs.existsSync(path.join(ROOT, u))) continue;
    const p = await c.newPage();
    try {
      await p.goto(`http://localhost:${port}/${u}`, { waitUntil: 'load', timeout: 30000 }); await p.waitForTimeout(400);
      const r = await p.evaluate(() => {
        const W = document.documentElement.clientWidth, sw = document.documentElement.scrollWidth;
        const btn = [...document.querySelectorAll('.hamburger, .kn-burger, .lp-cta')].find(x => { const s = getComputedStyle(x), q = x.getBoundingClientRect(); return s.display !== 'none' && s.visibility !== 'hidden' && q.width > 0 && q.right <= W + 1; });
        return { W, sw, btn: !!btn };
      });
      if (r.sw > r.W + 2) bad.push(`${u}: page is ${r.sw}px wide on a ${r.W}px phone screen`);
      if (!r.btn) bad.push(`${u}: no visible menu button on the phone`);
    } catch (e) { bad.push(`${u}: ${e.message.split('\n')[0]}`); }
    await p.close();
  }
  await b.close(); srv.close();
  if (bad.length) { console.log('phone check FAILED: ' + bad.join('; ')); process.exit(1); }
  console.log('phone check: %d pages OK', PAGES.length);
})();
