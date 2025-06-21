from jumia_scraper import scrape_jumia

def test_flask_integration():
    print("🔍 Testing Flask Integration with Jumia Scraper...")
    print("=" * 60)
    
    # Simulate what the Flask app does
    query = "laptop"
    selected_scrapers = ['jumia']
    
    print(f"Query: '{query}'")
    print(f"Selected scrapers: {selected_scrapers}")
    
    all_results = []
    
    for scraper_id in selected_scrapers:
        print(f"\n📡 Calling {scraper_id} scraper...")
        
        try:
            # Call the scraper function (same as Flask app)
            scraper_results = scrape_jumia(query, max_results=5)
            
            print(f"Raw results from scraper: {len(scraper_results)} items")
            
            # Add source information to each result (same as Flask app)
            for result in scraper_results:
                result['source'] = scraper_id
                print(f"  - {result['name']} ({result['price']})")
            
            all_results.extend(scraper_results)
            
        except Exception as e:
            print(f"❌ Error with {scraper_id} scraper: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n📊 Final Results Summary:")
    print(f"Total results: {len(all_results)}")
    
    if all_results:
        print("\n✅ Success! Results ready for template:")
        for i, result in enumerate(all_results, 1):
            print(f"{i}. {result['name']} - {result['price']} (Source: {result['source']})")
    else:
        print("\n❌ No results found!")
    
    return all_results

if __name__ == "__main__":
    test_flask_integration() 