"""
Financial Data Scraper Module
Scrapes financial data for companies using yfinance
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any
import json
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_service import CompanySymbolDetector, FinancialAnalystAI

logger = logging.getLogger(__name__)


def clean_nan_values(obj: Any) -> Any:
    """Recursively clean NaN and infinity values from data structures"""
    if isinstance(obj, float):
        if pd.isna(obj) or np.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: clean_nan_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(item) for item in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        if pd.isna(obj) or np.isinf(obj):
            return None
        return float(obj)
    return obj


class FinancialDataScraper:
    """Scraper for financial data using yfinance with AI-powered symbol detection and analysis"""
    
    def __init__(self, use_ai_detection: bool = True, use_ai_analysis: bool = True):
        self.history_period = "1y"
        self.use_ai_detection = use_ai_detection
        self.use_ai_analysis = use_ai_analysis
        self.symbol_detector = CompanySymbolDetector() if use_ai_detection else None
        self.financial_analyst = FinancialAnalystAI() if use_ai_analysis else None
        
    def resolve_company_to_symbol(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Resolve company name to Yahoo Finance symbol using AI
        
        Args:
            company_name: Name of the company
            
        Returns:
            Dictionary with symbol information or None if not found
        """
        if not self.use_ai_detection or not self.symbol_detector:
            logger.warning("AI symbol detection is disabled")
            return None
        
        logger.info(f"Resolving symbol for company: {company_name}")
        result = self.symbol_detector.detect_symbol(company_name)
        
        if result.get('yahoo_symbol'):
            logger.info(f"✓ Found symbol: {result['yahoo_symbol']} for {company_name}")
        else:
            logger.warning(f"✗ No public symbol found for {company_name}")
            logger.info(f"Reasoning: {result.get('reasoning', 'Unknown')}")
        
        return result
    
    def get_company_financial_data(
        self, 
        ticker_symbol: str, 
        include_history: bool = True,
        company_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch comprehensive financial data for a company.
        
        Args:
            ticker_symbol: Stock ticker symbol (e.g., "AAPL", "DHUNINV.NS")
            include_history: Whether to include historical price data
            company_name: Optional company name for better error messages
            
        Returns:
            Dictionary containing financial data
        """
        display_name = company_name or ticker_symbol
        print(f"Fetching Financial Data for: {display_name}")
        logger.info(f"Using symbol: {ticker_symbol}")
        
        # Create ticker object
        ticker = yf.Ticker(ticker_symbol)
        
        try:
            # Get company info
            info = ticker.info
            
            # Check if we got valid data
            if not info or 'symbol' not in info:
                raise ValueError(f"No data found for symbol: {ticker_symbol}")
        except Exception as e:
            logger.error(f"Error fetching data for {ticker_symbol}: {e}")
            # Return error information
            return {
                'ticker': ticker_symbol,
                'error': str(e),
                'info': {},
                'financials': None,
                'balance_sheet': None,
                'cashflow': None,
                'history': None,
                'history_data': None,
                'history_summary': None,
                'summary': {
                    'company_name': display_name,
                    'error': str(e)
                }
            }
        
        # Get financial statements
        financials = ticker.financials
        balance_sheet = ticker.balance_sheet
        cashflow = ticker.cashflow
        
        # Get historical data if requested
        history = None
        history_data = None
        history_summary = None
        
        if include_history:
            history = ticker.history(period=self.history_period)
            if history is not None and not history.empty:
                # Extract historical data for charting
                history_data = self._extract_history_for_chart(history)
                # Create summary statistics
                history_summary = self._summarize_history(history)
            
        return {
            'ticker': ticker_symbol,
            'info': info,
            'financials': self._convert_dataframe(financials),
            'balance_sheet': self._convert_dataframe(balance_sheet),
            'cashflow': self._convert_dataframe(cashflow),
            'history': self._convert_dataframe(history) if history is not None else None,
            'history_data': history_data,  # For charting
            'history_summary': history_summary,  # For AI analysis
            'summary': self._get_company_summary(info)
        }
    
    def _convert_dataframe(self, df: Optional[pd.DataFrame]) -> Optional[Dict]:
        """Convert DataFrame to JSON-serializable format"""
        if df is None or df.empty:
            return None
        
        # Replace NaN and infinity values
        df = df.replace([np.inf, -np.inf], None)
        df = df.fillna(value=None)
        
        # Convert to dict
        return {
            'columns': df.columns.tolist(),
            'index': df.index.astype(str).tolist(),
            'data': df.values.tolist()
        }
    
    def _get_company_summary(self, info: Dict) -> Dict[str, Any]:
        """Extract key company information and clean NaN values"""
        summary = {
            'company_name': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'employees': info.get('fullTimeEmployees'),
            'website': info.get('website', 'N/A'),
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('trailingPE'),
            'revenue': info.get('totalRevenue'),
            'profit_margin': info.get('profitMargins'),
            'current_price': info.get('currentPrice'),
            'currency': info.get('currency', 'USD'),
            'country': info.get('country', 'N/A'),
            'description': info.get('longBusinessSummary', 'N/A')
        }
        # Clean NaN and infinity values
        return clean_nan_values(summary)
    
    def _extract_history_for_chart(self, history: pd.DataFrame) -> list:
        """Extract historical data suitable for charting"""
        if history is None or history.empty:
            return []
        
        chart_data = []
        for date, row in history.iterrows():
            chart_data.append({
                'date': date.isoformat(),
                'open': float(row['Open']) if pd.notna(row['Open']) else 0,
                'high': float(row['High']) if pd.notna(row['High']) else 0,
                'low': float(row['Low']) if pd.notna(row['Low']) else 0,
                'close': float(row['Close']) if pd.notna(row['Close']) else 0,
                'volume': int(row['Volume']) if pd.notna(row['Volume']) else 0
            })
        
        return chart_data
    
    def _summarize_history(self, history: pd.DataFrame) -> Dict[str, Any]:
        """Create summary statistics from historical data"""
        if history is None or history.empty:
            return {}
        
        close_prices = history['Close'].dropna()
        
        if len(close_prices) == 0:
            return {}
        
        first_close = float(close_prices.iloc[0])
        last_close = float(close_prices.iloc[-1])
        price_change = last_close - first_close
        price_change_percent = (price_change / first_close * 100) if first_close != 0 else 0
        
        summary = {
            'first_close': round(first_close, 2),
            'last_close': round(last_close, 2),
            'price_change': round(price_change, 2),
            'price_change_percent': round(price_change_percent, 2),
            'highest_price': round(float(close_prices.max()), 2),
            'lowest_price': round(float(close_prices.min()), 2),
            'average_price': round(float(close_prices.mean()), 2),
            'volatility': round(float(close_prices.std()), 2),
            'data_points': len(close_prices)
        }
        # Clean any remaining NaN values
        return clean_nan_values(summary)
    
    def search_workforce_signals_by_company(
        self, 
        company_name: str
    ) -> Dict[str, Any]:
        """
        Search for workforce signals by company name (auto-detects symbol)
        
        Args:
            company_name: Name of the company
            
        Returns:
            Dictionary containing workforce signals or error information
        """
        # Try to resolve company name to symbol
        symbol_info = self.resolve_company_to_symbol(company_name)
        
        if not symbol_info or not symbol_info.get('yahoo_symbol'):
            # No public symbol found
            return {
                'company_name': company_name,
                'ticker': None,
                'signals': [],
                'metadata': {
                    'is_publicly_traded': False,
                    'reasoning': symbol_info.get('reasoning', 'Company is privately held or not found') if symbol_info else 'Symbol detection unavailable',
                    'parent_company': symbol_info.get('parent_company') if symbol_info else None,
                    'scrape_timestamp': datetime.now().isoformat()
                },
                'ai_detection': symbol_info
            }
        
        # Use detected symbol (could be from parent company)
        ticker_symbol = symbol_info['yahoo_symbol']
        
        # Determine display name
        if symbol_info.get('parent_company'):
            display_name = f"{company_name} (via {symbol_info['parent_company']})"
        else:
            display_name = company_name
        
        return self.search_workforce_signals(
            ticker_symbol=ticker_symbol,
            company_name=display_name,
            symbol_info=symbol_info
        )
    
    def search_workforce_signals(
        self, 
        ticker_symbol: str,
        company_name: Optional[str] = None,
        symbol_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for workforce-related signals in financial data
        
        Args:
            ticker_symbol: Stock ticker symbol
            company_name: Optional company name for display
            symbol_info: Optional AI detection information
            
        Returns:
            Dictionary containing workforce intelligence signals from financial metrics
        """
        data = self.get_company_financial_data(ticker_symbol, include_history=True, company_name=company_name)
        info = data['info']
        
        # Financial metrics are now only displayed in charts, not as signals
        signals = []
        
        # No longer adding financial signals to the list
        # Financial data (employee count, profit margins, etc.) will only be shown in the financial chart and summary
        
        result = {
            'ticker': ticker_symbol,
            'company_name': company_name or info.get('longName'),
            'signals': signals,
            'metadata': {
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'scrape_timestamp': datetime.now().isoformat()
            },
            'financial_data': data
        }
        
        # Add AI detection info if available
        if symbol_info:
            result['ai_detection'] = symbol_info
        
        # Add AI financial analysis if enabled
        if self.use_ai_analysis and self.financial_analyst and not data.get('error'):
            try:
                logger.info(f"Generating AI financial analysis for {ticker_symbol}")
                ai_analysis = self.financial_analyst.analyze_financial_data(data)
                result['ai_analysis'] = ai_analysis
            except Exception as e:
                logger.error(f"Failed to generate AI analysis: {e}")
                result['ai_analysis'] = None
        
        # Clean all NaN and infinity values before returning
        return clean_nan_values(result)
