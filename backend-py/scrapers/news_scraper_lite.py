"""
News Search Scraper Module (Lightweight Version)
Scrapes news articles using requests + BeautifulSoup instead of Selenium
"""
import time
import random
import re
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup


class NewsSearchScraper:
    """Lightweight scraper for news articles using requests + BeautifulSoup"""
    
    def __init__(self, max_articles: int = 10, general_sources: list = None, company_sources: list = None):
        self.max_articles = max_articles
        self.general_sources = general_sources or []
        self.company_sources = company_sources or []
        self.session = requests.Session()
        
        # Set realistic headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
    def extract_article_links(self, search_url: str) -> List[Dict[str, str]]:
        """Extract article links from search results page"""
        print(f"\n🔍 Loading search results: {search_url}")
        
        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            time.sleep(random.uniform(2, 4))  # Be polite
            
            soup = BeautifulSoup(response.content, 'html.parser')
            article_data = []
            seen_urls = set()
            
            # Find all links
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href')
                if not href:
                    continue
                
                # Make absolute URL
                url = urljoin(search_url, href)
                
                # Get title
                title = link.get_text(strip=True)
                
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
                    '?ref=' not in url and  # Skip navigation refs
                    len(title) > 20):
                    
                    seen_urls.add(url)
                    article_data.append({
                        'url': url,
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
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            time.sleep(random.uniform(2, 4))  # Be polite
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = ''
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)
            
            # Extract author
            author = ''
            author_selectors = ['[rel="author"]', '.author', '.byline', '.article-author']
            for selector in author_selectors:
                author_el = soup.select_one(selector)
                if author_el:
                    author = author_el.get_text(strip=True)
                    break
            
            # Extract date
            date = ''
            
            # Strategy 1: time element with datetime
            time_el = soup.find('time')
            if time_el and time_el.get('datetime'):
                date = time_el['datetime']
            
            # Strategy 2: Common date selectors
            if not date:
                date_selectors = [
                    'time', '.date', '.publish-date', '.published-date',
                    '.article-publish-date', '[class*="publish"]',
                    '[class*="date"]', '[class*="timestamp"]'
                ]
                for selector in date_selectors:
                    date_el = soup.select_one(selector)
                    if date_el:
                        date = date_el.get_text(strip=True)
                        break
            
            # Strategy 3: Meta tags
            if not date:
                meta_date = (soup.find('meta', {'property': 'article:published_time'}) or
                            soup.find('meta', {'name': 'publish-date'}) or
                            soup.find('meta', {'name': 'date'}))
                if meta_date:
                    date = meta_date.get('content', '')
            
            # Extract content
            content = ''
            content_selectors = [
                'article',
                '[class*="article-body"]',
                '[class*="content"]',
                '[class*="post-content"]',
                'main'
            ]
            
            for selector in content_selectors:
                content_el = soup.select_one(selector)
                if content_el:
                    paragraphs = content_el.find_all('p')
                    content = ' '.join([
                        p.get_text(strip=True) 
                        for p in paragraphs 
                        if len(p.get_text(strip=True)) > 30
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
                # Use extract_article_links to get article URLs
                article_links = self.extract_article_links(source['url'])
                
                print(f"📝 Found {len(article_links)} articles to check")
                
                # Scrape each article and filter by keywords
                for link_data in article_links[:self.max_articles * 2]:  # Check more articles
                    article = self.scrape_article_content(link_data['url'])
                    if article and article.get('content'):
                        # Check if keywords appear in title or content
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
        """Search and scrape company-specific news"""
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
            
            # Get article links from search results
            article_links = self.extract_article_links(search_url)
            
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
        """
        Main scraping method
        mode: 'general' or 'company'
        query: company name for company mode
        keywords: list of keywords for general mode
        """
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
