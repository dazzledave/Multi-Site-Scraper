import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
import os
import re

def scrape_jumia(query, max_results=5):
    # Get API key from environment variable or use default
    SCRAPERAPI_KEY = os.getenv('SCRAPERAPI_KEY', '38bde1db8b81b05543c7c870d085a6f7')
    
    # Try multiple ScraperAPI configurations
    configs_to_try = [
        {
            'name': 'Basic configuration',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.jumia.com.gh/catalog/?q={query.replace(' ', '+')}"
            }
        },
        {
            'name': 'With country code',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.jumia.com.gh/catalog/?q={query.replace(' ', '+')}",
                'country_code': 'gh'
            }
        },
        {
            'name': 'With premium proxies',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.jumia.com.gh/catalog/?q={query.replace(' ', '+')}",
                'premium': 'true'
            }
        },
        {
            'name': 'With residential proxies',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.jumia.com.gh/catalog/?q={query.replace(' ', '+')}",
                'residential': 'true'
            }
        },
        {
            'name': 'With JavaScript rendering',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.jumia.com.gh/catalog/?q={query.replace(' ', '+')}",
                'render': 'true',
                'wait': '3000'
            }
        },
        {
            'name': 'With custom headers',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.jumia.com.gh/catalog/?q={query.replace(' ', '+')}",
                'keep_headers': 'true'
            }
        },
        {
            'name': 'With session handling',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.jumia.com.gh/catalog/?q={query.replace(' ', '+')}",
                'session_number': '1'
            }
        }
    ]
    
    for i, config in enumerate(configs_to_try, 1):
        try:
            print(f"Attempt {i}: {config['name']}")
            results = _scraper_api_request_with_config(config, max_results, timeout=60)
            if results:
                print(f"✅ Success with {config['name']}!")
                return results
        except Exception as e:
            print(f"❌ {config['name']} failed: {e}")
            if i < len(configs_to_try):  # Don't sleep after last attempt
                time.sleep(2)
    
    print("❌ All ScraperAPI configurations failed")
    return []

def _scraper_api_request_with_config(config, max_results, timeout=60):
    """Make ScraperAPI request with specific configuration"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    search_url = 'https://api.scraperapi.com/'
    
    try:
        print(f"  Making request with {config['name']}...")
        response = requests.get(search_url, params=config['params'], headers=headers, timeout=timeout)
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response Size: {len(response.text)} characters")
        
        if response.status_code == 200:
            print(f"  ✅ Response received successfully")
            
            # Save debug HTML for troubleshooting
            debug_filename = f"jumia_debug_{config['name'].replace(' ', '_').lower()}.html"
            with open(debug_filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            return _parse_results(response.text, max_results)
        else:
            print(f"  ❌ HTTP {response.status_code}: {response.text[:200]}...")
            return []
            
    except requests.exceptions.Timeout:
        print(f"  ❌ Request timed out after {timeout} seconds")
        return []
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Request failed: {e}")
        return []
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return []

def _parse_results(html_content, max_results):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Try different selectors for product containers - updated for new structure
    products = soup.select('article.prd') or soup.select('article[class*="prd"]') or soup.select('div.c-prd') or soup.select('div[data-prd]')
    
    print(f"Found {len(products)} product containers")
    
    if not products:
        print("No products found with any selector")
        return []

    results = []
    for i, product in enumerate(products[:max_results]):
        try:
            print(f"\nProcessing product {i+1}:")
            
            # Updated selectors based on the HTML structure shown in the logs
            name_tag = (
                product.select_one('h2.name') or 
                product.select_one('h2[class*="name"]') or
                product.select_one('h3.name') or 
                product.select_one('h3[class*="name"]') or
                product.select_one('div[class*="name"]') or
                product.select_one('a[class*="name"]')
            )
            
            price_tag = (
                product.select_one('p.prc') or
                product.select_one('p[class*="prc"]') or
                product.select_one('div.prc') or
                product.select_one('div[class*="prc"]') or
                product.select_one('div[class*="price"]')
            )
            
            # Look for product links - find the first <a> with href starting with '/' and not containing '/cart/' or '/customer/'
            link_tag = None
            for a in product.find_all('a', href=True):
                href = a['href']
                if href.startswith('/') and '/cart/' not in href and '/customer/' not in href and '.html' in href:
                    link_tag = a
                    break
                    
            print(f"  Name tag found: {name_tag is not None}")
            print(f"  Price tag found: {price_tag is not None}")
            print(f"  Link tag found: {link_tag is not None}")
            
            if not all([name_tag, price_tag, link_tag]):
                print(f"  Missing required elements for product {i+1}")
                continue

            name = name_tag.get_text(strip=True)
            price = price_tag.get_text(strip=True)
            link = link_tag.get('href')
            
            print(f"  Name: {name}")
            print(f"  Price: {price}")
            print(f"  Link: {link}")
            
            if link and not link.startswith('http'):
                link = 'https://www.jumia.com.gh' + link
            link = link.split('?')[0]  # Remove query parameters
            
            image_tag = product.select_one('img')

            # Get image URL
            image = ''
            if image_tag:
                image = image_tag.get('data-src') or image_tag.get('src', '')
                if image and not image.startswith('http'):
                    image = 'https://www.jumia.com.gh' + image

            # Generate a more reliable link
            reliable_link = _generate_reliable_link(name, link)
            
            results.append({
                'name': name,
                'price': price,
                'link': reliable_link,
                'image': image
            })
            
            print(f"  Successfully processed product {i+1}")
            
        except Exception as e:
            print(f"Error parsing product {i+1}: {e}")
            continue

    print(f"\nTotal products successfully parsed: {len(results)}")
    return results

def _generate_reliable_link(name, original_link):
    """Generate a more reliable product link"""
    try:
        # Clean the product name for URL generation
        clean_name = re.sub(r'[^\w\s-]', '', name.lower())
        clean_name = re.sub(r'[-\s]+', '-', clean_name)
        clean_name = clean_name.strip('-')
        
        # If we have a good original link, use it
        if original_link and 'jumia.com.gh' in original_link:
            return original_link
        
        # Otherwise, create a search link
        search_query = name.replace(' ', '+')
        return f"https://www.jumia.com.gh/catalog/?q={search_query}"
        
    except Exception as e:
        print(f"Error generating reliable link: {e}")
        # Fallback to search page
        search_query = name.replace(' ', '+')
        return f"https://www.jumia.com.gh/catalog/?q={search_query}"
