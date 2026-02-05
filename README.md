# NTUC Workforce Intelligence Scraper

A comprehensive full-stack application for scraping and analyzing workforce intelligence signals using AI-powered analysis, multiple data sources, and advanced risk assessment.

## 🎯 Key Features

- **Multi-Source Data Collection**: News, Google News (RSS), Reddit, Financial data
- **AI-Powered Analysis**: Smart relevance filtering and hypothesis generation
- **Historical Data Access**: Google News RSS for accessing older historical articles
- **Risk Hypothesis Engine**: 1-to-1 signal mapping with comprehensive risk analysis
- **Interactive Visualizations**: Charts, risk scores, and source distributions
- **JSON Dump Management**: Save, track, and analyze scraped data
- **Production-Ready**: Monorepo configured for Render (backend) and Vercel (frontend) deployment

## 🏗️ Architecture

- **Frontend**: Next.js 15 with React 19, TypeScript, and Tailwind CSS
- **Backend**: Python FastAPI with FastAPI async capabilities
- **Scrapers**:
  - Financial data (yfinance)
  - News articles (Selenium + undetected-chromedriver)
  - Google News RSS (feedparser) - Historical data access
  - Reddit discussions (Selenium)
- **AI Integration**: OpenAI GPT for relevance filtering and hypothesis generation
- **Deployment**: Monorepo setup with separate configs for Render and Vercel

## ✨ Features

### Data Collection

- **Company-Specific Scraping**: Target specific companies across all data sources
- **General Keyword Search**: Broad workforce intelligence gathering
- **Financial Analysis**: Company financial health and workforce implications
- **Google News RSS**: Access to historical news articles (30 oldest for hypothesis)
- **AI Smart Filtering**: Relevance checking to filter out non-workforce signals

### Analysis & Insights

- **Risk Hypothesis Engine**: AI-powered multi-source risk analysis
  - 1-to-1 signal mapping (52 input signals → 52 supporting signals)
  - Evidence URLs preserved for each signal
  - Primary signals grouped into 8 thematic categories
  - Comprehensive source distribution (News + Social + Financial)
- **Financial Charts**: Interactive stock price visualization
- **AI Financial Analyst**: Automated insights on company health

### Data Management

- **JSON Dump System**: Save, load, and manage scraped datasets
- **Hypothesis from Dumps**: Analyze previously scraped data
- **Dump Browser**: View and download historical scraping results

### User Interface

- **Modern Design**: Clean, responsive UI with Tailwind CSS
- **Real-time Visualization**: Recharts for interactive data display
- **Signal Cards**: Detailed view of each workforce signal with metadata
- **Hypothesis Viewer**: Interactive risk analysis with clickable primary signals

## Getting Started

### Prerequisites

- **Node.js 18+** installed
- **Python 3.9+** installed (Python 3.13 recommended)
- **Chrome browser** (for Selenium scrapers)
- **OpenAI API Key** (for AI-powered features)

### Installation

1. **Clone the repository:**

```bash
git clone <your-repo-url>
cd ntuc-workforce-intelligence-scraper
```

2. **Install Node.js dependencies:**

```bash
npm install
```

3. **Install Python dependencies:**

```bash
cd backend-py
pip install -r requirements.txt
cd ..
```

4. **Configure environment variables:**

Create `.env.local` in the root directory:

```env
NEXT_PUBLIC_PYTHON_BACKEND_URL=http://localhost:8000
PYTHON_BACKEND_URL=http://localhost:8000
```

Create `backend-py/.env` or `backend-py/config.json` with your OpenAI API key:

```env
PORT=8000
FRONTEND_URL=http://localhost:3000,http://localhost:3001
LOG_LEVEL=INFO

# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Alternative: Anthropic Claude
# ANTHROPIC_API_KEY=your-anthropic-api-key-here

# AI Service Provider (openai, anthropic, or mock)
AI_PROVIDER=openai

# AI Model Configuration
OPENAI_MODEL=gpt-4o-mini
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

```

```json
{
  "openai_api_key": "sk-your-api-key-here",
  "general_news_sources": [],
  "company_search_sources": [],
  "scraper_settings": {
    "max_articles": 10
  },
  "google_news_settings": {
    "max_articles": null,
    "default_region": "SG",
    "default_language": "en-SG"
  }
}
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
- **Risk Hypothesis Engine**: [http://localhost:3000/hypothesis](http://localhost:3000/hypothesis)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📁 Project Structure

```
├── app/                    # Next.js app directory
│   ├── api/               # API routes
│   │   ├── scrape/        # Scraping proxy endpoints
│   │   └── dumps/         # Dump management endpoints
│   ├── hypothesis/        # Risk Hypothesis analysis page
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Main scraping page
├── backend-py/            # Python backend
│   ├── scrapers/          # Scraper modules
│   │   ├── __init__.py
│   │   ├── financial_scraper.py    # yfinance integration
│   │   ├── news_scraper.py         # Selenium news scraper
│   │   ├── google_news_rss_scraper.py  # Google News RSS (historical)
│   │   └── reddit_scraper.py       # Reddit discussions
│   ├── documents/         # Documentation
│   │   ├── HYPOTHESIS_ENGINE.md
│   │   ├── GOOGLE_NEWS_SCRAPER.md
│   │   ├── JSON_DUMP_DOCUMENTATION.md
│   │   └── ...
│   ├── dumps/             # Saved scraping results
│   │   ├── debug/         # Debug JSON outputs
│   │   └── *.json         # Dump files
│   ├── hypothesis_engine.py   # Risk analysis engine (1-to-1 mapping)
│   ├── ai_service.py          # OpenAI integration
│   ├── json_dump_manager.py   # Dump management
│   ├── main.py                # FastAPI server
│   ├── config.json            # Configuration
│   └── requirements.txt       # Python dependencies
├── components/            # React components
│   ├── HypothesisViewer.tsx    # Risk analysis UI
│   ├── SignalCard.tsx          # Individual signal display
│   ├── DumpBrowser.tsx         # Dump file browser
│   ├── JSONDumpManager.tsx     # Dump controls
│   └── ...
├── types.ts              # TypeScript type definitions
├── render.yaml           # Render deployment config
├── vercel.json           # Vercel deployment config
├── DEPLOYMENT.md         # Deployment guide
└── README.md
```

## 🔌 API Endpoints

### Python Backend (Port 8000)

#### Scraping Endpoints

- **POST** `/api/scrape` - Main scraping endpoint
  - Modes: `GENERAL`, `COMPANY`, `FINANCIAL`, `NEWS`, `REDDIT`, `GOOGLE_NEWS`
  - Parameters: `mode`, `companyName`, `keywords`, `enable_smart_filtering`, `auto_dump`
- **POST** `/api/scrape/financial?ticker=AAPL` - Financial data only
- **POST** `/api/scrape/news` - News articles only
- **POST** `/api/scrape/reddit` - Reddit discussions only

#### Hypothesis Engine

- **POST** `/api/hypothesis/analyze` - Generate comprehensive risk analysis
  - Body: `{"company_name": "CompanyName", "signals": [...], "financial_data": {...}}`
  - Or: `{"company_name": "CompanyName", "dump_filename": "company_date.json"}`

#### Dump Management

- **GET** `/api/dumps/list` - List all saved dumps
- **GET** `/api/dumps/checklist` - View dump tracking
- **GET** `/api/dumps/load/{filename}` - Load specific dump
- **DELETE** `/api/dumps/{filename}` - Delete a dump
- **GET** `/api/dumps/summary` - Get statistics

#### Health & Info

- **GET** `/health` - Health check endpoint
- **GET** `/` - API information
- **GET** `/docs` - Interactive API documentation (Swagger UI)

### Next.js API (Port 3000)

- **POST** `/api/scrape` - Proxies to Python backend

## 🔍 Scraper Details

### Financial Scraper (yfinance)

Fetches comprehensive company financial data:

- Company information and metrics
- Financial statements (income, balance, cash flow)
- Historical price data (1 year)
- Workforce signals extracted from financial metrics
- Employee count and workforce data

### News Scraper (Selenium)

Uses undetected-chromedriver to bypass bot detection:

- Searches Google/Bing News for company mentions
- Extracts article links and metadata
- Scrapes full article content (5 articles per company)
- Identifies workforce-related themes
- AI-powered relevance filtering

### Google News RSS Scraper (feedparser)

**NEW**: Historical data access via Google News RSS API:

- Fetches 100+ articles from RSS feed
- Metadata only (headlines, dates, source links)
- Selects 30 oldest articles for hypothesis engine
- Bypasses JavaScript-heavy web scraping
- More reliable than Selenium for historical data
- Date range: Can access articles from 2011-present

**Key Difference from News Scraper**:

- **News Scraper**: 5 recent articles with full content analysis
- **Google News RSS**: 30 oldest articles with metadata for historical coverage

### Reddit Scraper (Selenium)

Scrapes Reddit discussions:

- Searches multiple subreddits (e.g., r/singapore, r/askSingapore)
- Extracts thread discussions and comments
- Analyzes workforce-related conversations
- Community sentiment analysis

## 🧠 Development

### Risk Hypothesis Engine (Enhanced)

The Risk Hypothesis Engine performs comprehensive AI-powered risk analysis with **1-to-1 signal mapping**:

**Architecture:**

1. **Signal Preservation** (1-to-1 Mapping):
   - 52 input signals → 52 supporting signals
   - Each supporting signal preserves original URL and metadata
   - No signal condensation or loss

2. **Supporting Signals**:
   - Individual evidence pieces with titles, timeframes, and evidence URLs
   - Source types: news, google_news, social, reddit, financial
   - Severity classification: low, medium, high

3. **Primary Signals** (Thematic Grouping):
   - ~8 thematic categories grouping related supporting signals
   - Examples: OPERATIONAL DEGRADATION, FINANCIAL DISTRESS, WORKFORCE ISSUES
   - Each shows source distribution (News: X, Social: Y, Financial: Z)

4. **AI-Powered Scoring**:
   - Risk scores for each signal (0-100)
   - Overall company risk assessment
   - Major hypothesis synthesizing all evidence

**Example Flow:**

```
42 News signals + 10 Social signals = 52 input signals
           ↓
52 supporting signals (preserved with URLs)
           ↓
8 primary signals (grouped by theme):
  - OPERATIONAL DEGRADATION: 8 signals (News: 6, Social: 2)
  - FINANCIAL DISTRESS: 7 signals (News: 5, Social: 2)
  - WORKFORCE ISSUES: 10 signals (News: 8, Social: 2)
  - REGULATORY/LEGAL RISKS: 6 signals (News: 6, Social: 0)
  - MARKET PERCEPTION: 8 signals (News: 5, Social: 3)
  - etc.
```

**Features:**

- ✅ 1-to-1 signal mapping (no data loss)
- ✅ Evidence URL preservation
- ✅ Multi-source aggregation (News + Google News + Reddit + Financial)
- ✅ Interactive visualization with source distribution
- ✅ Clickable primary signals to view all supporting evidence
- ✅ AI-generated major hypothesis
- ✅ Debug JSON dumps for validation

**Usage:**

1. Navigate to `/hypothesis` in the web interface
2. Enter a company name (e.g., "Twelve Cupcakes")
3. Click "Analyze Risk"
4. View primary signals (source counts match input: 42 news + 10 social = 52 total)
5. Click any primary signal to see supporting evidence with URLs

**Validation:**

- Logs confirm: `✓ Created 52 supporting signals from 52 input signals`
- Logs confirm: `✓ All 52 supporting signals successfully assigned`
- Logs confirm: `Source distribution validation: News=42/42, Social=10/10`

For more details, see:

- [HYPOTHESIS_ENGINE.md](backend-py/documents/HYPOTHESIS_ENGINE.md)
- [HYPOTHESIS_ENGINE_ARCHITECTURE.md](backend-py/documents/HYPOTHESIS_ENGINE_ARCHITECTURE.md)

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

## 🚀 Deployment

This project is configured for production deployment as a **monorepo**:

- **Backend**: Deploy to [Render](https://render.com) (Python FastAPI)
- **Frontend**: Deploy to [Vercel](https://vercel.com) (Next.js)

### Quick Deployment

1. **Backend on Render**:
   - Connect GitHub repository
   - Render auto-detects `render.yaml`
   - Set environment variables: `OPENAI_API_KEY`, `FRONTEND_URL`
   - Deploy!

2. **Frontend on Vercel**:
   - Connect GitHub repository
   - Vercel auto-detects Next.js
   - Set environment variable: `NEXT_PUBLIC_PYTHON_BACKEND_URL`
   - Deploy!

3. **Update Cross-References**:
   - Update `FRONTEND_URL` in Render with your Vercel URL
   - Both services auto-redeploy

### Monitoring

- **Backend Health**: `https://your-backend.onrender.com/health`
- **API Docs**: `https://your-backend.onrender.com/docs`
- **Frontend**: `https://your-project.vercel.app`

---

## 🛠️ Technologies

### Frontend

- **Next.js 15**: React framework with App Router
- **React 19**: Latest React features
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Recharts**: Interactive data visualizations

### Backend

- **Python 3.9+**: Core language (3.13 recommended)
- **FastAPI**: Modern async API framework
- **Uvicorn**: ASGI server
- **OpenAI API**: GPT-4 for AI analysis

### Data Collection

- **yfinance**: Financial data
- **Selenium**: Web scraping
- **undetected-chromedriver**: Bot detection bypass
- **feedparser**: Google News RSS parsing
- **BeautifulSoup4**: HTML parsing

### Data Processing

- **pandas**: Data manipulation
- **numpy**: Numerical operations

### Deployment

- **Render**: Backend hosting
- **Vercel**: Frontend hosting
- **Monorepo**: Single repository, separate services

---

## 📝 Notes

- Scrapers use headless Chrome for web scraping
- Rate limiting and delays implemented to avoid detection
- CORS configured for production (supports both local and deployed frontend)
- Google News RSS provides more reliable historical data than web scraping
- Hypothesis engine preserves all signals (1-to-1 mapping) for comprehensive analysis
- Some scrapers may require Chrome/Chromium to be installed locally

---

## 🐛 Troubleshooting

### Python Backend Won't Start

**Issue**: `ModuleNotFoundError` or port conflicts

**Solutions**:

- Ensure Python 3.9+ is installed: `python --version`
- Install dependencies: `cd backend-py && pip install -r requirements.txt`
- Check if port 8000 is available: `netstat -ano | findstr :8000` (Windows)
- Kill conflicting process or change port in `main.py`

### OpenAI API Errors

**Issue**: `AuthenticationError` or `RateLimitError`

**Solutions**:

- Verify API key in `backend-py/config.json` or `.env`
- Check API key has sufficient credits: https://platform.openai.com/usage
- Check rate limits: https://platform.openai.com/account/limits

### Scrapers Not Working

**Issue**: ChromeDriver errors or timeout

**Solutions**:

- Install Chrome/Chromium browser
- Update ChromeDriver: `pip install --upgrade undetected-chromedriver`
- Check firewall/antivirus not blocking browser automation
- Try increasing timeout values in scraper files

### Hypothesis Engine - Signal Count Mismatch

**Issue**: Source distribution doesn't add up to input signals

**Solutions**:

- Check logs for validation messages: `✓ Created 52 supporting signals from 52 input signals`
- View debug files in `backend-py/dumps/debug/assignment_analysis.json`
- Ensure all source types are properly mapped in `hypothesis_engine.py`
- Look for unassigned signals in logs

### Google News RSS Not Fetching Data

**Issue**: Empty results or connection errors

**Solutions**:

- Check internet connection
- Verify `google_news_settings` in `config.json`
- Try different region/language codes
- Check if Google News RSS is accessible: https://news.google.com/rss

### Reddit Connection Error (WinError 10061)

**Issue**: `Failed to establish a new connection: [WinError 10061]`

**This means Reddit is blocking the connection.**

**Solutions**:

1. **Use a VPN or different network** - Reddit may be blocking your IP/network
2. **Check firewall/antivirus** - Allow Python/outbound connections to reddit.com
3. **Skip Reddit scraping** - Disable in scraper settings or use only other sources
4. **Use Reddit's Official API** (recommended for production):
   - Create app at https://www.reddit.com/prefs/apps
   - Use PRAW library instead of direct scraping
   - See [backend-py/README.md](backend-py/README.md) for details

**Note**: Reddit actively blocks automated requests. The scraper has retry logic but may still fail depending on your network/location.

### CORS Errors in Production

**Issue**: Frontend can't connect to backend API

**Solutions**:

- Verify `FRONTEND_URL` environment variable in Render matches your Vercel URL exactly
- Check CORS middleware in `backend-py/main.py` includes your frontend domain
- Ensure using HTTPS for production URLs
- Clear browser cache and retry

### Next.js Build Errors

**Issue**: Build fails with TypeScript or dependency errors

**Solutions**:

- Clear cache: `rm -rf .next node_modules && npm install`
- Update Next.js: `npm install next@latest react@latest react-dom@latest`
- Check Node.js version: `node --version` (should be 18+)
- Review build logs in Vercel dashboard for specific errors

---

**Last Updated**: February 4, 2026  
**Version**: 2.0 (Enhanced with Google News RSS, 1-to-1 signal mapping, and production deployment)
