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
        logger.info(f"Input signals - News: {len(news_signals)}, Social: {len(social_signals)}")
        total_input_signals = len(news_signals) + len(social_signals)
        
        # Step 1: Convert each input signal directly to supporting signal format (1-to-1 mapping)
        # This preserves all original data including URLs
        supporting_signals = self._create_supporting_signals_from_raw_signals(
            news_signals, social_signals
        )
        
        # CRITICAL VALIDATION: Ensure 1-to-1 mapping
        if len(supporting_signals) != total_input_signals:
            logger.error(f"MAPPING ERROR: Expected {total_input_signals} supporting signals, got {len(supporting_signals)}")
            raise ValueError(f"Supporting signal count mismatch: {len(supporting_signals)} != {total_input_signals}")
        
        logger.info(f"✓ Created {len(supporting_signals)} supporting signals from {total_input_signals} input signals (1-to-1 mapping confirmed)")
        
        # Validate all supporting signals have evidence_url
        signals_without_url = [s['id'] for s in supporting_signals if not s.get('evidence_url')]
        if signals_without_url:
            logger.warning(f"⚠ {len(signals_without_url)} supporting signals missing evidence_url: {signals_without_url[:5]}")
        
        # Add financial insights as additional supporting signals
        financial_insights = self._extract_financial_insights(company_name, financial_data)
        for idx, insight in enumerate(financial_insights):
            supporting_signals.append({
                "id": f"ss_financial_{idx + 1}",
                "title": insight.get('key_concern', 'Financial Concern'),
                "source_type": "financial",
                "timeframe": insight.get('timeframe', 'Unknown'),
                "evidence": insight.get('summary', 'No details available'),
                "evidence_url": None,
                "severity": insight.get('severity', 'medium')
            })
        
        total_supporting_signals = len(supporting_signals)
        logger.info(f"Total supporting signals (including {len(financial_insights)} financial): {total_supporting_signals}")
        
        # Dump supporting signals for debugging
        import os
        debug_dir = os.path.join(os.path.dirname(__file__), 'dumps', 'debug')
        os.makedirs(debug_dir, exist_ok=True)
        with open(os.path.join(debug_dir, 'supporting_signals.json'), 'w', encoding='utf-8') as f:
            json.dump(supporting_signals, f, indent=2, ensure_ascii=False)
        logger.info(f"Dumped {len(supporting_signals)} supporting signals to dumps/debug/supporting_signals.json")
        
        # Step 3: Group supporting signals into primary signals
        primary_signals = self._group_into_primary_signals(
            company_name, supporting_signals
        )
        
        # Dump primary signals for debugging
        with open(os.path.join(debug_dir, 'primary_signals.json'), 'w', encoding='utf-8') as f:
            json.dump(primary_signals, f, indent=2, ensure_ascii=False)
        logger.info(f"Dumped {len(primary_signals)} primary signals to dumps/debug/primary_signals.json")
        
        # Create assignment analysis
        all_assigned_ids = set()
        for ps in primary_signals:
            all_assigned_ids.update(ps.get('supporting_signal_ids', []))
        
        all_supporting_ids = {s['id'] for s in supporting_signals}
        unassigned_ids = all_supporting_ids - all_assigned_ids
        
        assignment_report = {
            "total_supporting_signals": len(supporting_signals),
            "total_assigned": len(all_assigned_ids),
            "total_unassigned": len(unassigned_ids),
            "unassigned_signal_ids": list(unassigned_ids),
            "unassigned_details": [s for s in supporting_signals if s['id'] in unassigned_ids],
            "primary_signal_assignments": [
                {
                    "primary_id": ps['id'],
                    "title": ps['title'],
                    "assigned_count": len(ps.get('supporting_signal_ids', [])),
                    "assigned_ids": ps.get('supporting_signal_ids', [])
                }
                for ps in primary_signals
            ]
        }
        
        with open(os.path.join(debug_dir, 'assignment_analysis.json'), 'w', encoding='utf-8') as f:
            json.dump(assignment_report, f, indent=2, ensure_ascii=False)
        
        # CRITICAL VALIDATION: All signals must be assigned
        if len(unassigned_ids) > 0:
            logger.error(f"❌ ASSIGNMENT ERROR: {len(unassigned_ids)}/{len(supporting_signals)} signals unassigned!")
            logger.error(f"Unassigned signal IDs: {sorted(unassigned_ids)}")
            # Force assign unassigned signals to a catch-all primary signal
            if unassigned_ids:
                logger.warning("Force-assigning unassigned signals to primary signals...")
                # Find or create a catch-all primary signal
                catchall_ps = next((ps for ps in primary_signals if 'other' in ps.get('title', '').lower()), None)
                if not catchall_ps:
                    # Add unassigned to the smallest primary signal
                    smallest_ps = min(primary_signals, key=lambda ps: len(ps.get('supporting_signal_ids', [])))
                    smallest_ps['supporting_signal_ids'].extend(sorted(unassigned_ids))
                    logger.warning(f"Added {len(unassigned_ids)} unassigned signals to '{smallest_ps['title']}'")
                else:
                    catchall_ps['supporting_signal_ids'].extend(sorted(unassigned_ids))
                    logger.warning(f"Added {len(unassigned_ids)} unassigned signals to catch-all category")
                
                # Recalculate distributions
                for ps in primary_signals:
                    ps['source_distribution'] = self._calculate_source_distribution(
                        ps.get('supporting_signal_ids', []),
                        supporting_signals
                    )
        else:
            logger.info(f"✓ All {len(supporting_signals)} supporting signals successfully assigned to primary signals")
        
        # Validate source count totals
        total_news_in_primaries = sum(ps['source_distribution']['News'] for ps in primary_signals)
        total_social_in_primaries = sum(ps['source_distribution']['Social'] for ps in primary_signals)
        logger.info(f"Source distribution validation: News={total_news_in_primaries}/{len(news_signals)}, Social={total_social_in_primaries}/{len(social_signals)}")
        
        if total_news_in_primaries != len(news_signals) or total_social_in_primaries != len(social_signals):
            logger.error(f"❌ SOURCE COUNT MISMATCH! Expected News={len(news_signals)}, Social={len(social_signals)}")
            logger.error(f"Got News={total_news_in_primaries}, Social={total_social_in_primaries}")
        
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
    
    def _create_supporting_signals_from_raw_signals(
        self,
        news_signals: List[Dict[str, Any]],
        social_signals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Convert raw input signals directly to supporting signals (1-to-1 mapping)
        Preserves all original signal data including URLs
        Generates concise, insight-focused titles using AI
        
        Args:
            news_signals: List of news signal data
            social_signals: List of social signal data
            
        Returns:
            List of supporting signals with preserved URLs and metadata
        """
        supporting_signals = []
        signal_counter = 1
        
        # Process news signals
        for signal in news_signals:
            full_title = signal.get('metadata', {}).get('title', '') or signal.get('headline', '') or signal.get('extracted_text', '')[:60]
            source_type = signal.get('source_type', 'news')
            date = signal.get('metadata', {}).get('publish_date', '') or signal.get('published_date', '') or signal.get('metadata', {}).get('date', 'Unknown')
            evidence_text = signal.get('extracted_text', 'No content available')
            metadata = signal.get('metadata', {}) or {}
            evidence_url = (
                signal.get('source_url', '')
                or signal.get('source_link', '')
                or signal.get('link', '')
                or signal.get('url', '')
                or metadata.get('source_url', '')
                or metadata.get('url', '')
                or metadata.get('link', '')
            )
            
            # Generate concise insight-focused title using AI
            insight_title = self._generate_insight_title(full_title, evidence_text, source_type)
            
            # Clean evidence text (remove repetitive title at the end)
            cleaned_evidence = self._clean_evidence_text(evidence_text, full_title)
            
            # Keep evidence text clean; render links separately in UI
            
            # Determine timeframe from date
            timeframe = 'Unknown'
            if date and date != 'Unknown':
                try:
                    from datetime import datetime as dt
                    if 'T' in str(date) or '-' in str(date):
                        year = str(date)[:4]
                        timeframe = year
                    else:
                        timeframe = str(date)
                except:
                    timeframe = str(date)[:4] if len(str(date)) >= 4 else 'Unknown'
            
            supporting_signals.append({
                "id": f"ss_{signal_counter}",
                "title": insight_title,
                "source_type": source_type,
                "timeframe": timeframe,
                "evidence": cleaned_evidence[:700],  # Increased limit to accommodate URL
                "evidence_url": evidence_url,
                "severity": "medium"  # Default severity, will be scored later
            })
            signal_counter += 1
        
        # Process social signals
        for signal in social_signals:
            full_title = signal.get('post_title', '') or signal.get('extracted_text', '')[:60]
            source_type = signal.get('source_type', 'social')
            # Check multiple possible date fields for social/Reddit signals
            date = (
                signal.get('created_date', '')
                or signal.get('metadata', {}).get('publish_date', '')
                or signal.get('metadata', {}).get('date', '')
                or signal.get('published_date', '')
                or 'Unknown'
            )
            evidence_text = signal.get('extracted_text', '') or signal.get('post_text', 'No content available')
            metadata = signal.get('metadata', {}) or {}
            evidence_url = (
                signal.get('source_url', '')
                or signal.get('source_link', '')
                or signal.get('link', '')
                or signal.get('url', '')
                or metadata.get('source_url', '')
                or metadata.get('url', '')
                or metadata.get('link', '')
            )
            
            # Generate concise insight-focused title using AI
            insight_title = self._generate_insight_title(full_title, evidence_text, source_type)
            
            # Clean evidence text
            cleaned_evidence = self._clean_evidence_text(evidence_text, full_title)

            # For social sources, prefer linking to the source instead of showing full content
            if evidence_url:
                cleaned_evidence = ""
            
            # Keep evidence text clean; render links separately in UI
            
            # Determine timeframe from date
            timeframe = 'Unknown'
            if date and date != 'Unknown':
                try:
                    from datetime import datetime as dt
                    # Handle ISO format dates
                    if 'T' in str(date) or '-' in str(date):
                        parsed_date = dt.fromisoformat(str(date).replace('Z', '+00:00'))
                        timeframe = str(parsed_date.year)
                    else:
                        year = str(date)[:4]
                        timeframe = year
                except:
                    try:
                        year = str(date)[:4]
                        timeframe = year
                    except:
                        timeframe = 'Unknown'
            
            supporting_signals.append({
                "id": f"ss_{signal_counter}",
                "title": insight_title,
                "source_type": source_type,
                "timeframe": timeframe,
                "evidence": cleaned_evidence[:700],
                "evidence_url": evidence_url,
                "severity": "medium"
            })
            signal_counter += 1
        
        return supporting_signals
        
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
    
    def _generate_insight_title(self, full_title: str, evidence_text: str, source_type: str) -> str:
        """
        Generate a concise, insight-focused title from the original title
        Examples:
        - "Company pleads guilty to underpaying employees" → "guilty of underpayment"
        - "Store closure affects 50 workers" → "store closure, worker impact"
        
        Args:
            full_title: Original full title
            evidence_text: Full evidence text
            source_type: Type of source (news, social, etc.)
            
        Returns:
            Concise title string
        """
        if not full_title:
            return "Untitled signal"
        
        # Use AI to extract key insight
        prompt = f"""Extract the KEY INSIGHT from this headline in 2-5 words. Focus on the ACTION or EVENT.

Headline: {full_title}

Examples:
- "Company x pleads guilty to underpaying 7 employees" → "guilty of underpayment"
- "Company announces layoffs of 100 workers" → "layoffs announced"
- "Store closure affects employees" → "store closure"

Return ONLY the concise insight (2-5 words), nothing else."""
        
        try:
            insight = self.ai_service.query(prompt, temperature=0.1, max_tokens=20)
            insight = insight.strip()

            # Remove code fences if present
            if insight.startswith("```"):
                insight = insight.strip("`\n \t")
            
            # Handle JSON responses
            if insight.startswith('{'):
                try:
                    parsed = json.loads(insight)
                    insight = (
                        parsed.get('key_insight')
                        or parsed.get('insight')
                        or parsed.get('title')
                        or parsed.get('summary')
                        or insight
                    )
                except json.JSONDecodeError:
                    # Best-effort extraction for malformed JSON-like responses
                    import re
                    match = re.search(r'"(?:key_insight|insight|title)"\s*:\s*"([^"]+)"', insight)
                    if match:
                        insight = match.group(1)
            else:
                # Handle embedded JSON in plain text
                import re
                match = re.search(r'\{[^\}]*"(?:key_insight|insight|title)"\s*:\s*"([^"]+)"[^\}]*\}', insight)
                if match:
                    insight = match.group(1)
            
            # Clean up quotes, backticks, and whitespace
            insight = insight.strip('"\'\'` \n\r\t')
            
            # Capitalize first letter
            if insight:
                insight = insight[0].upper() + insight[1:]
            
            # Validate it's concise enough
            if len(insight) < 80 and len(insight.split()) <= 8:
                return insight
        except Exception as e:
            logger.warning(f"Failed to generate insight title: {e}")
        
        # Fallback: use original title
        title = ' '.join(full_title.split())
        if len(title) > 150:
            title = title[:147] + "..."
        return title
    
    def _clean_evidence_text(self, evidence: str, title: str) -> str:
        """
        Clean evidence text to remove repetitive content
        
        Args:
            evidence: Original evidence text
            title: Original title to remove if duplicated
            
        Returns:
            Cleaned evidence text
        """
        import re
        
        # Remove the title if it appears at the end (common pattern)
        if title and title in evidence:
            # Remove exact title match
            evidence = evidence.replace(title, '').strip()
        
        # Remove duplicate consecutive sentences
        sentences = re.split(r'[.!?]\s+', evidence)
        seen = set()
        unique_sentences = []
        for sent in sentences:
            sent_lower = sent.lower().strip()
            if sent_lower and sent_lower not in seen and len(sent_lower) > 20:
                seen.add(sent_lower)
                unique_sentences.append(sent)
        
        cleaned = '. '.join(unique_sentences)
        if cleaned and not cleaned.endswith('.'):
            cleaned += '.'
            
        return cleaned.strip()
    
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
        # Process ALL signals - no arbitrary limit
        # If there are too many, we'll batch them
        total_signals = len(signals)
        logger.info(f"Processing {total_signals} {source_type} signals...")
        
        for idx, signal in enumerate(signals):
            text = signal.get('extracted_text', '')
            title = signal.get('metadata', {}).get('title', '') or signal.get('headline', '')
            date = signal.get('metadata', {}).get('publish_date', '') or signal.get('published_date', 'Unknown date')
            source_name = signal.get('source_name', 'Unknown source')
            
            signal_texts.append({
                "id": idx,
                "title": title,
                "text": text[:300],  # Reduce per-signal text to fit more signals
                "date": date,
                "source": source_name
            })
        
        prompt = self._get_summarization_prompt(company_name, signal_texts, source_type)
        
        try:
            # Significantly increase max_tokens to handle more signals
            response = self.ai_service.query(prompt, temperature=0.3, max_tokens=6000)
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

DATA TO ANALYZE ({len(signal_texts)} signals):
{signals_json}

CRITICAL TASK - READ CAREFULLY:
You have {len(signal_texts)} distinct signals. Your goal is to extract AT LEAST {max(15, int(len(signal_texts) * 0.65))} SEPARATE insights.

RULES:
1. DEFAULT: Each signal should become its own insight UNLESS multiple signals discuss the EXACT SAME event
2. "Same event" means: same date, same incident, same people involved
3. Different timeframes = SEPARATE insights (e.g., 2011 incident vs 2020 incident)
4. Different aspects = SEPARATE insights (e.g., closure vs lawsuit vs employee issue)
5. Different locations/people = SEPARATE insights
6. If uncertain whether to combine, DON'T - keep them separate

TARGET: Create {max(15, int(len(signal_texts) * 0.65))} or MORE insights from these {len(signal_texts)} signals.

For each distinct insight:
1. Provide a brief summary (1-2 sentences)
2. Identify the key concern or theme
3. Note the timeframe/date if available
4. List which signal IDs support this insight (usually 1-2 IDs unless truly identical)
5. Assess severity (high if critical workforce/operational issues, medium for concerning trends, low for minor issues)

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
- Business operations and closures (each closure/issue = separate insight)
- Financial performance concerns (group by timeframe)
- Employee/workforce issues (layoffs, underpayment, treatment, retention - separate by incident)
- Market perception and reputation (separate by theme)
- Industry trends
- Regulatory or legal issues (each case = separate insight)

IMPORTANT: Maximize the number of distinct insights. Better to have 15+ specific insights than 5 overly-broad ones.

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
            # Increase token limit to preserve more supporting signals
            response = self.ai_service.query(prompt, temperature=0.3, max_tokens=4500)
            result = json.loads(response)
            logger.info(f"Created {len(result.get('supporting_signals', []))} supporting signals from {len(all_insights)} insights")
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

INSIGHTS ({len(insights)} total):
{insights_json}

CRITICAL INSTRUCTION:
Each insight should become its OWN supporting signal. DO NOT combine or merge insights.
- If you receive 24 insights, create approximately 20-24 supporting signals
- Only combine insights if they describe the EXACT SAME incident with the same date
- Different timeframes, different aspects, or different concerns = separate supporting signals

TASK:
Transform these insights into supporting signals. Each supporting signal should have:
1. A clear, descriptive title (3-7 words) that summarizes the signal
2. The source type EXACTLY as provided in the insight (news, social, or financial)
3. The timeframe (year or date range)
4. Evidence data (the detailed insight/summary)
5. Severity level (high, medium, or low)

IMPORTANT: 
- Create a 1-to-1 mapping: one insight = one supporting signal (unless identical)
- Preserve the source_type from each insight exactly
- DO NOT over-consolidate - we want comprehensive analysis with many signals

Return a JSON object with this structure:
{{
    "supporting_signals": [
        {{
            "id": "ss_1",
            "title": "Founders Charged Underpaying Workers",
            "source_type": "news",
            "timeframe": "2020",
            "evidence": "Founders Daniel Ong and Jaime Teo charged with underpaying 7 foreign workers over 2 years.",
            "severity": "high"
        }},
        {{
            "id": "ss_2",
            "title": "Store Closures in 2019",
            "source_type": "news",
            "timeframe": "2019",
            "evidence": "News reports highlight store shutdowns and operational challenges.",
            "severity": "high"
        }},
            "id": "ss_2",
            "title": "Terminal Industry Outlook",
            "source_type": "social",
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
        Iterates through signals one by one to ensure all are assigned
        
        Args:
            company_name: Company name
            supporting_signals: List of supporting signals
            
        Returns:
            List of primary signals with grouped supporting signals
        """
        if not supporting_signals:
            return []
        
        logger.info(f"Grouping {len(supporting_signals)} signals iteratively...")
        
        # Define primary signal categories upfront
        primary_signals = {
            "OPERATIONAL_DEGRADATION": {
                "id": "ps_1",
                "title": "OPERATIONAL DEGRADATION",
                "description": "Evidence of declining operations, store closures, and business sustainability concerns",
                "risk_level": "high",
                "supporting_signal_ids": [],
                "key_indicators": []
            },
            "FINANCIAL_DISTRESS": {
                "id": "ps_2",
                "title": "FINANCIAL DISTRESS",
                "description": "Indicators of financial instability, debt, losses, and poor performance",
                "risk_level": "high",
                "supporting_signal_ids": [],
                "key_indicators": []
            },
            "WORKFORCE_ISSUES": {
                "id": "ps_3",
                "title": "WORKFORCE ISSUES",
                "description": "Concerns related to employee treatment, layoffs, underpayment, and labor violations",
                "risk_level": "high",
                "supporting_signal_ids": [],
                "key_indicators": []
            },
            "REGULATORY_LEGAL": {
                "id": "ps_4",
                "title": "REGULATORY/LEGAL RISKS",
                "description": "Legal challenges, fines, prosecutions, and compliance issues",
                "risk_level": "high",
                "supporting_signal_ids": [],
                "key_indicators": []
            },
            "MARKET_PERCEPTION": {
                "id": "ps_5",
                "title": "MARKET PERCEPTION",
                "description": "Public sentiment, reputation concerns, and customer complaints",
                "risk_level": "medium",
                "supporting_signal_ids": [],
                "key_indicators": []
            },
            "STRATEGIC_ANOMALIES": {
                "id": "ps_6",
                "title": "STRATEGIC ANOMALIES",
                "description": "Management decisions, ownership changes, and strategic issues",
                "risk_level": "medium",
                "supporting_signal_ids": [],
                "key_indicators": []
            },
            "INDUSTRY_CHALLENGES": {
                "id": "ps_7",
                "title": "INDUSTRY CHALLENGES",
                "description": "Market saturation, competitive pressure, and consumer trend shifts",
                "risk_level": "medium",
                "supporting_signal_ids": [],
                "key_indicators": []
            },
            "PRODUCT_SERVICE_ISSUES": {
                "id": "ps_8",
                "title": "PRODUCT/SERVICE ISSUES",
                "description": "Quality decline, product defects, and service failures",
                "risk_level": "medium",
                "supporting_signal_ids": [],
                "key_indicators": []
            }
        }
        
        # Iterate through each signal and assign to appropriate category
        for idx, signal in enumerate(supporting_signals):
            try:
                category = self._classify_single_signal(company_name, signal, list(primary_signals.keys()))
                
                if category in primary_signals:
                    primary_signals[category]['supporting_signal_ids'].append(signal['id'])
                    logger.info(f"[{idx+1}/{len(supporting_signals)}] {signal['id']} → {category}")
                else:
                    # Fallback to a default category if AI returns invalid category
                    logger.warning(f"Invalid category '{category}' for {signal['id']}, using MARKET_PERCEPTION")
                    primary_signals['MARKET_PERCEPTION']['supporting_signal_ids'].append(signal['id'])
                    
            except Exception as e:
                logger.error(f"Error classifying {signal['id']}: {e}, assigning to MARKET_PERCEPTION")
                primary_signals['MARKET_PERCEPTION']['supporting_signal_ids'].append(signal['id'])
        
        # Filter out empty primary signals and calculate distributions
        result = []
        for ps_data in primary_signals.values():
            if ps_data['supporting_signal_ids']:
                ps_data['source_distribution'] = self._calculate_source_distribution(
                    ps_data['supporting_signal_ids'],
                    supporting_signals
                )
                result.append(ps_data)
        
        logger.info(f"✓ Created {len(result)} primary signals covering all {len(supporting_signals)} supporting signals")
        return result
    
    def _classify_single_signal(
        self,
        company_name: str,
        signal: Dict[str, Any],
        available_categories: List[str]
    ) -> str:
        """
        Classify a single signal into one primary category
        
        Args:
            company_name: Company name
            signal: Single supporting signal
            available_categories: List of available category keys
            
        Returns:
            Category key (e.g., "WORKFORCE_ISSUES")
        """
        prompt = f"""Classify this risk signal for "{company_name}" into ONE category.

SIGNAL:
- ID: {signal['id']}
- Title: {signal['title']}
- Source: {signal['source_type']}
- Severity: {signal.get('severity', 'medium')}

AVAILABLE CATEGORIES:
1. OPERATIONAL_DEGRADATION - Store/business closures, operational decline
2. FINANCIAL_DISTRESS - Losses, debt, poor financial performance
3. WORKFORCE_ISSUES - Layoffs, underpayment, labor violations, employee concerns
4. REGULATORY_LEGAL - Legal cases, fines, compliance issues, prosecutions
5. MARKET_PERCEPTION - Reputation damage, customer complaints, public sentiment
6. STRATEGIC_ANOMALIES - Management changes, ownership changes, questionable decisions
7. INDUSTRY_CHALLENGES - Market saturation, competitive pressure, consumer trends
8. PRODUCT_SERVICE_ISSUES - Quality decline, product defects, service failures

Return ONLY the category key (e.g., "WORKFORCE_ISSUES"), nothing else."""
        
        try:
            response = self.ai_service.query(prompt, temperature=0.1, max_tokens=50)
            category = response.strip()
            
            # Handle JSON responses
            if category.startswith('{'):
                try:
                    parsed = json.loads(category)
                    category = parsed.get('category', category)
                except json.JSONDecodeError:
                    pass
            
            # Clean up quotes and whitespace
            category = category.strip('"\'` \n\r\t')
            
            # Validate response
            if category not in available_categories:
                logger.warning(f"AI returned invalid category '{category}', defaulting to MARKET_PERCEPTION")
                return "MARKET_PERCEPTION"
            
            return category
        except Exception as e:
            logger.error(f"Error classifying signal {signal['id']}: {e}")
            return "MARKET_PERCEPTION"
    
    def _get_primary_signals_prompt(
        self,
        company_name: str,
        supporting_signals: List[Dict[str, Any]]
    ) -> str:
        """Generate prompt for grouping into primary signals"""
        # Extract just the essential info for the prompt to reduce token usage
        signal_summaries = []
        for s in supporting_signals:
            signal_summaries.append({
                "id": s['id'],
                "title": s['title'],
                "source_type": s['source_type'],
                "severity": s.get('severity', 'medium')
            })
        
        signals_json = json.dumps(signal_summaries, indent=2)
        all_signal_ids = [s['id'] for s in supporting_signals]
        
        return f"""You are analyzing risk signals for "{company_name}". Group the following {len(supporting_signals)} supporting signals into broader primary signal categories.

SUPPORTING SIGNALS TO GROUP ({len(supporting_signals)} total):
{signals_json}

CRITICAL RULES - FAILURE TO FOLLOW WILL BREAK THE SYSTEM:
1. EVERY signal ID from {all_signal_ids[0]} to {all_signal_ids[-1]} MUST be assigned to exactly ONE primary signal
2. NO signal can be assigned to multiple primary signals (no duplicates)
3. NO signal can be left unassigned
4. Count: {len(supporting_signals)} signals in → {len(supporting_signals)} assignments out
5. Each primary signal should have 4-10 supporting signals

BEFORE RESPONDING:
✓ Count total IDs in your response = {len(supporting_signals)}?
✓ Check for duplicate IDs?
✓ Check every ID from the list above is included?

GROUPING CATEGORIES (choose 4-8 of these):
- OPERATIONAL DEGRADATION: Store/business closures, operational decline
- FINANCIAL DISTRESS: Losses, debt, poor financial performance  
- WORKFORCE ISSUES: Layoffs, underpayment, labor violations, employee concerns
- REGULATORY/LEGAL RISKS: Legal cases, fines, compliance issues, prosecutions
- MARKET PERCEPTION: Reputation damage, customer complaints, public sentiment
- STRATEGIC ANOMALIES: Management changes, questionable decisions
- INDUSTRY CHALLENGES: Market saturation, competitive pressure, consumer trends
- PRODUCT/SERVICE ISSUES: Quality decline, product defects, service failures

Return ONLY valid JSON (no markdown):
{{
    "primary_signals": [
        {{
            "id": "ps_1",
            "title": "WORKFORCE ISSUES",
            "description": "Concerns related to employee treatment and labor violations",
            "risk_level": "high",
            "supporting_signal_ids": ["ss_3", "ss_14", "ss_15", "ss_17", "ss_36", "ss_37"],
            "key_indicators": ["Underpayment", "Labor violations"]
        }}
    ]
}}"""
    
    def _calculate_source_distribution(
        self,
        supporting_signal_ids: List[str],
        supporting_signals: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate distribution of sources for a primary signal"""
        distribution = {"News": 0, "Social": 0, "Financial": 0}
        
        for signal in supporting_signals:
            if signal['id'] in supporting_signal_ids:
                source_type = signal.get('source_type', 'unknown').lower()
                # Map source types to distribution categories
                if source_type in ['news', 'google_news', 'blog']:
                    distribution['News'] += 1
                elif source_type in ['social', 'reddit', 'forum']:
                    distribution['Social'] += 1
                elif source_type == 'financial':
                    distribution['Financial'] += 1
                else:
                    logger.warning(f"Unknown source_type in supporting signal: '{source_type}' (signal id: {signal['id']})")
        
        # Log distribution for debugging
        total = sum(distribution.values())
        logger.info(f"Source distribution for {len(supporting_signal_ids)} signals: News={distribution['News']}, Social={distribution['Social']}, Financial={distribution['Financial']} (total={total})")
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


