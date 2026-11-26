# Notes for Claude (keithnah.com)

- When Keith says "my project file", "website project file", "project Excel" or "WEBSITE PROJECT FILE", he means
  **WEBSITE_PROJECT.xlsx**, made by `tools/export_projects_xlsx.py` from the site's project data.
  Not the Google Sheet "Keith - All Project Details".
- After adding or changing any project: classify it (state, zone, area), rebuild the site, regenerate
  WEBSITE_PROJECT.xlsx and send it to Keith. Steps: `tools/NEW_PROJECT_CHECKLIST.md`.
- Reply to Keith in Chinese. "给我看先" = preview only; "上线" = publish.
- "Airbnb" may appear in news/articles, but never in project descriptions (never say a project can do Airbnb).
  Projects built for short stays (e.g. MABA Suitez, Hanaz Suites) may be described as "short-term rental".

## Standing rules (from earlier conversations)
- Never write "KLCC" (use "KL City Centre"), "Guaranteed Rental Return" or "GRR".
- Never show rebates, nett prices, packages, commission, sales galleries or licence numbers.
- Restricted projects get NO developer info: Aricia, Enlace Suites II, Ayanna, Est8, Lunar, Tangen, Aurum, Anya, Avantro, Luminar.
- Six languages: en, zh-CN, zh-TW, ms, ja, ko (zh-TW from zh-CN with opencc s2tw). Project and place names stay in English.
- Selangor foreign-buyer minimum: write RM2 million (Keith: "写 RM200 万").
- Never invent facts. Market notes: neutral, no legal topics, no yields. Never force-push. No secrets in code or chat.
- Clouthaus, Golden Crown and Zenia drafts stay unpublished.
- Always check the phone version (tools/check_mobile.js runs in the build) before publishing.
- Without "给我看先" or "上线" in Keith's message: do it and publish.

## How the site is built and published
- Hostinger auto-deploys the `main` branch. Work on the session's claude/ branch, then PR to main and merge.
- Release: `git fetch origin main && git merge origin/main` → `python3 tools/build_all.py` (20–25 min, run in the
  background, log to the scratchpad) → `rm -rf tools/__pycache__` → commit, push (wrap in `timeout`, retry) →
  PR (owner keithnah) → merge with expectedHeadSha → curl the live page until the change shows.
- Many pages are generated; edit the generator in tools/, not the output. Key ones: site_header.py (menu, currency),
  build_landing.py / build_project_pages.py (project pages), build_menu.py, kn_hero.py + build_heroes.py (page tops),
  build_faq.py + faq_topics.json, build_maps.py, news_hub_modules.py + build_news_split.py (blog.html is restored from
  tools/news_full.html each build), build_market_notes.py + market_notes.json, add_silky.py (silky_src.js → /silky.js,
  fx_src.js → /fx.js). Language copies are rendered by build_lang_pages.js at the end of the build.
- Hand-maintained pages: index.html (+ assets/data/index-2.js), projects.html, compare.html, calculator.html, mm2h.html,
  about-keith.html. Project data: PROJECT_DETAILS / KN_TAGS (run tools/externalize.py in before editing).
- Previews: write to .preview-out/ (git-excluded), serve with `python3 -m http.server 8765`, screenshot with Playwright.
- Currency: fixed fallback rates live in site_header.py, the hand-maintained pages and assets/data/*.js;
  /fx.js loads daily rates in the browser (open.er-api.com, backup jsDelivr currency-api).

## Daily routines (scheduled tasks)
- 8:52 MYT "Market notes: 5 topics to Telegram": research news, POST a Topic Proposal to the Apps Script
  endpoint (URL in lead-tracker.js).
- 9:52 MYT "Market notes + Telegram site updates + new YouTube videos": Telegram /update requests, write the market
  notes Keith picked (tools/market_notes.json, 6 languages, sources), tools/sync_youtube_videos.py, publish.
  The full instructions are stored in each scheduled task's prompt.
