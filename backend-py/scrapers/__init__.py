"""
Scrapers package initialization
"""
from .financial_scraper import FinancialDataScraper
from .news_scraper_playwright import NewsSearchScraperPlaywright
from .reddit_scraper import RedditScraper
from .google_news_rss_scraper import GoogleNewsRSSScraper

# Alias for compatibility
NewsSearchScraper = NewsSearchScraperPlaywright

__all__ = ['FinancialDataScraper', 'NewsSearchScraper', 'NewsSearchScraperPlaywright', 'RedditScraper', 'GoogleNewsRSSScraper']
