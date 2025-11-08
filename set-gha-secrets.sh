#!/bin/bash

# Script to set GitHub Actions secrets for BEM Reports project
# Prerequisites: GitHub CLI (gh) must be installed and authenticated
# Install: brew install gh
# Authenticate: gh auth login

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI (gh) is not installed."
    echo "Install it with: brew install gh"
    echo "Then authenticate with: gh auth login"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    print_error "Not authenticated with GitHub CLI."
    echo "Run: gh auth login"
    exit 1
fi

# Function to set a secret
set_secret() {
    local secret_name=$1
    local secret_value=$2
    
    if [ -z "$secret_value" ]; then
        print_warning "Skipping $secret_name (no value provided)"
        return
    fi
    
    echo "$secret_value" | gh secret set "$secret_name"
    print_success "Set $secret_name"
}

# Function to set a secret from file
set_secret_from_file() {
    local secret_name=$1
    local file_path=$2
    
    if [ ! -f "$file_path" ]; then
        print_warning "Skipping $secret_name (file not found: $file_path)"
        return
    fi
    
    gh secret set "$secret_name" < "$file_path"
    print_success "Set $secret_name from $file_path"
}

# Function to set a secret from base64 encoded file
set_secret_from_file_base64() {
    local secret_name=$1
    local file_path=$2
    
    if [ ! -f "$file_path" ]; then
        print_warning "Skipping $secret_name (file not found: $file_path)"
        return
    fi
    
    base64 -i "$file_path" | tr -d '\n' | gh secret set "$secret_name"
    print_success "Set $secret_name from base64 encoded $file_path"
}

# Function to prompt for value
prompt_for_value() {
    local prompt_text=$1
    local default_value=$2
    local value=""
    
    if [ -n "$default_value" ]; then
        read -p "$prompt_text [$default_value]: " value
        value=${value:-$default_value}
    else
        read -p "$prompt_text: " value
    fi
    
    echo "$value"
}

# Main menu
echo ""
print_info "GitHub Actions Secrets Setup for BEM Reports"
echo ""
echo "What would you like to do?"
echo "1) Set all secrets (interactive)"
echo "2) Set common secrets only"
echo "3) Set staging secrets only"
echo "4) Set production secrets only"
echo "5) Set secrets from environment file"
echo "6) Exit"
echo ""
read -p "Choose an option [1-6]: " choice

case $choice in
    1)
        print_info "Setting all secrets interactively..."
        echo ""
        
        # Common secrets
        print_info "=== Common Secrets ==="
        echo ""
        
        # GCP_SA_KEY
        read -p "Path to key.json file [./key.json]: " key_file
        key_file=${key_file:-./key.json}
        if [ -f "$key_file" ]; then
            set_secret_from_file "GCP_SA_KEY" "$key_file"
        else
            print_warning "key.json not found at $key_file"
        fi
        
        # GCP_PROJECT_ID
        gcp_project=$(prompt_for_value "GCP Project ID")
        set_secret "GCP_PROJECT_ID" "$gcp_project"
        
        # SIGNING_SA_CREDENTIALS
        read -p "Path to signing-key.json file [./signing-key.json]: " signing_key_file
        signing_key_file=${signing_key_file:-./signing-key.json}
        if [ -f "$signing_key_file" ]; then
            set_secret_from_file_base64 "SIGNING_SA_CREDENTIALS" "$signing_key_file"
        else
            print_warning "signing-key.json not found at $signing_key_file"
        fi
        
        echo ""
        print_info "=== Staging Environment Secrets ==="
        echo ""
        
        staging_supabase_url=$(prompt_for_value "Staging Supabase URL")
        set_secret "STAGING_SUPABASE_URL" "$staging_supabase_url"
        
        staging_service_role=$(prompt_for_value "Staging Supabase Service Role Key")
        set_secret "STAGING_SUPABASE_SERVICE_ROLE" "$staging_service_role"
        
        staging_anon_key=$(prompt_for_value "Staging Supabase Anon Key")
        set_secret "STAGING_SUPABASE_ANON_KEY" "$staging_anon_key"
        
        staging_encryption_key=$(prompt_for_value "Staging Encryption Key (32 chars)")
        set_secret "STAGING_ENCRYPTION_KEY" "$staging_encryption_key"
        
        staging_encryption_salt=$(prompt_for_value "Staging Encryption Salt (16 chars)")
        set_secret "STAGING_ENCRYPTION_SALT" "$staging_encryption_salt"
        
        staging_bucket_name=$(prompt_for_value "Staging GCS Bucket Name")
        set_secret "STAGING_BUCKET_NAME" "$staging_bucket_name"
        
        staging_project_id=$(prompt_for_value "Staging Supabase Project ID")
        set_secret "STAGING_SUPABASE_PROJECT_ID" "$staging_project_id"
        
        staging_access_token=$(prompt_for_value "Staging Supabase Access Token")
        set_secret "STAGING_SUPABASE_ACCESS_TOKEN" "$staging_access_token"
        
        staging_db_password=$(prompt_for_value "Staging Supabase DB Password")
        set_secret "STAGING_SUPABASE_DB_PASSWORD" "$staging_db_password"
        
        read -p "Set optional staging DDX API URL? (y/n): " set_staging_ddx
        if [ "$set_staging_ddx" = "y" ]; then
            staging_ddx_url=$(prompt_for_value "Staging DDX API Base URL")
            set_secret "STAGING_DDX_API_BASE_URL" "$staging_ddx_url"
        fi
        
        read -p "Set optional staging redirect URL? (y/n): " set_staging_redirect
        if [ "$set_staging_redirect" = "y" ]; then
            staging_redirect=$(prompt_for_value "Staging Redirect URL")
            set_secret "STAGING_REDIRECT_URL" "$staging_redirect"
        fi
        
        echo ""
        print_info "=== Production Environment Secrets ==="
        echo ""
        
        prod_supabase_url=$(prompt_for_value "Production Supabase URL")
        set_secret "PROD_SUPABASE_URL" "$prod_supabase_url"
        
        prod_service_role=$(prompt_for_value "Production Supabase Service Role Key")
        set_secret "PROD_SUPABASE_SERVICE_ROLE" "$prod_service_role"
        
        prod_anon_key=$(prompt_for_value "Production Supabase Anon Key")
        set_secret "PROD_SUPABASE_ANON_KEY" "$prod_anon_key"
        
        prod_encryption_key=$(prompt_for_value "Production Encryption Key (32 chars)")
        set_secret "PROD_ENCRYPTION_KEY" "$prod_encryption_key"
        
        prod_encryption_salt=$(prompt_for_value "Production Encryption Salt (16 chars)")
        set_secret "PROD_ENCRYPTION_SALT" "$prod_encryption_salt"
        
        prod_bucket_name=$(prompt_for_value "Production GCS Bucket Name")
        set_secret "PROD_BUCKET_NAME" "$prod_bucket_name"
        
        prod_project_id=$(prompt_for_value "Production Supabase Project ID")
        set_secret "PROD_SUPABASE_PROJECT_ID" "$prod_project_id"
        
        prod_access_token=$(prompt_for_value "Production Supabase Access Token")
        set_secret "PROD_SUPABASE_ACCESS_TOKEN" "$prod_access_token"
        
        prod_db_password=$(prompt_for_value "Production Supabase DB Password")
        set_secret "PROD_SUPABASE_DB_PASSWORD" "$prod_db_password"
        
        read -p "Set optional production DDX API URL? (y/n): " set_prod_ddx
        if [ "$set_prod_ddx" = "y" ]; then
            prod_ddx_url=$(prompt_for_value "Production DDX API Base URL")
            set_secret "PROD_DDX_API_BASE_URL" "$prod_ddx_url"
        fi
        
        read -p "Set optional production redirect URL? (y/n): " set_prod_redirect
        if [ "$set_prod_redirect" = "y" ]; then
            prod_redirect=$(prompt_for_value "Production Redirect URL")
            set_secret "PROD_REDIRECT_URL" "$prod_redirect"
        fi
        
        echo ""
        print_success "All secrets have been set!"
        ;;
        
    2)
        print_info "Setting common secrets..."
        echo ""
        
        read -p "Path to key.json file [./key.json]: " key_file
        key_file=${key_file:-./key.json}
        set_secret_from_file "GCP_SA_KEY" "$key_file"
        
        gcp_project=$(prompt_for_value "GCP Project ID")
        set_secret "GCP_PROJECT_ID" "$gcp_project"
        
        read -p "Path to signing-key.json file [./signing-key.json]: " signing_key_file
        signing_key_file=${signing_key_file:-./signing-key.json}
        set_secret_from_file_base64 "SIGNING_SA_CREDENTIALS" "$signing_key_file"
        
        print_success "Common secrets have been set!"
        ;;
        
    3)
        print_info "Setting staging secrets..."
        echo ""
        
        staging_supabase_url=$(prompt_for_value "Staging Supabase URL")
        set_secret "STAGING_SUPABASE_URL" "$staging_supabase_url"
        
        staging_service_role=$(prompt_for_value "Staging Supabase Service Role Key")
        set_secret "STAGING_SUPABASE_SERVICE_ROLE" "$staging_service_role"
        
        staging_anon_key=$(prompt_for_value "Staging Supabase Anon Key")
        set_secret "STAGING_SUPABASE_ANON_KEY" "$staging_anon_key"
        
        staging_encryption_key=$(prompt_for_value "Staging Encryption Key (32 chars)")
        set_secret "STAGING_ENCRYPTION_KEY" "$staging_encryption_key"
        
        staging_encryption_salt=$(prompt_for_value "Staging Encryption Salt (16 chars)")
        set_secret "STAGING_ENCRYPTION_SALT" "$staging_encryption_salt"
        
        staging_bucket_name=$(prompt_for_value "Staging GCS Bucket Name")
        set_secret "STAGING_BUCKET_NAME" "$staging_bucket_name"
        
        staging_project_id=$(prompt_for_value "Staging Supabase Project ID")
        set_secret "STAGING_SUPABASE_PROJECT_ID" "$staging_project_id"
        
        staging_access_token=$(prompt_for_value "Staging Supabase Access Token")
        set_secret "STAGING_SUPABASE_ACCESS_TOKEN" "$staging_access_token"
        
        staging_db_password=$(prompt_for_value "Staging Supabase DB Password")
        set_secret "STAGING_SUPABASE_DB_PASSWORD" "$staging_db_password"
        
        print_success "Staging secrets have been set!"
        ;;
        
    4)
        print_info "Setting production secrets..."
        echo ""
        
        prod_supabase_url=$(prompt_for_value "Production Supabase URL")
        set_secret "PROD_SUPABASE_URL" "$prod_supabase_url"
        
        prod_service_role=$(prompt_for_value "Production Supabase Service Role Key")
        set_secret "PROD_SUPABASE_SERVICE_ROLE" "$prod_service_role"
        
        prod_anon_key=$(prompt_for_value "Production Supabase Anon Key")
        set_secret "PROD_SUPABASE_ANON_KEY" "$prod_anon_key"
        
        prod_encryption_key=$(prompt_for_value "Production Encryption Key (32 chars)")
        set_secret "PROD_ENCRYPTION_KEY" "$prod_encryption_key"
        
        prod_encryption_salt=$(prompt_for_value "Production Encryption Salt (16 chars)")
        set_secret "PROD_ENCRYPTION_SALT" "$prod_encryption_salt"
        
        prod_bucket_name=$(prompt_for_value "Production GCS Bucket Name")
        set_secret "PROD_BUCKET_NAME" "$prod_bucket_name"
        
        prod_project_id=$(prompt_for_value "Production Supabase Project ID")
        set_secret "PROD_SUPABASE_PROJECT_ID" "$prod_project_id"
        
        prod_access_token=$(prompt_for_value "Production Supabase Access Token")
        set_secret "PROD_SUPABASE_ACCESS_TOKEN" "$prod_access_token"
        
        prod_db_password=$(prompt_for_value "Production Supabase DB Password")
        set_secret "PROD_SUPABASE_DB_PASSWORD" "$prod_db_password"
        
        print_success "Production secrets have been set!"
        ;;
        
    5)
        print_info "Setting secrets from environment file..."
        read -p "Path to environment file: " env_file
        
        if [ ! -f "$env_file" ]; then
            print_error "File not found: $env_file"
            exit 1
        fi
        
        # Source the file and set secrets
        source "$env_file"
        
        # Common secrets
        [ -n "$GCP_SA_KEY_FILE" ] && set_secret_from_file "GCP_SA_KEY" "$GCP_SA_KEY_FILE"
        [ -n "$GCP_PROJECT_ID" ] && set_secret "GCP_PROJECT_ID" "$GCP_PROJECT_ID"
        [ -n "$SIGNING_SA_KEY_FILE" ] && set_secret_from_file_base64 "SIGNING_SA_CREDENTIALS" "$SIGNING_SA_KEY_FILE"
        
        # Staging secrets
        [ -n "$STAGING_SUPABASE_URL" ] && set_secret "STAGING_SUPABASE_URL" "$STAGING_SUPABASE_URL"
        [ -n "$STAGING_SUPABASE_SERVICE_ROLE" ] && set_secret "STAGING_SUPABASE_SERVICE_ROLE" "$STAGING_SUPABASE_SERVICE_ROLE"
        [ -n "$STAGING_SUPABASE_ANON_KEY" ] && set_secret "STAGING_SUPABASE_ANON_KEY" "$STAGING_SUPABASE_ANON_KEY"
        [ -n "$STAGING_ENCRYPTION_KEY" ] && set_secret "STAGING_ENCRYPTION_KEY" "$STAGING_ENCRYPTION_KEY"
        [ -n "$STAGING_ENCRYPTION_SALT" ] && set_secret "STAGING_ENCRYPTION_SALT" "$STAGING_ENCRYPTION_SALT"
        [ -n "$STAGING_BUCKET_NAME" ] && set_secret "STAGING_BUCKET_NAME" "$STAGING_BUCKET_NAME"
        [ -n "$STAGING_SUPABASE_PROJECT_ID" ] && set_secret "STAGING_SUPABASE_PROJECT_ID" "$STAGING_SUPABASE_PROJECT_ID"
        [ -n "$STAGING_SUPABASE_ACCESS_TOKEN" ] && set_secret "STAGING_SUPABASE_ACCESS_TOKEN" "$STAGING_SUPABASE_ACCESS_TOKEN"
        [ -n "$STAGING_SUPABASE_DB_PASSWORD" ] && set_secret "STAGING_SUPABASE_DB_PASSWORD" "$STAGING_SUPABASE_DB_PASSWORD"
        [ -n "$STAGING_DDX_API_BASE_URL" ] && set_secret "STAGING_DDX_API_BASE_URL" "$STAGING_DDX_API_BASE_URL"
        [ -n "$STAGING_REDIRECT_URL" ] && set_secret "STAGING_REDIRECT_URL" "$STAGING_REDIRECT_URL"
        
        # Production secrets
        [ -n "$PROD_SUPABASE_URL" ] && set_secret "PROD_SUPABASE_URL" "$PROD_SUPABASE_URL"
        [ -n "$PROD_SUPABASE_SERVICE_ROLE" ] && set_secret "PROD_SUPABASE_SERVICE_ROLE" "$PROD_SUPABASE_SERVICE_ROLE"
        [ -n "$PROD_SUPABASE_ANON_KEY" ] && set_secret "PROD_SUPABASE_ANON_KEY" "$PROD_SUPABASE_ANON_KEY"
        [ -n "$PROD_ENCRYPTION_KEY" ] && set_secret "PROD_ENCRYPTION_KEY" "$PROD_ENCRYPTION_KEY"
        [ -n "$PROD_ENCRYPTION_SALT" ] && set_secret "PROD_ENCRYPTION_SALT" "$PROD_ENCRYPTION_SALT"
        [ -n "$PROD_BUCKET_NAME" ] && set_secret "PROD_BUCKET_NAME" "$PROD_BUCKET_NAME"
        [ -n "$PROD_SUPABASE_PROJECT_ID" ] && set_secret "PROD_SUPABASE_PROJECT_ID" "$PROD_SUPABASE_PROJECT_ID"
        [ -n "$PROD_SUPABASE_ACCESS_TOKEN" ] && set_secret "PROD_SUPABASE_ACCESS_TOKEN" "$PROD_SUPABASE_ACCESS_TOKEN"
        [ -n "$PROD_SUPABASE_DB_PASSWORD" ] && set_secret "PROD_SUPABASE_DB_PASSWORD" "$PROD_SUPABASE_DB_PASSWORD"
        [ -n "$PROD_DDX_API_BASE_URL" ] && set_secret "PROD_DDX_API_BASE_URL" "$PROD_DDX_API_BASE_URL"
        [ -n "$PROD_REDIRECT_URL" ] && set_secret "PROD_REDIRECT_URL" "$PROD_REDIRECT_URL"
        
        print_success "Secrets from environment file have been set!"
        ;;
        
    6)
        print_info "Exiting..."
        exit 0
        ;;
        
    *)
        print_error "Invalid option"
        exit 1
        ;;
esac

echo ""
print_info "You can view your secrets at: https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/settings/secrets/actions"

