import React from 'react'
import { DocsThemeConfig } from 'nextra-theme-docs'
import { useRouter } from 'next/router'

const config: DocsThemeConfig = {
  logo: <span><strong>D3P Documentation</strong></span>,
  project: {
    link: '/dashboard/default',
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M10 19v-5h4v5c0 .55.45 1 1 1h3c.55 0 1-.45 1-1v-7h1.7c.46 0 .68-.57.33-.87L12.67 3.6c-.38-.34-.96-.34-1.34 0l-8.36 7.53c-.34.3-.13.87.33.87H5v7c0 .55.45 1 1 1h3c.55 0 1-.45 1-1z" fill="currentColor"/>
      </svg>
    )
  },
  docsRepositoryBase: 'https://github.com/your-org/d3p',
  footer: {
    text: `© ${new Date().getFullYear()} D3P. All rights reserved.`,
  },
  editLink: {
    component: null, // Disable edit link since docs are managed via git
  },
  feedback: {
    content: null, // Disable feedback since this is internal docs
  },
  navbar: {
    extraContent: () => {
      const router = useRouter()
      
      const handleLogout = async () => {
        // Import dynamically to avoid SSR issues
        const { createClient } = await import('utils/supabase')
        const supabase = createClient()
        await supabase.auth.signOut()
        router.push('/login')
      }
      
      return (
        <>
          <button
            onClick={() => router.push('/dashboard/default')}
            style={{
              marginRight: '8px',
              padding: '4px 12px',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              background: 'transparent',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Back to App
          </button>
          <button
            onClick={handleLogout}
            style={{
              padding: '4px 12px',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              background: 'transparent',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Logout
          </button>
        </>
      )
    }
  },
  primaryHue: 210, // Blue color to match D3P theme
  darkMode: true,
  nextThemes: {
    defaultTheme: 'light',
  },
}

export default config

