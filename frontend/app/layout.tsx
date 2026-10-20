import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Phishing Website Detection',
  description: 'Check before you click: analyze suspicious URLs with machine learning to help identify potential phishing websites.',
  generator: 'v0.app',
}

export const viewport: Viewport = { colorScheme: 'dark', themeColor: '#0B1020' }

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body className="antialiased">{children}{process.env.NODE_ENV === 'production' && <Analytics />}</body></html>
}
