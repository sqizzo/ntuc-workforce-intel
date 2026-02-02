"""
Hypothesis Engine for Risk Analysis
Analyzes news, financial statements, and social forums to generate risk hypotheses
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from ai_service import AIService
import json

logger = logging.getLogger(__name__)


class HypothesisEngine:
    """Engine for generating risk analysis hypotheses from multiple data sources"""
    
    def __init__(self, ai_service: Optional[AIService] = None):
        """
        Initialize the Hypothesis Engine
        
        Args:
            ai_service: AI service instance for analysis
        """
        self.ai_service = ai_service or AIService()
    
    def analyze_company_risk(
        self,
        company_name: str,
        news_signals: List[Dict[str, Any]],
        social_signals: List[Dict[str, Any]],
        financial_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive risk analysis on a company
        
        Args:
            company_name: Name of the company
            news_signals: List of news signal data
            social_signals: List of social/forum signal data
            financial_data: Optional financial data
            
        Returns:
            Complete risk analysis with primary and supporting signals
        """
        logger.info(f"Starting risk analysis for {company_name}")
        
        # Step 1: Summarize and extract insights from each data source
        news_insights = self._summarize_data_source(company_name, news_signals, "news")
        social_insights = self._summarize_data_source(company_name, social_signals, "social")
        financial_insights = self._extract_financial_insights(company_name, financial_data)
        
        # Step 2: Create supporting signals (evidence with titles)
        supporting_signals = self._create_supporting_signals(
            company_name, news_insights, social_insights, financial_insights
        )
        
        # Step 3: Group supporting signals into primary signals
        primary_signals = self._group_into_primary_signals(
            company_name, supporting_signals
        )
        
        # Step 4: Generate overall risk assessment
        risk_summary = self._generate_risk_summary(
            company_name, primary_signals, financial_data
        )
        
        return {
            "company_name": company_name,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "risk_summary": risk_summary,
            "primary_signals": primary_signals,
            "supporting_signals": supporting_signals,
            "data_sources": {
                "news_count": len(news_signals),
                "social_count": len(social_signals),
                "has_financial_data": financial_data is not None
            }
        }
    
    def _summarize_data_source(
        self,
        company_name: str,
        signals: List[Dict[str, Any]],
        source_type: str
    ) -> List[Dict[str, Any]]:
        """
        Summarize insights from a specific data source
        
        Args:
            company_name: Company name
            signals: List of signal data
            source_type: Type of source (news, social, etc.)
            
        Returns:
            List of insights with summaries
        """
        if not signals:
            return []
        
        # Prepare data for AI analysis
        signal_texts = []
        for idx, signal in enumerate(signals[:20]):  # Limit to 20 most relevant
            text = signal.get('extracted_text', '')
            title = signal.get('metadata', {}).get('title', '')
            date = signal.get('metadata', {}).get('publish_date', 'Unknown date')
            source_name = signal.get('source_name', 'Unknown source')
            
            signal_texts.append({
                "id": idx,
                "title": title,
                "text": text[:500],  # Limit text length
                "date": date,
                "source": source_name
            })
        
        prompt = self._get_summarization_prompt(company_name, signal_texts, source_type)
        
        try:
            response = self.ai_service.query(prompt, temperature=0.3, max_tokens=2000)
            insights = json.loads(response)
            return insights.get('insights', [])
        except Exception as e:
            logger.error(f"Error summarizing {source_type} data: {e}")
            return []
    
    def _get_summarization_prompt(
        self,
        company_name: str,
        signal_texts: List[Dict[str, Any]],
        source_type: str
    ) -> str:
        """Generate prompt for summarizing data source"""
        signals_json = json.dumps(signal_texts, indent=2)
        
        return f"""You are analyzing {source_type} data about "{company_name}" to extract key insights for risk analysis.

DATA TO ANALYZE:
{signals_json}

TASK:
Analyze the above {source_type} data and extract key insights. For each distinct insight:
1. Provide a brief summary (1-2 sentences)
2. Identify the key concern or theme
3. Note the timeframe/date if available
4. List which signal IDs support this insight

Return a JSON object with this structure:
{{
    "insights": [
        {{
            "summary": "Brief description of the insight",
            "key_concern": "Main theme or concern",
            "timeframe": "Year or date range",
            "signal_ids": [0, 1, 2],
            "severity": "low/medium/high"
        }}
    ]
}}

Focus on insights related to:
- Business operations and closures
- Financial performance concerns
- Employee/workforce issues
- Market perception and reputation
- Industry trends
- Regulatory or legal issues

Respond with ONLY valid JSON, no markdown formatting."""
    
    def _extract_financial_insights(
        self,
        company_name: str,
        financial_data: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract insights from financial data
        
        Args:
            company_name: Company name
            financial_data: Financial data dictionary
            
        Returns:
            List of insights from financial metrics
        """
        if not financial_data:
            return []
        
        insights = []
        
        # Extract key financial metrics
        summary = financial_data.get('financial_data', {}).get('summary', {})
        ai_analysis = financial_data.get('ai_analysis', {})
        
        if not summary and not ai_analysis:
            return []
        
        # Prepare financial data for AI analysis
        financial_info = {
            "market_cap": summary.get('market_cap'),
            "revenue": summary.get('revenue'),
            "profit_margin": summary.get('profit_margin'),
            "pe_ratio": summary.get('pe_ratio'),
            "employees": summary.get('employees'),
            "sector": summary.get('sector'),
            "industry": summary.get('industry'),
            "current_price": summary.get('current_price'),
            "ai_analysis": {
                "financial_health": ai_analysis.get('financial_health', {}) if ai_analysis else {},
                "stock_performance": ai_analysis.get('stock_performance', {}) if ai_analysis else {},
                "workforce_implications": ai_analysis.get('workforce_implications', {}) if ai_analysis else {}
            }
        }
        
        prompt = f"""You are analyzing financial data for "{company_name}" to extract risk insights.

FINANCIAL DATA:
{json.dumps(financial_info, indent=2)}

TASK:
Extract key financial risk insights. For each significant concern:
1. Provide a brief summary (1-2 sentences)
2. Identify the key financial concern
3. Estimate timeframe (current/recent)
4. Assess severity

Return a JSON object with this structure:
{{
    "insights": [
        {{
            "summary": "Brief description of financial concern",
            "key_concern": "Main financial theme",
            "timeframe": "Current" or year,
            "signal_ids": [],
            "severity": "low/medium/high"
        }}
    ]
}}

Focus on:
- Profitability concerns (negative margins, declining revenue)
- Valuation issues (low market cap, poor P/E ratio)
- Workforce costs and efficiency
- Industry challenges
- Stock performance issues
- Financial health warnings

Only include insights that indicate potential risks. If financials look healthy, return empty insights array.
Respond with ONLY valid JSON, no markdown formatting."""
        
        try:
            response = self.ai_service.query(prompt, temperature=0.3, max_tokens=1500)
            result = json.loads(response)
            financial_insights = result.get('insights', [])
            
            # Mark as financial source
            for insight in financial_insights:
                insight['source_type'] = 'financial'
            
            return financial_insights
        except Exception as e:
            logger.error(f"Error extracting financial insights: {e}")
            return []
    
    def _create_supporting_signals(
        self,
        company_name: str,
        news_insights: List[Dict[str, Any]],
        social_insights: List[Dict[str, Any]],
        financial_insights: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create supporting signals (evidence with descriptive titles)
        
        Args:
            company_name: Company name
            news_insights: Insights from news data
            social_insights: Insights from social data
            financial_insights: Insights from financial data
            
        Returns:
            List of supporting signals with titles and evidence
        """
        all_insights = []
        
        # Add news insights
        for insight in news_insights:
            all_insights.append({
                **insight,
                "source_type": "news"
            })
        
        # Add social insights
        for insight in social_insights:
            all_insights.append({
                **insight,
                "source_type": "social"
            })
        
        # Add financial insights
        for insight in financial_insights:
            all_insights.append({
                **insight,
                "source_type": "financial"
            })
        
        if not all_insights:
            return []
        
        # Use AI to create structured supporting signals with titles
        prompt = self._get_supporting_signals_prompt(company_name, all_insights)
        
        try:
            response = self.ai_service.query(prompt, temperature=0.3, max_tokens=2500)
            result = json.loads(response)
            return result.get('supporting_signals', [])
        except Exception as e:
            logger.error(f"Error creating supporting signals: {e}")
            # Fallback: create basic supporting signals
            return self._create_fallback_supporting_signals(all_insights)
    
    def _get_supporting_signals_prompt(
        self,
        company_name: str,
        insights: List[Dict[str, Any]]
    ) -> str:
        """Generate prompt for creating supporting signals"""
        insights_json = json.dumps(insights, indent=2)
        
        return f"""You are analyzing risk signals for "{company_name}". Create structured "supporting signals" from the following insights.

INSIGHTS:
{insights_json}

TASK:
Transform these insights into supporting signals. Each supporting signal should have:
1. A clear, descriptive title (3-7 words) that summarizes the signal
2. The source type (News or Social)
3. The timeframe (year or date range)
4. Evidence data (the detailed insight/summary)

Return a JSON object with this structure:
{{
    "supporting_signals": [
        {{
            "id": "ss_1",
            "title": "Scale Decay & Branch Closures",
            "source_type": "Social",
            "timeframe": "2019",
            "evidence": "Reddit discourse highlights store shutdowns and doubts about long-term business sustainability.",
            "severity": "high"
        }},
        {{
            "id": "ss_2",
            "title": "Terminal Industry Outlook",
            "source_type": "Social",
            "timeframe": "2024",
            "evidence": "Community consensus on r/askSingapore naming the brand as most likely to fail within 5 years.",
            "severity": "high"
        }}
    ]
}}

Make titles concise and professional. Combine similar insights if appropriate.
Respond with ONLY valid JSON, no markdown formatting."""
    
    def _create_fallback_supporting_signals(
        self,
        insights: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create basic supporting signals when AI fails"""
        supporting_signals = []
        for idx, insight in enumerate(insights):
            supporting_signals.append({
                "id": f"ss_{idx + 1}",
                "title": insight.get('key_concern', 'Business Concern'),
                "source_type": insight.get('source_type', 'Unknown').capitalize(),
                "timeframe": insight.get('timeframe', 'Unknown'),
                "evidence": insight.get('summary', 'No details available'),
                "severity": insight.get('severity', 'medium')
            })
        return supporting_signals
    
    def _group_into_primary_signals(
        self,
        company_name: str,
        supporting_signals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Group supporting signals into primary signals based on themes
        
        Args:
            company_name: Company name
            supporting_signals: List of supporting signals
            
        Returns:
            List of primary signals with grouped supporting signals
        """
        if not supporting_signals:
            return []
        
        prompt = self._get_primary_signals_prompt(company_name, supporting_signals)
        
        try:
            response = self.ai_service.query(prompt, temperature=0.3, max_tokens=2000)
            result = json.loads(response)
            primary_signals = result.get('primary_signals', [])
            
            # Calculate source distribution for each primary signal
            for ps in primary_signals:
                ps['source_distribution'] = self._calculate_source_distribution(
                    ps.get('supporting_signal_ids', []),
                    supporting_signals
                )
            
            return primary_signals
        except Exception as e:
            logger.error(f"Error grouping primary signals: {e}")
            return self._create_fallback_primary_signals(supporting_signals)
    
    def _get_primary_signals_prompt(
        self,
        company_name: str,
        supporting_signals: List[Dict[str, Any]]
    ) -> str:
        """Generate prompt for grouping into primary signals"""
        signals_json = json.dumps(supporting_signals, indent=2)
        
        return f"""You are analyzing risk signals for "{company_name}". Group the following supporting signals into broader primary signal categories.

SUPPORTING SIGNALS:
{signals_json}

TASK:
Group these supporting signals into primary signal categories based on similar themes. Common categories include:
- OPERATIONAL DEGRADATION (closures, declining business)
- FINANCIAL DISTRESS (losses, debt, poor performance)
- MARKET PERCEPTION (reputation, customer concerns)
- WORKFORCE ISSUES (layoffs, employee concerns)
- REGULATORY/LEGAL RISKS
- INDUSTRY CHALLENGES

Return a JSON object with this structure:
{{
    "primary_signals": [
        {{
            "id": "ps_1",
            "title": "OPERATIONAL DEGRADATION",
            "description": "Evidence of declining operations and business closures",
            "risk_level": "high",
            "supporting_signal_ids": ["ss_1", "ss_2"],
            "key_indicators": ["Store closures", "Business sustainability concerns"]
        }}
    ]
}}

Each primary signal should group 1-5 related supporting signals.
Respond with ONLY valid JSON, no markdown formatting."""
    
    def _calculate_source_distribution(
        self,
        supporting_signal_ids: List[str],
        supporting_signals: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate distribution of sources for a primary signal"""
        distribution = {"News": 0, "Social": 0, "Financial": 0}
        
        for signal in supporting_signals:
            if signal['id'] in supporting_signal_ids:
                source_type = signal.get('source_type', 'Unknown').capitalize()
                if source_type in distribution:
                    distribution[source_type] += 1
        
        return distribution
    
    def _create_fallback_primary_signals(
        self,
        supporting_signals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create basic primary signals when AI fails"""
        # Simple grouping by severity
        high_severity = [s for s in supporting_signals if s.get('severity') == 'high']
        
        if high_severity:
            return [{
                "id": "ps_1",
                "title": "BUSINESS RISK INDICATORS",
                "description": "Multiple risk signals identified",
                "risk_level": "high",
                "supporting_signal_ids": [s['id'] for s in high_severity],
                "key_indicators": [s['title'] for s in high_severity],
                "source_distribution": self._calculate_source_distribution(
                    [s['id'] for s in high_severity],
                    supporting_signals
                )
            }]
        
        return []
    
    def _generate_risk_summary(
        self,
        company_name: str,
        primary_signals: List[Dict[str, Any]],
        financial_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate overall risk assessment summary
        
        Args:
            company_name: Company name
            primary_signals: List of primary signals
            financial_data: Optional financial data
            
        Returns:
            Risk summary with overall assessment
        """
        if not primary_signals:
            return {
                "overall_risk": "low",
                "confidence": "low",
                "summary": "Insufficient data for comprehensive risk analysis",
                "recommendation": "Gather more data from multiple sources"
            }
        
        # Count high risk signals
        high_risk_count = sum(1 for ps in primary_signals if ps.get('risk_level') == 'high')
        total_signals = len(primary_signals)
        
        # Determine overall risk level
        if high_risk_count >= total_signals * 0.6:
            overall_risk = "high"
        elif high_risk_count >= total_signals * 0.3:
            overall_risk = "medium"
        else:
            overall_risk = "low"
        
        # Generate summary text
        signal_titles = [ps['title'] for ps in primary_signals[:3]]
        summary = f"Analysis identified {total_signals} primary risk categories for {company_name}"
        if signal_titles:
            summary += f", including {', '.join(signal_titles)}"
        
        return {
            "overall_risk": overall_risk,
            "confidence": "high" if total_signals >= 3 else "medium",
            "summary": summary,
            "recommendation": self._get_recommendation(overall_risk),
            "primary_signal_count": total_signals,
            "high_risk_signals": high_risk_count
        }
    
    def _get_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            "high": "Immediate attention required. Consider detailed due diligence and risk mitigation strategies.",
            "medium": "Monitor closely. Review specific risk areas and develop contingency plans.",
            "low": "Maintain standard monitoring procedures. Continue tracking key indicators."
        }
        return recommendations.get(risk_level, "Continue monitoring")
