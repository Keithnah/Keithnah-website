/**
 * KNRE Leads: Google Apps Script web app.
 *
 * Receives leads from lead-tracker.js on the website, adds one row per lead
 * to the "Leads" tab of the KNRE Leads Google Sheet, and sends a Telegram
 * message for each new lead.
 *
 * Setup (once):
 * 1. Open the KNRE Leads sheet > Extensions > Apps Script.
 * 2. Replace everything in Code.gs with this file and click Save.
 * 3. Deploy > New deployment > type "Web app".
 *    Execute as: Me. Who has access: Anyone. Click Deploy and allow access.
 * 4. Copy the Web app URL (ends in /exec) into LEADS_ENDPOINT in lead-tracker.js.
 *
 * Telegram notifications (optional):
 * 1. In Telegram, create a bot with @BotFather and copy its token.
 * 2. Send any message (e.g. "hi") to your new bot.
 * 3. Project Settings (gear icon) > Script Properties > add
 *    TELEGRAM_BOT_TOKEN = the token from BotFather.
 * 4. Run getTelegramChatId once: it finds your chat and saves TELEGRAM_CHAT_ID.
 * 5. Run testTelegram: you should get a test message.
 * 6. Deploy > Manage deployments > edit (pencil) > Version: New version > Deploy.
 *    This keeps the same /exec URL, so the website needs no change.
 * To stop messages for WhatsApp button clicks (keep Quick Enquiry only),
 * add the Script Property TELEGRAM_NOTIFY_CLICKS = no.
 *
 * Other websites can use the same URL: send a different "source" name
 * and add that name to column A of the Summary tab.
 */

var SHEET_NAME = 'Leads';
var MAX_LEN = 2000;
var TIME_ZONE = 'Asia/Kuala_Lumpur';

function doPost(e) {
  var d0 = {};
  try { d0 = JSON.parse((e && e.postData && e.postData.contents) || '{}'); } catch (err) { d0 = {}; }
  // Daily market-note topics (Keith picks 1-3 a day): Telegram button presses and messages from the Claude session
  if (d0.update_id !== undefined) return handleTelegramUpdate(e, d0);
  if (d0.type === 'Topic Proposal') return saveTopicProposal(d0);
  if (d0.type === 'Topic Published') return markTopicPublished(d0);
  if (d0.type === 'Site Check') return siteCheck_(d0);
  if (d0.type === 'Update Done') return updateDone_(d0);

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  var d = {}, type = '';
  try {
    d = d0;

    type = clean(d.type);
    if (type !== 'WhatsApp Click' && type !== 'Quick Enquiry') {
      return ContentService.createTextOutput('ignored');
    }

    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
    sheet.appendRow([
      new Date(),            // Date & Time
      clean(d.source),       // Source Website
      type,                  // Lead Type
      clean(d.page),         // Page
      clean(d.button),       // Button Clicked
      clean(d.name),         // Name
      asText(d.code),        // Country Code
      asText(d.phone),       // WhatsApp Number
      clean(d.email),        // Email
      clean(d.area),         // Preferred Area
      clean(d.look),         // Looking For
      clean(d.message),      // WhatsApp Message
      clean(d.lang),         // Language
      clean(d.device),       // Device
      clean(d.referrer),     // Came From (Referrer)
      clean(d.url),          // Page URL
      'New',                 // Follow-up Status
      ''                     // Notes
    ]);
  } finally {
    lock.releaseLock();
  }

  // The lead is already saved; a Telegram problem must never lose it.
  try { notifyTelegram(type, d); } catch (err) { console.error('Telegram: ' + err); }
  return ContentService.createTextOutput('ok');
}

function doGet(e) {
  if (e && e.parameter && e.parameter.action === 'topics') return topicStatus(e.parameter.date);
  if (e && e.parameter && e.parameter.action === 'updates') return json_({ ok: true, updates: pendingUpdates_() });
  return ContentService.createTextOutput('KNRE lead tracker is running.');
}

/* ---------- Daily market-note topics (Keith's Market Notes on the News page) ----------
 * 1. Every morning a Claude session sends 5 topic ideas here (type "Topic Proposal").
 * 2. This script sends them to Keith on Telegram with one button per topic.
 * 3. Keith taps a topic; Telegram calls this web app (the webhook), the choice is saved.
 * 4. A Claude session reads the choice (?action=topics), writes and publishes the note,
 *    then reports back (type "Topic Published") and Keith gets the link on Telegram.
 * Setup once: Deploy > Manage deployments > New version, then run setTelegramWebhook.
 */
var TOPIC_KEEP_DAYS = 7;
var HOOK_URL = 'https://keithnah.com/tg/hook.php';   // Telegram webhook relay on the website

function json_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function today_() { return Utilities.formatDate(new Date(), TIME_ZONE, 'yyyy-MM-dd'); }
// A topic round is "YYYY-MM-DD" or "YYYY-MM-DD-1/2/3" (morning, afternoon, evening).
function okDate_(s) { return /^\d{4}-\d{2}-\d{2}(-[1-3])?$/.test(String(s || '')) ? String(s) : ''; }
var ROUND_NAMES = { '1': '早上', '2': '下午', '3': '傍晚' };
function roundLabel_(id) { var m = String(id).match(/-([1-3])$/); return m ? ROUND_NAMES[m[1]] + ' · ' + id.slice(0, 10) : id; }

function tg_(method, payload) {
  var token = PropertiesService.getScriptProperties().getProperty('TELEGRAM_BOT_TOKEN');
  if (!token) throw new Error('TELEGRAM_BOT_TOKEN is not set.');
  return JSON.parse(UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/' + method, {
    method: 'post', contentType: 'application/json', payload: JSON.stringify(payload), muteHttpExceptions: true
  }).getContentText());
}

var MAX_PICKS = 5;   // Keith can pick 1 to all 5 topics

function topicKeyboard_(o) {
  var picked = o.picks || [];
  var row = o.topics.map(function (t) {
    var on = picked.indexOf(t.n) >= 0;
    return { text: (on ? '✅ ' : '') + t.n, callback_data: 'pick|' + o.date + '|' + t.n };
  });
  return [row, [{ text: picked.length ? '📤 发送 (' + picked.length + ')' : '今天不发', callback_data: (picked.length ? 'done|' : 'skip|') + o.date }]];
}

function saveTopicProposal(d) {
  var date = okDate_(d.date) || today_();
  var topics = (d.topics || []).slice(0, 5).map(function (t, i) {
    return { n: i + 1, zh: plain(t.zh).slice(0, 120), en: plain(t.en).slice(0, 160), brief: plain(t.brief).slice(0, 1500), area: plain(t.area).slice(0, 60) };
  }).filter(function (t) { return t.zh || t.en; });
  if (topics.length < 2) return json_({ ok: false, error: 'need at least 2 topics' });
  var props = PropertiesService.getScriptProperties();
  var chatId = props.getProperty('TELEGRAM_CHAT_ID');
  var o = { date: date, topics: topics, picks: [], closed: false, published: [] };
  var lines = ['📰 <b>市场短评：选 1 至 ' + MAX_PICKS + ' 个主题</b> · ' + roundLabel_(date), ''];
  topics.forEach(function (t) { lines.push('<b>' + t.n + '.</b> ' + esc(t.zh || t.en) + (t.en && t.zh ? '\n<i>' + esc(t.en) + '</i>' : '')); lines.push(''); });
  lines.push('点数字选择（再点一次取消），选好后按下方「📤 发送」。每个主题会写成一则短评并自动上线。');
  var r = tg_('sendMessage', { chat_id: chatId, text: lines.join('\n'), parse_mode: 'HTML', reply_markup: { inline_keyboard: topicKeyboard_(o) } });
  o.msg = r && r.result ? r.result.message_id : null;
  cleanupTopics_();   // before saving, so a test proposal dated 2000-01-01 survives
  props.setProperty('TOPICS_' + date, JSON.stringify(o));
  return json_({ ok: !!(r && r.ok), date: date, count: topics.length });
}

function topicStatus(date) {
  date = okDate_(date) || today_();
  var raw = PropertiesService.getScriptProperties().getProperty('TOPICS_' + date);
  if (!raw) return json_({ ok: true, date: date, found: false });
  var o = JSON.parse(raw), done = (o.published || []).map(function (x) { return x.n; });
  var chosen = o.closed ? o.topics.filter(function (t) { return (o.picks || []).indexOf(t.n) >= 0; }) : [];
  var todo = chosen.filter(function (t) { return done.indexOf(t.n) < 0; });
  return json_({ ok: true, date: date, found: true, closed: !!o.closed, skipped: !!o.closed && !(o.picks || []).length,
                 picks: o.picks || [], chosen: chosen, todo: todo, published: o.published || [] });
}

function markTopicPublished(d) {
  var date = okDate_(d.date) || today_();
  var props = PropertiesService.getScriptProperties();
  var raw = props.getProperty('TOPICS_' + date);
  if (!raw) return json_({ ok: false, error: 'no topics for ' + date });
  var o = JSON.parse(raw), n = parseInt(d.n, 10);
  if (!o.closed || (o.picks || []).indexOf(n) < 0) return json_({ ok: false, error: 'topic ' + d.n + ' was not picked' });
  o.published = o.published || [];
  if (o.published.some(function (x) { return x.n === n; })) return json_({ ok: true, already: true });
  var url = String(d.url || '');
  if (!/^https:\/\/keithnah\.com\//.test(url)) return json_({ ok: false, error: 'bad url' });
  o.published.push({ n: n, url: url, at: new Date().toISOString() });
  props.setProperty('TOPICS_' + date, JSON.stringify(o));
  tg_('sendMessage', { chat_id: props.getProperty('TELEGRAM_CHAT_ID'), parse_mode: 'HTML', disable_web_page_preview: true,
    text: '✅ <b>已上线</b>（' + o.published.length + '/' + o.picks.length + '）：' + esc(plain(d.title) || '') + '\n' + esc(url) });
  return json_({ ok: true });
}

function handleTelegramUpdate(e, u) {
  var props = PropertiesService.getScriptProperties();
  var secret = props.getProperty('TG_WEBHOOK_SECRET');
  if (!secret || !e.parameter || e.parameter.tg !== secret) return ContentService.createTextOutput('ignored');
  if (u.message) return handleTelegramMessage_(u);
  var q = u.callback_query;
  if (!q || !q.message || String(q.message.chat.id) !== String(props.getProperty('TELEGRAM_CHAT_ID'))) return ContentService.createTextOutput('ok');
  var lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    // Telegram may deliver the same button press more than once (it retries when the web app answers
    // with a redirect). Handle each press once, or a pick would be undone by its own repeat.
    var cache = CacheService.getScriptCache();
    if (cache.get('tgcb_' + q.id) || cache.get('tgup_' + u.update_id)) return ContentService.createTextOutput('ok');
    cache.put('tgcb_' + q.id, '1', 21600); cache.put('tgup_' + u.update_id, '1', 21600);
    var parts = String(q.data || '').split('|'), act = parts[0], date = okDate_(parts[1]);
    var raw = date && props.getProperty('TOPICS_' + date);
    if (!raw) { tg_('answerCallbackQuery', { callback_query_id: q.id, text: '这组主题已过期。' }); return ContentService.createTextOutput('ok'); }
    var o = JSON.parse(raw); o.picks = o.picks || [];
    if (o.closed) { tg_('answerCallbackQuery', { callback_query_id: q.id, text: '今天的选择已经完成。' }); return ContentService.createTextOutput('ok'); }
    if (act === 'pick') {
      var n = parseInt(parts[2], 10), i = o.picks.indexOf(n);
      if (!o.topics.some(function (x) { return x.n === n; })) { tg_('answerCallbackQuery', { callback_query_id: q.id, text: '找不到这个主题。' }); return ContentService.createTextOutput('ok'); }
      if (i >= 0) o.picks.splice(i, 1);
      else if (o.picks.length >= MAX_PICKS) { tg_('answerCallbackQuery', { callback_query_id: q.id, text: '最多选 ' + MAX_PICKS + ' 个，先取消一个。' }); return ContentService.createTextOutput('ok'); }
      else o.picks.push(n);
      o.picks.sort(function (a, b) { return a - b; });
      props.setProperty('TOPICS_' + date, JSON.stringify(o));
      tg_('answerCallbackQuery', { callback_query_id: q.id, text: o.picks.length ? '已选：' + o.picks.join('、') + '，选好后按「📤 发送」' : '已取消' });
      if (o.msg) tg_('editMessageReplyMarkup', { chat_id: q.message.chat.id, message_id: o.msg, reply_markup: { inline_keyboard: topicKeyboard_(o) } });
      return ContentService.createTextOutput('ok');
    }
    o.closed = true; o.closedAt = new Date().toISOString();
    props.setProperty('TOPICS_' + date, JSON.stringify(o));
    tg_('answerCallbackQuery', { callback_query_id: q.id, text: o.picks.length ? '好的' : '今天不发' });
    if (o.msg) tg_('editMessageReplyMarkup', { chat_id: q.message.chat.id, message_id: o.msg, reply_markup: { inline_keyboard: [] } });
    var text = o.picks.length
      ? '✍️ 已选 ' + o.picks.length + ' 个主题：\n' + o.topics.filter(function (t) { return o.picks.indexOf(t.n) >= 0; }).map(function (t) { return '• ' + esc(t.zh || t.en); }).join('\n') + '\n短评写好后会自动上线（约 1 小时内），每则上线后会通知你。'
      : '👌 今天不发短评。';
    tg_('sendMessage', { chat_id: q.message.chat.id, text: text, parse_mode: 'HTML' });
  } finally { lock.releaseLock(); }
  return ContentService.createTextOutput('ok');
}

function cleanupTopics_() {
  var props = PropertiesService.getScriptProperties(), all = props.getProperties();
  var limit = Utilities.formatDate(new Date(Date.now() - TOPIC_KEEP_DAYS * 864e5), TIME_ZONE, 'yyyy-MM-dd');
  Object.keys(all).forEach(function (k) { if (k.indexOf('TOPICS_') === 0 && k.slice(7) < limit) props.deleteProperty(k); });
}

// Run once from the editor after deploying a new version: Telegram will send button presses here.
function setTelegramWebhook() {
  var props = PropertiesService.getScriptProperties();
  var secret = props.getProperty('TG_WEBHOOK_SECRET');
  if (!secret) { secret = Utilities.getUuid().replace(/-/g, ''); props.setProperty('TG_WEBHOOK_SECRET', secret); }
  // Telegram calls the relay on the website (keithnah.com/tg/hook.php). It answers Telegram at once and
  // passes the update to this web app with Telegram's secret header as ?tg=. Pointing Telegram straight at
  // this web app works badly: it answers with a redirect, so Telegram retries and the buttons feel stuck.
  var r = tg_('setWebhook', { url: HOOK_URL, secret_token: secret, allowed_updates: ['callback_query', 'message'], drop_pending_updates: true });
  console.log(r.ok ? 'Webhook set. Tap a button in Telegram to test.' : 'Telegram said: ' + JSON.stringify(r));
}

// Run from the editor to send yourself a sample topic message with buttons.
function testTopics() {
  // test date 2000-01-01: the daily publisher only looks at today's topics, so a test pick is never published
  saveTopicProposal({ date: '2000-01-01', topics: [
    { zh: '测试主题一', en: 'Test topic one' }, { zh: '测试主题二', en: 'Test topic two' }, { zh: '测试主题三', en: 'Test topic three' }] });
  console.log('Sent. Tap a button in Telegram.');
}

/* ---------- Telegram ---------- */

function notifyTelegram(type, d) {
  var props = PropertiesService.getScriptProperties();
  var token = props.getProperty('TELEGRAM_BOT_TOKEN');
  var chatId = props.getProperty('TELEGRAM_CHAT_ID');
  if (!token || !chatId) return;
  if (type === 'WhatsApp Click' && String(props.getProperty('TELEGRAM_NOTIFY_CLICKS')).toLowerCase() === 'no') return;
  sendTelegram(token, chatId, buildLeadMessage(type, d));
}

function buildLeadMessage(type, d) {
  var when = Utilities.formatDate(new Date(), TIME_ZONE, 'dd MMM yyyy, h:mm a');
  var site = esc(plain(d.source) || 'Website');
  var lines = [];
  if (type === 'Quick Enquiry') {
    var phone = (plain(d.code) + ' ' + plain(d.phone)).trim();
    var waNumber = waDigits(d.code, d.phone);
    lines.push('🔔 <b>New Quick Enquiry</b> · ' + site);
    lines.push('');
    lines.push('👤 <b>' + esc(plain(d.name) || '-') + '</b>');
    lines.push('📱 ' + esc(phone || '-') + (waNumber ? '  <a href="https://wa.me/' + waNumber + '">Reply on WhatsApp</a>' : ''));
    if (plain(d.email)) lines.push('✉️ ' + esc(plain(d.email)));
    if (plain(d.area)) lines.push('📍 ' + esc(plain(d.area)));
    if (plain(d.look)) lines.push('🎯 ' + esc(plain(d.look)));
  } else {
    lines.push('💬 <b>WhatsApp button clicked</b> · ' + site);
    lines.push('');
    if (plain(d.button)) lines.push('🔘 ' + esc(plain(d.button)));
    if (plain(d.message)) lines.push('📝 ' + esc(plain(d.message)));
    lines.push('The visitor may message you on WhatsApp shortly.');
  }
  lines.push('');
  lines.push('📄 ' + esc(plain(d.page) || '-') + ' · ' + esc(plain(d.device) || '-') + ' · ' + esc(plain(d.lang) || '-'));
  lines.push('🕒 ' + when);
  return lines.join('\n');
}

function sendTelegram(token, chatId, text) {
  var res = UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/sendMessage', {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({ chat_id: chatId, text: text, parse_mode: 'HTML', disable_web_page_preview: true }),
    muteHttpExceptions: true
  });
  if (res.getResponseCode() !== 200) throw new Error(res.getResponseCode() + ' ' + res.getContentText());
}

// Run once from the editor after messaging your bot: finds and saves your chat ID.
function getTelegramChatId() {
  var props = PropertiesService.getScriptProperties();
  var token = props.getProperty('TELEGRAM_BOT_TOKEN');
  if (!token) throw new Error('Add the Script Property TELEGRAM_BOT_TOKEN first.');
  var res = JSON.parse(UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/getUpdates', { muteHttpExceptions: true }).getContentText());
  if (!res.ok) throw new Error('Telegram refused the token: ' + (res.description || 'unknown error'));
  var chats = {};
  (res.result || []).forEach(function (u) {
    var m = u.message || u.channel_post || u.my_chat_member;
    if (m && m.chat) chats[m.chat.id] = m.chat.title || [m.chat.first_name, m.chat.last_name].join(' ').trim() || m.chat.username || '';
  });
  var ids = Object.keys(chats);
  if (ids.length === 0) throw new Error('No messages found. Send "hi" to your bot in Telegram, then run this again.');
  if (ids.length > 1) {
    console.log('Several chats found. Set TELEGRAM_CHAT_ID to the right one yourself:');
    ids.forEach(function (id) { console.log(id + '  ' + chats[id]); });
    return;
  }
  props.setProperty('TELEGRAM_CHAT_ID', ids[0]);
  console.log('Saved TELEGRAM_CHAT_ID = ' + ids[0] + ' (' + chats[ids[0]] + '). Now run testTelegram.');
}

// Run from the editor to send yourself a sample Quick Enquiry message.
function testTelegram() {
  var props = PropertiesService.getScriptProperties();
  var token = props.getProperty('TELEGRAM_BOT_TOKEN'), chatId = props.getProperty('TELEGRAM_CHAT_ID');
  if (!token || !chatId) throw new Error('Set TELEGRAM_BOT_TOKEN and run getTelegramChatId first.');
  sendTelegram(token, chatId, buildLeadMessage('Quick Enquiry', {
    source: 'KNRE website', name: 'TEST - sample lead', code: '+60', phone: '123456789',
    email: 'test@example.com', area: 'Bukit Bintang', look: 'Investment',
    page: 'Home', device: 'Mobile', lang: 'en'
  }));
  console.log('Test message sent. Check Telegram.');
}

/* ---------- Helpers ---------- */

// Trim, cap length, and stop text starting with = + - @ from running as a formula.
function clean(v) {
  var s = String(v == null ? '' : v).trim().slice(0, MAX_LEN);
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}

// Keep phone numbers and codes such as +60 or 0123 as text.
function asText(v) {
  var s = String(v == null ? '' : v).trim().slice(0, 40);
  return s ? "'" + s : '';
}

function plain(v) { return String(v == null ? '' : v).trim().slice(0, 500); }

function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }

// +60 and 012-345 6789 -> 60123456789 (WhatsApp link format).
function waDigits(code, phone) {
  var c = String(code || '').replace(/\D/g, ''), p = String(phone || '').replace(/\D/g, '');
  if (!p) return '';
  if (c && p.indexOf(c) === 0 && p.length > 9) return p; // number already includes the code
  return c + p.replace(/^0+/, '');
}

// Run from the editor to see whether Telegram can reach the web app.
function checkTelegramWebhook() {
  var r = tg_('getWebhookInfo', {});
  var u = r.result || {};
  console.log('url: ' + String(u.url || '').replace(/\?tg=.*/, '?tg=(hidden)'));
  console.log('pending updates: ' + u.pending_update_count);
  console.log('last error: ' + (u.last_error_message || 'none') + (u.last_error_date ? ' at ' + new Date(u.last_error_date * 1000) : ''));
}


/* ---------- Website updates from Telegram ----------
 * Keith sends e.g. "/update Clouthaus starting price now RM1.2M" (or /改, 更新) to the bot.
 * The request is queued here; the hourly Claude publishing session reads ?action=updates,
 * makes the change on keithnah.com, publishes it, and reports back (type "Update Done").
 * Only messages from TELEGRAM_CHAT_ID are accepted. Needs setTelegramWebhook to be run again
 * once, so Telegram also sends messages (not only button presses).
 */
var MAX_UPDATES = 20;

function handleTelegramMessage_(u) {
  var props = PropertiesService.getScriptProperties(), m = u.message;
  if (!m.chat || String(m.chat.id) !== String(props.getProperty('TELEGRAM_CHAT_ID'))) return ContentService.createTextOutput('ok');
  var cache = CacheService.getScriptCache();
  if (cache.get('tgup_' + u.update_id)) return ContentService.createTextOutput('ok');
  cache.put('tgup_' + u.update_id, '1', 21600);
  var text = String(m.text || '').trim();
  var cmd = text.match(/^(\/update(?:@\w+)?|\/改|\/更新|更新|修改)\s*([\s\S]*)$/i);
  if (cmd) {
    var req = cmd[2].trim().slice(0, 1500);
    if (!req) {
      tg_('sendMessage', { chat_id: m.chat.id, text: '请在 /update 后面写要改什么，例如：\n/update Clouthaus 起价改成 RM1,200,000' });
      return ContentService.createTextOutput('ok');
    }
    var lock = LockService.getScriptLock(); lock.waitLock(10000);
    try {
      var list = pendingUpdates_();
      if (list.length >= MAX_UPDATES) {
        tg_('sendMessage', { chat_id: m.chat.id, text: '待处理的更新已经有 ' + list.length + ' 个，请等它们完成后再发。' });
        return ContentService.createTextOutput('ok');
      }
      var id = Utilities.formatDate(new Date(), TIME_ZONE, 'yyyyMMdd-HHmmss') + '-' + Math.floor(Math.random() * 1000);
      list.push({ id: id, text: req, at: new Date().toISOString() });
      props.setProperty('SITE_UPDATES', JSON.stringify(list));
    } finally { lock.releaseLock(); }
    tg_('sendMessage', { chat_id: m.chat.id, parse_mode: 'HTML', text: '📝 收到网站更新：\n<i>' + esc(req) + '</i>\n一小时内会更新（早上 9 点到晚上 11 点），完成后会通知你。' });
  } else if (/^\/(help|start)/i.test(text)) {
    tg_('sendMessage', { chat_id: m.chat.id, text: '可以用的指令：\n/update 要改的内容 — 更新网站资料，例如「/update Clouthaus 起价改成 RM1,200,000」\n/report — 马上发本周网站数据报告\n/updates — 查看还在等待的更新' });
  } else if (/^\/report/i.test(text)) {
    try { weeklyReport(); } catch (err) { tg_('sendMessage', { chat_id: m.chat.id, text: '报告失败：' + err.message }); }
  } else if (/^\/updates/i.test(text)) {
    var l = pendingUpdates_();
    tg_('sendMessage', { chat_id: m.chat.id, text: l.length ? '等待中的更新：\n' + l.map(function (x) { return '• ' + x.text; }).join('\n') : '没有等待中的更新。' });
  }
  return ContentService.createTextOutput('ok');
}

function pendingUpdates_() {
  try { return JSON.parse(PropertiesService.getScriptProperties().getProperty('SITE_UPDATES') || '[]'); } catch (e) { return []; }
}

function updateDone_(d) {
  var props = PropertiesService.getScriptProperties();
  var lock = LockService.getScriptLock(); lock.waitLock(10000);
  var item;
  try {
    var list = pendingUpdates_();
    item = list.filter(function (x) { return x.id === d.id; })[0];
    if (!item) return json_({ ok: false, error: 'no such update' });
    if (d.status !== 'unclear') props.setProperty('SITE_UPDATES', JSON.stringify(list.filter(function (x) { return x.id !== d.id; })));
  } finally { lock.releaseLock(); }
  var url = String(d.url || '');
  if (url && !/^https:\/\/keithnah\.com\//.test(url)) url = '';
  var head = d.status === 'done' ? '✅ 网站已更新' : d.status === 'unclear' ? '❓ 需要你确认' : '⚠️ 没有更新';
  var text = head + '：' + esc(item.text) + (d.message ? '\n' + esc(plain(d.message)) : '') + (url ? '\n' + esc(url) : '');
  if (d.status === 'unclear') {
    text += '\n（请回复新的 /update 说明清楚，这一条会删除）';
    props.setProperty('SITE_UPDATES', JSON.stringify(pendingUpdates_().filter(function (x) { return x.id !== d.id; })));
  }
  tg_('sendMessage', { chat_id: props.getProperty('TELEGRAM_CHAT_ID'), parse_mode: 'HTML', disable_web_page_preview: true, text: text });
  return json_({ ok: true });
}


/* ---------- Weekly site check (from .github/workflows/site-check.yml) ---------- */
function siteCheck_(d) {
  var props = PropertiesService.getScriptProperties();
  var last = +props.getProperty('LAST_SITE_CHECK') || 0;
  if (Date.now() - last < 20 * 3600 * 1000) return json_({ ok: false, error: 'already sent this week' });
  props.setProperty('LAST_SITE_CHECK', String(Date.now()));
  var okUrl = function (s) { return /^\/[\w\-\/.%]*$/.test(String(s)); };
  var lines = ['🩺 <b>每周网站检查</b>（' + (parseInt(d.pages, 10) || 0) + ' 页）'];
  var bt = parseInt(d.broken_total, 10) || 0;
  lines.push(bt ? '❌ 坏链接 ' + bt + ' 个：' : '✅ 没有坏链接');
  (d.broken || []).slice(0, 8).forEach(function (b) { if (okUrl(b.path)) lines.push('• ' + esc(b.path) + '（' + (parseInt(b.count, 10) || 1) + ' 页）'); });
  var sb = (d.sources || []).filter(function (s) { return /^https?:\/\//.test(s.url); });
  lines.push(sb.length ? '📰 新闻来源失效 ' + sb.length + ' 个：' : '✅ 新闻来源链接都正常');
  sb.slice(0, 5).forEach(function (s) { lines.push('• ' + esc(plain(s.note)).slice(0, 60)); });
  var g = d.gap_counts || {}, names = { price: '没有价格', developer: '没有发展商', completion: '没有完工日期', photo: '没有照片' };
  var gl = Object.keys(names).filter(function (k) { return +g[k] > 0; });
  if (gl.length) {
    lines.push('📋 项目资料待补：');
    gl.forEach(function (k) { lines.push('• ' + names[k] + ' ' + (+g[k]) + ' 个：' + esc(((d.gaps || {})[k] || []).slice(0, 6).map(plain).join('、'))); });
    lines.push('可以用 /update 补上，例如「/update Arden 起价 RM600,000」');
  } else lines.push('✅ 项目资料齐全');
  tg_('sendMessage', { chat_id: props.getProperty('TELEGRAM_CHAT_ID'), parse_mode: 'HTML', disable_web_page_preview: true, text: lines.join('\n') });
  return json_({ ok: true });
}


/* ---------- Weekly Google Analytics report to Telegram ----------
 * Setup once:
 * 1. In this Apps Script editor: Services (+) > Google Analytics Data API > Add.
 * 2. Script Properties: GA4_PROPERTY_ID = the number in GA Admin > Property details (not the G- ID).
 * 3. Run setupWeeklyReport once (it sends a report now and every Monday at 9am).
 */
function setupWeeklyReport() {
  ScriptApp.getProjectTriggers().forEach(function (tr) { if (tr.getHandlerFunction() === 'weeklyReport') ScriptApp.deleteTrigger(tr); });
  ScriptApp.newTrigger('weeklyReport').timeBased().onWeekDay(ScriptApp.WeekDay.MONDAY).atHour(9).inTimezone(TIME_ZONE).create();
  weeklyReport();
}

function gaRun_(id, body) {
  return AnalyticsData.Properties.runReport(body, 'properties/' + id);
}

function weeklyReport() {
  var props = PropertiesService.getScriptProperties(), id = props.getProperty('GA4_PROPERTY_ID');
  var chat = props.getProperty('TELEGRAM_CHAT_ID');
  if (!id) { tg_('sendMessage', { chat_id: chat, text: '还没设定 GA4_PROPERTY_ID，无法生成报告。' }); return; }
  var ranges = [{ startDate: '7daysAgo', endDate: 'yesterday', name: 'now' }, { startDate: '14daysAgo', endDate: '8daysAgo', name: 'before' }];
  var tot = gaRun_(id, { dateRanges: ranges, metrics: [{ name: 'activeUsers' }, { name: 'sessions' }, { name: 'screenPageViews' }] });
  var val = function (r, range, m) {
    var row = (r.rows || []).filter(function (x) { return !x.dimensionValues || x.dimensionValues.some(function (v) { return v.value === range; }); })[0];
    return row ? +row.metricValues[m].value : 0;
  };
  var ch = function (a, b) { if (!b) return ''; var p = Math.round((a - b) / b * 100); return '（' + (p >= 0 ? '+' : '') + p + '%）'; };
  var u1 = val(tot, 'now', 0), u0 = val(tot, 'before', 0), s1 = val(tot, 'now', 1), v1 = val(tot, 'now', 2), v0 = val(tot, 'before', 2);
  var ev = gaRun_(id, { dateRanges: [ranges[0]], dimensions: [{ name: 'eventName' }], metrics: [{ name: 'eventCount' }],
    dimensionFilter: { filter: { fieldName: 'eventName', inListFilter: { values: ['generate_lead', 'quiz_complete', 'page_not_found'] } } } });
  var evc = {}; (ev.rows || []).forEach(function (r) { evc[r.dimensionValues[0].value] = +r.metricValues[0].value; });
  var top = function (dim, n) {
    var r = gaRun_(id, { dateRanges: [ranges[0]], dimensions: [{ name: dim }], metrics: [{ name: 'screenPageViews' }], limit: n,
      orderBys: [{ metric: { metricName: 'screenPageViews' }, desc: true }] });
    return (r.rows || []).map(function (x) { return [x.dimensionValues[0].value, +x.metricValues[0].value]; });
  };
  var pages = top('pageTitle', 5), countries = top('country', 5), langs = top('contentGroup', 6);
  var L = ['📊 <b>keithnah.com 本周数据</b>（过去 7 天）',
    '👥 访客 ' + u1 + ch(u1, u0) + ' · 浏览 ' + v1 + ch(v1, v0) + ' · 访问 ' + s1,
    '💬 WhatsApp / 询问：' + (evc.generate_lead || 0) + ' · 找房问答完成：' + (evc.quiz_complete || 0) + ' · 404：' + (evc.page_not_found || 0),
    '', '🔝 最多人看的页面：'];
  pages.forEach(function (p, i) { L.push((i + 1) + '. ' + esc(p[0].replace(/\s*\|\s*Keith Nah.*$/, '')).slice(0, 60) + ' — ' + p[1]); });
  L.push('', '🌍 国家：' + countries.map(function (c) { return esc(c[0]) + ' ' + c[1]; }).join('、'));
  L.push('🈯 语言版本：' + langs.map(function (c) { return esc(c[0] === '(not set)' ? 'en' : c[0]) + ' ' + c[1]; }).join('、'));
  tg_('sendMessage', { chat_id: chat, parse_mode: 'HTML', disable_web_page_preview: true, text: L.join('\n') });
}
