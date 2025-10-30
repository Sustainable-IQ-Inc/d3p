from google.cloud import storage
import logging_start
import os
from datetime import datetime,timedelta
import urllib.parse
import json
import base64

BUCKET_NAME = os.getenv('BUCKET_NAME')

# Get signing service account credentials from environment variable (base64 encoded)
SIGNING_SA_CREDENTIALS_BASE64 = os.getenv('SIGNING_SA_CREDENTIALS_BASE64')

def get_signing_client():
    """Get a storage client configured for signing URLs"""
    if SIGNING_SA_CREDENTIALS_BASE64:
        # Decode base64 encoded credentials and use service account credentials for signing
        try:
            credentials_json = base64.b64decode(SIGNING_SA_CREDENTIALS_BASE64).decode('utf-8')
            credentials_info = json.loads(credentials_json)
            return storage.Client.from_service_account_info(credentials_info)
        except Exception as e:
            print(f"Error decoding SIGNING_SA_CREDENTIALS_BASE64: {e}")
            # Fall back to default credentials (won't be able to sign URLs)
            return storage.Client()
    else:
        # Fall back to default credentials (won't be able to sign URLs)
        return storage.Client()

def get_signed_url_from_url(url, **kwargs):
    download_as = kwargs.get('download_as',None)
    parsed = urllib.parse.urlparse(url)
    blob_name = parsed.path[1:]
    folder = blob_name.split('/')[1]
    file_name = blob_name.split('/')[2]   
    blob_name = f"{folder}/{file_name}" 
    return generate_signed_url(blob_name,download_as=download_as)

def generate_signed_url(blob_name, **kwargs):
    download_as = kwargs.get('download_as',None)
    """Generates a v4 signed URL for downloading a blob.
    """
    headers = {}
    if download_as:
        headers['response_disposition'] = f'attachment; filename={download_as}'

    # Use signing client for URL generation
    signing_client = get_signing_client()
    bucket = signing_client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    # Generate signed URL - this will fail if signing credentials aren't available
    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 1 hour
        expiration=timedelta(hours=1),
        # Allow GET requests using this URL.
        method="GET",
        response_disposition=headers['response_disposition'] if download_as else None
    )
    print("Generated GET signed URL:")
    print(url)
    return url





def upload_blob(bucket_name, destination_blob_name, **kwargs):
    file_obj=kwargs.get('file_obj',None)
    source_file_name=kwargs.get('source_file_name',None)
    
   
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    # Use signing client for uploads to ensure proper authentication
    storage_client = get_signing_client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    if(file_obj):
        blob.upload_from_file(file_obj)
    elif(source_file_name):
        blob.upload_from_filename(source_file_name)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."

        
    )

    # Generate signed URL for the uploaded file
    signing_client = get_signing_client()
    bucket = signing_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    # Generate signed URL - this will fail if signing credentials aren't available
    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 1 hour
        expiration=timedelta(hours=1),
        # Allow GET requests using this URL.
        method="GET",
    )
    print(f"Generated signed URL: {url}")
    return url
    

#upload_blob(BUCKET_NAME, 'individual_scripts/bulk_upload_main_template.xlsx', 'temp_uploads/bulk_upload_main_template.xlsx')



def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    generation_match_precondition = None

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to delete is aborted if the object's
    # generation number does not match your precondition.
    blob.reload()  # Fetch blob metadata to use in generation_match_precondition.
    generation_match_precondition = blob.generation

    blob.delete(if_generation_match=generation_match_precondition)

    print(f"Blob {blob_name} deleted.")



#delete_blob('bem-reports.appspot.com','bulk_upload_main_template.xlsx')


#get_signed_url_from_url("https://storage.googleapis.com/bem-reports.appspot.com/report_uploads/e06e506d-4128-42a6-a3f0-c862b76b2111filename?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-file-upload%40bem-reports.iam.gserviceaccount.com%2F20240323%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20240323T162047Z&X-Goog-Expires=15&X-Goog-SignedHeaders=host&X-Goog-Signature=6afc9b08ac680589eb27ae963de48fa5cb9eae34ee06a809f791d6ad65fe352a3f47784a85eb704bd20b6cb856fb7afea0f853cf10c415ab6e2e9c3265ddca7016b9135c431086f1c831fe9b21e2e214b75dcd1837d7b3b688314299b1351b3176bed370a8bc465754521d9449ea7b6fec0d32c502b992f118b95980e89b9469f22275bd0df377369cf44624a92bb2a6f8963dfd749d896413f20c02b65e560ee0137397904c555f4db9974ee9e11f4d3baec6fca0801ba9c25ce4d886ee4a1f2791b19fffa97f6fa7ed7cd354051b8435be24aaa97d196eb129d9f99e165f6cad3dec2dd971b5b5a70cb91c61bf034ece2d6c4791a0cc35cdf1bbb019bbfb2b",download_as="filename.pdf")
print("gcs loaded")