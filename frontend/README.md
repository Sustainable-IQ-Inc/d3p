# BEM Reports Frontend

A Next.js application for Building Energy Management (BEM) reports with TypeScript and Material-UI.

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Install Playwright browsers (for testing):
```bash
npx playwright install
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:8081](http://localhost:8081) in your browser to see the application.

## Testing

This project uses **Playwright** for end-to-end testing.

### Available Test Commands

```bash
# Run all tests headlessly (recommended for CI)
npm test

# Run tests with browser UI visible (good for debugging)
npm run test:headed

# Open Playwright UI for interactive testing
npm run test:ui

# Run tests in debug mode with step-by-step execution
npm run test:debug

# Run specific test file
npx playwright test login.spec.ts
```


### Test Structure

- **Test files**: Located in `tests/` directory with `.spec.ts` extension
- **Fixtures**: Test data files in `tests/fixtures/`
- **Configuration**: `playwright.config.ts`

### Test Features

- **Cross-browser testing**: Chromium, Firefox, and WebKit
- **Automatic screenshots**: On test failures
- **Video recording**: For failed tests
- **Trace collection**: For debugging on retries
- **HTML reports**: Generated after test runs

### Environment Variables

Tests use the following configuration:
- **Base URL**: `http://localhost:8081`
- **Test credentials**: Set via environment variables (see below)
- **Auto server start**: Tests automatically start the dev server

#### Required Environment Variables

Create a `.env.local` file in the frontend directory with:

```bash
# Login credentials for E2E tests
LOGIN_EMAIL=your-test-email@example.com
LOGIN_PASSWORD=your-test-password
```

**Note**: If environment variables are not set, the tests will fall back to default test credentials.

## Project Structure

```
frontend/
├── src/                 # Source code
├── tests/              # Playwright tests
│   ├── fixtures/       # Test data files
│   └── *.spec.ts      # Test files
├── test-results/       # Test artifacts (screenshots, videos)
├── playwright.config.ts # Playwright configuration
├── package.json
└── README.md
```

## Scripts

- `npm run dev` - Start development server on port 8081
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run prettier` - Format code with Prettier
- `npm test` - Run Playwright tests
- `npm run test:headed` - Run tests with visible browser
- `npm run test:ui` - Open Playwright UI
- `npm run test:debug` - Debug tests step-by-step

## Tech Stack

- **Framework**: Next.js 14
- **Language**: TypeScript
- **UI Library**: Material-UI (MUI)
- **Testing**: Playwright
- **Styling**: Emotion CSS-in-JS
- **State Management**: React Query (TanStack Query)
- **Forms**: Formik + Yup validation

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Playwright Documentation](https://playwright.dev/)
- [Material-UI Documentation](https://mui.com/)
