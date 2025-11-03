# Deploy to Your Own GCP Project

This guide will help you deploy the D3P BEM Reports platform to your own Google Cloud Platform project using GitHub Actions.

## Quick Setup

### 1. Fork this repository

Click the "Fork" button on GitHub to create your own copy of this repository.

### 2. Set up your GCP project

1. **Create a new GCP project** (or use an existing one)
2. **Enable billing** on your project
3. **Enable these APIs**:
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable secretmanager.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   gcloud services enable cloudresourcemanager.googleapis.com
   ```

### 3. Create a Service Account

Create a service account with the necessary permissions:

```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Create service accounts
gcloud iam service-accounts create bem-reports-deployer \
  --display-name="BEM Reports Deployer" \
  --project=$PROJECT_ID

gcloud iam service-accounts create bem-reports-signer \
  --display-name="BEM Reports URL Signer" \
  --project=$PROJECT_ID

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:bem-reports-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:bem-reports-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:bem-reports-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:bem-reports-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Grant permissions to the signing service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:bem-reports-signer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"


gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:bem-reports-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Get project number and grant permission to act as the Compute Engine default service account
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud iam service-accounts add-iam-policy-binding \
  "${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --member="serviceAccount:bem-reports-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser" \
  --project=$PROJECT_ID

# Grant the Compute Engine default service account access to Secret Manager and Storage
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Create and download key 
# ⚠️ **WARNING**: Do **NOT** add these `*.json` files to git or commit them to your repository at any time.  
# These files must remain private. They contains credentials that allow access to your GCP project.  
# Make sure your `.gitignore` lists these files and you do not upload it anywhere public.

# Create and download deployment key 
gcloud iam service-accounts keys create key.json \
  --iam-account=bem-reports-deployer@$PROJECT_ID.iam.gserviceaccount.com \
  --project=$PROJECT_ID

# Create and download signing service account key
gcloud iam service-accounts keys create signing-key.json \
  --iam-account=bem-reports-signer@$PROJECT_ID.iam.gserviceaccount.com \
  --project=$PROJECT_ID
```

### 4. Set up Supabase

1. **Create a Supabase project** at [supabase.com](https://supabase.com)
  - Keep track of your DB Password to be stored as a GitHub Actions secret
2. **Get your project credentials**:
   - Project URL
   - Anon key (public)
   - Service role key (secret)
   - Personal Access Token (Under Account Preferences)

3. **Install Supabase CLI locally**:
   ```bash
   # Install Supabase CLI
   npm install -g supabase
   # or using Homebrew on macOS
   brew install supabase/tap/supabase
   ```

4. **Set up your local Supabase environment**:
   ```bash
   # Navigate to the backend directory where Supabase is configured
   cd backend
   
   # Start local Supabase instance
   supabase start
   
   # Link to your remote Supabase project
   supabase link --project-ref YOUR_PROJECT_ID
   
   # Push database schema and run migrations
   supabase db push
   ```
   
   **Note**: The `supabase db push` command will:
   - Run all database migrations from the `backend/supabase/migrations/` directory
   - Apply the complete database schema including tables, views, functions, and RLS policies
   - Seed the database with starting enum data (energy codes, climate zones, etc.) from the seed files
   - Set up all the necessary database structure for the BEM Reports application

5. **Configure Email Settings**:
   
   Go to your Supabase project dashboard → Authentication → Email Templates and configure:

   **Invite User Template**:
   ```html
   <h2>You have been invited</h2>


   <p>You’ve been invited to join {{ .Data.company_name }}  on DOE/LBNL’s D3P (Deep Design Data Portal). Click the link to accept:</p>
   <p><a href="{{ .ConfirmationURL }}">Accept</a></p>

   <i>Experience how deep design data can inform design decisions...</i>
   ```

   **Magic Link Template**:
   ```html
   <h2>Magic Link</h2>
   
   <p>Follow this link to login to your company account on DOE/LBNL's D3P Deep Design Data Portal.</p>
   <p><a href="{{ .ConfirmationURL }}">Log In</a></p>
   ```

   **Configure SMTP Settings**:
   - Go to Authentication → Settings → SMTP Settings
   - **Note**: Supabase has built-in SMTP, but the limits are very low and emails will likely get flagged as spam
   - Configure your own SMTP provider (SendGrid, Resend, etc.) for testing and production usage.

6. **Configure URL Settings**:
   
   Go to your Supabase project dashboard → Authentication → Settings and configure:

   **Site URL**:
   - Set to your frontend service URL (e.g., `https://your-frontend-domain.com`)
   - This is the URL where users will be redirected after authentication


  **Redirect URLs**:
  - Add your frontend authentication callback URL: `https://your-frontend-domain.com/callback`
  - Add your frontend email confirmation URL: `https://your-frontend-domain.com/auth/confirm`
  - Add local development callback URL: `http://localhost:3000/callback`
  - Add local development email confirmation URL: `http://localhost:3000/auth/confirm`
  - Add any other URLs where users should be redirected after authentication
  - **Note**: These URLs must be explicitly allowed for security reasons

  **Multiple Environments**:
  - **Repeat this entire Supabase setup process for each environment** (staging, production, etc.) as desired
  - Each environment should have its own Supabase project with the same configuration
  - Update the GitHub Secrets with the appropriate Supabase credentials for each environment

  



### 5. Set up Artifact Registry

Create an Artifact Registry repository for storing Docker images:

```bash
# Create the repository
gcloud artifacts repositories create bem-reports \
  --repository-format=docker \
  --location=us-central1 \
  --description="Docker repository for BEM Reports" \
  --project=$PROJECT_ID
```

### 6. Set up Google Cloud Storage

1. **Create a GCS bucket** for file storage:
   ```bash
   gsutil mb gs://your-bucket-name
   ```
2. **Note the bucket name** for later use

3. **Grant permissions to the signing service account**:
   
   The signing service account needs permissions to create objects, view objects, and generate signed URLs. You can grant these permissions individually or all at once:
   
   **Option 1: Grant all permissions at once (recommended)**:
   ```bash
   gsutil iam ch serviceAccount:bem-reports-signer@$PROJECT_ID.iam.gserviceaccount.com:objectCreator,objectViewer,objectAdmin gs://your-bucket-name
   ```
   
   **Option 2: Grant permissions individually**:
   ```bash
   # Grant object creation permissions
   gsutil iam ch serviceAccount:bem-reports-signer@$PROJECT_ID.iam.gserviceaccount.com:objectCreator gs://your-bucket-name
   
   # Grant object viewing permissions (needed for signed URLs)
   gsutil iam ch serviceAccount:bem-reports-signer@$PROJECT_ID.iam.gserviceaccount.com:objectViewer gs://your-bucket-name
   
   # Grant object admin permissions (full access for signed URLs)
   gsutil iam ch serviceAccount:bem-reports-signer@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://your-bucket-name
   ```

   **Important**: Replace `your-bucket-name` with your actual bucket name (e.g., `bem-reports.appspot.com`).
   
   **Troubleshooting**: If you get a 403 error when uploading files that mentions "does not have storage.objects.create access", run the above commands again to ensure permissions are properly set.

4. **Create a GCS bucket for seed files** (optional but recommended):
   
   The deployment workflow can download an optional seed file from GCS to populate your database. This is especially useful for provisioning test or demo environments with example data, including test user login credentials and sample datasets, so that you can immediately log in as a demo user and view realistic data within d3p. 
   
   ```bash
   # Create the seed_files bucket
   gsutil mb gs://seed_files
   
   # Grant permissions to the deployment service account to read seed files
   gsutil iam ch serviceAccount:bem-reports-deployer@$PROJECT_ID.iam.gserviceaccount.com:objectViewer gs://seed_files
   ```
   
5. **Upload your seed file** (optional):
   
   If you have a `seed.staging.sql` file that you want to use for database seeding during deployment:
   
   ```bash
   # Upload your seed file to the bucket
   gsutil cp path/to/seed.staging.sql gs://seed_files/seed.staging.sql
   ```
   
   **Note**: 
   - The deployment workflow will attempt to download `seed.staging.sql` from the `seed_files` bucket
   - If the file doesn't exist, the deployment will continue without it (the step is non-blocking)
   - The downloaded seed file will be saved as `backend/supabase/seeds/seed.local.sql` and used during database deployment
   - The seed file from GCS is used for both staging and production environments if provided
   - If no seed file is uploaded to GCS, the deployment will use the seed files from the repository (`backend/supabase/seeds/seed.sql`)

### 7. Generate Encryption Keys

Generate secure encryption keys for data protection which will be used for GitHub secrets in the next step:

```bash
# Generate 32-character encryption key
openssl rand -base64 32

# Generate 16-character salt
openssl rand -base64 12
```

### 8. Set up GitHub Secrets

Go to your forked repository → **Settings** → **Secrets and variables** → **Actions**

The deployment workflow uses environment-specific secrets to support separate staging and production deployments:

#### Common Secrets (used by both environments):
- `GCP_SA_KEY`: Contents of the `key.json` file from step 3
- `GCP_PROJECT_ID`: Your GCP project ID
- `SIGNING_SA_CREDENTIALS`: Base64 encoded contents of the `signing-key.json` file (shared across environments)
  - **Important**: Encode the file before adding to GitHub: `base64 -w 0 signing-key.json`

#### Staging Environment Secrets:
- `STAGING_SUPABASE_URL`: Your staging Supabase project URL
- `STAGING_SUPABASE_SERVICE_ROLE`: Your staging Supabase service role key
- `STAGING_SUPABASE_ANON_KEY`: Your staging Supabase anon key
- `STAGING_ENCRYPTION_KEY`: The 32-character encryption key for staging
- `STAGING_ENCRYPTION_SALT`: The 16-character salt for staging
- `STAGING_BUCKET_NAME`: Your staging GCS bucket name
- `STAGING_SUPABASE_PROJECT_ID`: Your staging Supabase project ID
- `STAGING_SUPABASE_ACCESS_TOKEN`: Your staging Supabase personal access token (from Account Preferences)
- `STAGING_SUPABASE_DB_PASSWORD`: Your staging Supabase database password

#### Production Environment Secrets:
- `PROD_SUPABASE_URL`: Your production Supabase project URL
- `PROD_SUPABASE_SERVICE_ROLE`: Your production Supabase service role key
- `PROD_SUPABASE_ANON_KEY`: Your production Supabase anon key
- `PROD_ENCRYPTION_KEY`: The 32-character encryption key for production
- `PROD_ENCRYPTION_SALT`: The 16-character salt for production
- `PROD_BUCKET_NAME`: Your production GCS bucket name
- `PROD_SUPABASE_ACCESS_TOKEN`: Your production Supabase personal access token (from Account Preferences)
- `PROD_SUPABASE_DB_PASSWORD`: Your production Supabase database password



#### Optional Secrets (both environments):
- `STAGING_DDX_API_BASE_URL` / `PROD_DDX_API_BASE_URL`: DDX API URL (if using DDX integration)
- `STAGING_REDIRECT_URL` / `PROD_REDIRECT_URL`: (Optional) Override the default frontend URL. If not provided, will be auto-generated as `https://{environment}-bem-reports-web-{project-number}.us-central1.run.app`

### 9. Update the Example Workflow

Edit `.github/workflows/deploy-example.yml` and replace `'my-gcp-project-id'` with your actual GCP project ID.

### 9.5. Commit Your Changes

Commit the updated workflow file to your repository

### 10. Deploy!

The deployment workflow automatically selects the correct secrets based on the branch:

#### Automatic Deployment:
- **Push to `staging` branch** → Uses `STAGING_*` secrets → Deploys to staging environment
- **Push to `main` branch** → Uses `PROD_*` secrets → Deploys to production environment

#### Manual Deployment:
1. Go to the **Actions** tab in your repository
2. Select **"Deploy Cloud Run Services"**
3. Click **"Run workflow"**
4. Choose which services to deploy (frontend/backend/visualizer)
5. Click **"Run workflow"**

The workflow will automatically use the appropriate environment secrets based on your current branch.

### 11. Access your services

After deployment, you'll see the service URLs in the workflow output. The services will be automatically generated based on your project number:
- **Backend**: `https://{environment}-bem-reports-{project-number}.us-central1.run.app`
- **Frontend**: `https://{environment}-bem-reports-web-{project-number}.us-central1.run.app` (or your custom `REDIRECT_URL`)
- **Visualizer**: `https://{environment}-d3p-viewer-{project-number}.us-central1.run.app`

## URL Pattern

Your service URLs will be automatically generated based on your GCP project number:
```
https://{environment}-{service-name}-{project-number}.us-central1.run.app
```

Where:
- `{environment}`: `staging` or `prod`
- `{service-name}`: `bem-reports`, `bem-reports-web`, or `d3p-viewer`
- `{project-number}`: Your GCP project number (12 digits)

**Example URLs** (for project number `123456789012`):
- Backend: `https://staging-bem-reports-123456789012.us-central1.run.app`
- Frontend: `https://staging-bem-reports-web-123456789012.us-central1.run.app`
- Visualizer: `https://staging-d3p-viewer-123456789012.us-central1.run.app`

To find your project number:
```bash
gcloud projects describe your-project-id --format="value(projectNumber)"
```

**Note**: You can override the frontend URL by providing a `REDIRECT_URL` secret, but the backend and visualizer URLs are always auto-generated.

## Local Development

For local development, use the `.env` files as documented in the main README:

1. Copy example files:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.local.example frontend/.env.local
   cp visualizer/.env.example visualizer/.env
   ```

2. Edit with your local values

3. Run: `./start-dev.sh`

## Troubleshooting

### Common Issues:

1. **"Permission denied" errors**: Ensure your service account has all required roles
2. **"Secret not found" errors**: Check that all required GitHub secrets are set with the correct naming convention:
   - Staging: `STAGING_*` secrets
   - Production: `PROD_*` secrets
   - Common: `GCP_SA_KEY`, `GCP_PROJECT_ID`
3. **"Service already exists" errors**: This is normal for updates
4. **"Build failed" errors**: Check that your Docker images build locally
5. **Environment mismatch**: Make sure you're using the correct branch:
   - `staging` branch → Uses `STAGING_*` secrets
   - `main` branch → Uses `PROD_*` secrets

### Getting Help:

1. Check the GitHub Actions logs for detailed error messages
2. Ensure all required APIs are enabled in your GCP project
3. Verify your service account has the correct permissions
4. Make sure all GitHub secrets are set correctly

## Troubleshooting Common Issues

### File Upload Errors (500 Internal Server Error)

If you encounter 500 errors when uploading files, check these common issues:

#### 1. Malformed JSON in SIGNING_SA_CREDENTIALS
**Error**: `json.loads()` fails when parsing `SIGNING_SA_CREDENTIALS`

**Solution**: Ensure your `signing-key.json` file is valid JSON with proper quotes:
```bash
# Check if the secret is valid JSON
gcloud secrets versions access latest --secret="staging_SIGNING_SA_CREDENTIALS" --project=YOUR_PROJECT_ID | jq .
```

If the JSON is malformed, update the secret:
```bash
gcloud secrets versions add staging_SIGNING_SA_CREDENTIALS --data-file=signing-key.json --project=YOUR_PROJECT_ID
```

#### 2. Missing GCS Permissions
**Error**: `Permission 'storage.objects.create' denied`

**Solution**: Grant the signing service account proper permissions:
```bash
# Replace YOUR_BUCKET_NAME with your actual bucket name
gsutil iam ch serviceAccount:bem-reports-signer@YOUR_PROJECT_ID.iam.gserviceaccount.com:objectCreator gs://YOUR_BUCKET_NAME
gsutil iam ch serviceAccount:bem-reports-signer@YOUR_PROJECT_ID.iam.gserviceaccount.com:objectViewer gs://YOUR_BUCKET_NAME
gsutil iam ch serviceAccount:bem-reports-signer@YOUR_PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://YOUR_BUCKET_NAME
```

#### 3. Missing SIGNING_SA_CREDENTIALS in Workflow
**Error**: `Secret SIGNING_SA_CREDENTIALS is required, but not provided`

**Solution**: Ensure your `.github/workflows/deploy-example.yml` includes the `SIGNING_SA_CREDENTIALS` secret in the `secrets:` section.

### Service Account Authentication Issues

If you see authentication errors, verify:
1. The service account keys are correctly formatted JSON
2. The service account has the necessary IAM roles
3. The Cloud Run service is using the correct service account

## Security Notes

- Never commit your `key.json` file to the repository
- Use strong, unique encryption keys for each deployment
- Regularly rotate your service account keys
- Monitor your GCP usage and costs
- Use least-privilege access for your service account

## Cost Considerations

This deployment uses:
- **Cloud Run**: Pay per request (very cost-effective for low traffic)
- **Secret Manager**: Small cost per secret. It's recommended to delete old secret versions periodically.
- **Artifact Registry**: Storage costs for Docker images
- **Cloud Storage**: Storage costs for uploaded files

For development/testing, costs should be minimal. Monitor your GCP billing dashboard.
