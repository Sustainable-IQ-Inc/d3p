FROM ubuntu:latest

# Install dependencies, Python3, pip3, and ClamAV
RUN apt-get update && apt-get install -y \
    clamav \
    clamav-daemon \
    python3 \
    python3-pip \
    python3-flask \
    && rm -rf /var/lib/apt/lists/*

# Update the ClamAV database
RUN freshclam

# Copy the scan script and Flask app
COPY scan.sh /usr/local/bin/scan.sh
COPY app.py /usr/local/bin/app.py

# Make the scan script executable
RUN chmod +x /usr/local/bin/scan.sh

# Expose port 8080
EXPOSE 8080

# Define the entrypoint script
ENTRYPOINT ["python3", "/usr/local/bin/app.py"]
