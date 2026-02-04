"""
Test script for Hypothesis Engine
"""
import json
import os
from hypothesis_engine import HypothesisEngine
from ai_service import AIService

def test_hypothesis_engine():
    """Test the hypothesis engine with sample data"""
    
    # Initialize engine
    print("Initializing Hypothesis Engine...")
    ai_service = AIService()
    engine = HypothesisEngine(ai_service)
    
    # Load a sample dump file
    dump_dir = os.path.join(os.path.dirname(__file__), 'dumps')
    dump_files = [f for f in os.listdir(dump_dir) if f.endswith('.json') and f != '_dump_checklist.json']
    
    if not dump_files:
        print("No dump files found to test with")
        return
    
    # Use the first dump file
    test_file = dump_files[0]
    print(f"\nLoading test data from: {test_file}")
    
    with open(os.path.join(dump_dir, test_file), 'r', encoding='utf-8') as f:
        dump_data = json.load(f)
    
    # Extract signals
    signals = dump_data.get('signals', [])
    news_signals = [s for s in signals if s.get('source_type', '').lower() in ['news', 'blog']]
    social_signals = [s for s in signals if s.get('source_type', '').lower() in ['social', 'forum']]
    financial_data = dump_data.get('financial_data')
    
    company_name = dump_data.get('company_name', 'Unknown Company')
    
    print(f"\nCompany: {company_name}")
    print(f"News signals: {len(news_signals)}")
    print(f"Social signals: {len(social_signals)}")
    print(f"Has financial data: {financial_data is not None}")
    
    # Run analysis
    print("\n" + "="*60)
    print("RUNNING HYPOTHESIS ANALYSIS")
    print("="*60)
    
    try:
        result = engine.analyze_company_risk(
            company_name=company_name,
            news_signals=news_signals,
            social_signals=social_signals,
            financial_data=financial_data
        )
        
        # Display results
        print("\n" + "="*60)
        print("ANALYSIS RESULTS")
        print("="*60)
        
        # Overall Risk Score
        overall_risk = result.get('overall_risk_score', {})
        print(f"\n🎯 OVERALL RISK SCORE: {overall_risk.get('score', 0)}/100")
        print(f"   Level: {overall_risk.get('level', 'unknown').upper()}")
        print(f"   Confidence: {overall_risk.get('confidence', 'unknown').upper()}")
        print(f"   Reasoning: {overall_risk.get('reasoning', 'N/A')}")
        
        # Major Hypothesis
        major_hypothesis = result.get('major_hypothesis', 'N/A')
        print(f"\n📋 MAJOR HYPOTHESIS:")
        print(f"   {major_hypothesis}")
        
        # Risk Summary
        risk_summary = result['risk_summary']
        print(f"\n\n📊 RISK SUMMARY:")
        print(f"   Overall Risk: {risk_summary['overall_risk'].upper()}")
        print(f"   Confidence: {risk_summary['confidence'].upper()}")
        print(f"   Summary: {risk_summary['summary']}")
        print(f"   Recommendation: {risk_summary['recommendation']}")
        
        print(f"\n\n🎯 PRIMARY SIGNALS: {len(result['primary_signals'])}")
        for i, ps in enumerate(result['primary_signals'], 1):
            print(f"\n{i}. {ps['title']} (Risk: {ps['risk_level'].upper()})")
            print(f"   Score: {ps.get('risk_score', 'N/A')}/100")
            print(f"   {ps['description']}")
            print(f"   Risk Reasoning: {ps.get('risk_reasoning', 'N/A')}")
            print(f"   Supporting Signals: {len(ps['supporting_signal_ids'])}")
            print(f"   Key Indicators: {', '.join(ps['key_indicators'][:3])}")
        
        print(f"\n\n📌 SUPPORTING SIGNALS: {len(result['supporting_signals'])}")
        for i, ss in enumerate(result['supporting_signals'][:5], 1):
            print(f"\n{i}. {ss['title']} ({ss['source_type']}, {ss['timeframe']})")
            print(f"   Score: {ss.get('risk_score', 'N/A')}/100")
            print(f"   Severity: {ss['severity']}")
            print(f"   Risk Reasoning: {ss.get('risk_reasoning', 'N/A')}")
            print(f"   Evidence: {ss['evidence'][:100]}...")
        
        if len(result['supporting_signals']) > 5:
            print(f"\n   ... and {len(result['supporting_signals']) - 5} more")
        
        # Save results
        output_file = os.path.join(dump_dir, f'hypothesis_analysis_{company_name.lower().replace(" ", "_")}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n\nResults saved to: {output_file}")
        print("\n" + "="*60)
        print("TEST COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\n\nERROR during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hypothesis_engine()
