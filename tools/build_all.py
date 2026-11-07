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
STEPS = ['no_klcc.py', 'update_tags.py', 'update_areas.py', 'build_list_pages.py', 'build_area_pages.py',
         'build_project_pages.py', 'build_news_page.py', 'float_wa.py', 'build_ai_seo.py']
for s in STEPS:
    r = subprocess.run([sys.executable, os.path.join(HERE, s)], capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or [''])[-1]
    print('%-24s %s' % (s, last[:110]))
    if r.returncode:
        print(r.stderr)
        sys.exit(r.returncode)
