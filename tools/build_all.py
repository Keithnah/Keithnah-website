"""Rebuild everything generated from the project data, in the right order.

Run after adding or editing projects (tools/add_projects.py, set_project_photo.py):
    python3 tools/build_all.py
New projects automatically join the right area guide and every matching
best-of list, and the project pages show the lists they appear in.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ['no_klcc.py', 'update_tags.py', 'update_areas.py', 'merge_project_translations.py', 'build_list_pages.py', 'build_area_pages.py', 'build_proj_layout.py', 'build_compare.py',
         'build_project_pages.py', 'build_landing.py', 'build_hubs.py', 'build_quiz.py', 'build_mm2h.py', 'build_news_page.py', 'build_market_notes.py', 'build_data.py', 'build_guides.py', 'build_resources.py', 'build_foreign.py', 'build_about_stats.py', 'build_menu.py', 'float_wa.py', 'build_404.py', 'build_footer.py', 'build_saved.py', 'seo_meta.py', 'analytics.py', 'build_ai_seo.py', 'build_image_sitemap.py', 'build_og.py']


def stamp_translations():
    """Add a version to the translation file URLs so browsers fetch new translations straight away."""
    import glob, hashlib, re
    root = os.path.dirname(HERE)
    h = hashlib.sha1()
    for p in sorted(glob.glob(os.path.join(root, 'i18n-projects-*.js'))):
        h.update(open(p, 'rb').read())
    v = h.hexdigest()[:10]
    for name in ('projects.html', 'compare.html', 'index.html'):
        p = os.path.join(root, name)
        t = open(p, encoding='utf-8').read()
        t2 = re.sub(r"'i18n-projects-' \+ l \+ '\.js(?:\?v=\w+)?'", "'i18n-projects-' + l + '.js?v=%s'" % v, t)
        if t2 != t:
            open(p, 'w', encoding='utf-8').write(t2)
    print('%-24s translation files version %s' % ('stamp', v))


# The big data blocks live in assets/data/ between builds; the generators need them inline.
subprocess.run([sys.executable, os.path.join(HERE, 'externalize.py'), 'in'], check=True)
for s in STEPS:
    r = subprocess.run([sys.executable, os.path.join(HERE, s)], capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or [''])[-1]
    print('%-24s %s' % (s, last[:110]))
    if r.returncode:
        print(r.stderr)
        sys.exit(r.returncode)
stamp_translations()
r = subprocess.run([sys.executable, os.path.join(HERE, 'externalize.py'), 'out'], capture_output=True, text=True)
print('%-24s %s' % ('externalize.py', r.stdout.strip()))
if r.returncode:
    print(r.stderr)
    sys.exit(r.returncode)

# Last: the crawlable copies in every language (/zh/, /zh-tw/, /ms/, /ja/, /ko/), from the finished English pages.
r = subprocess.run(['node', os.path.join(HERE, 'build_lang_pages.js')], capture_output=True, text=True)
print('%-24s %s' % ('build_lang_pages.js', (r.stdout.strip().splitlines() or [''])[-1][:110]))
if r.returncode:
    print(r.stderr[-3000:])
    sys.exit(r.returncode)
