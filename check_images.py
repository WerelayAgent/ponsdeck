import os, re
html_path = r'C:\Tools\ponsdeck\index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

srcs = re.findall(r'src=[\"\']([^\"\']+)[\"\']', html)
hrefs = re.findall(r'href=[\"\']([^\"\']+)[\"\']', html)

missing = []
for p in set(srcs + hrefs):
    if p.startswith('http') or p.startswith('data:') or p == '#': continue
    
    local_p = p.split('?')[0] # remove query
    if local_p.startswith('/'):
        local_p = local_p[1:]
    
    full_path = os.path.join(r'C:\Tools\ponsdeck', local_p.replace('/', '\\'))
    if not os.path.exists(full_path):
        missing.append((p, full_path))

print(f'Missing files: {len(missing)}')
for m in missing[:10]:
    print(f"URL: {m[0]} -> Expected Path: {m[1]}")
