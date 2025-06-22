import requests
from bs4 import BeautifulSoup
import time
import os
import re
from datetime import datetime

def scrape_temu(query, max_results=5, debug_mode=False):
    SCRAPERAPI_KEY = os.getenv('SCRAPERAPI_KEY', 'afb25771be473a63ced548fe95761266')
    
    configs_to_try = [
        {
            'name': 'US English site',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.temu.com/search.html?search_key={query.replace(' ', '+')}",
                'country_code': 'us'
            }
        },
        {
            'name': 'With premium proxies US',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.temu.com/search.html?search_key={query.replace(' ', '+')}",
                'premium': 'true',
                'country_code': 'us'
            }
        },
        {
            'name': 'With residential proxies US',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.temu.com/search.html?search_key={query.replace(' ', '+')}",
                'residential': 'true',
                'country_code': 'us'
            }
        },
        {
            'name': 'With JavaScript rendering US',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.temu.com/search.html?search_key={query.replace(' ', '+')}",
                'render': 'true',
                'wait': '5000',
                'country_code': 'us'
            }
        },
        {
            'name': 'With custom headers US',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.temu.com/search.html?search_key={query.replace(' ', '+')}",
                'keep_headers': 'true',
                'country_code': 'us'
            }
        },
        {
            'name': 'With session handling US',
            'params': {
                'api_key': SCRAPERAPI_KEY,
                'url': f"https://www.temu.com/search.html?search_key={query.replace(' ', '+')}",
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
                debug_filename = f"temu_debug_{config['name'].replace(' ', '_').lower()}_{timestamp}.html"
                with open(debug_filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"  📁 Debug file saved: {debug_filename}")
            
            return _parse_results(response.text, max_results)
        else:
            print(f"  ❌ HTTP {response.status_code}: {response.text[:200]}...")
            # Create debug file for errors even if debug_mode is False
            if not debug_mode:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                debug_filename = f"temu_error_{config['name'].replace(' ', '_').lower()}_{timestamp}.html"
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
    
    results = []
    
    # Method 1: Look for JSON data in script tags containing product information
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and ('priceInfo' in script.string or 'linkUrl' in script.string):
            try:
                # Extract JSON-like data from script content
                script_text = script.string
                # Look for patterns like "priceInfo":{"price":2176,"currency":"USD"...}
                import re
                
                # Find price patterns
                price_matches = re.findall(r'"price":(\d+),', script_text)
                price_text_matches = re.findall(r'"priceStr":"([^"]+)"', script_text)
                link_matches = re.findall(r'"linkUrl":"([^"]+)"', script_text)
                title_matches = re.findall(r'"title":"([^"]+)"', script_text)
                image_matches = re.findall(r'"image":"([^"]+)"', script_text)
                
                # Combine matches into products
                for i in range(min(len(price_matches), len(link_matches), max_results)):
                    if i < len(results):
                        continue
                        
                    price = price_matches[i] if i < len(price_matches) else "0"
                    price_str = price_text_matches[i] if i < len(price_text_matches) else f"${int(price)/100:.2f}" if price.isdigit() else "N/A"
                    link = link_matches[i] if i < len(link_matches) else ""
                    title = title_matches[i] if i < len(title_matches) else "Product"
                    image = image_matches[i] if i < len(image_matches) else ""
                    
                    # Clean up URL encoding
                    link = link.replace('\\u002F', '/')
                    title = title.replace('\\u002F', '/')
                    image = image.replace('\\u002F', '/')
                    
                    if link and not link.startswith('http'):
                        link = f"https://www.temu.com{link}"
                    if image and not image.startswith('http'):
                        image = f"https:{image}"
                    
                    results.append({
                        'name': title,
                        'price': price_str,
                        'link': link,
                        'image': image
                    })
                    
                    if len(results) >= max_results:
                        break
                        
            except Exception as e:
                print(f"Error parsing script data: {e}")
                continue
    
    # Method 2: Look for price elements with data-type="price"
    if len(results) < max_results:
        price_elements = soup.select('[data-type="price"]')
        print(f"Found {len(price_elements)} price elements")
        
        for price_elem in price_elements[:max_results - len(results)]:
            try:
                # Get price from aria-label or text content
                price = price_elem.get('aria-label', '')
                if not price:
                    price = price_elem.get_text(strip=True)
                
                # Find the parent container that might contain the product link
                parent = price_elem
                link_elem = None
                name_elem = None
                
                # Look for link in parent containers
                for _ in range(5):  # Look up to 5 levels up
                    parent = parent.parent
                    if not parent:
                        break
                    
                    # Look for link
                    if not link_elem:
                        link_elem = parent.find('a', href=True)
                    
                    # Look for image with alt text (product name)
                    if not name_elem:
                        img_elem = parent.find('img', alt=True)
                        if img_elem and img_elem.get('alt'):
                            name_elem = img_elem
                
                link = link_elem.get('href') if link_elem else ""
                name = name_elem.get('alt') if name_elem else "Product"
                image = name_elem.get('src') if name_elem else ""
                
                # Clean up URLs
                if link and not link.startswith('http'):
                    link = f"https://www.temu.com{link}"
                if image and not image.startswith('http'):
                    image = f"https:{image}"
                
                results.append({
                    'name': name,
                    'price': price,
                    'link': link,
                    'image': image
                })
                
            except Exception as e:
                print(f"Error parsing price element: {e}")
                continue
    
    # Method 3: Look for any links that might be product links
    if len(results) < max_results:
        product_links = soup.find_all('a', href=True)
        for link_elem in product_links:
            if len(results) >= max_results:
                break
                
            href = link_elem.get('href', '')
            if '/channel/' in href or '/attendance/' in href:
                try:
                    # Look for image with alt text
                    img_elem = link_elem.find('img', alt=True)
                    name = img_elem.get('alt') if img_elem else "Product"
                    image = img_elem.get('src') if img_elem else ""
                    
                    # Look for price in the link or nearby
                    price_elem = link_elem.find(attrs={'data-type': 'price'})
                    price = price_elem.get('aria-label', 'N/A') if price_elem else "N/A"
                    
                    # Clean up URLs
                    if not href.startswith('http'):
                        href = f"https://www.temu.com{href}"
                    if image and not image.startswith('http'):
                        image = f"https:{image}"
                    
                    results.append({
                        'name': name,
                        'price': price,
                        'link': href,
                        'image': image
                    })
                    
                except Exception as e:
                    print(f"Error parsing product link: {e}")
                    continue
    
    print(f"Total products found: {len(results)}")
    return results[:max_results]

if __name__ == "__main__":
    test_query = "laptop"
    print(f"Testing Temu scraper with query: {test_query}")
    # Set debug_mode=False to prevent debug file creation
    results = scrape_temu(test_query, max_results=3, debug_mode=False)
    if results:
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['name']} - {result['price']}")
    else:
        print("No results found") 