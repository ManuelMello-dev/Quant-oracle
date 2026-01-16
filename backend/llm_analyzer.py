"""LLM-based Professional Analysis Engine
Uses OpenAI API for professional-grade analysis
"""

import json
import os
from typing import Dict, List, Optional
import pandas as pd
from openai import OpenAI

# Initialize OpenAI client
try:
    client = OpenAI()
    OPENAI_AVAILABLE = True
except Exception as e:
    OPENAI_AVAILABLE = False
    print(f"⚠️  OpenAI client not available: {e}")


class LLMAnalyzer:
    """Professional analysis using OpenAI API"""
    
    def __init__(self, model_name: str = "gpt-4.1-mini"):
        """
        Initialize LLM analyzer using OpenAI API
        
        Args:
            model_name: OpenAI model identifier
                       Default: gpt-4.1-mini (fast and cost-effective)
                       Alternatives: 
                       - "gpt-4.1-nano" (faster, lower cost)
                       - "gpt-4" (most capable, higher cost)
        """
        self.model_name = model_name
        self.initialized = OPENAI_AVAILABLE
        
        if not OPENAI_AVAILABLE:
            print("⚠️  OpenAI API not available. Using rule-based analysis.")
    
    def analyze_market_data(self, df: pd.DataFrame, symbol: str) -> Dict:
        """
        Generate professional analysis from market data
        
        Args:
            df: DataFrame with OHLCV + indicators
            symbol: Trading pair symbol
            
        Returns:
            Dict with analysis sections
        """
        if not self.initialized:
            return self._fallback_analysis(df, symbol)
        
        # Extract key metrics
        latest = df.iloc[-1]
        metrics = self._extract_metrics(df, latest)
        
        # Generate analysis prompt
        prompt = self._create_analysis_prompt(symbol, metrics)
        
        # Generate analysis using OpenAI API
        try:
            response = client.messages.create(
                model=self.model_name,
                max_tokens=512,
                temperature=0.7,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional quantitative analyst specializing in cryptocurrency trading. Provide concise, actionable market insights based on technical analysis data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            analysis_text = response.content[0].text.strip()
            
            return {
                'symbol': symbol,
                'analysis': analysis_text,
                'metrics': metrics,
                'model': self.model_name,
                'method': 'llm'
            }
        except Exception as e:
            print(f"⚠️  LLM generation failed: {e}. Using rule-based analysis.")
            return self._fallback_analysis(df, symbol)
    
    def _extract_metrics(self, df: pd.DataFrame, latest: pd.Series) -> Dict:
        """Extract key metrics for analysis"""
        return {
            'price': float(latest['close']),
            'vwap': float(latest['Z_prime']),
            'deviation': float(latest['E']),
            'volume_ratio': float(latest['Volume_Ratio']),
            'signal': latest['Signal'],
            'phase': float(latest.get('Phase_Rad', 0)),
            'trend': latest.get('Trend_Consensus', 'unknown'),
            'regime': latest.get('Market_Regime', 'unknown'),
            
            # Historical context
            'price_change_24h': float((latest['close'] / df.iloc[-24]['close'] - 1) * 100) if len(df) >= 24 else 0,
            'high_24h': float(df.tail(24)['high'].max()) if len(df) >= 24 else float(latest['high']),
            'low_24h': float(df.tail(24)['low'].min()) if len(df) >= 24 else float(latest['low']),
            
            # Signal statistics
            'buy_signals_recent': int((df.tail(100)['Signal'] == 'BUY').sum()),
            'sell_signals_recent': int((df.tail(100)['Signal'] == 'SELL').sum()),
        }
    
    def _create_analysis_prompt(self, symbol: str, metrics: Dict) -> str:
        """Create structured prompt for LLM"""
        prompt = f"""Analyze this cryptocurrency trading data and provide professional insights:

Symbol: {symbol}
Current Price: ${metrics['price']:.4f}
VWAP (Equilibrium): ${metrics['vwap']:.4f}
Deviation: {metrics['deviation']:.2f}σ
Signal: {metrics['signal']}
Volume Ratio: {metrics['volume_ratio']:.1f}%
Trend: {metrics['trend']}
Market Regime: {metrics['regime']}
Phase Position: {metrics['phase']:.2f}°
24h Change: {metrics['price_change_24h']:+.2f}%
24h High: ${metrics['high_24h']:.4f}
24h Low: ${metrics['low_24h']:.4f}

Provide a concise professional analysis (2-3 sentences) covering:
1. Current market position and deviation interpretation
2. Trend and regime assessment
3. Trading recommendation with risk considerations"""
        
        return prompt
    
    def _fallback_analysis(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Rule-based analysis when LLM unavailable"""
        latest = df.iloc[-1]
        metrics = self._extract_metrics(df, latest)
        
        # Rule-based interpretation
        analysis_parts = []
        
        # Deviation analysis
        dev = metrics['deviation']
        if dev < -2.0:
            analysis_parts.append(f"Price is {abs(dev):.1f}σ below equilibrium - strong undervaluation. Mean reversion likely.")
        elif dev > 2.0:
            analysis_parts.append(f"Price is {dev:.1f}σ above equilibrium - strong overvaluation. Correction likely.")
        else:
            analysis_parts.append(f"Price near equilibrium ({dev:.1f}σ) - range-bound trading expected.")
        
        # Volume analysis
        vol = metrics['volume_ratio']
        if vol > 150:
            analysis_parts.append(f"Exceptional volume ({vol:.0f}%) confirms strong conviction.")
        elif vol > 100:
            analysis_parts.append(f"Above-average volume ({vol:.0f}%) supports signal reliability.")
        else:
            analysis_parts.append(f"Below-average volume ({vol:.0f}%) - wait for confirmation.")
        
        # Trend alignment
        trend = metrics['trend'].lower() if isinstance(metrics['trend'], str) else 'unknown'
        signal = metrics['signal'].upper() if isinstance(metrics['signal'], str) else 'HOLD'
        if 'uptrend' in trend and signal == 'BUY':
            analysis_parts.append("Signal aligns with uptrend - high probability setup.")
        elif 'downtrend' in trend and signal == 'SELL':
            analysis_parts.append("Signal aligns with downtrend - high probability setup.")
        elif 'ranging' in trend or 'sideways' in trend:
            analysis_parts.append("Ranging market - mean reversion strategy optimal.")
        
        # Risk assessment
        regime = metrics['regime'].lower() if isinstance(metrics['regime'], str) else 'unknown'
        if 'volatile' in regime:
            analysis_parts.append("⚠️  High volatility - reduce position size by 50%.")
        elif 'trending' in regime:
            analysis_parts.append("Trending market - consider trend-following stops.")
        
        # Recommendation
        if signal == 'BUY' and vol > 100:
            analysis_parts.append(f"✅ ENTRY: Consider long position near ${metrics['price']:.4f}")
            analysis_parts.append(f"🎯 TARGET: ${metrics['vwap']:.4f} (equilibrium)")
            analysis_parts.append(f"🛑 STOP: ${metrics['low_24h']:.4f} (24h low)")
        elif signal == 'SELL' and vol > 100:
            analysis_parts.append(f"✅ EXIT: Consider closing longs or shorting near ${metrics['price']:.4f}")
            analysis_parts.append(f"🎯 TARGET: ${metrics['vwap']:.4f} (equilibrium)")
            analysis_parts.append(f"🛑 STOP: ${metrics['high_24h']:.4f} (24h high)")
        else:
            analysis_parts.append(f"⏸️  HOLD: Wait for volume confirmation (need >100%, currently {vol:.0f}%)")
        
        analysis_text = "\n\n".join(analysis_parts)
        
        return {
            'symbol': symbol,
            'analysis': analysis_text,
            'metrics': metrics,
            'model': 'rule-based',
            'method': 'fallback'
        }
    
    def generate_report(self, analysis: Dict) -> str:
        """Format analysis as readable report"""
        report = f"""
{'='*80}
PROFESSIONAL MARKET ANALYSIS - {analysis['symbol']}
{'='*80}

CURRENT METRICS:
  Price:           ${analysis['metrics']['price']:.4f}
  VWAP:            ${analysis['metrics']['vwap']:.4f}
  Deviation:       {analysis['metrics']['deviation']:.2f}σ
  Signal:          {analysis['metrics']['signal']}
  Volume:          {analysis['metrics']['volume_ratio']:.1f}%
  Trend:           {analysis['metrics']['trend']}
  Regime:          {analysis['metrics']['regime']}
  24h Change:      {analysis['metrics']['price_change_24h']:+.2f}%

ANALYSIS:
{analysis['analysis']}

{'='*80}
Generated by: {analysis['model']} ({analysis['method']})
{'='*80}
"""
        return report


def analyze_with_llm(df: pd.DataFrame, symbol: str, model_name: Optional[str] = None) -> Dict:
    """
    Convenience function for LLM analysis
    
    Args:
        df: DataFrame with market data and indicators
        symbol: Trading pair symbol
        model_name: Optional model override
        
    Returns:
        Analysis dictionary
    """
    analyzer = LLMAnalyzer(model_name=model_name) if model_name else LLMAnalyzer()
    return analyzer.analyze_market_data(df, symbol)


if __name__ == "__main__":
    # Test with sample data
    print("Testing LLM Analyzer...")
    
    # Create sample data
    import numpy as np
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
    sample_df = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 101,
        'low': np.random.randn(100).cumsum() + 99,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100),
    }, index=dates)
    
    # Add required columns
    sample_df['Z_prime'] = sample_df['close'].rolling(20).mean()
    sample_df['E'] = (sample_df['close'] - sample_df['Z_prime']) / sample_df['close'].std()
    sample_df['Volume_Ratio'] = 100
    sample_df['Signal'] = 'BUY'
    sample_df['Phase_Rad'] = np.random.rand(100) * 2 * np.pi
    sample_df['Trend_Consensus'] = 'Uptrend'
    sample_df['Market_Regime'] = 'Trending'
    sample_df['Confidence'] = 'High'
    
    # Test analysis
    analyzer = LLMAnalyzer()
    result = analyzer.analyze_market_data(sample_df, 'BTC/USD')
    print(analyzer.generate_report(result))
