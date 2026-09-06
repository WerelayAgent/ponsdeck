import os
import re

html_path = r'C:\Tools\ponsdeck\index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

hrefs = set(re.findall(r'href=[\"\'](/[^\"\']+)[\"\']', html))
print('HREFs in index.html:')
for h in sorted(list(hrefs)):
    print(h)
    
srcs = set(re.findall(r'src=[\"\'](/[^\"\']+)[\"\']', html))
print('\nSRCs in index.html:')
for s in sorted(list(srcs)):
    print(s)
