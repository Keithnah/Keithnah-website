#!/usr/bin/env python3
"""Export every project on the Keith Nah site into WEBSITE_PROJECT.xlsx (+ images folder).
Run from the site folder after ANY project add / remove / edit:
    python3 tools/export_projects_xlsx.py [out_dir]
Reads projects.html (PROJECT_DETAILS, PS_META, cards) and compare.html (PROJECTS).
"""
import re, json, base64, os, sys, zipfile, shutil, datetime
from collections import Counter
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/outputs'
IMG_DIR = os.path.join(OUT, 'project_images')

def load_json_after(text, key, end='\n'):
    a = text.index(key) + len(key); e = text.index(end, a)
    return json.loads(text[a:e].rstrip(';'))

s = open(os.path.join(SITE, 'projects.html'), encoding='utf-8').read()
D = load_json_after(s, 'const PROJECT_DETAILS = ')
a = s.index('var PS_META=') + 12; e = s.index('];', a) + 1
META = json.loads(s[a:e])
c = open(os.path.join(SITE, 'compare.html'), encoding='utf-8').read()
CMP = load_json_after(c, 'const PROJECTS = ')
assert len(D) == len(META) == len(CMP), (len(D), len(META), len(CMP))

def slug(t): return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')

# cover photos from static cards
covers = {}
for m in re.finditer(r'<div class="proj-card"[^>]*data-idx="(\d+)"', s):
    i = int(m.group(1))
    p = s.find('proj-photo" src="', m.end())
    if p == -1: continue
    p += len('proj-photo" src="'); q = s.index('"', p)
    covers[i] = s[p:q]

def save_img(dataurl, folder, name):
    if not dataurl or ',' not in dataurl: return ''
    os.makedirs(folder, exist_ok=True)
    ext = 'png' if 'image/png' in dataurl[:30] else ('webp' if 'webp' in dataurl[:30] else 'jpg')
    fn = f'{name}.{ext}'
    open(os.path.join(folder, fn), 'wb').write(base64.b64decode(dataurl.split(',', 1)[1]))
    return fn

if os.path.isdir(IMG_DIR): shutil.rmtree(IMG_DIR)
os.makedirs(IMG_DIR)

AREA_ORDER = ['Bukit Bintang', 'KL City Centre', 'TRX & Merdeka Maybank', 'KL City', 'Bukit Jalil', 'Petaling Jaya', 'Penang', 'Johor', 'Melaka']
order = sorted(range(len(D)), key=lambda i: (AREA_ORDER.index(D[i]['tag']) if D[i]['tag'] in AREA_ORDER else 99, D[i]['name'].lower()))

# ---------- styles
F = 'Arial'
NAVY = '1D1B4F'; PURPLE = '5E5FCF'; LIGHT = 'EEF0FB'; GREY = 'F5F5F7'
f_title = Font(name=F, size=16, bold=True, color='FFFFFF')
f_hdr = Font(name=F, size=10, bold=True, color='FFFFFF')
f_sec = Font(name=F, size=11, bold=True, color='FFFFFF')
f_lab = Font(name=F, size=10, bold=True, color=NAVY)
f_val = Font(name=F, size=10)
f_link = Font(name=F, size=10, color='0563C1', underline='single')
fill_navy = PatternFill('solid', fgColor=NAVY); fill_pur = PatternFill('solid', fgColor=PURPLE)
fill_light = PatternFill('solid', fgColor=LIGHT); fill_grey = PatternFill('solid', fgColor=GREY)
thin = Side(style='thin', color='D6D8E8'); box = Border(left=thin, right=thin, top=thin, bottom=thin)
wrap = Alignment(wrap_text=True, vertical='top')

wb = openpyxl.Workbook()
wsI = wb.active; wsI.title = 'INDEX'

def sheet_name(n, name):
    base = re.sub(r'[\[\]\:\*\?/\\]', '', name)
    return f'{n:02d} {base}'[:31]

names = {}
for n, i in enumerate(order, 1): names[i] = sheet_name(n, D[i]['name'])

def pname(idx): return D[idx]['name'] if 0 <= idx < len(D) else str(idx)

# ---------- per-project sheets
EXTRA_KEYS = Counter()
for p in D: EXTRA_KEYS.update(p.get('details_extra', {}).keys())
for n, i in enumerate(order, 1):
    p = D[i]; cm = CMP[i]; m = META[i]
    ws = wb.create_sheet(names[i]); ws.sheet_view.showGridLines = False
    ws.column_dimensions['A'].width = 26
    for col in 'BCDEFG': ws.column_dimensions[col].width = 28
    ws.column_dimensions['H'].width = 30
    r = 1
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
    ws.cell(r, 1, p['name']).font = f_title
    for col in range(1, 9): ws.cell(r, col).fill = fill_navy
    ws.row_dimensions[r].height = 30; ws.cell(r, 1).alignment = Alignment(vertical='center')
    r += 1
    ws.cell(r, 1, '← Back to INDEX').hyperlink = "#'INDEX'!A1"; ws.cell(r, 1).font = f_link
    r += 2
    def section(title):
        global r
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
        ws.cell(r, 1, title).font = f_sec
        for col in range(1, 9): ws.cell(r, col).fill = fill_pur
        r += 1
    def kv(label, val):
        global r
        ws.cell(r, 1, label).font = f_lab; ws.cell(r, 1).fill = fill_light; ws.cell(r, 1).border = box
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=8)
        v = ws.cell(r, 2, val if val not in (None, '') else '-'); v.font = f_val; v.alignment = wrap
        for col in range(2, 9): ws.cell(r, col).border = box
        L = len(str(val or '')); ws.row_dimensions[r].height = max(16, 15 * (1 + L // 150))
        r += 1
    def lst(title, items):
        global r
        section(title)
        if not items: kv('-', '-')
        for k, t in enumerate(items, 1): kv(str(k), t)
        r += 1
    section('1. BASIC INFORMATION')
    kv('Project name', p['name']); kv('Area / section', p['tag']); kv('Location', p.get('loc'))
    kv('Property type', cm.get('type')); kv('Status', p.get('status'))
    kv('Starting price', p.get('price')); kv('Price (short, card)', cm.get('price'))
    kv('Tenure', p.get('tenure')); kv('Size', p.get('size')); kv('Bedrooms', p.get('rooms'))
    kv('Completion', p.get('completion')); kv('Completion year(s) (filter)', ', '.join(map(str, m.get('y', []))) or ('Completed' if m.get('c') else '-'))
    kv('Completed building (filter)', 'Yes' if m.get('c') else 'No'); kv('Developer (filter group)', m.get('d'))
    kv('Cover image file', ''); cover_row = r - 1
    wa = 'https://api.whatsapp.com/send/?phone=60102821568&text=' + re.sub(r'\s', '+', '(KNRE) Hi Keith, I would like to know more about "%s".' % p['name'])
    kv('WhatsApp enquiry text', '(KNRE) Hi Keith, I would like to know more about "%s".' % p['name'])
    r += 1
    section('2. OVERVIEW'); kv('Overview paragraph', p.get('overview')); r += 1
    lst('3. TOP 3 HIGHLIGHTS', p.get('points', []))
    lst('4. KEY SELLING POINTS', p.get('selling_points', []))
    lst('5. NEARBY AMENITIES / LANDMARKS', p.get('amenities', []))
    section('6. LOCATION'); kv('Location description', p.get('loc_text'))
    kv('Related / similar projects', ', '.join(pname(x) for x in p.get('nearby', []))); r += 1
    section('7. BUYER FIT')
    for bf in p.get('buyer_fit', []): kv(bf['title'], bf['desc'])
    if not p.get('buyer_fit'): kv('-', '-')
    r += 1
    section('8. FACT SHEET (details)')
    for k, v in p.get('details_extra', {}).items(): kv(k, v)
    if not p.get('details_extra'): kv('-', '-')
    if p.get('facilities'):
        r += 1; lst('FACILITIES', p['facilities'])
    r += 1
    section('9. UNIT TYPES / LAYOUTS')
    for col, h in enumerate(['Type', 'Size', 'Rooms', 'Tag', 'Image file', 'Description'], 1):
        x = ws.cell(r, col, h); x.font = f_hdr; x.fill = fill_navy; x.border = box
    ws.merge_cells(start_row=r, start_column=6, end_row=r, end_column=8); r += 1
    folder = os.path.join(IMG_DIR, slug(p['name']))
    cov = save_img(covers.get(i), folder, 'cover')
    ws.cell(cover_row, 2, (slug(p['name']) + '/' + cov) if cov else '-').font = f_val
    for lay in p.get('layouts', []):
        fn = save_img(lay.get('img'), folder, 'layout-' + slug(lay.get('type', 'type')))
        vals = [lay.get('type'), lay.get('size'), lay.get('rooms'), lay.get('tag'), (slug(p['name']) + '/' + fn) if fn else '-', lay.get('desc')]
        for col, v in enumerate(vals, 1):
            x = ws.cell(r, col, v); x.font = f_val; x.alignment = wrap; x.border = box
        ws.merge_cells(start_row=r, start_column=6, end_row=r, end_column=8)
        ws.row_dimensions[r].height = max(30, 15 * (1 + len(str(lay.get('desc') or '')) // 60)); r += 1
    if not p.get('layouts'): kv('-', 'No layouts recorded')
    ws.freeze_panes = 'A3'

# ---------- INDEX
wsI.sheet_view.showGridLines = False
wsI.merge_cells('A1:L1'); wsI['A1'] = 'KEITH NAH REAL ESTATE — WEBSITE PROJECT DATABASE'
wsI['A1'].font = f_title
for col in range(1, 13): wsI.cell(1, col).fill = fill_navy
wsI.row_dimensions[1].height = 32
wsI['A2'] = f'{len(D)} projects · exported {datetime.date.today().isoformat()} · one sheet per project (click the project name). Update by running tools/export_projects_xlsx.py after every project change.'
wsI['A2'].font = Font(name=F, size=9, italic=True, color='666666')
heads = ['#', 'Project', 'Area / section', 'Developer', 'Status', 'Tenure', 'Starting price', 'Size', 'Bedrooms', 'Completion', 'Location', 'Type']
for col, h in enumerate(heads, 1):
    x = wsI.cell(4, col, h); x.font = f_hdr; x.fill = fill_pur; x.border = box; x.alignment = Alignment(vertical='center', wrap_text=True)
for n, i in enumerate(order, 1):
    p = D[i]; cm = CMP[i]; row = 4 + n
    dev = p.get('details_extra', {}).get('Developer') or META[i].get('d') or '-'
    vals = [n, p['name'], p['tag'], dev, p.get('status'), p.get('tenure'), p.get('price'), p.get('size'), p.get('rooms'), p.get('completion'), p.get('loc'), cm.get('type')]
    for col, v in enumerate(vals, 1):
        x = wsI.cell(row, col, v); x.font = f_val; x.border = box; x.alignment = Alignment(vertical='top', wrap_text=True)
        if n % 2 == 0: x.fill = fill_grey
    wsI.cell(row, 2).hyperlink = f"#'{names[i]}'!A1"; wsI.cell(row, 2).font = f_link
for col, w in zip('ABCDEFGHIJKL', [5, 34, 20, 24, 18, 18, 34, 20, 18, 24, 34, 18]): wsI.column_dimensions[col].width = w
wsI.freeze_panes = 'C5'; wsI.auto_filter.ref = f'A4:L{4 + len(D)}'

# ---------- MASTER (flat, all fields) for easy import
wsM = wb.create_sheet('MASTER TABLE', 1)
base_cols = ['name', 'tag', 'status', 'price', 'tenure', 'size', 'rooms', 'completion', 'loc', 'overview', 'loc_text']
extra_cols = [k for k, _ in EXTRA_KEYS.most_common()]
head = ['Project', 'Area', 'Status', 'Starting price', 'Tenure', 'Size', 'Bedrooms', 'Completion', 'Location', 'Overview', 'Location text', 'Top 3 highlights', 'Selling points', 'Amenities', 'Buyer fit', 'Related projects', 'Layout types', 'Property type', 'Completion years', 'Completed?'] + extra_cols
for col, h in enumerate(head, 1):
    x = wsM.cell(1, col, h); x.font = f_hdr; x.fill = fill_navy; x.alignment = Alignment(wrap_text=True, vertical='center'); x.border = box
for n, i in enumerate(order, 1):
    p = D[i]; row = 1 + n
    vals = [p[k] if k not in ('name',) else p['name'] for k in base_cols]
    vals += [' | '.join(p.get('points', [])), ' | '.join(p.get('selling_points', [])), ', '.join(p.get('amenities', [])),
             ' | '.join(f"{b['title']}: {b['desc']}" for b in p.get('buyer_fit', [])), ', '.join(pname(x) for x in p.get('nearby', [])),
             ', '.join(l.get('type', '') for l in p.get('layouts', [])), CMP[i].get('type'), ', '.join(map(str, META[i].get('y', []))), 'Yes' if META[i].get('c') else 'No']
    vals += [p.get('details_extra', {}).get(k, '') for k in extra_cols]
    for col, v in enumerate(vals, 1):
        x = wsM.cell(row, col, v); x.font = f_val; x.alignment = Alignment(vertical='top', wrap_text=True); x.border = box
for col in range(1, len(head) + 1):
    wsM.column_dimensions[get_column_letter(col)].width = 60 if col in (10, 11, 12, 13, 15) else 24
wsM.column_dimensions['A'].width = 32
wsM.freeze_panes = 'B2'; wsM.auto_filter.ref = f'A1:{get_column_letter(len(head))}{1 + len(D)}'

# ---------- LAYOUTS (all unit types)
wsL = wb.create_sheet('ALL LAYOUTS', 2)
for col, h in enumerate(['Project', 'Area', 'Type', 'Size', 'Rooms', 'Tag', 'Description', 'Image file'], 1):
    x = wsL.cell(1, col, h); x.font = f_hdr; x.fill = fill_navy; x.border = box
row = 2
for i in order:
    p = D[i]
    for lay in p.get('layouts', []):
        fn = 'layout-' + slug(lay.get('type', 'type'))
        ext = next((f for f in os.listdir(os.path.join(IMG_DIR, slug(p['name']))) if f.startswith(fn + '.')), '') if os.path.isdir(os.path.join(IMG_DIR, slug(p['name']))) else ''
        for col, v in enumerate([p['name'], p['tag'], lay.get('type'), lay.get('size'), lay.get('rooms'), lay.get('tag'), lay.get('desc'), (slug(p['name']) + '/' + ext) if ext else '-'], 1):
            x = wsL.cell(row, col, v); x.font = f_val; x.alignment = Alignment(wrap_text=True, vertical='top'); x.border = box
        row += 1
for col, w in zip('ABCDEFGH', [32, 20, 18, 22, 28, 14, 70, 34]): wsL.column_dimensions[col].width = w
wsL.freeze_panes = 'A2'; wsL.auto_filter.ref = f'A1:H{row - 1}'

# ---------- README
wsR = wb.create_sheet('README', 3)
lines = ['HOW THIS FILE WORKS',
 '• INDEX — one row per project; click a project name to jump to its own sheet.',
 '• MASTER TABLE — every project in one flat table (best for importing into a new website / database).',
 '• ALL LAYOUTS — every unit type of every project.',
 '• One sheet per project — sections: Basic info, Overview, Top 3 highlights, Selling points, Amenities, Location, Buyer fit, Fact sheet, Unit types.',
 '• Images are in the project_images folder (one sub-folder per project: cover + layout images). The "Image file" cells give the file path.',
 '• All prices are GROSS prices as published on the site. Rebates, nett prices, commission and other internal developer information are NOT recorded here.',
 '• Source of truth = the website files (projects.html / compare.html). This workbook is regenerated from them after every project add / remove / edit.']
for k, t in enumerate(lines, 1):
    wsR.cell(k, 1, t).font = Font(name=F, size=12 if k == 1 else 10, bold=(k == 1)); wsR.cell(k, 1).alignment = Alignment(wrap_text=True, vertical='top')
wsR.column_dimensions['A'].width = 140

os.makedirs(OUT, exist_ok=True)
xl = os.path.join(OUT, 'WEBSITE_PROJECT.xlsx'); wb.save(xl)
zp = os.path.join(OUT, 'project_images.zip')
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(IMG_DIR):
        for f in files:
            full = os.path.join(root, f); z.write(full, os.path.relpath(full, OUT))
print('projects', len(D), 'sheets', len(wb.sheetnames), 'images', sum(len(f) for _, _, f in os.walk(IMG_DIR)))
