import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Quant Oracle - Professional Trading Analysis',
  description: 'AI-powered quantitative trading analysis with mean reversion signals',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
