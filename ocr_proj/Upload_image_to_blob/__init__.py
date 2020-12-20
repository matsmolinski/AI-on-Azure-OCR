import logging
import os
import uuid

import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Received request to post image')

    files_len = len(req.files.to_dict().items())
    connect_str=os.environ["AzureWebJobsStorage"]
    container=os.environ["ContainerName"]
    
    if files_len == 0:
        logging.error('Missing file in form-data body')
        return func.HttpResponse(
            f'Missing file in form-data body',
            status_code=406
            )
    
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    for input_file in req.files.values():
        extension = input_file.filename.split('.')[1]
        file_uuid = str(uuid.uuid4())
        logging.info('Adding file to blob storage...')

        blob_client = blob_service_client.get_blob_client(container=container,blob=file_uuid + "." + extension)
        blob_client.upload_blob(input_file)
        logging.info('File added')

    return func.HttpResponse(
        f'File added for processing',
        status_code=200
        )
