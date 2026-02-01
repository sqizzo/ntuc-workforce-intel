from scrapers.reddit_scraper import RedditScraper
import json
from datetime import datetime

if __name__ == '__main__':
    # Test Reddit scraper with debugging
    scraper = RedditScraper()
    
    print("Testing Reddit scraper...")
    print("This will open a headless browser and search Reddit\n")
    
    signals = scraper.search_workforce_signals(
        subreddit="askSingapore",
        keywords=["Twelve Cupcakes"]
    )

    print(f"\n{'='*60}")
    print(f"RESULTS: Found {len(signals)} Reddit signals")
    print(f"{'='*60}\n")
    
    if len(signals) == 0:
        print("No signals found. Possible reasons:")
        print("1. No Reddit posts about this topic")
        print("2. Reddit blocked the automated browser")
        print("3. Try searching manually: https://www.reddit.com/r/singapore/search/?q=Twelve+Cupcakes&restrict_sr=1&sort=relevance&t=all")
    else:
        for i, signal in enumerate(signals, 1):
            print(f"{i}. {signal['metadata']['title']}")
            print(f"   URL: {signal['source_url']}")
            print(f"   Comments: {signal['metadata']['comment_count']}")
            print(f"   Theme: {signal['inferred_workforce_theme']}")
            print()
        
        # Save results to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reddit_test_dump_{timestamp}.json"
        
        dump_data = {
            "search_query": "Twelve Cupcakes",
            "subreddit": "singapore",
            "timestamp": datetime.now().isoformat(),
            "total_signals": len(signals),
            "signals": signals
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dump_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results saved to: {filename}")