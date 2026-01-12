import { Stack } from 'expo-router'
import { StatusBar } from 'expo-status-bar'

export default function RootLayout() {
  return (
    <>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerStyle: {
            backgroundColor: '#0a0e27',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen 
          name="index" 
          options={{ 
            title: 'Quant Oracle',
            headerShown: true
          }} 
        />
        <Stack.Screen 
          name="analyze/[symbol]" 
          options={{ 
            title: 'Analysis',
            headerShown: true
          }} 
        />
        <Stack.Screen 
          name="watchlist" 
          options={{ 
            title: 'Watchlist',
            headerShown: true
          }} 
        />
        <Stack.Screen 
          name="backtest" 
          options={{ 
            title: 'Backtest',
            headerShown: true
          }} 
        />
      </Stack>
    </>
  )
}
