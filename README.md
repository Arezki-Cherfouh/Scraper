# 🔍 Advanced Web Scraper

Advanced Python web scraper with anti-bot bypass capabilities, multi-search engine support, and beautiful HTML report generation.

## ✨ Features

### Core Capabilities

- 🚀 **Anti-Bot Bypass** - Bypasses Cloudflare and common anti-bot protections using cloudscraper
- 🔎 **Multi-Search Engine Support** - Tries SearXNG → DuckDuckGo → Brave → Google automatically
- 📚 **Wikipedia Integration** - Direct Wikipedia API access for reliable summaries
- 🎭 **Multiple Parsing Methods** - BeautifulSoup with lxml, html5lib, and html.parser fallbacks
- 🌐 **Selenium Fallback** - Handles JavaScript-heavy sites with headless Chrome
- 🔄 **Smart Retry Logic** - Exponential backoff with configurable retries
- 🎲 **Header Rotation** - Randomized user agents and headers to avoid detection

### Report Generation

- 🎨 **Beautiful HTML Reports** - Responsive, modern design with card-based layout
- 🌓 **Smart Theme Support** - Auto-detects system theme, manual override saved to localStorage
- 📱 **Fully Responsive** - Works perfectly on mobile, tablet, and desktop
- 🖱️ **Smart Pointer Detection** - Cursor pointer only on `@media (pointer: fine)` devices
- ♿ **Accessible** - Semantic HTML, ARIA labels, respects `prefers-reduced-motion`
- 💾 **Dual Format Output** - Saves both JSON (data) and HTML (visual report)

## 📦 Installation

### Requirements

- Python 3.7+
- Chrome/Chromium (for Selenium features)

### Install Dependencies

```bash
pip install cloudscraper requests beautifulsoup4 lxml selenium wikipedia-api --break-system-packages
```

Or if you prefer using a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install cloudscraper requests beautifulsoup4 lxml selenium wikipedia-api
```

## 🚀 Quick Start

### Basic Usage

```python
from researcher import AdvancedWebScraper

# Initialize scraper
scraper = AdvancedWebScraper()

# Scrape a single URL
result = scraper.scrape_url("https://example.com")
print(result.title)
print(result.content)

# Research a topic (searches web + Wikipedia)
results = scraper.scrape_topic("machine learning", num_sites=3)

# Save results (creates both JSON and HTML)
scraper.save_results(results, "research.json")

scraper.close()
```

### Command Line

```bash
# Scrape a single URL
python researcher.py https://example.com

# Research a topic with multiple sources
python researcher.py "artificial intelligence" -t -n 5

# Use Selenium for JavaScript sites
python researcher.py https://dynamic-site.com -s

# Custom output file
python researcher.py "climate change" -t -o climate_research.json
```

### Command Line Options

```
positional arguments:
  input                 URL to scrape or topic to search

optional arguments:
  -h, --help            show this help message and exit
  -t, --topic           Treat input as topic (search web using multiple engines and Wikipedia)
  -n NUM, --num-sites NUM
                        Number of sites to scrape for topics (default: 3)
  -s, --selenium        Use Selenium for JavaScript rendering
  -o OUTPUT, --output OUTPUT
                        Output JSON file (default: scraped_data.json)
  --no-wikipedia        Skip Wikipedia summary for topics
```

## 📚 Examples

Run the examples file to see all features in action:

```bash
python examples.py
```

### Example 1: Scrape Single URL

```python
from researcher import AdvancedWebScraper

scraper = AdvancedWebScraper()
result = scraper.scrape_url("https://en.wikipedia.org/wiki/Python_(programming_language)")

if result:
    print(f"Title: {result.title}")
    print(f"Content: {result.content[:200]}...")
    scraper.save_results([result], "python_info.json")

scraper.close()
```

### Example 2: Research a Topic

```python
scraper = AdvancedWebScraper()
results = scraper.scrape_topic("quantum computing", num_sites=5, include_wikipedia=True)

print(f"Found {len(results)} sources")
for result in results:
    print(f"- {result.title} ({result.source})")

scraper.save_results(results, "quantum_research.json")
scraper.close()
```

### Example 3: Wikipedia Only

```python
scraper = AdvancedWebScraper()
result = scraper.get_wikipedia_summary("Neural Networks")

if result:
    print(result.content)
    scraper.save_results([result], "neural_networks.json")

scraper.close()
```

### Example 4: Search Web

```python
scraper = AdvancedWebScraper()
urls = scraper.search_web("python best practices", num_results=10)

print(f"Found {len(urls)} URLs:")
for url in urls:
    print(f"- {url}")

scraper.close()
```

### Example 5: With Selenium (for JavaScript sites)

```python
scraper = AdvancedWebScraper(use_selenium=True)
result = scraper.scrape_url("https://dynamic-javascript-site.com")
scraper.save_results([result], "dynamic_content.json")
scraper.close()
```

## 📊 Data Structure

Each scraped result contains:

```python
{
    "url": str,              # Source URL
    "title": str,            # Page title
    "content": str,          # Main content (up to 5000 chars)
    "meta_description": str, # Meta description (optional)
    "links": List[str],      # Up to 20 external links
    "images": List[str],     # Up to 10 image URLs
    "source": str            # "direct" or "wikipedia"
}
```

## 🎨 HTML Report Features

The generated HTML reports include:

- **Sticky Header** with results count and theme toggle
- **Card-Based Layout** with hover effects (on fine pointer devices)
- **Content Sections** with scrollable areas
- **Related Links** displayed as clickable badges
- **Image Gallery** with lazy loading and error handling
- **Theme Persistence** - Manual theme selection saved to localStorage
- **System Theme Detection** - Automatically respects `prefers-color-scheme`
- **Responsive Design** - Optimized for all screen sizes
- **Accessibility** - ARIA labels, semantic HTML, reduced motion support

## 🔧 Advanced Configuration

### Custom Search Engines

The scraper tries multiple search engines in order:

1. **SearXNG** - JSON API, most reliable
2. **DuckDuckGo** - Scraper-friendly
3. **Brave** - Privacy-focused
4. **Google** - Last resort (actively blocks scrapers)

### Retry Logic

- Default: 3 retries with exponential backoff
- Delay formula: `2^attempt + random(0, 1)` seconds

### User Agent Rotation

Automatically rotates between 5 different user agents:

- Chrome on Windows
- Chrome on macOS
- Chrome on Linux
- Firefox on Windows
- Safari on macOS

## 🚨 Important Notes

### Network Restrictions

If running in a restricted environment (e.g., containers with disabled network):

- Search engines may fail (all 4 will be tried)
- Wikipedia usually still works
- Consider providing direct URLs instead of search queries
- Enable network access in environment settings if possible

### Rate Limiting

- Includes random delays between requests (1-3 seconds)
- Respects robots.txt through cloudscraper
- Be polite - don't hammer servers

### Legal Considerations

- Respect website Terms of Service
- Follow robots.txt guidelines
- Don't scrape copyrighted content without permission
- Use for personal research and educational purposes
- Consider API alternatives when available

## 🛠️ Troubleshooting

### Search Engines Failing

If all search engines fail:

```
ERROR - All search engines failed - possible causes:
  1. Network access is disabled or restricted
  2. Search engines are blocking automated requests
  3. Anti-bot protections are too strong
```

**Solutions:**

- Use Wikipedia-only mode
- Provide direct URLs instead of search queries
- Enable network access in environment settings
- Use API-based search services (Google Custom Search, Bing API)

### Selenium Not Working

```bash
# Install Chrome/Chromium
sudo apt-get install chromium-browser chromium-chromedriver

# Or on macOS
brew install chromium chromedriver
```

### Import Errors

Make sure all dependencies are installed:

```bash
pip install cloudscraper requests beautifulsoup4 lxml selenium wikipedia-api --break-system-packages
```

## 📁 Project Structure

```
.
├── researcher.py          # Main scraper class
├── examples.py            # Example usage scripts
├── DESCRIPTION.txt        # Repo description (350 chars)
└── README.md             # This file
```

## 🤝 Contributing

Contributions are welcome! Some ideas:

- Add more search engine integrations
- Improve content extraction algorithms
- Add support for more file formats
- Enhance HTML report features
- Add more anti-bot bypass techniques

## 📝 License

This project is provided as-is for educational and research purposes.

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Users are responsible for ensuring their use complies with applicable laws and website terms of service. The authors are not responsible for misuse or any damages caused by this software.

## 🌟 Acknowledgments

- **cloudscraper** - Cloudflare bypass
- **BeautifulSoup** - HTML parsing
- **Selenium** - JavaScript rendering
- **Wikipedia API** - Reliable knowledge source
- **SearXNG, DuckDuckGo, Brave, Google** - Search capabilities

---

**Made with ❤️ for researchers, developers, and data enthusiasts**
