"""
Prompts for AI-powered company and symbol detection
"""

from typing import List, Optional, Dict, Any


def get_workforce_extraction_prompt(company_name: str, signals: List[Dict[str, Any]]) -> str:
    """
    Prompt to extract actual workforce/employee information from news and social signals.
    
    Args:
        company_name: The name of the company
        signals: List of signal dictionaries containing news articles and social posts
        
    Returns:
        A prompt string for extracting workforce data
    """
    # Combine text from all signals
    signal_texts = []
    for idx, signal in enumerate(signals[:10], 1):  # Limit to first 10 signals
        source = signal.get('source_name', 'Unknown')
        text = signal.get('extracted_text', '')
        title = signal.get('metadata', {}).get('title', '')
        signal_texts.append(f"Source {idx} ({source}):\nTitle: {title}\nContent: {text[:300]}...")
    
    combined_signals = "\n\n".join(signal_texts)
    
    return f"""You are analyzing workforce intelligence data for "{company_name}". Extract accurate employee/workforce information from the following news articles and social media posts.

SIGNALS TO ANALYZE:
{combined_signals}

TASK:
Extract the following information about {company_name}'s workforce:
1. **employee_count**: Most recent/accurate employee or worker count mentioned
2. **affected_workers**: Number of workers affected by layoffs/closures (if mentioned)
3. **source_confidence**: How confident are you in this data? (high/medium/low)
4. **data_source**: Which signal number(s) provided this information?
5. **context**: Brief context about the workforce situation (1-2 sentences)
6. **is_subsidiary_data**: Is this data specifically about the subsidiary/brand, not parent company? (true/false)

Return a JSON object with this structure:
{{
    "employee_count": <number or null>,
    "affected_workers": <number or null>,
    "source_confidence": "<high/medium/low>",
    "data_source": "<signal numbers>",
    "context": "<brief context>",
    "is_subsidiary_data": <true/false>
}}

If no employee information is found, return null for employee_count and explain in context."""


def get_parent_company_detection_prompt(company_name: str) -> str:
    """
    Prompt to detect the parent company and publicly traded entity for a given company.
    
    Args:
        company_name: The name of the company to analyze
        
    Returns:
        A prompt string for the AI to identify parent companies and trading symbols
    """
    return f"""You are a corporate structure and financial markets analyst with access to global business databases. Analyze the company "{company_name}" and provide information about its ownership structure and stock market presence.

CRITICAL TASK:
1. Determine if "{company_name}" is publicly traded on any stock exchange
2. If not publicly traded, YOU MUST RESEARCH its parent company, holding company, or owner
3. Check multiple sources: company websites, business registries, news articles, acquisition records
4. Find the Yahoo Finance stock symbol for the publicly traded entity (either the company itself or its parent)
5. Provide confidence level for your findings

KNOWN OWNERSHIP EXAMPLES (Use as reference):
- "Twelve Cupcakes" (Singapore F&B) → Acquired by "Dhunseri Ventures Ltd" (2018) → Symbol: "DHUNINV.NS" (NSE India)
- "Instagram" → Owned by "Meta Platforms" → Symbol: "META" (NASDAQ)
- "Shopee" → Owned by "Sea Limited" → Symbol: "SE" (NYSE)
- "WhatsApp" → Owned by "Meta Platforms" → Symbol: "META" (NASDAQ)
- "YouTube" → Owned by "Alphabet Inc" → Symbol: "GOOGL" (NASDAQ)
- "LinkedIn" → Owned by "Microsoft" → Symbol: "MSFT" (NASDAQ)

RESEARCH CHECKLIST for "{company_name}":
□ Is it a subsidiary or brand of a larger company?
□ Has it been acquired? When and by whom?
□ Who are the major shareholders or owners?
□ Is the parent company publicly traded?
□ What is the correct Yahoo Finance symbol?

REGIONAL NOTES:
- Singapore Companies: May have SGX-listed (.SI) parents, or be owned by Indian/Malaysian conglomerates
- F&B/Retail brands: Often owned by larger holding companies (check acquisition history)
- Tech platforms: Usually owned by publicly traded tech giants
- Indian companies: Check NSE (.NS) or BSE (.BO) listings
- Malaysian companies: Check KLSE (.KL) listings

Return ONLY a valid JSON object with the following structure:
{{
    "company_name": "{company_name}",
    "is_publicly_traded": true/false,
    "parent_company": "Name of parent/holding company if applicable, or null",
    "publicly_traded_entity": "Name of the publicly traded company (could be parent)",
    "yahoo_symbol": "The Yahoo Finance ticker symbol (e.g., AAPL, META, DHUNINV.NS, GRAB.SI)",
    "exchange": "Primary stock exchange (e.g., NASDAQ, NYSE, SGX, NSE)",
    "confidence": "high/medium/low",
    "reasoning": "Brief explanation of the corporate structure and why this symbol was chosen"
}}

If the company has no publicly traded parent or cannot be traced to any public entity, return:
{{
    "company_name": "{company_name}",
    "is_publicly_traded": false,
    "parent_company": null,
    "publicly_traded_entity": null,
    "yahoo_symbol": null,
    "exchange": null,
    "confidence": "high",
    "reasoning": "Company is privately held with no publicly traded parent company"
}}

Use your knowledge of corporate structures, mergers, acquisitions, and stock market listings. For Singapore companies, check SGX listings (symbols often end with .SI). For Malaysian companies, check KLSE (symbols end with .KL). For Indian companies, check NSE (.NS) or BSE (.BO). For US companies, check NYSE and NASDAQ.

Do not include any markdown formatting, backticks, or explanatory text. Return only the raw JSON object."""


def get_symbol_validation_prompt(company_name: str, suggested_symbol: str) -> str:
    """
    Prompt to validate if a suggested Yahoo Finance symbol is correct for a company.
    
    Args:
        company_name: The name of the company
        suggested_symbol: The symbol to validate
        
    Returns:
        A prompt string for the AI to validate the symbol
    """
    return f"""You are a financial markets validator. Verify if the Yahoo Finance symbol "{suggested_symbol}" is the correct ticker for "{company_name}".

Analyze:
1. Does this symbol exist on Yahoo Finance?
2. Does it represent the correct company or its parent?
3. Is it actively traded or delisted?
4. Are there alternative/better symbols for this entity?

Return ONLY a valid JSON object:
{{
    "symbol": "{suggested_symbol}",
    "is_valid": true/false,
    "is_active": true/false,
    "company_match": "exact/parent/subsidiary/incorrect",
    "alternative_symbols": ["SYMBOL1", "SYMBOL2"],
    "recommendation": "The symbol to use, or null if none applicable",
    "notes": "Brief explanation"
}}

Do not include any markdown formatting or extra text. Return only the JSON object."""


def get_multiple_companies_symbol_prompt(company_names: List[str]) -> str:
    """
    Batch prompt to detect symbols for multiple companies at once.
    
    Args:
        company_names: List of company names to analyze
        
    Returns:
        A prompt string for batch company analysis
    """
    companies_list = "\n".join([f"- {name}" for name in company_names])
    
    return f"""You are a corporate structure and financial markets analyst. Analyze the following companies and find their Yahoo Finance stock symbols or their publicly traded parent companies:

{companies_list}

For each company, determine:
1. If it's publicly traded or privately held
2. Its parent company if applicable
3. The appropriate Yahoo Finance symbol
4. The stock exchange

Return ONLY a valid JSON object with this structure:
{{
    "results": [
        {{
            "company_name": "Company Name",
            "is_publicly_traded": true/false,
            "parent_company": "Parent name or null",
            "yahoo_symbol": "SYMBOL or null",
            "exchange": "Exchange name or null",
            "confidence": "high/medium/low"
        }}
    ]
}}

For Singapore companies, symbols typically end with .SI (e.g., GRAB.SI, DBS.SI).
For Malaysian companies, symbols end with .KL.
For US companies, use standard NYSE/NASDAQ symbols.

If a company is privately held with no public parent, set yahoo_symbol to null.

Do not include markdown formatting or explanatory text. Return only the raw JSON object."""


def get_industry_sector_prompt(company_name: str, yahoo_symbol: Optional[str] = None) -> str:
    """
    Prompt to identify the industry and sector of a company for better financial analysis context.
    
    Args:
        company_name: The name of the company
        yahoo_symbol: Optional Yahoo Finance symbol if known
        
    Returns:
        A prompt string to identify company industry and sector
    """
    symbol_context = f' (Symbol: {yahoo_symbol})' if yahoo_symbol else ''
    
    return f"""You are an industry classification expert. Analyze "{company_name}"{symbol_context} and provide its industry classification.

Provide:
1. Primary industry sector (e.g., Technology, Healthcare, Consumer Goods)
2. Specific industry (e.g., Software, Biotechnology, Food & Beverage)
3. Sub-sector if applicable
4. Key business activities

Return ONLY a valid JSON object:
{{
    "company_name": "{company_name}",
    "sector": "Primary sector",
    "industry": "Specific industry",
    "sub_sector": "Sub-sector or null",
    "business_description": "Brief description of main business activities",
    "competitors": ["Competitor1", "Competitor2", "Competitor3"]
}}

Do not include markdown formatting. Return only the JSON object."""


def get_financial_context_prompt(company_name: str, yahoo_symbol: str, error_message: str) -> str:
    """
    Prompt to provide context when financial data retrieval fails.
    
    Args:
        company_name: The name of the company
        yahoo_symbol: The symbol that failed
        error_message: The error message received
        
    Returns:
        A prompt to explain the issue and suggest alternatives
    """
    return f"""You are a financial data troubleshooting expert. The system attempted to fetch financial data for "{company_name}" using Yahoo Finance symbol "{yahoo_symbol}" but encountered this error:

{error_message}

Analyze the situation and provide guidance:

Return ONLY a valid JSON object:
{{
    "issue": "Brief description of the problem",
    "likely_cause": "Why this error occurred (delisted/private/wrong symbol/etc)",
    "suggested_actions": [
        "Action 1",
        "Action 2"
    ],
    "alternative_symbols": ["SYMBOL1", "SYMBOL2"],
    "data_alternatives": [
        "Alternative data source 1",
        "Alternative data source 2"
    ],
    "recommendation": "Best course of action"
}}

Do not include markdown formatting. Return only the JSON object."""


def get_workforce_relevance_prompt(title: str, first_paragraph: str) -> str:
    """
    Prompt to check if a news article is relevant to workforce signals.
    
    Args:
        title: The article title
        first_paragraph: The first paragraph of the article
        
    Returns:
        A prompt string for the AI to determine workforce relevance
    """
    return f"""You are an assistant helping to filter news articles for a workforce early-signal monitoring system.
Your task is NOT to predict outcomes or analyse risks.

Based ONLY on the article title and the first paragraph provided below:

ARTICLE TITLE:
"{title}"

FIRST PARAGRAPH:
"{first_paragraph}"

INSTRUCTIONS:
1. Determine whether the article is relevant to workforce-related issues.

2. Workforce-related issues include:
   - employment conditions
   - manpower shortages
   - retrenchment, layoffs, closures
   - cost pressures affecting workers
   - operational challenges impacting workers
   - hiring trends or freezes
   - wage issues
   - labor disputes
   - business restructuring affecting staff
   - company financial troubles impacting jobs

3. The following topics are NOT workforce-related and should be excluded:
   - food promotions or menu launches
   - restaurant openings or reviews
   - lifestyle, entertainment, or human-interest stories
   - consumer trends without employment impact
   - product launches without workforce context
   - celebrity news or gossip
   - general business news without workforce implications

4. If the article IS workforce-related, classify the sentiment:
   - WORKFORCE_NEGATIVE: job losses, closures, cost-cutting affecting workers
   - WORKFORCE_NEUTRAL: general workforce news without clear positive/negative impact
   - WORKFORCE_POSITIVE: hiring expansions, wage increases, improved conditions

Return your answer in this EXACT format (no JSON, just plain text):

PrimaryLabel: <WORKFORCE_RELEVANT or NOT_WORKFORCE_RELEVANT>
SecondaryLabel: <WORKFORCE_NEGATIVE, WORKFORCE_NEUTRAL, WORKFORCE_POSITIVE, or NONE>
Rationale: <one short sentence explaining the decision>"""


def get_financial_analyst_prompt(company_data: Dict[str, Any]) -> str:
    """
    Prompt for AI to analyze financial data as a financial analyst.
    
    Args:
        company_data: Dictionary containing company financial information
        
    Returns:
        A prompt string for comprehensive financial analysis
    """
    # Get company name from summary first, then fallback to top-level
    company_name = (
        company_data.get('summary', {}).get('company_name') or 
        company_data.get('company_name') or 
        'Unknown Company'
    )
    ticker = company_data.get('ticker', 'N/A')
    info = company_data.get('summary', {})
    history = company_data.get('history_summary', {})
    
    return f"""You are a senior financial analyst specializing in workforce intelligence and corporate health assessment. Analyze the following financial data for {company_name} ({ticker}) and provide comprehensive insights.

COMPANY INFORMATION:
- Company Name: {company_name}
- Ticker: {ticker}
- Sector: {info.get('sector', 'N/A')}
- Industry: {info.get('industry', 'N/A')}
- Country: {info.get('country', 'N/A')}
- Employees: {info.get('employees', 'N/A')}

FINANCIAL METRICS:
- Market Cap: {info.get('market_cap', 'N/A')}
- Current Price: {info.get('current_price', 'N/A')} {info.get('currency', 'USD')}
- P/E Ratio: {info.get('pe_ratio', 'N/A')}
- Profit Margin: {info.get('profit_margin', 'N/A')}
- Total Revenue: {info.get('revenue', 'N/A')}

STOCK PERFORMANCE (Last Year):
- Starting Price: {history.get('first_close', 'N/A')}
- Current Price: {history.get('last_close', 'N/A')}
- Price Change: {history.get('price_change', 'N/A')}
- Price Change %: {history.get('price_change_percent', 'N/A')}
- Highest Price: {history.get('highest_price', 'N/A')}
- Lowest Price: {history.get('lowest_price', 'N/A')}
- Volatility: {history.get('volatility', 'N/A')}

BUSINESS DESCRIPTION:
{info.get('description', 'N/A')}

ANALYSIS REQUIREMENTS:
1. **Financial Health Assessment** (2-3 sentences)
   - Overall financial stability
   - Key strengths and weaknesses
   - Comparison to industry standards

2. **Workforce Implications** (3-4 sentences)
   - Impact on employment stability
   - Hiring outlook based on financial performance
   - Risk factors for workforce (layoffs, restructuring)
   - Opportunities for expansion

3. **Stock Performance Analysis** (2-3 sentences)
   - Trend analysis (bullish/bearish/neutral)
   - Volatility and what it indicates
   - Investor confidence level

4. **Key Insights & Recommendations** (3-4 bullet points)
   - Critical observations for workforce intelligence
   - Red flags or positive signals
   - Strategic recommendations

5. **Risk Rating** (Single rating)
   - LOW RISK: Stable financials, growing, good margins
   - MEDIUM RISK: Mixed signals, moderate concerns
   - HIGH RISK: Financial stress, declining metrics, volatility

Return your analysis in this EXACT JSON format (no markdown formatting):
{{
    "financial_health": {{
        "assessment": "2-3 sentence assessment",
        "rating": "Excellent/Good/Fair/Poor",
        "key_metrics_summary": "Brief summary of critical metrics"
    }},
    "workforce_implications": {{
        "employment_stability": "Assessment of job security",
        "hiring_outlook": "Positive/Neutral/Negative with explanation",
        "risk_factors": ["Risk 1", "Risk 2"],
        "opportunities": ["Opportunity 1", "Opportunity 2"]
    }},
    "stock_performance": {{
        "trend": "Bullish/Bearish/Neutral",
        "trend_explanation": "Why the trend is classified this way",
        "volatility_assessment": "Low/Medium/High with implications",
        "investor_confidence": "Strong/Moderate/Weak"
    }},
    "key_insights": [
        "Insight 1",
        "Insight 2",
        "Insight 3",
        "Insight 4"
    ],
    "risk_rating": "LOW RISK/MEDIUM RISK/HIGH RISK",
    "summary": "1-2 sentence executive summary"
}}

Provide actionable, data-driven insights based solely on the provided financial information. Be objective and professional."""
