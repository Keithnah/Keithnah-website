/* KNRE lead tracker
 * Records WhatsApp button clicks (only when the visitor actually leaves for WhatsApp,
 * once per 30 minutes) and every Quick Enquiry submission
 * in the "KNRE Leads" Google Sheet, through a Google Apps Script web app.
 *
 * Setup: paste the web app URL (ends in /exec) into LEADS_ENDPOINT below.
 * The Apps Script code is in tools/leads-apps-script.gs.
 */
(function () {
  var LEADS_ENDPOINT = 'https://script.google.com/macros/s/AKfycbwzuJuSItPGTzI6XOHrPo2O3LzgOsCD6VHRp11v38qtZsSiYruOqg2INeM0zSxlDMQtiA/exec';
  var SOURCE_WEBSITE = 'KNRE website';

  var PAGE_NAMES = {
    'index': 'Home', '': 'Home', 'projects': 'View Projects', 'compare': 'Compare Projects',
    'blog': 'News', 'calculator': 'Calculator', 'mm2h': 'MM2H', 'about-keith': 'About Keith'
  };

  function pageName() {
    var sub = { property: 'Project page: ', article: 'Article: ', topic: 'Topic: ' };
    var m = location.pathname.match(/\/(property|article|topic)\//);
    if (m) {
      var h = document.querySelector('h1');
      return sub[m[1]] + (h ? h.textContent.trim() : location.pathname.split('/').pop());
    }
    var f = (location.pathname.split('/').pop() || '').replace(/\.html?$/i, '');
    return PAGE_NAMES[f] || f || 'Home';
  }

  function device() {
    return /iPad|Tablet/i.test(navigator.userAgent) ? 'Tablet'
      : /Mobi|Android|iPhone/i.test(navigator.userAgent) ? 'Mobile' : 'Desktop';
  }

  function send(data) {
    if (!LEADS_ENDPOINT) return;
    data.source = SOURCE_WEBSITE;
    data.page = pageName();
    data.lang = document.documentElement.getAttribute('lang') || 'en';
    data.device = device();
    data.referrer = document.referrer || '';
    data.url = location.href;
    var body = JSON.stringify(data);
    // sendBeacon survives the page switching to WhatsApp; fetch is the fallback.
    try {
      if (navigator.sendBeacon && navigator.sendBeacon(LEADS_ENDPOINT, new Blob([body], { type: 'text/plain' }))) return;
    } catch (e) {}
    try {
      fetch(LEADS_ENDPOINT, { method: 'POST', mode: 'no-cors', keepalive: true, headers: { 'Content-Type': 'text/plain' }, body: body });
    } catch (e) {}
  }

  function isWhatsApp(href) {
    return /(^|\/\/)(wa\.me|api\.whatsapp\.com|web\.whatsapp\.com)\/|^whatsapp:/i.test(href || '');
  }

  function whatsAppText(href) {
    try { return new URL(href).searchParams.get('text') || ''; } catch (e) { return ''; }
  }

  function buttonLabel(a) {
    if (a.classList.contains('float-wa')) return 'Floating WhatsApp button';
    if (a.classList.contains('whatsapp-btn')) return 'Header WhatsApp button';
    var t = (a.textContent || '').replace(/\s+/g, ' ').trim();
    if (!t || t.length < 2) t = a.getAttribute('aria-label') || a.getAttribute('title') || '';
    if (a.classList.contains('proj-plus') || a.classList.contains('proj-arrow')) t = 'Project card: ' + (t || 'Enquire');
    return (t || 'WhatsApp link').slice(0, 120);
  }

  // A WhatsApp click is only recorded once the visitor really goes to WhatsApp
  // (the page is hidden, unloaded or loses focus within a few seconds).
  // A tap that does not leave the page is treated as accidental and dropped,
  // and repeat clicks from the same visitor within 30 minutes are recorded once.
  var CONFIRM_MS = 5000, REPEAT_MS = 30 * 60 * 1000, KEY = 'knre_wa_last';
  var pending = null;

  function recentlySent() {
    try { return Date.now() - (+localStorage.getItem(KEY) || 0) < REPEAT_MS; } catch (e) { return false; }
  }

  function confirmPending() {
    if (!pending || Date.now() - pending.t > CONFIRM_MS) { pending = null; return; }
    var d = pending.data; pending = null;
    if (recentlySent()) return;
    try { localStorage.setItem(KEY, String(Date.now())); } catch (e) {}
    send(d);
  }
  document.addEventListener('visibilitychange', function () { if (document.visibilityState === 'hidden') confirmPending(); });
  window.addEventListener('pagehide', confirmPending);
  window.addEventListener('blur', function () { setTimeout(function () { if (!document.hasFocus()) confirmPending(); }, 300); });

  function onClick(e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a || !isWhatsApp(a.href)) return;
    pending = { t: Date.now(), data: { type: 'WhatsApp Click', button: buttonLabel(a), message: whatsAppText(a.href) } };
    setTimeout(function () { if (pending && Date.now() - pending.t >= CONFIRM_MS) pending = null; }, CONFIRM_MS + 100);
  }
  document.addEventListener('click', onClick, true);
  document.addEventListener('auxclick', function (e) { if (e.button === 1) onClick(e); }, true);

  // Quick Enquiry form: record every field, then let the original handler open WhatsApp.
  var originalSend = window.knqSend;
  if (typeof originalSend === 'function') {
    window.knqSend = function (f) {
      var name = f.name.value.trim(), digits = f.phone.value.replace(/[^0-9]/g, '');
      if (name && digits.length >= 6) { // same check as the form itself
        var msg = '(KNRE) Hi Keith, I would like to make an enquiry.\nName: ' + name +
          '\nWhatsApp: ' + f.code.value + ' ' + f.phone.value.trim();
        if (f.email.value.trim()) msg += '\nEmail: ' + f.email.value.trim();
        if (f.area.value) msg += '\nPreferred area: ' + f.area.value;
        if (f.look.value) msg += '\nLooking for: ' + f.look.value;
        send({
          type: 'Quick Enquiry', button: 'Quick Enquiry form', name: name,
          code: f.code.value, phone: f.phone.value.trim(), email: f.email.value.trim(),
          area: f.area.value, look: f.look.value, message: msg
        });
      }
      return originalSend(f);
    };
  }
})();
