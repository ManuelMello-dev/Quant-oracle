"""
Entry Point Analysis System for Quant Oracle
Based on Genesis Drift Oracle V3.1

Provides comprehensive entry point analysis including:
- Sigma bands calculation
- Optimal entry zones (Aggressive/Standard/Conservative)
- User entry evaluation
- Risk/Reward calculations
- Stop loss suggestions
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


class EntryPointAnalyzer:
    """Analyzes and suggests optimal entry points based on Genesis Drift framework."""
    
    @staticmethod
    def calculate_sigma_bands(Z_prime: float, sigma: float, num_bands: int = 3) -> Dict[str, float]:
        """
        Calculates price levels at various sigma deviations from equilibrium.
        
        Args:
            Z_prime: Equilibrium price (VWAP)
            sigma: Standard deviation
            num_bands: Number of sigma bands above and below (default: 3)
            
        Returns:
            Dict with price levels for each sigma band
        """
        bands = {}
        for i in range(-num_bands, num_bands + 1):
            if i == 0:
                bands['Z_prime (0σ)'] = Z_prime
            else:
                label = f"{'+' if i > 0 else ''}{i}σ"
                bands[label] = Z_prime + (i * sigma)
        return bands
    
    @staticmethod
    def get_optimal_entry_long(Z_prime: float, sigma: float, sigma_threshold: float = 2.0) -> Dict[str, Dict]:
        """
        Calculates optimal entry prices for LONG positions.
        
        Args:
            Z_prime: Equilibrium price (VWAP)
            sigma: Standard deviation
            sigma_threshold: Threshold for coherent signal (default: 2.0)
            
        Returns:
            Dict with entry zones and their characteristics
        """
        return {
            'Aggressive Entry': {
                'price': Z_prime - (1.0 * sigma),
                'E_at_entry': -1.0,
                'description': 'Early accumulation zone. Higher risk, earlier entry.',
                'risk_level': 'High',
                'potential_reward': 'Moderate'
            },
            'Standard Entry': {
                'price': Z_prime - (sigma_threshold * sigma),
                'E_at_entry': -sigma_threshold,
                'description': f'Coherent long zone. Price at -{sigma_threshold}σ from equilibrium.',
                'risk_level': 'Medium',
                'potential_reward': 'High'
            },
            'Conservative Entry': {
                'price': Z_prime - (2.5 * sigma),
                'E_at_entry': -2.5,
                'description': 'Deep value zone. Lower risk, may not fill.',
                'risk_level': 'Low',
                'potential_reward': 'Very High'
            },
            'Target (Z\')': {
                'price': Z_prime,
                'E_at_entry': 0,
                'description': 'Equilibrium target. Expected return destination.',
                'risk_level': 'N/A',
                'potential_reward': 'N/A'
            }
        }
    
    @staticmethod
    def get_optimal_entry_short(Z_prime: float, sigma: float, sigma_threshold: float = 2.0) -> Dict[str, Dict]:
        """
        Calculates optimal entry prices for SHORT positions.
        
        Args:
            Z_prime: Equilibrium price (VWAP)
            sigma: Standard deviation
            sigma_threshold: Threshold for coherent signal (default: 2.0)
            
        Returns:
            Dict with entry zones and their characteristics
        """
        return {
            'Aggressive Entry': {
                'price': Z_prime + (1.0 * sigma),
                'E_at_entry': 1.0,
                'description': 'Early distribution zone. Higher risk, earlier entry.',
                'risk_level': 'High',
                'potential_reward': 'Moderate'
            },
            'Standard Entry': {
                'price': Z_prime + (sigma_threshold * sigma),
                'E_at_entry': sigma_threshold,
                'description': f'Coherent short zone. Price at +{sigma_threshold}σ from equilibrium.',
                'risk_level': 'Medium',
                'potential_reward': 'High'
            },
            'Conservative Entry': {
                'price': Z_prime + (2.5 * sigma),
                'E_at_entry': 2.5,
                'description': 'Extreme overvaluation zone. Lower risk, may not fill.',
                'risk_level': 'Low',
                'potential_reward': 'Very High'
            },
            'Target (Z\')': {
                'price': Z_prime,
                'E_at_entry': 0,
                'description': 'Equilibrium target. Expected return destination.',
                'risk_level': 'N/A',
                'potential_reward': 'N/A'
            }
        }
    
    @staticmethod
    def evaluate_user_entry(
        user_entry_price: float,
        Z_prime: float,
        sigma: float,
        current_price: float,
        timing_signal: bool,
        sigma_threshold: float = 2.0
    ) -> Dict:
        """
        Evaluates a user-provided entry price against the current market state.
        
        Args:
            user_entry_price: User's actual or proposed entry price
            Z_prime: Equilibrium price (VWAP)
            sigma: Standard deviation
            current_price: Current market price
            timing_signal: Whether phase timing is favorable
            sigma_threshold: Threshold for coherent signal (default: 2.0)
            
        Returns:
            Comprehensive assessment dictionary
        """
        # Calculate E at user's entry price
        E_at_entry = (user_entry_price - Z_prime) / sigma if sigma > 0 else 0
        E_current = (current_price - Z_prime) / sigma if sigma > 0 else 0
        
        # Determine position type based on entry vs equilibrium
        if user_entry_price < Z_prime:
            position_type = "LONG"
            distance_to_target = Z_prime - user_entry_price
            distance_to_target_pct = (distance_to_target / user_entry_price) * 100 if user_entry_price > 0 else 0
        else:
            position_type = "SHORT"
            distance_to_target = user_entry_price - Z_prime
            distance_to_target_pct = (distance_to_target / user_entry_price) * 100 if user_entry_price > 0 else 0
        
        # Assess entry quality
        abs_E = abs(E_at_entry)
        if abs_E >= sigma_threshold:
            if timing_signal:
                entry_quality = "Excellent"
                entry_description = f"Entry at {E_at_entry:.2f}σ with phase alignment. Maximum coherence potential."
            else:
                entry_quality = "Good"
                entry_description = f"Entry at {E_at_entry:.2f}σ. Strong deviation, awaiting phase confirmation."
        elif abs_E >= 1.5:
            entry_quality = "Moderate"
            entry_description = f"Entry at {E_at_entry:.2f}σ. Reasonable deviation from equilibrium."
        elif abs_E >= 1.0:
            entry_quality = "Fair"
            entry_description = f"Entry at {E_at_entry:.2f}σ. Mild deviation. Consider waiting for better entry."
        else:
            entry_quality = "Poor"
            entry_description = f"Entry at {E_at_entry:.2f}σ. Near equilibrium. Low reward potential."
        
        # Risk assessment
        if position_type == "LONG":
            # For longs, risk is if price goes lower
            stop_loss_suggested = Z_prime - (3.0 * sigma)
            risk_pct = ((user_entry_price - stop_loss_suggested) / user_entry_price) * 100 if user_entry_price > 0 else 0
        else:
            # For shorts, risk is if price goes higher
            stop_loss_suggested = Z_prime + (3.0 * sigma)
            risk_pct = ((stop_loss_suggested - user_entry_price) / user_entry_price) * 100 if user_entry_price > 0 else 0
        
        # Risk/Reward ratio
        if risk_pct > 0:
            risk_reward_ratio = distance_to_target_pct / risk_pct
        else:
            risk_reward_ratio = float('inf')
        
        return {
            'User_Entry_Price': user_entry_price,
            'Current_Price': current_price,
            'Equilibrium_Z_prime': Z_prime,
            'Sigma': sigma,
            'E_at_Entry': E_at_entry,
            'E_Current': E_current,
            'Position_Type': position_type,
            'Entry_Quality': entry_quality,
            'Entry_Description': entry_description,
            'Distance_to_Target': distance_to_target,
            'Distance_to_Target_Pct': distance_to_target_pct,
            'Stop_Loss_Suggested': stop_loss_suggested,
            'Risk_Pct': risk_pct,
            'Risk_Reward_Ratio': risk_reward_ratio,
            'Timing_Signal': timing_signal
        }
    
    @staticmethod
    def get_entry_analysis(df: pd.DataFrame, sigma_threshold: float = 2.0) -> Dict:
        """
        Performs comprehensive entry analysis on the latest market data.
        
        Args:
            df: DataFrame with OHLCV + indicators (must have Z_prime, Sigma, E, etc.)
            sigma_threshold: Threshold for coherent signal (default: 2.0)
            
        Returns:
            Complete entry analysis including bands, optimal entries, and current state
        """
        if df is None or len(df) == 0:
            return {'error': 'No data available for entry analysis'}
        
        latest = df.iloc[-1]
        
        # Extract required values
        Z_prime = float(latest['Z_prime']) if 'Z_prime' in latest and not pd.isna(latest['Z_prime']) else None
        sigma = float(latest['Sigma']) if 'Sigma' in latest and not pd.isna(latest['Sigma']) else None
        current_price = float(latest['close'])
        E = float(latest['E']) if 'E' in latest and not pd.isna(latest['E']) else None
        
        if Z_prime is None or sigma is None or sigma == 0:
            return {'error': 'Insufficient data for entry analysis (missing Z_prime or Sigma)'}
        
        # Check timing signal
        timing_signal = False
        if 'T_reversal' in latest and 'Dominant_Period' in latest:
            T_reversal = latest['T_reversal']
            Dominant_Period = latest['Dominant_Period']
            if not pd.isna(T_reversal) and not pd.isna(Dominant_Period) and Dominant_Period > 0:
                reversal_threshold_bars = Dominant_Period * 0.10  # 10% of dominant period
                timing_signal = T_reversal < reversal_threshold_bars
        
        # Calculate sigma bands
        sigma_bands = EntryPointAnalyzer.calculate_sigma_bands(Z_prime, sigma)
        
        # Determine current signal direction
        if E is not None and abs(E) >= sigma_threshold:
            if E < 0:
                signal_direction = "LONG"
                optimal_entries = EntryPointAnalyzer.get_optimal_entry_long(Z_prime, sigma, sigma_threshold)
            else:
                signal_direction = "SHORT"
                optimal_entries = EntryPointAnalyzer.get_optimal_entry_short(Z_prime, sigma, sigma_threshold)
        else:
            signal_direction = "HOLD"
            optimal_entries = {
                'LONG': EntryPointAnalyzer.get_optimal_entry_long(Z_prime, sigma, sigma_threshold),
                'SHORT': EntryPointAnalyzer.get_optimal_entry_short(Z_prime, sigma, sigma_threshold)
            }
        
        return {
            'symbol': latest.get('symbol', 'N/A'),
            'current_price': float(current_price),
            'equilibrium_Z_prime': float(Z_prime),
            'sigma': float(sigma),
            'E_current': float(E) if E is not None else None,
            'signal_direction': str(signal_direction),
            'timing_signal': bool(timing_signal),
            'sigma_bands': {k: float(v) for k, v in sigma_bands.items()},
            'optimal_entries': optimal_entries,
            'timestamp': str(latest.name) if hasattr(latest, 'name') else 'N/A'
        }


def analyze_entry_point(df: pd.DataFrame, user_entry_price: Optional[float] = None, sigma_threshold: float = 2.0) -> Dict:
    """
    Convenience function for entry point analysis.
    
    Args:
        df: DataFrame with market data and indicators
        user_entry_price: Optional user entry price to evaluate
        sigma_threshold: Threshold for coherent signal (default: 2.0)
        
    Returns:
        Entry analysis dictionary
    """
    analyzer = EntryPointAnalyzer()
    analysis = analyzer.get_entry_analysis(df, sigma_threshold)
    
    if user_entry_price is not None and 'error' not in analysis:
        latest = df.iloc[-1]
        Z_prime = analysis['equilibrium_Z_prime']
        sigma = analysis['sigma']
        current_price = analysis['current_price']
        timing_signal = analysis['timing_signal']
        
        user_eval = analyzer.evaluate_user_entry(
            user_entry_price, Z_prime, sigma, current_price, timing_signal, sigma_threshold
        )
        analysis['user_entry_evaluation'] = user_eval
    
    return analysis


if __name__ == "__main__":
    # Test with sample data
    print("Testing Entry Point Analyzer...")
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
    sample_df = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 101,
        'low': np.random.randn(100).cumsum() + 99,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100),
        'Z_prime': np.random.randn(100).cumsum() + 100,
        'Sigma': np.random.uniform(0.5, 2.0, 100),
        'E': np.random.randn(100) * 2,
        'T_reversal': np.random.uniform(5, 50, 100),
        'Dominant_Period': np.random.uniform(50, 100, 100),
    }, index=dates)
    
    # Test entry analysis
    analysis = analyze_entry_point(sample_df, user_entry_price=98.5)
    
    print("\n=== Entry Analysis ===")
    print(f"Current Price: ${analysis['current_price']:.2f}")
    print(f"Equilibrium (Z'): ${analysis['equilibrium_Z_prime']:.2f}")
    print(f"Sigma: ${analysis['sigma']:.2f}")
    print(f"E: {analysis['E_current']:.2f}σ")
    print(f"Signal Direction: {analysis['signal_direction']}")
    print(f"Timing Signal: {analysis['timing_signal']}")
    
    print("\n=== Sigma Bands ===")
    for band, price in analysis['sigma_bands'].items():
        print(f"{band}: ${price:.2f}")
    
    if 'user_entry_evaluation' in analysis:
        print("\n=== User Entry Evaluation ===")
        eval_data = analysis['user_entry_evaluation']
        print(f"Entry Price: ${eval_data['User_Entry_Price']:.2f}")
        print(f"Entry Quality: {eval_data['Entry_Quality']}")
        print(f"Position Type: {eval_data['Position_Type']}")
        print(f"E at Entry: {eval_data['E_at_Entry']:.2f}σ")
        print(f"Distance to Target: {eval_data['Distance_to_Target_Pct']:.2f}%")
        print(f"Stop Loss: ${eval_data['Stop_Loss_Suggested']:.2f}")
        print(f"Risk: {eval_data['Risk_Pct']:.2f}%")
        print(f"Risk/Reward Ratio: {eval_data['Risk_Reward_Ratio']:.2f}")
