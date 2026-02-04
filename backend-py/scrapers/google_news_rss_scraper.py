"""
Alternative Google News Scraper using RSS Feed
More reliable than parsing the JavaScript-heavy web interface
"""
import feedparser
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus


class GoogleNewsRSSScraper:
    """Scraper for Google News using RSS feed - more reliable than web scraping"""
    
    def __init__(self, max_articles: Optional[int] = None):
        """Initialize scraper. If max_articles is None, fetches ALL articles from RSS feed."""
        self.max_articles = max_articles
        
    def build_rss_url(self, query: str, region: str = "SG", language: str = "en") -> str:
        """
        Build Google News RSS URL
        
        Args:
            query: Search query
            region: Region code (default: SG for Singapore)
            language: Language code (default: en)
            
        Returns:
            Google News RSS feed URL
        """
        encoded_query = quote_plus(query)
        # Google News RSS format
        return f"https://news.google.com/rss/search?q={encoded_query}&hl={language}-{region}&gl={region}&ceid={region}:{language}"
    
    def parse_rss_feed(self, feed_url: str) -> List[Dict[str, Any]]:
        """
        Parse Google News RSS feed
        
        Args:
            feed_url: RSS feed URL
            
        Returns:
            List of article dictionaries
        """
        articles = []
        
        try:
            print(f"Fetching RSS feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                print("No entries found in RSS feed")
                return articles
            
            print(f"Found {len(feed.entries)} entries in RSS feed")
            
            # Fetch all entries if max_articles is None, otherwise limit
            entries_to_process = feed.entries if self.max_articles is None else feed.entries[:self.max_articles]
            print(f"Processing {len(entries_to_process)} articles...")
            
            for entry in entries_to_process:
                try:
                    # Extract article data
                    headline = entry.get('title', 'Unknown Title')
                    source_link = entry.get('link', '')
                    
                    # Extract source name (usually in title like "Title - Source Name")
                    source_name = 'Unknown Source'
                    if ' - ' in headline:
                        parts = headline.rsplit(' - ', 1)
                        if len(parts) == 2:
                            source_name = parts[1]
                            headline = parts[0]  # Clean headline
                    
                    # Extract publish date
                    published_date = None
                    raw_date = 'Unknown'
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        # Convert to datetime
                        published_date = datetime(*entry.published_parsed[:6]).isoformat()
                        raw_date = entry.get('published', 'Unknown')
                    elif hasattr(entry, 'published'):
                        raw_date = entry.get('published', 'Unknown')
                        try:
                            # Try to parse the date string
                            from email.utils import parsedate_to_datetime
                            dt = parsedate_to_datetime(raw_date)
                            published_date = dt.isoformat()
                        except:
                            published_date = datetime.now().isoformat()
                    
                    if not published_date:
                        published_date = datetime.now().isoformat()
                    
                    # Clean description from HTML tags
                    description = entry.get('summary', '').strip() if 'summary' in entry else ''
                    if description:
                        # Remove HTML tags
                        description = re.sub(r'<[^>]+>', '', description)
                        # Replace HTML entities
                        description = description.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                        description = description.strip()
                    
                    article_data = {
                        'headline': headline.strip(),
                        'source_name': source_name.strip(),
                        'source_link': source_link,
                        'published_date': published_date,
                        'raw_date': raw_date,
                        'extracted_timestamp': datetime.now().isoformat(),
                        'description': description
                    }
                    
                    articles.append(article_data)
                    print(f"  [{len(articles)}] {article_data['headline'][:80]}... ({article_data['raw_date']})")
                    
                except Exception as e:
                    print(f"Failed to parse entry: {e}")
                    continue
            
            print(f"Successfully extracted {len(articles)} articles from Google News RSS")
            
        except Exception as e:
            print(f"Error parsing RSS feed: {e}")
            import traceback
            traceback.print_exc()
        
        return articles
    
    def scrape_google_news(self, query: str, region: str = "SG", language: str = "en") -> List[Dict[str, Any]]:
        """
        Scrape Google News RSS feed for the given query
        
        Args:
            query: Search query (e.g., company name, topic)
            region: Region code (default: SG for Singapore)
            language: Language code (default: en)
            
        Returns:
            List of article dictionaries with headline, source, date, and link
        """
        feed_url = self.build_rss_url(query, region, language)
        return self.parse_rss_feed(feed_url)
    
    def search_workforce_signals(
        self, 
        query: str, 
        region: str = "SG", 
        language: str = "en",
        before_date: Optional[str] = None,
        oldest_only: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search Google News RSS and convert results to workforce signal format
        
        Args:
            query: Search query
            region: Region code
            language: Language code
            before_date: Optional filter to only include articles before this date (ISO format)
            oldest_only: If specified, returns only the N oldest articles (useful for historical analysis)
            
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
                'id': f"gnews_rss_{hash(article['headline'] + article['source_link'])}",
                'source_type': 'google_news',
                'source_name': article['source_name'],
                'source_url': article['source_link'],
                'ingestion_timestamp': article['extracted_timestamp'],
                'extracted_text': f"{article['headline']}. {article['description']}" if article['description'] else article['headline'],
                'headline': article['headline'],
                'published_date': article['published_date'],
                'raw_date': article['raw_date'],
                'metadata': {
                    'search_query': query,
                    'region': region,
                    'language': language,
                    'scraper': 'google_news_rss',
                    'description': article['description'],
                    'title': article['headline']
                }
            }
            signals.append(signal)
        
        # If oldest_only is specified, sort by date and return only oldest N articles
        if oldest_only is not None and oldest_only > 0:
            # Sort signals by published_date (oldest first)
            try:
                signals_with_dates = []
                for sig in signals:
                    try:
                        date_obj = datetime.fromisoformat(sig['published_date'].replace('Z', '+00:00'))
                        signals_with_dates.append((date_obj, sig))
                    except:
                        # If date parsing fails, put at the end
                        signals_with_dates.append((datetime.max, sig))
                
                # Sort by date (oldest first)
                signals_with_dates.sort(key=lambda x: x[0])
                
                # Return only the oldest N
                signals = [sig for _, sig in signals_with_dates[:oldest_only]]
                print(f"Filtered to {len(signals)} oldest articles for analysis")
            except Exception as e:
                print(f"Failed to sort by date: {e}, returning unsorted")
        
        return signals


if __name__ == "__main__":
    # Test the scraper - fetch ALL articles then filter to 30 oldest
    print("Testing Google News RSS Scraper...")
    print("Fetching ALL available articles from Google News RSS feed...")
    print("Then selecting 30 OLDEST articles for historical analysis...")
    scraper = GoogleNewsRSSScraper()  # No limit = fetch all
    
    # Test with a company name
    test_query = "Twelve Cupcakes Singapore"
    print(f"\nSearching for: {test_query}")
    
    # Get 30 oldest articles
    signals = scraper.search_workforce_signals(test_query, oldest_only=30)
    
    print(f"\n{'='*80}")
    print(f"Found {len(signals)} OLDEST signals (for historical analysis)")
    print(f"{'='*80}\n")
    
    for i, signal in enumerate(signals, 1):
        print(f"{i}. {signal['headline']}")
        print(f"   Source: {signal['source_name']}")
        print(f"   Date: {signal['raw_date']}")
        print(f"   Link: {signal['source_url'][:80]}...")
        if signal['metadata']['description']:
            print(f"   Desc: {signal['metadata']['description'][:100]}...")
        print()
