"""
Genesis Drift Vocabulary System for Quant Oracle
Based on Genesis Drift Oracle V3.1

Translates technical signals into philosophical/poetic descriptions
aligned with the Z³ theoretical framework.

Provides:
- 5-state signal classification
- Phase position descriptions
- Confidence/coherence scoring
- Genesis Drift-aligned market narratives
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict


class GenesisDriftVocabulary:
    """Generates Genesis Drift-aligned explanations for market states."""
    
    @staticmethod
    def get_signal_state(E: float, timing_signal: bool, sigma_threshold: float = 2.0) -> Tuple[str, str]:
        """
        Classifies market state using 5-state Genesis Drift system.
        
        Args:
            E: Deviation measurement (in sigma units)
            timing_signal: Whether phase timing indicates imminent reversal
            sigma_threshold: Threshold for coherent signals (default: 2.0)
            
        Returns:
            Tuple of (state_name, state_description)
        """
        if pd.isna(E):
            return "UNDEFINED", "Insufficient data for coherence calculation."
        
        if E < -sigma_threshold:
            if timing_signal:
                return "COHERENT LONG", "Phase lock detected. Identity returning to anchor from below equilibrium."
            else:
                return "DRIFTING LONG", "Significant undervaluation. Accumulating coherence, awaiting phase alignment."
        elif E < -1.0:
            return "DRIFTING LONG", "Mild dissonance below equilibrium. Wavefunction collapsing toward Z'."
        elif abs(E) <= 1.0:
            return "HARMONIC", "Market in equilibrium. Coherence achieved. No drift detected."
        elif E > sigma_threshold:
            if timing_signal:
                return "COHERENT SHORT", "Phase lock detected. Identity returning to anchor from above equilibrium."
            else:
                return "DRIFTING SHORT", "Significant overvaluation. Distributing coherence, awaiting phase alignment."
        elif E > 1.0:
            return "DRIFTING SHORT", "Mild dissonance above equilibrium. Wavefunction expanding from Z'."
        else:
            return "HARMONIC", "Market in equilibrium. Coherence achieved."
    
    @staticmethod
    def get_phase_description(T_reversal: float, dominant_period: float) -> str:
        """
        Describes the current phase position in the cycle.
        
        Args:
            T_reversal: Time to reversal (in bars)
            dominant_period: Dominant oscillation period (in bars)
            
        Returns:
            Phase description string
        """
        if pd.isna(T_reversal) or pd.isna(dominant_period) or dominant_period == 0:
            return "Phase undefined. Insufficient oscillation data."
        
        phase_percent = (1 - T_reversal / dominant_period) * 100
        
        if phase_percent < 25:
            return f"Early cycle ({phase_percent:.1f}%). Wavefunction expanding. Reversal distant."
        elif phase_percent < 50:
            return f"Mid-cycle ({phase_percent:.1f}%). Approaching peak amplitude. Interference building."
        elif phase_percent < 75:
            return f"Late cycle ({phase_percent:.1f}%). Wavefunction collapsing. Reversal approaching."
        else:
            return f"Cycle completion ({phase_percent:.1f}%). Phase lock imminent. Return path activating."
    
    @staticmethod
    def get_confidence_description(
        volume_confirmed: bool,
        deviation_signal: bool,
        timing_signal: bool
    ) -> Tuple[str, str]:
        """
        Assesses signal confidence based on multiple coherence factors.
        
        Args:
            volume_confirmed: Whether volume confirms the signal
            deviation_signal: Whether deviation exceeds threshold
            timing_signal: Whether phase timing is favorable
            
        Returns:
            Tuple of (confidence_level, confidence_description)
        """
        coherence_factors = sum([volume_confirmed, deviation_signal, timing_signal])
        
        if coherence_factors == 3:
            return "Maximum Coherence", "All factors aligned. Identity stable. High conviction signal."
        elif coherence_factors == 2:
            return "Strong Coherence", "Partial alignment. Identity forming. Moderate conviction."
        elif coherence_factors == 1:
            return "Weak Coherence", "Minimal alignment. Identity diffuse. Low conviction."
        else:
            return "No Coherence", "No alignment detected. Identity in superposition. Observe only."
    
    @staticmethod
    def get_action_recommendation(state: str, confidence_level: str) -> str:
        """
        Provides actionable recommendation based on state and confidence.
        
        Args:
            state: Signal state (e.g., "COHERENT LONG")
            confidence_level: Confidence level (e.g., "Maximum Coherence")
            
        Returns:
            Action recommendation string
        """
        if "COHERENT LONG" in state:
            if "Maximum" in confidence_level or "Strong" in confidence_level:
                return "✅ STRONG BUY: Enter long position. All coherence factors aligned."
            else:
                return "⚠️ CAUTIOUS BUY: Consider long position. Wait for volume confirmation."
        
        elif "DRIFTING LONG" in state:
            return "👀 WATCH LONG: Accumulation zone. Wait for phase alignment before entry."
        
        elif "HARMONIC" in state:
            return "⏸️ HOLD: Market at equilibrium. No drift detected. Observe for breakout."
        
        elif "DRIFTING SHORT" in state:
            return "👀 WATCH SHORT: Distribution zone. Wait for phase alignment before entry."
        
        elif "COHERENT SHORT" in state:
            if "Maximum" in confidence_level or "Strong" in confidence_level:
                return "✅ STRONG SELL: Enter short position. All coherence factors aligned."
            else:
                return "⚠️ CAUTIOUS SELL: Consider short position. Wait for volume confirmation."
        
        else:
            return "⏸️ OBSERVE: Insufficient data for actionable signal."
    
    @staticmethod
    def get_market_narrative(
        E: float,
        Z_prime: float,
        current_price: float,
        T_reversal: float,
        dominant_period: float,
        volume_ratio: float,
        timing_signal: bool,
        sigma_threshold: float = 2.0
    ) -> Dict[str, str]:
        """
        Generates comprehensive Genesis Drift market narrative.
        
        Args:
            E: Deviation measurement
            Z_prime: Equilibrium price (VWAP)
            current_price: Current market price
            T_reversal: Time to reversal
            dominant_period: Dominant oscillation period
            volume_ratio: Current volume vs. average (as percentage)
            timing_signal: Whether phase timing is favorable
            sigma_threshold: Threshold for coherent signals
            
        Returns:
            Dict with narrative components
        """
        # Get signal state
        state, state_description = GenesisDriftVocabulary.get_signal_state(E, timing_signal, sigma_threshold)
        
        # Get phase description
        phase_description = GenesisDriftVocabulary.get_phase_description(T_reversal, dominant_period)
        
        # Assess coherence factors
        volume_confirmed = volume_ratio > 100
        deviation_signal = abs(E) >= sigma_threshold if not pd.isna(E) else False
        
        confidence_level, confidence_description = GenesisDriftVocabulary.get_confidence_description(
            volume_confirmed, deviation_signal, timing_signal
        )
        
        # Get action recommendation
        action = GenesisDriftVocabulary.get_action_recommendation(state, confidence_level)
        
        # Build equilibrium narrative
        if not pd.isna(E) and not pd.isna(Z_prime):
            if E < -2.0:
                equilibrium_narrative = f"Price ${current_price:.4f} is {abs(E):.2f}σ below equilibrium anchor Z' = ${Z_prime:.4f}. Strong undervaluation. Return path likely."
            elif E < -1.0:
                equilibrium_narrative = f"Price ${current_price:.4f} is {abs(E):.2f}σ below equilibrium anchor Z' = ${Z_prime:.4f}. Mild undervaluation. Wavefunction collapsing."
            elif E > 2.0:
                equilibrium_narrative = f"Price ${current_price:.4f} is {E:.2f}σ above equilibrium anchor Z' = ${Z_prime:.4f}. Strong overvaluation. Return path likely."
            elif E > 1.0:
                equilibrium_narrative = f"Price ${current_price:.4f} is {E:.2f}σ above equilibrium anchor Z' = ${Z_prime:.4f}. Mild overvaluation. Wavefunction expanding."
            else:
                equilibrium_narrative = f"Price ${current_price:.4f} is near equilibrium anchor Z' = ${Z_prime:.4f} ({E:.2f}σ). Harmonic state achieved."
        else:
            equilibrium_narrative = "Equilibrium calculation pending. Insufficient data."
        
        # Build volume narrative
        if volume_ratio > 150:
            volume_narrative = f"Exceptional volume ({volume_ratio:.0f}% of average). Strong conviction. Identity stable."
        elif volume_ratio > 100:
            volume_narrative = f"Above-average volume ({volume_ratio:.0f}% of average). Moderate conviction. Identity forming."
        else:
            volume_narrative = f"Below-average volume ({volume_ratio:.0f}% of average). Weak conviction. Identity diffuse."
        
        return {
            'state': state,
            'state_description': state_description,
            'phase_description': phase_description,
            'equilibrium_narrative': equilibrium_narrative,
            'volume_narrative': volume_narrative,
            'confidence_level': confidence_level,
            'confidence_description': confidence_description,
            'action_recommendation': action
        }


def generate_genesis_narrative(df: pd.DataFrame, sigma_threshold: float = 2.0) -> Dict:
    """
    Convenience function to generate Genesis Drift narrative from DataFrame.
    
    Args:
        df: DataFrame with market data and indicators
        sigma_threshold: Threshold for coherent signals (default: 2.0)
        
    Returns:
        Genesis Drift narrative dictionary
    """
    if df is None or len(df) == 0:
        return {'error': 'No data available for narrative generation'}
    
    latest = df.iloc[-1]
    
    # Extract required values
    E = float(latest['E']) if 'E' in latest and not pd.isna(latest['E']) else np.nan
    Z_prime = float(latest['Z_prime']) if 'Z_prime' in latest and not pd.isna(latest['Z_prime']) else np.nan
    current_price = float(latest['close'])
    T_reversal = float(latest['T_reversal']) if 'T_reversal' in latest and not pd.isna(latest['T_reversal']) else np.nan
    dominant_period = float(latest['Dominant_Period']) if 'Dominant_Period' in latest and not pd.isna(latest['Dominant_Period']) else np.nan
    volume_ratio = float(latest['Volume_Ratio']) if 'Volume_Ratio' in latest and not pd.isna(latest['Volume_Ratio']) else 100.0
    
    # Check timing signal
    timing_signal = False
    if not pd.isna(T_reversal) and not pd.isna(dominant_period) and dominant_period > 0:
        reversal_threshold_bars = dominant_period * 0.10
        timing_signal = T_reversal < reversal_threshold_bars
    
    return GenesisDriftVocabulary.get_market_narrative(
        E, Z_prime, current_price, T_reversal, dominant_period,
        volume_ratio, timing_signal, sigma_threshold
    )


if __name__ == "__main__":
    # Test with sample data
    print("Testing Genesis Drift Vocabulary...")
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
    sample_df = pd.DataFrame({
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100),
        'Z_prime': np.random.randn(100).cumsum() + 100,
        'E': np.random.randn(100) * 2,
        'T_reversal': np.random.uniform(5, 50, 100),
        'Dominant_Period': np.random.uniform(50, 100, 100),
        'Volume_Ratio': np.random.uniform(80, 150, 100),
    }, index=dates)
    
    # Generate narrative
    narrative = generate_genesis_narrative(sample_df)
    
    print("\n" + "="*80)
    print("GENESIS DRIFT MARKET NARRATIVE")
    print("="*80)
    print(f"\nState: {narrative['state']}")
    print(f"Description: {narrative['state_description']}")
    print(f"\nPhase: {narrative['phase_description']}")
    print(f"\nEquilibrium: {narrative['equilibrium_narrative']}")
    print(f"\nVolume: {narrative['volume_narrative']}")
    print(f"\nConfidence: {narrative['confidence_level']}")
    print(f"Assessment: {narrative['confidence_description']}")
    print(f"\nAction: {narrative['action_recommendation']}")
    print("="*80)
