# Python Backend for Workforce Intelligence Scraper

FastAPI-based backend service for scraping workforce intelligence signals from multiple sources.

## Features

- **Financial Scraper**: Scrapes company financial data using yfinance
- **News Scraper**: Scrapes news articles from search results
- **Reddit Scraper**: Scrapes Reddit discussions and threads

## Installation

1. Create and activate a virtual environment:

**On Windows (PowerShell):**

```bash
cd backend-py
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Or use the provided activation script:

```bash
.\activate.bat
```

**On Linux/Mac:**

```bash
cd backend-py
python -m venv venv
source venv/bin/activate
```

Or use the provided activation script:

```bash
./activate.sh
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
cd backend-py
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Main Scraping Endpoint

**POST** `/api/scrape`

Request body:

```json
{
  "mode": "GENERAL" | "COMPANY" | "FINANCIAL" | "NEWS" | "REDDIT",
  "keywords": ["layoffs", "hiring"],
  "companyName": "Apple",
  "ticker": "AAPL",
  "subreddit": "singapore",
  "max_articles": 10
}
```

### Specific Scrapers

- **POST** `/api/scrape/financial?ticker=AAPL`
- **POST** `/api/scrape/news` - Body: `{"keywords": ["layoffs"], "max_articles": 10}`
- **POST** `/api/scrape/reddit` - Body: `{"subreddit": "singapore", "keywords": ["jobs"]}`

## Scraper Modules

### Financial Scraper (`scrapers/financial_scraper.py`)

Uses yfinance to fetch company financial data and extract workforce signals from financial metrics.

## Troubleshooting

### Reddit Connection Errors

If you encounter this error when scraping Reddit:

```
NewConnectionError: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it
```

**Quick Diagnosis:**

Run the connection test script to diagnose the issue:

```bash
cd backend-py
python tests/test_reddit_connection.py
```

This will test your Reddit connection and provide specific recommendations.

**Causes:**

1. **Reddit is blocking automated requests** (most common)
2. Firewall/antivirus blocking the connection
3. Network proxy/VPN issues
4. Reddit API rate limiting

**Solutions:**

1. **Use a VPN or different network**: Reddit may be blocking your IP address or network
   - Try connecting through a VPN
   - Try from a different network (mobile hotspot, etc.)

2. **Check firewall/antivirus settings**:
   - Temporarily disable antivirus to test
   - Add Python to firewall exceptions
   - Allow outbound connections to reddit.com

3. **Use Reddit's Official API** (Recommended for production):
   - Create a Reddit app at https://www.reddit.com/prefs/apps
   - Get client_id and client_secret
   - Use PRAW (Python Reddit API Wrapper) instead of direct scraping
   - Install: `pip install praw`

4. **Reduce request frequency**:
   - The scraper has retry logic, but Reddit may still block frequent requests
   - Consider caching results or reducing scraping frequency

5. **Alternative: Use Reddit search without API**:
   - Visit reddit.com manually and check if it loads
   - If Reddit blocks all connections, you may need to use their official API or skip Reddit scraping

**Note**: Reddit heavily restricts automated access. For production use, it's recommended to use Reddit's official API with proper authentication.

### News Scraper (`scrapers/news_scraper.py`)

Uses Selenium and undetected-chromedriver to scrape news articles from search results.

### Reddit Scraper (`scrapers/reddit_scraper.py`)

Uses Selenium to scrape Reddit threads and extract workforce discussions.

## Environment Variables

Create a `.env` file:

```
PORT=8000
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
```

## Notes

- The scrapers use headless Chrome for web scraping
- Rate limiting and delays are implemented to avoid detection
- CORS is configured to allow Next.js frontend connections
