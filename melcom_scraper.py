import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
from cache_manager import CacheManager
import concurrent.futures
import time
import re

SCRAPERAPI_KEY = '38bde1db8b81b05543c7c870d085a6f7'

def scrape_melcom(query, max_results=5):
    cache = CacheManager()
    
    # Try to get cached results first
    cached_results = cache.get_cached_results(query, 'melcom')
    if cached_results:
        print("Returning cached Melcom results")
        return cached_results

    # Try ScraperAPI first (like Jumia does) to get HTML and extract real links
    try:
        results = _scraper_api_request(query, max_results)
        if results:
            print(f"ScraperAPI returned {len(results)} results")
            cache.cache_results(query, 'melcom', results)
            return results
    except Exception as e:
        print(f"ScraperAPI request failed: {e}")

    # Fall back to mobile API if HTML parsing fails
    try:
        results = _mobile_api_request(query, max_results)
        if results:
            print(f"Mobile API returned {len(results)} results")
            cache.cache_results(query, 'melcom', results)
            return results
    except Exception as e:
        print(f"Mobile API request failed: {e}")

    return []

def _find_product_link_from_anchors(anchors):
    for a in anchors:
        href = a.get('href', '')
        if href.endswith('.html'):
            if href.startswith('/'):
                return f"https://melcom.com{href}"
            elif href.startswith('http'):
                return href
            else:
                return f"https://melcom.com/{href}"
    return None

def _is_valid_link(url, timeout=5):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, stream=True, allow_redirects=True)
        resp.close()
        if resp.status_code in (200, 301, 302):
            return True
        if resp.status_code in (403, 405) and url.endswith('.html'):
            # Some sites block bots or HEAD/GET, but the link is likely valid if it matches the pattern
            return True
        return False
    except Exception as e:
        print(f"Link check failed for {url}: {e}")
        # If the link matches .html, assume valid as fallback
        if url.endswith('.html'):
            return True
        return False

def _mobile_api_request(query, max_results, timeout=15):
    encoded_query = urllib.parse.quote(query)
    api_url = f"https://melcom.com/rest/V1/products?searchCriteria[filterGroups][0][filters][0][field]=name&searchCriteria[filterGroups][0][filters][0][value]=%25{encoded_query}%25&searchCriteria[filterGroups][0][filters][0][conditionType]=like&searchCriteria[pageSize]={max_results}&searchCriteria[currentPage]=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
        'Accept': 'application/json',
        'Store': 'default'
    }

    print(f"Making API request to: {api_url}")
    response = requests.get(api_url, headers=headers, timeout=timeout)
    print(f"API response status: {response.status_code}")
    
    if response.status_code != 200:
        raise Exception(f"Mobile API request failed with status code: {response.status_code}")

    data = response.json()
    if not isinstance(data, dict) or 'items' not in data:
        raise Exception("Invalid API response format")

    results = []
    for item in data['items'][:max_results*2]:  # Fetch more to account for filtering
        try:
            name = item.get('name', '')
            price = str(item.get('price', '0.00'))
            sku = item.get('sku', '')
            product_id = item.get('id', '')
            
            print(f"Processing product: {name} (ID: {product_id}, SKU: {sku})")
            
            # Get the first image if available
            image = ''
            if 'media_gallery_entries' in item and item['media_gallery_entries']:
                image = item['media_gallery_entries'][0].get('file', '')
                if image and not image.startswith('http'):
                    image = f"https://melcom.com/media/catalog/product{image}"
            
            # Try to get the actual product URL from the API response
            # Some APIs include the product URL in the response
            product_url = None
            if 'custom_attributes' in item:
                for attr in item['custom_attributes']:
                    if attr.get('attribute_code') == 'url_key':
                        url_key = attr.get('value')
                        if url_key:
                            product_url = f"/{url_key}.html"
                            break
            
            # Find the first .html link
            link = None
            if product_url:
                link = _find_product_link_from_anchors([type('A', (), {'get': lambda self, k, default=None: product_url if k == 'href' else default})()])
            if not link:
                link = _generate_simple_link(name, product_id, sku)
            print(f"Final link: {link}")
            
            results.append({
                'name': name,
                'price': f"GHS {price}",
                'link': link,
                'image': image
            })
        except Exception as e:
            print(f"Error processing product from API: {e}")
            continue
    # Filter for valid links
    filtered = [r for r in results if _is_valid_link(r['link'])]
    return filtered[:max_results]

def _generate_simple_link(name, product_id, sku, url_key=None):
    """Generate a simple, reliable link for Melcom"""
    try:
        # If we have a product ID, use it for direct product view
        if product_id:
            return f"https://melcom.com/catalog/product/view/id/{product_id}"
        
        # If we have an SKU, try to construct a product URL
        if sku:
            # Clean the product name for URL generation
            clean_name = _clean_product_name(name)
            return f"https://melcom.com/{clean_name}-{sku}.html"
        
        # Otherwise, use the product name for search
        search_query = urllib.parse.quote(name)
        return f"https://melcom.com/catalogsearch/result/?q={search_query}"
        
    except Exception as e:
        print(f"Error generating simple link: {e}")
        # Fallback to search page with product name
        search_query = urllib.parse.quote(name)
        return f"https://melcom.com/catalogsearch/result/?q={search_query}"

def _clean_product_name(name):
    """Clean product name for URL generation"""
    try:
        # Remove special characters and replace spaces with hyphens
        import re
        # Remove special characters except letters, numbers, and spaces
        clean_name = re.sub(r'[^\w\s-]', '', name)
        # Replace multiple spaces with single hyphen
        clean_name = re.sub(r'\s+', '-', clean_name)
        # Replace multiple hyphens with single hyphen
        clean_name = re.sub(r'-+', '-', clean_name)
        # Convert to lowercase
        clean_name = clean_name.lower()
        # Remove leading/trailing hyphens
        clean_name = clean_name.strip('-')
        return clean_name
    except Exception as e:
        print(f"Error cleaning product name: {e}")
        return name.lower().replace(' ', '-')

def _scraper_api_request(query, max_results, timeout=30):
    target_url = f"https://melcom.com/catalogsearch/result/?q={urllib.parse.quote(query)}"
    search_url = f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&render=true&premium=true&country_code=gh&url={target_url}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    response = requests.get(search_url, headers=headers, timeout=timeout)
    if response.status_code != 200:
        raise Exception(f"ScraperAPI request failed with status code: {response.status_code}")

    return _parse_html_results(response.text, max_results)

def _parse_html_results(html_content, max_results):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Try multiple selectors
    product_cards = (
        soup.select("ol.products.list.items.product-items > li.item.product.product-item") or
        soup.select(".products-grid .product-item") or
        soup.select(".product-items .product-item") or
        soup.select("[data-container='product-grid'] .product-item")
    )
    
    print(f"Found {len(product_cards)} product cards in HTML")
    
    results = []
    for card in product_cards:
        try:
            # Product name
            name_elem = (
                card.select_one("a.product-item-link") or
                card.select_one("a.product-name") or
                card.select_one("strong.product.name.product-item-name a")
            )
            
            # Price
            price_elem = (
                card.select_one("span[data-price-type='finalPrice'] .price") or
                card.select_one(".special-price .price") or
                card.select_one(".price-box .price")
            )
            
            # Look for product links - find the first <a> with href containing product info
            anchors = card.find_all('a', href=True)
            link = _find_product_link_from_anchors(anchors)
            
            # Image
            image_elem = (
                card.select_one("img.product-image-photo") or
                card.select_one("img.photo.image")
            )
            
            if not all([name_elem, price_elem, link]):
                continue
                
            name = name_elem.text.strip()
            price = price_elem.text.strip()
            image = image_elem['src'] if image_elem and image_elem.has_attr('src') else ""

            print(f"Processing HTML product: {name}")
            print(f"Final link: {link}")

            results.append({
                "name": name,
                "price": price,
                "link": link,
                "image": image
            })
        except Exception as e:
            print(f"Error parsing product from HTML: {e}")
            continue

    # Filter for valid links
    filtered = [r for r in results if _is_valid_link(r['link'])]
    return filtered[:max_results]

def _get_reliable_link(original_link, name):
    # Only use links ending with .html as product links
    if original_link and original_link.endswith('.html'):
        if original_link.startswith('/'):
            return f"https://melcom.com{original_link}"
        elif original_link.startswith('http'):
            return original_link
        else:
            return f"https://melcom.com/{original_link}"
    # Otherwise, create a search link
    import urllib.parse
    search_query = urllib.parse.quote(name)
    return f"https://melcom.com/catalogsearch/result/?q={search_query}" 