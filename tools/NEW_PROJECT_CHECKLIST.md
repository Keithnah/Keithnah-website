# Adding a new project (checklist for future sessions)

When Keith adds a project:

1. Project data goes in `PROJECT_DETAILS` / `KN_TAGS` in `projects.html` (run `python3 tools/externalize.py in` first).
   Set its state and area (see `tools/update_areas.py`).
2. Classify the area into a zone: edit `ZONES` in `tools/build_proj_layout.py`
   (KL: centre / west / south / ne; Selangor: pj / kwasa / subang / ssel / klang; Penang: island / mainland).
   An area not listed shows under "Other areas". The View Projects filter, the menu "Search by State" and the
   project sections all read `ZONES`.
3. Run `python3 tools/build_all.py`.  Every project page is built in the new one-project layout (tools/build_landing.py); an optional hook line and curated points can be added in tools/i18n/landing.json "projects".
4. Keith's project file is **WEBSITE_PROJECT.xlsx** ("the website project file"). It is made from the site data:
   `python3 tools/externalize.py in && python3 tools/export_projects_xlsx.py <scratchpad>/export && python3 tools/externalize.py out`
   It has INDEX (with State / Zone / Area columns), BY STATE, one sheet per state and per project, plus
   project_images.zip and projects_by_state.json. Send Keith the new WEBSITE_PROJECT.xlsx after every project change.
   (It is NOT the Google Sheet "Keith - All Project Details"; that is Keith's private sales sheet.)
