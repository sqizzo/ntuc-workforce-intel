"""
Monitor RAM usage of Playwright news scraper
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psutil
import time
from scrapers.news_scraper_playwright import NewsSearchScraperPlaywright

def get_memory_usage():
    """Get current process memory usage in MB"""
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / 1024 / 1024  # Convert to MB
    return mem

def monitor_scraping():
    """Monitor RAM usage during scraping"""
    
    test_sources = [{
        "name": "Straits Times Singapore",
        "url": "https://www.straitstimes.com/singapore",
        "enabled": True
    }]
    
    test_company_sources = [{
        "name": "Straits Times Search",
        "search_url": "https://www.straitstimes.com/search?searchkey={query}&sort=relevancydate",
        "enabled": True
    }]
    
    print("🔍 Memory Usage Monitoring")
    print("="*60)
    
    # Baseline memory
    baseline = get_memory_usage()
    print(f"📊 Baseline (Python startup): {baseline:.1f} MB")
    
    # After importing scraper
    import_mem = get_memory_usage()
    print(f"📦 After imports: {import_mem:.1f} MB (+{import_mem - baseline:.1f} MB)")
    
    # Test 1: General scraping
    print("\n" + "="*60)
    print("TEST 1: General News Scraping")
    print("="*60)
    
    scraper = NewsSearchScraperPlaywright(
        max_articles=2,
        general_sources=test_sources
    )
    
    start_mem = get_memory_usage()
    print(f"📊 Before scraping: {start_mem:.1f} MB")
    
    # Start scraping
    results = scraper.scrape(
        mode="general",
        keywords=["Singapore"]
    )
    
    peak_mem = get_memory_usage()
    print(f"📊 After scraping: {peak_mem:.1f} MB")
    print(f"📈 Memory used for scraping: {peak_mem - start_mem:.1f} MB")
    print(f"📊 Total RAM used: {peak_mem:.1f} MB")
    print(f"✓ Found {results['total_signals']} articles")
    
    # Test 2: Company search with JS
    print("\n" + "="*60)
    print("TEST 2: Company Search (with JavaScript)")
    print("="*60)
    
    scraper2 = NewsSearchScraperPlaywright(
        max_articles=1,
        company_sources=test_company_sources
    )
    
    start_mem2 = get_memory_usage()
    print(f"📊 Before search: {start_mem2:.1f} MB")
    
    results2 = scraper2.scrape(
        mode="company",
        query="NTUC"
    )
    
    peak_mem2 = get_memory_usage()
    print(f"📊 After search: {peak_mem2:.1f} MB")
    print(f"📈 Memory used for search: {peak_mem2 - start_mem2:.1f} MB")
    print(f"📊 Total RAM used: {peak_mem2:.1f} MB")
    print(f"✓ Found {results2['total_signals']} articles")
    
    # Final summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    max_mem = max(peak_mem, peak_mem2)
    print(f"📊 Peak memory usage: {max_mem:.1f} MB")
    print(f"📊 Memory overhead: {max_mem - baseline:.1f} MB")
    
    # Render free tier has 512MB RAM
    render_limit = 512
    remaining = render_limit - max_mem
    
    print(f"\n🎯 Render Free Tier Analysis:")
    print(f"   Total RAM available: {render_limit} MB")
    print(f"   Peak usage: {max_mem:.1f} MB ({max_mem/render_limit*100:.1f}%)")
    print(f"   Remaining: {remaining:.1f} MB")
    
    if max_mem < render_limit * 0.8:
        print(f"   ✅ SAFE: Well within limits!")
    elif max_mem < render_limit:
        print(f"   ⚠️  CAUTION: Close to limit")
    else:
        print(f"   ❌ UNSAFE: Exceeds free tier limit")

if __name__ == "__main__":
    try:
        monitor_scraping()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
