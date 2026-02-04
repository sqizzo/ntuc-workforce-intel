"""
Reddit Connection Test Script

Run this to diagnose Reddit connection issues.
"""
import sys
import requests
import socket

def test_basic_connectivity():
    """Test basic internet connectivity"""
    print("=" * 60)
    print("TEST 1: Basic Internet Connectivity")
    print("=" * 60)
    
    try:
        response = requests.get("https://www.google.com", timeout=10)
        print(f"✓ Internet connection working (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"✗ Internet connection failed: {e}")
        print("  → Check your internet connection first!")
        return False

def test_reddit_website():
    """Test if Reddit website is accessible"""
    print("\n" + "=" * 60)
    print("TEST 2: Reddit Website Access")
    print("=" * 60)
    
    try:
        response = requests.get("https://www.reddit.com", timeout=10)
        print(f"✓ Reddit website accessible (Status: {response.status_code})")
        return True
    except requests.ConnectionError as e:
        error_str = str(e)
        if "10061" in error_str or "refused" in error_str.lower():
            print("✗ Reddit is BLOCKING your connection!")
            print("  → Error: Connection actively refused")
            print("  → This means Reddit's anti-bot protection detected you")
        else:
            print(f"✗ Cannot connect to Reddit: {e}")
        return False
    except Exception as e:
        print(f"✗ Reddit access failed: {e}")
        return False

def test_reddit_json_api():
    """Test Reddit JSON API endpoint"""
    print("\n" + "=" * 60)
    print("TEST 3: Reddit JSON API")
    print("=" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        url = "https://www.reddit.com/r/singapore/search.json"
        params = {'q': 'test', 'limit': 1}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Reddit API working! Found data: {len(data.get('data', {}).get('children', []))} posts")
            return True
        else:
            print(f"⚠ Reddit API returned status: {response.status_code}")
            return False
            
    except requests.ConnectionError as e:
        error_str = str(e)
        if "10061" in error_str or "refused" in error_str.lower():
            print("✗ Reddit API is BLOCKING your connection!")
            print("  → Error: WinError 10061 - Connection refused")
            print("  → This is the exact error you're seeing in the scraper")
        else:
            print(f"✗ Cannot connect to Reddit API: {e}")
        return False
    except Exception as e:
        print(f"✗ Reddit API test failed: {e}")
        return False

def test_dns_resolution():
    """Test DNS resolution for reddit.com"""
    print("\n" + "=" * 60)
    print("TEST 4: DNS Resolution")
    print("=" * 60)
    
    try:
        ip_address = socket.gethostbyname("www.reddit.com")
        print(f"✓ DNS working - reddit.com resolves to: {ip_address}")
        return True
    except Exception as e:
        print(f"✗ DNS resolution failed: {e}")
        return False

def print_diagnosis(results):
    """Print diagnosis and recommendations"""
    print("\n" + "=" * 60)
    print("DIAGNOSIS & RECOMMENDATIONS")
    print("=" * 60)
    
    internet, reddit_web, reddit_api, dns = results
    
    if not internet:
        print("\n❌ PROBLEM: No internet connection")
        print("   → Fix your internet connection first")
        
    elif not dns:
        print("\n❌ PROBLEM: DNS resolution issue")
        print("   → Try changing DNS servers (8.8.8.8 or 1.1.1.1)")
        print("   → Check if Reddit is blocked in your country/network")
        
    elif not reddit_web and not reddit_api:
        print("\n❌ PROBLEM: Reddit is completely blocked")
        print("   → Reddit is blocking your IP or network")
        print("\n   SOLUTIONS (in order of effectiveness):")
        print("   1. ✓ Connect to a VPN (ExpressVPN, NordVPN, etc.)")
        print("   2. ✓ Try mobile hotspot instead of WiFi")
        print("   3. ✓ Check firewall/antivirus settings")
        print("   4. ✓ Use Reddit's official API (see REDDIT_TROUBLESHOOTING.md)")
        print("   5. ✓ Skip Reddit scraping - use only Financial & News scrapers")
        
    elif reddit_web and not reddit_api:
        print("\n⚠ PROBLEM: Reddit website works but API is blocked")
        print("   → Reddit is specifically blocking automated requests")
        print("\n   SOLUTIONS:")
        print("   1. ✓ Use Reddit's official API with authentication")
        print("   2. ✓ Use a VPN")
        print("   3. ✓ Skip Reddit scraping")
        
    else:
        print("\n✓ All tests passed!")
        print("   → Reddit connection should work")
        print("   → If scraper still fails, try:")
        print("     - Restart the Python backend")
        print("     - Clear Python cache: delete __pycache__ folders")
        print("     - Reinstall requests: pip install --upgrade requests")

def main():
    print("\n🔍 REDDIT CONNECTION DIAGNOSTIC TOOL")
    print("This will test your connection to Reddit\n")
    
    results = (
        test_basic_connectivity(),
        test_reddit_website(),
        test_reddit_json_api(),
        test_dns_resolution()
    )
    
    print_diagnosis(results)
    
    print("\n" + "=" * 60)
    print("For detailed solutions, see: REDDIT_TROUBLESHOOTING.md")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(0)
