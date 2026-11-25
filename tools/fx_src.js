/* Daily exchange rates for the currency menu (keithnah.com).
   The browser reads today's rates from a free public rate service in the background (no page opens, nothing shown),
   keeps them for 12 hours, and updates the prices. If the service does not answer, the fixed rates in each page stay.
   A rate is only used if it is within -30% / +40% of the fixed rate, so a bad reply can never show silly prices. */
(function(){
  var BASE = {USD:0.243, SGD:0.314, CNY:1.61, TWD:7.9, HKD:1.9, JPY:38.8, KRW:325};
  var KEY = 'kn_fx', TTL = 12 * 3600 * 1000;
  function get(){ try{ return JSON.parse(localStorage.getItem(KEY) || 'null'); }catch(e){ return null; } }
  function put(r){ try{ localStorage.setItem(KEY, JSON.stringify({t: Date.now(), r: r})); }catch(e){} }
  function clean(r){
    var ok = {}, n = 0;
    for (var c in BASE){ var v = +(r && r[c]); if (v > 0 && v / BASE[c] > 0.7 && v / BASE[c] < 1.4){ ok[c] = v; n++; } }
    return n ? ok : null;
  }
  function apply(ok, redraw){
    window.KN_FX = ok;
    [window.KN_RATE, window.KN_RATES_MAIN].forEach(function(o){ if (o) for (var c in ok) o[c] = ok[c]; });
    if (!redraw) return;
    var cur = 'MYR'; try{ cur = localStorage.getItem('kn_currency') || 'MYR'; }catch(e){}
    if (cur !== 'MYR'){
      if (typeof window.knSetCur === 'function') window.knSetCur(cur);
      else if (typeof window.setCurrency === 'function') window.setCurrency(cur);
    }
    var a = document.getElementById('cv_amt');
    if (a) a.dispatchEvent(new Event('input', {bubbles: true}));
  }
  function getJSON(u){ return fetch(u, {cache: 'no-store'}).then(function(r){ if (!r.ok) throw 0; return r.json(); }); }
  var c = get();
  if (c && c.r && clean(c.r)) apply(clean(c.r), true);
  if (c && Date.now() - c.t < TTL) return;
  getJSON('https://open.er-api.com/v6/latest/MYR').then(function(j){ return j && j.rates; })
    .catch(function(){ return getJSON('https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/myr.min.json')
      .then(function(j){ var o = {}, m = (j && j.myr) || {}; for (var k in m) o[k.toUpperCase()] = m[k]; return o; }); })
    .then(function(r){ var ok = clean(r); if (ok){ put(ok); apply(ok, true); } })
    .catch(function(){});
})();
