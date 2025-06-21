import requests
import os

def test_scraperapi_key():
    print("🔍 Testing ScraperAPI Key...")
    print("=" * 50)
    
    # Your API key
    api_key = 'afb25771be473a63ced548fe95761266'
    print(f"API Key: {api_key[:10]}...")
    
    # Test sites to try
    test_sites = [
        {
            'name': 'HTTPBin (Simple Test)',
            'url': 'https://httpbin.org/html',
            'description': 'Basic HTML page'
        },
        {
            'name': 'Google',
            'url': 'https://www.google.com',
            'description': 'Google homepage'
        },
        {
            'name': 'Wikipedia',
            'url': 'https://en.wikipedia.org/wiki/Python_(programming_language)',
            'description': 'Wikipedia page'
        }
    ]
    
    for i, site in enumerate(test_sites, 1):
        print(f"\n{i}. Testing: {site['name']}")
        print(f"   URL: {site['url']}")
        print(f"   Description: {site['description']}")
        
        try:
            # ScraperAPI parameters
            params = {
                'api_key': api_key,
                'url': site['url']
            }
            
            print("   Making request...")
            response = requests.get('https://api.scraperapi.com/', params=params, timeout=30)
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Size: {len(response.text)} characters")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS!")
                
                # Check if response looks like HTML
                if '<html' in response.text.lower() or '<!doctype' in response.text.lower():
                    print("   ✅ Response contains HTML content")
                else:
                    print("   ⚠️  Response doesn't look like HTML")
                    
            elif response.status_code == 403:
                print("   ❌ FORBIDDEN - Key might be invalid or blocked")
            elif response.status_code == 429:
                print("   ❌ RATE LIMITED - Too many requests")
            else:
                print(f"   ❌ ERROR - Status {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("   ❌ TIMEOUT - Request took too long")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ REQUEST ERROR: {e}")
        except Exception as e:
            print(f"   ❌ UNEXPECTED ERROR: {e}")
    
    print(f"\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print("If all tests fail with 403, your key is invalid or blocked.")
    print("If some tests work, the issue is specific to Jumia.")
    print("If tests timeout, there might be network issues.")

if __name__ == "__main__":
    test_scraperapi_key() 