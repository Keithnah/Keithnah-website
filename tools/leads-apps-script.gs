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
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  var d = {}, type = '';
  try {
    try { d = JSON.parse((e && e.postData && e.postData.contents) || '{}'); } catch (err) { d = {}; }

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

function doGet() {
  return ContentService.createTextOutput('KNRE lead tracker is running.');
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
