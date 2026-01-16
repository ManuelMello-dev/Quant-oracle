"""
Advanced LLM Analyzer for Quant Oracle
Provides highly contextual, personalized, actionable trading recommendations

Features:
- Position tracking and trade history
- Staged entry plans with specific quantities and prices
- Contextual analysis ("You've been waiting for...")
- Concrete action plans with stop loss, alerts, and targets
- Position comparison (original vs new trade)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import json
import os

# Import LLM narrative generator
try:
    from llm_narrative_generator import LLMNarrativeGenerator
    LLM_NARRATIVE_AVAILABLE = True
except ImportError:
    LLM_NARRATIVE_AVAILABLE = False


class TradeHistory:
    """Manages user's trade history and positions"""
    
    def __init__(self, history_file: str = "/tmp/trade_history.json"):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self) -> Dict:
        """Load trade history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_history(self):
        """Save trade history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save trade history: {e}")
    
    def add_trade(self, symbol: str, entry: float, exit: Optional[float] = None, 
                  quantity: float = 0, profit_pct: Optional[float] = None):
        """Add a trade to history"""
        if symbol not in self.history:
            self.history[symbol] = []
        
        trade = {
            'entry': entry,
            'exit': exit,
            'quantity': quantity,
            'profit_pct': profit_pct,
            'timestamp': datetime.now().isoformat()
        }
        self.history[symbol].append(trade)
        self._save_history()
    
    def get_last_trade(self, symbol: str) -> Optional[Dict]:
        """Get the most recent trade for a symbol"""
        if symbol in self.history and len(self.history[symbol]) > 0:
            return self.history[symbol][-1]
        return None
    
    def get_all_trades(self, symbol: str) -> List[Dict]:
        """Get all trades for a symbol"""
        return self.history.get(symbol, [])


class AdvancedLLMAnalyzer:
    """Advanced LLM analyzer with contextual, actionable recommendations"""
    
    def __init__(self, use_local_llm: bool = True):
        self.use_local_llm = use_local_llm
        self.trade_history = TradeHistory()
        
        # Try to initialize local LLM
        if use_local_llm:
            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM
                import torch
                
                model_name = "Qwen/Qwen2.5-3B-Instruct"
                print(f"Loading local LLM: {model_name}...")
                
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None
                )
                self.initialized = True
                print("✅ Local LLM initialized successfully")
            except Exception as e:
                print(f"⚠️  Could not initialize local LLM: {e}")
                self.initialized = False
        else:
            self.initialized = False
    
    def generate_actionable_analysis(
        self,
        df: pd.DataFrame,
        symbol: str,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate highly contextual, actionable trading analysis
        
        Args:
            df: DataFrame with market data and indicators
            symbol: Trading symbol
            user_context: Optional context (previous trades, questions, etc.)
            
        Returns:
            Comprehensive analysis with action plan
        """
        if df is None or len(df) == 0:
            return {'error': 'No data available'}
        
        latest = df.iloc[-1]
        
        # Extract key metrics
        current_price = float(latest['close'])
        Z_prime = float(latest['Z_prime']) if not pd.isna(latest['Z_prime']) else current_price
        sigma = float(latest['Sigma']) if not pd.isna(latest['Sigma']) else 0
        E = float(latest['E']) if not pd.isna(latest['E']) else 0
        volume_ratio = float(latest['Volume_Ratio']) if 'Volume_Ratio' in latest else 100
        signal = latest['Signal']
        
        # Calculate entry zones
        entry_aggressive = Z_prime - (1.0 * sigma) if E < 0 else Z_prime + (1.0 * sigma)
        entry_standard = Z_prime - (2.0 * sigma) if E < 0 else Z_prime + (2.0 * sigma)
        entry_conservative = Z_prime - (2.5 * sigma) if E < 0 else Z_prime + (2.5 * sigma)
        stop_loss = Z_prime - (3.0 * sigma) if E < 0 else Z_prime + (3.0 * sigma)
        
        # Targets
        target_primary = Z_prime  # Equilibrium
        target_secondary = Z_prime + (1.0 * sigma) if E < 0 else Z_prime - (1.0 * sigma)
        target_stretch = Z_prime + (2.0 * sigma) if E < 0 else Z_prime - (2.0 * sigma)
        
        # Check conditions
        deviation_signal = abs(E) >= 2.0
        volume_confirmed = volume_ratio > 100
        
        # Timing signal
        timing_signal = False
        if 'T_reversal' in latest and 'Dominant_Period' in latest:
            T_reversal = latest['T_reversal']
            Dominant_Period = latest['Dominant_Period']
            if not pd.isna(T_reversal) and not pd.isna(Dominant_Period) and Dominant_Period > 0:
                timing_signal = T_reversal < (Dominant_Period * 0.10)
        
        # Get trade history
        last_trade = self.trade_history.get_last_trade(symbol)
        
        # Build analysis
        analysis = self._build_contextual_analysis(
            symbol=symbol,
            current_price=current_price,
            Z_prime=Z_prime,
            sigma=sigma,
            E=E,
            volume_ratio=volume_ratio,
            signal=signal,
            deviation_signal=deviation_signal,
            volume_confirmed=volume_confirmed,
            timing_signal=timing_signal,
            entry_aggressive=entry_aggressive,
            entry_standard=entry_standard,
            entry_conservative=entry_conservative,
            stop_loss=stop_loss,
            target_primary=target_primary,
            target_secondary=target_secondary,
            target_stretch=target_stretch,
            last_trade=last_trade,
            user_context=user_context
        )
        
        return analysis
    
    def _build_contextual_analysis(
        self,
        symbol: str,
        current_price: float,
        Z_prime: float,
        sigma: float,
        E: float,
        volume_ratio: float,
        signal: str,
        deviation_signal: bool,
        volume_confirmed: bool,
        timing_signal: bool,
        entry_aggressive: float,
        entry_standard: float,
        entry_conservative: float,
        stop_loss: float,
        target_primary: float,
        target_secondary: float,
        target_stretch: float,
        last_trade: Optional[Dict],
        user_context: Optional[Dict]
    ) -> Dict:
        """Build comprehensive contextual analysis"""
        
        # Determine position type
        position_type = "LONG" if E < 0 else "SHORT"
        is_entry_zone = abs(E) >= 2.0
        
        # Calculate potential profits
        if position_type == "LONG":
            profit_to_primary = ((target_primary - current_price) / current_price) * 100
            profit_to_secondary = ((target_secondary - current_price) / current_price) * 100
            profit_to_stretch = ((target_stretch - current_price) / current_price) * 100
            risk_pct = ((current_price - stop_loss) / current_price) * 100
        else:
            profit_to_primary = ((current_price - target_primary) / current_price) * 100
            profit_to_secondary = ((current_price - target_secondary) / current_price) * 100
            profit_to_stretch = ((current_price - target_stretch) / current_price) * 100
            risk_pct = ((stop_loss - current_price) / current_price) * 100
        
        # Build conditions met list
        conditions_met = []
        if deviation_signal:
            conditions_met.append(f"✅ Price to drop to -2σ → ACHIEVED ({E:.2f}σ)")
        if volume_confirmed:
            conditions_met.append(f"✅ Volume to return → ACHIEVED ({volume_ratio:.1f}%)")
        if timing_signal:
            conditions_met.append(f"✅ Phase alignment → ACHIEVED")
        else:
            conditions_met.append(f"⏳ Phase alignment → PENDING")
        
        # Confidence assessment
        confidence_factors = sum([deviation_signal, volume_confirmed, timing_signal])
        if confidence_factors == 3:
            confidence = "HIGH"
            confidence_desc = "All factors aligned. Identity stable. High conviction signal."
        elif confidence_factors == 2:
            confidence = "MEDIUM"
            confidence_desc = "Partial alignment. Identity forming. Moderate conviction."
        else:
            confidence = "LOW"
            confidence_desc = "Minimal alignment. Identity diffuse. Low conviction."
        
        # Build action plan if entry zone
        action_plan = None
        if is_entry_zone and (deviation_signal or volume_confirmed):
            # Calculate position sizing (example: $100 budget)
            budget = 100  # Default budget
            qty_50pct = (budget * 0.5) / current_price
            qty_25pct = (budget * 0.25) / current_price
            cost_50pct = budget * 0.5
            cost_25pct = budget * 0.25
            total_qty = qty_50pct + qty_25pct + qty_25pct
            avg_entry = ((current_price * qty_50pct) + (entry_aggressive * qty_25pct) + (entry_conservative * qty_25pct)) / total_qty if total_qty > 0 else current_price
            
            action_plan = {
                'title': '📋 Immediate Action Plan',
                'recommendation': f"{'BUY' if position_type == 'LONG' else 'SELL'} NOW - Entry Zone Reached",
                'stages': [
                    {
                        'stage': 1,
                        'action': f"Enter 50% Position NOW",
                        'instruction': f"{'BUY' if position_type == 'LONG' else 'SELL'}: {qty_50pct:.0f} {symbol.split('/')[0]} @ market (~${current_price:.4f})",
                        'cost': f"${cost_50pct:.2f}",
                        'reason': f"{E:.2f}σ + volume spike + {'high' if confidence == 'HIGH' else 'medium'} confidence"
                    },
                    {
                        'stage': 2,
                        'action': f"Add 25% on Bounce Confirmation",
                        'instruction': f"IF price bounces to ${entry_aggressive:.4f}:",
                        'details': f"{'BUY' if position_type == 'LONG' else 'SELL'}: {qty_25pct:.0f} {symbol.split('/')[0]} @ ${entry_aggressive:.4f}",
                        'cost': f"${cost_25pct:.2f}"
                    },
                    {
                        'stage': 3,
                        'action': f"Add Final 25% on Momentum",
                        'instruction': f"IF price breaks ${entry_conservative:.4f}:",
                        'details': f"{'BUY' if position_type == 'LONG' else 'SELL'}: {qty_25pct:.0f} {symbol.split('/')[0]} @ ${entry_conservative:.4f}",
                        'cost': f"${cost_25pct:.2f}"
                    }
                ],
                'summary': {
                    'total_position': f"{total_qty:.0f} {symbol.split('/')[0]}",
                    'average_entry': f"~${avg_entry:.4f}",
                    'total_cost': f"${budget:.2f}"
                },
                'stop_loss': {
                    'price': f"${stop_loss:.4f}",
                    'risk': f"{risk_pct:.1f}%",
                    'reason': "Protects against breakdown below -3σ"
                },
                'alerts': [
                    f"Alert @ ${entry_aggressive:.4f} → Add 25% position",
                    f"Alert @ ${entry_conservative:.4f} → Add final 25% position",
                    f"Alert @ ${target_primary:.4f} → Consider exit (equilibrium)",
                    f"Alert @ ${target_secondary:.4f} → Exit target (your previous exit level)" if last_trade and last_trade.get('exit') else f"Alert @ ${target_secondary:.4f} → Exit target (+{profit_to_secondary:.1f}%)"
                ],
                'targets': {
                    'primary': f"${target_primary:.4f} (equilibrium, +{profit_to_primary:.1f}%)",
                    'secondary': f"${target_secondary:.4f} (previous exit level, +{profit_to_secondary:.1f}%)" if last_trade and last_trade.get('exit') else f"${target_secondary:.4f} (+{profit_to_secondary:.1f}%)",
                    'stretch': f"${target_stretch:.4f} (previous high, +{profit_to_stretch:.1f}%)"
                }
            }
        
        # Build position comparison if there's history
        position_comparison = None
        if last_trade and last_trade.get('exit'):
            original_entry = last_trade['entry']
            original_exit = last_trade['exit']
            original_profit = ((original_exit - original_entry) / original_entry) * 100
            
            new_potential_primary = profit_to_primary
            new_potential_secondary = profit_to_secondary
            
            combined_total = original_profit + new_potential_secondary
            
            position_comparison = {
                'title': '💰 Your Position Comparison',
                'original_trade': {
                    'entry': f"${original_entry:.4f}",
                    'exit': f"${original_exit:.4f}",
                    'profit': f"+{original_profit:.1f}%"
                },
                'new_trade_if_enter_now': {
                    'entry': f"${current_price:.4f}",
                    'target': f"${target_primary:.4f} (equilibrium)",
                    'potential': f"+{new_potential_primary:.1f}%"
                },
                'if_reaches_exit_level': {
                    'entry': f"${current_price:.4f}",
                    'target': f"${target_secondary:.4f} (previous exit)",
                    'potential': f"+{new_potential_secondary:.1f}%"
                },
                'combined_from_original_entry': {
                    'original': f"+{original_profit:.1f}%",
                    'new_trade': f"+{new_potential_secondary:.1f}%",
                    'total': f"+{combined_total:.1f}% from original ${original_entry:.4f}"
                }
            }
        
        # Build "why this is your entry" section
        why_entry = None
        if is_entry_zone:
            what_happened = []
            if last_trade and last_trade.get('exit'):
                price_change = ((current_price - last_trade['exit']) / last_trade['exit']) * 100
                what_happened.append(f"Price dropped from ${last_trade['exit']:.4f} (your exit) to ${current_price:.4f}")
                what_happened.append(f"{price_change:.1f}% decline")
            
            what_happened.extend([
                f"Hit the -2σ zone you were targeting",
                f"Volume spiked to {volume_ratio:.1f}% (strong {'buying' if position_type == 'LONG' else 'selling'} interest)",
                f"Oracle confidence: {confidence}"
            ])
            
            why_entry = {
                'title': '💡 ANALYSIS - Why This Is Your Entry',
                'youve_been_waiting_for': conditions_met,
                'what_happened': what_happened
            }
        
        # Build oracle status
        oracle_status = {
            'title': '🎯 BOTTOM LINE',
            'oracle_status': {
                'deviation': f"{E:.2f}σ {'✅' if abs(E) >= 2.0 else '❌'} ({'BELOW' if E < 0 else 'ABOVE'} -2σ threshold)",
                'volume': f"{volume_ratio:.1f}% {'✅' if volume_confirmed else '❌'} ({'ABOVE' if volume_confirmed else 'BELOW'} average)",
                'confidence': f"{confidence} {'✅' if confidence == 'HIGH' else '⚠️'}",
                'signal': f"{signal} (but entry conditions {'met' if is_entry_zone else 'NOT met'})"
            },
            'your_status': self._build_user_status(last_trade, current_price, target_secondary, is_entry_zone),
            'recommendation': self._build_recommendation(is_entry_zone, deviation_signal, volume_confirmed, confidence, position_type, current_price),
            'final_message': self._build_final_message(is_entry_zone, deviation_signal, volume_confirmed, last_trade)
        }
        
        # Generate AI narrative if available
        ai_narrative = None
        if LLM_NARRATIVE_AVAILABLE:
            try:
                generator = LLMNarrativeGenerator()
                ai_narrative = generator.generate_analysis_narrative(
                    {
                        'raw_metrics': {
                            'current_price': current_price,
                            'equilibrium': Z_prime,
                            'deviation': E,
                            'volume_ratio': volume_ratio,
                            'signal': signal,
                            'confidence': confidence
                        },
                        'oracle_status': oracle_status,
                        'action_plan': action_plan,
                        'why_entry': why_entry,
                        'position_comparison': position_comparison
                    },
                    symbol
                )
            except Exception as e:
                print(f"⚠️  AI narrative generation failed: {e}")
                ai_narrative = None
        
        # Assemble complete analysis
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'ai_narrative': ai_narrative,
            'oracle_status': oracle_status,
            'why_entry': why_entry,
            'position_comparison': position_comparison,
            'action_plan': action_plan,
            'raw_metrics': {
                'current_price': current_price,
                'equilibrium': Z_prime,
                'deviation': E,
                'volume_ratio': volume_ratio,
                'confidence': confidence,
                'signal': signal
            }
        }
    
    def _build_user_status(self, last_trade: Optional[Dict], current_price: float, target: float, is_entry_zone: bool) -> Dict:
        """Build user status section"""
        status = {}
        
        if last_trade and last_trade.get('exit'):
            profit = ((last_trade['exit'] - last_trade['entry']) / last_trade['entry']) * 100
            status['exited'] = f"${last_trade['exit']:.4f} (+{profit:.1f}% profit) ✅"
            status['waiting'] = f"For -2σ entry {'✅' if is_entry_zone else '⏳'}"
        
        if is_entry_zone:
            status['now'] = "Entry zone reached 🎯"
        
        return status
    
    def _build_recommendation(self, is_entry_zone: bool, deviation_signal: bool, volume_confirmed: bool, confidence: str, position_type: str, current_price: float) -> str:
        """Build recommendation text"""
        if is_entry_zone and (deviation_signal or volume_confirmed):
            return f"ENTER 50% POSITION NOW @ ${current_price:.4f}"
        elif is_entry_zone:
            return f"WATCH CLOSELY - Entry zone reached but wait for volume confirmation"
        else:
            return f"HOLD - Wait for -2σ entry zone"
    
    def _build_final_message(self, is_entry_zone: bool, deviation_signal: bool, volume_confirmed: bool, last_trade: Optional[Dict]) -> str:
        """Build final motivational message"""
        if is_entry_zone and deviation_signal and volume_confirmed:
            return "This is the setup you've been patiently waiting for. The oracle has given you the signal. Volume confirms it. Don't overthink it. 🚀\n\nYour patience has been rewarded. Time to execute!"
        elif is_entry_zone:
            return "Entry zone reached but volume is weak. The oracle says wait for confirmation."
        else:
            return "Not yet. The oracle will alert you when conditions align."
    
    def format_for_display(self, analysis: Dict) -> str:
        """Format analysis for beautiful terminal/app display"""
        if 'error' in analysis:
            return f"❌ ERROR: {analysis['error']}"
        
        output = []
        output.append("\n" + "="*80)
        output.append(f"🔮 ORACLE ANALYSIS - {analysis['symbol']}")
        output.append("="*80 + "\n")
        
        # AI Narrative section
        if analysis.get('ai_narrative'):
            output.append("🤖 AI ANALYSIS\n")
            output.append(analysis['ai_narrative'])
            output.append("\n" + "-"*80 + "\n")
        
        # Why Entry section
        if analysis.get('why_entry'):
            why = analysis['why_entry']
            output.append(f"{why['title']}")
            output.append("\nYou've been waiting for:")
            for condition in why['youve_been_waiting_for']:
                output.append(f"  {condition}")
            output.append("\nWhat happened:")
            for event in why['what_happened']:
                output.append(f"  • {event}")
            output.append("")
        
        # Action Plan
        if analysis.get('action_plan'):
            plan = analysis['action_plan']
            output.append(f"\n{plan['title']}")
            output.append(f"\n{plan['recommendation']}\n")
            
            for stage in plan['stages']:
                output.append(f"STAGE {stage['stage']}: {stage['action']}")
                output.append(f"  {stage['instruction']}")
                if 'details' in stage:
                    output.append(f"  {stage['details']}")
                output.append(f"  Cost: {stage['cost']}")
                if 'reason' in stage:
                    output.append(f"  Reason: {stage['reason']}")
                output.append("")
            
            output.append(f"Total Position: {plan['summary']['total_position']}")
            output.append(f"Average Entry: {plan['summary']['average_entry']}")
            output.append("")
            
            output.append("Targets:")
            for key, value in plan['targets'].items():
                output.append(f"  • {key.capitalize()}: {value}")
            output.append("")
            
            output.append(f"Stop Loss: {plan['stop_loss']['price']} ({plan['stop_loss']['risk']} risk)")
            output.append(f"  → {plan['stop_loss']['reason']}")
            output.append("")
        
        # Position Comparison
        if analysis.get('position_comparison'):
            comp = analysis['position_comparison']
            output.append(f"\n{comp['title']}")
            output.append("\nOriginal Trade:")
            for key, value in comp['original_trade'].items():
                output.append(f"  • {key.capitalize()}: {value}")
            output.append("\nNew Trade (if you enter now):")
            for key, value in comp['new_trade_if_enter_now'].items():
                output.append(f"  • {key.capitalize()}: {value}")
            output.append("\nCombined from original entry:")
            output.append(f"  • Total: {comp['combined_from_original_entry']['total']}")
            output.append("")
        
        # Oracle Status
        if analysis.get('oracle_status'):
            status = analysis['oracle_status']
            output.append(f"\n{status['title']}")
            output.append("\nOracle Status:")
            for key, value in status['oracle_status'].items():
                output.append(f"  • {key.capitalize()}: {value}")
            
            if status.get('your_status'):
                output.append("\nYour Status:")
                for key, value in status['your_status'].items():
                    output.append(f"  • {key.capitalize()}: {value}")
            
            output.append(f"\nRecommendation: {status['recommendation']}")
            output.append(f"\n{status['final_message']}")
        
        output.append("\n" + "="*80)
        return "\n".join(output)


# Convenience function
def analyze_with_advanced_llm(df: pd.DataFrame, symbol: str, user_context: Optional[Dict] = None) -> Dict:
    """
    Convenience function for advanced LLM analysis
    
    Args:
        df: DataFrame with market data
        symbol: Trading symbol
        user_context: Optional user context
        
    Returns:
        Comprehensive analysis dictionary
    """
    analyzer = AdvancedLLMAnalyzer(use_local_llm=True)
    return analyzer.generate_actionable_analysis(df, symbol, user_context)


if __name__ == "__main__":
    # Test with sample data
    print("Testing Advanced LLM Analyzer...")
    
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
    sample_df = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 101,
        'low': np.random.randn(100).cumsum() + 99,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100),
        'Z_prime': np.random.randn(100).cumsum() + 102,
        'Sigma': np.random.uniform(1.0, 3.0, 100),
        'E': np.random.randn(100) * 3,  # Simulate -2σ condition
        'Volume_Ratio': np.random.uniform(80, 150, 100),
        'Signal': ['HOLD'] * 100,
        'T_reversal': np.random.uniform(5, 50, 100),
        'Dominant_Period': np.random.uniform(50, 100, 100),
    }, index=dates)
    
    # Force a BUY signal condition
    sample_df.iloc[-1, sample_df.columns.get_loc('E')] = -2.68
    sample_df.iloc[-1, sample_df.columns.get_loc('Volume_Ratio')] = 118.6
    sample_df.iloc[-1, sample_df.columns.get_loc('Signal')] = 'BUY'
    
    analyzer = AdvancedLLMAnalyzer(use_local_llm=False)
    analysis = analyzer.generate_actionable_analysis(sample_df, "DOGE/USD")
    
    print(analyzer.format_for_display(analysis))
