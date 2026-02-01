"""
Quick test script to verify scraper functionality
"""
import sys
sys.path.append('.')

from scrapers.financial_scraper import FinancialDataScraper

def test_financial_scraper():
    """Test financial scraper with a sample ticker"""
    print("\n" + "="*70)
    print("Testing Financial Scraper")
    print("="*70)
    
    scraper = FinancialDataScraper()
    
    # Test with Apple stock
    ticker = "AAPL"
    print(f"\nFetching data for {ticker}...")
    
    try:
        result = scraper.search_workforce_signals(ticker)
        
        print(f"\n✓ Success! Found {len(result['signals'])} signals")
        print(f"Company: {result['company_name']}")
        print(f"Sector: {result['metadata']['sector']}")
        
        print("\nSignals:")
        for signal in result['signals']:
            print(f"  - {signal['workforce_signal_type']}: {signal['confidence_note']}")
        
        return True
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_financial_scraper()
    
    if success:
        print("\n" + "="*70)
        print("✓ Test passed! Financial scraper is working.")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("✗ Test failed. Check the error above.")
        print("="*70)
        sys.exit(1)
