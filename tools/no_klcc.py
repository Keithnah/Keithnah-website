"""Site rule: never use the word "KLCC" (developer marketing guideline). Use "KL City Centre".

clean(text) rewrites any text; running this file rewrites the website's source
files in place. The build scripts call clean() on new project data too.
    python3 tools/no_klcc.py
"""
import glob
import re

RULES = [(r'Suria KLCC', 'Suria KL City Centre'), (r'KLCC Park', 'KL City Centre Park'),
         (r'KLCC LRT', 'KL City Centre LRT'), (r'\bKLCC\b', 'KL City Centre'),
         (r'(?<![A-Za-z])klcc(?![A-Za-z])', 'kl city centre')]


def clean(text):
    for a, b in RULES:
        text = re.sub(a, b, text)
    text = re.sub(r'kl city centre(\s+kl city centre)+', 'kl city centre', text)  # search keywords
    return text


FILES = ['projects.html', 'compare.html', 'index.html', 'blog.html', 'about-keith.html', 'mm2h.html', 'calculator.html'] + \
    glob.glob('i18n-projects-*.js') + glob.glob('tools/new_projects/*.json') + ['tools/tag_groups.json']

if __name__ == '__main__':
    n = 0
    for f in FILES:
        t = open(f, encoding='utf-8').read()
        c = clean(t)
        if c != t:
            open(f, 'w', encoding='utf-8').write(c)
            n += 1
    print('cleaned', n, 'files')
