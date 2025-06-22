import requests
from bs4 import BeautifulSoup
import time
import os
import re
from datetime import datetime

def scrape_aliexpress(query, max_results=5, debug_mode=False):
    SCRAPERAPI_KEY = os.getenv('SCRAPERAPI_KEY', 'afb25771be473a63ced548fe95761266')
    
    configs_to_try = [
        {
            'name': 'US English site',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.aliexpress.us/wholesale?SearchText={query.replace(' ', '+')}",
                'country_code': 'us'
            }
        },
        {
            'name': 'Global English site',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.aliexpress.com/wholesale?SearchText={query.replace(' ', '+')}&language=en_US",
                'country_code': 'us'
            }
        },
        {
            'name': 'With premium proxies US',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.aliexpress.us/wholesale?SearchText={query.replace(' ', '+')}",
                'premium': 'true',
                'country_code': 'us'
            }
        },
        {
            'name': 'With residential proxies US',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.aliexpress.us/wholesale?SearchText={query.replace(' ', '+')}",
                'residential': 'true',
                'country_code': 'us'
            }
        },
        {
            'name': 'With JavaScript rendering US',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.aliexpress.us/wholesale?SearchText={query.replace(' ', '+')}",
                'render': 'true',
                'wait': '5000',
                'country_code': 'us'
            }
        },
        {
            'name': 'With custom headers US',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.aliexpress.us/wholesale?SearchText={query.replace(' ', '+')}",
                'keep_headers': 'true',
                'country_code': 'us'
            }
        },
        {
            'name': 'With session handling US',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.aliexpress.us/wholesale?SearchText={query.replace(' ', '+')}",
                'session_number': '1',
                'country_code': 'us'
            }
        }
    ]
    
    for i, config in enumerate(configs_to_try, 1):
        try:
            print(f"Attempt {i}: {config['name']}")
            results = _scraper_api_request_with_config(config, max_results, timeout=60, debug_mode=debug_mode)
            if results:
                print(f"✅ Success with {config['name']}!")
                return results
        except Exception as e:
            print(f"❌ {config['name']} failed: {e}")
            if i < len(configs_to_try):
                time.sleep(2)
    print("❌ All ScraperAPI configurations failed")
    return []

def _scraper_api_request_with_config(config, max_results, timeout=60, debug_mode=False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
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
            
            # Only create debug file if debug_mode is enabled or if there's an error
            if debug_mode:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                debug_filename = f"aliexpress_debug_{config['name'].replace(' ', '_').lower()}_{timestamp}.html"
                with open(debug_filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"  📁 Debug file saved: {debug_filename}")
            
            return _parse_results(response.text, max_results)
        else:
            print(f"  ❌ HTTP {response.status_code}: {response.text[:200]}...")
            # Create debug file for errors even if debug_mode is False
            if not debug_mode:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                debug_filename = f"aliexpress_error_{config['name'].replace(' ', '_').lower()}_{timestamp}.html"
                with open(debug_filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"  📁 Error debug file saved: {debug_filename}")
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
    
    # Updated selectors based on AliExpress HTML structure
    products = soup.select('a.kr_b.search-card-item') or soup.select('a.kr_b') or soup.select('div.kr_ke a.kr_b')
    
    print(f"Found {len(products)} product containers")
    
    if not products:
        print("No products found with any selector")
        return []

    results = []
    for i, product in enumerate(products[:max_results]):
        try:
            print(f"\nProcessing product {i+1}:")
            
            # Product name - look for title elements
            name_tag = (
                product.select_one('.kr_j0') or  # Product title class
                product.select_one('.kr_av') or  # Alternative title class
                product.select_one('span[class*="title"]') or
                product.select_one('div[class*="title"]')
            )
            
            # Price - look for price elements
            price_tag = (
                product.select_one('.kr_gf .kr_kj') or  # Main price
                product.select_one('.kr_gf .kr_kk') or  # Alternative price
                product.select_one('span[class*="price"]') or
                product.select_one('div[class*="price"]')
            )
            
            # Product link - the href attribute of the product card
            link = product.get('href', '')
            
            print(f"  Name tag found: {name_tag is not None}")
            print(f"  Price tag found: {price_tag is not None}")
            print(f"  Link found: {bool(link)}")
            
            if not all([name_tag, price_tag, link]):
                print(f"  Missing required elements for product {i+1}")
                continue

            name = name_tag.get_text(strip=True)
            price = price_tag.get_text(strip=True)
            
            print(f"  Name: {name}")
            print(f"  Price: {price}")
            print(f"  Link: {link}")
            
            # Clean up the link
            if link and not link.startswith('http'):
                link = 'https:' + link if link.startswith('//') else 'https://www.aliexpress.us' + link
            
            # Clean up price text
            price = re.sub(r'[^\d.,]', '', price)  # Keep only digits, dots, and commas
            if price:
                price = f"${price}"
            
            # Get image URL
            image_tag = product.select_one('img')
            image = ''
            if image_tag:
                image = image_tag.get('src') or image_tag.get('data-src', '')
                if image and not image.startswith('http'):
                    image = 'https:' + image if image.startswith('//') else 'https://www.aliexpress.us' + image
            
            result = {
                'name': name,
                'price': price,
                'link': link,
                'image': image
            }
            
            print(f"  ✅ Product {i+1} processed successfully")
            results.append(result)
            
        except Exception as e:
            print(f"  ❌ Error processing product {i+1}: {e}")
            continue
    
    print(f"\n✅ Successfully processed {len(results)} products")
    return results

if __name__ == "__main__":
    test_query = "laptop"
    print(f"Testing AliExpress scraper with query: {test_query}")
    # Set debug_mode=False to prevent debug file creation
    results = scrape_aliexpress(test_query, max_results=3, debug_mode=False)
    if results:
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['name']} - {result['price']}")
    else:
        print("No results found") 