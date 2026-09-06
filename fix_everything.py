import os
import re
import urllib.request
from urllib.parse import urljoin, unquote

base_url = 'https://trenches.cards'
directory = r'C:\Tools\ponsdeck'

# 1. Download missing pages
missing_pages = ['/deck', '/mint', '/tournament']
for p in missing_pages:
    print(f"Downloading {p}")
    url = base_url + p
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as res:
            html = res.read().decode('utf-8')
            
            # Save it
            save_path = os.path.join(directory, p.strip('/') + '.html')
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(html)
                
            folder_save_path = os.path.join(directory, p.strip('/'), 'index.html')
            os.makedirs(os.path.dirname(folder_save_path), exist_ok=True)
            with open(folder_save_path, 'w', encoding='utf-8') as f:
                f.write(html)
    except Exception as e:
        print(f"Failed to download {p}: {e}")

# 2. Rebrand everything again to be sure (including the new pages)
rebrand_patterns = [
    (re.compile(r'Trenches Card Game', re.IGNORECASE), 'Pons Deck'),
    (re.compile(r'TRENCHES CARD GAME'), 'PONS DECK'),
    (re.compile(r'Trenches', re.IGNORECASE), 'Pons Deck'),
    (re.compile(r'TRENCHES'), 'PONS DECK'),
    (re.compile(r'\$TCG'), '$PDECK'),
    (re.compile(r'Solana', re.IGNORECASE), 'Robinhood Chain'),
    (re.compile(r'SOLANA'), 'ROBINHOOD CHAIN'),
    (re.compile(r'trenches\.cards', re.IGNORECASE), 'ponsdeck.com'),
    (re.compile(r'pump\.fun', re.IGNORECASE), 'ponsfamily.com'),
    (re.compile(r'PUMP\.FUN', re.IGNORECASE), 'PONSFAMILY.COM'),
    (re.compile(r'live on pons</span><span[^>]*>COPY</span>', re.IGNORECASE), 'live on pons</span>'),
    (re.compile(r'8CHMXANcVNkbWe9eLuyfNHDExpP4RgAFCCEVQ6q7pump</span><span[^>]*>COPY</span>'), 'live on pons</span>'),
    (re.compile(r'8CHMXANcVNkbWe9eLuyfNHDExpP4RgAFCCEVQ6q7pump'), 'live on pons')
]

for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.html') or file.endswith('.js') or file.endswith('.css'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Also fix image paths just in case they were missed
                def fix_image_path(match):
                    full_src = match.group(0)
                    inner_url = match.group(1)
                    if '?' in inner_url and not inner_url.startswith('/_next/'):
                        clean_url = inner_url.split('?')[0]
                        return full_src.replace(inner_url, clean_url)
                    return full_src
                
                content = re.sub(r'src=[\"\']([^\"\']+)[\"\']', fix_image_path, content)
                content = re.sub(r'href=[\"\']([^\"\']+)[\"\']', fix_image_path, content)

                original_content = content
                for pattern, replacement in rebrand_patterns:
                    content = pattern.sub(replacement, content)
                    
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
            except Exception as e:
                pass

# 3. Find and download any missing assets (images, fonts, etc)
all_assets = set()
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.html') or file.endswith('.css'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                srcs = re.findall(r'src=[\"\'](/[^\"\']+)[\"\']', content)
                hrefs = re.findall(r'href=[\"\'](/[^\"\']+)[\"\']', content)
                for s in srcs + hrefs:
                    if s.startswith('http') or s.startswith('data:') or s == '#': continue
                    all_assets.add(s.split('?')[0])
            except:
                pass

for asset in all_assets:
    local_path = os.path.join(directory, unquote(asset).lstrip('/').replace('/', '\\'))
    if not os.path.exists(local_path):
        print(f"Missing asset: {asset} -> downloading")
        dl_url = base_url + asset
        try:
            req = urllib.request.Request(dl_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as res:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, 'wb') as f:
                    f.write(res.read())
        except Exception as e:
            print(f"Failed to download {dl_url}: {e}")

print("Fix complete.")
