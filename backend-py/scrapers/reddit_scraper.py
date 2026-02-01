"""
Reddit Scraper Module
Scrapes Reddit threads and comments using Reddit JSON API (fallback to Selenium)
"""
import time
import random
import re
import requests
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, quote_plus
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class RedditScraper:
    """Scraper for Reddit threads and comments"""
    
    def __init__(self):
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
            
        print("Setting up undetected-chromedriver...")
        
        try:
            # Create completely fresh options object each time
            options = uc.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            # Add more realistic browser settings
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--lang=en-US")
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
            
            # Disable automation indicators
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2
            }
            options.add_experimental_option("prefs", prefs)
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # Use version 144 explicitly to match current Chrome
            self.driver = uc.Chrome(
                options=options,
                version_main=144,
                use_subprocess=False
            )
            print("✓ Undetected Chrome initialized")
        except Exception as e:
            print(f"⚠ Failed to setup Chrome with version 144, trying auto-detect: {e}")
            try:
                # Fallback: let it auto-detect
                options = uc.ChromeOptions()
                options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                self.driver = uc.Chrome(options=options, use_subprocess=False)
                print("✓ Undetected Chrome initialized (auto-detected version)")
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
    
    def dismiss_modals(self):
        """Dismiss Reddit modals/popups"""
        try:
            time.sleep(2)
            self.driver.execute_script("""
                document.querySelectorAll('[role="dialog"]').forEach(el => el.remove());
                document.querySelectorAll('.Overlay').forEach(el => el.remove());
            """)
            close_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "button[aria-label='Close'], button[icon='close']")
            for btn in close_buttons:
                try:
                    if btn.is_displayed():
                        btn.click()
                        time.sleep(1)
                except:
                    pass
            print("✓ Dismissed modals")
        except:
            pass
    
    def scroll_page(self, scrolls: int = 8):
        """Scroll page to load more content"""
        print(f"📜 Scrolling to load comments ({scrolls} scrolls)...")
        for i in range(scrolls):
            self.driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(random.uniform(0.5, 1.5))
        print("✓ Scrolling complete")
    
    def scrape_reddit_thread(self, url: str) -> Dict[str, Any]:
        """
        Scrape a Reddit thread including post and comments
        
        Args:
            url: Reddit thread URL
            
        Returns:
            Dictionary containing thread data and comments
        """
        try:
            self.setup_driver()
            
            print(f"\n🌐 Loading Reddit: {url}")
            self.driver.get(url)
            time.sleep(random.uniform(5, 8))
            
            self.dismiss_modals()
            self.scroll_page()
            
            # Extract post data
            post_data = self.driver.execute_script("""
                let post = {};
                
                // Title
                let titleEl = document.querySelector('[slot="title"]') || 
                              document.querySelector('h1');
                post.title = titleEl ? titleEl.textContent.trim() : '';
                
                // Author
                let authorEl = document.querySelector('[slot="authorName"]') || 
                               document.querySelector('[data-testid="post-author"]');
                post.author = authorEl ? authorEl.textContent.trim() : '';
                
                // Post text
                let textEl = document.querySelector('[slot="text-body"]') ||
                            document.querySelector('[data-click-id="text"]');
                post.text = textEl ? textEl.textContent.trim() : '';
                
                // Subreddit
                let subredditEl = document.querySelector('[data-testid="subreddit-name"]');
                post.subreddit = subredditEl ? subredditEl.textContent.trim() : '';
                
                return post;
            """)
            
            print(f"✓ Post: {post_data['title'][:60]}...")
            
            # Extract comments
            comments_data = self.driver.execute_script("""
                let comments = [];
                let commentElements = document.querySelectorAll('[data-testid="comment"]');
                
                commentElements.forEach(el => {
                    let author = el.querySelector('[data-testid="comment_author_link"]')?.textContent.trim() || '';
                    let text = el.querySelector('[data-testid="comment"]')?.textContent.trim() || '';
                    
                    if (text.length > 20) {
                        comments.push({
                            author: author,
                            text: text
                        });
                    }
                });
                
                return comments;
            """)
            
            print(f"✓ Extracted {len(comments_data)} comments")
            
            return {
                'url': url,
                'post': post_data,
                'comments': comments_data,
                'scrape_timestamp': datetime.now().isoformat()
            }
            
        finally:
            self.close_driver()
    
    def search_using_json_api(
        self,
        subreddit: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search Reddit using JSON API (no selenium needed)
        Returns full signal data including post content
        """
        try:
            # Build Reddit JSON API URL
            search_url = f"https://www.reddit.com/r/{subreddit}/search.json"
            params = {
                'q': query,
                'restrict_sr': 'on',
                'sort': 'relevance',
                't': 'all',
                'limit': limit
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            }
            
            print(f"🔍 Searching Reddit JSON API: {search_url}?q={query}")
            
            # Retry logic for connection issues
            for attempt in range(3):
                try:
                    response = requests.get(search_url, params=params, headers=headers, timeout=15)
                    response.raise_for_status()
                    break
                except (requests.ConnectionError, requests.Timeout) as e:
                    if attempt < 2:
                        wait_time = (attempt + 1) * 2
                        print(f"⚠️ Connection failed (attempt {attempt + 1}/3), retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        raise
            
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            
            signals = []
            for idx, post in enumerate(posts):
                post_data = post.get('data', {})
                permalink = post_data.get('permalink')
                title = post_data.get('title', 'Untitled')
                selftext = post_data.get('selftext', '')
                author = post_data.get('author', 'unknown')
                subreddit_name = post_data.get('subreddit', subreddit)
                num_comments = post_data.get('num_comments', 0)
                
                if permalink and title:
                    url = f"https://www.reddit.com{permalink}"
                    
                    # Fetch comments from the thread
                    print(f"  📥 Fetching comments for: {title[:50]}...")
                    comments = self._fetch_comments_json(permalink, headers, limit=10)
                    
                    # Create combined text for searching
                    combined_text = f"{title} {selftext}"
                    if comments:
                        comments_text = ' '.join([c['text'] for c in comments])
                        combined_text += f" {comments_text}"
                        print(f"    ✓ Fetched {len(comments)} comments")
                    else:
                        print(f"    ⚠️ No comments fetched")
                    
                    signals.append({
                        'id': f'signal-reddit-{int(time.time())}-{idx}',
                        'source_type': 'social',
                        'source_name': f"Reddit r/{subreddit_name}",
                        'source_url': url,
                        'ingestion_timestamp': datetime.now().isoformat(),
                        'post_title': title,
                        'post_text': selftext,
                        'extracted_text': combined_text[:1000],
                        'comments': comments,
                        'matched_keywords': query.split(' OR '),
                        'inferred_workforce_theme': self._infer_theme(combined_text),
                        'metadata': {
                            'title': title,
                            'author': author,
                            'comment_count': num_comments
                        }
                    })
            
            print(f"✓ Found {len(signals)} Reddit signals via JSON API")
            return signals
            
        except Exception as e:
            print(f"❌ JSON API failed: {e}")
            return []
    
    def _fetch_comments_json(
        self,
        permalink: str,
        headers: Dict[str, str],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch top comments from a Reddit thread using JSON API
        
        Args:
            permalink: Thread permalink (e.g., /r/singapore/comments/...)
            headers: HTTP headers to use
            limit: Maximum number of comments to fetch
            
        Returns:
            List of comment dictionaries with author, text, score
        """
        try:
            # Reddit thread JSON API
            thread_url = f"https://www.reddit.com{permalink}.json"
            
            # Retry logic
            for attempt in range(2):
                try:
                    response = requests.get(thread_url, headers=headers, timeout=10)
                    response.raise_for_status()
                    break
                except (requests.ConnectionError, requests.Timeout):
                    if attempt < 1:
                        time.sleep(2)
                    else:
                        return []
            
            data = response.json()
            
            # Reddit returns [post_data, comments_data]
            if len(data) < 2:
                return []
            
            comments_data = data[1].get('data', {}).get('children', [])
            
            comments = []
            
            for comment in comments_data:
                if len(comments) >= limit:
                    break
                    
                comment_data = comment.get('data', {})
                body = comment_data.get('body', '')
                author = comment_data.get('author', 'unknown')
                score = comment_data.get('score', 0)
                
                # Skip deleted, removed, or AutoModerator comments
                if body and body not in ['[deleted]', '[removed]'] and author != 'AutoModerator':
                    comments.append({
                        'author': author,
                        'text': body,
                        'score': score
                    })
            
            return comments
            
        except Exception as e:
            print(f"⚠️ Failed to fetch comments for {permalink}: {e}")
            return []
    
    def search_workforce_signals(
        self,
        subreddit: str = "singapore",
        keywords: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search Reddit for workforce-related discussions
        Uses JSON API (no Selenium/browser needed)
        
        Args:
            subreddit: Subreddit to search
            keywords: Optional keywords to search for
            
        Returns:
            List of workforce signals from Reddit
        """
        try:
            # Build search query
            if keywords:
                query = " OR ".join(keywords)
            else:
                query = "workforce layoff job"
            
            # Use JSON API (fast and reliable)
            signals = self.search_using_json_api(subreddit, query, limit=5)
            return signals
            
        except Exception as e:
            print(f"Error in search_workforce_signals: {e}")
            return []
    
    def _infer_theme(self, content: str) -> str:
        """Infer workforce theme from content"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['retrench', 'layoff', 'lose job', 'fired']):
            return 'Job Loss & Retrenchment'
        elif any(word in content_lower for word in ['hiring', 'job opening', 'career']):
            return 'Job Opportunities'
        elif any(word in content_lower for word in ['salary', 'pay', 'wage', 'compensation']):
            return 'Salary & Compensation'
        elif any(word in content_lower for word in ['work culture', 'toxic', 'burnout']):
            return 'Work Culture & Environment'
        else:
            return 'General Career Discussion'
