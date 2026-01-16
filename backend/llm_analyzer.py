"""
LLM-based Professional Analysis Engine
Uses local Transformers model for cost-effective analysis
"""

import json
from typing import Dict, List, Optional
import pandas as pd

# Transformers integration (optional - graceful degradation)
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  Transformers not available. Install with: pip install transformers torch")


class LLMAnalyzer:
    """Professional analysis using local LLM"""
    
    def __init__(self, model_name: str = "microsoft/Phi-3-mini-4k-instruct"):
        """
        Initialize LLM analyzer
        
        Args:
            model_name: HuggingFace model identifier
                       Default: Phi-3-mini (3.8B params, runs on CPU/GPU)
                       Alternatives: 
                       - "microsoft/phi-2" (2.7B, faster)
                       - "TinyLlama/TinyLlama-1.1B-Chat-v1.0" (1.1B, very fast)
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.initialized = False
        
        if not TRANSFORMERS_AVAILABLE:
            print("❌ Transformers library not available")
            return
            
        self._initialize_model()
    
    def _initialize_model(self):
        """Load model and tokenizer"""
        try:
            print(f"🔄 Loading {self.model_name}...")
            
            # Use CPU by default (GPU if available)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None
            )
            
            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
            
            self.initialized = True
            print(f"✅ Model loaded on {device}")
            
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            self.initialized = False
    
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
        
        # Generate analysis
        try:
            response = self.pipeline(prompt)[0]['generated_text']
            # Extract only the generated part (after prompt)
            analysis_text = response[len(prompt):].strip()
            
            return {
                'symbol': symbol,
                'analysis': analysis_text,
                'metrics': metrics,
                'model': self.model_name,
                'method': 'llm'
            }
        except Exception as e:
            print(f"❌ LLM generation failed: {e}")
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
        prompt = f"""You are a professional quantitative analyst. Analyze this trading data and provide actionable insights.

Symbol: {symbol}
Current Price: ${metrics['price']:.4f}
VWAP (Equilibrium): ${metrics['vwap']:.4f}
Deviation: {metrics['deviation']:.2f}σ
Signal: {metrics['signal']}
Volume Ratio: {metrics['volume_ratio']:.1f}%
Trend: {metrics['trend']}
Market Regime: {metrics['regime']}
24h Change: {metrics['price_change_24h']:+.2f}%

Analysis Guidelines:
1. Interpret the deviation (σ) - extreme values indicate mean reversion opportunities
2. Assess signal quality based on volume and trend alignment
3. Identify key support/resistance levels
4. Provide risk assessment and position sizing guidance
5. Give clear entry/exit recommendations

Professional Analysis:"""
        
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
