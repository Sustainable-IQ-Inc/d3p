#Base Image to use
FROM python:3.11

#Expose port 8080
EXPOSE 8080

#Optional - install git to fetch packages directly from github
RUN apt-get update && apt-get install -y git

# Upgrade pip to latest version to ensure proper dependency resolution
RUN pip install --upgrade pip

#Copy Requirements.txt file into app directory
COPY requirements.txt app/requirements.txt

#install all requirements in requirements.txt
RUN pip install -r app/requirements.txt

#Copy all files in current directory into app directory
COPY . /app

# Copy backend dependencies if available (works for both local and deployment)
# Create target directory
RUN mkdir -p /app/backend_dependencies

# Use shell to conditionally copy backend dependencies after changing to /app
RUN cd /app && if [ -d "backend/dependencies" ]; then \
        cp -r backend/dependencies/* backend_dependencies/; \
        echo "Backend dependencies copied"; \
    else \
        echo "Backend dependencies not found - using fallback"; \
    fi

#Change Working Directory to app directory
WORKDIR /app

#Run the application on port 8080
ENTRYPOINT ["streamlit", "run", "d3p-dataview.py", "--server.port=8080", "--server.address=0.0.0.0"]
