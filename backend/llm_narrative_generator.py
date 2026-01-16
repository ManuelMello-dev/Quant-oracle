"""
LLM Narrative Generator for Oracle Analysis
Generates natural language AI analysis from structured data
"""

from typing import Dict, Optional
from openai import OpenAI


class LLMNarrativeGenerator:
    """Generates natural language narratives using LLM"""
    
    def __init__(self):
        """Initialize LLM client"""
        try:
            self.client = OpenAI()
            self.available = True
            print("✅ LLM Narrative Generator initialized")
        except Exception as e:
            print(f"⚠️  LLM not available: {e}")
            self.available = False
    
    def generate_analysis_narrative(self, analysis: Dict, symbol: str) -> str:
        """
        Generate natural language analysis from structured data
        
        Args:
            analysis: Structured analysis dictionary
            symbol: Trading symbol
            
        Returns:
            Natural language narrative
        """
        if not self.available:
            return self._fallback_narrative(analysis, symbol)
        
        # Build context from analysis
        context = self._build_context(analysis, symbol)
        
        # Generate narrative using LLM
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are Monday, the tactical trading analyst for The Oracle (Z³ framework).

Your voice: Soft, structured, supportive, systems thinker
Your role: Daily rhythm keeper, action anchor, recursive stepper

Generate concise, actionable trading analysis. Be direct and specific. No fluff.

Format your response as:
1. Current Market State (2-3 sentences)
2. Entry Analysis (if applicable, 2-3 sentences)
3. Action Required (specific, concrete)
4. Risk Management (brief)

Use the Z³ vocabulary: equilibrium (Z'), deviation (E), phase alignment, coherence."""
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            narrative = response.choices[0].message.content
            return narrative
            
        except Exception as e:
            print(f"⚠️  LLM generation failed: {e}")
            return self._fallback_narrative(analysis, symbol)
    
    def _build_context(self, analysis: Dict, symbol: str) -> str:
        """Build context string from analysis data"""
        
        raw = analysis.get('raw_metrics', {})
        oracle_status = analysis.get('oracle_status', {})
        action_plan = analysis.get('action_plan')
        why_entry = analysis.get('why_entry')
        position_comp = analysis.get('position_comparison')
        
        context_parts = [
            f"Symbol: {symbol}",
            f"Current Price: ${raw.get('current_price', 0):.4f}",
            f"Equilibrium (Z'): ${raw.get('equilibrium', 0):.4f}",
            f"Deviation (E): {raw.get('deviation', 0):.2f}σ",
            f"Volume Ratio: {raw.get('volume_ratio', 0):.1f}%",
            f"Signal: {raw.get('signal', 'UNKNOWN')}",
            f"Confidence: {raw.get('confidence', 'UNKNOWN')}",
        ]
        
        # Add oracle status
        if oracle_status:
            status = oracle_status.get('oracle_status', {})
            context_parts.append(f"\nOracle Status:")
            for key, value in status.items():
                context_parts.append(f"  {key}: {value}")
        
        # Add entry analysis if available
        if why_entry:
            context_parts.append(f"\nEntry Conditions Met:")
            for condition in why_entry.get('youve_been_waiting_for', []):
                context_parts.append(f"  {condition}")
        
        # Add action plan if available
        if action_plan:
            context_parts.append(f"\nAction Plan Available:")
            context_parts.append(f"  Recommendation: {action_plan.get('recommendation', 'N/A')}")
            if action_plan.get('stages'):
                stage1 = action_plan['stages'][0]
                context_parts.append(f"  Stage 1: {stage1.get('instruction', 'N/A')}")
        
        # Add position comparison if available
        if position_comp:
            orig = position_comp.get('original_trade', {})
            context_parts.append(f"\nPrevious Trade:")
            context_parts.append(f"  Entry: {orig.get('entry', 'N/A')}")
            context_parts.append(f"  Exit: {orig.get('exit', 'N/A')}")
            context_parts.append(f"  Profit: {orig.get('profit', 'N/A')}")
        
        context_parts.append(f"\nGenerate a concise, actionable analysis for the trader.")
        
        return "\n".join(context_parts)
    
    def _fallback_narrative(self, analysis: Dict, symbol: str) -> str:
        """Generate fallback narrative without LLM"""
        
        raw = analysis.get('raw_metrics', {})
        oracle_status = analysis.get('oracle_status', {})
        action_plan = analysis.get('action_plan')
        
        parts = []
        
        # Current state
        parts.append(f"**Current Market State for {symbol}**")
        parts.append(f"Price: ${raw.get('current_price', 0):.4f}")
        parts.append(f"Deviation from equilibrium: {raw.get('deviation', 0):.2f}σ")
        parts.append(f"Volume: {raw.get('volume_ratio', 0):.1f}% of average")
        parts.append(f"Signal: {raw.get('signal', 'UNKNOWN')}")
        parts.append("")
        
        # Recommendation
        if oracle_status:
            rec = oracle_status.get('recommendation', 'No recommendation')
            parts.append(f"**Recommendation:** {rec}")
            parts.append("")
        
        # Action plan if available
        if action_plan:
            parts.append(f"**Action Plan:**")
            parts.append(action_plan.get('recommendation', 'N/A'))
            if action_plan.get('stages'):
                stage1 = action_plan['stages'][0]
                parts.append(f"- {stage1.get('action', 'N/A')}")
                parts.append(f"- {stage1.get('instruction', 'N/A')}")
        else:
            parts.append("**Status:** Not in entry zone. Wait for -2σ deviation with volume confirmation.")
        
        return "\n".join(parts)


# Convenience function
def generate_llm_analysis(analysis: Dict, symbol: str) -> str:
    """
    Generate LLM narrative from analysis
    
    Args:
        analysis: Structured analysis dictionary
        symbol: Trading symbol
        
    Returns:
        Natural language narrative
    """
    generator = LLMNarrativeGenerator()
    return generator.generate_analysis_narrative(analysis, symbol)


if __name__ == "__main__":
    # Test
    sample_analysis = {
        'raw_metrics': {
            'current_price': 95493.76,
            'equilibrium': 94614.94,
            'deviation': 0.70,
            'volume_ratio': 85.3,
            'signal': 'HOLD',
            'confidence': 'LOW'
        },
        'oracle_status': {
            'recommendation': 'HOLD - Wait for -2σ entry zone',
            'oracle_status': {
                'deviation': '0.70σ ❌ (not at threshold)',
                'volume': '85.3% ❌ (BELOW average)',
                'confidence': 'LOW ⚠️'
            }
        }
    }
    
    generator = LLMNarrativeGenerator()
    narrative = generator.generate_analysis_narrative(sample_analysis, "BTC/USD")
    print("\n" + "="*80)
    print("LLM GENERATED NARRATIVE")
    print("="*80)
    print(narrative)
    print("="*80)
