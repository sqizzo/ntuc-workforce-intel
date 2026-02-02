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
