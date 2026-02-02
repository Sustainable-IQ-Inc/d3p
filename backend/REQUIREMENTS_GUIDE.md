# Requirements Management Guide

## Overview

This project uses `requirements.in` to track **top-level dependencies** (packages we explicitly use) and `requirements.txt` as a **lockfile** with all resolved dependencies (including transitive ones).

## Files

- **`requirements.in`**: Minimal list of direct dependencies with version pins
- **`requirements.txt`**: Full lockfile generated from `requirements.in` (committed to repo)

## Usage

### Initial Setup

Install pip-tools:
```bash
pip install pip-tools
```

### Generate requirements.txt from requirements.in

```bash
cd backend
pip-compile requirements.in
```

This creates/updates `requirements.txt` with all dependencies resolved to compatible versions.

### Update a Specific Package

Edit the version in `requirements.in`, then regenerate:
```bash
pip-compile requirements.in
```

### Upgrade All Packages to Latest Compatible Versions

```bash
pip-compile --upgrade requirements.in
```

### Install from Lockfile (Production/CI)

```bash
pip install -r requirements.txt
```

### Install from Source + Sync (Development)

```bash
pip-sync requirements.txt
```

This installs packages from the lockfile **and removes** any packages not listed (keeps env clean).

## Benefits

✅ **Avoid conflicts**: Sub-packages (like `httpx`, `postgrest`, `gotrue`) are resolved by pip, not manually pinned  
✅ **Easy updates**: Change one line in `requirements.in`, run `pip-compile`  
✅ **Reproducible**: `requirements.txt` lockfile ensures same versions in dev/CI/prod  
✅ **Clear intent**: `requirements.in` shows what your code actually depends on

## Workflow

1. **Add a new dependency**: Add to `requirements.in` → run `pip-compile` → commit both files
2. **Update a dependency**: Edit version in `requirements.in` → run `pip-compile` → commit both files
3. **Deploy/CI**: Use `pip install -r requirements.txt` (lockfile)

## Dockerfile

Update your Dockerfile to use the lockfile:

```dockerfile
# Copy both files
COPY requirements.in requirements.txt app/

# Install from lockfile
RUN pip install -r app/requirements.txt
```

Or to compile during build (not recommended for production):

```dockerfile
COPY requirements.in app/
RUN pip install pip-tools && pip-compile app/requirements.in
RUN pip install -r app/requirements.txt
```

## Regenerating requirements.txt

After pulling changes that update `requirements.in`:

```bash
cd backend
pip-compile requirements.in
pip-sync requirements.txt  # Optional: sync your local env
```
