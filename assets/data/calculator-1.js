
// ---- Calculators (amounts in RM) ----
(function(){
  const $ = id => document.getElementById(id);
  const parse = s => { const v = parseFloat(String(s).replace(/,/g,'')); return isFinite(v) ? v : 0; };
  const rm = v => 'RM ' + Math.round(v).toLocaleString('en-US');
  const pc = v => (isFinite(v) ? v : 0).toFixed(2) + '%';
  const clamp = (v, a, b) => Math.min(Math.max(v, a), b);
  const num = (v,d) => (isFinite(v)?v:0).toLocaleString('en-US',{maximumFractionDigits:d});

  const FIELDS = {
    price: {label:'Property purchase price', min:100000, max:10000000, step:10000, val:1000000, pre:'RM', dec:0, lo:'RM 100,000', hi:'RM 10,000,000', w:11},
    down:  {label:'Down payment', min:0, max:100, step:1, val:10, suf:'%', amt:true, dec:0, lo:'0% (full loan)', hi:'100% (cash)', w:4},
    rate:  {label:'Annual interest rate', min:1, max:10, step:0.05, val:4, suf:'% p.a.', dec:2, lo:'1.0%', hi:'10.0%', w:5},
    years: {label:'Loan tenure (years)', min:5, max:35, step:1, val:30, suf:'Years', dec:0, lo:'5 years', hi:'35 years', w:4},
    rent:  {label:'Monthly rent (RM)', min:500, max:50000, step:100, val:4000, pre:'RM', dec:0, lo:'RM 500', hi:'RM 50,000', w:7},
    rocc:  {label:'Expected occupancy (%)', min:0, max:100, step:1, val:95, suf:'%', dec:0, lo:'0%', hi:'100%', w:4},
    nightly:{label:'Average nightly rate (RM)', min:50, max:3000, step:10, val:300, pre:'RM', dec:0, lo:'RM 50', hi:'RM 3,000', w:6},
    occ:   {label:'Average occupancy (%)', min:10, max:100, step:1, val:65, suf:'%', dec:0, lo:'10%', hi:'100%', w:4},
    extra: {label:'Extra payment every month (RM)', min:0, max:20000, step:100, val:500, pre:'RM', dec:0, lo:'RM 0', hi:'RM 20,000', w:7},
    lump:  {label:'One-off lump sum paid at the start (RM)', min:0, max:1000000, step:5000, val:0, pre:'RM', dec:0, lo:'RM 0', hi:'RM 1,000,000', w:9},
    income:{label:'Monthly gross income (RM)', min:1000, max:100000, step:500, val:12000, pre:'RM', dec:0, lo:'RM 1,000', hi:'RM 100,000', w:8},
    deduct:{label:'EPF, SOCSO & income tax (RM)', min:0, max:50000, step:50, val:1250, pre:'RM', dec:0, lo:'RM 0', hi:'RM 50,000', w:7},
    dsrlim:{label:'Reference DSR limit % (varies by bank)', min:30, max:80, step:1, val:70, suf:'%', dec:0, lo:'30%', hi:'80%', w:4},
    sell:  {label:'Expected selling price (RM)', min:100000, max:20000000, step:10000, val:1200000, pre:'RM', dec:0, lo:'RM 100,000', hi:'RM 20,000,000', w:11},
    dyear: {label:'Year of disposal (4 = sold in the 4th year of ownership)', min:1, max:10, step:1, val:4, suf:'Year', dec:0, lo:'1', hi:'10', w:3},
    rcost: {label:'Legal fees, agent commission and renovation (RM)', min:0, max:1000000, step:1000, val:30000, pre:'RM', dec:0, lo:'RM 0', hi:'RM 1,000,000', w:9}
  };
  const state = {};
  const fmtVal = (k, v) => { const f = FIELDS[k]; return f.dec ? String(parseFloat(v.toFixed(f.dec))) : Math.round(v).toLocaleString('en-US'); };
  function build(k){
    const f = FIELDS[k]; state[k] = f.val;
    return '<div class="sl" data-k="'+k+'"><div class="sl-top"><div class="sl-label">'+f.label+'</div>'+
      '<div class="sl-edit">'+(f.pre?'<span class="pre">'+f.pre+'</span>':'')+
      '<input type="text" inputmode="decimal" id="in_'+k+'" value="'+fmtVal(k,f.val)+'" style="--w:'+f.w+'ch" aria-label="'+f.label+'">'+
      (f.suf?'<span class="suf">'+f.suf+'</span>':'')+(f.amt?'<em class="amt" id="amt_'+k+'"></em>':'')+
      '</div></div>'+
      '<input type="range" class="rng" id="rg_'+k+'" min="'+f.min+'" max="'+f.max+'" step="'+f.step+'" value="'+f.val+'" aria-label="'+f.label+'">'+
      '<div class="sl-range"><span>'+f.lo+'</span><span>'+f.hi+'</span></div></div>';
  }
  $('primaryGrid').innerHTML = ['price','down','rate','years'].map(build).join('');
  document.querySelectorAll('[data-slot]').forEach(el => { el.innerHTML = build(el.dataset.slot); el.classList.add('slot'); });

  const paint = k => { const f = FIELDS[k]; $('rg_'+k).style.setProperty('--p', ((state[k]-f.min)/(f.max-f.min)*100)+'%'); };
  function setVal(k, v, fromText){
    const f = FIELDS[k];
    v = clamp(v, f.min, f.max);
    if(f.dec === 0) v = Math.round(v);
    state[k] = v; $('rg_'+k).value = v;
    if(!fromText) $('in_'+k).value = fmtVal(k, v);
    paint(k);
  }
  Object.keys(FIELDS).forEach(function(k){
    const f = FIELDS[k], inp = $('in_'+k), rg = $('rg_'+k);
    rg.addEventListener('input', function(){ setVal(k, parseFloat(rg.value)); recalc(); });
    inp.addEventListener('input', function(){
      let raw = inp.value.replace(/[^\d.]/g,'');
      if(!f.dec) raw = raw.split('.')[0];
      else { const p = raw.split('.'); raw = p[0] + (p.length>1 ? '.' + p.slice(1).join('').slice(0,f.dec) : ''); }
      const live = raw === '' ? 0 : parseFloat(raw);
      inp.value = f.dec ? raw : (raw === '' ? '' : Math.min(parseFloat(raw), 1e9).toLocaleString('en-US'));
      state[k] = clamp(live, 0, f.max);
      if(live >= f.min) { rg.value = state[k]; paint(k); }
      recalc();
    });
    inp.addEventListener('blur', function(){ setVal(k, inp.value === '' ? f.min : parse(inp.value)); recalc(); });
    inp.addEventListener('keydown', function(e){ if(e.key==='Enter') inp.blur(); });
    paint(k);
  });

  document.querySelectorAll('input.money').forEach(function(inp){
    inp.addEventListener('input', function(){
      const raw = inp.value.replace(/[^\d.]/g,''), parts = raw.split('.');
      parts[0] = parts[0].replace(/^0+(?=\d)/,'').replace(/\B(?=(\d{3})+(?!\d))/g, ',');
      inp.value = parts.length > 1 ? parts[0] + '.' + parts[1].slice(0,4) : parts[0];
      recalc();
    });
  });
  ['i_fire','i_mrta','i_mlta'].forEach(id => $(id).addEventListener('input', recalc));
  $('r_cash0').addEventListener('input', function(){ this.dataset.touched = 1; });

  const motLocal = p => { const tiers = [[100000,0.01],[400000,0.02],[500000,0.03],[Infinity,0.04]]; let left = p, duty = 0;
    for(const [size, rate] of tiers){ const part = Math.min(left, size); if(part <= 0) break; duty += part * rate; left -= part; } return duty; };
  const legal = b => b <= 0 ? 0 : Math.max(500, 0.0125 * Math.min(b, 500000) + 0.01 * Math.max(b - 500000, 0));
  const pmt = (loan, r, n) => (loan > 0 && n > 0) ? (r > 0 ? loan * r / (1 - Math.pow(1 + r, -n)) : loan / n) : 0;
  const ym = m => { const y = Math.floor(m/12), mo = m % 12; return (y? y+' yr ':'') + (mo? mo+' mo':'') || '0'; };
  let lastSyncedPrice = null, lastAreaPrice = null;

  function recalc(){
    const price = state.price, downPct = clamp(state.down, 0, 100), yrs = state.years, rate = state.rate;
    const downAmt = price * downPct / 100, loan = Math.max(price - downAmt, 0), n = Math.round(yrs * 12), r = rate / 100 / 12;
    const buyer = document.querySelector('input[name=d_buyer]:checked').value;
    $('amt_down').textContent = '(' + rm(downAmt) + ')';
    const inst = pmt(loan, r, n), total = inst * n;
    $('foreignInfo').classList.toggle('show', buyer === 'foreign');

    // 1 mortgage
    $('m_loan').textContent = rm(loan); $('m_downamt').textContent = rm(downAmt);
    { const it = Math.max(total - loan, 0), pp = total > 0 ? Math.round(loan / total * 100) : 100, ip = 100 - pp;
      $('bk_p').style.flexBasis = pp + '%'; $('bk_i').style.flexBasis = ip + '%'; $('bk_p').dataset.p = pp + '%'; $('bk_i').dataset.p = ip + '%'; $('bk_i').style.display = ip === 0 ? 'none' : 'flex'; }
    $('m_inst').textContent = rm(inst); $('m_total').textContent = rm(total); $('m_int').textContent = rm(Math.max(total - loan, 0));

    // 2 amortization
    const view = document.querySelector('input[name=am_view]:checked').value;
    let bal = loan, rows = '', yP = 0, yI = 0, yPaid = 0;
    (function(){const h=$('am_h0'),yv=view==='y';h.dataset.v=h.dataset.v||'';})();
    for(let i = 1; i <= n; i++){
      const it = bal * r, pr = Math.min(inst - it, bal); bal = Math.max(bal - pr, 0);
      if(view === 'm') rows += '<tr><td>'+i+'</td><td>'+num(inst,0)+'</td><td>'+num(pr,0)+'</td><td>'+num(it,0)+'</td><td>'+num(bal,0)+'</td></tr>';
      else { yP += pr; yI += it; yPaid += inst;
        if(i % 12 === 0 || i === n){ rows += '<tr><td>'+Math.ceil(i/12)+'</td><td>'+num(yPaid,0)+'</td><td>'+num(yP,0)+'</td><td>'+num(yI,0)+'</td><td>'+num(bal,0)+'</td></tr>'; yP = yI = yPaid = 0; } }
    }
    $('am_body').innerHTML = rows;

    // 3 interest saving
    const extra = state.extra, lump = state.lump;
    let b2 = Math.max(loan - lump, 0), months = 0, int1 = 0;
    while(b2 > 0.005 && months < 1200){ const it = b2 * r; int1 += it; b2 = b2 + it - (inst + extra); months++; if(inst + extra <= it) break; }
    const int0 = Math.max(total - loan, 0);
    const saved = Math.max(int0 - int1, 0), early = Math.max(n - months, 0);
    $('s_saved').textContent = rm(saved);
    $('s_time').textContent = Math.floor(early/12) + ' yr ' + (early % 12) + ' mo';
    $('s_new').textContent = Math.floor(months/12) + ' yr ' + (months % 12) + ' mo';
    $('s_int0').textContent = rm(int0); $('s_int1').textContent = rm(int1);

    // 4 DSR
    const grossInc = state.income, deduct = state.deduct, lim = state.dsrlim;
    const net = Math.max(grossInc - deduct, 0);
    let commit = 0; document.querySelectorAll('input.cm').forEach(e => commit += parse(e.value));
    const oblig = commit + inst;
    const dsr = net > 0 ? oblig / net * 100 : 0;
    const maxInst = Math.max(net * lim / 100 - commit, 0);
    const maxLoan = r > 0 ? maxInst * (1 - Math.pow(1 + r, -n)) / r : maxInst * n;
    const maxPrice = downPct < 100 ? maxLoan / (1 - downPct / 100) : 0;
    const over = dsr > lim;
    $('c_sum').textContent = rm(commit);
    $('a_dsr').textContent = dsr.toFixed(1) + '%';
    $('a_fill').style.width = Math.min(dsr, 100) + '%'; $('a_fill').classList.toggle('over', over);
    $('a_mark').style.left = lim + '%'; $('a_l1').dataset.p = '<' + lim + '%'; $('a_l2').dataset.p = lim + '%';
    $('a_ok').classList.toggle('show', !over); $('a_bad').classList.toggle('show', over);
    $('a_net').textContent = rm(net); $('a_inst').textContent = rm(inst); $('a_oblig').textContent = rm(oblig);
    $('a_maxinst').textContent = rm(maxInst); $('a_maxloan').textContent = rm(maxLoan); $('a_maxprice').textContent = downPct < 100 ? rm(maxPrice) : '-';

    // 5 purchase cost
    const type = 'res', wantFirst = $('d_first').checked;
    const eligible = buyer === 'local' && type === 'res' && price > 0 && price <= 500000;
    const exempt = wantFirst && eligible, foreignRes = buyer === 'foreign' && type === 'res';
    let mot = foreignRes ? price * 0.08 : motLocal(price), ld = loan * 0.005;
    if(exempt){ mot = 0; ld = 0; }
    const src = document.querySelector('input[name=d_src]:checked').value;
    const spa = legal(price), lf = legal(loan);
    const consent = foreignRes ? 2000 : 0;
    $('c_consent_row').style.display = foreignRes ? '' : 'none';
    $('c_consent_out').textContent = rm(consent);
    $('d_flag_dev').classList.toggle('show', src === 'dev'); $('d_flag_sub').classList.toggle('show', src === 'sub');
    $('mot_table').style.display = buyer === 'local' ? '' : 'none';
    [100000,500000,1000000,Infinity].some(function(lim,i){ const hit = price <= lim; if(hit) [0,1,2,3].forEach(function(j){ $('mot_r'+j).classList.toggle('hl', j === i); }); return hit; });
    $('d_motlbl').classList.toggle('f8', foreignRes);
    $('d_mot').textContent = rm(mot); $('d_loanduty').textContent = rm(ld);
    $('c_spa').textContent = rm(spa); $('c_loanfee').textContent = rm(lf);
    $('c_total').textContent = rm(mot + ld + spa + lf + consent); $('c_cash').textContent = rm(downAmt + mot + ld + spa + lf + consent);
    $('d_flag_first').classList.toggle('show', exempt);
    $('d_flag_foreign').classList.toggle('show', foreignRes);
    $('d_flag_notfirst').classList.toggle('show', wantFirst && !eligible);

    // timeline
    { const pcts = [10, 10, 15, 10, 10, 10, 5, 2.5, 2.5, 17.5, 2.5, 5]; let dleft = downAmt, cum = 0, totClaim = 0, totBank = 0;
      pcts.forEach(function(p, i){ const c = price * p / 100, bp = Math.min(c, dleft); dleft -= bp; const bank = c - bp; cum += bank; totClaim += c; totBank += bank;
        $('t_c'+i).textContent = rm(c); $('t_b'+i).textContent = rm(bank); $('t_u'+i).textContent = rm(cum); $('t_i'+i).textContent = rm(cum * rate / 100 / 12); });
      $('t_price').textContent = rm(price); $('t_down').textContent = rm(downAmt); $('t_loan').textContent = rm(loan); $('t_full').textContent = rm(loan * rate / 100 / 12); }

    // 6 rental
    if(!$('r_cash0').dataset.touched && $('r_cash0').dataset.last !== String(downAmt)){ $('r_cash0').value = Math.round(downAmt).toLocaleString('en-US'); $('r_cash0').dataset.last = String(downAmt); }
    const rent = state.rent, rocc = state.rocc / 100, maintY = parse($('r_maint').value) * 12, othY = parse($('r_exp').value), costsY = maintY + othY, cash0 = parse($('r_cash0').value);
    const incomeStd = rent * 12 * rocc, netStd = incomeStd - costsY, annualCF = netStd - inst * 12;
    const signed = v => (v < 0 ? '-' : '') + rm(Math.abs(v));
    $('r_price').textContent = rm(price); $('r_inst').textContent = rm(inst);
    $('r_gross').textContent = pc(price > 0 ? rent * 12 / price * 100 : 0);
    $('r_net').textContent = pc(price > 0 ? netStd / price * 100 : 0);
    $('r_annual').textContent = signed(annualCF);
    $('r_coc').textContent = pc(cash0 > 0 ? annualCF / cash0 * 100 : 0);
    $('r_be').textContent = rocc > 0 ? rm((costsY + inst * 12) / (12 * rocc)) : '-';
    { const sOcc = state.occ, sNights = 365 * sOcc / 100, sRev = sNights * state.nightly, sNet = sRev - costsY, sCF = sNet - inst * 12;
      $('s_n').textContent = Math.round(sNights); $('s_p').textContent = '(' + sOcc + '%)'; $('s_rev').textContent = rm(sRev);
      $('s_net').textContent = pc(price > 0 ? sNet / price * 100 : 0); $('s_income').textContent = signed(sNet);
      $('s_gross').textContent = pc(price > 0 ? sRev / price * 100 : 0); $('s_costs').textContent = rm(costsY);
      $('s_inst').textContent = rm(inst); $('s_annual').textContent = signed(sCF); $('s_coc').textContent = pc(cash0 > 0 ? sCF / cash0 * 100 : 0);
      $('s_cmp').textContent = pc(price > 0 ? netStd / price * 100 : 0); }
    { const m = document.querySelector('input[name=rent_mode]:checked').value; $('rent-std').style.display = m === 'std' ? '' : 'none'; $('rent-air').style.display = m === 'air' ? '' : 'none'; }

    // 7 RPGT
    const sell = state.sell, yr = state.dyear, costs = state.rcost, cat = document.querySelector('input[name=g_cat]:checked').value;
    const RT = [[30,30,30],[30,30,30],[20,20,30],[15,15,30],[0,10,10]], ci = {cit:0, co:1, for:2}[cat], ri = yr <= 2 ? 0 : yr === 3 ? 1 : yr === 4 ? 2 : yr === 5 ? 3 : 4, rt = RT[ri][ci];
    for(let i = 0; i < 5; i++){ const tr = $('rt_r'+i); tr.classList.toggle('hl', i === ri); [...tr.children].forEach(function(td, c){ td.classList.toggle('hc', i === ri && c === ci + 1); }); }
    const gain = Math.max(sell - price - costs, 0);
    const ex = cat === 'co' ? 0 : Math.min(Math.max(10000, gain * 0.1), gain), taxable = Math.max(gain - ex, 0), tax = taxable * rt / 100;
    $('g_buy').textContent = rm(price); $('g_rate').textContent = rt + '%'; $('g_gain').textContent = rm(gain);
    $('g_ex').textContent = rm(ex); $('g_taxable').textContent = rm(taxable); $('g_tax').textContent = rm(tax);
    $('g_net').textContent = (sell - price - costs - tax < 0 ? '-' : '') + rm(Math.abs(sell - price - costs - tax));

    // 8 insurance
    if(!$('i_sum').dataset.touched && lastSyncedPrice !== price){ $('i_sum').value = Math.round(price).toLocaleString('en-US'); lastSyncedPrice = price; }
    $('i_fire_out').textContent = rm(parse($('i_sum').value) / 1000 * parse($('i_fire').value));
    $('i_mrta_out').textContent = rm(loan * parse($('i_mrta').value) / 100);
    $('i_mlta_out').textContent = rm(loan * parse($('i_mlta').value) / 100);
    $('i_loan').textContent = rm(loan);

    // 9 area & currency
    if(lastAreaPrice !== price){ lastAreaPrice = price; const a0 = parse($('u_val').value);
      $('u_total').value = Math.round(price).toLocaleString('en-US'); $('u_psf_in').value = a0 > 0 ? (price / a0).toLocaleString('en-US',{maximumFractionDigits:2}) : '0';
      if(!$('cv_amt').dataset.touched && $('cv_from').value === 'MYR') $('cv_amt').value = Math.round(price).toLocaleString('en-US'); }
    const areaV = parse($('u_val').value), totalV = parse($('u_total').value), sqft = areaV, sqm = sqft / 10.7639, ping = sqft / 35.5832;
    $('a_sqft').textContent = num(sqft,2); $('a_sqm').textContent = num(sqm,2); $('a_ping').textContent = num(ping,2);
    const upf = sqft > 0 ? totalV / sqft : 0, ups = sqm > 0 ? totalV / sqm : 0, upp = ping > 0 ? totalV / ping : 0;
    $('up_sqft').textContent = 'RM ' + num(upf,2); $('up_sqm').textContent = 'RM ' + num(ups,0); $('up_ping').textContent = 'RM ' + num(upp,0);
    const RATE = {MYR:1, USD:0.21, SGD:0.285, CNY:1.52, JPY:31.5, KRW:290}, SYM = {MYR:'RM', USD:'US$', SGD:'S$', CNY:'CN¥', JPY:'JP¥', KRW:'₩'};
    const f = $('cv_from').value, t = $('cv_to').value, per = RATE[t] / RATE[f], conv = parse($('cv_amt').value) * per;
    $('cv_out').textContent = num(conv, (t === 'JPY' || t === 'KRW') ? 0 : 2) + ' ' + t;
    $('cv_rate').textContent = '1 ' + f + ' = ' + per.toFixed(4) + ' ' + t;
    const rt2 = RATE[t], d2 = (t === 'JPY' || t === 'KRW') ? 0 : 2;
    $('cu_sqft').textContent = SYM[t] + ' ' + num(upf * rt2, d2); $('cu_sqm').textContent = SYM[t] + ' ' + num(ups * rt2, d2 ? 0 : 0); $('cu_ping').textContent = SYM[t] + ' ' + num(upp * rt2, 0);
  }
  $('u_val').addEventListener('input', function(){ $('u_total').value = Math.round(parse($('u_val').value) * parse($('u_psf_in').value)).toLocaleString('en-US'); recalc(); });
  $('u_psf_in').addEventListener('input', function(){ $('u_total').value = Math.round(parse($('u_val').value) * parse($('u_psf_in').value)).toLocaleString('en-US'); recalc(); });
  $('u_total').addEventListener('input', function(){ const a = parse($('u_val').value); $('u_psf_in').value = a > 0 ? (parse($('u_total').value) / a).toLocaleString('en-US',{maximumFractionDigits:2}) : '0'; recalc(); });
  $('cv_amt').addEventListener('input', function(){ this.dataset.touched = 1; recalc(); });
  $('cv_from').addEventListener('change', recalc); $('cv_to').addEventListener('change', recalc);
  $('cv_swap').addEventListener('click', function(){ const f = $('cv_from').value, t = $('cv_to').value, outTxt = $('cv_out').textContent.replace(/[^\d.]/g,'');
    $('cv_from').value = t; $('cv_to').value = f; $('cv_amt').value = outTxt ? Number(outTxt).toLocaleString('en-US',{maximumFractionDigits:2}) : '0'; $('cv_amt').dataset.touched = 1; recalc(); });
  $('i_sum').addEventListener('input', function(){ this.dataset.touched = 1; });
  document.querySelectorAll('input[name=d_buyer],input[name=d_src],input[name=g_cat],input[name=rent_mode],input[name=am_view],#d_first').forEach(el => el.addEventListener('change', recalc));
  document.querySelectorAll('.calc-opt').forEach(function(tab){
    tab.addEventListener('click', function(){
      document.querySelectorAll('.calc-opt').forEach(t => t.classList.toggle('active', t === tab));
      document.querySelectorAll('.calc-panel').forEach(p => p.classList.toggle('active', p.id === 'panel-' + tab.dataset.tab));
    });
  });
  function syncNat(from, to){ document.querySelectorAll('input[name='+from+']').forEach(function(el){ el.addEventListener('change', function(){ document.querySelectorAll('input[name='+to+']').forEach(function(o){ o.checked = (o.value === el.value) && el.checked || o.checked && o.value === el.value; }); const t = document.querySelector('input[name='+to+'][value='+el.value+']'); if(t) t.checked = true; recalc(); }); }); }
  syncNat('d_buyer','d_nat'); syncNat('d_nat','d_buyer');
  // Opened from a project page: ?price=&down=&rate=&years=&tab=
  try {
    const q = new URLSearchParams(location.search);
    ['price','down','rate','years'].forEach(function(k){ const v = parseFloat(q.get(k)); if(!isNaN(v)) setVal(k, v); });
    const tb = q.get('tab'), btn = tb && document.querySelector('.calc-opt[data-tab="'+tb+'"]');
    if(btn) btn.click();
  } catch(e) {}
  recalc();
})();
