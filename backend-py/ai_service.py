"""
AI Service Module for Company and Symbol Detection
Supports OpenAI and Anthropic APIs
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class AIService:
    """Service for interacting with AI APIs to detect company symbols and information"""
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize AI Service
        
        Args:
            provider: AI provider to use ('openai', 'anthropic', or 'mock')
                     If None, uses AI_PROVIDER env variable or defaults to 'mock'
        """
        self.provider = provider or os.getenv('AI_PROVIDER', 'mock')
        self.api_key = None
        self.client = None
        self.model = None
        
        if self.provider == 'openai':
            self._init_openai()
        elif self.provider == 'anthropic':
            self._init_anthropic()
        elif self.provider == 'mock':
            logger.warning("Using MOCK AI service - responses will be simulated")
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            import openai
            self.api_key = os.getenv('OPENAI_API_KEY')
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            
            self.client = openai.OpenAI(api_key=self.api_key)
            self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            logger.info(f"OpenAI service initialized with model: {self.model}")
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def _init_anthropic(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            self.api_key = os.getenv('ANTHROPIC_API_KEY')
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
            logger.info(f"Anthropic service initialized with model: {self.model}")
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
    # TODO: USE MLAPI BY ELICE
    # def _init_mlapi(self):
    #     import mlapi
    
    def query(self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000) -> str:
        """
        Send a query to the AI service
        
        Args:
            prompt: The prompt to send
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            The AI's response as a string
        """
        if self.provider == 'openai':
            return self._query_openai(prompt, temperature, max_tokens)
        elif self.provider == 'anthropic':
            return self._query_anthropic(prompt, temperature, max_tokens)
        elif self.provider == 'mock':
            return self._query_mock(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _query_openai(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Query OpenAI API"""
        try:
            # Build parameters - some models have restrictions on temperature
            params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a financial markets and corporate structure expert. Always respond with valid JSON only, no markdown formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_completion_tokens": max_tokens
            }
            
            # Only add temperature if it's not the default (1.0)
            # Some models only support default temperature
            if temperature != 1.0:
                try:
                    params["temperature"] = temperature
                    response = self.client.chat.completions.create(**params)
                except Exception as e:
                    if "temperature" in str(e).lower():
                        # Retry without temperature parameter
                        logger.warning(f"Temperature not supported, using default: {e}")
                        params.pop("temperature")
                        response = self.client.chat.completions.create(**params)
                    else:
                        raise
            else:
                response = self.client.chat.completions.create(**params)
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def extract_workforce_data(self, company_name: str, signals: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Extract actual workforce/employee information from signals using AI.
        
        Args:
            company_name: Name of the company
            signals: List of scraped signals (news, reddit, etc.)
            
        Returns:
            Dictionary with extracted workforce data or None if extraction fails
        """
        from prompts import get_workforce_extraction_prompt
        
        if not signals:
            return None
        
        try:
            prompt = get_workforce_extraction_prompt(company_name, signals)
            response = self.query(prompt, temperature=0.3, max_tokens=500)
            
            logger.info(f"AI Response for workforce extraction: {response[:200]}...")
            
            try:
                workforce_data = self.parse_json_response(response)
                logger.info(f"Parsed workforce data: {workforce_data}")
            except Exception as parse_error:
                logger.error(f"Failed to parse workforce response: {parse_error}")
                logger.error(f"Full response: {response}")
                return None
            
            return workforce_data
        except Exception as e:
            logger.error(f"Failed to extract workforce data: {e}", exc_info=True)
            return None
    
    def _query_anthropic(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Query Anthropic API"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system="You are a financial markets and corporate structure expert. Always respond with valid JSON only, no markdown formatting.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def _query_mock(self, prompt: str) -> str:
        """Mock response for testing without API key"""
        # Simple mock logic based on prompt content
        if "Twelve Cupcakes" in prompt:
            return json.dumps({
                "company_name": "Twelve Cupcakes",
                "is_publicly_traded": False,
                "parent_company": "Dhunseri Ventures Ltd",
                "publicly_traded_entity": "Dhunseri Ventures Ltd",
                "yahoo_symbol": "DHUNINV.NS",
                "exchange": "NSE India",
                "confidence": "high",
                "reasoning": "Twelve Cupcakes is owned by Dhunseri Ventures Ltd, which is publicly traded on NSE India"
            })
        elif "Grab" in prompt:
            return json.dumps({
                "company_name": "Grab",
                "is_publicly_traded": True,
                "parent_company": None,
                "publicly_traded_entity": "Grab Holdings Limited",
                "yahoo_symbol": "GRAB",
                "exchange": "NASDAQ",
                "confidence": "high",
                "reasoning": "Grab is publicly traded on NASDAQ under ticker GRAB"
            })
        elif "Shopee" in prompt:
            return json.dumps({
                "company_name": "Shopee",
                "is_publicly_traded": False,
                "parent_company": "Sea Limited",
                "publicly_traded_entity": "Sea Limited",
                "yahoo_symbol": "SE",
                "exchange": "NYSE",
                "confidence": "high",
                "reasoning": "Shopee is owned by Sea Limited, which is publicly traded on NYSE under ticker SE"
            })
        else:
            return json.dumps({
                "company_name": prompt.split('"')[1] if '"' in prompt else "Unknown",
                "is_publicly_traded": False,
                "parent_company": None,
                "publicly_traded_entity": None,
                "yahoo_symbol": None,
                "exchange": None,
                "confidence": "medium",
                "reasoning": "Unable to determine public trading status without more information"
            })
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from AI, handling potential markdown formatting
        
        Args:
            response: Raw response string from AI
            
        Returns:
            Parsed JSON as dictionary
        """
        # Remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        response = response.strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response}")
            raise


class CompanySymbolDetector:
    """High-level service for detecting company symbols using AI"""
    
    def __init__(self, ai_service: Optional[AIService] = None):
        """
        Initialize detector
        
        Args:
            ai_service: AIService instance. If None, creates a new one
        """
        self.ai_service = ai_service or AIService()
    
    def detect_symbol(self, company_name: str) -> Dict[str, Any]:
        """
        Detect Yahoo Finance symbol for a company
        
        Args:
            company_name: Name of the company
            
        Returns:
            Dictionary with company information and symbol
        """
        from prompts import get_parent_company_detection_prompt
        
        prompt = get_parent_company_detection_prompt(company_name)
        
        try:
            response = self.ai_service.query(prompt, temperature=0.2)
            result = self.ai_service.parse_json_response(response)
            
            logger.info(f"Symbol detection for '{company_name}': {result.get('yahoo_symbol', 'None')}")
            return result
        except Exception as e:
            logger.error(f"Error detecting symbol for '{company_name}': {e}")
            # Return a safe default
            return {
                "company_name": company_name,
                "is_publicly_traded": False,
                "parent_company": None,
                "publicly_traded_entity": None,
                "yahoo_symbol": None,
                "exchange": None,
                "confidence": "low",
                "reasoning": f"Error during detection: {str(e)}"
            }
    
    def validate_symbol(self, company_name: str, symbol: str) -> Dict[str, Any]:
        """
        Validate if a symbol is correct for a company
        
        Args:
            company_name: Name of the company
            symbol: Symbol to validate
            
        Returns:
            Validation result dictionary
        """
        from prompts import get_symbol_validation_prompt
        
        prompt = get_symbol_validation_prompt(company_name, symbol)
        
        try:
            response = self.ai_service.query(prompt, temperature=0.2)
            return self.ai_service.parse_json_response(response)
        except Exception as e:
            logger.error(f"Error validating symbol '{symbol}' for '{company_name}': {e}")
            return {
                "symbol": symbol,
                "is_valid": False,
                "is_active": False,
                "company_match": "unknown",
                "alternative_symbols": [],
                "recommendation": None,
                "notes": f"Error during validation: {str(e)}"
            }
    
    def detect_multiple_symbols(self, company_names: List[str]) -> Dict[str, Any]:
        """
        Detect symbols for multiple companies at once
        
        Args:
            company_names: List of company names
            
        Returns:
            Dictionary with results for all companies
        """
        from prompts import get_multiple_companies_symbol_prompt
        
        prompt = get_multiple_companies_symbol_prompt(company_names)
        
        try:
            response = self.ai_service.query(prompt, temperature=0.2, max_tokens=2000)
            return self.ai_service.parse_json_response(response)
        except Exception as e:
            logger.error(f"Error detecting symbols for multiple companies: {e}")
            return {
                "results": [
                    {
                        "company_name": name,
                        "is_publicly_traded": False,
                        "parent_company": None,
                        "yahoo_symbol": None,
                        "exchange": None,
                        "confidence": "low"
                    }
                    for name in company_names
                ]
            }


class WorkforceRelevanceFilter:
    """Service for filtering workforce-relevant news articles using AI"""
    
    def __init__(self, ai_service: Optional[AIService] = None):
        """
        Initialize relevance filter
        
        Args:
            ai_service: AIService instance. If None, creates a new one
        """
        self.ai_service = ai_service or AIService()
    
    def check_relevance(self, title: str, first_paragraph: str, company_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if a news article is relevant to workforce signals
        
        Args:
            title: Article title
            first_paragraph: First paragraph of the article
            company_name: Optional company name for context (company-specific scraping)
            
        Returns:
            Dictionary with relevance information
        """
        from prompts import get_workforce_relevance_prompt
        
        prompt = get_workforce_relevance_prompt(title, first_paragraph, company_name)
        
        try:
            response = self.ai_service.query(prompt, temperature=0.3, max_tokens=300)
            
            # Parse the plain text response
            lines = response.strip().split('\n')
            result = {
                "primary_label": "UNKNOWN",
                "secondary_label": "NONE",
                "rationale": "Unable to determine relevance"
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith("PrimaryLabel:"):
                    result["primary_label"] = line.split(":", 1)[1].strip()
                elif line.startswith("SecondaryLabel:"):
                    result["secondary_label"] = line.split(":", 1)[1].strip()
                elif line.startswith("Rationale:"):
                    result["rationale"] = line.split(":", 1)[1].strip()
            
            is_relevant = result["primary_label"] == "WORKFORCE_RELEVANT"
            result["is_relevant"] = is_relevant
            
            logger.info(f"Relevance check: {result['primary_label']} - {result['rationale'][:50]}")
            return result
            
        except Exception as e:
            logger.error(f"Error checking workforce relevance: {e}")
            # Default to relevant to avoid filtering out potentially important articles
            return {
                "is_relevant": True,
                "primary_label": "WORKFORCE_RELEVANT",
                "secondary_label": "WORKFORCE_NEUTRAL",
                "rationale": f"Error during relevance check, defaulting to relevant: {str(e)}"
            }


class FinancialAnalystAI:
    """AI-powered financial analyst service for comprehensive company analysis"""
    
    def __init__(self, ai_service: Optional[AIService] = None):
        """
        Initialize financial analyst AI
        
        Args:
            ai_service: AIService instance. If None, creates a new one
        """
        self.ai_service = ai_service or AIService()
    
    def analyze_financial_data(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive financial analysis of company data
        
        Args:
            company_data: Dictionary containing company financial information
                         including summary, history, and metrics
            
        Returns:
            Dictionary with detailed AI-generated financial analysis
        """
        from prompts import get_financial_analyst_prompt
        
        prompt = get_financial_analyst_prompt(company_data)
        
        try:
            response = self.ai_service.query(prompt, temperature=0.4, max_tokens=1500)
            analysis = self.ai_service.parse_json_response(response)
            
            # Get company name from summary or top-level
            company_name = (
                company_data.get('summary', {}).get('company_name') or 
                company_data.get('company_name') or 
                company_data.get('ticker', 'Unknown')
            )
            
            logger.info(f"Financial analysis completed for {company_name}")
            logger.info(f"Risk Rating: {analysis.get('risk_rating', 'Unknown')}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing financial data: {e}")
            # Return a safe default analysis
            return {
                "financial_health": {
                    "assessment": "Unable to complete analysis due to technical error.",
                    "rating": "Unknown",
                    "key_metrics_summary": "Data unavailable"
                },
                "workforce_implications": {
                    "employment_stability": "Cannot assess",
                    "hiring_outlook": "Neutral - Insufficient data",
                    "risk_factors": ["Analysis unavailable"],
                    "opportunities": []
                },
                "stock_performance": {
                    "trend": "Neutral",
                    "trend_explanation": "Unable to determine trend",
                    "volatility_assessment": "Unknown",
                    "investor_confidence": "Unknown"
                },
                "key_insights": [
                    "Financial analysis could not be completed",
                    f"Error: {str(e)}"
                ],
                "risk_rating": "UNKNOWN",
                "summary": f"Analysis failed: {str(e)}"
            }
