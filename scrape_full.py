import os
import re
import urllib.request
from urllib.parse import urljoin, unquote, urlparse, parse_qs
import shutil

base_url = 'https://trenches.cards'
output_dir = r'C:\Tools\ponsdeck'
os.makedirs(output_dir, exist_ok=True)

# List of pages to download
pages = [
    '/',
    '/play',
    '/cards',
    '/pvp',
    '/burn',
    '/profile',
    '/trenchpaper'
]

# Regex patterns for rebranding
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
    (re.compile(r'8CHMXANcVNkbWe9eLuyfNHDExpP4RgAFCCEVQ6q7pump'), 'live on pons')
]

# Extra targeted replacement for the copy block if needed
# We might need to replace the entire <span> or <div> that holds "COPY", but let's see if string replacement is enough.

def get_content(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as res:
            return res.read()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def download_asset(url, save_path):
    if os.path.exists(save_path): return # Skip if already downloaded
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    content = get_content(url)
    if content:
        with open(save_path, 'wb') as f:
            f.write(content)

# We will collect all unique asset URLs to download
asset_urls = set()

# Process each page
for page in pages:
    page_url = base_url + page
    print(f"Fetching {page_url}")
    html_bytes = get_content(page_url)
    if not html_bytes:
        continue
    
    html = html_bytes.decode('utf-8')
    
    # Extract asset URLs
    urls = re.findall(r'href=[\"\'](/?_next/.*?)[\"\']|src=[\"\'](/?_next/.*?)[\"\']|src=[\"\'](/.*?\.png|/.*?\.webp|/.*?\.jpg|/.*?\.svg)[\"\']', html)
    for u in urls:
        path = next((x for x in u if x), None)
        if path:
            asset_urls.add(path)
            
    # Apply rebranding
    for pattern, replacement in rebrand_patterns:
        html = pattern.sub(replacement, html)
        
    # Also replace image paths from /_next/image?url=... to direct paths
    def fix_image_path(match):
        full_src = match.group(0)
        inner_url = match.group(1)
        if '/_next/image?url=' in inner_url:
            parsed_url = urlparse(inner_url)
            query_params = parse_qs(parsed_url.query)
            if 'url' in query_params:
                real_img_path = query_params['url'][0]
                # We want to replace the whole /_next/image... with real_img_path
                return full_src.replace(inner_url, real_img_path)
        # If it has a version param ?v=...
        if '?' in inner_url and not inner_url.startswith('/_next/'):
            clean_url = inner_url.split('?')[0]
            return full_src.replace(inner_url, clean_url)
        return full_src

    html = re.sub(r'src=[\"\']([^\"\']+)[\"\']', fix_image_path, html)
    html = re.sub(r'href=[\"\']([^\"\']+)[\"\']', fix_image_path, html)
    
    # Save HTML
    # If page is '/', save as index.html
    # If page is '/play', save as play.html (and maybe play/index.html)
    if page == '/':
        save_path = os.path.join(output_dir, 'index.html')
    else:
        save_path = os.path.join(output_dir, page.strip('/') + '.html')
        # Also save in a folder for clean URLs
        folder_save_path = os.path.join(output_dir, page.strip('/'), 'index.html')
        os.makedirs(os.path.dirname(folder_save_path), exist_ok=True)
        with open(folder_save_path, 'w', encoding='utf-8') as f:
            f.write(html)
            
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(html)

print(f"Found {len(asset_urls)} assets to process.")

# Process assets
for path in asset_urls:
    if not path.startswith('/'):
        path = '/' + path
        
    # If it's a next/image, we need to extract the real URL and download it
    if path.startswith('/_next/image?url='):
        parsed = urlparse(path)
        qs = parse_qs(parsed.query)
        if 'url' in qs:
            real_path = qs['url'][0]
            # Download from base_url + real_path
            dl_url = base_url + real_path
            local_path = os.path.join(output_dir, unquote(real_path).lstrip('/').replace('/', '\\'))
            download_asset(dl_url, local_path)
            # The HTML already points to this real path due to fix_image_path
    else:
        # Normal asset
        dl_url = base_url + path
        local_path = os.path.join(output_dir, unquote(path.split('?')[0]).lstrip('/').replace('/', '\\'))
        download_asset(dl_url, local_path)
        
        # If it's a JS or CSS file, we need to apply rebranding to it too
        if local_path.endswith('.js') or local_path.endswith('.css'):
            if os.path.exists(local_path):
                try:
                    with open(local_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    for pattern, replacement in rebrand_patterns:
                        content = pattern.sub(replacement, content)
                        
                    if content != original_content:
                        with open(local_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                except Exception as e:
                    pass

print("Full scrape and rebrand complete.")
