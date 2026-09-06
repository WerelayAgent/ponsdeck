import re

html_path = 'C:\\Tools\\ponsdeck\\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace src="/path/to/image.png?v=123" with src="/path/to/image.png"
def clean_src(match):
    full_src = match.group(0)
    inner_url = match.group(1)
    # Remove query string
    clean_url = inner_url.split('?')[0]
    return full_src.replace(inner_url, clean_url)

html = re.sub(r'src=[\"\']([^\"\']+)[\"\']', clean_src, html)
html = re.sub(r'href=[\"\']([^\"\']+)[\"\']', clean_src, html)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
    
print("Fixed image and href paths.")
