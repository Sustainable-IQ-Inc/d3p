import os

import logging 

#now we will Create and configure logger 
logging.basicConfig(filename="std.log", 
                format='%(asctime)s %(message)s', 
                filemode='w') 

#Let us Create an object 
logger=logging.getLogger() 

#Now we are going to Set the threshold of logger to DEBUG 
logger.setLevel(logging.DEBUG) 

logging.getLogger('pdfplumber').setLevel(logging.WARNING)
logging.getLogger('pdfminer').setLevel(logging.WARNING)
logging.getLogger('pdfminer.pdfparser').setLevel(logging.WARNING)
logging.getLogger('pdfminer.pdfdocument').setLevel(logging.WARNING)
logging.getLogger('pdfminer.pdfpage').setLevel(logging.WARNING)
logging.getLogger('pdfminer.pdfinterp').setLevel(logging.WARNING)
logging.getLogger('pdfminer.converter').setLevel(logging.WARNING)
logging.getLogger('pdfminer.cmapdb').setLevel(logging.WARNING)
logging.getLogger('pdfminer.layout').setLevel(logging.WARNING) 


# Check if we're running locally
env = os.environ.get('ENV', 'local').lower()
is_local = env == 'local' or os.environ.get('env_use', '').lower() == 'local'

# Also check if we're running in Cloud Run (which sets K_SERVICE)
is_cloud_run = os.environ.get('K_SERVICE') is not None

if is_local and not is_cloud_run:
    logger.info("logging running locally - skipping Google Cloud Logging setup")
else:
    logger.info("logging running on cloud - setting up Google Cloud Logging")
    
    # Imports the Cloud Logging client library
    try:
        import google.cloud.logging

        # Instantiates a client
        client = google.cloud.logging.Client()

        # Retrieves a Cloud Logging handler based on the environment
        # you're running in and integrates the handler with the
        # Python logging module. By default this captures all logs
        # at INFO level and higher
        client.setup_logging()
        logger.info("Google Cloud Logging setup successful")
    except Exception as e:
        # Silently fail if Cloud Logging setup fails (e.g., in local dev without proper GCP credentials)
        # This prevents log noise from repeated connection attempts
        logger.warning(f"Google Cloud Logging setup failed (this is OK for local development): {str(e)}")
    
