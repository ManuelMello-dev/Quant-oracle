"""
Backtesting module for the Quant Oracle.

Analyzes historical signal performance without executing trades.
Provides metrics on signal accuracy, timing, and market conditions.
"""

import pandas as pd
import numpy as np


def calculate_forward_returns(df, periods=[1, 3, 5, 10, 24]):
    """
    Calculates forward returns for multiple time horizons.
    
    Args:
        df: DataFrame with OHLCV data
        periods: List of forward-looking periods (in bars)
    
    Returns:
        DataFrame with forward return columns added
    """
    for period in periods:
        df[f'Forward_Return_{period}'] = (
            df['close'].shift(-period) / df['close'] - 1
        ) * 100
    
    return df


def analyze_signal_performance(df, signal_col='Signal'):
    """
    Analyzes the performance of generated signals.
    
    Calculates metrics for BUY and SELL signals separately.
    """
    
    results = {
        'total_bars': len(df),
        'valid_bars': df[signal_col].notna().sum(),
        'signals': {}
    }
    
    for signal_type in ['BUY', 'SELL']:
        signal_mask = df[signal_col] == signal_type
        signal_count = signal_mask.sum()
        
        if signal_count == 0:
            results['signals'][signal_type] = {
                'count': 0,
                'percentage': 0.0
            }
            continue
        
        signal_data = df[signal_mask].copy()
        
        metrics = {
            'count': signal_count,
            'percentage': (signal_count / len(df)) * 100,
            'avg_deviation_e': signal_data['E'].mean(),
            'avg_volume_ratio': signal_data['Volume_Ratio'].mean(),
            'high_confidence_pct': (signal_data['Confidence'] == 'High').sum() / signal_count * 100,
            'forward_returns': {}
        }
        
        # Calculate forward return statistics
        for col in df.columns:
            if col.startswith('Forward_Return_'):
                period = col.split('_')[-1]
                returns = signal_data[col].dropna()
                
                if len(returns) > 0:
                    # For BUY signals, positive returns are good
                    # For SELL signals, negative returns are good (price went down)
                    if signal_type == 'SELL':
                        returns = -returns  # Invert for SELL signals
                    
                    metrics['forward_returns'][period] = {
                        'mean': returns.mean(),
                        'median': returns.median(),
                        'std': returns.std(),
                        'win_rate': (returns > 0).sum() / len(returns) * 100,
                        'best': returns.max(),
                        'worst': returns.min()
                    }
        
        results['signals'][signal_type] = metrics
    
    return results


def analyze_phase_accuracy(df):
    """
    Analyzes the accuracy of phase-based reversal predictions.
    
    Checks if price actually reversed within the predicted timeframe.
    """
    
    results = {
        'total_predictions': 0,
        'accurate_predictions': 0,
        'false_predictions': 0,
        'avg_error_bars': 0.0
    }
    
    # Only analyze bars with valid phase data and signals
    valid_mask = (
        df['T_reversal'].notna() & 
        df['Timing_Signal'] == True
    )
    
    valid_data = df[valid_mask].copy()
    
    if len(valid_data) == 0:
        return results
    
    results['total_predictions'] = len(valid_data)
    
    errors = []
    
    for idx, row in valid_data.iterrows():
        t_reversal = int(row['T_reversal'])
        signal_type = row['Signal']
        
        # Get the position in the dataframe
        pos = df.index.get_loc(idx)
        
        # Look ahead up to t_reversal + buffer
        lookback = min(t_reversal + 5, len(df) - pos - 1)
        
        if lookback <= 0:
            continue
        
        future_prices = df.iloc[pos+1:pos+1+lookback]['close'].values
        current_price = row['close']
        
        if len(future_prices) == 0:
            continue
        
        # Check for reversal based on signal type
        if signal_type == 'BUY':
            # Expecting price to go up (was undervalued)
            reversal_occurred = np.any(future_prices > current_price * 1.01)  # 1% threshold
            if reversal_occurred:
                reversal_bar = np.argmax(future_prices > current_price * 1.01)
                errors.append(abs(reversal_bar - t_reversal))
                results['accurate_predictions'] += 1
            else:
                results['false_predictions'] += 1
                
        elif signal_type == 'SELL':
            # Expecting price to go down (was overvalued)
            reversal_occurred = np.any(future_prices < current_price * 0.99)  # 1% threshold
            if reversal_occurred:
                reversal_bar = np.argmax(future_prices < current_price * 0.99)
                errors.append(abs(reversal_bar - t_reversal))
                results['accurate_predictions'] += 1
            else:
                results['false_predictions'] += 1
    
    if errors:
        results['avg_error_bars'] = np.mean(errors)
        results['median_error_bars'] = np.median(errors)
    
    if results['total_predictions'] > 0:
        results['accuracy_rate'] = (
            results['accurate_predictions'] / results['total_predictions'] * 100
        )
    
    return results


def analyze_market_conditions(df):
    """
    Analyzes market conditions during signal generation.
    
    Categorizes market as trending, ranging, or volatile.
    """
    
    results = {
        'overall': {},
        'by_signal': {}
    }
    
    # Calculate trend strength (using linear regression slope)
    df['Trend_Strength'] = df['close'].rolling(window=50).apply(
        lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) == 50 else np.nan
    )
    
    # Calculate volatility (rolling std)
    df['Volatility'] = df['close'].pct_change().rolling(window=20).std() * 100
    
    # Overall statistics
    results['overall'] = {
        'avg_trend_strength': df['Trend_Strength'].mean(),
        'avg_volatility': df['Volatility'].mean(),
        'trend_direction': 'Uptrend' if df['Trend_Strength'].mean() > 0 else 'Downtrend'
    }
    
    # Statistics by signal type
    for signal_type in ['BUY', 'SELL', 'HOLD']:
        signal_mask = df['Signal'] == signal_type
        signal_data = df[signal_mask]
        
        if len(signal_data) > 0:
            results['by_signal'][signal_type] = {
                'count': len(signal_data),
                'avg_trend_strength': signal_data['Trend_Strength'].mean(),
                'avg_volatility': signal_data['Volatility'].mean()
            }
    
    return results


def generate_backtest_report(df, symbol, timeframe, enable_trade_sim=True):
    """
    Generates a comprehensive backtest report.
    
    Args:
        df: DataFrame with OHLCV and signal data
        symbol: Trading pair symbol
        timeframe: Candle interval
        enable_trade_sim: Run trade simulation if True
    
    Returns a dictionary with all analysis results.
    """
    
    print("\n" + "="*60)
    print(f"BACKTEST REPORT: {symbol} @ {timeframe}")
    print("="*60)
    
    # Calculate forward returns
    df = calculate_forward_returns(df)
    
    # Analyze signal performance
    print("\n[1/5] Analyzing signal performance...")
    signal_perf = analyze_signal_performance(df)
    
    # Analyze phase accuracy
    print("[2/5] Analyzing phase prediction accuracy...")
    phase_acc = analyze_phase_accuracy(df)
    
    # Analyze market conditions
    print("[3/5] Analyzing market conditions...")
    market_cond = analyze_market_conditions(df)
    
    # Run trade simulation
    trade_sim = None
    advanced_metrics = None
    
    if enable_trade_sim:
        print("[4/5] Running trade simulation...")
        trade_sim = simulate_trades(df)
        
        print("[5/5] Calculating advanced metrics...")
        advanced_metrics = calculate_advanced_metrics(trade_sim)
    
    report = {
        'symbol': symbol,
        'timeframe': timeframe,
        'period': {
            'start': df.index[0],
            'end': df.index[-1],
            'total_bars': len(df)
        },
        'signal_performance': signal_perf,
        'phase_accuracy': phase_acc,
        'market_conditions': market_cond,
        'trade_simulation': trade_sim,
        'advanced_metrics': advanced_metrics
    }
    
    return report


def print_backtest_report(report):
    """
    Prints a formatted backtest report to console.
    """
    
    print("\n" + "="*60)
    print("SIGNAL PERFORMANCE SUMMARY")
    print("="*60)
    
    sp = report['signal_performance']
    print(f"\nTotal Bars Analyzed: {sp['total_bars']}")
    print(f"Valid Signal Bars: {sp['valid_bars']}")
    
    for signal_type in ['BUY', 'SELL']:
        if signal_type not in sp['signals']:
            continue
            
        metrics = sp['signals'][signal_type]
        print(f"\n{signal_type} SIGNALS:")
        print(f"  Count: {metrics['count']} ({metrics['percentage']:.2f}%)")
        
        if metrics['count'] == 0:
            continue
            
        print(f"  Avg Deviation (E): {metrics['avg_deviation_e']:.3f}")
        print(f"  Avg Volume Ratio: {metrics['avg_volume_ratio']:.3f}")
        print(f"  High Confidence: {metrics['high_confidence_pct']:.1f}%")
        
        if metrics['forward_returns']:
            print(f"\n  Forward Returns:")
            for period, stats in sorted(metrics['forward_returns'].items(), key=lambda x: int(x[0])):
                print(f"    {period} bars: Mean={stats['mean']:+.2f}%, "
                      f"Median={stats['median']:+.2f}%, "
                      f"WinRate={stats['win_rate']:.1f}%")
    
    print("\n" + "="*60)
    print("PHASE PREDICTION ACCURACY")
    print("="*60)
    
    pa = report['phase_accuracy']
    if pa['total_predictions'] > 0:
        print(f"\nTotal Predictions: {pa['total_predictions']}")
        print(f"Accurate: {pa['accurate_predictions']} ({pa.get('accuracy_rate', 0):.1f}%)")
        print(f"False: {pa['false_predictions']}")
        if 'avg_error_bars' in pa and pa['avg_error_bars'] > 0:
            print(f"Avg Timing Error: {pa['avg_error_bars']:.1f} bars")
            print(f"Median Timing Error: {pa.get('median_error_bars', 0):.1f} bars")
    else:
        print("\nNo phase predictions to analyze")
    
    print("\n" + "="*60)
    print("MARKET CONDITIONS")
    print("="*60)
    
    mc = report['market_conditions']
    overall = mc['overall']
    print(f"\nOverall Trend: {overall['trend_direction']}")
    print(f"Avg Trend Strength: {overall['avg_trend_strength']:.6f}")
    print(f"Avg Volatility: {overall['avg_volatility']:.3f}%")
    
    if mc['by_signal']:
        print("\nConditions by Signal Type:")
        for signal_type, stats in mc['by_signal'].items():
            print(f"  {signal_type}: Count={stats['count']}, "
                  f"Trend={stats['avg_trend_strength']:.6f}, "
                  f"Vol={stats['avg_volatility']:.3f}%")
    
    # Print trade simulation results
    if report.get('trade_simulation'):
        ts = report['trade_simulation']
        am = report.get('advanced_metrics', {})
        
        print("\n" + "="*60)
        print("TRADE SIMULATION RESULTS")
        print("="*60)
        
        print(f"\nInitial Capital: ${ts['initial_capital']:,.2f}")
        print(f"Final Capital: ${ts['final_capital']:,.2f}")
        print(f"Total Return: ${ts['total_return']:+,.2f} ({ts['total_return_pct']:+.2f}%)")
        print(f"Total Fees Paid: ${ts['total_fees']:,.2f}")
        
        print(f"\nTotal Trades: {ts['total_trades']}")
        print(f"  LONG: {ts['long_trades']} | SHORT: {ts['short_trades']}")
        print(f"Winning Trades: {ts['winning_trades']} ({ts['win_rate']:.1f}%)")
        print(f"Losing Trades: {ts['losing_trades']}")
        
        print(f"\nAverage Win: ${ts['avg_win']:+,.2f}")
        print(f"Average Loss: ${ts['avg_loss']:+,.2f}")
        print(f"Largest Win: ${ts['largest_win']:+,.2f}")
        print(f"Largest Loss: ${ts['largest_loss']:+,.2f}")
        print(f"Profit Factor: {ts['profit_factor']:.2f}")
        
        print(f"\nAvg Holding Period: {ts['avg_holding_period']:.1f} bars")
        
        print(f"\nExit Reasons:")
        print(f"  Stop Loss: {ts['stop_loss_exits']}")
        print(f"  Take Profit: {ts['take_profit_exits']}")
        print(f"  Signal Reversal: {ts['signal_reversal_exits']}")
        
        if am:
            print("\n" + "="*60)
            print("ADVANCED METRICS")
            print("="*60)
            
            print(f"\nSharpe Ratio: {am['sharpe_ratio']:.3f}")
            print(f"Sortino Ratio: {am['sortino_ratio']:.3f}")
            print(f"Calmar Ratio: {am['calmar_ratio']:.3f}")
            print(f"Recovery Factor: {am['recovery_factor']:.3f}")
            
            print(f"\nMax Drawdown: {am['max_drawdown_pct']:.2f}%")
            print(f"Max Drawdown Duration: {am['max_drawdown_duration']} bars")
            
            print(f"\nAvg Return per Bar: {am['avg_return_per_bar']:.4f}%")
            print(f"Volatility: {am['volatility']:.3f}%")
    
    print("\n" + "="*60)


def export_signals_to_csv(df, filename='oracle_signals.csv'):
    """
    Exports signal data to CSV for external analysis.
    """
    
    export_cols = [
        'open', 'high', 'low', 'close', 'volume',
        'Z_prime', 'Deviation', 'Sigma', 'E',
        'Dominant_Period', 'Phase_Rad', 'T_reversal',
        'Deviation_Signal', 'Timing_Signal',
        'Signal', 'Direction', 'Confidence', 'Volume_Ratio'
    ]
    
    # Only export columns that exist
    export_cols = [col for col in export_cols if col in df.columns]
    
    df[export_cols].to_csv(filename)
    print(f"\n✅ Exported signal data to {filename}")
    
    return filename


# ============================================================================
# TRADE SIMULATION MODULE
# ============================================================================

def simulate_trades(df, initial_capital=10000, position_size_pct=0.95, 
                   stop_loss_pct=0.02, take_profit_pct=0.05, 
                   fee_pct=0.001, use_confidence=True):
    """
    Simulates actual trading with entry/exit rules, position management, and risk controls.
    
    Args:
        df: DataFrame with OHLCV and signal data
        initial_capital: Starting account balance in USD
        position_size_pct: % of capital to use per trade (0.95 = 95%)
        stop_loss_pct: Stop loss as % from entry (0.02 = 2%)
        take_profit_pct: Take profit as % from entry (0.05 = 5%)
        fee_pct: Trading fee per trade (0.001 = 0.1%)
        use_confidence: Only trade "High" confidence signals if True
    
    Returns:
        Dictionary with trade simulation results
    """
    
    # Trading state
    capital = initial_capital
    position = None  # None, 'LONG', or 'SHORT'
    entry_price = 0
    entry_bar = 0
    position_size = 0
    
    # Trade tracking
    trades = []
    equity_curve = [initial_capital]
    
    for i, (idx, row) in enumerate(df.iterrows()):
        signal = row['Signal']
        price = row['close']
        confidence = row.get('Confidence', 'Medium')
        
        # Skip if using confidence filter and signal is not high confidence
        if use_confidence and confidence != 'High' and signal in ['BUY', 'SELL']:
            equity_curve.append(capital)
            continue
        
        # === ENTRY LOGIC ===
        if position is None:
            if signal == 'BUY' and capital > 0:
                # Enter LONG position
                position = 'LONG'
                entry_price = price
                entry_bar = i
                
                # Calculate position size (account for fees)
                position_size = (capital * position_size_pct) / price
                entry_cost = position_size * price
                entry_fee = entry_cost * fee_pct
                capital -= (entry_cost + entry_fee)
                
                trades.append({
                    'entry_bar': i,
                    'entry_time': idx,
                    'entry_price': entry_price,
                    'position': 'LONG',
                    'position_size': position_size,
                    'entry_fee': entry_fee,
                    'confidence': confidence,
                    'entry_deviation': row['E']
                })
                
            elif signal == 'SELL' and capital > 0:
                # Enter SHORT position
                position = 'SHORT'
                entry_price = price
                entry_bar = i
                
                # For shorts, borrow and sell
                position_size = (capital * position_size_pct) / price
                entry_proceeds = position_size * price
                entry_fee = entry_proceeds * fee_pct
                capital += (entry_proceeds - entry_fee)
                
                trades.append({
                    'entry_bar': i,
                    'entry_time': idx,
                    'entry_price': entry_price,
                    'position': 'SHORT',
                    'position_size': position_size,
                    'entry_fee': entry_fee,
                    'confidence': confidence,
                    'entry_deviation': row['E']
                })
        
        # === EXIT LOGIC ===
        elif position == 'LONG':
            exit_triggered = False
            exit_reason = None
            
            # Check stop loss
            if price <= entry_price * (1 - stop_loss_pct):
                exit_triggered = True
                exit_reason = 'Stop Loss'
            
            # Check take profit
            elif price >= entry_price * (1 + take_profit_pct):
                exit_triggered = True
                exit_reason = 'Take Profit'
            
            # Check signal reversal
            elif signal == 'SELL':
                exit_triggered = True
                exit_reason = 'Signal Reversal'
            
            # Check max holding period (prevent stuck positions)
            elif i - entry_bar > 100:  # Adjust based on timeframe
                exit_triggered = True
                exit_reason = 'Max Hold Period'
            
            if exit_triggered:
                # Close LONG position
                exit_proceeds = position_size * price
                exit_fee = exit_proceeds * fee_pct
                capital += (exit_proceeds - exit_fee)
                
                # Calculate P&L
                pnl = exit_proceeds - (position_size * entry_price)
                pnl_pct = (price / entry_price - 1) * 100
                total_fees = trades[-1]['entry_fee'] + exit_fee
                net_pnl = pnl - total_fees
                
                # Update trade record
                trades[-1].update({
                    'exit_bar': i,
                    'exit_time': idx,
                    'exit_price': price,
                    'exit_fee': exit_fee,
                    'exit_reason': exit_reason,
                    'holding_period': i - entry_bar,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'net_pnl': net_pnl,
                    'total_fees': total_fees,
                    'exit_deviation': row['E']
                })
                
                position = None
                position_size = 0
        
        elif position == 'SHORT':
            exit_triggered = False
            exit_reason = None
            
            # Check stop loss (price went up)
            if price >= entry_price * (1 + stop_loss_pct):
                exit_triggered = True
                exit_reason = 'Stop Loss'
            
            # Check take profit (price went down)
            elif price <= entry_price * (1 - take_profit_pct):
                exit_triggered = True
                exit_reason = 'Take Profit'
            
            # Check signal reversal
            elif signal == 'BUY':
                exit_triggered = True
                exit_reason = 'Signal Reversal'
            
            # Check max holding period
            elif i - entry_bar > 100:
                exit_triggered = True
                exit_reason = 'Max Hold Period'
            
            if exit_triggered:
                # Close SHORT position (buy back)
                exit_cost = position_size * price
                exit_fee = exit_cost * fee_pct
                capital -= (exit_cost + exit_fee)
                
                # Calculate P&L (profit when price goes down)
                pnl = (position_size * entry_price) - exit_cost
                pnl_pct = (entry_price / price - 1) * 100
                total_fees = trades[-1]['entry_fee'] + exit_fee
                net_pnl = pnl - total_fees
                
                # Update trade record
                trades[-1].update({
                    'exit_bar': i,
                    'exit_time': idx,
                    'exit_price': price,
                    'exit_fee': exit_fee,
                    'exit_reason': exit_reason,
                    'holding_period': i - entry_bar,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'net_pnl': net_pnl,
                    'total_fees': total_fees,
                    'exit_deviation': row['E']
                })
                
                position = None
                position_size = 0
        
        # Track equity curve
        if position is None:
            equity_curve.append(capital)
        else:
            # Mark-to-market for open position
            if position == 'LONG':
                unrealized_pnl = position_size * (price - entry_price)
                equity_curve.append(capital + (position_size * price))
            else:  # SHORT
                unrealized_pnl = position_size * (entry_price - price)
                equity_curve.append(capital - (position_size * price))
    
    # Close any remaining open position at last price
    if position is not None:
        last_price = df.iloc[-1]['close']
        if position == 'LONG':
            exit_proceeds = position_size * last_price
            exit_fee = exit_proceeds * fee_pct
            capital += (exit_proceeds - exit_fee)
            pnl = exit_proceeds - (position_size * entry_price)
        else:  # SHORT
            exit_cost = position_size * last_price
            exit_fee = exit_cost * fee_pct
            capital -= (exit_cost + exit_fee)
            pnl = (position_size * entry_price) - exit_cost
        
        trades[-1].update({
            'exit_bar': len(df) - 1,
            'exit_time': df.index[-1],
            'exit_price': last_price,
            'exit_fee': exit_fee,
            'exit_reason': 'End of Data',
            'holding_period': len(df) - 1 - entry_bar,
            'pnl': pnl - (trades[-1]['entry_fee'] + exit_fee),
            'pnl_pct': (last_price / entry_price - 1) * 100 if position == 'LONG' else (entry_price / last_price - 1) * 100,
            'net_pnl': pnl - (trades[-1]['entry_fee'] + exit_fee),
            'total_fees': trades[-1]['entry_fee'] + exit_fee,
            'exit_deviation': df.iloc[-1]['E']
        })
    
    # Calculate trade statistics
    completed_trades = [t for t in trades if 'exit_price' in t]
    
    if len(completed_trades) == 0:
        return {
            'total_trades': 0,
            'final_capital': capital,
            'total_return_pct': (capital / initial_capital - 1) * 100,
            'trades': [],
            'equity_curve': equity_curve
        }
    
    winning_trades = [t for t in completed_trades if t['net_pnl'] > 0]
    losing_trades = [t for t in completed_trades if t['net_pnl'] <= 0]
    
    total_pnl = sum(t['net_pnl'] for t in completed_trades)
    total_fees = sum(t['total_fees'] for t in completed_trades)
    
    results = {
        'initial_capital': initial_capital,
        'final_capital': capital,
        'total_return': total_pnl,
        'total_return_pct': (capital / initial_capital - 1) * 100,
        'total_trades': len(completed_trades),
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'win_rate': len(winning_trades) / len(completed_trades) * 100 if completed_trades else 0,
        'avg_win': np.mean([t['net_pnl'] for t in winning_trades]) if winning_trades else 0,
        'avg_loss': np.mean([t['net_pnl'] for t in losing_trades]) if losing_trades else 0,
        'largest_win': max([t['net_pnl'] for t in winning_trades]) if winning_trades else 0,
        'largest_loss': min([t['net_pnl'] for t in losing_trades]) if losing_trades else 0,
        'avg_holding_period': np.mean([t['holding_period'] for t in completed_trades]),
        'total_fees': total_fees,
        'profit_factor': abs(sum(t['net_pnl'] for t in winning_trades) / sum(t['net_pnl'] for t in losing_trades)) if losing_trades and sum(t['net_pnl'] for t in losing_trades) != 0 else float('inf'),
        'trades': completed_trades,
        'equity_curve': equity_curve,
        'long_trades': len([t for t in completed_trades if t['position'] == 'LONG']),
        'short_trades': len([t for t in completed_trades if t['position'] == 'SHORT']),
        'stop_loss_exits': len([t for t in completed_trades if t['exit_reason'] == 'Stop Loss']),
        'take_profit_exits': len([t for t in completed_trades if t['exit_reason'] == 'Take Profit']),
        'signal_reversal_exits': len([t for t in completed_trades if t['exit_reason'] == 'Signal Reversal'])
    }
    
    return results


def calculate_advanced_metrics(trade_results):
    """
    Calculates advanced trading metrics (Sharpe, Sortino, Drawdown, etc.)
    
    Args:
        trade_results: Output from simulate_trades()
    
    Returns:
        Dictionary with advanced metrics
    """
    
    if trade_results['total_trades'] == 0:
        return {
            'sharpe_ratio': 0,
            'sortino_ratio': 0,
            'max_drawdown_pct': 0,
            'max_drawdown_duration': 0,
            'calmar_ratio': 0,
            'recovery_factor': 0
        }
    
    equity_curve = np.array(trade_results['equity_curve'])
    returns = np.diff(equity_curve) / equity_curve[:-1] * 100  # % returns
    
    # Sharpe Ratio (assuming 252 trading days, adjust for timeframe)
    if len(returns) > 1 and np.std(returns) > 0:
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
    else:
        sharpe_ratio = 0
    
    # Sortino Ratio (only penalize downside volatility)
    downside_returns = returns[returns < 0]
    if len(downside_returns) > 1 and np.std(downside_returns) > 0:
        sortino_ratio = np.mean(returns) / np.std(downside_returns) * np.sqrt(252)
    else:
        sortino_ratio = 0
    
    # Maximum Drawdown
    cumulative_max = np.maximum.accumulate(equity_curve)
    drawdown = (equity_curve - cumulative_max) / cumulative_max * 100
    max_drawdown_pct = abs(np.min(drawdown))
    
    # Drawdown duration (bars in drawdown)
    in_drawdown = drawdown < -0.01  # More than 0.01% drawdown
    if np.any(in_drawdown):
        drawdown_periods = np.split(np.where(in_drawdown)[0], 
                                   np.where(np.diff(np.where(in_drawdown)[0]) != 1)[0] + 1)
        max_drawdown_duration = max(len(period) for period in drawdown_periods)
    else:
        max_drawdown_duration = 0
    
    # Calmar Ratio (return / max drawdown)
    if max_drawdown_pct > 0:
        calmar_ratio = trade_results['total_return_pct'] / max_drawdown_pct
    else:
        calmar_ratio = 0
    
    # Recovery Factor (net profit / max drawdown)
    if max_drawdown_pct > 0:
        recovery_factor = trade_results['total_return'] / (trade_results['initial_capital'] * max_drawdown_pct / 100)
    else:
        recovery_factor = 0
    
    return {
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'max_drawdown_pct': max_drawdown_pct,
        'max_drawdown_duration': max_drawdown_duration,
        'calmar_ratio': calmar_ratio,
        'recovery_factor': recovery_factor,
        'avg_return_per_bar': np.mean(returns) if len(returns) > 0 else 0,
        'volatility': np.std(returns) if len(returns) > 1 else 0
    }
