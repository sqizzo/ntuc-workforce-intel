"""
Test script for AI-powered symbol detection
Run this to test the integration before using in production
"""
import sys
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import services
from ai_service import CompanySymbolDetector, AIService
from scrapers.financial_scraper import FinancialDataScraper

def test_ai_service():
    """Test basic AI service connectivity"""
    print("=" * 60)
    print("Testing AI Service")
    print("=" * 60)
    
    ai_service = AIService()
    print(f"✓ AI Provider: {ai_service.provider}")
    print(f"✓ Model: {ai_service.model}")
    print()

def test_single_company():
    """Test single company symbol detection"""
    print("=" * 60)
    print("Testing Single Company Detection")
    print("=" * 60)
    
    detector = CompanySymbolDetector()
    
    test_companies = [
        "Twelve Cupcakes",
        "Grab",
        "DBS Bank",
        "Shopee",
        "Sea Limited"
    ]
    
    for company in test_companies:
        print(f"\n🔍 Testing: {company}")
        result = detector.detect_symbol(company)
        
        print(f"   Publicly Traded: {result.get('is_publicly_traded')}")
        print(f"   Yahoo Symbol: {result.get('yahoo_symbol', 'N/A')}")
        print(f"   Exchange: {result.get('exchange', 'N/A')}")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   Reasoning: {result.get('reasoning')[:100]}...")

def test_batch_detection():
    """Test batch company detection"""
    print("\n" + "=" * 60)
    print("Testing Batch Detection")
    print("=" * 60)
    
    detector = CompanySymbolDetector()
    
    companies = ["Apple", "Microsoft", "Twelve Cupcakes", "Grab"]
    print(f"\n🔍 Detecting symbols for: {', '.join(companies)}")
    
    result = detector.detect_multiple_symbols(companies)
    
    print("\nResults:")
    for company_info in result.get('results', []):
        symbol = company_info.get('yahoo_symbol', 'N/A')
        name = company_info.get('company_name')
        print(f"   {name}: {symbol}")

def test_financial_scraper():
    """Test financial scraper with AI detection"""
    print("\n" + "=" * 60)
    print("Testing Financial Scraper with AI")
    print("=" * 60)
    
    scraper = FinancialDataScraper(use_ai_detection=True)
    
    # Test with a known public company
    print("\n🔍 Testing: Grab (should find GRAB)")
    result = scraper.search_workforce_signals_by_company("Grab")
    
    if result.get('ticker'):
        print(f"   ✓ Found ticker: {result['ticker']}")
        print(f"   ✓ Signals found: {len(result.get('signals', []))}")
    else:
        print(f"   ℹ No ticker found: {result.get('metadata', {}).get('reasoning')}")
    
    # Test with a private company
    print("\n🔍 Testing: Twelve Cupcakes (should not find symbol)")
    result = scraper.search_workforce_signals_by_company("Twelve Cupcakes")
    
    if result.get('ticker'):
        print(f"   ✓ Found ticker: {result['ticker']}")
    else:
        print(f"   ℹ No ticker found (expected): {result.get('metadata', {}).get('reasoning')}")

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AI-POWERED SYMBOL DETECTION TEST SUITE")
    print("=" * 60)
    
    provider = os.getenv('AI_PROVIDER', 'mock')
    print(f"\nUsing AI Provider: {provider.upper()}")
    
    if provider == 'mock':
        print("⚠ WARNING: Using MOCK mode - responses are simulated")
        print("   To use real AI, set up your .env file with API keys")
    
    try:
        test_ai_service()
        test_single_company()
        test_batch_detection()
        test_financial_scraper()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
