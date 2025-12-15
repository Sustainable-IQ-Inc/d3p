#!/bin/bash

# Script to clean up old Google Cloud Secret Manager versions
# This helps reduce costs by keeping only the most recent versions
# Usage: ./cleanup-secret-versions.sh [PROJECT_ID] [KEEP_VERSIONS]

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

# Get parameters
PROJECT_ID=${1:-""}
KEEP_VERSIONS=${2:-2}

# Prompt for project ID if not provided
if [ -z "$PROJECT_ID" ]; then
    read -p "Enter GCP Project ID: " PROJECT_ID
fi

# Validate project ID
if [ -z "$PROJECT_ID" ]; then
    print_error "Project ID is required"
    exit 1
fi

print_info "Cleaning up secret versions in project: $PROJECT_ID"
print_info "Keeping the latest $KEEP_VERSIONS version(s) of each secret"
echo ""

# Confirm before proceeding
read -p "Do you want to continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Cancelled"
    exit 0
fi

echo ""

# Get all secrets
secrets=$(gcloud secrets list --project="$PROJECT_ID" --format="value(name)" 2>/dev/null)

if [ -z "$secrets" ]; then
    print_warning "No secrets found in project $PROJECT_ID"
    exit 0
fi

total_deleted=0
total_kept=0

for secret in $secrets; do
    print_info "Processing: $secret"
    
    # Get total number of versions
    total_versions=$(gcloud secrets versions list "$secret" \
        --project="$PROJECT_ID" \
        --format="value(name)" \
        --filter="state=ENABLED" \
        2>/dev/null | wc -l | tr -d ' ')
    
    if [ "$total_versions" -le "$KEEP_VERSIONS" ]; then
        print_success "  $secret has $total_versions version(s) - keeping all"
        total_kept=$((total_kept + total_versions))
        continue
    fi
    
    # Get all versions except the latest $KEEP_VERSIONS
    versions_to_delete=$(gcloud secrets versions list "$secret" \
        --project="$PROJECT_ID" \
        --format="value(name)" \
        --filter="state=ENABLED" \
        --sort-by="~createTime" \
        2>/dev/null | tail -n +$((KEEP_VERSIONS + 1)))
    
    deleted_count=0
    for version in $versions_to_delete; do
        gcloud secrets versions destroy "$version" \
            --secret="$secret" \
            --project="$PROJECT_ID" \
            --quiet 2>/dev/null
        deleted_count=$((deleted_count + 1))
    done
    
    if [ "$deleted_count" -gt 0 ]; then
        print_success "  Deleted $deleted_count old version(s), kept $KEEP_VERSIONS"
        total_deleted=$((total_deleted + deleted_count))
        total_kept=$((total_kept + KEEP_VERSIONS))
    fi
done

echo ""
print_info "Summary:"
print_success "  Total versions deleted: $total_deleted"
print_success "  Total versions kept: $total_kept"
echo ""
print_info "You can run this script periodically to keep secret costs down"

