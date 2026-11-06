/**
 * KNRE Leads: Google Apps Script web app.
 *
 * Receives leads from lead-tracker.js on the website and adds one row
 * per lead to the "Leads" tab of the KNRE Leads Google Sheet.
 *
 * Setup (once):
 * 1. Open the KNRE Leads sheet > Extensions > Apps Script.
 * 2. Replace everything in Code.gs with this file and click Save.
 * 3. Deploy > New deployment > type "Web app".
 *    Execute as: Me. Who has access: Anyone. Click Deploy and allow access.
 * 4. Copy the Web app URL (ends in /exec) into LEADS_ENDPOINT in lead-tracker.js.
 *
 * Other websites can use the same URL: send a different "source" name
 * and add that name to column A of the Summary tab.
 */

var SHEET_NAME = 'Leads';
var MAX_LEN = 2000;

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var d = {};
    try { d = JSON.parse((e && e.postData && e.postData.contents) || '{}'); } catch (err) { d = {}; }

    var type = clean(d.type);
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
    return ContentService.createTextOutput('ok');
  } finally {
    lock.releaseLock();
  }
}

function doGet() {
  return ContentService.createTextOutput('KNRE lead tracker is running.');
}

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
