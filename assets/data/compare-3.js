
(function(){
  var LBL = {"en": {"dev": "Developer", "type": "Type", "tenure": "Tenure", "title": "Title", "status": "Status", "completion": "Completion", "price": "Starting price", "psf": "Price psf", "mo": "Est. monthly (35 yrs)", "size": "Size", "rooms": "Bedrooms", "maint": "Maintenance fee", "units": "Total units", "cars": "Car parks", "rail": "Nearest rail", "area": "Area", "elig": "Buyer eligibility", "low": "Lowest", "large": "Largest", "early": "Earliest", "few": "Most exclusive", "pm": "/ month", "moNote": "10% down, 4% p.a. Estimate only.", "share": "Copy share link", "copied": "Link copied!", "print": "Print / Save PDF", "map": "Where they are", "mapNote": "Pins show approximate locations.", "view": "View project", "best": "Best value is marked for each row.", "calc": "Open calculator", "ready": "Ready", "search": "Search by project name or area...", "sel": "selected", "pick": "Pick one more to compare", "clear": "Clear", "go": "Compare now"}, "zh-CN": {"dev": "发展商", "type": "类型", "tenure": "产权", "title": "地契", "status": "状态", "completion": "竣工", "price": "起价", "psf": "每平方尺价格", "mo": "预计月供（35 年）", "size": "面积", "rooms": "卧室", "maint": "管理费", "units": "总单位", "cars": "停车位", "rail": "最近轨道站", "area": "地区", "elig": "购买资格", "low": "最低", "large": "最大", "early": "最早", "few": "最低密度", "pm": "/ 月", "moNote": "首付 10%，年利率 4%，仅供参考。", "share": "复制分享链接", "copied": "链接已复制！", "print": "打印 / 保存 PDF", "map": "项目位置", "mapNote": "地图标记为大约位置。", "view": "查看项目", "best": "每一行的最佳数值已标出。", "calc": "打开计算器", "ready": "现房", "search": "按项目名称或地区搜索…", "sel": "已选", "pick": "再选一个即可比较", "clear": "清除", "go": "立即比较"}, "ms": {"dev": "Pemaju", "type": "Jenis", "tenure": "Pegangan", "title": "Hak milik", "status": "Status", "completion": "Siap", "price": "Harga permulaan", "psf": "Harga sk", "mo": "Anggaran bulanan (35 thn)", "size": "Saiz", "rooms": "Bilik tidur", "maint": "Yuran penyelenggaraan", "units": "Jumlah unit", "cars": "Tempat letak kereta", "rail": "Stesen rel terdekat", "area": "Kawasan", "elig": "Kelayakan pembeli", "low": "Terendah", "large": "Terbesar", "early": "Terawal", "few": "Paling eksklusif", "pm": "/ bulan", "moNote": "Deposit 10%, 4% setahun. Anggaran sahaja.", "share": "Salin pautan", "copied": "Pautan disalin!", "print": "Cetak / Simpan PDF", "map": "Lokasi projek", "mapNote": "Pin menunjukkan lokasi anggaran.", "view": "Lihat projek", "best": "Nilai terbaik ditandakan bagi setiap baris.", "calc": "Buka kalkulator", "ready": "Sedia", "search": "Cari mengikut nama projek atau kawasan...", "sel": "dipilih", "pick": "Pilih satu lagi untuk dibandingkan", "clear": "Kosongkan", "go": "Bandingkan"}, "ja": {"dev": "デベロッパー", "type": "タイプ", "tenure": "保有形態", "title": "権利種別", "status": "ステータス", "completion": "完成", "price": "最低価格", "psf": "平方フィート単価", "mo": "月々の返済目安（35年）", "size": "面積", "rooms": "ベッドルーム", "maint": "管理費", "units": "総戸数", "cars": "駐車場", "rail": "最寄り駅", "area": "エリア", "elig": "購入資格", "low": "最安", "large": "最大", "early": "最も早い", "few": "最も希少", "pm": "/ 月", "moNote": "頭金10%、年利4%。目安です。", "share": "共有リンクをコピー", "copied": "コピーしました！", "print": "印刷 / PDF保存", "map": "所在地", "mapNote": "ピンはおおよその位置です。", "view": "プロジェクトを見る", "best": "各行のベスト値に印が付いています。", "calc": "計算機を開く", "ready": "完成済み", "search": "プロジェクト名またはエリアで検索…", "sel": "選択中", "pick": "もう1件選ぶと比較できます", "clear": "クリア", "go": "比較する"}, "ko": {"dev": "개발사", "type": "유형", "tenure": "소유 형태", "title": "권리 유형", "status": "상태", "completion": "준공", "price": "시작 가격", "psf": "평방피트당 가격", "mo": "예상 월 상환액 (35년)", "size": "면적", "rooms": "침실", "maint": "관리비", "units": "총 세대수", "cars": "주차", "rail": "가장 가까운 역", "area": "지역", "elig": "구매 자격", "low": "최저", "large": "최대", "early": "가장 빠름", "few": "가장 희소", "pm": "/ 월", "moNote": "계약금 10%, 연 4%. 참고용 추정치입니다.", "share": "공유 링크 복사", "copied": "링크가 복사되었습니다!", "print": "인쇄 / PDF 저장", "map": "위치", "mapNote": "핀은 대략적인 위치입니다.", "view": "프로젝트 보기", "best": "각 행의 최고 값이 표시됩니다.", "calc": "계산기 열기", "ready": "입주 가능", "search": "프로젝트명 또는 지역으로 검색…", "sel": "선택됨", "pick": "하나 더 선택하면 비교할 수 있어요", "clear": "지우기", "go": "비교하기"}, "zh-TW": {"dev": "發展商", "type": "類型", "tenure": "產權", "title": "地契", "status": "狀態", "completion": "竣工", "price": "起價", "psf": "每平方尺價格", "mo": "預計月供（35 年）", "size": "面積", "rooms": "臥室", "maint": "管理費", "units": "總單位", "cars": "停車位", "rail": "最近軌道站", "area": "地區", "elig": "購買資格", "low": "最低", "large": "最大", "early": "最早", "few": "最低密度", "pm": "/ 月", "moNote": "首付 10%，年利率 4%，僅供參考。", "share": "複製分享鏈接", "copied": "鏈接已複製！", "print": "打印 / 保存 PDF", "map": "項目位置", "mapNote": "地圖標記為大約位置。", "view": "查看項目", "best": "每一行的最佳數值已標出。", "calc": "打開計算器", "ready": "現房", "search": "按項目名稱或地區搜索…", "sel": "已選", "pick": "再選一個即可比較", "clear": "清除", "go": "立即比較"}};
  function lang(){ var l = (typeof currentLang !== 'undefined' && currentLang) ? currentLang : 'en'; return LBL[l] ? l : 'en'; }
  function T(k){ return LBL[lang()][k] || LBL.en[k]; }
  function esc(v){ return escapeHtml(v == null ? '' : v); }
  function rm(n){ return 'RM ' + Math.round(n).toLocaleString('en-US'); }
  var ROWS = [
    {k:'dev'}, {k:'type'}, {k:'tenure'}, {k:'title'}, {k:'status'},
    {k:'completion', n:'nYear', best:'min', b:'early'},
    {k:'price', n:'nPrice', best:'min', b:'low'},
    {k:'psf', v:'psfTxt', n:'nPsf', best:'min', b:'low'},
    {k:'mo', n:'nMo', best:'min', b:'low', fmt:function(p){ return p.nMo ? rm(p.nMo) + ' ' + T('pm') : ''; }},
    {k:'size', n:'nSize', best:'max', b:'large'}, {k:'rooms'},
    {k:'maint', n:'nMaint', best:'min', b:'low'},
    {k:'units', n:'nUnits', best:'min', b:'few'},
    {k:'cars'}, {k:'rail'},
    {k:'area', fmt:function(p){ return p.area + ', ' + p.state; }},
    {k:'elig', opt:true}
  ];
  function val(p, r){ if(r.fmt) return r.fmt(p); return p[r.v || r.k] || ''; }
  function bestSet(r){
    if(!r.best) return [];
    var nums = selectedIdx.map(function(i){ var v = PROJECTS[i][r.n]; return (v === null || v === undefined) ? null : v; });
    var have = nums.filter(function(v){ return v !== null; });
    if(have.length < 2) return [];
    var b = r.best === 'min' ? Math.min.apply(null, have) : Math.max.apply(null, have);
    if(have.every(function(v){ return v === b; })) return [];
    return nums.map(function(v){ return v === b; });
  }
  window.renderTable = function(){
    var table = document.getElementById('cmpTable');
    document.getElementById('cmpModalTitle').textContent = 'Compare Projects (' + selectedIdx.length + ' / 3 Selected)';
    var names = selectedIdx.map(function(i){ return PROJECTS[i].name; });
    var namesText = names.length < 3 ? names.join(' and ') : names.slice(0, -1).join(', ') + ' and ' + names[names.length - 1];
    var wa = document.getElementById('cmpWaLink');
    if(wa) wa.href = 'https://api.whatsapp.com/send/?phone=60102821568&text=' + encodeURIComponent('(KNRE) Hi Keith, I\'m comparing ' + namesText + ' and would like your advice on which fits me best. ' + shareUrl()) + '&type=phone_number&app_absent=0';
    var h = '<colgroup><col class="label-col">' + selectedIdx.map(function(){ return '<col>'; }).join('') + '</colgroup><thead><tr><th></th>';
    selectedIdx.forEach(function(idx, n){
      var p = PROJECTS[idx];
      var img = document.querySelector('.cmp-card[data-idx="' + idx + '"] .cmp-card-photo');
      var media = img ? '<img class="cmp-th-photo" src="' + img.getAttribute('src') + '" alt="' + esc(p.name) + '">' : '<div class="cmp-th-icon">' + p.icon + '</div>';
      h += '<th><div class="cmp-th-media" style="background:linear-gradient(135deg,' + (p.grad || '#1c1a17,#3a3226') + ')">' + media
        + '<div class="cmp-th-remove" onclick="removeFromCompare(' + idx + ')">&times;</div></div>'
        + '<span class="cmp-th-name"><span class="cmp-th-num">' + (n + 1) + '</span><a href="' + p.url + '">' + esc(p.name) + '</a></span>'
        + '<span class="cmp-th-price">' + esc(p.price) + '</span></th>';
    });
    h += '</tr></thead><tbody>';
    ROWS.forEach(function(r){
      var vals = selectedIdx.map(function(i){ return val(PROJECTS[i], r); });
      if(vals.every(function(v){ return !v; })) return;
      var best = bestSet(r);
      var same = vals.every(function(v){ return v === vals[0]; });
      h += '<tr><td class="label">' + esc(T(r.k)) + '</td>';
      vals.forEach(function(v, j){
        var p = PROJECTS[selectedIdx[j]], cls = [];
        if(highlightOn && !same) cls.push('diff');
        if(best[j]) cls.push('best');
        var cell = '<div>' + (v ? esc(v) : '—') + '</div>';
        if(r.k === 'mo' && v) cell += '<small>' + esc(T('moNote')) + '</small><div><a class="cmp-mini" href="calculator.html?price=' + Math.round(p.nPrice) + '&down=10&rate=4&years=35">' + esc(T('calc')) + ' →</a></div>';
        if(best[j]) cell += '<div><span class="cmp-best">' + esc(T(r.b)) + '</span></div>';
        h += '<td class="' + cls.join(' ') + '">' + cell + '</td>';
      });
      h += '</tr>';
    });
    table.innerHTML = h + '</tbody>';
    var note = document.getElementById('cmpBestNote'); if(note) note.textContent = T('best');
    setActions();
    drawMap();
  };

  // ---- share link, print, extra buttons ----
  function shareUrl(){
    return location.origin + location.pathname + '?p=' + selectedIdx.map(function(i){ return PROJECTS[i].slug; }).join(',');
  }
  function setActions(){
    var s = document.getElementById('cmpShare'), pr = document.getElementById('cmpPrint');
    if(s && !s.dataset.busy) s.textContent = T('share');
    if(pr) pr.textContent = T('print');
    var mh = document.getElementById('cmpMapHead'), mn = document.getElementById('cmpMapNote');
    if(mh) mh.textContent = T('map'); if(mn) mn.textContent = T('mapNote');
    try{ history.replaceState(null, '', '?p=' + selectedIdx.map(function(i){ return PROJECTS[i].slug; }).join(',')); }catch(e){}
  }
  function setup(){
    var ov = document.getElementById('cmpModalOverlay');
    if(ov && ov.parentNode !== document.body) document.body.appendChild(ov);   // so print can show it on its own
    var cta = document.querySelector('.cmp-modal-cta'), wa = document.getElementById('cmpWaLink');
    if(!cta || document.getElementById('cmpShare')) return;
    var wrap = document.querySelector('.cmp-table-wrap');
    var note = document.createElement('p'); note.className = 'cmp-note'; note.id = 'cmpBestNote';
    wrap.parentNode.insertBefore(note, wrap.nextSibling);
    var mw = document.createElement('div'); mw.className = 'cmp-map-wrap';
    mw.innerHTML = '<h4 id="cmpMapHead"></h4><div id="cmpMap"></div><p id="cmpMapNote"></p>';
    note.parentNode.insertBefore(mw, note.nextSibling);
    var act = document.createElement('div'); act.className = 'cmp-actions';
    wa.parentNode.insertBefore(act, wa); act.appendChild(wa);
    var sh = document.createElement('button'); sh.type = 'button'; sh.className = 'btn btn-line'; sh.id = 'cmpShare';
    sh.onclick = function(){
      var u = shareUrl();
      function done(){ sh.dataset.busy = 1; sh.textContent = T('copied'); setTimeout(function(){ delete sh.dataset.busy; sh.textContent = T('share'); }, 2200); }
      if(navigator.share && /Mobi|Android|iPhone/i.test(navigator.userAgent)){ navigator.share({title:document.title, url:u}).catch(function(){}); return; }
      if(navigator.clipboard) navigator.clipboard.writeText(u).then(done, function(){ prompt('', u); });
      else prompt('', u);
    };
    var pr = document.createElement('button'); pr.type = 'button'; pr.className = 'btn btn-line'; pr.id = 'cmpPrint';
    pr.onclick = function(){ window.print(); };
    act.appendChild(sh); act.appendChild(pr);
  }

  // ---- map of the selected projects (Leaflet is loaded the first time it is needed) ----
  var map = null, layer = null, loading = false;
  function loadLeaflet(cb){
    if(window.L && L.map) return cb();
    if(loading) return; loading = true;
    var c = document.createElement('link'); c.rel = 'stylesheet'; c.href = 'vendor/leaflet/leaflet.css'; document.head.appendChild(c);
    var j = document.createElement('script'); j.src = 'vendor/leaflet/leaflet.js'; j.onload = function(){ loading = false; cb(); }; document.head.appendChild(j);
  }
  function drawMap(){
    var el = document.getElementById('cmpMap'); if(!el) return;
    var pts = selectedIdx.map(function(i, n){ var p = PROJECTS[i]; return p.ll && p.ll[0] ? {p:p, n:n + 1} : null; }).filter(Boolean);
    el.parentNode.style.display = pts.length ? '' : 'none';
    if(!pts.length) return;
    loadLeaflet(function(){
      if(!map){
        map = L.map(el, {scrollWheelZoom:false, dragging:!L.Browser.mobile, tap:false});
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom:19, attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(map);
      }
      if(layer) map.removeLayer(layer);
      layer = L.layerGroup().addTo(map);
      var b = [];
      pts.forEach(function(x, j){
        var ll = x.p.ll.slice();
        pts.slice(0, j).forEach(function(y){ if(Math.abs(y.ll[0] - ll[0]) < 1e-4 && Math.abs(y.ll[1] - ll[1]) < 1e-4){ ll[0] += 0.0018 * Math.cos(j * 2.1); ll[1] += 0.0018 * Math.sin(j * 2.1); } });
        x.ll = ll;
        var ic = L.divIcon({className:'', html:'<div class="cmpn">' + x.n + '</div>', iconSize:[28,28], iconAnchor:[14,14]});
        L.marker(x.ll, {icon:ic, title:x.p.name}).addTo(layer)
          .bindTooltip(x.n + '. ' + x.p.name, {direction:j % 2 ? 'bottom' : 'top', offset:[0, j % 2 ? 12 : -12], permanent:pts.length <= 3})
          .bindPopup('<b>' + esc(x.p.name) + '</b><br>' + esc(x.p.area) + '<br><a href="' + x.p.url + '">' + esc(T('view')) + ' →</a>');
        b.push(x.ll);
      });
      setTimeout(function(){
        map.invalidateSize();
        if(b.length === 1) map.setView(b[0], 14); else map.fitBounds(b, {padding:[50,50], maxZoom:15});
      }, 60);
    });
  }

  // ---- state / area filters ----
  var fState = '', fArea = '';
  window.applyFilters = function(){
    var q = ((document.getElementById('cmpSearch') || {}).value || '').toLowerCase().trim(), n = 0;
    document.querySelectorAll('.cmp-card').forEach(function(card){
      var p = PROJECTS[+card.getAttribute('data-idx')];
      var ok = (card.getAttribute('data-search') || '').indexOf(q) > -1 && (!fState || p.state === fState) && (!fArea || p.area === fArea);
      card.style.display = ok ? '' : 'none'; if(ok) n++;
    });
    var e = document.getElementById('cmpEmpty'); if(e) e.style.display = n ? 'none' : 'block';
  };
  var fw = document.getElementById('cmpFilters'), subs = document.getElementById('cmpSubs');
  if(fw){
    var nf = fw.cloneNode(true); fw.parentNode.replaceChild(nf, fw);   // drop the old tag-based click handler
    nf.addEventListener('click', function(e){
      var b = e.target.closest('.cmp-filter-btn'); if(!b) return;
      nf.querySelectorAll('.cmp-filter-btn').forEach(function(x){ x.classList.remove('active'); });
      b.classList.add('active');
      fState = b.getAttribute('data-state') || ''; fArea = '';
      subs.querySelectorAll('.cmp-sub').forEach(function(s){ s.classList.toggle('show', s.getAttribute('data-for') === fState); s.querySelectorAll('.cmp-filter-btn').forEach(function(x){ x.classList.remove('active'); }); });
      applyFilters();
    });
  }
  var se = document.getElementById('cmpSearch'); if(se) se.addEventListener('input', function(){ applyFilters(); });
  if(subs) subs.addEventListener('click', function(e){
    var b = e.target.closest('.cmp-sub-btn'); if(!b) return;
    var on = b.classList.contains('active');
    b.parentNode.querySelectorAll('.cmp-filter-btn').forEach(function(x){ x.classList.remove('active'); });
    if(!on) b.classList.add('active');
    fArea = on ? '' : b.getAttribute('data-area');
    applyFilters();
  });

  // ---- presets and ?p= share links ----
  function compare(ids){
    selectedIdx.length = 0;
    ids.forEach(function(i){ if(PROJECTS[i] && selectedIdx.length < 3 && selectedIdx.indexOf(i) < 0) selectedIdx.push(i); });
    renderSelection();
    if(selectedIdx.length >= 2) openModal();
  }
  document.querySelectorAll('.cmp-preset').forEach(function(b){
    b.addEventListener('click', function(){ compare(b.getAttribute('data-p').split(',').map(Number)); });
  });
  var _rs = window.renderSelection;
  window.renderSelection = function(){
    var r = _rs.apply(this, arguments), n = selectedIdx.length, bar = document.getElementById('cmpBar');
    if(bar){
      var slots = '';
      for(var k = 0; k < 3; k++){
        var i = selectedIdx[k];
        if(i === undefined){ slots += '<div class="cmpb-slot">+</div>'; continue; }
        var img = document.querySelector('.cmp-card[data-idx="' + i + '"] .cmp-card-photo');
        slots += '<div class="cmpb-slot on" title="' + esc(PROJECTS[i].name) + '">' + (img ? '<img src="' + img.getAttribute('src') + '" alt="">' : '')
          + '<span class="x" data-rm="' + i + '">&times;</span></div>';
      }
      bar.innerHTML = '<div class="cmpb-slots">' + slots + '</div><div class="cmpb-info"><b>' + n + ' / 3 ' + esc(T('sel')) + '</b><small>'
        + esc(n < 2 ? T('pick') : selectedIdx.map(function(i){ return PROJECTS[i].name; }).join(' · ')) + '</small></div>'
        + '<button type="button" class="cmpb-clear">' + esc(T('clear')) + '</button>'
        + '<button type="button" class="cmpb-go">' + esc(T('go')) + '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></button>';
      bar.classList.toggle('show', n >= 1); bar.classList.toggle('one', n === 1);
    }
    document.body.classList.toggle('cmp-bar-on', n >= 1);
    return r;
  };
  (function(){
    var bar = document.getElementById('cmpBar'); if(!bar) return;
    bar.addEventListener('click', function(e){
      var x = e.target.closest('[data-rm]');
      if(x){ toggleSelect(+x.getAttribute('data-rm')); return; }
      if(e.target.closest('.cmpb-clear')){ selectedIdx.length = 0; renderSelection(); return; }
      if(e.target.closest('.cmpb-go')) openModal();
    });
  })();
  var _om = window.openModal, _cm0 = window.closeModal;
  window.openModal = function(){ var r = _om.apply(this, arguments); if(document.getElementById('cmpModalOverlay').classList.contains('open')) document.body.classList.add('cmp-modal-open'); return r; };
  setup();
  function ph(){ var se = document.getElementById('cmpSearch'); if(se) se.placeholder = T('search'); }
  ph();
  var _close = window.closeModal;
  window.closeModal = function(){ _close.apply(this, arguments); document.body.classList.remove('cmp-modal-open'); try{ history.replaceState(null, '', location.pathname); }catch(e){} };
  document.addEventListener('DOMContentLoaded', function(){   // setLanguage is defined by a later script
    var _setLang = window.setLanguage;
    if(typeof _setLang === 'function') window.setLanguage = function(){
      var r = _setLang.apply(this, arguments);
      ph(); renderSelection();
      if(document.getElementById('cmpModalOverlay').classList.contains('open')) renderTable();
      return r;
    };
    ph();
  });
  window.addEventListener('load', ph);
  var q = (location.search.match(/[?&]p=([^&]+)/) || [])[1];
  if(q){
    var want = decodeURIComponent(q).split(',');
    var ids = want.map(function(sl){ for(var i = 0; i < PROJECTS.length; i++) if(PROJECTS[i].slug === sl) return i; return -1; }).filter(function(i){ return i > -1; });
    window.addEventListener('load', function(){ compare(ids); });
  }
})();
