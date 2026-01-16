"""
Hugging Face LLM Analyzer for Quant Oracle
Uses local Hugging Face models for professional market analysis (no API calls)
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import warnings
warnings.filterwarnings('ignore')

# Try to import transformers
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  transformers not installed. Install with: pip install transformers torch")


class HuggingFaceLLMAnalyzer:
    """Professional analysis using local Hugging Face models"""
    
    def __init__(self, model_name: str = "Qwen/Qwen2.5-3B-Instruct"):
        """
        Initialize HuggingFace LLM analyzer with local model
        
        Args:
            model_name: Hugging Face model identifier
                       Default: Qwen/Qwen2.5-3B-Instruct (3B params, efficient)
                       Alternatives: 
                       - "Qwen/Qwen3-0.6B" (smallest, fastest)
                       - "Qwen/Qwen2.5-1.5B-Instruct" (small, balanced)
                       - "meta-llama/Llama-3.1-8B-Instruct" (larger, more capable)
        """
        self.model_name = model_name
        self.initialized = False
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if not TRANSFORMERS_AVAILABLE:
            print("⚠️  Transformers library not available. Using rule-based analysis.")
            return
        
        # Initialize model (lazy loading)
        try:
            print(f"🤖 Loading {model_name} model...")
            print(f"   Device: {self.device}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            self.initialized = True
            print(f"✅ Model loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"⚠️  Failed to load model: {e}")
            print("   Falling back to rule-based analysis")
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
        
        # Extract metrics
        latest = df.iloc[-1]
        metrics = self._extract_metrics(df, latest)
        
        # Create prompt
        prompt = self._create_analysis_prompt(symbol, metrics)
        
        # Generate analysis using HuggingFace model
        try:
            analysis_text = self._generate_with_model(prompt)
            
            return {
                'symbol': symbol,
                'analysis': analysis_text,
                'metrics': metrics,
                'model': self.model_name,
                'method': 'huggingface-local'
            }
        except Exception as e:
            print(f"⚠️  LLM generation failed: {e}. Using rule-based analysis.")
            return self._fallback_analysis(df, symbol)
    
    def _generate_with_model(self, prompt: str, max_new_tokens: int = 256) -> str:
        """Generate text using the loaded model"""
        
        # Format prompt for chat models
        messages = [
            {"role": "system", "content": "You are a professional quantitative analyst specializing in cryptocurrency trading. Provide concise, actionable market insights based on technical analysis data."},
            {"role": "user", "content": prompt}
        ]
        
        # Tokenize
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)
        
        # Generate
        with torch.no_grad():
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        generated_ids = [
            output_ids[len(input_ids):] 
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return response.strip()
    
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
24h Change: {metrics['price_change_24h']:+.2f}%

Provide a concise professional analysis (2-3 sentences) covering:
1. Current market position and deviation interpretation
2. Signal strength and volume confirmation
3. Actionable recommendation with risk assessment"""
        
        return prompt
    
    def _fallback_analysis(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Rule-based analysis when LLM unavailable"""
        latest = df.iloc[-1]
        metrics = self._extract_metrics(df, latest)
        
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
QUANT ORACLE ANALYSIS: {analysis['symbol']}
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


def analyze_with_hf_llm(df: pd.DataFrame, symbol: str, model_name: Optional[str] = None) -> Dict:
    """
    Convenience function for HuggingFace LLM analysis
    
    Args:
        df: DataFrame with market data and indicators
        symbol: Trading pair symbol
        model_name: Optional model override
        
    Returns:
        Analysis dictionary
    """
    analyzer = HuggingFaceLLMAnalyzer(model_name) if model_name else HuggingFaceLLMAnalyzer()
    return analyzer.analyze_market_data(df, symbol)


if __name__ == "__main__":
    # Test with sample data
    print("Testing HuggingFace LLM Analyzer...")
    
    # Create sample data
    import numpy as np
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
    sample_df = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 101,
        'low': np.random.randn(100).cumsum() + 99,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100),
        'Z_prime': np.random.randn(100).cumsum() + 100,
        'E': np.random.randn(100) * 2,
        'Volume_Ratio': np.random.uniform(0.5, 1.5, 100),
        'Signal': np.random.choice(['BUY', 'SELL', 'HOLD'], 100),
        'Phase_Rad': np.random.uniform(0, 2*np.pi, 100),
        'Trend_Consensus': np.random.choice(['Uptrend', 'Downtrend', 'Ranging'], 100),
        'Market_Regime': np.random.choice(['Trending', 'Ranging', 'Volatile'], 100),
    }, index=dates)
    
    # Test analyzer
    analyzer = HuggingFaceLLMAnalyzer()
    analysis = analyzer.analyze_market_data(sample_df, 'BTC/USD')
    
    print("\n" + analyzer.generate_report(analysis))
