import { useEffect, useState } from 'react'
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, StyleSheet, RefreshControl } from 'react-native'
import { useLocalSearchParams, useRouter } from 'expo-router'
import api, { AnalysisResponse } from '../../lib/api'

export default function AnalyzeScreen() {
  const params = useLocalSearchParams()
  const router = useRouter()
  const symbol = (params.symbol as string).replace('-', '/')
  
  const [data, setData] = useState<AnalysisResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [useLLM, setUseLLM] = useState(false)
  const [timeframe, setTimeframe] = useState('1h')

  useEffect(() => {
    loadData()
  }, [symbol, timeframe, useLLM])

  const loadData = async () => {
    try {
      setLoading(true)
      const result = await api.analyze(symbol, timeframe, 365, useLLM)
      setData(result)
    } catch (error) {
      console.error('Failed to load analysis:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const onRefresh = () => {
    setRefreshing(true)
    loadData()
  }

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY': return '#10b981'
      case 'SELL': return '#ef4444'
      default: return '#f59e0b'
    }
  }

  const getSignalEmoji = (signal: string) => {
    switch (signal) {
      case 'BUY': return '🟢'
      case 'SELL': return '🔴'
      default: return '🟡'
    }
  }

  if (loading && !data) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#3b82f6" />
        <Text style={styles.loadingText}>Analyzing {symbol}...</Text>
      </View>
    )
  }

  if (!data) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>Failed to load analysis</Text>
        <TouchableOpacity style={styles.button} onPress={() => router.back()}>
          <Text style={styles.buttonText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    )
  }

  const { metrics, historical } = data

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#3b82f6" />
      }
    >
      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.symbolText}>{symbol}</Text>
          <Text style={styles.timestampText}>
            {new Date(data.timestamp).toLocaleString()}
          </Text>
        </View>

        {/* Controls */}
        <View style={styles.controls}>
          <TouchableOpacity
            style={[styles.controlButton, useLLM && styles.controlButtonActive]}
            onPress={() => setUseLLM(!useLLM)}
          >
            <Text style={styles.controlButtonText}>
              {useLLM ? '🤖 AI On' : '🤖 AI Off'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Main Signal */}
        <View style={[styles.signalCard, { borderColor: getSignalColor(metrics.signal) }]}>
          <Text style={styles.signalEmoji}>{getSignalEmoji(metrics.signal)}</Text>
          <Text style={[styles.signalText, { color: getSignalColor(metrics.signal) }]}>
            {metrics.signal}
          </Text>
          <Text style={styles.signalDescription}>
            {metrics.deviation < -2 && 'Strong undervaluation - Mean reversion likely'}
            {metrics.deviation > 2 && 'Strong overvaluation - Correction likely'}
            {Math.abs(metrics.deviation) <= 2 && 'Near equilibrium - Range-bound trading'}
          </Text>
        </View>

        {/* Metrics Grid */}
        <View style={styles.metricsGrid}>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Price</Text>
            <Text style={styles.metricValue}>${metrics.price.toFixed(4)}</Text>
          </View>

          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>VWAP</Text>
            <Text style={styles.metricValue}>${metrics.vwap.toFixed(4)}</Text>
          </View>

          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Deviation</Text>
            <Text style={[
              styles.metricValue,
              { color: metrics.deviation < -2 ? '#10b981' : metrics.deviation > 2 ? '#ef4444' : '#9ca3af' }
            ]}>
              {metrics.deviation > 0 ? '+' : ''}{metrics.deviation.toFixed(2)}σ
            </Text>
          </View>

          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Volume</Text>
            <Text style={[
              styles.metricValue,
              { color: metrics.volume_ratio > 100 ? '#10b981' : '#9ca3af' }
            ]}>
              {metrics.volume_ratio.toFixed(0)}%
            </Text>
          </View>

          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Trend</Text>
            <Text style={styles.metricValueSmall}>{metrics.trend}</Text>
          </View>

          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Regime</Text>
            <Text style={styles.metricValueSmall}>{metrics.regime}</Text>
          </View>
        </View>

        {/* Professional Analysis */}
        {data.professional_analysis && (
          <View style={styles.analysisCard}>
            <Text style={styles.analysisTitle}>
              Professional Analysis
              <Text style={styles.analysisMethod}> ({data.analysis_method})</Text>
            </Text>
            <Text style={styles.analysisText}>{data.professional_analysis}</Text>
          </View>
        )}

        {/* Historical Stats */}
        <View style={styles.statsCard}>
          <Text style={styles.statsTitle}>Historical Statistics</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Total Bars</Text>
              <Text style={styles.statValue}>{historical.bars}</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>BUY Signals</Text>
              <Text style={[styles.statValue, { color: '#10b981' }]}>
                {historical.buy_signals} ({((historical.buy_signals / historical.bars) * 100).toFixed(1)}%)
              </Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>SELL Signals</Text>
              <Text style={[styles.statValue, { color: '#ef4444' }]}>
                {historical.sell_signals} ({((historical.sell_signals / historical.bars) * 100).toFixed(1)}%)
              </Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>HOLD Signals</Text>
              <Text style={[styles.statValue, { color: '#f59e0b' }]}>
                {historical.hold_signals} ({((historical.hold_signals / historical.bars) * 100).toFixed(1)}%)
              </Text>
            </View>
          </View>
        </View>

        {/* Action Button */}
        <TouchableOpacity
          style={styles.backtestButton}
          onPress={() => router.push(`/backtest?symbol=${symbol}`)}
        >
          <Text style={styles.buttonText}>Run Backtest</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#060918',
  },
  content: {
    padding: 16,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#060918',
  },
  loadingText: {
    color: '#9ca3af',
    marginTop: 16,
    fontSize: 16,
  },
  errorText: {
    color: '#ef4444',
    fontSize: 18,
    marginBottom: 16,
  },
  header: {
    marginBottom: 16,
  },
  symbolText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
  },
  timestampText: {
    fontSize: 14,
    color: '#9ca3af',
    marginTop: 4,
  },
  controls: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  controlButton: {
    backgroundColor: '#374151',
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  controlButtonActive: {
    backgroundColor: '#3b82f6',
  },
  controlButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  signalCard: {
    backgroundColor: '#0a0e27',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    marginBottom: 16,
    borderWidth: 2,
  },
  signalEmoji: {
    fontSize: 48,
    marginBottom: 8,
  },
  signalText: {
    fontSize: 36,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  signalDescription: {
    fontSize: 14,
    color: '#9ca3af',
    textAlign: 'center',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 16,
  },
  metricCard: {
    backgroundColor: '#0a0e27',
    borderRadius: 12,
    padding: 16,
    width: '48%',
    borderWidth: 1,
    borderColor: '#1f2937',
  },
  metricLabel: {
    fontSize: 12,
    color: '#9ca3af',
    marginBottom: 4,
  },
  metricValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    fontFamily: 'monospace',
  },
  metricValueSmall: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
    textTransform: 'capitalize',
  },
  analysisCard: {
    backgroundColor: '#0a0e27',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#1f2937',
  },
  analysisTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 12,
  },
  analysisMethod: {
    fontSize: 12,
    color: '#9ca3af',
  },
  analysisText: {
    fontSize: 14,
    color: '#d1d5db',
    lineHeight: 20,
  },
  statsCard: {
    backgroundColor: '#0a0e27',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#1f2937',
  },
  statsTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 12,
  },
  statsGrid: {
    gap: 12,
  },
  statItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 14,
    color: '#9ca3af',
  },
  statValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  button: {
    backgroundColor: '#3b82f6',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 24,
  },
  backtestButton: {
    backgroundColor: '#3b82f6',
    borderRadius: 8,
    paddingVertical: 16,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
})
