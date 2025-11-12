/** @type {import('next').NextConfig} */

const withNextra = require('nextra')({
  latex: true,
  search: {
    codeblocks: false
  }
})

module.exports = withNextra({
  output: 'standalone',
  modularizeImports: {
    '@mui/material': {
      transform: '@mui/material/{{member}}'
    },
    '@mui/lab': {
      transform: '@mui/lab/{{member}}'
    }
  },
  images: {
    domains: ['flagcdn.com']
  },
  transpilePackages: ['react-syntax-highlighter'],
  env: {
    REACT_APP_VERSION: process.env.REACT_APP_VERSION,
    NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET_KEY,
    NEXTAUTH_URL: process.env.NEXTAUTH_URL,
    NEXT_APP_API_URL: process.env.REACT_APP_API_URL,
    NEXT_APP_JWT_SECRET: process.env.REACT_APP_JWT_SECRET,
    NEXT_APP_JWT_TIMEOUT: process.env.REACT_APP_JWT_TIMEOUT,
    NEXTAUTH_SECRET_KEY: process.env.NEXTAUTH_SECRET_KEY,
    NEXT_APP_GOOGLE_MAPS_API_KEY: process.env.REACT_APP_GOOGLE_MAPS_API_KEY,
    NEXT_APP_MAPBOX_ACCESS_TOKEN: process.env.REACT_APP_MAPBOX_ACCESS_TOKEN,
    REDIRECT_URL: process.env.REDIRECT_URL,
    ALLOW_ORIGIN_URL: process.env.ALLOW_ORIGIN_URL,
  }
});
