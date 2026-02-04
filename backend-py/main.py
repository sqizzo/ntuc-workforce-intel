"""
FastAPI Server for Workforce Intelligence Scraping
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import logging
import json
import os

from scrapers.financial_scraper import FinancialDataScraper
from scrapers.news_scraper import NewsSearchScraper
from scrapers.reddit_scraper import RedditScraper
from scrapers.google_news_rss_scraper import GoogleNewsRSSScraper
from json_dump_manager import JSONDumpManager
from hypothesis_engine import HypothesisEngine
from ai_service import AIService, WorkforceRelevanceFilter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
def load_config():
    """Load configuration from config.json"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {
        "general_news_sources": [],
        "company_search_sources": [],
        "scraper_settings": {"max_articles": 10}
    }

CONFIG = load_config()

# Initialize JSON dump manager
dump_settings = CONFIG.get('json_dump_settings', {})
dump_manager = JSONDumpManager(
    dump_dir=dump_settings.get('dump_directory', 'dumps')
)

# Initialize AI service and hypothesis engine
ai_service = AIService()
hypothesis_engine = HypothesisEngine(ai_service)
relevance_filter = WorkforceRelevanceFilter(ai_service)

# Create FastAPI app
app = FastAPI(
    title="NTUC Workforce Intelligence Scraper API",
    description="Backend API for scraping workforce intelligence signals",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ScraperMode(str, Enum):
    GENERAL = "GENERAL"
    COMPANY = "COMPANY"
    FINANCIAL = "FINANCIAL"
    NEWS = "NEWS"
    REDDIT = "REDDIT"
    GOOGLE_NEWS = "GOOGLE_NEWS"


class ScrapeRequest(BaseModel):
    mode: ScraperMode
    keywords: Optional[List[str]] = Field(default=None, description="Keywords for general mode")
    companyName: Optional[str] = Field(default=None, description="Company name for company mode")
    ticker: Optional[str] = Field(default=None, description="Stock ticker for financial mode")
    subreddit: Optional[str] = Field(default="singapore", description="Subreddit for Reddit scraping")
    max_articles: Optional[int] = Field(default=10, description="Maximum articles to scrape")
    auto_dump: Optional[bool] = Field(default=None, description="Automatically dump results to JSON")
    before_date: Optional[str] = Field(default=None, description="Filter data before this date (YYYY-MM-DD format)")
    enable_smart_filtering: Optional[bool] = Field(default=True, description="Enable AI-powered relevance filtering")


class DumpRequest(BaseModel):
    data: Any = Field(description="Data to dump")
    dump_type: str = Field(description="Type of dump (general, company, financial, etc.)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    filename: Optional[str] = Field(default=None, description="Custom filename for the dump")


class WorkforceSignal(BaseModel):
    id: str
    source_type: str
    source_name: str
    source_url: str
    ingestion_timestamp: str
    extracted_text: str
    matched_keywords: Optional[List[str]] = None
    inferred_workforce_theme: Optional[str] = None
    company_name: Optional[str] = None
    parent_company: Optional[str] = None
    workforce_signal_type: Optional[str] = None
    confidence_note: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


# Initialize scrapers
financial_scraper = FinancialDataScraper()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NTUC Workforce Intelligence Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "scrape": "/api/scrape",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "workforce-scraper"}


@app.post("/api/scrape")
async def scrape_workforce_signals(request: ScrapeRequest):
    """
    Main scraping endpoint - routes to appropriate scraper based on mode
    """
    try:
        logger.info(f"Scraping request: mode={request.mode}, keywords={request.keywords}, company={request.companyName}")
        
        signals = []
        financial_result = None
        
        if request.mode == ScraperMode.FINANCIAL:
            # Financial data scraping
            if not request.ticker and not request.companyName:
                raise HTTPException(status_code=400, detail="Ticker or company name required for financial mode")
            
            ticker = request.ticker or request.companyName
            result = financial_scraper.search_workforce_signals(ticker)
            signals = result['signals']
            
        elif request.mode == ScraperMode.NEWS:
            # News search scraping
            if not request.keywords:
                raise HTTPException(status_code=400, detail="Keywords required for news mode")
            
            # Get enabled general sources
            general_sources = [s for s in CONFIG.get('general_news_sources', []) if s.get('enabled', True)]
            max_articles = request.max_articles or CONFIG.get('scraper_settings', {}).get('max_articles', 10)
            
            news_scraper = NewsSearchScraper(max_articles=max_articles, general_sources=general_sources)
            signals = news_scraper.search_workforce_signals(request.keywords, before_date=request.before_date)
            
        elif request.mode == ScraperMode.REDDIT:
            # Reddit scraping - search across multiple subreddits
            default_subreddits = CONFIG.get('reddit_settings', {}).get('default_subreddits', ['singapore'])
            subreddits_to_search = [request.subreddit] if request.subreddit else default_subreddits
            
            reddit_scraper = RedditScraper()
            for subreddit in subreddits_to_search:
                try:
                    subreddit_signals = reddit_scraper.search_workforce_signals(
                        subreddit=subreddit,
                        keywords=request.keywords,
                        before_date=request.before_date
                    )
                    signals.extend(subreddit_signals)
                    logger.info(f"Found {len(subreddit_signals)} signals from r/{subreddit}")
                except Exception as e:
                    logger.warning(f"Failed to scrape r/{subreddit}: {e}")
            
        elif request.mode == ScraperMode.GOOGLE_NEWS:
            # Google News scraping - fetch headlines, dates, and source links via RSS
            if not request.keywords and not request.companyName:
                raise HTTPException(status_code=400, detail="Keywords or company name required for Google News mode")
            
            query = request.companyName if request.companyName else ' '.join(request.keywords)
            # Get max_articles from request, config, or None (fetch all)
            max_articles = request.max_articles if request.max_articles is not None else CONFIG.get('google_news_settings', {}).get('max_articles')
            
            google_news_scraper = GoogleNewsRSSScraper(max_articles=max_articles)
            signals = google_news_scraper.search_workforce_signals(
                query=query,
                before_date=request.before_date
            )
            logger.info(f"Found {len(signals)} signals from Google News for '{query}'")
            
        elif request.mode == ScraperMode.COMPANY:
            # Company-specific scraping (combines all sources)
            if not request.companyName:
                raise HTTPException(status_code=400, detail="Company name required for company mode")
            
            financial_result = None
            
            # Try financial data first with AI symbol detection
            try:
                financial_result = financial_scraper.search_workforce_signals_by_company(request.companyName)
                signals.extend(financial_result['signals'])
            except Exception as e:
                logger.warning(f"Financial scraping failed: {e}")
            
            # Add news scraping with company search sources
            try:
                company_sources = [s for s in CONFIG.get('company_search_sources', []) if s.get('enabled', True)]
                news_scraper = NewsSearchScraper(max_articles=5, company_sources=company_sources)
                news_signals = news_scraper.search_workforce_signals_company(request.companyName, before_date=request.before_date)
                signals.extend(news_signals)
            except Exception as e:
                logger.warning(f"News scraping failed: {e}")
            
            # Add Reddit scraping for company mentions across multiple subreddits
            try:
                reddit_subreddits = CONFIG.get('reddit_settings', {}).get('default_subreddits', ['singapore'])
                reddit_scraper = RedditScraper()
                
                for subreddit in reddit_subreddits:
                    try:
                        subreddit_signals = reddit_scraper.search_workforce_signals(
                            subreddit=subreddit,
                            keywords=[request.companyName],
                            before_date=request.before_date
                        )
                        signals.extend(subreddit_signals)
                        logger.info(f"Found {len(subreddit_signals)} Reddit signals from r/{subreddit} for {request.companyName}")
                    except Exception as sub_e:
                        logger.warning(f"Failed to scrape r/{subreddit}: {sub_e}")
            except Exception as e:
                logger.warning(f"Reddit scraping failed: {e}")
            
            # Add Google News scraping for more historical coverage via RSS
            # Use oldest_only=30 to get historical data for hypothesis engine
            try:
                # Get max_articles from config (None = fetch all)
                max_gnews = CONFIG.get('google_news_settings', {}).get('max_articles')
                google_news_scraper = GoogleNewsRSSScraper(max_articles=max_gnews)
                gnews_signals = google_news_scraper.search_workforce_signals(
                    query=request.companyName,
                    before_date=request.before_date,
                    oldest_only=30  # Only use 30 oldest articles for hypothesis engine
                )
                signals.extend(gnews_signals)
                logger.info(f"Found {len(gnews_signals)} oldest signals from Google News for {request.companyName}")
            except Exception as e:
                logger.warning(f"Google News scraping failed: {e}")
            
            # Extract actual workforce data from signals if we have them
            if financial_result and signals:
                try:
                    logger.info(f"Extracting workforce data from {len(signals)} signals...")
                    from ai_service import AIService
                    ai_service = AIService()
                    workforce_data = ai_service.extract_workforce_data(request.companyName, signals)
                    logger.info(f"Workforce extraction result: {workforce_data}")
                    
                    if workforce_data and workforce_data.get('employee_count'):
                        financial_result['actual_workforce'] = workforce_data
                        logger.info(f"✓ Extracted actual workforce data: {workforce_data.get('employee_count')} employees")
                    else:
                        logger.info("No employee count found in workforce extraction")
                except Exception as e:
                    logger.error(f"Workforce extraction failed: {e}", exc_info=True)
                    # Don't fail the entire request, just skip this enhancement
            
            # Apply AI-powered relevance filtering for company mode signals
            if signals and request.enable_smart_filtering:
                logger.info(f"Applying AI relevance filtering to {len(signals)} company signals...")
                filtered_signals = []
                
                for signal in signals:
                    try:
                        # Get title and content for relevance check
                        title = signal.get('metadata', {}).get('title', '') or signal.get('post_title', '') or signal.get('extracted_text', '')[:100]
                        content = signal.get('extracted_text', '') or signal.get('post_text', '')
                        
                        # Check relevance WITH company context
                        relevance_result = relevance_filter.check_relevance(title, content[:500], company_name=request.companyName)
                        
                        # Add relevance info to signal
                        signal['relevance'] = relevance_result
                        
                        # Only keep relevant signals
                        if relevance_result.get('is_relevant', False):
                            filtered_signals.append(signal)
                        else:
                            logger.info(f"Filtered out irrelevant signal: {title[:50]}... - {relevance_result.get('rationale', 'No reason')[:50]}")
                            
                    except Exception as e:
                        logger.warning(f"Error filtering signal: {e}, keeping signal by default")
                        filtered_signals.append(signal)
                
                original_count = len(signals)
                signals = filtered_signals
                logger.info(f"Relevance filtering complete: {original_count} -> {len(signals)} signals (filtered out {original_count - len(signals)})")
            
            # If we have financial data, return the full structure
            if financial_result:
                financial_result['signals'] = signals  # Include all signals
                logger.info(f"Successfully scraped {len(signals)} signals with financial data")
                return financial_result
            
        elif request.mode == ScraperMode.GENERAL:
            # General keyword-based scraping
            if not request.keywords:
                raise HTTPException(status_code=400, detail="Keywords required for general mode")
            
            # Get enabled general sources
            general_sources = [s for s in CONFIG.get('general_news_sources', []) if s.get('enabled', True)]
            max_articles = request.max_articles or CONFIG.get('scraper_settings', {}).get('max_articles', 10)
            
            # News scraping with general sources
            try:
                news_scraper = NewsSearchScraper(max_articles=max_articles, general_sources=general_sources)
                news_signals = news_scraper.search_workforce_signals(request.keywords, before_date=request.before_date)
                signals.extend(news_signals)
            except Exception as e:
                logger.warning(f"News scraping failed: {e}")
            
            # Reddit scraping
            try:
                reddit_scraper = RedditScraper()
                reddit_signals = reddit_scraper.search_workforce_signals(
                    keywords=request.keywords,
                    before_date=request.before_date
                )
                signals.extend(reddit_signals)
            except Exception as e:
                logger.warning(f"Reddit scraping failed: {e}")
        
        logger.info(f"Successfully scraped {len(signals)} signals")
        
        # Apply AI-powered relevance filtering
        if signals and request.enable_smart_filtering:
            logger.info(f"Applying AI relevance filtering to {len(signals)} signals...")
            filtered_signals = []
            
            for signal in signals:
                try:
                    # Get title and content for relevance check
                    title = signal.get('metadata', {}).get('title', '') or signal.get('post_title', '') or signal.get('extracted_text', '')[:100]
                    content = signal.get('extracted_text', '') or signal.get('post_text', '')
                    
                    # Check relevance (no company context for general mode)
                    relevance_result = relevance_filter.check_relevance(title, content[:500], company_name=None)
                    
                    # Add relevance info to signal
                    signal['relevance'] = relevance_result
                    
                    # Only keep relevant signals
                    if relevance_result.get('is_relevant', False):
                        filtered_signals.append(signal)
                    else:
                        logger.info(f"Filtered out irrelevant signal: {title[:50]}... - {relevance_result.get('rationale', 'No reason')[:50]}")
                        
                except Exception as e:
                    logger.warning(f"Error filtering signal: {e}, keeping signal by default")
                    filtered_signals.append(signal)
            
            original_count = len(signals)
            signals = filtered_signals
            logger.info(f"Relevance filtering complete: {original_count} -> {len(signals)} signals (filtered out {original_count - len(signals)})")
        
        # Auto-dump if enabled
        auto_dump = request.auto_dump if request.auto_dump is not None else CONFIG.get('json_dump_settings', {}).get('auto_dump', False)
        if auto_dump and dump_settings.get('enabled', True):
            try:
                dump_metadata = {
                    "mode": request.mode,
                    "keywords": request.keywords,
                    "company_name": request.companyName,
                    "signal_count": len(signals)
                }
                dump_result = dump_manager.dump_data(
                    data=signals if not financial_result else financial_result,
                    dump_type=request.mode.lower(),
                    metadata=dump_metadata
                )
                logger.info(f"Auto-dumped data: {dump_result.get('filename')}")
            except Exception as e:
                logger.warning(f"Auto-dump failed: {e}")
        
        return signals
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scraping error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@app.post("/api/scrape/financial")
async def scrape_financial(ticker: str, include_history: bool = True):
    """
    Scrape financial data for a specific company ticker
    """
    try:
        logger.info(f"Financial scraping: ticker={ticker}")
        result = financial_scraper.search_workforce_signals(ticker)
        return result
    except Exception as e:
        logger.error(f"Financial scraping error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Financial scraping failed: {str(e)}")


@app.post("/api/scrape/news")
async def scrape_news(keywords: List[str], max_articles: int = 10):
    """
    Scrape news articles based on keywords
    """
    try:
        logger.info(f"News scraping: keywords={keywords}")
        news_scraper = NewsSearchScraper(max_articles=max_articles)
        signals = news_scraper.search_workforce_signals(keywords)
        return {"signals": signals, "count": len(signals)}
    except Exception as e:
        logger.error(f"News scraping error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"News scraping failed: {str(e)}")


@app.post("/api/scrape/reddit")
async def scrape_reddit(subreddit: str = "singapore", keywords: Optional[List[str]] = None):
    """
    Scrape Reddit discussions
    """
    try:
        logger.info(f"Reddit scraping: subreddit={subreddit}, keywords={keywords}")
        reddit_scraper = RedditScraper()
        signals = reddit_scraper.search_workforce_signals(
            subreddit=subreddit,
            keywords=keywords
        )
        return {"signals": signals, "count": len(signals)}
    except Exception as e:
        logger.error(f"Reddit scraping error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Reddit scraping failed: {str(e)}")


@app.get("/api/config/news-sources")
async def get_news_sources():
    """
    Get configured news sources (both general and company-specific)
    """
    return {
        "general_sources": CONFIG.get('general_news_sources', []),
        "company_sources": CONFIG.get('company_search_sources', [])
    }


@app.post("/api/config/news-sources")
async def add_news_source(source: Dict[str, Any]):
    """
    Add a new news source (general or company-specific)
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        
        source_type = source.get('type', 'general')  # 'general' or 'company'
        
        # Validate source
        if source_type == 'general' and 'url' not in source:
            raise HTTPException(status_code=400, detail="General source must have a 'url' field")
        elif source_type == 'company' and 'search_url' not in source:
            raise HTTPException(status_code=400, detail="Company source must have a 'search_url' field")
        
        # Add to appropriate config array
        source['enabled'] = source.get('enabled', True)
        if source_type == 'company':
            if 'company_search_sources' not in CONFIG:
                CONFIG['company_search_sources'] = []
            CONFIG['company_search_sources'].append(source)
        else:
            if 'general_news_sources' not in CONFIG:
                CONFIG['general_news_sources'] = []
            CONFIG['general_news_sources'].append(source)
        
        # Save to file
        with open(config_path, 'w') as f:
            json.dump(CONFIG, f, indent=2)
        
        return {"message": "News source added successfully", "source": source}
    except Exception as e:
        logger.error(f"Error adding news source: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/config/news-sources/{source_type}/{index}")
async def update_news_source(source_type: str, index: int, source: Dict[str, Any]):
    """
    Update an existing news source
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        
        sources_key = 'company_search_sources' if source_type == 'company' else 'general_news_sources'
        
        if index < 0 or index >= len(CONFIG.get(sources_key, [])):
            raise HTTPException(status_code=404, detail="News source not found")
        
        CONFIG[sources_key][index] = source
        
        # Save to file
        with open(config_path, 'w') as f:
            json.dump(CONFIG, f, indent=2)
        
        return {"message": "News source updated successfully", "source": source}
    except Exception as e:
        logger.error(f"Error updating news source: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/config/news-sources/{source_type}/{index}")
async def delete_news_source(source_type: str, index: int):
    """
    Delete a news source
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        
        sources_key = 'company_search_sources' if source_type == 'company' else 'general_news_sources'
        
        if index < 0 or index >= len(CONFIG.get(sources_key, [])):
            raise HTTPException(status_code=404, detail="News source not found")
        
        deleted = CONFIG[sources_key].pop(index)
        
        # Save to file
        with open(config_path, 'w') as f:
            json.dump(CONFIG, f, indent=2)
        
        return {"message": "News source deleted successfully", "deleted": deleted}
    except Exception as e:
        logger.error(f"Error deleting news source: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# JSON Dump Endpoints

@app.post("/api/dumps/create")
async def create_dump(request: DumpRequest):
    """
    Manually create a JSON dump of provided data
    """
    try:
        result = dump_manager.dump_data(
            data=request.data,
            dump_type=request.dump_type,
            metadata=request.metadata,
            filename=request.filename
        )
        
        if result["success"]:
            return {
                "message": "Data dumped successfully",
                "dump_info": result["checklist_entry"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Error creating dump: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dumps/checklist")
async def get_dump_checklist():
    """
    Get the complete dump checklist
    """
    try:
        checklist = dump_manager.get_checklist()
        return checklist
    except Exception as e:
        logger.error(f"Error getting checklist: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dumps/summary")
async def get_dump_summary():
    """
    Get summary statistics of all dumps
    """
    try:
        summary = dump_manager.get_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dumps/{filename}")
async def get_dump_by_filename(filename: str):
    """
    Get information about a specific dump
    """
    try:
        dump_info = dump_manager.get_dump_by_filename(filename)
        if dump_info:
            return dump_info
        else:
            raise HTTPException(status_code=404, detail="Dump not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dump: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dumps/load/{filename}")
async def load_dump(filename: str):
    """
    Load and return the contents of a dump file
    """
    try:
        data = dump_manager.load_dump(filename)
        if data:
            return data
        else:
            raise HTTPException(status_code=404, detail="Dump file not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading dump: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/dumps/{filename}")
async def delete_dump(filename: str):
    """
    Delete a specific dump file
    """
    try:
        success = dump_manager.delete_dump(filename)
        if success:
            return {"message": "Dump deleted successfully", "filename": filename}
        else:
            raise HTTPException(status_code=404, detail="Dump not found or could not be deleted")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dump: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dumps/type/{dump_type}")
async def get_dumps_by_type(dump_type: str):
    """
    Get all dumps of a specific type
    """
    try:
        dumps = dump_manager.get_dumps_by_type(dump_type)
        return {"dump_type": dump_type, "count": len(dumps), "dumps": dumps}
    except Exception as e:
        logger.error(f"Error getting dumps by type: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dumps/date/{date_str}")
async def get_dumps_by_date(date_str: str):
    """
    Get all dumps from a specific date (YYYY-MM-DD format)
    """
    try:
        dumps = dump_manager.get_dumps_by_date(date_str)
        return {"date": date_str, "count": len(dumps), "dumps": dumps}
    except Exception as e:
        logger.error(f"Error getting dumps by date: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/dumps/clear-all")
async def clear_all_dumps():
    """
    Clear all dumps (use with caution)
    """
    try:
        success = dump_manager.clear_all_dumps()
        if success:
            return {"message": "All dumps cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear dumps")
    except Exception as e:
        logger.error(f"Error clearing dumps: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config/dump-settings")
async def get_dump_settings():
    """
    Get current JSON dump settings
    """
    return CONFIG.get('json_dump_settings', {})


@app.put("/api/config/dump-settings")
async def update_dump_settings(settings: Dict[str, Any]):
    """
    Update JSON dump settings
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        
        CONFIG['json_dump_settings'] = settings
        
        # Save to file
        with open(config_path, 'w') as f:
            json.dump(CONFIG, f, indent=2)
        
        # Reinitialize dump manager with new settings
        global dump_manager
        dump_manager = JSONDumpManager(
            dump_dir=settings.get('dump_directory', 'dumps')
        )
        
        return {"message": "Dump settings updated successfully", "settings": settings}
    except Exception as e:
        logger.error(f"Error updating dump settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dumps/list")
async def list_dumps():
    """
    List all available dump files
    """
    try:
        dump_dir = dump_settings.get('dump_directory', 'dumps')
        dump_path = os.path.join(os.path.dirname(__file__), dump_dir)
        
        if not os.path.exists(dump_path):
            return {"dumps": []}
        
        dumps = []
        for filename in os.listdir(dump_path):
            if filename.endswith('.json'):
                file_path = os.path.join(dump_path, filename)
                stat = os.stat(file_path)
                
                # Try to read metadata from file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        metadata = data.get('metadata', {}) if isinstance(data, dict) else {}
                        
                        # Count signals
                        if isinstance(data, list):
                            signal_count = len(data)
                        elif isinstance(data, dict) and 'signals' in data:
                            signal_count = len(data.get('signals', []))
                        else:
                            signal_count = 0
                        
                        dumps.append({
                            'filename': filename,
                            'size': stat.st_size,
                            'created': stat.st_ctime,
                            'modified': stat.st_mtime,
                            'metadata': metadata,
                            'signal_count': signal_count
                        })
                except Exception as e:
                    logger.warning(f"Error reading dump file {filename}: {e}")
                    dumps.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'created': stat.st_ctime,
                        'modified': stat.st_mtime,
                        'metadata': {},
                        'signal_count': 0
                    })
        
        # Sort by modified time, newest first
        dumps.sort(key=lambda x: x['modified'], reverse=True)
        
        return {"dumps": dumps}
    except Exception as e:
        logger.error(f"Error listing dumps: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dumps/load/{filename}")
async def load_dump(filename: str):
    """
    Load a specific dump file
    """
    try:
        dump_dir = dump_settings.get('dump_directory', 'dumps')
        dump_path = os.path.join(os.path.dirname(__file__), dump_dir)
        file_path = os.path.join(dump_path, filename)
        
        # Security check - ensure filename doesn't contain path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Dump file not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded dump file: {filename}")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading dump: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


class HypothesisAnalysisRequest(BaseModel):
    """Request model for hypothesis analysis"""
    company_name: str = Field(..., description="Name of the company to analyze")
    signals: Optional[List[Dict[str, Any]]] = Field(None, description="Signals data from scraping")
    financial_data: Optional[Dict[str, Any]] = Field(None, description="Financial data from scraping")
    dump_filename: Optional[str] = Field(None, description="Specific dump file to analyze (legacy)")


@app.post("/api/hypothesis/analyze")
async def analyze_hypothesis(request: HypothesisAnalysisRequest):
    """
    Generate risk hypothesis analysis for a company based on available data.
    Data can be provided directly (signals, financial_data) or loaded from dump file.
    """
    try:
        logger.info(f"Starting hypothesis analysis for: {request.company_name}")
        
        # Load data for analysis
        news_signals = []
        social_signals = []
        financial_data = None
        
        # Priority 1: Use provided signals and financial data directly
        if request.signals is not None:
            logger.info(f"Using provided signals data ({len(request.signals)} signals)")
            for signal in request.signals:
                source_type = signal.get('source_type', '').lower()
                # Include news, blog, and google_news as news signals
                if source_type in ['news', 'blog', 'google_news']:
                    news_signals.append(signal)
                elif source_type in ['social', 'forum', 'reddit']:
                    social_signals.append(signal)
            
            if request.financial_data:
                financial_data = request.financial_data
                logger.info("Using provided financial data")
        
        # Priority 2: Load from specific dump file
        elif request.dump_filename:
            logger.info(f"Loading data from dump file: {request.dump_filename}")
            dump_dir = dump_settings.get('dump_directory', 'dumps')
            dump_path = os.path.join(os.path.dirname(__file__), dump_dir)
            file_path = os.path.join(dump_path, request.dump_filename)
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    dump_data = json.load(f)
                
                # Extract signals from dump
                signals = dump_data.get('signals', [])
                for signal in signals:
                    source_type = signal.get('source_type', '').lower()
                    # Include news, blog, and google_news as news signals
                    if source_type in ['news', 'blog', 'google_news']:
                        news_signals.append(signal)
                    elif source_type in ['social', 'forum', 'reddit']:
                        social_signals.append(signal)
                
                # Extract financial data if available
                financial_data = dump_data.get('financial_data')
        
        # Priority 3: Search dump files by company name (legacy fallback)
        else:
            logger.info(f"Searching dump files for company: {request.company_name}")
            dump_dir = dump_settings.get('dump_directory', 'dumps')
            dump_path = os.path.join(os.path.dirname(__file__), dump_dir)
            
            if os.path.exists(dump_path):
                for filename in os.listdir(dump_path):
                    if filename.endswith('.json') and filename != '_dump_checklist.json':
                        file_path = os.path.join(dump_path, filename)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                dump_data = json.load(f)
                            
                            # Check if this dump is for the requested company
                            dump_company = dump_data.get('company_name', '').lower()
                            search_company = request.company_name.lower()
                            
                            # Match if company name is in the dump's company_name field
                            if search_company in dump_company or dump_company in search_company:
                                # Extract signals
                                signals = dump_data.get('signals', [])
                                for signal in signals:
                                    source_type = signal.get('source_type', '').lower()
                                    # Include news, blog, and google_news as news signals
                                    if source_type in ['news', 'blog', 'google_news']:
                                        news_signals.append(signal)
                                    elif source_type in ['social', 'forum', 'reddit']:
                                        social_signals.append(signal)
                                
                                # Get financial data
                                if not financial_data and dump_data.get('financial_data'):
                                    financial_data = dump_data.get('financial_data')
                                break  # Use the first matching dump
                        except Exception as e:
                            logger.warning(f"Error reading dump {filename}: {e}")
                            continue
        
        if not news_signals and not social_signals:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for company: {request.company_name}"
            )
        
        # Perform hypothesis analysis
        analysis_result = hypothesis_engine.analyze_company_risk(
            company_name=request.company_name,
            news_signals=news_signals,
            social_signals=social_signals,
            financial_data=financial_data
        )
        
        logger.info(f"Hypothesis analysis completed for {request.company_name}")
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in hypothesis analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
