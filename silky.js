/* keithnah.com silky scrolling. Built by tools/add_silky.py from this file; edit here, then run the build. */
(function(){if(window.KN_RENDER)return;var s=document.createElement('style');s.textContent="html.sl-on{scroll-behavior:auto!important}\nhtml.sl-on .sl-wait{opacity:.5;transform:translate3d(0,26px,0);backface-visibility:hidden;will-change:transform,opacity}\nhtml.sl-on .sl-wait.sl-done{opacity:1;transform:none;transition:none;clip-path:none;will-change:auto}\nhtml.sl-on .sl-wait.sl-in{opacity:1;transform:none;transition:opacity .55s cubic-bezier(.16,1,.3,1) var(--d,0s),transform .75s cubic-bezier(.16,1,.3,1) var(--d,0s)}\nhtml.sl-on .sl-mask.sl-wait{opacity:1;clip-path:inset(-12% -6% 100% -6%);transform:translate3d(0,40px,0)}\nhtml.sl-on .sl-mask.sl-wait.sl-in{clip-path:inset(-12% -6% -18% -6%);transform:none;transition:clip-path .9s cubic-bezier(.16,1,.3,1) var(--d,0s),transform .9s cubic-bezier(.16,1,.3,1) var(--d,0s)}\nhtml.sl-on .sl-card{transition:transform .7s cubic-bezier(.16,1,.3,1),box-shadow .7s cubic-bezier(.16,1,.3,1)}\nhtml.sl-on .sl-card.sl-card.sl-card:hover{transform:translate3d(0,-6px,0);box-shadow:0 26px 50px -30px rgba(29,27,79,.45)}\nhtml.sl-on img.sl-px{transition:none!important;will-change:transform}\n#sl-bar{position:fixed;left:0;right:0;top:0;height:3px;z-index:9998;background:linear-gradient(90deg,#5E60CE,#a5a7ff);transform:scaleX(0);transform-origin:0 50%;pointer-events:none}\n@media print{#sl-bar{display:none}}\n/* the two long project lists: the browser only lays out and paints the cards near the screen, and they fade in without rising */\n.proj-card{content-visibility:auto;contain-intrinsic-size:auto 620px}\n.cmp-card{content-visibility:auto;contain-intrinsic-size:auto 320px}\nhtml.sl-on :is(.proj-card,.cmp-card).sl-wait{transform:none;will-change:opacity}\n.sl-rest,.sl-rest *{animation-play-state:paused!important}";document.head.appendChild(s);})();
/* Silky scrolling on every page: smooth mouse-wheel glide on computers, sections and cards rising softly into view,
   photos drifting gently inside their frames, the hero text easing away, and a thin reading-progress bar.
   Phones keep their own native scrolling; everything is off for people who ask for reduced motion. */
(function () {
  var root = document.documentElement;
  if (window.KN_RENDER) return; /* the language pages are pre-rendered in a browser: leave them untouched */
  if (window.self !== window.top || !window.matchMedia || matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;
  var desk = matchMedia('(hover:hover) and (pointer:fine) and (min-width:900px)').matches;
  root.classList.add('sl-on');

  /* ---- smooth wheel glide (computers) ---- */
  var glide = null, sync = null, gliding = false;
  /* very long pages (the full project list, compare) scroll faster with the browser's own smooth wheel */
  if (desk && document.getElementsByTagName('*').length < 6000) (function () {
    var cur = scrollY, tar = cur, set = cur, run = false, last = 0, tau = 165;
    function max() { return root.scrollHeight - innerHeight; }
    function loop(now) {
      if (Math.abs(scrollY - set) > 3) { run = gliding = false; cur = tar = scrollY; if (sync) sync(); return; }
      var dt = Math.max(4, Math.min(40, now - last)); last = now; cur += (tar - cur) * (1 - Math.exp(-dt / tau));
      if (Math.abs(tar - cur) < .25) { cur = tar; run = false; } gliding = run; scrollTo(0, cur); set = scrollY; if (sync) sync(); if (run) requestAnimationFrame(loop);
    }
    function start() { if (!run) { run = true; gliding = true; set = scrollY; last = performance.now(); requestAnimationFrame(loop); } }
    function inner(el, dy) { for (; el && el !== document.body; el = el.parentElement) { if (el.scrollHeight > el.clientHeight + 1) { var o = getComputedStyle(el).overflowY; if ((o === 'auto' || o === 'scroll') && (dy > 0 ? el.scrollTop + el.clientHeight < el.scrollHeight - 1 : el.scrollTop > 0)) return true; } } return false; }
    var mo = document.getElementsByClassName('open'); function menuOpen() { return document.body.style.overflow === 'hidden' || [].some.call(mo, function (m) { return m.matches('.mobile-menu,.nav-links,.menu-open'); }); }
    addEventListener('wheel', function (e) {
      if (!run && e.deltaMode === 0 && Math.abs(e.deltaY) < 50 && e.deltaY % 1 !== 0) return; // trackpad: the system already scrolls smoothly
      if (e.ctrlKey || e.defaultPrevented || Math.abs(e.deltaX) > Math.abs(e.deltaY) || (!run && menuOpen()) || (e.target.closest && e.target.closest('dialog,select,textarea,iframe,[role=dialog],.leaflet-container')) || inner(e.target, e.deltaY)) return;
      e.preventDefault(); var d = e.deltaMode === 1 ? e.deltaY * 32 : e.deltaMode === 2 ? e.deltaY * innerHeight : e.deltaY;
      tau = Math.abs(d) < 60 ? 70 : 110; if (!run) cur = tar = scrollY; tar = Math.max(0, Math.min(max(), tar + d)); start();
    }, { passive: false });
    addEventListener('scroll', function () { if (!run) cur = tar = scrollY; }, { passive: true });
    glide = function (y) { tau = 150; cur = scrollY; tar = Math.max(0, Math.min(max(), y)); start(); };
  })();

  /* ---- in-page links glide too ---- */
  document.addEventListener('click', function (e) {
    if (!glide || e.defaultPrevented || e.button || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest && e.target.closest('a[href^="#"]'); if (!a || a.getAttribute('role') === 'tab') return;
    var h = a.getAttribute('href'), t = h.length > 1 && document.getElementById(h.slice(1)); if (!t) return;
    e.preventDefault(); glide(t.getBoundingClientRect().top + scrollY - 90); try { history.pushState(null, '', h); } catch (x) {}
  });

  /* ---- soft reveals + counters ---- */
  var ITEM = '.section-head p,.section-head .eyebrow,.keith-portrait,.keith-hero-copy,.stat-tile,.ab-tile,.fbh-c,.ls-card,.video-card,.ftk-c,.why-item,.article-prev-card,.kq-card,.mmh-t,.faq-item,.proj-card,.cmp-card,.article-card,.acard,.card,.pc,.lp-plan,.lp-nw,.lp-row,.art-stat,.nf-item,.bg-stage,.tier-stat,.blk,.kph-ph,[class$="card"],[class*="card "],[class$="-tile"],[class*="-tile "]';
  var CARD = '.fbh-c,.ls-card,.video-card,.article-prev-card,.ftk-c';
  var TITLE = 'h2', seen = new WeakSet(), firstScan = true;
  function count(el) {
    var o = el.textContent, m = o.trim().match(/^(\d[\d,]*)(\+?)$/); if (!m || el.querySelector('*')) return;
    var end = +m[1].replace(/,/g, ''), t0 = performance.now(); if (end < 2) return; el.style.fontVariantNumeric = 'tabular-nums';
    (function tick(now) { var p = Math.min(1, (now - t0) / 1500), e = 1 - Math.pow(1 - p, 4); el.textContent = p < 1 ? Math.round(end * e).toLocaleString('en-US') + m[2] : o; if (p < 1) requestAnimationFrame(tick); })(t0);
  }
  function imgs(el) { return [].slice.call(el.querySelectorAll('img')); }
  function warm(el) { imgs(el).forEach(function (im) { if (im.loading === 'lazy') im.loading = 'eager'; }); }
  function ready(el, cb) {
    var list = imgs(el).filter(function (im) { return !(im.complete && im.naturalWidth); }), done = false;
    function go() { if (!done) { done = true; cb(); } }
    if (!list.length) return go();
    warm(el); setTimeout(go, 450);
    Promise.all(list.map(function (im) { return im.decode ? im.decode().catch(function () {}) : Promise.resolve(); })).then(go);
  }
  function show(el, d) { ready(el, function () { reveal(el, d); }); }
  function reveal(el, d) {
    el.style.setProperty('--d', d + 's'); el.classList.add('sl-in');
    [].forEach.call(el.querySelectorAll('b,.stat-num,.ab-n'), count);
    setTimeout(function () { el.classList.add('sl-done'); }, (d + 1) * 1000);
  }
  var io = new IntersectionObserver(function (es) { var i = 0; es.forEach(function (e) { if (!e.isIntersecting) return; io.unobserve(e.target); var el = e.target.__t || e.target; if (e.target.__t) e.target.remove(); show(el, Math.min(i++, 6) * .085); }); }, { rootMargin: '100000px 0px -6% 0px', threshold: 0 });
  /* cards inside a sideways-scrolling row are clipped by the row, so the whole row reveals together */
  function clipBox(el) { for (var p = el.parentElement; p && p !== document.body; p = p.parentElement) { var o = getComputedStyle(p).overflowX; if (o === 'auto' || o === 'scroll' || o === 'hidden') return p; } return null; }
  var grp = new IntersectionObserver(function (es) { es.forEach(function (e) { if (!e.isIntersecting) return; grp.unobserve(e.target); (e.target.__g || []).forEach(function (c, i) { show(c, Math.min(i, 6) * .085); }); }); }, { rootMargin: '100000px 0px -6% 0px', threshold: 0 });
  var SKIP = 'header,nav,footer,dialog,[role=dialog],.kn-fab,.mobile-menu,.hero,.tk,[hidden]';
  var pre = new IntersectionObserver(function (es) { es.forEach(function (e) { if (!e.isIntersecting) return; pre.unobserve(e.target); warm(e.target); }); }, { rootMargin: '0px 0px 150% 0px', threshold: 0 });
  function onFirst(el) { return firstScan && el.getBoundingClientRect().top < innerHeight; }
  function scan() {
    document.querySelectorAll(ITEM).forEach(function (el) {
      if (seen.has(el) || el.closest(SKIP) || (el.parentElement && el.parentElement.closest('.sl-item'))) return; seen.add(el);
      if (el.matches(CARD)) el.classList.add('sl-card');
      el.classList.add('sl-item'); if (onFirst(el)) return; el.classList.add('sl-wait'); if (el.querySelector('img')) pre.observe(el);
      var box = clipBox(el); if (box) { if (!box.__g) { box.__g = []; grp.observe(box); } box.__g.push(el); } else io.observe(el);
    });
    document.querySelectorAll(TITLE).forEach(function (el) {
      if (seen.has(el) || el.closest(SKIP) || el.closest('.sl-item')) return; seen.add(el); el.classList.add('sl-item'); if (onFirst(el)) return; el.classList.add('sl-wait', 'sl-mask');
      var m = document.createElement('i'); m.setAttribute('aria-hidden', 'true'); m.style.cssText = 'position:absolute;width:1px;height:1px;pointer-events:none'; m.__t = el; el.parentNode.insertBefore(m, el); io.observe(m);
    });
    firstScan = false;
  }

  /* ---- photos drift inside their frames (computers) ---- */
  var vis = new Set(), pxIO = new IntersectionObserver(function (es) { es.forEach(function (e) { var el = e.target; if (e.isIntersecting) { place(el); vis.add(el); need(); } else vis.delete(el); }); }, { rootMargin: '12% 0px' });
  function place(el) { var b = el.parentElement.getBoundingClientRect(); el.__top = b.top + scrollY; el.__h = b.height; }
  if (desk) document.querySelectorAll('.ls-img img,.fbh-i img,.video-thumb img,.keith-portrait img').forEach(function (el) { el.parentElement.style.overflow = 'hidden'; el.classList.add('sl-px'); el.__r = .07; el.__s = 1.15; pxIO.observe(el); });

  /* ---- hero text eases away as the page moves on (computers) ---- */
  var hero = desk && document.querySelector('section.hero'), hIn = hero ? [].slice.call(hero.querySelectorAll('.hero-content,.hero-actions')) : [], heroH = hero ? hero.offsetHeight : 0;

  /* ---- decorative loops (hero shine, sparkles, tickers, sliding rows) rest while off screen ---- */
  var restIO = new IntersectionObserver(function (es) { es.forEach(function (e) { e.target.classList.toggle('sl-rest', !e.isIntersecting); }); }, { rootMargin: '80px 0px' });
  [].forEach.call(document.querySelectorAll('section.hero,.tk,.kab-band,.fbh-r,.ftk-r,.kab-r'), function (el) { restIO.observe(el); });

  /* ---- one scroll loop ---- */
  var bar = document.createElement('div'); bar.id = 'sl-bar'; document.body.appendChild(bar);
  var queued = false, vh = innerHeight, docMax = 1;
  function measure() { vh = innerHeight; docMax = Math.max(1, root.scrollHeight - vh); if (hero) heroH = hero.offsetHeight; vis.forEach(place); }
  function frame() {
    queued = false; var y = scrollY; bar.style.transform = 'scaleX(' + Math.min(1, y / docMax) + ')';
    if (hero && y <= heroH * 1.1) hIn.forEach(function (el) { el.style.transform = 'translate3d(0,' + (y * .35).toFixed(1) + 'px,0)'; el.style.opacity = Math.max(0, 1 - y / (heroH * .75)).toFixed(3); });
    vis.forEach(function (el) { var h = el.__h, p = (el.__top - y + h / 2 - vh / 2) / (vh / 2 + h / 2); el.style.transform = 'translate3d(0,' + (-p * h * el.__r).toFixed(2) + 'px,0) scale(' + el.__s + ')'; });
  }
  function need() { if (!queued && !gliding) { queued = true; requestAnimationFrame(frame); } }
  sync = frame;
  addEventListener('scroll', need, { passive: true });
  var mT = 0; function remeasure() { clearTimeout(mT); mT = setTimeout(function () { measure(); need(); }, 120); }
  addEventListener('resize', remeasure); addEventListener('load', remeasure); if ('ResizeObserver' in window) new ResizeObserver(remeasure).observe(document.body);
  setTimeout(function () { scan(); measure(); frame(); }, 40);
})();

/* ---- Depth cards (option B): project and area cards tilt toward the mouse, the photo, tags and text move as separate
   layers, a soft sheen follows the pointer, a press pushes the card down, and it eases back when the mouse leaves.
   Cards also stand up from behind as they appear (every device). Adapted from homeinmalaysia.com. ---- */
(function () {
  if (window.KN_RENDER || window.self !== window.top || !window.matchMedia || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var CARD = '.card,.proj-card,.cmp-card,.fbh-c,.pc,.ls-card';
  /* photo, tag and text layers of each card type */
  var PHOTO = '.proj-media,.cmp-card-media,.fbh-i,.pc-i,.ls-img', IMG = ':scope>img,.proj-photo,.cmp-card-photo,.fbh-i img,.pc-i img,.ls-img img';
  var TAG = '.proj-badges,.cmp-card-status,.fbh-i>i,.pc-i>em,.ls-n', BODY = '.card-b,.proj-body,.cmp-card-body,.fbh-b,.pc-b,.ls-b';
  var css = [
    'html.sl-on.tl-flip :is(.card,.pc,.ls-card,.proj-card,.cmp-card).sl-wait:not(.sl-in):not(.sl-done){transform:perspective(1100px) rotateX(9deg) translate3d(0,40px,0);transform-origin:50% 100%}',
    '.tl-live{position:relative;z-index:3;will-change:transform;transition:box-shadow .45s cubic-bezier(.16,1,.3,1)!important;box-shadow:0 34px 60px -28px rgba(29,27,79,.55)!important}',
    '.tl-card .tl-img{translate:var(--ix,0) var(--iy,0);scale:var(--is,1)}',
    '.tl-card .tl-tag{translate:var(--tx,0) var(--ty,0)}',
    '.tl-card .tl-body{translate:var(--bx,0) var(--by,0)}',
    '.tl-sheen{position:absolute;inset:0;z-index:2;pointer-events:none;opacity:0;transition:opacity .4s ease;border-radius:inherit;background:radial-gradient(320px circle at var(--mx,50%) var(--my,50%),rgba(255,255,255,.3),rgba(255,255,255,0) 68%)}',
    '.tl-live .tl-sheen{opacity:1}'
  ].join('\n');
  var st0 = document.createElement('style'); st0.textContent = css; document.head.appendChild(st0);
  /* the stand-up entrance is for pages with a handful of cards; long lists (all projects, compare) rise flat, which scrolls far smoother */
  if (document.querySelectorAll(CARD).length <= 40) document.documentElement.classList.add('tl-flip');
  if (!matchMedia('(hover:hover) and (pointer:fine)').matches) return; // phones and tablets keep the 3D entrance only

  var CFG = { rot: 6, lift: 8, zoom: 1.02, img: 8, tag: 5, body: 1.5, is: 1.09 };
  var active = new Set(), hover = null, running = false, last = 0, mx = -1, my = -1;
  function st(c) { return c.__tl || (c.__tl = { rx: 0, ry: 0, px: .5, py: .5, trx: 0, try_: 0, tpx: .5, tpy: .5, on: 0, ton: 0, press: 0, tpress: 0 }); }
  function prep(c) {
    if (c.__tlp) return; c.__tlp = 1; c.classList.add('tl-card');
    if (getComputedStyle(c).position === 'static') c.style.position = 'relative';
    var img = c.querySelector(IMG); if (img) img.classList.add('tl-img');
    [].forEach.call(c.querySelectorAll(TAG), function (t) { t.classList.add('tl-tag'); });
    var b = c.querySelector(BODY); if (b) b.classList.add('tl-body');
    var ph = c.querySelector(PHOTO) || c; if (getComputedStyle(ph).position === 'static') ph.style.position = 'relative';
    var g = document.createElement('span'); g.className = 'tl-sheen'; g.setAttribute('aria-hidden', 'true'); ph.appendChild(g); c.__sheen = g;
  }
  function enter(c) {
    if (c.classList.contains('sl-wait') && !c.classList.contains('sl-done') && !c.classList.contains('sl-in')) return false; // still appearing
    prep(c); var s = st(c); if (!active.has(c) || !s.ton) { var r = c.getBoundingClientRect(); s.left = r.left; s.top = r.top; s.w = r.width; s.h = r.height; s.y0 = scrollY; }
    s.ton = 1; c.classList.add('tl-live'); active.add(c); start(); return true;
  }
  function leave(c) { var s = st(c); s.ton = 0; s.trx = s.try_ = 0; s.tpx = s.tpy = .5; s.tpress = 0; }
  function aim(c) {
    var s = st(c); if (!s.w) return; var x = Math.max(0, Math.min(1, (mx - s.left) / s.w)), y = Math.max(0, Math.min(1, (my - (s.top - (scrollY - s.y0))) / s.h));
    s.tpx = x; s.tpy = y; s.try_ = (x - .5) * 2 * CFG.rot; s.trx = (.5 - y) * 2 * CFG.rot;
  }
  function draw(c, s) {
    c.style.transform = 'perspective(1000px) rotateX(' + s.rx.toFixed(3) + 'deg) rotateY(' + s.ry.toFixed(3) + 'deg) translate3d(0,' + (-CFG.lift * s.on).toFixed(2) + 'px,0) scale(' + (1 + (CFG.zoom - 1) * s.on - .018 * s.press).toFixed(4) + ')';
    var dx = (s.px - .5) * 2 * s.on, dy = (s.py - .5) * 2 * s.on, v = function (n, a) { c.style.setProperty(n, a.toFixed(2) + 'px'); };
    v('--ix', -dx * CFG.img); v('--iy', -dy * CFG.img); v('--tx', dx * CFG.tag); v('--ty', dy * CFG.tag); v('--bx', dx * CFG.body); v('--by', dy * CFG.body);
    c.style.setProperty('--is', (1 + (CFG.is - 1) * s.on).toFixed(4));
    if (c.__sheen) { c.__sheen.style.setProperty('--mx', (s.px * 100).toFixed(1) + '%'); c.__sheen.style.setProperty('--my', (s.py * 100).toFixed(1) + '%'); }
  }
  function loop(now) {
    var dt = Math.max(4, Math.min(40, now - last)); last = now; var k = 1 - Math.exp(-dt / 85), out = 1 - Math.exp(-dt / 150);
    active.forEach(function (c) {
      var s = st(c), f = s.ton ? k : out; s.rx += (s.trx - s.rx) * f; s.ry += (s.try_ - s.ry) * f; s.px += (s.tpx - s.px) * f; s.py += (s.tpy - s.py) * f; s.on += (s.ton - s.on) * f; s.press += (s.tpress - s.press) * k; draw(c, s);
      if (!s.ton && s.on < .004) { active.delete(c); c.classList.remove('tl-live'); c.style.transform = ''; s.rx = s.ry = s.on = 0; ['--ix', '--iy', '--tx', '--ty', '--bx', '--by', '--is'].forEach(function (n) { c.style.removeProperty(n); }); }
    });
    if (active.size) requestAnimationFrame(loop); else running = false;
  }
  function start() { if (!running) { running = true; last = performance.now(); requestAnimationFrame(loop); } }
  function track(c) { if (c !== hover) { if (hover) leave(hover); hover = c; } if (c) { if (!active.has(c) || !st(c).ton) enter(c); aim(c); } }
  function cardAt(t) { var c = t && t.closest ? t.closest(CARD) : null; return c && !c.closest('header,nav,footer,dialog,.mobile-menu') ? c : null; }
  document.addEventListener('pointermove', function (e) { if (e.pointerType !== 'mouse') return; mx = e.clientX; my = e.clientY; if (scrolling) return; track(cardAt(e.target)); }, { passive: true });
  document.documentElement.addEventListener('mouseleave', function () { mx = -1; if (hover) { leave(hover); hover = null; } });
  /* while the page is scrolling the cards stay flat (a card under a resting mouse would otherwise tilt and settle
     one after another, which costs frames); the tilt comes back with the next mouse move */
  var scrolling = false, sT = 0;
  addEventListener('scroll', function () {
    if (!scrolling) { scrolling = true; if (hover) { leave(hover); hover = null; } }
    clearTimeout(sT); sT = setTimeout(function () { scrolling = false; }, 160);
  }, { passive: true });
  document.addEventListener('pointerdown', function (e) { var c = cardAt(e.target); if (c && active.has(c)) st(c).tpress = 1; });
  document.addEventListener('pointerup', function () { active.forEach(function (c) { st(c).tpress = 0; }); });
})();
