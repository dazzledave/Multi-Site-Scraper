from flask import Flask, render_template, request, redirect, url_for
from jumia_scraper import scrape_jumia
from amazon_scraper import scrape_amazon
from aliexpress_scraper import scrape_aliexpress
from temu_scraper import scrape_temu

app = Flask(__name__)

# Available scrapers configuration
AVAILABLE_SCRAPERS = {
    'jumia': {
        'name': 'Jumia',
        'function': scrape_jumia,
        'description': 'African e-commerce platform',
        'status': 'available'
    },
    'amazon': {
        'name': 'Amazon',
        'function': scrape_amazon,
        'description': 'Global e-commerce giant',
        'status': 'available'
    },
    'aliexpress': {
        'name': 'AliExpress',
        'function': scrape_aliexpress,
        'description': 'Global online retail',
        'status': 'available'
    },
    'temu': {
        'name': 'Temu',
        'function': scrape_temu,
        'description': 'Fast fashion & lifestyle',
        'status': 'available'
    },
    'ebay': {
        'name': 'eBay',
        'function': None,
        'description': 'Online auction & shopping',
        'status': 'coming_soon'
    },
    'walmart': {
        'name': 'Walmart',
        'function': None,
        'description': 'American retail corporation',
        'status': 'coming_soon'
    }
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('product_name')
        selected_scrapers = request.form.getlist('scrapers')
        
        if not selected_scrapers:
            # If no scrapers selected, redirect back with error
            return redirect(url_for('index'))
        
        return redirect(url_for('results', query=query, scrapers=','.join(selected_scrapers)))
    
    return render_template('index.html', scrapers=AVAILABLE_SCRAPERS)

@app.route('/results')
def results():
    query = request.args.get('query')
    scrapers_param = request.args.get('scrapers', '')
    selected_scrapers = scrapers_param.split(',') if scrapers_param else []
    
    all_results = []
    
    if query and selected_scrapers:
        for scraper_id in selected_scrapers:
            if scraper_id in AVAILABLE_SCRAPERS:
                scraper_config = AVAILABLE_SCRAPERS[scraper_id]
                
                if scraper_config['function'] and scraper_config['status'] == 'available':
                    try:
                        # Call the scraper function
                        if scraper_id in ['aliexpress', 'temu']:
                            scraper_results = scraper_config['function'](query, max_results=5, debug_mode=False)
                        else:
                            scraper_results = scraper_config['function'](query, max_results=5)
                        
                        # Add source information to each result
                        for result in scraper_results:
                            result['source'] = scraper_id
                        
                        all_results.extend(scraper_results)
                        
                    except Exception as e:
                        print(f"Error with {scraper_id} scraper: {e}")
                        # Add error result
                        all_results.append({
                            'name': f"Error: Could not scrape {scraper_config['name']}",
                            'price': 'N/A',
                            'link': '#',
                            'image': '',
                            'source': scraper_id,
                            'error': True
                        })
                else:
                    # Add placeholder for unavailable scrapers
                    all_results.append({
                        'name': f"{scraper_config['name']} scraper is not available yet",
                        'price': 'Coming Soon',
                        'link': '#',
                        'image': '',
                        'source': scraper_id,
                        'placeholder': True
                    })
    
    return render_template('results.html', results=all_results, query=query, selected_scrapers=selected_scrapers)

if __name__ == '__main__':
    app.run(debug=True) 