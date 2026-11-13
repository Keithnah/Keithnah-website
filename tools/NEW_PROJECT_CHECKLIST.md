# Adding a new project (checklist for future sessions)

When Keith adds a project:

1. Project data goes in `PROJECT_DETAILS` / `KN_TAGS` in `projects.html` (run `python3 tools/externalize.py in` first).
   Set its state and area (see `tools/update_areas.py`).
2. Classify the area into a zone: edit `ZONES` in `tools/build_proj_layout.py`
   (KL: centre / west / south / ne; Selangor: pj / kwasa / subang / ssel / klang; Penang: island / mainland).
   An area not listed shows under "Other areas". The View Projects filter, the menu "Search by State" and the
   project sections all read `ZONES`.
3. Keith's own project sheet "Keith - All Project Details" (Google Sheets id
   `1TbA2zatqHux0jIoINR29Rt7mbrKccs2SCrsrnJlHlG0`) also gets a row, in the right tab:
   KL, PJ & Others, PENANG, JOHOR, LANDED (EXSIM KL / EXSIM OTHER for Exsim projects).
   Columns: MAIN PROJECTS, LAND SIZE, TENURE, COMPLETION, TITLE, UNIT, FLOOR, LIFT, M.FEE, CARPARK, SIZE, LAYOUT,
   PRICE (SPA), NETT.P, PSF, BOOKING FEE, PACKAGE, LEGAL FEE, COMM, REMARK.
   That sheet is private to Keith; nett prices, packages and commission never go on the website.
4. Run `python3 tools/build_all.py`.
