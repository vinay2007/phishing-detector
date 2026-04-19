import urllib.parse, tldextract, re, requests, whois, os, pandas as pd, csv, time, sys, asyncio, html
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# FIX: Windows asyncio compatibility for Playwright/Subprocesses
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Try to import playwright, fallback if not installed
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

def normalize_url(url):
    """
    Standardizes a URL for comparison.
    Removes protocol, www, trailing slashes, HTML entities, and accidentally copied CSV labels.
    """
    if not isinstance(url, str): return ""
    try:
        # Handle HTML escaping (e.g., &amp; -> &)
        url = html.unescape(url).strip().lower()

        # FIX: Remove accidentally copied CSV labels or trailing backslashes
        # Matches ,0 or ,1 or / or \ at the end of the string
        url = re.sub(r'[,\\/ ]+[01]?$', '', url)

        # Remove protocol
        if "://" in url:
            url = url.split("://")[-1]
        # Remove www.
        if url.startswith("www."):
            url = url[4:]

        # Final trim of any remaining edge slashes
        url = url.strip('/')

        return url
    except:
        return str(url).strip().lower()

def load_list(filename, is_csv=False):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', filename)
    if not os.path.exists(path): return set()
    try:
        if is_csv:
            df = pd.read_csv(path, encoding='utf-8')
            return set(normalize_url(u) for u in df[df['label'] == 1]['url'].astype(str))
        else:
            with open(path, 'r', encoding='utf-8') as f:
                return set(normalize_url(line) for line in f if line.strip())
    except: return set()

WHITELIST = load_list('whitelist.txt')
BLACKLIST = load_list('phishing_dataset.csv', is_csv=True)

def update_whitelist(url):
    """Adds a URL to the local whitelist file to prevent future false positives."""
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'whitelist.txt')
    os.makedirs(os.path.dirname(path), exist_ok=True)

    norm_url = normalize_url(url)

    # Check if already in memory whitelist to avoid duplicates
    if norm_url in WHITELIST:
        return "already whitelisted"

    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(f"\n{url}")
        WHITELIST.add(norm_url)
        return "whitelisted"
    except Exception as e:
        return f"error: {str(e)}"

def get_live_browser_intelligence(url):
    """
    Tier 4: Live Dynamic Analysis.
    Launches a real headless browser to audit the website.
    """
    res = {
        'has_password': 0,
        'ext_forms': 0,
        'link_ratio': 0.0,
        'brand_spoofing': 0,
        'urgent_keywords': 0,
        'js_rendered': 0
    }

    if not PLAYWRIGHT_AVAILABLE:
        return res

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            page = context.new_page()

            page.goto(url, timeout=10000, wait_until="networkidle")
            res['js_rendered'] = 1

            page_text = page.inner_text("body").lower()
            title = page.title().lower()
            domain = tldextract.extract(url).domain

            if page.query_selector("input[type='password']"):
                res['has_password'] = 1

            top_brands = ['google', 'microsoft', 'paypal', 'amazon', 'apple', 'netflix', 'facebook', 'bank']
            for brand in top_brands:
                if brand in title and brand not in domain:
                    res['brand_spoofing'] = 1
                    break

            suspicious_phrases = ['verify your identity', 'account suspended', 'login to continue', 'unauthorized access', 'update payment']
            if any(phrase in page_text for phrase in suspicious_phrases):
                res['urgent_keywords'] = 1

            forms = page.query_selector_all("form")
            for form in forms:
                action = form.get_attribute("action") or ""
                if action.startswith("http") and domain not in action:
                    res['ext_forms'] = 1
                    break

            links = page.query_selector_all("a")
            if len(links) > 0:
                ext_count = 0
                for link in links:
                    href = link.get_attribute("href") or ""
                    if href.startswith("http") and domain not in href:
                        ext_count += 1
                res['link_ratio'] = ext_count / len(links)

            browser.close()
    except Exception as e:
        print(f"Tier 4 Error: {e}")
    return res

def get_ai_dna_risk(url):
    score = 0
    if len(url) > 75: score += 15
    if url.count('.') > 3: score += 10
    if any(w in url.lower() for w in ['login', 'verify', 'bank', 'secure', 'update', 'account']):
        score += 25
    if re.search(r"bit\.ly|goo\.gl|tinyurl", url):
        score += 20
    return score

def get_infra_intelligence(url):
    try:
        reg_domain = tldextract.extract(url).registered_domain
        w = whois.whois(reg_domain)
        creation = w.creation_date
        if isinstance(creation, list): creation = creation[0]
        return 1 if (datetime.now() - creation).days < 365 else 0
    except: return 0.5

def perform_ai_inference(url):
    """Hybrid AI Inference with Live Dynamic Tier."""
    infra = get_infra_intelligence(url)
    dna_risk = get_ai_dna_risk(url)
    behavior = get_live_browser_intelligence(url)

    risk = dna_risk + (infra * 20) + (behavior['has_password']*35) + (behavior['brand_spoofing']*45) + (behavior['urgent_keywords']*20)

    return {
        'total_risk': min(risk, 100.0),
        'evidence': behavior,
        'dna_score': dna_risk,
        'infra_score': infra * 100
    }

def update_ai_training_set(url, label=1):
    """
    Saves or updates user feedback in the local threat dataset.
    Ensures labels are updated if the URL already exists (normalized matching).
    """
    # Use absolute path for reliability
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'phishing_dataset.csv')

    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    try:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            df = pd.read_csv(path, encoding='utf-8', low_memory=False)
        else:
            df = pd.DataFrame(columns=['url', 'label'])

        # Sanitize data types
        df['url'] = df['url'].astype(str)
        df['label'] = pd.to_numeric(df['label'], errors='coerce').fillna(0).astype(int)

        target_norm = normalize_url(url)
        match_idx = -1

        # Robust normalized matching
        if not df.empty:
            for i, existing_url in enumerate(df['url']):
                if normalize_url(existing_url) == target_norm:
                    match_idx = i
                    break

        if match_idx != -1:
            # Update existing record
            df.at[match_idx, 'label'] = int(label)
            # Optionally update URL to the latest version used
            df.at[match_idx, 'url'] = url
            res_status = "updated"
        else:
            # Append new record
            new_row = pd.DataFrame({'url': [url], 'label': [int(label)]})
            df = pd.concat([df, new_row], ignore_index=True)
            res_status = "added"

        # Save with explicit encoding and quoting to prevent corruption
        df.to_csv(path, index=False, encoding='utf-8', quoting=csv.QUOTE_MINIMAL)

        # Sync memory BLACKLIST
        if int(label) == 1:
            BLACKLIST.add(target_norm)
        elif target_norm in BLACKLIST:
            BLACKLIST.remove(target_norm)

        return res_status
    except Exception as e:
        print(f"Dataset Update Error: {e}")
        return f"error: {str(e)}"

def extract_all_features(url, behavior_data=None, infra_score=0.5):
    """
    Sequences URL DNA and integrates behavioral markers into a single feature vector.
    """
    features = [
        len(url), url.count('.'), url.count('-'), url.count('/'),
        1 if "@" in url else 0,
        1 if any(w in url.lower() for w in ['login', 'verify', 'bank', 'secure', 'update', 'account']) else 0,
        1 if re.search(r"bit\.ly|goo\.gl|tinyurl", url) else 0,
        1 if any(c.isdigit() for c in url) else 0
    ]

    if behavior_data:
        features.extend([
            behavior_data.get('has_password', 0),
            behavior_data.get('ext_forms', 0),
            behavior_data.get('brand_spoofing', 0),
            behavior_data.get('urgent_keywords', 0),
            behavior_data.get('link_ratio', 0.0),
            infra_score
        ])
    else:
        # Defaults for training mode or when browser scan is skipped
        # Maintains 14 features for model compatibility
        features.extend([0, 0, 0, 0, 0.0, infra_score])

    return features
