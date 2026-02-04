"""
Google News Scraper Module
Scrapes headlines, dates, and source links from Google News search results
"""
import time
import random
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus, urlparse
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchWindowException, TimeoutException


class GoogleNewsScraper:
    """Scraper for Google News search results - fetches headlines, dates, and source links"""
    
    def __init__(self, max_articles: int = 20):
        self.max_articles = max_articles
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
            
        print("Setting up Google News scraper browser...")
        try:
            options = uc.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = uc.Chrome(options=options, version_main=None)
            self.driver.set_page_load_timeout(30)
            print("Google News browser setup complete!")
            
        except Exception as e:
            print(f"Failed to setup Google News browser: {e}")
            raise
    
    def cleanup_driver(self):
        """Clean up the driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            finally:
                self.driver = None
    
    def build_search_url(self, query: str, region: str = "SG", language: str = "en-SG") -> str:
        """
        Build Google News search URL
        
        Args:
            query: Search query
            region: Region code (default: SG for Singapore)
            language: Language code (default: en-SG)
            
        Returns:
            Google News search URL
        """
        encoded_query = quote_plus(query)
        return f"https://news.google.com/search?q={encoded_query}&hl={language}&gl={region}&ceid={region}%3Aen"
    
    def parse_relative_date(self, date_str: str) -> Optional[str]:
        """
        Parse relative date strings from Google News (e.g., '2 hours ago', '3 days ago')
        
        Args:
            date_str: Relative date string
            
        Returns:
            ISO format date string or None if parsing fails
        """
        if not date_str:
            return None
            
        try:
            from datetime import timedelta
            now = datetime.now()
            
            date_str = date_str.lower().strip()
            
            # Handle "X hours ago"
            if 'hour' in date_str:
                hours = int(re.search(r'(\d+)', date_str).group(1))
                date = now - timedelta(hours=hours)
                return date.isoformat()
            
            # Handle "X days ago"
            elif 'day' in date_str:
                days = int(re.search(r'(\d+)', date_str).group(1))
                date = now - timedelta(days=days)
                return date.isoformat()
            
            # Handle "X weeks ago"
            elif 'week' in date_str:
                weeks = int(re.search(r'(\d+)', date_str).group(1))
                date = now - timedelta(weeks=weeks)
                return date.isoformat()
            
            # Handle "X months ago" (approximate)
            elif 'month' in date_str:
                months = int(re.search(r'(\d+)', date_str).group(1))
                date = now - timedelta(days=months*30)
                return date.isoformat()
            
            # Handle "X years ago" (approximate)
            elif 'year' in date_str:
                years = int(re.search(r'(\d+)', date_str).group(1))
                date = now - timedelta(days=years*365)
                return date.isoformat()
            
            # If it's "just now" or similar
            elif 'just' in date_str or 'now' in date_str:
                return now.isoformat()
            
            return None
            
        except Exception as e:
            print(f"Failed to parse date '{date_str}': {e}")
            return None
    
    def extract_article_data(self, article_element) -> Optional[Dict[str, Any]]:
        """
        Extract headline, date, source, and link from a Google News article element
        
        Args:
            article_element: Selenium WebElement for the article
            
        Returns:
            Dictionary with article data or None if extraction fails
        """
        try:
            # Extract headline - try multiple approaches
            headline = None
            source_link = None
            
            # If element is already a link
            if article_element.tag_name == 'a':
                try:
                    headline = article_element.text.strip()
                    href = article_element.get_attribute("href")
                    if href and href.startswith('/'):
                        source_link = f"https://news.google.com{href}"
                    elif href:
                        source_link = href
                except:
                    pass
            
            # Try finding headline by various selectors
            if not headline:
                try:
                    headline_elem = article_element.find_element(By.CSS_SELECTOR, "a.JtKRv")
                    headline = headline_elem.text.strip()
                    href = headline_elem.get_attribute("href")
                    if href:
                        source_link = f"https://news.google.com{href}" if href.startswith('/') else href
                except:
                    pass
            
            if not headline:
                try:
                    headline_elem = article_element.find_element(By.TAG_NAME, "h3")
                    headline = headline_elem.text.strip()
                except:
                    pass
            
            if not headline:
                try:
                    headline_elem = article_element.find_element(By.TAG_NAME, "h4")
                    headline = headline_elem.text.strip()
                except:
                    pass
            
            # If still no headline, try getting all text
            if not headline:
                headline = article_element.text.strip()
                if len(headline) > 200:  # Too long, probably not just a headline
                    headline = headline[:200] + "..."
            
            if not headline or len(headline) < 10:  # Headline too short or missing
                return None
            
            # Extract source link if not already found
            if not source_link:
                try:
                    link_elem = article_element.find_element(By.TAG_NAME, "a")
                    href = link_elem.get_attribute("href")
                    if href:
                        if href.startswith('/'):
                            source_link = f"https://news.google.com{href}"
                        else:
                            source_link = href
                except:
                    pass
            
            # Extract source name
            source_name = None
            try:
                source_elem = article_element.find_element(By.CSS_SELECTOR, "div[data-n-tid]")
                source_name = source_elem.text.strip()
            except:
                try:
                    source_elem = article_element.find_element(By.CSS_SELECTOR, "a.wEwyrc")
                    source_name = source_elem.text.strip()
                except:
                    try:
                        # Try to find source in aria-label or data attributes
                        source_name = article_element.get_attribute("data-source")
                    except:
                        pass
            
            # Extract date
            date_str = None
            date_iso = None
            try:
                date_elem = article_element.find_element(By.CSS_SELECTOR, "time")
                date_str = date_elem.get_attribute("datetime")
                if date_str:
                    date_iso = date_str
                else:
                    # If datetime attribute not available, try text content
                    date_str = date_elem.text.strip()
                    date_iso = self.parse_relative_date(date_str)
            except:
                pass
            
            if not date_iso:
                # Try to find date text anywhere in the element
                try:
                    full_text = article_element.text
                    # Look for patterns like "X hours ago", "X days ago"
                    date_pattern = r'(\d+\s+(?:hour|day|week|month|year)s?\s+ago)'
                    match = re.search(date_pattern, full_text, re.IGNORECASE)
                    if match:
                        date_str = match.group(1)
                        date_iso = self.parse_relative_date(date_str)
                except:
                    pass
            
            return {
                'headline': headline,
                'source_name': source_name or 'Unknown Source',
                'source_link': source_link or '',
                'published_date': date_iso or datetime.now().isoformat(),
                'raw_date': date_str or 'Unknown',
                'extracted_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Failed to extract article data: {e}")
            return None
    
    def scrape_google_news(self, query: str, region: str = "SG", language: str = "en-SG") -> List[Dict[str, Any]]:
        """
        Scrape Google News search results for the given query
        
        Args:
            query: Search query (e.g., company name, topic)
            region: Region code (default: SG)
            language: Language code (default: en-SG)
            
        Returns:
            List of article dictionaries with headline, source, date, and link
        """
        articles = []
        
        try:
            self.setup_driver()
            
            # Build and navigate to search URL
            search_url = self.build_search_url(query, region, language)
            print(f"Navigating to: {search_url}")
            self.driver.get(search_url)
            
            # Wait for page to load
            time.sleep(random.uniform(3, 5))
            
            # Try to wait for article elements to appear
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
            except TimeoutException:
                print("Timeout waiting for articles, continuing anyway...")
            
            # Scroll to load more articles
            scroll_attempts = 3
            for i in range(scroll_attempts):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1, 2))
            
            # Find all article/link elements using multiple strategies
            article_elements = []
            
            # Strategy 1: Standard article tags
            try:
                article_elements = self.driver.find_elements(By.TAG_NAME, "article")
                print(f"Strategy 1 (article tag): Found {len(article_elements)} elements")
            except:
                pass
            
            # Strategy 2: Article containers by class
            if not article_elements:
                try:
                    article_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.xrnccd")
                    print(f"Strategy 2 (xrnccd): Found {len(article_elements)} elements")
                except:
                    pass
            
            # Strategy 3: By article links
            if not article_elements:
                try:
                    article_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.NiLAwe")
                    print(f"Strategy 3 (NiLAwe): Found {len(article_elements)} elements")
                except:
                    pass
            
            # Strategy 4: Find all links that look like article links
            if not article_elements:
                try:
                    all_links = self.driver.find_elements(By.TAG_NAME, "a")
                    article_elements = [link for link in all_links if link.get_attribute("href") and "/articles/" in link.get_attribute("href")]
                    print(f"Strategy 4 (article links): Found {len(article_elements)} elements")
                except:
                    pass
            
            if not article_elements:
                print("Warning: No articles found with any selector strategy")
                # Save page source for debugging
                try:
                    with open('google_news_debug.html', 'w', encoding='utf-8') as f:
                        f.write(self.driver.page_source)
                    print("Saved page source to google_news_debug.html for debugging")
                except:
                    pass
            
            print(f"Found {len(article_elements)} potential articles")
            
            # Extract data from each article
            for idx, article_elem in enumerate(article_elements[:self.max_articles]):
                if len(articles) >= self.max_articles:
                    break
                
                article_data = self.extract_article_data(article_elem)
                if article_data:
                    articles.append(article_data)
                    print(f"  [{len(articles)}] {article_data['headline'][:80]}... ({article_data['raw_date']})")
                
                # Small delay between extractions
                time.sleep(random.uniform(0.1, 0.3))
            
            print(f"Successfully extracted {len(articles)} articles from Google News")
            
        except Exception as e:
            print(f"Error scraping Google News: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            self.cleanup_driver()
        
        return articles
    
    def search_workforce_signals(
        self, 
        query: str, 
        region: str = "SG", 
        language: str = "en-SG",
        before_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search Google News and convert results to workforce signal format
        
        Args:
            query: Search query
            region: Region code
            language: Language code
            before_date: Optional filter to only include articles before this date (ISO format)
            
        Returns:
            List of workforce signals
        """
        articles = self.scrape_google_news(query, region, language)
        
        signals = []
        for article in articles:
            # Apply date filter if provided
            if before_date:
                try:
                    article_date = datetime.fromisoformat(article['published_date'].replace('Z', '+00:00'))
                    filter_date = datetime.fromisoformat(before_date)
                    if article_date >= filter_date:
                        continue
                except:
                    pass
            
            # Convert to workforce signal format
            signal = {
                'id': f"gnews_{hash(article['headline'] + article['source_link'])}",
                'source_type': 'google_news',
                'source_name': article['source_name'],
                'source_url': article['source_link'],
                'ingestion_timestamp': article['extracted_timestamp'],
                'extracted_text': article['headline'],
                'headline': article['headline'],
                'published_date': article['published_date'],
                'raw_date': article['raw_date'],
                'metadata': {
                    'search_query': query,
                    'region': region,
                    'language': language,
                    'scraper': 'google_news'
                }
            }
            signals.append(signal)
        
        return signals


if __name__ == "__main__":
    # Test the scraper
    print("Testing Google News Scraper...")
    scraper = GoogleNewsScraper(max_articles=10)
    
    # Test with a company name
    test_query = "Twelve Cupcakes"
    print(f"\nSearching for: {test_query}")
    
    signals = scraper.search_workforce_signals(test_query)
    
    print(f"\n{'='*80}")
    print(f"Found {len(signals)} signals")
    print(f"{'='*80}\n")
    
    for i, signal in enumerate(signals, 1):
        print(f"{i}. {signal['headline']}")
        print(f"   Source: {signal['source_name']}")
        print(f"   Date: {signal['raw_date']}")
        print(f"   Link: {signal['source_url'][:80]}...")
        print()
