"""
Visualization utilities for the Quant Oracle.

Generates ASCII charts and summary visualizations for terminal output.
No external plotting libraries required.
"""

import pandas as pd
import numpy as np


def create_ascii_chart(series, height=10, width=60, title="Chart"):
    """
    Creates a simple ASCII line chart.
    
    Args:
        series: Pandas Series or list of values
        height: Chart height in characters
        width: Chart width in characters
        title: Chart title
    
    Returns:
        String containing ASCII chart
    """
    
    if isinstance(series, pd.Series):
        values = series.dropna().values
    else:
        values = np.array(series)
    
    if len(values) == 0:
        return f"{title}\n(No data to display)"
    
    # Normalize values to chart height
    min_val = np.min(values)
    max_val = np.max(values)
    
    if max_val == min_val:
        normalized = np.full(len(values), height // 2)
    else:
        normalized = ((values - min_val) / (max_val - min_val) * (height - 1)).astype(int)
    
    # Sample data to fit width
    if len(normalized) > width:
        indices = np.linspace(0, len(normalized) - 1, width, dtype=int)
        normalized = normalized[indices]
        values = values[indices]
    
    # Build chart
    chart = [title]
    chart.append("─" * (width + 10))
    
    for row in range(height - 1, -1, -1):
        line = ""
        
        # Y-axis label
        val_at_row = min_val + (max_val - min_val) * row / (height - 1)
        line += f"{val_at_row:8.2f} │"
        
        # Plot points
        for col in range(len(normalized)):
            if normalized[col] == row:
                line += "●"
            elif normalized[col] > row:
                line += "│"
            else:
                line += " "
        
        chart.append(line)
    
    # X-axis
    chart.append(" " * 9 + "└" + "─" * len(normalized))
    
    return "\n".join(chart)


def create_signal_timeline(df, max_width=80):
    """
    Creates an ASCII timeline showing signals over time.
    
    Args:
        df: DataFrame with Signal column
        max_width: Maximum width of timeline
    
    Returns:
        String containing signal timeline
    """
    
    signals = df['Signal'].values
    
    # Sample to fit width
    if len(signals) > max_width:
        indices = np.linspace(0, len(signals) - 1, max_width, dtype=int)
        signals = signals[indices]
    
    # Create timeline
    timeline = []
    timeline.append("SIGNAL TIMELINE")
    timeline.append("─" * len(signals))
    
    # Signal line
    signal_line = ""
    for sig in signals:
        if sig == 'BUY':
            signal_line += "▲"
        elif sig == 'SELL':
            signal_line += "▼"
        else:
            signal_line += "─"
    
    timeline.append(signal_line)
    timeline.append("─" * len(signals))
    timeline.append("▲ = BUY  ▼ = SELL  ─ = HOLD")
    
    return "\n".join(timeline)


def create_deviation_heatmap(df, max_width=80):
    """
    Creates an ASCII heatmap of deviation values.
    
    Args:
        df: DataFrame with E (deviation) column
        max_width: Maximum width of heatmap
    
    Returns:
        String containing deviation heatmap
    """
    
    deviations = df['E'].dropna().values
    
    if len(deviations) == 0:
        return "DEVIATION HEATMAP\n(No data to display)"
    
    # Sample to fit width
    if len(deviations) > max_width:
        indices = np.linspace(0, len(deviations) - 1, max_width, dtype=int)
        deviations = deviations[indices]
    
    # Create heatmap
    heatmap = []
    heatmap.append("DEVIATION HEATMAP (E)")
    heatmap.append("─" * len(deviations))
    
    # Map deviation to characters
    heat_line = ""
    for dev in deviations:
        abs_dev = abs(dev)
        if abs_dev > 3:
            heat_line += "█"  # Very high
        elif abs_dev > 2:
            heat_line += "▓"  # High
        elif abs_dev > 1:
            heat_line += "▒"  # Medium
        else:
            heat_line += "░"  # Low
    
    heatmap.append(heat_line)
    heatmap.append("─" * len(deviations))
    heatmap.append("░ = Low  ▒ = Medium  ▓ = High  █ = Very High")
    
    return "\n".join(heatmap)


def create_phase_cycle_diagram(phase_rad, t_reversal, dominant_period):
    """
    Creates an ASCII representation of the current phase position.
    
    Args:
        phase_rad: Phase in radians
        t_reversal: Time to reversal in bars
        dominant_period: Dominant cycle period
    
    Returns:
        String containing phase diagram
    """
    
    if pd.isna(phase_rad) or pd.isna(t_reversal) or pd.isna(dominant_period):
        return "PHASE CYCLE DIAGRAM\n(Insufficient data)"
    
    # Convert phase to position on circle (0-360 degrees)
    phase_deg = np.degrees(phase_rad)
    
    # Create circle representation
    diagram = []
    diagram.append("PHASE CYCLE DIAGRAM")
    diagram.append("─" * 40)
    
    # Simple circle with position marker
    radius = 8
    center_x, center_y = 10, 8
    
    # Calculate position on circle
    angle = phase_rad
    pos_x = int(center_x + radius * np.cos(angle))
    pos_y = int(center_y - radius * np.sin(angle))
    
    # Draw circle
    for y in range(17):
        line = ""
        for x in range(21):
            dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            
            if x == pos_x and y == pos_y:
                line += "●"  # Current position
            elif abs(dist - radius) < 0.5:
                line += "○"  # Circle
            elif x == center_x and y == center_y:
                line += "+"  # Center
            else:
                line += " "
        
        diagram.append(line)
    
    diagram.append("─" * 40)
    diagram.append(f"Phase: {phase_deg:.1f}°")
    diagram.append(f"Time to Reversal: {t_reversal:.1f} bars")
    diagram.append(f"Cycle Period: {dominant_period:.1f} bars")
    diagram.append(f"Completion: {(1 - t_reversal/dominant_period)*100:.1f}%")
    
    return "\n".join(diagram)


def create_summary_dashboard(oracle_result, df):
    """
    Creates a comprehensive ASCII dashboard with key metrics.
    
    Args:
        oracle_result: Dictionary from generate_signal()
        df: DataFrame with all calculated indicators
    
    Returns:
        String containing dashboard
    """
    
    dashboard = []
    dashboard.append("╔" + "═" * 78 + "╗")
    dashboard.append("║" + " " * 25 + "QUANT ORACLE DASHBOARD" + " " * 31 + "║")
    dashboard.append("╠" + "═" * 78 + "╣")
    
    # Current State
    signal = oracle_result['Final_Signal']
    signal_emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '⚪'}.get(signal, '⚪')
    
    dashboard.append(f"║ Symbol: {oracle_result['Symbol']:<20} Timeframe: {oracle_result['Timeframe']:<10} Signal: {signal_emoji} {signal:<10} ║")
    dashboard.append(f"║ Price: ${oracle_result['Current_Price']:<20.6f} Direction: {oracle_result['Direction']:<30} ║")
    dashboard.append("╠" + "═" * 78 + "╣")
    
    # Key Metrics
    dashboard.append("║ KEY METRICS" + " " * 66 + "║")
    dashboard.append(f"║   Equilibrium (Z'): ${oracle_result['Equilibrium_Z_prime']:<10.6f}  Deviation (E): {oracle_result['Deviation_E']:>+8.3f}      ║")
    dashboard.append(f"║   Sigma: {oracle_result['Sigma']:<15.6f}  Threshold: {oracle_result['Sigma_Threshold']:<20.1f}  ║")
    dashboard.append(f"║   Volume Ratio: {oracle_result['Volume_Ratio']:<15.3f}  Confidence: {oracle_result['Confidence']:<20}  ║")
    dashboard.append("╠" + "═" * 78 + "╣")
    
    # Phase Analysis
    dashboard.append("║ PHASE ANALYSIS" + " " * 63 + "║")
    dashboard.append(f"║   Dominant Period: {oracle_result['Dominant_Period']:<10.2f} bars  Phase: {oracle_result['Phase_Deg']:<10.2f}°        ║")
    dashboard.append(f"║   Time to Reversal: {oracle_result['T_reversal']:<10.2f} bars  Threshold: {oracle_result['Reversal_Threshold_Bars']:<10.2f} bars  ║")
    dashboard.append(f"║   Spectral Power: {oracle_result['Spectral_Power']:<20.6f}                              ║")
    dashboard.append("╠" + "═" * 78 + "╣")
    
    # Signal Statistics
    signal_counts = df['Signal'].value_counts()
    total_signals = len(df)
    
    dashboard.append("║ HISTORICAL SIGNALS" + " " * 59 + "║")
    for sig_type in ['BUY', 'SELL', 'HOLD']:
        count = signal_counts.get(sig_type, 0)
        pct = (count / total_signals * 100) if total_signals > 0 else 0
        bar_length = int(pct / 2)  # Scale to fit
        bar = "█" * bar_length + "░" * (50 - bar_length)
        dashboard.append(f"║   {sig_type:<4}: {bar} {pct:>5.1f}%  ║")
    
    dashboard.append("╚" + "═" * 78 + "╝")
    
    return "\n".join(dashboard)


def print_visual_analysis(oracle_result, df):
    """
    Prints a complete visual analysis to the console.
    
    Args:
        oracle_result: Dictionary from generate_signal()
        df: DataFrame with all calculated indicators
    """
    
    print("\n")
    
    # Dashboard
    print(create_summary_dashboard(oracle_result, df))
    
    print("\n")
    
    # Price chart
    print(create_ascii_chart(df['close'].tail(60), title="PRICE CHART (Last 60 bars)"))
    
    print("\n")
    
    # Deviation heatmap
    print(create_deviation_heatmap(df.tail(80)))
    
    print("\n")
    
    # Signal timeline
    print(create_signal_timeline(df.tail(80)))
    
    print("\n")
    
    # Phase diagram
    print(create_phase_cycle_diagram(
        oracle_result['Phase_Rad'],
        oracle_result['T_reversal'],
        oracle_result['Dominant_Period']
    ))
    
    print("\n")
