#!/usr/bin/env python3
"""
Test script for advanced analysis across multiple coins
"""

from api_wrapper import analyze_symbol
from advanced_llm_analyzer import AdvancedLLMAnalyzer
import sys

symbols = ['BTC/USD', 'ETH/USD', 'DOGE/USD', 'SOL/USD', 'XRP/USD', 'ADA/USD']

analyzer = AdvancedLLMAnalyzer(use_local_llm=False)

print("\n" + "="*80)
print("TESTING ADVANCED ANALYSIS ACROSS MULTIPLE COINS")
print("="*80 + "\n")

for symbol in symbols:
    print("\n" + "="*80)
    print(f"Testing {symbol}")
    print("="*80)
    try:
        df = analyze_symbol(symbol, timeframe='1h', days=7)
        if df is not None and len(df) > 0:
            analysis = analyzer.generate_actionable_analysis(df, symbol)
            
            if 'error' not in analysis:
                latest = df.iloc[-1]
                print(f"✅ SUCCESS: {len(df)} bars")
                print(f"   Price: ${latest['close']:.4f}")
                print(f"   E: {latest['E']:.2f}σ")
                print(f"   Signal: {latest['Signal']}")
                
                # Check if analysis is unique
                if analysis.get('oracle_status'):
                    rec = analysis['oracle_status'].get('recommendation', '')
                    print(f"   Recommendation: {rec[:80]}...")
                
                if analysis.get('action_plan'):
                    print(f"   ✅ Has action plan")
                    plan = analysis['action_plan']
                    print(f"   Action: {plan['recommendation']}")
                else:
                    print(f"   ⚠️  No action plan (not in entry zone)")
                    
                # Show raw metrics for uniqueness check
                print(f"\n   Raw Metrics:")
                raw = analysis.get('raw_metrics', {})
                print(f"     Current Price: ${raw.get('current_price', 0):.4f}")
                print(f"     Equilibrium: ${raw.get('equilibrium', 0):.4f}")
                print(f"     Deviation: {raw.get('deviation', 0):.2f}σ")
                print(f"     Volume Ratio: {raw.get('volume_ratio', 0):.1f}%")
            else:
                print(f"❌ Analysis error: {analysis['error']}")
        else:
            print(f"❌ FAILED: No data returned")
    except Exception as e:
        print(f"❌ ERROR: {str(e)[:200]}")
        import traceback
        traceback.print_exc()

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
