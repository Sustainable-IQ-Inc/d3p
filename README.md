# D3P BEM Reports Platform

A cloud-native platform for managing and visualizing design performance data sourced from Building Energy Model (BEM) reports. This system enables users to upload, validate, process, export, and visualize energy modeling data from various simulation engines.

## Table of Contents
- [Overview](#overview)
- [System Architecture](#system-architecture)
- [How It Works](#how-it-works)
- [Deployment Pipeline](#deployment-pipeline)
- [Getting Started](#getting-started)

## Overview

The D3P BEM Reports Platform is a solution for managing building energy modeling data:

- **Upload & Validate**: Accepts energy model reports from multiple building energy modeling simulation tools (EnergyPlus, eQUEST, IES-VE)
- **Process & Store**: Validates, parses, and stores energy data with full audit trails
- **Visualize**: Provides interactive charts for exploring and comparing building performance
- **Secure**: Role-based access control with company-level data isolation
- **Scalable**: Cloud-native architecture that scales automatically with demand

## System Architecture

### Components

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Frontend      │       │    Backend      │       │   Visualizer    │
│   (Next.js)     │◄─────►│   (FastAPI)     │◄─────►│  (Streamlit)    │
│                 │       │                 │       │                 │
│  - User Auth    │       │  - API Logic    │       │  - Analytics    │
│  - File Upload  │       │  - Validation   │       │  - Charts       │
│  - Management   │       │  - Processing   │       │  - Filters      │
└─────────────────┘       └─────────────────┘       └─────────────────┘
         │                         │                         │
         │                         ▼                         │
         │                ┌─────────────────┐               │
         └───────────────►│   Supabase      │◄──────────────┘
                          │   (PostgreSQL)  │
                          │                 │
                          │  - Auth/Users   │
                          │  - Projects     │
                          │  - Energy Data  │
                          └─────────────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │  Cloud Storage  │
                          │  (GCS Buckets)  │
                          │                 │
                          │  - Raw Files    │
                          │  - Attachments  │
                          └─────────────────┘
```

### Technology Stack

- **Frontend**: Next.js with TypeScript and Material-UI
- **Backend**: Python FastAPI with Supabase client
- **Database**: PostgreSQL via Supabase (with Row Level Security)
- **Visualization**: Streamlit dashboard with Plotly charts
- **Storage**: Google Cloud Storage for file uploads
- **Deployment**: Google Cloud Run (containerized services)
- **CI/CD**: GitHub Actions with multi-environment support

## How It Works

### 1. User Authentication & Authorization

- Users authenticate through Supabase Auth (magic link)
- Each user belongs to a **company** with specific permissions
- D3P Admin users can manage company members and invite new users

### 2. Data Upload Flow

```
1. User uploads file (Excel/PDF/HTML) via Frontend
2. Frontend sends file to Backend API
3. Backend validates file format and user permissions
4. File stored in GCS with signed URL for secure access
5. Backend parses file based on report type
6. Extracted data stored in Supabase with full metadata
7. User notified of success/errors
```

### 3. Data Validation

The backend performs comprehensive validation:
- **Pre-validation**: File format, required fields, data types, file size
- **Business rules**: Energy code compliance, climate zone matching
- **Post-processing**: Unit conversions, calculations, derived metrics

### 4. Data Visualization

The Streamlit visualizer provides:
- **Project comparison**: Compare multiple buildings side-by-side
- **Energy breakdowns**: By end-use, fuel type, system

- **Filtering**: By climate zone, building type, year, etc.
- **Export**: Download filtered data as CSV

## Deployment Pipeline

The platform uses GitHub Actions for automated deployment with **separate staging and production environments**.

### Branch Strategy

- **`staging` branch** → Deploys to staging environment (with test data)
- **`main` branch** → Deploys to production environment (live data)

### Deployment Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  Push to staging/main branch                                │
│  or Manual workflow trigger                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  1. Check Changes     │
         │  (Which services?)    │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  2. Setup Secrets     │
         │  (GCP Secret Manager) │
         └───────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌────────────────┐     ┌────────────────┐
│  3a. Frontend  │     │  3b. Visualizer│
│  (if changed)  │     │  (if changed)  │
└────────────────┘     └────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  3c. Backend          │
         │  (if changed)         │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  4. Database          │
         │  Migrations & Seeds   │
         │  (ONLY after backend  │
         │   deploys successfully)│
         └───────────────────────┘
```

### Key Deployment Features

1. **Environment-based secrets**: Staging and production use separate credentials
2. **Conditional deployment**: Only deploy changed services (detected via git diff)
3. **Sequential database deployment**: Migrations run **only after** backend successfully deploys
4. **Automatic rollback**: Failed deployments don't affect running services
5. **URL generation**: Service URLs auto-generated based on GCP project number

### Manual Deployment

Trigger deployments manually via GitHub Actions:
1. Go to **Actions** → **Deploy Cloud Run Services**
2. Click **Run workflow**
3. Select which services to deploy (frontend/backend/visualizer)
4. Workflow uses secrets based on current branch (`staging` or `main`)

## Getting Started


### For Administrators (Deploying the Platform)

1. **Initial Setup**: Follow [DEPLOYMENT.md](./DEPLOYMENT.md) for complete setup instructions
   - Set up GCP project and service accounts
   - Configure Supabase (staging and/or production)
   - Set GitHub Actions secrets
   - Deploy via GitHub Actions

2. **Managing Users**:
   - Admin users can invite new users via the frontend
   - Users are automatically assigned to companies
   - Permissions managed through Supabase dashboard

3. **Monitoring**:
   - View deployment status in GitHub Actions
   - Check service logs in GCP Cloud Run console
   - Monitor database in Supabase dashboard
   - Track costs in GCP Billing

### For Developers (Local Development)

See [LOCAL_DEVELOPMENT.md](./LOCAL_DEVELOPMENT.md) for detailed instructions on:
- Setting up your local environment
- Running services locally
- Database migrations
- Testing





## Testing

### Backend Tests

The backend includes a comprehensive test suite covering models, API endpoints, utilities, and business logic.

#### Setup

1. Ensure you have the backend virtual environment activated:
```bash
cd backend
source backend-venv/bin/activate  # On Windows: backend-venv\Scripts\activate
```

2. Install test dependencies (already included in `requirements.txt`):
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the `backend/` directory with test configuration:
```bash
cp env.example .env
# Edit .env with test values (see env.example for required fields)
```

#### Running Tests

**Run all tests:**
```bash
cd backend
source backend-venv/bin/activate
python -m pytest tests/ -v
```

**Run specific test file:**
```bash
python -m pytest tests/test_conversions.py -v
python -m pytest tests/test_models.py -v
python -m pytest tests/test_main_api.py -v
```

**Run tests with coverage:**
```bash
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
```

**Run tests matching a pattern:**
```bash
python -m pytest tests/ -k "conversion" -v
```

#### Test Organization

- `test_models.py` - Pydantic model validation tests
- `test_conversions.py` - Unit conversion and energy calculation tests
- `test_main_api.py` - API endpoint tests with mocked authentication
- `test_authorization_required.py` - Authorization and security tests
- `test_utils.py` - Utility function tests (encryption, enums, etc.)
- `test_weather_location.py` - Weather and location parsing tests

#### Test Results

Current test coverage:
- ✅ **109 tests passing**
- ⏭️ **5 tests skipped** (async tests requiring pytest-asyncio configuration)



****************************

**Copyright Notice**

Deep Design Data Portal (D3P) Copyright (c) 2025, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy) and Sustainable IQ, Inc. All rights reserved.

If you have questions about your rights to use or distribute this software,
please contact Berkeley Lab's Intellectual Property Office at
IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department
of Energy and the U.S. Government consequently retains certain rights.  As
such, the U.S. Government has been granted for itself and others acting on
its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the
Software to reproduce, distribute copies to the public, prepare derivative 
works, and perform publicly and display publicly, and to permit others to do so.