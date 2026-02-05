"""
Test the Playwright news scraper locally
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.news_scraper_playwright import NewsSearchScraperPlaywright
import json

# Test configuration
test_sources = [
    {
        "name": "Straits Times Singapore",
        "url": "https://www.straitstimes.com/singapore",
        "enabled": True
    }
]

test_company_sources = [
    {
        "name": "Straits Times Search",
        "search_url": "https://www.straitstimes.com/search?searchkey={query}&sort=relevancydate",
        "enabled": True
    }
]

def test_general_scraping():
    """Test general news scraping"""
    print("\n" + "="*60)
    print("TEST 1: General News Scraping (Playwright)")
    print("="*60)
    
    scraper = NewsSearchScraperPlaywright(
        max_articles=2,  # Keep it small for testing
        general_sources=test_sources
    )
    
    results = scraper.scrape(
        mode="general",
        keywords=["Singapore", "workforce", "employment"]
    )
    
    print(f"\n📊 Results: {results['total_signals']} signals found")
    if results['signals']:
        for signal in results['signals']:
            print(f"\n✓ {signal['title']}")
            print(f"  Date: {signal['date']}")
            print(f"  Content: {signal['content'][:100]}...")

def test_company_scraping():
    """Test company-specific scraping"""
    print("\n" + "="*60)
    print("TEST 2: Company News Scraping (Playwright + JS)")
    print("="*60)
    
    scraper = NewsSearchScraperPlaywright(
        max_articles=2,
        company_sources=test_company_sources
    )
    
    results = scraper.scrape(
        mode="company",
        query="twelve cupcakes"
    )
    
    print(f"\n📊 Results: {results['total_signals']} signals found")
    if results['signals']:
        for signal in results['signals']:
            print(f"\n✓ {signal['title']}")
            print(f"  Date: {signal['date']}")
            print(f"  Content: {signal['content'][:100]}...")

if __name__ == "__main__":
    print("🧪 Testing Playwright News Scraper")
    print("This uses Playwright with Chromium (50-100MB RAM)")
    
    try:
        test_general_scraping()
        test_company_scraping()
        print("\n✅ Tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
