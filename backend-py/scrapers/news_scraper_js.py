"""
News Search Scraper with JavaScript support using requests-html
Lighter than Selenium (~50-80MB vs 150MB)
"""
import time
import random
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from requests_html import HTMLSession


class NewsSearchScraperJS:
    """Lightweight scraper with JavaScript support using requests-html"""
    
    def __init__(self, max_articles: int = 10, general_sources: list = None, company_sources: list = None):
        self.max_articles = max_articles
        self.general_sources = general_sources or []
        self.company_sources = company_sources or []
        self.session = HTMLSession()
        
    def extract_article_links(self, search_url: str, use_js: bool = False) -> List[Dict[str, str]]:
        """Extract article links from search results page"""
        print(f"\n🔍 Loading search results: {search_url}")
        
        try:
            response = self.session.get(search_url, timeout=15)
            
            # Render JavaScript if needed
            if use_js:
                print("⚙️ Rendering JavaScript...")
                response.html.render(timeout=20, sleep=2)
            
            time.sleep(random.uniform(1, 2))
            
            article_data = []
            seen_urls = set()
            
            # Find all links
            for link in response.html.absolute_links:
                # Check if it looks like an article URL
                is_article = any(pattern in link for pattern in [
                    '/singapore/', '/asia/', '/world/', '/business/', 
                    '/opinion/', '/life/', '/sport/',
                    '/article/', '/news/', '/story/'
                ])
                
                if (is_article and
                    link not in seen_urls and
                    '/search' not in link and
                    '/tag/' not in link and
                    '/category/' not in link):
                    
                    # Try to find title from link text
                    title = ""
                    for element in response.html.find('a'):
                        if element.absolute_links and link in element.absolute_links:
                            title = element.text.strip()
                            if len(title) > 20:
                                break
                    
                    if not title:
                        title = "Article"
                    
                    seen_urls.add(link)
                    article_data.append({
                        'url': link,
                        'previewTitle': title
                    })
                    
                    if len(article_data) >= self.max_articles:
                        break
            
            print(f"✓ Found {len(article_data)} article links")
            return article_data[:self.max_articles]
            
        except Exception as e:
            print(f"✗ Error extracting links from {search_url}: {e}")
            return []
    
    def scrape_article_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape content from a single article"""
        try:
            print(f"📄 Scraping: {url}")
            response = self.session.get(url, timeout=15)
            time.sleep(random.uniform(1, 2))
            
            # Extract title
            title = ""
            h1_elements = response.html.find('h1', first=True)
            if h1_elements:
                title = h1_elements.text
            
            # Extract author
            author = ""
            author_selectors = ['[rel="author"]', '.author', '.byline', '.article-author']
            for selector in author_selectors:
                author_el = response.html.find(selector, first=True)
                if author_el:
                    author = author_el.text
                    break
            
            # Extract date
            date = ""
            time_el = response.html.find('time', first=True)
            if time_el:
                date = time_el.attrs.get('datetime', time_el.text)
            
            if not date:
                date_selectors = ['time', '.date', '.publish-date', '[class*="date"]']
                for selector in date_selectors:
                    date_el = response.html.find(selector, first=True)
                    if date_el:
                        date = date_el.text
                        break
            
            # Extract content
            content = ""
            content_selectors = ['article', '[class*="article-body"]', '[class*="content"]', 'main']
            
            for selector in content_selectors:
                content_el = response.html.find(selector, first=True)
                if content_el:
                    paragraphs = content_el.find('p')
                    content = ' '.join([
                        p.text.strip() 
                        for p in paragraphs 
                        if len(p.text.strip()) > 30
                    ])
                    if len(content) > 200:
                        break
            
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
                article_links = self.extract_article_links(source['url'], use_js=False)
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
        
        for source in self.company_sources:
            if not source.get('enabled', True):
                continue
            
            search_url = source['search_url'].replace('{query}', company_name.replace(' ', '+'))
            print(f"\n🌐 Searching: {source['name']}")
            
            # Get article links with JS rendering
            article_links = self.extract_article_links(search_url, use_js=True)
            
            # Scrape each article
            for link_data in article_links:
                article = self.scrape_article_content(link_data['url'])
                if article:
                    signals.append({
                        'type': 'company_news',
                        'source': source['name'],
                        'search_query': company_name,
                        **article
                    })
                
                if len(signals) >= self.max_articles:
                    break
            
            if len(signals) >= self.max_articles:
                break
        
        return signals
    
    def scrape(self, mode: str = "general", query: Optional[str] = None, keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """Main scraping method"""
        signals = []
        
        if mode == "general" and keywords:
            signals = self.scrape_general_sources(keywords)
        elif mode == "company" and query:
            signals = self.scrape_company_search(query)
        else:
            print("⚠ Invalid mode or missing parameters")
        
        return {
            'mode': mode,
            'query': query or 'N/A',
            'keywords': keywords or [],
            'signals': signals,
            'total_signals': len(signals)
        }
    
    def close(self):
        """Close the session"""
        self.session.close()
