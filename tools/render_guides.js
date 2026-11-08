// Renders the area guide PDFs for tools/build_guides.py (run by it; needs Playwright + Chromium).
// For each job: screenshot the area page map, print the guide HTML to PDF, and capture the first pages as previews.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch();
  const c = await b.newContext({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 2 });
  const p = await c.newPage();
  for (const j of jobs) {
    await p.goto('file://' + j.area, { waitUntil: 'load' });
    await p.waitForTimeout(2500);
    await p.addStyleTag({ content: '.leaflet-control-zoom,.kmap-all{display:none!important}' });
    const m = await p.$('#kmap');
    if (m) await m.screenshot({ path: j.map });
    await p.goto('file://' + j.html, { waitUntil: 'networkidle' });
    await p.pdf({ path: j.pdf, format: 'A4', printBackground: true, preferCSSPageSize: true });
    await p.setViewportSize({ width: 794, height: 1123 });
    const pages = await p.$$('.pg');
    for (let n = 0; n < Math.min(3, pages.length); n++) await pages[n].screenshot({ path: j.prev + (n + 1) + '.png' });
    await p.setViewportSize({ width: 1200, height: 900 });
    console.log('ok', j.slug);
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
