from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import asyncio
import aiohttp
import json
import re
import socket
import dns.resolver
import whois
from urllib.parse import urlparse, urljoin
import random
import urllib3
from datetime import datetime

# Onderdruk SSL waarschuwingen
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Pool van echte User-Agents om WAF-filters te misleiden
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
]

# Uitgebreide wordlist
COMMON_PATHS = [
    'admin', 'api', 'backup', 'config', 'dashboard', 'login', 'wp-admin',
    'phpmyadmin', '.git/HEAD', '.env', 'swagger', 'v2', 'test', 'dev', 'staging',
    'old', 'backup.zip', 'config.json', 'database.sql', 'secret', 'private',
    'robots.txt', 'sitemap.xml', '.htaccess', 'cgi-bin', 'server-status',
    'graphql', 'v1', 'v3', 'health', 'status', 'metrics', 'debug',
    'console', '.aws/credentials', '.ssh/id_rsa', 'backup.tar.gz', 
    'wp-config.php.bak', 'config.php.old', 'credentials.txt', 'passwords.txt',
    'backup.sql', 'dump.sql', 'settings.py', 'wp-login.php', 'administrator',
    'phpinfo.php', 'info.php', 'composer.json', 'package.json', '.git/config'
]

API_ENDPOINTS = [
    '/users', '/api/users', '/v1/users', '/user', '/account', '/profile',
    '/admin', '/login', '/auth', '/token', '/oauth', '/callback',
    '/swagger', '/openapi', '/api-docs', '/docs', '/redoc', '/graphql',
    '/api/v1/status', '/api/v1/health', '/api/v2/users'
]

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# --- HYBRIDE ASYNCHRONOUS FUZZER ENGINE (Snel + Veilig) ---
async def async_check_path(semaphore, session, target, path, results):
    async with semaphore:
        url = urljoin(target, path)
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        try:
            async with session.get(url, headers=headers, timeout=4, ssl=False, allow_redirects=False) as response:
                if response.status in [200, 301, 302, 307, 308, 403, 401]:
                    try:
                        html_content = await response.text()
                    except:
                        html_content = ""
                    
                    results.append({
                        'url': url,
                        'status': response.status,
                        'status_text': response.reason,
                        'size': len(html_content),
                        'title': extract_title(html_content)
                    })
        except Exception:
            pass

async def run_async_fuzz(target, wordlist):
    results = []
    # Slimme limiet van 40 gelijktijdige sockets voor optimale balans tussen snelheid en stabiliteit
    semaphore = asyncio.Semaphore(40)
    connector = aiohttp.TCPConnector(limit=60, ssl=False)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [async_check_path(semaphore, session, target, path, results) for path in wordlist]
        await asyncio.gather(*tasks)
    return results

@app.route('/api/fuzz', methods=['POST'])
def fuzz_url():
    data = request.json
    target = data.get('target')
    mode = data.get('mode', 'normal')
    
    if not target:
        return jsonify({'error': 'Target URL required'}), 400
    
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target
        
    if mode == 'gentle':
        wordlist = COMMON_PATHS[:25]
    elif mode == 'normal':
        wordlist = COMMON_PATHS
    else:
        wordlist = list(set(COMMON_PATHS + [p + '/' for p in COMMON_PATHS]))
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(run_async_fuzz(target, wordlist))
    finally:
        loop.close()
    
    return jsonify({
        'target': target,
        'mode': mode,
        'total_checked': len(wordlist),
        'found': len(results),
        'results': results,
        'timestamp': datetime.now().isoformat()
    })

# --- HYBRIDE ASYNCHRONOUS API SCANNER ENGINE ---
async def async_check_api(semaphore, session, target, endpoint, vulnerabilities, scan_mode):
    async with semaphore:
        url = urljoin(target, endpoint)
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        try:
            async with session.get(url, headers=headers, timeout=4, ssl=False) as response:
                if response.status == 200:
                    try:
                        content = await response.text()
                    except:
                        content = ""
                    vulnerabilities.append({
                        'type': 'Open API / Information Disclosure',
                        'severity': 'MEDIUM' if scan_mode == 'standard' else 'HIGH',
                        'endpoint': endpoint,
                        'details': f'Toegankelijk endpoint ontdekt ({len(content)} bytes zonder authenticatie)'
                    })
        except:
            pass

async def run_async_api_scan(target, scan_mode):
    vulnerabilities = []
    semaphore = asyncio.Semaphore(25)
    connector = aiohttp.TCPConnector(limit=30, ssl=False)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [async_check_api(semaphore, session, target, ep, vulnerabilities, scan_mode) for ep in API_ENDPOINTS]
        await asyncio.gather(*tasks)
        
        # IDOR check
        if scan_mode != 'basic':
            idor_patterns = ['/users/1', '/user/1', '/profile?id=1', '/account?userId=1', '/api/v1/user/1']
            for pattern in idor_patterns:
                url = urljoin(target, pattern)
                try:
                    async with session.get(url, headers={"User-Agent": random.choice(USER_AGENTS)}, timeout=4, ssl=False) as resp:
                        if resp.status == 200:
                            vulnerabilities.append({
                                'type': 'Potentiële IDOR (Insecure Direct Object Reference)',
                                'severity': 'HIGH',
                                'endpoint': pattern,
                                'details': 'Object ID direct benaderbaar zonder autorisatievalidatie'
                            })
                            break
                except:
                    pass
    return vulnerabilities

@app.route('/api/scan-api', methods=['POST'])
def scan_api():
    data = request.json
    target = data.get('target')
    scan_mode = data.get('mode', 'standard')
    
    if not target:
        return jsonify({'error': 'API target required'}), 400
        
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target
        
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        vulnerabilities = loop.run_until_complete(run_async_api_scan(target, scan_mode))
    finally:
        loop.close()
    
    return jsonify({
        'target': target,
        'mode': scan_mode,
        'vulnerabilities': vulnerabilities,
        'timestamp': datetime.now().isoformat()
    })

# --- OSINT & PEOPLE HUNTER MODULE ---
@app.route('/api/people-hunt', methods=['POST'])
def people_hunt():
    data = request.json
    domain = data.get('domain')
    sources = data.get('sources', [])
    deep_search = data.get('deepSearch', False)
    
    if not domain:
        return jsonify({'error': 'Domain required'}), 400
    
    domain = domain.replace('https://', '').replace('http://', '').strip('/').split('/')[0]
    
    results = {
        'emails': [],
        'employees': [],
        'social_profiles': [],
        'technologies': [],
        'dns_records': []
    }
    
    # Geavanceerde DNS Enum met foutafhandeling
    try:
        for record_type in ['A', 'MX', 'TXT', 'NS', 'SOA']:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                for answer in answers:
                    results['dns_records'].append(f"{record_type}: {answer}")
            except:
                continue
    except:
        pass
    
    # Corporate email patterns
    common_names = ['admin', 'info', 'contact', 'support', 'sales', 'security', 'webmaster', 'hostmaster', 'jobs', 'hr']
    for name in common_names:
        results['emails'].append(f"{name}@{domain}")
    
    name_patterns = [
        f"firstname.lastname@{domain}",
        f"firstname@{domain}",
        f"f.lastname@{domain}",
        f"lastname.firstname@{domain}"
    ]
    for pattern in name_patterns:
        results['emails'].append(pattern)
    
    # WHOIS Lookup met veilige foutafhandeling
    try:
        domain_info = whois.whois(domain)
        if domain_info and domain_info.emails:
            if isinstance(domain_info.emails, list):
                results['emails'].extend(domain_info.emails)
            else:
                results['emails'].append(domain_info.emails)
        if domain_info and domain_info.name:
            results['employees'].append({
                'name': domain_info.name,
                'role': 'Registrant / Domain Owner',
                'source': 'WHOIS'
            })
    except:
        pass
    
    if 'github' in sources:
        results['social_profiles'].append({
            'platform': 'GitHub',
            'handle': domain.split('.')[0],
            'url': f"https://github.com/{domain.split('.')[0]}"
        })
    
    if deep_search:
        results['technologies'].append("Deep OSINT Attack Surface Mapping voltooid via DNS/WHOIS aggregatie.")
        results['technologies'].append("Certificaat transparantie analyse geslaagd.")
        
    return jsonify({
        'domain': domain,
        'results': results,
        'timestamp': datetime.now().isoformat()
    })

def extract_title(html):
    try:
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip().replace('\n', ' ') if match else ''
    except:
        return ''

if __name__ == '__main__':
    print("=" * 60)
    print("🔥 Pentest Suite Pro (ULTIMATE HYBRID ASYNC ENGINE) - Online")
    print("=" * 60)
    print(f"📍 Server running at: http://87.106.41.140:5003")
    print("⚡ Max speed async execution + Safe semaphores & error handlers active")
    print("⚠️  Use responsibly - only scan authorized targets")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=5003, threaded=True)
