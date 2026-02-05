"""
News Search Scraper with JavaScript support using Playwright Async API
Designed for FastAPI async endpoints - no ThreadPoolExecutor needed
"""
import asyncio
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout
from datetime import datetime
import time
import random


class NewsSearchScraperAsync:
    """Async scraper with JavaScript support using Playwright"""
    
    def __init__(self, max_articles: int = 10, general_sources: list = None, company_sources: list = None):
        self.max_articles = max_articles
        self.general_sources = general_sources or []
        self.company_sources = company_sources or []
        self.playwright = None
        self.browser = None
        
    async def setup_browser(self):
        """Initialize Playwright browser"""
        if not self.playwright:
            print("🌐 Initializing Playwright...")
            self.playwright = await async_playwright().start()
            print("🚀 Launching Chromium...")
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            print("✓ Playwright browser initialized (async)")
    
    async def close_browser(self):
        """Close browser and cleanup"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("✓ Browser closed")
    
    async def extract_article_links(self, search_url: str, wait_for_js: bool = False) -> List[Dict[str, str]]:
        """Extract article links from search results page"""
        print(f"\n🔍 Loading search results: {search_url}")
        
        try:
            await self.setup_browser()
            page = await self.browser.new_page()
            
            await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
            
            if wait_for_js:
                print("⚙️ Waiting for JavaScript to load...")
                try:
                    await page.wait_for_selector('a[href*="/singapore"], a[href*="/business"]', timeout=5000)
                except:
                    pass
                await asyncio.sleep(2)
            
            article_data = []
            seen_urls = set()
            
            links = await page.query_selector_all('a')
            
            for link in links:
                try:
                    href = await link.get_attribute('href')
                    if not href:
                        continue
                    
                    url = urljoin(search_url, href)
                    title = (await link.text_content()).strip()
                    
                    is_article = any(pattern in href for pattern in [
                        '/singapore/', '/asia/', '/world/', '/business/',
                        '/opinion/', '/life/', '/sport/', '/article/', '/news/'
                    ])
                    
                    if (is_article and url not in seen_urls and '/search' not in url and
                        '/tag/' not in url and len(title) > 20):
                        seen_urls.add(url)
                        article_data.append({'url': url, 'previewTitle': title})
                        
                        if len(article_data) >= self.max_articles:
                            break
                except:
                    continue
            
            await page.close()
            print(f"✓ Found {len(article_data)} article links")
            return article_data[:self.max_articles]
            
        except Exception as e:
            print(f"✗ Error extracting links: {e}")
            return []
    
    async def scrape_article_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape content from a single article"""
        try:
            print(f"📄 Scraping: {url}")
            await self.setup_browser()
            page = await self.browser.new_page()
            
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            try:
                await page.wait_for_selector('article, h1', timeout=3000)
            except:
                pass
            
            # Extract title
            title = ""
            try:
                title_el = await page.query_selector('h1')
                if title_el:
                    title = (await title_el.text_content()).strip()
            except:
                pass
            
            # Extract content
            content = ""
            for selector in ['article', '[class*="article-body"]', 'main']:
                try:
                    content_el = await page.query_selector(selector)
                    if content_el:
                        paragraphs = await content_el.query_selector_all('p')
                        texts = []
                        for p in paragraphs:
                            text = (await p.text_content()).strip()
                            if len(text) > 30:
                                texts.append(text)
                        content = ' '.join(texts)
                        if len(content) > 200:
                            break
                except:
                    continue
            
            await page.close()
            
            if content:
                print(f"✓ Scraped: {title[:50]}...")
                return {'title': title, 'content': content, 'url': url, 'author': '', 'date': ''}
            return None
                
        except Exception as e:
            print(f"✗ Error scraping: {e}")
            return None
    
    async def scrape_company_search(self, company_name: str) -> List[Dict[str, Any]]:
        """Search and scrape company-specific news"""
        signals = []
        
        if not self.company_sources:
            return signals
        
        print(f"\n🔍 Searching company news for: {company_name}")
        
        articles_per_source = max(2, self.max_articles // len(self.company_sources))
        
        for source in self.company_sources:
            if not source.get('enabled', True):
                continue
            
            search_url = source['search_url'].replace('{query}', company_name.replace(' ', '+'))
            print(f"\n🌐 Searching: {source['name']}")
            
            article_links = await self.extract_article_links(search_url, wait_for_js=True)
            
            source_count = 0
            for link_data in article_links:
                if source_count >= articles_per_source:
                    break
                    
                article = await self.scrape_article_content(link_data['url'])
                if article:
                    signals.append({
                        'type': 'company_news',
                        'source': source['name'],
                        'search_query': company_name,
                        **article
                    })
                    source_count += 1
        
        return signals[:self.max_articles]
    
    async def search_workforce_signals_company(self, company_name: str, before_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Compatible with main.py API - async version"""
        signals = []
        
        try:
            article_results = await self.scrape_company_search(company_name)
            
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
            
        finally:
            await self.close_browser()
