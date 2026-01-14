# -*- coding: utf-8 -*-
"""
YC Founder Data Scraper - v2
Scrapes founder information from YC company pages
"""

import requests
import json
import time
import re
import sys
from pathlib import Path
from collections import Counter

# Configure encoding
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

def scrape_company_page(slug):
    """Scrape a single company page for founder data"""
    url = f'https://www.ycombinator.com/companies/{slug}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return {'error': f'HTTP {resp.status_code}'}
        
        text = resp.text
        founders = []
        
        # Find Active Founders section
        if 'Active Founders' in text:
            idx = text.find('Active Founders')
            section = text[idx:idx+20000]  # Large enough for 4-5 founders
            
            # Extract names from img alt attributes
            names = re.findall(r'alt="([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)"', section)
            unique_names = list(dict.fromkeys(names))  # Remove duplicates, keep order
            
            # Extract roles
            roles = re.findall(r'>([^<]*(?:Co-founder|Founder|CEO|CTO|COO|CPO|CRO|CMO|CFO)[^<]{0,20})</div>', section, re.IGNORECASE)
            
            # Extract bios (longer text with keywords)
            bios = re.findall(r'>([^<]{80,600})</div>', section)
            relevant_bios = [b for b in bios if any(kw in b for kw in 
                ['Before', 'Previously', 'Stanford', 'MIT', 'Berkeley', 'Harvard', 'CMU', 
                 'Google', 'Meta', 'Apple', 'Amazon', 'Microsoft', 'Tesla',
                 'studied', 'worked', 'founded', 'built', 'engineer', 'PhD'])]
            
            # Match names with bios
            for i, name in enumerate(unique_names):
                founder = {'name': name, 'role': '', 'bio': ''}
                
                # Find role for this founder
                for role in roles:
                    if name.split()[0] in role or (i < len(roles) and len(role) < 30):
                        founder['role'] = role.strip()
                        break
                
                # Find bio for this founder
                for bio in relevant_bios:
                    if name.split()[0] in bio:
                        founder['bio'] = bio.strip()
                        break
                
                founders.append(founder)
        
        # Extract Primary Partner
        partner = None
        partner_match = re.search(r'Primary Partner.*?href="/people/[^"]*"[^>]*>([^<]+)', text)
        if partner_match:
            partner = partner_match.group(1).strip()
        
        # Extract Founded year
        founded = None
        founded_match = re.search(r'"Founded:"[^}]*"(\d{4})"', text)
        if founded_match:
            founded = founded_match.group(1)
        
        return {
            'founders': founders,
            'primary_partner': partner,
            'founded': founded,
            'founders_count': len(founders)
        }
        
    except Exception as e:
        return {'error': str(e)}


def main():
    # Load company list
    data_dir = Path('C:/Users/WIN/Desktop/Cursor Project/docs/yc')
    with open(data_dir / 'yc_2024_2026.json', 'r', encoding='utf-8') as f:
        companies = json.load(f)
    
    print(f'Total companies to scrape: {len(companies)}')
    
    # Results storage
    results = []
    errors = []
    
    # Progress tracking
    start_time = time.time()
    
    for i, company in enumerate(companies):
        slug = company['slug']
        name = company['name']
        
        # Progress update every 50 companies
        if i % 50 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed if elapsed > 0 else 1
            remaining = (len(companies) - i) / rate if rate > 0 else 0
            print(f'[{i}/{len(companies)}] Processing... (ETA: {remaining/60:.1f} min)')
        
        # Scrape
        data = scrape_company_page(slug)
        
        # Merge with existing company data
        result = {**company, **data}
        results.append(result)
        
        if 'error' in data:
            errors.append({'slug': slug, 'name': name, 'error': data['error']})
        
        # Rate limiting - 0.3s between requests
        time.sleep(0.3)
        
        # Save checkpoint every 100 companies
        if (i + 1) % 100 == 0:
            with open(data_dir / 'yc_founders_checkpoint.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f'  Checkpoint saved: {i+1} companies, {len(errors)} errors')
    
    # Final save
    output_path = data_dir / 'yc_founders_2024_2026.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f'\n=== Complete ===')
    print(f'Total: {len(results)} companies')
    print(f'Errors: {len(errors)}')
    print(f'Saved to: {output_path}')
    
    # Quick stats
    total_founders = sum(r.get('founders_count', 0) for r in results)
    print(f'Total founders found: {total_founders}')
    
    # Analyze bios for common keywords
    all_bios = []
    for r in results:
        for f in r.get('founders', []):
            if f.get('bio'):
                all_bios.append(f['bio'])
    
    # School analysis
    schools = ['Stanford', 'MIT', 'Berkeley', 'Harvard', 'CMU', 'Princeton', 'Yale', 'Columbia', 'Cornell', 'Penn', 'Caltech']
    school_counts = Counter()
    for bio in all_bios:
        for school in schools:
            if school in bio:
                school_counts[school] += 1
    
    print('\nTop schools mentioned:')
    for school, count in school_counts.most_common(10):
        print(f'  {school}: {count}')
    
    # Company analysis
    companies_list = ['Google', 'Meta', 'Facebook', 'Apple', 'Amazon', 'Microsoft', 'Tesla', 'Uber', 'Airbnb', 'Stripe', 'OpenAI', 'DeepMind']
    company_counts = Counter()
    for bio in all_bios:
        for comp in companies_list:
            if comp in bio:
                company_counts[comp] += 1
    
    print('\nTop companies mentioned:')
    for comp, count in company_counts.most_common(10):
        print(f'  {comp}: {count}')


if __name__ == '__main__':
    main()
