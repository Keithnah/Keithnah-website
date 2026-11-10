/* Hero headline: split into letters for the wave entrance; add sparkles to the highlighted word. */
(function () {
  var h = document.querySelector('.hero-content h1[data-anim]');
  if (!h) return;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var SPARKS = [[3, 18, '0s'], [30, 5, '.9s'], [52, 88, '1.7s'], [76, 10, '.45s'], [99, 40, '1.25s'], [16, 80, '2.1s']];
  function split() {
    var n = 0;
    (function walk(node, acc) {
      Array.prototype.slice.call(node.childNodes).forEach(function (c) {
        if (c.nodeType === 3) {
          var frag = document.createDocumentFragment();
          c.textContent.split(/(\s+)/).forEach(function (w) {
            if (!w) return;
            if (/^\s+$/.test(w)) { frag.appendChild(document.createTextNode(' ')); return; }
            var ws = document.createElement('span'); ws.className = 'hw';
            w.split('').forEach(function (ch, j) {
              var s = document.createElement('span'); s.className = 'hl'; s.textContent = ch;
              s.style.setProperty('--i', n++); if (acc) s.style.setProperty('--j', j);
              ws.appendChild(s);
            });
            frag.appendChild(ws);
          });
          node.replaceChild(frag, c);
        } else if (c.nodeType === 1 && c.tagName !== 'BR') {
          if (!acc) c.classList.add('acc');
          walk(c, true);
          var sh = document.createElement('span'); sh.className = 'shn'; sh.setAttribute('aria-hidden', 'true'); sh.textContent = c.textContent; c.appendChild(sh);
          var gl = document.createElement('i'); gl.className = 'glow'; gl.setAttribute('aria-hidden', 'true'); c.insertBefore(gl, c.firstChild);
          SPARKS.forEach(function (p) {
            var k = document.createElement('i'); k.className = 'spk'; k.setAttribute('aria-hidden', 'true');
            k.style.left = p[0] + '%'; k.style.top = p[1] + '%'; k.style.setProperty('--d', p[2]);
            c.appendChild(k);
          });
        }
      });
    })(h, false);
    h.style.setProperty('--n', n);
  }
  function run() {
    if (h.dataset.split && h.dataset.split === h.innerHTML) return;
    split();
    h.classList.remove('ha-on'); h.classList.add('ha');
    h.dataset.split = h.innerHTML;
    if (reduce) { h.classList.add('ha-still'); return; }
    requestAnimationFrame(function () { requestAnimationFrame(function () { h.classList.add('ha-on'); }); });
  }
  run();
  new MutationObserver(function () { if (h.dataset.split !== h.innerHTML) run(); }).observe(h, { childList: true });
})();
