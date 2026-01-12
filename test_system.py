#!/usr/bin/env python3
"""
End-to-end system test for Quant Oracle
Tests all components: data sources, oracle, LLM, API
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test all imports work"""
    print("Testing imports...")
    try:
        import pandas as pd
        import numpy as np
        from scipy import fft
        import ccxt
        from pycoingecko import CoinGeckoAPI
        print("✅ Core dependencies imported")
        
        from backend.config import validate_config
        from backend.data_sources import fetch_ohlcv_data
        from backend.api_wrapper import analyze_symbol, run_backtest, analyze_multiple_timeframes
        from backend.llm_analyzer import LLMAnalyzer
        print("✅ All modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    try:
        from backend.config import validate_config
        validate_config()
        print(f"✅ Config valid")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def test_data_sources():
    """Test data source integration"""
    print("\nTesting data sources...")
    try:
        from backend.data_sources import fetch_ohlcv_data
        
        # Test data fetch (small dataset)
        df = fetch_ohlcv_data('BTC/USD', days=7, source='auto')
        if df is not None and len(df) > 0:
            print(f"✅ Data fetched: {len(df)} bars")
            print(f"   Columns: {list(df.columns)}")
            print(f"   Date range: {df.index[0]} to {df.index[-1]}")
            return True
        else:
            print("❌ No data returned")
            return False
    except Exception as e:
        print(f"❌ Data source test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_oracle():
    """Test oracle analysis"""
    print("\nTesting oracle analysis...")
    try:
        from backend.api_wrapper import analyze_symbol
        
        df = analyze_symbol('BTC/USD', timeframe='1h', days=7)
        if df is not None and len(df) > 0:
            latest = df.iloc[-1]
            print(f"✅ Oracle analysis complete: {len(df)} bars")
            print(f"   Price: ${latest['close']:.2f}")
            print(f"   VWAP: ${latest['vwap']:.2f}")
            print(f"   Deviation: {latest['deviation']:.2f}σ")
            print(f"   Signal: {latest['signal']}")
            print(f"   Volume: {latest['volume_ratio']:.1f}%")
            
            # Verify all required columns exist
            required = ['vwap', 'deviation', 'signal', 'volume_ratio', 'phase']
            missing = [col for col in required if col not in df.columns]
            if missing:
                print(f"⚠️  Missing columns: {missing}")
                return False
            
            return True
        else:
            print("❌ Oracle returned no data")
            return False
    except Exception as e:
        print(f"❌ Oracle test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backtest():
    """Test backtesting"""
    print("\nTesting backtest...")
    try:
        from backend.api_wrapper import run_backtest
        
        results = run_backtest('BTC/USD', timeframe='1h', days=30, holding_periods=[5, 10])
        if results:
            print(f"✅ Backtest complete")
            print(f"   Symbol: {results['symbol']}")
            print(f"   Bars: {results['total_bars']}")
            
            if 'signal_performance' in results:
                for signal, perf in results['signal_performance'].items():
                    print(f"   {signal}: {perf['count']} signals, {perf['win_rate_10']:.1f}% win rate")
            
            return True
        else:
            print("❌ Backtest returned no results")
            return False
    except Exception as e:
        print(f"❌ Backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_timeframe():
    """Test multi-timeframe analysis"""
    print("\nTesting multi-timeframe analysis...")
    try:
        from backend.api_wrapper import analyze_multiple_timeframes
        
        results = analyze_multiple_timeframes('BTC/USD', timeframes=['1h', '4h'])
        if results:
            print(f"✅ Multi-timeframe analysis complete")
            print(f"   Symbol: {results['symbol']}")
            
            if 'timeframes' in results:
                for tf, data in results['timeframes'].items():
                    print(f"   {tf}: {data['signal']} ({data['deviation']:.2f}σ)")
            
            if 'confluence' in results:
                print(f"   Confluence: {results['confluence']['score']:.1f}%")
            
            return True
        else:
            print("❌ Multi-timeframe returned no results")
            return False
    except Exception as e:
        print(f"❌ Multi-timeframe test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_analyzer():
    """Test LLM analyzer (fallback mode)"""
    print("\nTesting LLM analyzer...")
    try:
        from backend.llm_analyzer import LLMAnalyzer
        from backend.api_wrapper import analyze_symbol
        
        # Get sample data
        df = analyze_symbol('BTC/USD', timeframe='1h', days=7)
        if df is None or len(df) == 0:
            print("⚠️  No data for LLM test")
            return False
        
        # Test analyzer (will use fallback if transformers not available)
        analyzer = LLMAnalyzer()
        analysis = analyzer.analyze_market_data(df, 'BTC/USD')
        
        if analysis:
            print(f"✅ LLM analysis complete")
            print(f"   Method: {analysis['method']}")
            print(f"   Model: {analysis['model']}")
            print(f"   Analysis length: {len(analysis['analysis'])} chars")
            
            # Show first 200 chars
            preview = analysis['analysis'][:200]
            print(f"   Preview: {preview}...")
            
            return True
        else:
            print("❌ LLM analyzer returned no results")
            return False
    except Exception as e:
        print(f"❌ LLM analyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_server():
    """Test API server can start"""
    print("\nTesting API server...")
    try:
        # Just test import, don't actually start server
        from backend.api.server import app
        print("✅ API server module loaded")
        print("   To start server: cd backend && python api/server.py")
        return True
    except Exception as e:
        print(f"❌ API server test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("QUANT ORACLE - SYSTEM TEST")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Data Sources", test_data_sources),
        ("Oracle Analysis", test_oracle),
        ("Backtesting", test_backtest),
        ("Multi-Timeframe", test_multi_timeframe),
        ("LLM Analyzer", test_llm_analyzer),
        ("API Server", test_api_server),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
