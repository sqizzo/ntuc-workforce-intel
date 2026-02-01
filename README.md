# NTUC Workforce Intelligence Scraper

A full-stack application for scraping and analyzing workforce intelligence signals using Python scrapers and a Next.js frontend.

## Architecture

- **Frontend**: Next.js 15 with React 19 and Tailwind CSS
- **Backend**: Python FastAPI with multiple scrapers
- **Scrapers**: Financial (yfinance), News (Selenium), Reddit (Selenium)

## Features

- **General Mode**: Scrape workforce signals based on keywords from news and social media
- **Company Mode**: Target specific companies for workforce intelligence across all sources
- **Financial Mode**: Analyze company financial data for workforce signals
- **Financial Charts**: Interactive stock price visualization with 1-year historical data
- **AI Financial Analyst**: AI-powered insights on company health and workforce implications
- **JSON Dump Manager**: Save, track, and manage scraped data with automatic or manual dumps
- Real-time data visualization with Recharts
- Modern UI with Tailwind CSS

## Getting Started

### Prerequisites

- **Node.js 18+** installed
- **Python 3.8+** installed
- Chrome browser (for Selenium scrapers)

### Installation

1. **Install Node.js dependencies:**

```bash
npm install
```

2. **Install Python dependencies:**

```bash
cd backend-py
pip install -r requirements.txt
cd ..
```

3. **Configure environment variables:**

Create/update `.env.local` in the root directory:

```
PYTHON_BACKEND_URL=http://localhost:8000
```

### Running the Application

#### Option 1: Quick Start (Both Services)

**Windows:**

```bash
start.bat
```

**Linux/Mac:**

```bash
chmod +x start.sh
./start.sh
```

#### Option 2: Manual Start

**Terminal 1 - Python Backend:**

```bash
cd backend-py
python main.py
```

**Terminal 2 - Next.js Frontend:**

```bash
npm run dev
```

### Access the Application

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure

```
├── app/                    # Next.js app directory
│   ├── api/               # API routes
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Main page
├── backend-py/            # Python backend
│   ├── scrapers/          # Scraper modules
│   │   ├── financial_scraper.py
│   │   ├── news_scraper.py
│   │   └── reddit_scraper.py
│   ├── main.py           # FastAPI server
│   └── requirements.txt   # Python dependencies
├── components/            # React components
├── types.ts              # TypeScript types
└── README.md
```

## API Endpoints

### Python Backend (Port 8000)

- **POST** `/api/scrape` - Main scraping endpoint
  - Modes: `GENERAL`, `COMPANY`, `FINANCIAL`, `NEWS`, `REDDIT`
- **POST** `/api/scrape/financial?ticker=AAPL` - Financial data only
- **POST** `/api/scrape/news` - News articles only
- **POST** `/api/scrape/reddit` - Reddit discussions only

### Next.js API (Port 3000)

- **POST** `/api/scrape` - Proxies to Python backend

## Scraper Details

### Financial Scraper

Uses yfinance to fetch company financial data including:

- Company information
- Financial statements
- Balance sheets
- Cash flow
- Historical price data
- Workforce signals from financial metrics

### News Scraper

Uses Selenium with undetected-chromedriver to:

- Search Google/Bing News
- Extract article links
- Scrape article content
- Identify workforce-related themes

### Reddit Scraper

Uses Selenium to:

- Search Reddit subreddits
- Extract thread discussions
- Scrape comments
- Analyze workforce discussions

## Development

### JSON Dump Feature

The application includes a comprehensive JSON dump system to save and manage scraped data:

**Enable Auto-Dump:**

1. Find the JSON Dump Manager panel in the UI
2. Toggle "Auto-dump" ON
3. All scraping results will automatically save to JSON

**Manual Dump via API:**

```bash
curl -X PUT http://localhost:8000/api/config/dump-settings \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "auto_dump": true}'
```

**Features:**

- ✅ Automatic or manual data dumps
- ✅ Checklist tracking with statistics
- ✅ Download dumps as JSON files
- ✅ Filter by type or date
- ✅ Complete metadata included

**API Endpoints:**

- `GET /api/dumps/checklist` - View all dumps
- `GET /api/dumps/summary` - Get statistics
- `GET /api/dumps/load/{filename}` - Load dump data
- `DELETE /api/dumps/{filename}` - Delete a dump

### Build for Production

```bash
npm run build
npm start
```

## Technologies

- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS, Recharts
- **Backend**: Python 3.8+, FastAPI, Uvicorn
- **Scrapers**: yfinance, Selenium, undetected-chromedriver, BeautifulSoup4
- **Data**: pandas, numpy

## Notes

- The scrapers use headless Chrome for web scraping
- Rate limiting and delays are implemented to avoid detection
- CORS is configured to allow frontend connections
- Some scrapers may require Chrome/Chromium to be installed

## Troubleshooting

### Python Backend Won't Start

- Ensure Python 3.8+ is installed: `python --version`
- Install dependencies: `cd backend-py && pip install -r requirements.txt`
- Check if port 8000 is available

### Scrapers Not Working

- Install Chrome/Chromium browser
- Update ChromeDriver: `pip install --upgrade undetected-chromedriver`
- Check for firewall/antivirus blocking

### Next.js Build Errors

- Clear cache: `rm -rf .next node_modules && npm install`
- Update Next.js: `npm install next@latest react@latest react-dom@latest`
