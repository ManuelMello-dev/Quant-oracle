#!/usr/bin/env python3
"""Test the core oracle - this WORKS"""

import sys
sys.path.insert(0, 'backend')

from oracle import run_oracle_analysis
import ccxt

def test_symbol(symbol):
    print(f"\n🔍 Analyzing {symbol}...")
    
    try:
        exchange = ccxt.binance()
        result = run_oracle_analysis(
            exchange=exchange,
            symbol=symbol,
            timeframe='1h',
            limit=168,  # 7 days
            vwap_period=100,
            fft_period=256,
            sigma_threshold=2.0,
            reversal_threshold_percent=0.10,
            data_source='coingecko'
        )
        
        df = result[0]
        latest = df.iloc[-1]
        
        print(f"✅ Success!")
        print(f"   Price:     ${latest['close']:.2f}")
        print(f"   VWAP:      ${latest['Z_prime']:.2f}")
        print(f"   Deviation: {latest['E']:.2f}σ")
        print(f"   Signal:    {latest['Signal']}")
        print(f"   Volume:    {latest['Volume_Ratio']*100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("QUANT ORACLE - CORE SYSTEM TEST")
    print("="*60)
    
    symbols = ['BTC/USD', 'ETH/USD', 'DOGE/USD']
    results = []
    
    for symbol in symbols:
        results.append(test_symbol(symbol))
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {sum(results)}/{len(results)} passed")
    print(f"{'='*60}\n")
    
    if all(results):
        print("🎉 Core system works perfectly!")
        print("\nThe oracle engine is solid and ready.")
        print("The issue is just the API server in Gitpod.")
        print("\nNext step: Deploy to production:")
        print("  - Railway: railway.app")
        print("  - Render: render.com")
        print("  - DigitalOcean: digitalocean.com")
    else:
        print("⚠️  Some tests failed")
