#!/usr/bin/env python3
"""
Advanced Web Scraper with Anti-Bot Bypass
Features:
- Bypasses Cloudflare and common anti-bot protections
- Multi-search engine integration (SearXNG, DuckDuckGo, Brave, Google)
- Wikipedia summaries
- Multiple parsing methods (BeautifulSoup, lxml, html5lib)
- Selenium fallback for JavaScript-heavy sites
- Request headers rotation
- Retry logic with exponential backoff
"""

import cloudscraper
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote_plus, unquote
import time
import random
import json
import re
import wikipedia
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass, asdict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ScrapedData:
    """Data structure for scraped content"""
    url: str
    title: str
    content: str
    meta_description: Optional[str] = None
    links: List[str] = None
    images: List[str] = None
    source: str = "direct"
    
    def to_dict(self):
        return asdict(self)


class AdvancedWebScraper:
    """Advanced web scraper with anti-bot bypass capabilities"""
    
    def __init__(self, use_selenium: bool = False):
        """
        Initialize the scraper
        
        Args:
            use_selenium: Whether to use Selenium for JavaScript rendering
        """
        self.use_selenium = use_selenium
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # Rotating user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        self.driver = None
        if use_selenium:
            self._setup_selenium()
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver with headless Chrome"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument(f'user-agent={random.choice(self.user_agents)}')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Selenium WebDriver initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Selenium: {e}")
            self.driver = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get randomized headers for requests"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def _fetch_with_cloudscraper(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Fetch URL using cloudscraper (bypasses Cloudflare)"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching {url} with cloudscraper (attempt {attempt + 1}/{max_retries})")
                response = self.scraper.get(url, headers=self._get_headers(), timeout=30)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.warning(f"Cloudscraper attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt + random.uniform(0, 1))
        return None
    
    def _fetch_with_selenium(self, url: str) -> Optional[str]:
        """Fetch URL using Selenium (for JavaScript-heavy sites)"""
        if not self.driver:
            logger.warning("Selenium not initialized")
            return None
        
        try:
            logger.info(f"Fetching {url} with Selenium")
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)  # Wait for dynamic content
            return self.driver.page_source
        except TimeoutException:
            logger.warning(f"Selenium timeout for {url}")
            return None
        except Exception as e:
            logger.error(f"Selenium error: {e}")
            return None
    
    def _fetch_content(self, url: str) -> Optional[str]:
        """Fetch content with multiple fallback methods"""
        # Try cloudscraper first
        html = self._fetch_with_cloudscraper(url)
        
        # Fallback to Selenium if enabled and cloudscraper failed
        if not html and self.use_selenium:
            html = self._fetch_with_selenium(url)
        
        return html
    
    def _parse_html(self, html: str, parser: str = 'lxml') -> BeautifulSoup:
        """Parse HTML with specified parser"""
        try:
            return BeautifulSoup(html, parser)
        except Exception as e:
            logger.warning(f"Parser {parser} failed: {e}, falling back to html.parser")
            return BeautifulSoup(html, 'html.parser')
    
    def _extract_content(self, soup: BeautifulSoup, url: str) -> ScrapedData:
        """Extract relevant content from parsed HTML"""
        # Extract title
        title = ""
        if soup.title:
            title = soup.title.string
        elif soup.find('h1'):
            title = soup.find('h1').get_text(strip=True)
        else:
            title = urlparse(url).netloc
        
        # Extract meta description
        meta_desc = None
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if not meta_tag:
            meta_tag = soup.find('meta', attrs={'property': 'og:description'})
        if meta_tag:
            meta_desc = meta_tag.get('content', '')
        
        # Extract main content
        # Remove script, style, and navigation elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try to find main content area
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article', re.I))
        
        if main_content:
            content = main_content.get_text(separator='\n', strip=True)
        else:
            # Fallback to body
            content = soup.get_text(separator='\n', strip=True)
        
        # Clean up content
        content = re.sub(r'\n\s*\n+', '\n\n', content)  # Remove excessive newlines
        content = content.strip()
        
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http'):
                links.append(href)
        
        # Extract images
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            if src.startswith('http'):
                images.append(src)
        
        return ScrapedData(
            url=url,
            title=title,
            content=content[:5000],  # Limit content length
            meta_description=meta_desc,
            links=links[:20],  # Limit links
            images=images[:10],  # Limit images
            source="direct"
        )
    
    def scrape_url(self, url: str) -> Optional[ScrapedData]:
        """Scrape a single URL"""
        logger.info(f"Scraping URL: {url}")
        
        html = self._fetch_content(url)
        if not html:
            logger.error(f"Failed to fetch content from {url}")
            return None
        
        soup = self._parse_html(html)
        return self._extract_content(soup, url)
    
    def _search_duckduckgo(self, query: str, num_results: int = 5) -> List[str]:
        """Search using DuckDuckGo (more scraper-friendly)"""
        logger.info(f"Searching DuckDuckGo for: {query}")
        
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        
        try:
            html = self._fetch_with_cloudscraper(search_url)
            if not html:
                return []
            
            soup = self._parse_html(html)
            urls = []
            
            # DuckDuckGo uses different classes, try multiple patterns
            # Pattern 1: Links with result__a class
            for link in soup.find_all('a', class_='result__a', href=True):
                url = link['href']
                if url.startswith('http') and 'duckduckgo.com' not in url:
                    urls.append(url)
                    if len(urls) >= num_results:
                        break
            
            # Pattern 2: Try result__url class if first pattern failed
            if not urls:
                for link in soup.find_all('a', class_='result__url', href=True):
                    url = link['href']
                    if url.startswith('http') and 'duckduckgo.com' not in url:
                        urls.append(url)
                        if len(urls) >= num_results:
                            break
            
            # Pattern 3: Look for any links in result divs
            if not urls:
                for result_div in soup.find_all('div', class_='result'):
                    links = result_div.find_all('a', href=True)
                    for link in links:
                        url = link.get('href', '')
                        # DuckDuckGo sometimes wraps URLs
                        if '//duckduckgo.com/l/?uddg=' in url:
                            # Extract actual URL from redirect
                            import re
                            match = re.search(r'uddg=([^&]+)', url)
                            if match:
                                url = unquote(match.group(1))
                        
                        if url.startswith('http') and 'duckduckgo.com' not in url:
                            urls.append(url)
                            if len(urls) >= num_results:
                                break
                    if len(urls) >= num_results:
                        break
            
            logger.info(f"DuckDuckGo found {len(urls)} results")
            return urls
        
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
            return []
    
    def _search_searxng(self, query: str, num_results: int = 5) -> List[str]:
        """Search using SearXNG (open meta-search engine)"""
        logger.info(f"Searching SearXNG for: {query}")
        
        # Use a public SearXNG instance
        search_url = f"https://searx.be/search?q={quote_plus(query)}&format=json"
        
        try:
            logger.debug(f"SearXNG URL: {search_url}")
            response = self.scraper.get(search_url, headers=self._get_headers(), timeout=10)
            logger.debug(f"SearXNG response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"SearXNG JSON response keys: {data.keys()}")
                
                results = data.get('results', [])
                logger.debug(f"SearXNG found {len(results)} results in JSON")
                
                urls = []
                for result in results[:num_results]:
                    url = result.get('url', '')
                    if url and url.startswith('http'):
                        urls.append(url)
                        logger.debug(f"SearXNG result: {url}")
                
                logger.info(f"SearXNG found {len(urls)} valid results")
                return urls
            else:
                logger.warning(f"SearXNG returned status {response.status_code}")
        except requests.exceptions.JSONDecodeError as e:
            logger.warning(f"SearXNG JSON decode error: {e}")
            logger.debug(f"Response text: {response.text[:500]}")
        except Exception as e:
            logger.warning(f"SearXNG search failed: {e}")
            logger.debug(f"Exception type: {type(e).__name__}")
        
        return []
    
    def _search_brave(self, query: str, num_results: int = 5) -> List[str]:
        """Search using Brave Search (privacy-focused, scraper-friendly)"""
        logger.info(f"Searching Brave for: {query}")
        
        search_url = f"https://search.brave.com/search?q={quote_plus(query)}"
        
        try:
            html = self._fetch_with_cloudscraper(search_url)
            if not html:
                return []
            
            soup = self._parse_html(html)
            urls = []
            
            # Brave uses various result containers
            # Try multiple patterns
            patterns = [
                ('div', {'class': 'snippet'}),
                ('div', {'data-type': 'web'}),
                ('a', {'class': 'result-header'}),
            ]
            
            for tag, attrs in patterns:
                for result in soup.find_all(tag, attrs):
                    # Find links in result
                    link = result.find('a', href=True) if tag != 'a' else result
                    if link:
                        url = link.get('href', '')
                        # Clean and validate URL
                        if url.startswith('http') and 'brave.com' not in url:
                            if url not in urls:  # Avoid duplicates
                                urls.append(url)
                                if len(urls) >= num_results:
                                    break
                
                if len(urls) >= num_results:
                    break
            
            # Fallback: find any external links
            if not urls:
                for link in soup.find_all('a', href=True):
                    url = link.get('href', '')
                    if (url.startswith('http') and 
                        'brave.com' not in url and 
                        'javascript:' not in url and
                        len(url) > 20):  # Filter out short/suspicious URLs
                        if url not in urls:
                            urls.append(url)
                            if len(urls) >= num_results:
                                break
            
            logger.info(f"Brave found {len(urls)} results")
            return urls
        
        except Exception as e:
            logger.warning(f"Brave search failed: {e}")
            return []
    
    def _search_google_fallback(self, query: str, num_results: int = 5) -> List[str]:
        """
        Attempt Google search with multiple strategies
        Note: Google actively blocks scrapers, so this may not work
        """
        logger.info(f"Attempting Google search for: {query}")
        
        # Try different Google URLs
        urls_to_try = [
            f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}",
            f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}&gl=us&hl=en",
        ]
        
        for search_url in urls_to_try:
            try:
                html = self._fetch_with_cloudscraper(search_url)
                if not html:
                    continue
                
                soup = self._parse_html(html)
                found_urls = []
                
                # Try multiple selectors for Google's changing structure
                # Pattern 1: Classic result divs
                for result in soup.find_all('div', class_='g'):
                    link = result.find('a', href=True)
                    if link:
                        url = link['href']
                        if url.startswith('http') and 'google.com' not in url:
                            found_urls.append(url)
                            if len(found_urls) >= num_results:
                                break
                
                # Pattern 2: Look for h3 tags (often contain result titles)
                if not found_urls:
                    for h3 in soup.find_all('h3'):
                        parent = h3.find_parent('a', href=True)
                        if parent:
                            url = parent['href']
                            if url.startswith('http') and 'google.com' not in url:
                                if url not in found_urls:
                                    found_urls.append(url)
                                    if len(found_urls) >= num_results:
                                        break
                
                # Pattern 3: Find all links and filter
                if not found_urls:
                    for link in soup.find_all('a', href=True):
                        url = link['href']
                        # Google result URLs are clean HTTP(S) links
                        if (url.startswith('http') and 
                            'google.com' not in url and
                            '/search?' not in url and
                            'javascript:' not in url and
                            len(url) > 20):
                            if url not in found_urls:
                                found_urls.append(url)
                                if len(found_urls) >= num_results:
                                    break
                
                if found_urls:
                    logger.info(f"Google found {len(found_urls)} results")
                    return found_urls
            
            except Exception as e:
                logger.warning(f"Google search attempt failed: {e}")
                continue
        
        return []
    
    def search_web(self, query: str, num_results: int = 5) -> List[str]:
        """
        Search the web and return top result URLs
        Tries multiple search engines: SearXNG -> DuckDuckGo -> Brave -> Google
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of URLs
            
        Note: If all search engines fail (due to anti-bot measures or network restrictions), consider:
              1. Using Wikipedia only (usually works well for research)
              2. Providing direct URLs instead of search terms
              3. Using API-based search services (Google Custom Search, Bing API)
              4. Enabling network access if running in a restricted environment
        """
        # Try SearXNG first (uses JSON API, most reliable)
        try:
            urls = self._search_searxng(query, num_results)
            if urls:
                return urls
        except Exception as e:
            logger.warning(f"SearXNG exception: {e}")
        
        # Try DuckDuckGo
        logger.info("SearXNG failed, trying DuckDuckGo...")
        try:
            urls = self._search_duckduckgo(query, num_results)
            if urls:
                return urls
        except Exception as e:
            logger.warning(f"DuckDuckGo exception: {e}")
        
        # Try Brave as fallback
        logger.info("DuckDuckGo failed, trying Brave...")
        try:
            urls = self._search_brave(query, num_results)
            if urls:
                return urls
        except Exception as e:
            logger.warning(f"Brave exception: {e}")
        
        # Try Google as last resort
        logger.info("Brave failed, trying Google...")
        try:
            urls = self._search_google_fallback(query, num_results)
            if urls:
                return urls
        except Exception as e:
            logger.warning(f"Google exception: {e}")
        
        logger.error("All search engines failed - possible causes:")
        logger.error("  1. Network access is disabled or restricted")
        logger.error("  2. Search engines are blocking automated requests")
        logger.error("  3. Anti-bot protections are too strong")
        logger.info("Suggestions:")
        logger.info("  - Use Wikipedia summary (often works even with network restrictions)")
        logger.info("  - Provide direct URLs instead of search queries")
        logger.info("  - Enable network access in environment settings")
        logger.info("  - Use API-based search services with authentication")
        return []
    
    def google_search(self, query: str, num_results: int = 5) -> List[str]:
        """
        Search the web using multiple search engines
        Alias for search_web() - kept for backward compatibility
        """
        return self.search_web(query, num_results)
    
    def get_wikipedia_summary(self, topic: str) -> Optional[ScrapedData]:
        """
        Get Wikipedia summary for a topic
        
        Args:
            topic: Topic to search
            
        Returns:
            ScrapedData object with Wikipedia content
        """
        logger.info(f"Fetching Wikipedia summary for: {topic}")
        
        try:
            # Set language to English
            wikipedia.set_lang("en")
            
            # Search for the topic
            search_results = wikipedia.search(topic, results=1)
            if not search_results:
                logger.warning(f"No Wikipedia results for: {topic}")
                return None
            
            # Get the page
            page = wikipedia.page(search_results[0], auto_suggest=False)
            
            return ScrapedData(
                url=page.url,
                title=page.title,
                content=page.summary,
                meta_description=page.summary[:200] + "...",
                links=[page.url],
                images=page.images[:5] if hasattr(page, 'images') else [],
                source="wikipedia"
            )
        
        except wikipedia.exceptions.DisambiguationError as e:
            logger.warning(f"Disambiguation page found, using first option: {e.options[0]}")
            try:
                page = wikipedia.page(e.options[0])
                return ScrapedData(
                    url=page.url,
                    title=page.title,
                    content=page.summary,
                    meta_description=page.summary[:200] + "...",
                    links=[page.url],
                    images=page.images[:5] if hasattr(page, 'images') else [],
                    source="wikipedia"
                )
            except Exception as e2:
                logger.error(f"Failed to fetch disambiguation page: {e2}")
                return None
        
        except Exception as e:
            logger.error(f"Wikipedia error: {e}")
            return None
    
    def scrape_topic(self, topic: str, num_sites: int = 3, include_wikipedia: bool = True) -> List[ScrapedData]:
        """
        Scrape multiple sources for a topic
        
        Args:
            topic: Topic to search and scrape
            num_sites: Number of websites to scrape from search results
            include_wikipedia: Whether to include Wikipedia summary
            
        Returns:
            List of ScrapedData objects
        """
        results = []
        
        # Get Wikipedia summary
        if include_wikipedia:
            wiki_data = self.get_wikipedia_summary(topic)
            if wiki_data:
                results.append(wiki_data)
        
        # Search web and scrape top results
        urls = self.search_web(topic, num_results=num_sites)
        
        for url in urls:
            try:
                data = self.scrape_url(url)
                if data:
                    results.append(data)
                time.sleep(random.uniform(1, 3))  # Be polite
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")
                continue
        
        return results
    
    def save_results(self, results: List[ScrapedData], output_file: str = "scraped_data.json"):
        """Save scraped results to JSON and HTML files"""
        # Save JSON
        data = [result.to_dict() for result in results]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(results)} results to {output_file}")
        
        # Also save HTML
        html_file = output_file.replace('.json', '.html')
        if html_file == output_file:  # If not .json extension, add .html
            html_file = output_file + '.html'
        
        self.save_results_html(results, html_file)
        logger.info(f"Saved HTML report to {html_file}")
    
    def save_results_html(self, results: List[ScrapedData], output_file: str = "scraped_data.html"):
        """Save scraped results to a beautiful, responsive HTML file with theme support"""
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Scraping Results</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg-primary: #ffffff;
            --bg-secondary: #f8f9fa;
            --bg-card: #ffffff;
            --text-primary: #212529;
            --text-secondary: #6c757d;
            --text-muted: #adb5bd;
            --border-color: #dee2e6;
            --accent-color: #0d6efd;
            --accent-hover: #0b5ed7;
            --shadow: rgba(0, 0, 0, 0.1);
            --code-bg: #f8f9fa;
        }

        [data-theme="dark"] {
            --bg-primary: #1a1a1a;
            --bg-secondary: #242424;
            --bg-card: #2d2d2d;
            --text-primary: #e9ecef;
            --text-secondary: #adb5bd;
            --text-muted: #6c757d;
            --border-color: #3d3d3d;
            --accent-color: #4a9eff;
            --accent-hover: #66b0ff;
            --shadow: rgba(0, 0, 0, 0.3);
            --code-bg: #1e1e1e;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            transition: background-color 0.3s ease, color 0.3s ease;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }

        header {
            background: var(--bg-card);
            border-bottom: 2px solid var(--border-color);
            padding: 1.5rem 0;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px var(--shadow);
            position: sticky;
            top: 0;
            z-index: 100;
            transition: all 0.3s ease;
        }

        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }

        h1 {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .results-count {
            background: var(--accent-color);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.875rem;
            font-weight: 600;
        }

        .theme-toggle {
            background: var(--bg-secondary);
            border: 2px solid var(--border-color);
            border-radius: 2rem;
            padding: 0.5rem 1rem;
            font-size: 1rem;
            color: var(--text-primary);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 500;
        }

        @media (pointer: fine) {
            .theme-toggle {
                cursor: pointer;
            }
            
            .theme-toggle:hover {
                background: var(--accent-color);
                color: white;
                border-color: var(--accent-color);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px var(--shadow);
            }
        }

        .theme-toggle:active {
            transform: translateY(0);
        }

        .card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 1rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px var(--shadow);
            transition: all 0.3s ease;
        }

        @media (pointer: fine) {
            .card:hover {
                transform: translateY(-4px);
                box-shadow: 0 8px 24px var(--shadow);
                border-color: var(--accent-color);
            }
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }

        .card-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            line-height: 1.3;
        }

        .source-badge {
            background: var(--bg-secondary);
            color: var(--text-secondary);
            padding: 0.375rem 0.875rem;
            border-radius: 0.5rem;
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            white-space: nowrap;
        }

        .source-badge.wikipedia {
            background: #e8f4f8;
            color: #0d6efd;
        }

        [data-theme="dark"] .source-badge.wikipedia {
            background: #1a3a4a;
            color: #4a9eff;
        }

        .source-badge.direct {
            background: #f0f0f0;
            color: #495057;
        }

        [data-theme="dark"] .source-badge.direct {
            background: #383838;
            color: #adb5bd;
        }

        .card-url {
            color: var(--accent-color);
            text-decoration: none;
            font-size: 0.9rem;
            word-break: break-all;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }

        @media (pointer: fine) {
            .card-url {
                cursor: pointer;
            }
            
            .card-url:hover {
                color: var(--accent-hover);
                text-decoration: underline;
            }
        }

        .card-meta {
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-bottom: 1rem;
            font-style: italic;
        }

        .card-content {
            color: var(--text-primary);
            line-height: 1.8;
            white-space: pre-wrap;
            background: var(--bg-secondary);
            padding: 1.25rem;
            border-radius: 0.75rem;
            border-left: 4px solid var(--accent-color);
            max-height: 500px;
            overflow-y: auto;
        }

        .card-content::-webkit-scrollbar {
            width: 8px;
        }

        .card-content::-webkit-scrollbar-track {
            background: var(--bg-primary);
            border-radius: 4px;
        }

        .card-content::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }

        @media (pointer: fine) {
            .card-content::-webkit-scrollbar-thumb:hover {
                background: var(--text-muted);
            }
        }

        .links-section, .images-section {
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border-color);
        }

        .section-title {
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .links-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .link-item {
            background: var(--bg-secondary);
            color: var(--accent-color);
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            text-decoration: none;
            font-size: 0.875rem;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
            display: inline-block;
        }

        @media (pointer: fine) {
            .link-item {
                cursor: pointer;
            }
            
            .link-item:hover {
                background: var(--accent-color);
                color: white;
                border-color: var(--accent-color);
                transform: translateY(-2px);
            }
        }

        .images-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .image-item {
            border-radius: 0.5rem;
            overflow: hidden;
            border: 2px solid var(--border-color);
            transition: all 0.3s ease;
            aspect-ratio: 1;
            background: var(--bg-secondary);
        }

        @media (pointer: fine) {
            .image-item {
                cursor: pointer;
            }
            
            .image-item:hover {
                transform: scale(1.05);
                border-color: var(--accent-color);
                box-shadow: 0 8px 16px var(--shadow);
            }
        }

        .image-item img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        footer {
            text-align: center;
            padding: 2rem 1rem;
            color: var(--text-muted);
            font-size: 0.875rem;
            border-top: 1px solid var(--border-color);
            margin-top: 3rem;
        }

        .no-results {
            text-align: center;
            padding: 4rem 2rem;
            color: var(--text-secondary);
            font-size: 1.25rem;
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 1.5rem;
            }

            .card {
                padding: 1.25rem;
            }

            .card-title {
                font-size: 1.25rem;
            }

            .container {
                padding: 1rem 0.5rem;
            }

            .images-grid {
                grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            }
        }

        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <h1>
                🔍 Web Scraping Results
                <span class="results-count" id="resultsCount">0</span>
            </h1>
            <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">
                <span id="themeIcon">🌙</span>
                <span id="themeText">Dark</span>
            </button>
        </div>
    </header>

    <div class="container" id="resultsContainer">
        <!-- Results will be inserted here -->
    </div>

    <footer>
        <p>Generated by Advanced Web Scraper | """ + time.strftime("%Y-%m-%d %H:%M:%S") + """</p>
    </footer>

    <script>
        // Theme Management
        const themeToggle = document.getElementById('themeToggle');
        const themeIcon = document.getElementById('themeIcon');
        const themeText = document.getElementById('themeText');
        const html = document.documentElement;

        // Check for saved theme preference or default to browser preference
        function getInitialTheme() {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme) {
                return savedTheme;
            }
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }

        // Set theme
        function setTheme(theme) {
            html.setAttribute('data-theme', theme);
            if (theme === 'dark') {
                themeIcon.textContent = '☀️';
                themeText.textContent = 'Light';
            } else {
                themeIcon.textContent = '🌙';
                themeText.textContent = 'Dark';
            }
        }

        // Initialize theme
        setTheme(getInitialTheme());

        // Toggle theme
        themeToggle.addEventListener('click', () => {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });

        // Listen for system theme changes (only if user hasn't manually set theme)
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                setTheme(e.matches ? 'dark' : 'light');
            }
        });

        // Results data
        const results = """ + json.dumps([result.to_dict() for result in results], ensure_ascii=False) + """;

        // Render results
        const container = document.getElementById('resultsContainer');
        const resultsCount = document.getElementById('resultsCount');
        
        resultsCount.textContent = results.length;

        if (results.length === 0) {
            container.innerHTML = '<div class="no-results">No results to display</div>';
        } else {
            results.forEach((result, index) => {
                const card = document.createElement('div');
                card.className = 'card';
                
                let content = `
                    <div class="card-header">
                        <div>
                            <h2 class="card-title">${escapeHtml(result.title)}</h2>
                            <a href="${escapeHtml(result.url)}" target="_blank" rel="noopener noreferrer" class="card-url">
                                🔗 ${escapeHtml(result.url)}
                            </a>
                        </div>
                        <span class="source-badge ${result.source}">${result.source}</span>
                    </div>
                `;

                if (result.meta_description) {
                    content += `<div class="card-meta">${escapeHtml(result.meta_description)}</div>`;
                }

                content += `<div class="card-content">${escapeHtml(result.content)}</div>`;

                if (result.links && result.links.length > 0) {
                    content += `
                        <div class="links-section">
                            <div class="section-title">📎 Related Links (${result.links.length})</div>
                            <div class="links-list">
                                ${result.links.slice(0, 10).map(link => 
                                    `<a href="${escapeHtml(link)}" target="_blank" rel="noopener noreferrer" class="link-item">
                                        ${getDomain(link)}
                                    </a>`
                                ).join('')}
                            </div>
                        </div>
                    `;
                }

                if (result.images && result.images.length > 0) {
                    content += `
                        <div class="images-section">
                            <div class="section-title">🖼️ Images (${result.images.length})</div>
                            <div class="images-grid">
                                ${result.images.map(img => 
                                    `<div class="image-item">
                                        <img src="${escapeHtml(img)}" alt="Image" loading="lazy" onerror="this.parentElement.style.display='none'">
                                    </div>`
                                ).join('')}
                            </div>
                        </div>
                    `;
                }

                card.innerHTML = content;
                container.appendChild(card);
            });
        }

        // Helper functions
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function getDomain(url) {
            try {
                const domain = new URL(url).hostname;
                return domain.replace('www.', '');
            } catch {
                return url;
            }
        }
    </script>
</body>
</html>"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Saved {len(results)} results to {output_file}")
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver closed")


def main():
    """Main function demonstrating scraper usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced Web Scraper')
    parser.add_argument('input', help='URL to scrape or topic to search')
    parser.add_argument('-t', '--topic', action='store_true', 
                       help='Treat input as topic (search web using multiple engines and Wikipedia)')
    parser.add_argument('-n', '--num-sites', type=int, default=3,
                       help='Number of sites to scrape for topics (default: 3)')
    parser.add_argument('-s', '--selenium', action='store_true',
                       help='Use Selenium for JavaScript rendering')
    parser.add_argument('-o', '--output', default='scraped_data.json',
                       help='Output JSON file (default: scraped_data.json)')
    parser.add_argument('--no-wikipedia', action='store_true',
                       help='Skip Wikipedia summary for topics')
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = AdvancedWebScraper(use_selenium=args.selenium)
    
    try:
        if args.topic:
            # Scrape topic from multiple sources
            logger.info(f"Scraping topic: {args.input}")
            results = scraper.scrape_topic(
                args.input, 
                num_sites=args.num_sites,
                include_wikipedia=not args.no_wikipedia
            )
        else:
            # Scrape single URL
            logger.info(f"Scraping URL: {args.input}")
            result = scraper.scrape_url(args.input)
            results = [result] if result else []
        
        # Display results
        print("\n" + "="*80)
        print(f"SCRAPED {len(results)} SOURCES")
        print("="*80 + "\n")
        
        for i, result in enumerate(results, 1):
            print(f"\n[{i}] {result.title}")
            print(f"Source: {result.source}")
            print(f"URL: {result.url}")
            print(f"\nContent Preview:")
            print("-" * 80)
            print(result.content[:500] + "..." if len(result.content) > 500 else result.content)
            print("-" * 80)
        
        # Save results
        if results:
            scraper.save_results(results, args.output)
            print(f"\n✓ Results saved to {args.output} and HTML report")
        else:
            print("\n✗ No results to save")
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()



