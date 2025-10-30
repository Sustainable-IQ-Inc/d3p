#Base Image to use
FROM python:3.11


ENV env_use=local
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

#Change Working Directory to app directory
WORKDIR /app


# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable



CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
