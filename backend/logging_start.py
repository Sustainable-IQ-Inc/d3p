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

'''
try:
    if(os.environ['env_use']=="local"):
        logger.info("logging running locally") 
       



except:'''
logger.info("logging running on cloud") 

#importing the module 
    # Imports the Cloud Logging client library

import google.cloud.logging

# Instantiates a client
client = google.cloud.logging.Client()

# Retrieves a Cloud Logging handler based on the environment
# you're running in and integrates the handler with the
# Python logging module. By default this captures all logs
# at INFO level and higher
client.setup_logging()
    
