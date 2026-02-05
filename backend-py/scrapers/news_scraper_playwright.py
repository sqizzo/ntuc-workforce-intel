"""
News Search Scraper with JavaScript support using Playwright
More efficient and reliable than Selenium (~50-100MB RAM)
"""
import time
import random
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout


class NewsSearchScraperPlaywright:
    """Lightweight scraper with JavaScript support using Playwright"""
    
    def __init__(self, max_articles: int = 10, general_sources: list = None, company_sources: list = None):
        self.max_articles = max_articles
        self.general_sources = general_sources or []
        self.company_sources = company_sources or []
        self.playwright = None
        self.browser = None
        self.page = None
        
    def setup_browser(self):
        """Initialize Playwright browser"""
        if not self.playwright:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=True)
            self.page = self.browser.new_page()
            print("✓ Playwright browser initialized")
    
    def close_browser(self):
        """Close browser and cleanup"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("✓ Browser closed")
    
    def extract_article_links(self, search_url: str, wait_for_js: bool = False) -> List[Dict[str, str]]:
        """Extract article links from search results page"""
        print(f"\n🔍 Loading search results: {search_url}")
        
        try:
            self.setup_browser()
            
            # Use 'domcontentloaded' instead of 'networkidle' - faster and more reliable
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
            
            if wait_for_js:
                print("⚙️ Waiting for JavaScript to load...")
                # Wait for content to appear
                try:
                    self.page.wait_for_selector('a[href*="/singapore"], a[href*="/business"], a[href*="/article"]', timeout=5000)
                except:
                    pass  # Continue even if selector not found
                time.sleep(2)  # Additional wait for dynamic content
            
            article_data = []
            seen_urls = set()
            
            # Get all links
            links = self.page.query_selector_all('a')
            
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if not href:
                        continue
                    
                    # Make absolute URL
                    url = urljoin(search_url, href)
                    
                    # Get title
                    title = link.text_content().strip()
                    
                    # Check if it looks like an article URL
                    is_article = any(pattern in href for pattern in [
                        '/singapore/', '/asia/', '/world/', '/business/', 
                        '/opinion/', '/life/', '/sport/',
                        '/article/', '/news/', '/story/'
                    ])
                    
                    # Filter criteria
                    if (is_article and
                        url not in seen_urls and
                        '/search' not in url and
                        '/tag/' not in url and
                        '/category/' not in url and
                        len(title) > 20):
                        
                        seen_urls.add(url)
                        article_data.append({
                            'url': url,
                            'previewTitle': title
                        })
                        
                        if len(article_data) >= self.max_articles:
                            break
                except:
                    continue
            
            print(f"✓ Found {len(article_data)} article links")
            return article_data[:self.max_articles]
            
        except Exception as e:
            print(f"✗ Error extracting links from {search_url}: {e}")
            return []
    
    def scrape_article_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape content from a single article"""
        try:
            print(f"📄 Scraping: {url}")
            self.setup_browser()
            self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # Wait for article content to load
            try:
                self.page.wait_for_selector('article, h1', timeout=3000)
            except:
                pass
            
            time.sleep(1)
            
            # Extract title
            title = ""
            try:
                title_el = self.page.query_selector('h1')
                if title_el:
                    title = title_el.text_content().strip()
            except:
                pass
            
            # Extract author
            author = ""
            author_selectors = ['[rel="author"]', '.author', '.byline', '.article-author']
            for selector in author_selectors:
                try:
                    author_el = self.page.query_selector(selector)
                    if author_el:
                        author = author_el.text_content().strip()
                        break
                except:
                    continue
            
            # Extract date
            date = ""
            try:
                time_el = self.page.query_selector('time')
                if time_el:
                    date = time_el.get_attribute('datetime') or time_el.text_content().strip()
            except:
                pass
            
            if not date:
                date_selectors = ['.date', '.publish-date', '[class*="date"]']
                for selector in date_selectors:
                    try:
                        date_el = self.page.query_selector(selector)
                        if date_el:
                            date = date_el.text_content().strip()
                            break
                    except:
                        continue
            
            # Extract content
            content = ""
            content_selectors = ['article', '[class*="article-body"]', '[class*="content"]', 'main']
            
            for selector in content_selectors:
                try:
                    content_el = self.page.query_selector(selector)
                    if content_el:
                        paragraphs = content_el.query_selector_all('p')
                        content = ' '.join([
                            p.text_content().strip() 
                            for p in paragraphs 
                            if len(p.text_content().strip()) > 30
                        ])
                        if len(content) > 200:
                            break
                except:
                    continue
            
            article_data = {
                'title': title,
                'author': author,
                'date': date,
                'content': content,
                'url': url
            }
            
            if content:
                print(f"✓ Scraped: {title[:50]}...")
                return article_data
            else:
                print(f"⚠ No content found for: {url}")
                return None
                
        except Exception as e:
            print(f"✗ Error scraping {url}: {str(e)}")
            return None
    
    def scrape_general_sources(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Scrape from general configured news sources"""
        signals = []
        
        if not self.general_sources:
            return signals
        
        print(f"\n📰 Scraping general news sources for keywords: {keywords}")
        
        for source in self.general_sources:
            if not source.get('enabled', True):
                continue
                
            print(f"\n🌐 Scraping: {source['name']}")
            
            try:
                # Get article links
                article_links = self.extract_article_links(source['url'], wait_for_js=False)
                print(f"📝 Found {len(article_links)} articles to check")
                
                # Scrape and filter by keywords
                for link_data in article_links[:self.max_articles * 2]:
                    article = self.scrape_article_content(link_data['url'])
                    if article and article.get('content'):
                        content_lower = (article['title'] + ' ' + article['content']).lower()
                        if any(kw.lower() in content_lower for kw in keywords):
                            signals.append({
                                'type': 'news_article',
                                'source': source['name'],
                                'source_url': source['url'],
                                **article
                            })
                            print(f"✓ Matched keyword in: {article['title'][:50]}...")
                    
                    if len(signals) >= self.max_articles:
                        break
                        
            except Exception as e:
                print(f"✗ Error with source {source['name']}: {e}")
                continue
        
        return signals
    
    def scrape_company_search(self, company_name: str) -> List[Dict[str, Any]]:
        """Search and scrape company-specific news with JS rendering"""
        signals = []
        
        if not self.company_sources:
            print("⚠ No company search sources configured")
            return signals
        
        print(f"\n🔍 Searching company news for: {company_name}")
        
        # Calculate articles per source
        articles_per_source = max(2, self.max_articles // len(self.company_sources))
        
        for source in self.company_sources:
            if not source.get('enabled', True):
                continue
            
            search_url = source['search_url'].replace('{query}', company_name.replace(' ', '+'))
            print(f"\n🌐 Searching: {source['name']}")
            
            # Get article links with JS rendering
            article_links = self.extract_article_links(search_url, wait_for_js=True)
            
            # Scrape each article (limit per source)
            source_count = 0
            for link_data in article_links:
                if source_count >= articles_per_source:
                    break
                    
                article = self.scrape_article_content(link_data['url'])
                if article:
                    signals.append({
                        'type': 'company_news',
                        'source': source['name'],
                        'search_query': company_name,
                        **article
                    })
                    source_count += 1
        
        return signals[:self.max_articles]  # Final limit
    
    def scrape(self, mode: str = "general", query: Optional[str] = None, keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """Main scraping method"""
        signals = []
        
        try:
            if mode == "general" and keywords:
                signals = self.scrape_general_sources(keywords)
            elif mode == "company" and query:
                signals = self.scrape_company_search(query)
            else:
                print("⚠ Invalid mode or missing parameters")
        finally:
            self.close_browser()
        
        return {
            'mode': mode,
            'query': query or 'N/A',
            'keywords': keywords or [],
            'signals': signals,
            'total_signals': len(signals)
        }
    
    def search_workforce_signals_company(self, company_name: str, before_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for company-specific news using configured search URLs
        Compatible with main.py API
        
        Args:
            company_name: Name of the company to search for
            before_date: Filter articles before this date (YYYY-MM-DD) - currently not implemented
            
        Returns:
            List of workforce signals from company-specific searches
        """
        from datetime import datetime
        from urllib.parse import urlparse
        import time
        import random
        
        signals = []
        
        if not self.company_sources:
            print("No company search sources configured")
            return signals
        
        try:
            print(f"Searching for '{company_name}' across {len(self.company_sources)} sources...")
            
            # Use scrape_company_search method
            article_results = self.scrape_company_search(company_name)
            
            # Convert to workforce signals format
            for idx, article in enumerate(article_results):
                signals.append({
                    'id': f'signal-company-{int(time.time())}-{idx}',
                    'source_type': 'news',
                    'source_name': article.get('source', 'Unknown'),
                    'source_url': article['url'],
                    'ingestion_timestamp': datetime.now().isoformat(),
                    'extracted_text': article.get('content', '')[:500],
                    'matched_keywords': [company_name],
                    'inferred_workforce_theme': 'company_news',
                    'company_name': company_name,
                    'metadata': {
                        'title': article.get('title', ''),
                        'author': article.get('author', ''),
                        'publish_date': article.get('date', ''),
                        'company_search': True,
                        'full_content': article.get('content', '')
                    }
                })
            
            return signals
            
        except Exception as e:
            print(f"⚠ Company search failed: {e}")
            return signals

