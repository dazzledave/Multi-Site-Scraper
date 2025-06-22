# Multi-Site Product Scraper

A modern web application that allows users to search for products across multiple e-commerce platforms simultaneously. Built with Flask and featuring a beautiful, responsive UI.

![image](https://github.com/user-attachments/assets/8fb5dbcd-7059-477d-8e6e-ca217d78ef65)


##  Features

- **Multi-Platform Search**: Search across multiple e-commerce sites at once
- **Beautiful UI**: Modern, responsive design with dark/light theme toggle
- **Real-time Results**: Get product information, prices, and links instantly
- **Scraper Selection**: Choose which platforms to search from
- **Error Handling**: Robust error handling and retry mechanisms

## 🛠️ Currently Supported Platforms

- ✅ **Jumia** - African e-commerce platform
- 🔄 **Amazon** - Coming Soon
- 🔄 **eBay** - Coming Soon
- 🔄 **AliExpress** - Coming Soon
- 🔄 **Walmart** - Coming Soon

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- ScraperAPI account (for web scraping)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/multi-site-product-scraper.git
   cd multi-site-product-scraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your ScraperAPI key**
   - Get your API key from [ScraperAPI](https://www.scraperapi.com/)
   - Set it as an environment variable:
     ```bash
     export SCRAPERAPI_KEY=your_api_key_here
     ```
   - Or update the default key in the scraper files

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   - Go to `http://127.0.0.1:5000`
   - Start searching for products!


### Adding New Scrapers

To add a new scraper:

1. Create a new scraper file (e.g., `amazon_scraper.py`)
2. Implement the scraping function
3. Add it to the `AVAILABLE_SCRAPERS` configuration in `app.py`
4. Update the UI templates if needed

### Environment Variables

- `SCRAPERAPI_KEY`: Your ScraperAPI key for web scraping

