/**
 * Keith Nah Real Estate — Project Enquiry collector.
 *
 * Bound to the "Keith Nah Real Estate — Project Enquiries" Google Sheet.
 * Deploy this as a Web App (see SETUP.md) and paste the resulting /exec
 * URL into ENQUIRY_SHEET_ENDPOINT near the top of the <script> block in
 * projects.html. Every enquiry form submission on the site will then be
 * appended here as a new row automatically — no manual copy/paste needed.
 *
 * Column order must match the sheet's header row exactly:
 * Timestamp | Project | Enquiry Type | Name | Phone | Email | Buying Purpose |
 * Budget | Min Bedrooms | Timeline | Preferred Contact Time | What Matters Most |
 * Consent | Updates Opt-in | Source Page
 */

function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    var p = (e && e.parameter) ? e.parameter : {};

    sheet.appendRow([
      new Date(),
      p.project || '',
      p.enquiryType || '',
      p.name || '',
      p.phone || '',
      p.email || '',
      p.purpose || '',
      p.budget || '',
      p.bedrooms || '',
      p.timeline || '',
      p.contactTime || '',
      p.preferences || '',
      p.consent || '',
      p.updatesOptIn || '',
      p.page || ''
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ result: 'success' }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ result: 'error', error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Lets you open the deployed /exec URL directly in a browser to confirm
// the deployment is live (it will just show a short status message).
function doGet(e) {
  return ContentService
    .createTextOutput('Keith Nah Real Estate enquiry endpoint is live.')
    .setMimeType(ContentService.MimeType.TEXT);
}
