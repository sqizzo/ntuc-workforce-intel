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
        
        # Step 4: AI-powered risk scoring for all signals
        supporting_signals_with_scores = self._add_ai_risk_scores_to_supporting_signals(
            company_name, supporting_signals
        )
        
        primary_signals_with_scores = self._add_ai_risk_scores_to_primary_signals(
            company_name, primary_signals, supporting_signals_with_scores
        )
        
        # Step 5: Calculate overall risk score using AI
        overall_risk_score = self._calculate_overall_risk_score(
            company_name, primary_signals_with_scores, supporting_signals_with_scores, financial_data
        )
        
        # Step 6: Generate major hypothesis synthesizing all signals
        major_hypothesis = self._generate_major_hypothesis(
            company_name, primary_signals_with_scores, supporting_signals_with_scores, overall_risk_score
        )
        
        # Step 7: Generate overall risk assessment
        risk_summary = self._generate_risk_summary(
            company_name, primary_signals_with_scores, financial_data
        )
        
        return {
            "company_name": company_name,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "overall_risk_score": overall_risk_score,
            "major_hypothesis": major_hypothesis,
            "risk_summary": risk_summary,
            "primary_signals": primary_signals_with_scores,
            "supporting_signals": supporting_signals_with_scores,
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
        # Might need to be open ended
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
- PRODUCT & CUSTOMER VALUE EROSION
- STRATEGIC ANOMALIES
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
    
    def _add_ai_risk_scores_to_supporting_signals(
        self,
        company_name: str,
        supporting_signals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Add AI-powered risk scores to each supporting signal based on Singapore workforce context
        
        Args:
            company_name: Company name
            supporting_signals: List of supporting signals
            
        Returns:
            Supporting signals with added risk_score and risk_reasoning
        """
        if not supporting_signals:
            return []
        
        prompt = f"""You are a Singapore workforce intelligence analyst. Analyze each supporting signal for "{company_name}" and assign a risk score (0-100) based on its impact on Singapore's workforce.

CONTEXT: Singapore Workforce Risk Factors
- Job losses and unemployment impact
- Skills mismatch and retraining needs
- Industry disruption and economic ripple effects
- Worker welfare and employment conditions
- Business sustainability affecting livelihoods

SUPPORTING SIGNALS:
{json.dumps(supporting_signals, indent=2)}

TASK:
For each supporting signal, provide:
1. risk_score: Integer 0-100 where:
   - 80-100: Critical workforce impact (mass layoffs, major closures)
   - 60-79: High workforce impact (significant job losses, industry decline)
   - 40-59: Medium workforce impact (operational issues, potential job risks)
   - 20-39: Low workforce impact (minor concerns, limited job impact)
   - 0-19: Minimal workforce impact (general business concerns)

2. risk_reasoning: 1-2 sentences explaining the score in Singapore workforce context

Return JSON:
{{
    "scored_signals": [
        {{
            "id": "ss_1",
            "risk_score": 85,
            "risk_reasoning": "Store closures directly threaten jobs of Singapore retail workers and indicate broader industry instability affecting livelihoods."
        }}
    ]
}}

Respond with ONLY valid JSON, no markdown formatting."""
        
        try:
            response = self.ai_service.query(prompt, temperature=0.2, max_tokens=2500)
            result = json.loads(response)
            scored_signals_map = {s['id']: s for s in result.get('scored_signals', [])}
            
            # Add scores to original signals
            enhanced_signals = []
            for signal in supporting_signals:
                signal_copy = signal.copy()
                score_data = scored_signals_map.get(signal['id'], {})
                signal_copy['risk_score'] = score_data.get('risk_score', 50)
                signal_copy['risk_reasoning'] = score_data.get('risk_reasoning', 'Risk assessment pending')
                enhanced_signals.append(signal_copy)
            
            return enhanced_signals
        except Exception as e:
            logger.error(f"Error adding risk scores to supporting signals: {e}")
            # Fallback: assign default scores based on severity
            for signal in supporting_signals:
                severity_scores = {'high': 75, 'medium': 50, 'low': 25}
                signal['risk_score'] = severity_scores.get(signal.get('severity', 'medium'), 50)
                signal['risk_reasoning'] = 'Default risk assessment based on severity'
            return supporting_signals
    
    def _add_ai_risk_scores_to_primary_signals(
        self,
        company_name: str,
        primary_signals: List[Dict[str, Any]],
        supporting_signals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Add AI-powered risk scores to each primary signal based on its supporting signals
        
        Args:
            company_name: Company name
            primary_signals: List of primary signals
            supporting_signals: List of supporting signals with scores
            
        Returns:
            Primary signals with added risk_score and risk_reasoning
        """
        if not primary_signals:
            return []
        
        # Create mapping of supporting signals
        supporting_map = {s['id']: s for s in supporting_signals}
        
        prompt = f"""You are a Singapore workforce intelligence analyst. Analyze each primary signal for "{company_name}" and assign a comprehensive risk score (0-100).

PRIMARY SIGNALS WITH SUPPORTING EVIDENCE:
{json.dumps(primary_signals, indent=2)}

SUPPORTING SIGNALS DETAILS:
{json.dumps(supporting_signals, indent=2)}

CRITICAL SCORING RULE:
The primary signal's risk_score MUST be primarily derived from its supporting signals' risk_scores.
- Calculate the average/weighted average of supporting signals' risk_scores
- Adjust up/down by maximum ±20 points based on:
  * Volume of evidence (more supporting signals = higher confidence)
  * Pattern consistency (reinforcing evidence = higher risk)
  * Temporal factors (recent signals = higher weight)
  * Cross-signal correlation (interconnected risks = amplification)

TASK:
For each primary signal, provide:
1. risk_score: Integer 0-100 that:
   - STARTS with the average of its supporting signals' risk_scores
   - Then applies adjustment factors (max ±20 points)
   - Example: If 3 supporting signals have scores [20, 20, 25], base = 21.67, final could be 25-41

2. risk_reasoning: 2-3 sentences explaining:
   - Base score from supporting signals (mention their scores)
   - Any adjustment factors applied and why
   - Singapore workforce implications

Return JSON:
{{
    "scored_primary_signals": [
        {{
            "id": "ps_1",
            "risk_score": 35,
            "risk_reasoning": "Based on 3 supporting signals averaging 21.67 (scores: 20, 20, 25), adjusted up to 35 due to multiple sources confirming the pattern. Indicates growing market skepticism affecting business viability and potential job security concerns in Singapore retail sector."
        }}
    ]
}}

Respond with ONLY valid JSON, no markdown formatting."""
        
        try:
            response = self.ai_service.query(prompt, temperature=0.2, max_tokens=2500)
            result = json.loads(response)
            scored_primary_map = {s['id']: s for s in result.get('scored_primary_signals', [])}
            
            # Add scores to original primary signals
            enhanced_primary = []
            for primary in primary_signals:
                primary_copy = primary.copy()
                score_data = scored_primary_map.get(primary['id'], {})
                primary_copy['risk_score'] = score_data.get('risk_score', 60)
                primary_copy['risk_reasoning'] = score_data.get('risk_reasoning', 'Risk assessment pending')
                enhanced_primary.append(primary_copy)
            
            return enhanced_primary
        except Exception as e:
            logger.error(f"Error adding risk scores to primary signals: {e}")
            # Fallback: calculate from supporting signals
            for primary in primary_signals:
                supporting_ids = primary.get('supporting_signal_ids', [])
                supporting_scores = [supporting_map[sid]['risk_score'] for sid in supporting_ids if sid in supporting_map]
                if supporting_scores:
                    # Calculate average and add small boost for multiple signals (max +10)
                    base_score = sum(supporting_scores) / len(supporting_scores)
                    volume_boost = min(len(supporting_scores) * 2, 10)  # +2 per signal, max +10
                    primary['risk_score'] = int(min(base_score + volume_boost, 100))
                    primary['risk_reasoning'] = f'Calculated from {len(supporting_scores)} supporting signals (avg: {base_score:.1f}, +{volume_boost} volume boost)'
                else:
                    primary['risk_score'] = 50
                    primary['risk_reasoning'] = 'No supporting signals available for scoring'
            return primary_signals
    
    def _calculate_overall_risk_score(
        self,
        company_name: str,
        primary_signals: List[Dict[str, Any]],
        supporting_signals: List[Dict[str, Any]],
        financial_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate overall risk score using AI to understand context and patterns
        
        Args:
            company_name: Company name
            primary_signals: List of primary signals with scores
            supporting_signals: List of supporting signals with scores
            financial_data: Optional financial data
            
        Returns:
            Overall risk score with reasoning and confidence
        """
        if not primary_signals:
            return {
                "score": 0,
                "level": "minimal",
                "confidence": "low",
                "reasoning": "Insufficient data for comprehensive risk assessment"
            }
        
        # Prepare financial context
        financial_context = "No financial data available"
        if financial_data:
            summary = financial_data.get('financial_data', {}).get('summary', {})
            financial_context = f"""Financial Data:
- Market Cap: {summary.get('market_cap', 'N/A')}
- Employees: {summary.get('employees', 'N/A')}
- Profit Margin: {summary.get('profit_margin', 'N/A')}
- Sector: {summary.get('sector', 'N/A')}"""
        
        prompt = f"""You are a Singapore workforce intelligence analyst. Calculate the OVERALL RISK SCORE for "{company_name}" considering all available evidence.

PRIMARY SIGNALS:
{json.dumps(primary_signals, indent=2)}

SUPPORTING SIGNALS COUNT: {len(supporting_signals)}
High-risk supporting signals: {len([s for s in supporting_signals if s.get('risk_score', 0) >= 70])}

{financial_context}

TASK:
Analyze ALL evidence comprehensively and provide:

1. score: Integer 0-100 representing overall workforce risk:
   - 90-100: Catastrophic (imminent collapse, mass unemployment)
   - 75-89: Severe (major job losses likely, industry crisis)
   - 60-74: High (significant workforce impact probable)
   - 40-59: Moderate (notable concerns, some job risk)
   - 20-39: Low (minor concerns, limited impact)
   - 0-19: Minimal (stable situation)

2. level: "catastrophic", "severe", "high", "moderate", "low", or "minimal"

3. confidence: "very_high", "high", "medium", or "low" based on:
   - Data source diversity (news + social + financial)
   - Consistency across signals
   - Timespan of evidence
   - Specificity of information

4. reasoning: 3-4 sentences explaining:
   - How all signals converge or diverge
   - Key patterns across evidence
   - Specific Singapore workforce implications
   - Why this score reflects the overall situation

CONSIDER:
- Do multiple independent sources corroborate the same concerns?
- Are risks isolated or systemic?
- What is the potential scale of workforce impact?
- How does this affect Singapore's economic stability?

Return JSON:
{{
    "score": 85,
    "level": "severe",
    "confidence": "high",
    "reasoning": "Convergent evidence from social discourse, news reports, and operational data shows sustained business decline over 5+ years. Multiple store closures confirmed across Singapore. Public perception indicates terminal trajectory. Threatens 200+ retail jobs in critical F&B sector."
}}

Respond with ONLY valid JSON, no markdown formatting."""
        
        try:
            response = self.ai_service.query(prompt, temperature=0.2, max_tokens=1500)
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error(f"Error calculating overall risk score: {e}")
            # Fallback calculation
            avg_primary_score = sum(p.get('risk_score', 50) for p in primary_signals) / len(primary_signals)
            return {
                "score": int(avg_primary_score),
                "level": "moderate" if avg_primary_score < 60 else "high",
                "confidence": "medium",
                "reasoning": f"Calculated from {len(primary_signals)} primary signals with average risk score of {avg_primary_score:.1f}"
            }
    
    def _generate_major_hypothesis(
        self,
        company_name: str,
        primary_signals: List[Dict[str, Any]],
        supporting_signals: List[Dict[str, Any]],
        overall_risk_score: Dict[str, Any]
    ) -> str:
        """
        Generate a comprehensive major hypothesis paragraph synthesizing all signals
        
        Args:
            company_name: Company name
            primary_signals: List of primary signals with scores
            supporting_signals: List of supporting signals with scores
            overall_risk_score: Overall risk score with reasoning
            
        Returns:
            Major hypothesis as a paragraph
        """
        if not primary_signals:
            return f"Insufficient data to generate comprehensive hypothesis for {company_name}."
        
        prompt = f"""You are a Singapore workforce intelligence analyst. Generate a MAJOR HYPOTHESIS paragraph for "{company_name}" that synthesizes ALL evidence into a coherent narrative.

OVERALL RISK SCORE: {overall_risk_score.get('score')}/100 ({overall_risk_score.get('level', 'unknown').upper()})

PRIMARY SIGNALS:
{json.dumps(primary_signals, indent=2)}

SUPPORTING SIGNALS:
{json.dumps(supporting_signals, indent=2)}

TASK:
Write a single comprehensive paragraph (150-250 words) that:

1. Presents the major hypothesis about {company_name}'s workforce risk
2. Incorporates ALL primary signals and their key themes
3. References critical supporting signal evidence
4. Explains the interconnections between different risk factors
5. Contextualizes within Singapore's workforce/economy
6. Concludes with the overall risk assessment and implications

STYLE:
- Professional and analytical tone
- Flow naturally, not as a list
- Use specific evidence ("X store closures", "Y employees affected")
- Make causal connections between signals
- Emphasize workforce/employment impact

EXAMPLE STRUCTURE:
"[Company] faces [primary risk theme] characterized by [key evidence]. [Second primary signal] compounds this through [supporting evidence], while [third signal] indicates [pattern]. Analysis of [source types] reveals [convergent pattern]. This situation threatens [X] jobs in Singapore's [sector], with [timeframe] implications. Overall assessment: [risk level] risk of [specific workforce impact]."

Return JSON:
{{
    "major_hypothesis": "Your comprehensive paragraph here..."
}}

Respond with ONLY valid JSON, no markdown formatting."""
        
        try:
            response = self.ai_service.query(prompt, temperature=0.3, max_tokens=1500)
            result = json.loads(response)
            return result.get('major_hypothesis', '')
        except Exception as e:
            logger.error(f"Error generating major hypothesis: {e}")
            # Fallback: create basic hypothesis
            primary_themes = [p['title'] for p in primary_signals[:3]]
            themes_text = ', '.join(primary_themes)
            return f"{company_name} exhibits multiple risk indicators including {themes_text}. Analysis of {len(supporting_signals)} supporting signals from news, social, and financial sources reveals converging evidence of business challenges. The overall risk score of {overall_risk_score.get('score', 0)}/100 suggests {overall_risk_score.get('level', 'moderate')} risk to Singapore workforce stability. Immediate attention to employment implications is warranted."


