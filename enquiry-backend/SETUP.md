# Project Enquiry Form — connect it to your Google Sheet

Every project page now has an enquiry form ("Need help with [Project]?") under the
WhatsApp button. When someone submits it, two things already happen with no setup:

1. WhatsApp opens with their details pre-filled, addressed to you.
2. They see a "Thank you" confirmation on the page.

This guide adds the **third thing**: every submission is also saved as a new row in
your Google Sheet automatically, so you always have a complete, compiled list —
open it anytime, or download it as an Excel file (`.xlsx`) whenever you like.

The sheet already exists:
**"Keith Nah Real Estate — Project Enquiries"** in your Google Drive.

This is a one-time setup, about 2 minutes. After this, it runs forever with nothing
further to do.

## Steps

1. Open the **"Keith Nah Real Estate — Project Enquiries"** sheet in Google Sheets.
2. Click **Extensions → Apps Script** in the menu bar.
3. Delete any placeholder code in the editor, then open `Code.gs` (in this same
   folder) and paste its entire contents in.
4. Click the **Save** icon (or Ctrl/Cmd + S).
5. Click **Deploy → New deployment**.
6. Click the gear icon ⚙️ next to "Select type" and choose **Web app**.
7. Fill in:
   - **Execute as:** Me (your Google account)
   - **Who has access:** Anyone
8. Click **Deploy**.
9. Google will ask you to **Authorize access** — this is expected since the script
   needs permission to write to your own sheet. Click through with your Google
   account (you may see an "unverified app" warning since this script is private
   to you — click **Advanced → Go to [project name] (unsafe)** to proceed; this
   is safe because it's your own script).
10. Copy the **Web app URL** shown (it ends in `/exec`).
11. Send that URL to Claude (or paste it directly into `projects.html`, replacing
    the empty `ENQUIRY_SHEET_ENDPOINT = ''` near the top of the main `<script>`
    block with `ENQUIRY_SHEET_ENDPOINT = 'https://script.google.com/.../exec'`).

That's it. From then on, every enquiry submitted anywhere on the site lands as a
new row in the sheet within a second or two.

## Notes

- If you ever need to re-paste or edit `Code.gs`, redeploy via **Deploy → Manage
  deployments → Edit (pencil icon) → New version → Deploy** — editing the script
  alone does not update a live deployment.
- The sheet's first row is the header; don't delete or reorder those columns, since
  the script writes into fixed column positions.
- You can filter, sort, or add a pivot table / chart directly in the sheet without
  affecting new submissions.
- To get an Excel file: in Google Sheets, **File → Download → Microsoft Excel
  (.xlsx)**.
