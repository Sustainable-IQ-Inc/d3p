# Local Development Setup

This guide helps you set up the BEM Reports application for local development.

## 🏗️ Architecture Overview

The application consists of three main components:

- **Frontend** (Next.js) - Port 8081
- **Backend** (FastAPI) - Port 8080  
- **Visualizer** (Streamlit) - Port 8501

## 📋 Prerequisites

### Required Software
- **Node.js** (v18+) and npm/yarn
- **Python** (v3.9+)
- **Docker** and Docker Compose
- **Git**

### Python Virtual Environments
**Recommended**: Create separate virtual environments for backend and visualizer to avoid dependency conflicts:

```bash
# Create virtual environment for backend
cd backend
python -m venv backend-venv
source backend-venv/bin/activate  # On Windows: backend-venv\Scripts\activate
pip install -r requirements.txt

# Create virtual environment for visualizer
cd ../visualizer
python -m venv visualizer-venv
source visualizer-venv/bin/activate  # On Windows: visualizer-venv\Scripts\activate
pip install -r requirements.txt
```

This ensures clean dependency isolation between the two Python services.

### Required Accounts
- **Google Cloud Platform** account with billing enabled
- **Supabase** account (for database and authentication)

## 🚀 Quick Start

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone <your-repo-url>
cd d3p-bem-reports-workflow-test

# Install frontend dependencies
cd frontend
npm install
cd ..

# Install backend dependencies
cd backend
python -m venv backend-venv
source backend-venv/bin/activate  # On Windows: backend-venv\Scripts\activate
pip install -r requirements.txt
cd ..

# Install visualizer dependencies
cd visualizer
python -m venv visualizer-venv
source visualizer-venv/bin/activate  # On Windows: visualizer-venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 2. Environment Setup

#### Backend Environment
```bash
# Copy and configure backend environment
cp backend/env.example backend/.env
```

Edit `backend/.env` with your values:
```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE=your_service_role_key

# Encryption (generate new keys)
ENCRYPTION_KEY=your_32_character_encryption_key
ENCRYPTION_SALT=your_16_character_salt

# Frontend URL for email redirects
REDIRECT_URL=http://localhost:3000

# CORS Configuration (include both localhost and 127.0.0.1)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8081,http://localhost:8501,http://127.0.0.1:3000,http://127.0.0.1:8081,http://127.0.0.1:8501

# External Services (optional)
DDX_API_BASE_URL=your_ddx_api_base_url

# Storage
BUCKET_NAME=your_gcs_bucket_name

# Environment
ENV=local
```

#### Frontend Environment
```bash
# Copy and configure frontend environment
cp frontend/env.local.example frontend/.env.local
```

Edit `frontend/.env.local` with your values:
```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key

# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
NEXT_PUBLIC_STREAMLIT_URL=http://localhost:8501

# Authentication
REDIRECT_URL=http://localhost:8081

# Environment
NEXT_PUBLIC_ENV=local
```

#### Visualizer Environment
```bash
# Copy and configure visualizer environment
cp visualizer/env.example visualizer/.env
```

Edit `visualizer/.env` with your values:
```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE=your_service_role_key

# Storage
BUCKET_NAME=your_gcs_bucket_name

# Environment
ENV=local
```

### 3. Start Development Servers

Start each service in a separate terminal:

**Terminal 1 - Backend:**
```bash
cd backend
source backend-venv/bin/activate  # On Windows: backend-venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Visualizer:**
```bash
cd visualizer
source visualizer-venv/bin/activate  # On Windows: visualizer-venv\Scripts\activate
streamlit run d3p-dataview.py --server.port 8501
```


## 🔧 Development Tools

### Backend Development
- **FastAPI** with automatic API documentation at `http://localhost:8080/docs`
- **Hot reload** enabled for development
- **Debug mode** available with `docker-compose.debug.yml`

### Frontend Development
- **Next.js** with hot reload
- **TypeScript** support
- **ESLint** and **Prettier** configured

### Visualizer Development
- **Streamlit** with hot reload
- **Port 8501** for the visualizer interface

## 🐛 Debugging

### Backend Debugging
```bash
# Start with debugger
cd backend
docker-compose -f docker-compose.debug.yml up --build
```
Then attach your IDE debugger to `localhost:5678`.

**Note**: Docker debugging is only available for the backend service.

### Frontend Debugging
- Use browser dev tools
- React DevTools extension recommended
- Next.js built-in debugging

### Visualizer Debugging
- Streamlit provides built-in debugging
- Check console output for errors

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm run test                    # Run all tests
npm run test:staging           # Run against staging
npm run test:ui                # Run with UI
```

### Backend Tests
```bash
cd backend
source backend-venv/bin/activate  # On Windows: backend-venv\Scripts\activate
python -m pytest              # Run all tests
python -m pytest -v           # Verbose output
```

## 🔐 Authentication Setup

### Google Cloud Setup
1. Create a GCP project
2. Enable required APIs:
   - Cloud Run API
   - Secret Manager API
   - Cloud Storage API
3. Create a service account with required permissions
4. Download the service account key as JSON

### Supabase Setup
1. Create a new Supabase project
2. Get your project URL and API keys
3. Set up your database schema using the migrations in `backend/supabase/migrations/`

## 📁 Project Structure

```
├── backend/                   # FastAPI backend
│   ├── main.py              # Main application
│   ├── models.py            # Database models
│   ├── requirements.txt     # Python dependencies
│   └── supabase/           # Database migrations
├── frontend/                # Next.js frontend
│   ├── src/                # Source code
│   ├── package.json        # Node dependencies
│   └── next.config.js      # Next.js configuration
├── visualizer/              # Streamlit visualizer
│   ├── d3p-dataview.py     # Main visualizer
│   └── requirements.txt    # Python dependencies
└── .github/workflows/      # GitHub Actions
```

## 🚨 Common Issues

### Port Conflicts
- Backend: Change port in `uvicorn` command
- Frontend: Change port in `package.json` scripts
- Visualizer: Change port in `streamlit` command

### Environment Variables
- Ensure all `.env` files are properly configured
- Check that Supabase URLs and keys are correct
- Verify GCP credentials are properly set

### CORS Issues
- Update `ALLOWED_ORIGINS` in backend `.env`
- Ensure frontend URL matches the allowed origins

### Database Issues
- Run Supabase migrations: `supabase db push`
- Check Supabase project is active
- Verify service role key has correct permissions

## 🔄 Development Workflow

1. **Make changes** to your code
2. **Test locally** using the development servers
3. **Commit changes** to your feature branch
4. **Push to GitHub** to trigger deployment workflow
5. **Monitor deployment** in GitHub Actions

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Supabase Documentation](https://supabase.com/docs)
- [Google Cloud Documentation](https://cloud.google.com/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📞 Support

If you encounter issues:
1. Check the logs in your terminal
2. Review the environment configuration
3. Check the GitHub Actions workflow logs
4. Create an issue in the repository
