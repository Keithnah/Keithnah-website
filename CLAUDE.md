# keithnah.com — notes for Claude

Static site (plain HTML/CSS/JS, no build step, no framework). Keith Nah is a Kuala Lumpur
property consultant. The owner writes requests in Chinese or English; reply in the language used.

## Token rules (important)
- Pages embed images as base64 `data:` URIs: projects.html ~30MB, index.html ~8MB,
  compare.html ~3MB. 93–98% of each file is image data.
- NEVER Read/cat a whole page. Never print lines containing `data:image`.
- Search with Grep/grep and keep output short (`cut -c1-200`, `head`). To view code, strip images:
  `sed -E 's/data:[a-z/+]+;base64,[A-Za-z0-9+\/=]+/DATAURI/g' FILE | sed -n 'A,Bp' | cut -c1-300`
- Edit with small exact-string Edit calls or a short Python script; don't rewrite whole files.
- i18n-projects-*.js are single-line ~600KB–1MB files: never Read them; edit via Python (json).

## Pages
| File | What it is |
|---|---|
| index.html | Home: hero, featured projects carousel (`#miniTrack`), locations, UI translations (`const I18N`) |
| projects.html | All projects: cards in `#projGrid` (`.proj-card`, `data-idx`, `data-tag`=area), detail modal, search by name/area/year/developer |
| compare.html | Compare up to 3: cards `.cmp-card` + `const PROJECTS = [...]` |
| blog.html | Articles in `const ARTICLES = {...}`; opened via `blog.html?article=ID` |
| calculator.html | Mortgage, stamp duty (MOT), DSR, rental yield/Airbnb, RPGT, MRTA/MLTA, area & currency panels (`#panel-*`) |
| mm2h.html | MM2H guide + Silver/Gold/Platinum tiers |
| about-keith.html | Bio, stats, YouTube, contact |
| sitemap.xml, robots.txt | SEO; update `<lastmod>` and add any new page to sitemap |

## Project data (most common edits)
A project appears in several places — keep them in sync, same order/index:
1. projects.html: `.proj-card` in `#projGrid` + entry in `const PROJECT_DETAILS = [...]` (detail modal data).
2. compare.html: `.cmp-card` (`data-idx`, `data-search`) + entry in `const PROJECTS = [...]`.
3. index.html: its own `const PROJECT_DETAILS` (featured carousel) and article maps
   (`PROJECT_ARTICLE_OVERRIDES`, e.g. `'Accent Residence': ['a23',...]`) — only if featured.
4. i18n-projects-<lang>.js: `window.KN_TR["<lang>"] = { "English text": "translation" }` for
   zh-CN, zh-TW, ms, ta, ja, ko, ar. Add/remove keys for new/removed project text.
After adding/removing a project: reindex `data-idx`/`openDetailModal(n)`/`toggleSelect(n)` so they
match array positions, and update area filter counts and any project counts.
Prices are stored in MYR; currency conversion uses `data-price-myr` and `EXCHANGE_RATES`.

## Shared code duplicated on every page
Header nav, language menu (`LANG_NAMES`, `setLanguage`, localStorage `kn_lang`), currency menu
(`EXCHANGE_RATES`, `CURRENCY_SYMBOL`, `setCurrency`, localStorage `kn_currency`), mobile slide-in
menu, WhatsApp links (`60102821568`, prefilled text starts with `(Web)`). A change to any of these
must be applied to all 7 HTML pages.

## SEO
Each page has title, meta description (≤160 chars), canonical `https://keithnah.com/<page>`,
og:* tags. Keep them in sync when renaming pages or titles.

## Checks before commit
- Data arrays must still parse and counts must match (currently 66 / 66 / 6 featured):
  ```
  python3 -c "import re,json
  for f,v in [('projects.html','PROJECT_DETAILS'),('compare.html','PROJECTS'),('index.html','PROJECT_DETAILS')]:
      s=open(f,encoding='utf-8').read(); m=re.search(r'const '+v+r' = (\[.*?\]);\n',s,re.S); print(f,len(json.loads(m.group(1))))"
  ```
- For visual changes, screenshot with Playwright (Chromium is preinstalled) at mobile + desktop width.
- Commit messages: short, describe what changed (e.g. "Add X project; reindex and update counts").
