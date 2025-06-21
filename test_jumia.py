from jumia_scraper import scrape_jumia
import json

def test_jumia_scraper():
    print("🔍 Testing Jumia Scraper...")
    print("=" * 50)
    
    # Test with a simple query
    query = "laptop"
    print(f"Searching for: '{query}'")
    
    try:
        results = scrape_jumia(query, max_results=3)
        
        print(f"\n📊 Results Summary:")
        print(f"Total results found: {len(results)}")
        
        if results:
            print(f"\n✅ Success! Found {len(results)} products:")
            for i, product in enumerate(results, 1):
                print(f"\n{i}. {product['name']}")
                print(f"   Price: {product['price']}")
                print(f"   Link: {product['link']}")
                print(f"   Image: {product['image']}")
        else:
            print("\n❌ No results found!")
            
            # Check if debug file was created
            try:
                with open('jumia_debug.html', 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    print(f"\n📄 Debug HTML file created ({len(html_content)} characters)")
                    
                    # Check for common issues
                    if "Access Denied" in html_content:
                        print("🚫 Issue: Access Denied - ScraperAPI might be blocked")
                    elif "404" in html_content:
                        print("🚫 Issue: 404 Not Found - URL might be incorrect")
                    elif "500" in html_content:
                        print("🚫 Issue: 500 Server Error - ScraperAPI issue")
                    elif len(html_content) < 1000:
                        print("🚫 Issue: Very short response - might be an error page")
                    else:
                        print("✅ HTML response looks normal, but no products found")
                        
            except FileNotFoundError:
                print("📄 No debug HTML file created")
                
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_jumia_scraper() 