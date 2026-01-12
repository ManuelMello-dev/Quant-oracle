import { useState } from 'react'
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet } from 'react-native'
import { useRouter } from 'expo-router'

const POPULAR_SYMBOLS = [
  'BTC/USD', 'ETH/USD', 'DOGE/USD', 'SOL/USD',
  'ADA/USD', 'XRP/USD', 'MATIC/USD', 'AVAX/USD'
]

export default function HomeScreen() {
  const router = useRouter()
  const [symbol, setSymbol] = useState('')

  const handleAnalyze = () => {
    if (symbol) {
      router.push(`/analyze/${symbol.replace('/', '-')}`)
    }
  }

  const handleSelectSymbol = (selectedSymbol: string) => {
    setSymbol(selectedSymbol)
    router.push(`/analyze/${selectedSymbol.replace('/', '-')}`)
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Quant Oracle</Text>
          <Text style={styles.subtitle}>
            Professional Trading Analysis
          </Text>
        </View>

        {/* Search */}
        <View style={styles.searchCard}>
          <Text style={styles.cardTitle}>Analyze Symbol</Text>
          <View style={styles.searchRow}>
            <TextInput
              style={styles.input}
              value={symbol}
              onChangeText={(text) => setSymbol(text.toUpperCase())}
              placeholder="Enter symbol (e.g., BTC/USD)"
              placeholderTextColor="#6b7280"
              autoCapitalize="characters"
            />
            <TouchableOpacity 
              style={styles.analyzeButton}
              onPress={handleAnalyze}
            >
              <Text style={styles.buttonText}>Analyze</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Popular Symbols */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Popular Symbols</Text>
          <View style={styles.symbolGrid}>
            {POPULAR_SYMBOLS.map((sym) => (
              <TouchableOpacity
                key={sym}
                style={styles.symbolButton}
                onPress={() => handleSelectSymbol(sym)}
              >
                <Text style={styles.symbolText}>{sym}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Features */}
        <View style={styles.featuresGrid}>
          <View style={styles.featureCard}>
            <Text style={styles.featureEmoji}>📊</Text>
            <Text style={styles.featureTitle}>VWAP Analysis</Text>
            <Text style={styles.featureText}>
              Volume-weighted equilibrium detection
            </Text>
          </View>

          <View style={styles.featureCard}>
            <Text style={styles.featureEmoji}>🔮</Text>
            <Text style={styles.featureTitle}>FFT Prediction</Text>
            <Text style={styles.featureText}>
              Cycle detection and timing
            </Text>
          </View>

          <View style={styles.featureCard}>
            <Text style={styles.featureEmoji}>🤖</Text>
            <Text style={styles.featureTitle}>AI Analysis</Text>
            <Text style={styles.featureText}>
              Professional insights (Premium)
            </Text>
          </View>

          <View style={styles.featureCard}>
            <Text style={styles.featureEmoji}>📈</Text>
            <Text style={styles.featureTitle}>Backtesting</Text>
            <Text style={styles.featureText}>
              71.4% win rate validated
            </Text>
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.actionsRow}>
          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={() => router.push('/watchlist')}
          >
            <Text style={styles.buttonText}>Watchlist</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={() => router.push('/backtest')}
          >
            <Text style={styles.buttonText}>Backtest</Text>
          </TouchableOpacity>
        </View>
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
  header: {
    alignItems: 'center',
    marginBottom: 24,
  },
  title: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#3b82f6',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#9ca3af',
  },
  searchCard: {
    backgroundColor: '#0a0e27',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#1f2937',
  },
  card: {
    backgroundColor: '#0a0e27',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#1f2937',
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 12,
  },
  searchRow: {
    flexDirection: 'row',
    gap: 8,
  },
  input: {
    flex: 1,
    backgroundColor: '#060918',
    borderWidth: 1,
    borderColor: '#374151',
    borderRadius: 8,
    padding: 12,
    color: '#fff',
    fontSize: 16,
  },
  analyzeButton: {
    backgroundColor: '#3b82f6',
    borderRadius: 8,
    paddingHorizontal: 24,
    justifyContent: 'center',
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
  symbolGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  symbolButton: {
    backgroundColor: '#060918',
    borderRadius: 8,
    padding: 12,
    minWidth: '30%',
    alignItems: 'center',
  },
  symbolText: {
    color: '#fff',
    fontWeight: '500',
  },
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 16,
  },
  featureCard: {
    backgroundColor: '#0a0e27',
    borderRadius: 12,
    padding: 16,
    width: '48%',
    borderWidth: 1,
    borderColor: '#1f2937',
  },
  featureEmoji: {
    fontSize: 32,
    marginBottom: 8,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 4,
  },
  featureText: {
    fontSize: 12,
    color: '#9ca3af',
  },
  actionsRow: {
    flexDirection: 'row',
    gap: 12,
  },
  secondaryButton: {
    flex: 1,
    backgroundColor: '#374151',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
  },
})
