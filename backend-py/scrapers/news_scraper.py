"""
News Search Scraper Module
Scrapes news articles from search results using Selenium
"""
import time
import random
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, urljoin
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchWindowException


class NewsSearchScraper:
    """Scraper for news articles from search results"""
    
    def __init__(self, max_articles: int = 10, general_sources: list = None, company_sources: list = None):
        self.max_articles = max_articles
        self.general_sources = general_sources or []
        self.company_sources = company_sources or []
        self.driver = None
        
    def setup_driver(self):
        """Setup undetected Chrome driver"""
        if self.driver:
            try:
                # Test if driver is still alive
                _ = self.driver.current_url
                return
            except:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            
        print("Setting up stealth browser...")
        try:
            # Create completely fresh options object
            options = uc.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            # Use version 144 explicitly to match current Chrome
            self.driver = uc.Chrome(
                options=options,
                version_main=144,
                use_subprocess=False
            )
            print("✓ Stealth browser ready")
        except Exception as e:
            print(f"⚠ Failed to setup Chrome with version 144, trying auto-detect: {e}")
            try:
                # Fallback: let it auto-detect
                options = uc.ChromeOptions()
                options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                self.driver = uc.Chrome(options=options, use_subprocess=False)
                print("✓ Stealth browser ready (auto-detected version)")
            except Exception as e2:
                print(f"✗ Failed to setup Chrome: {e2}")
                raise
        
    def close_driver(self):
        """Close the browser driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def is_driver_alive(self) -> bool:
        """Check if driver is still active"""
        if not self.driver:
            return False
        try:
            _ = self.driver.current_url
            return True
        except (WebDriverException, NoSuchWindowException):
            return False
    
    def extract_article_links(self, search_url: str) -> List[Dict[str, str]]:
        """Extract article links from search results page"""
        print(f"\n🔍 Loading search results: {search_url}")
        
        if not self.is_driver_alive():
            self.setup_driver()
        
        self.driver.get(search_url)
        time.sleep(random.uniform(3, 5))
        
        # Extract article links using JavaScript
        article_data = self.driver.execute_script("""
            let articles = [];
            let linkElements = document.querySelectorAll('a[href*="/article"], a[href*="/news"], a[href*="/singapore"], a[href*="/business"]');
            let seenUrls = new Set();
            
            linkElements.forEach(link => {
                let url = link.href;
                let title = link.textContent.trim();
                
                if (url && 
                    !url.includes('/search') && 
                    !url.includes('/tag') && 
                    !url.includes('/category') &&
                    !seenUrls.has(url) &&
                    title.length > 20) {
                    
                    seenUrls.add(url);
                    articles.push({
                        url: url,
                        previewTitle: title
                    });
                }
            });
            
            return articles;
        """)
        
        print(f"✓ Found {len(article_data)} article links")
        return article_data[:self.max_articles]
    
    def scrape_article_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape content from a single article"""
        try:
            if not self.is_driver_alive():
                self.setup_driver()
                
            print(f"📄 Scraping: {url}")
            self.driver.get(url)
            time.sleep(random.uniform(2, 4))
            
            # Extract article data using JavaScript
            article_data = self.driver.execute_script("""
                let title = document.querySelector('h1')?.textContent.trim() || '';
                let author = document.querySelector('[rel="author"], .author, .byline')?.textContent.trim() || '';
                let date = document.querySelector('time, .date, .publish-date')?.textContent.trim() || '';
                
                let contentSelectors = [
                    'article',
                    '[class*="article-body"]',
                    '[class*="content"]',
                    '[class*="post-content"]',
                    'main'
                ];
                
                let content = '';
                for (let selector of contentSelectors) {
                    let el = document.querySelector(selector);
                    if (el) {
                        let paragraphs = el.querySelectorAll('p');
                        content = Array.from(paragraphs)
                            .map(p => p.textContent.trim())
                            .filter(text => text.length > 30)
                            .join(' ');
                        if (content.length > 200) break;
                    }
                }
                
                return {
                    title: title,
                    author: author,
                    date: date,
                    content: content,
                    url: window.location.href
                };
            """)
            
            if article_data['content']:
                print(f"✓ Scraped: {article_data['title'][:50]}...")
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
            
        print(f"Scraping {len(self.general_sources)} general sources...")
        
        for idx, source in enumerate(self.general_sources):
            try:
                article = self.scrape_article_content(source['url'])
                
                if article:
                    matched = [kw for kw in keywords if kw.lower() in article['content'].lower()]
                    
                    signals.append({
                        'id': f'signal-general-{int(time.time())}-{idx}',
                        'source_type': 'news',
                        'source_name': source.get('name', urlparse(article['url']).netloc),
                        'source_url': article['url'],
                        'ingestion_timestamp': datetime.now().isoformat(),
                        'extracted_text': article['content'][:500],
                        'matched_keywords': matched,
                        'inferred_workforce_theme': self._infer_theme(article['content'], keywords),
                        'metadata': {
                            'title': article['title'],
                            'author': article['author'],
                            'publish_date': article['date'],
                            'general_source': True,
                            'full_content': article['content']
                        }
                    })
            except Exception as e:
                print(f"⚠ Failed to scrape {source.get('url')}: {e}")
            
            time.sleep(random.uniform(1, 2))
        
        return signals
    
    def search_workforce_signals(
        self, 
        keywords: List[str],
        search_engine: str = "google"
    ) -> List[Dict[str, Any]]:
        """
        Search for workforce-related news articles
        
        Args:
            keywords: List of keywords to search for
            search_engine: Search engine to use (google, bing, etc.)
            
        Returns:
            List of workforce signals from news articles
        """
        signals = []
        
        try:
            # First scrape general sources if available
            if self.general_sources:
                self.setup_driver()
                general_signals = self.scrape_general_sources(keywords)
                signals.extend(general_signals)
                print(f"✓ Scraped {len(general_signals)} signals from general sources")
            
            # If we still need more articles, search online
            remaining = self.max_articles - len(signals)
            if remaining > 0:
                self.setup_driver()
                
                # Construct search query
                query = " OR ".join(keywords)
                if search_engine == "google":
                    search_url = f"https://www.google.com/search?q={query}+singapore+workforce&tbm=nws"
                else:
                    search_url = f"https://www.bing.com/news/search?q={query}+singapore+workforce"
                
                # Extract article links
                articles = self.extract_article_links(search_url)
                
                # Scrape each article
                for idx, article_link in enumerate(articles[:remaining]):
                    article = self.scrape_article_content(article_link['url'])
                    
                    if article:
                        # Find matched keywords
                        matched = [kw for kw in keywords if kw.lower() in article['content'].lower()]
                        
                        signals.append({
                            'id': f'signal-news-{int(time.time())}-{idx}',
                            'source_type': 'news',
                            'source_name': urlparse(article['url']).netloc,
                            'source_url': article['url'],
                            'ingestion_timestamp': datetime.now().isoformat(),
                            'extracted_text': article['content'][:500],
                            'matched_keywords': matched,
                            'inferred_workforce_theme': self._infer_theme(article['content'], keywords),
                            'metadata': {
                                'title': article['title'],
                                'author': article['author'],
                                'publish_date': article['date'],
                                'full_content': article['content']
                            }
                        })
                    
                    time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            print(f"⚠ Error during news scraping: {e}")
        finally:
            self.close_driver()
        
        return signals
    
    def search_workforce_signals_company(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Search for company-specific news using configured search URLs
        
        Args:
            company_name: Name of the company to search for
            
        Returns:
            List of workforce signals from company-specific searches
        """
        signals = []
        
        if not self.company_sources:
            print("No company search sources configured")
            return signals
        
        try:
            self.setup_driver()
            print(f"Searching for '{company_name}' across {len(self.company_sources)} sources...")
            
            for idx, source in enumerate(self.company_sources):
                try:
                    # Format search URL with company name
                    search_url = source['search_url'].replace('{query}', company_name.replace(' ', '+'))
                    
                    # Extract article links
                    articles = self.extract_article_links(search_url)
                    
                    # Scrape each article
                    for article_idx, article_link in enumerate(articles[:3]):  # Limit per source
                        article = self.scrape_article_content(article_link['url'])
                        
                        if article:
                            signals.append({
                                'id': f'signal-company-{int(time.time())}-{idx}-{article_idx}',
                                'source_type': 'news',
                                'source_name': source.get('name', urlparse(article['url']).netloc),
                                'source_url': article['url'],
                                'ingestion_timestamp': datetime.now().isoformat(),
                                'extracted_text': article['content'][:500],
                                'matched_keywords': [company_name],
                                'inferred_workforce_theme': self._infer_theme(article['content'], [company_name]),
                                'company_name': company_name,
                                'metadata': {
                                    'title': article['title'],
                                    'author': article['author'],
                                    'publish_date': article['date'],
                                    'company_search': True,
                                    'full_content': article['content']
                                }
                            })
                        
                        time.sleep(random.uniform(1, 2))
                        
                except Exception as e:
                    print(f"⚠ Failed to search {source.get('name')}: {e}")
                
                time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"⚠ Error during company search: {e}")
        finally:
            self.close_driver()
        
        return signals
    
    def _infer_theme(self, content: str, keywords: List[str]) -> str:
        """Infer workforce theme from content"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['layoff', 'retrenchment', 'job cut']):
            return 'Workforce Reduction'
        elif any(word in content_lower for word in ['hiring', 'recruitment', 'job opening']):
            return 'Hiring Activity'
        elif any(word in content_lower for word in ['automation', 'ai', 'technology']):
            return 'Technology & Automation'
        elif any(word in content_lower for word in ['wage', 'salary', 'pay']):
            return 'Compensation & Benefits'
        elif any(word in content_lower for word in ['restructur', 'reorganiz']):
            return 'Organizational Change'
        else:
            return 'General Workforce Trend'
