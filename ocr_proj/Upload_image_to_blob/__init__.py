import logging
import os
import uuid
import re
import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Received request to post image')

    files_len = len(req.files.to_dict().items())
    connect_str=os.environ["AzureWebJobsStorage"]
    container=os.environ["ContainerName"]

    if files_len == 0:
        msg = 'Missing file in form-data body'
        logging.error(msg)
        return func.HttpResponse(msg, status_code=400)

    req_keys = req.form.keys()

    if 'email' not in req_keys:
        msg = 'Missing "email" in body'
        logging.warn(msg)
        return func.HttpResponse(msg, status_code=400)
    email_address = req.form.get('email')

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email_address):
        msg = 'Email address is not valid'
        logging.warn(msg)
        return func.HttpResponse(msg, status_code=422)

    lang = ''
    if 'language' in req_keys:
        lang = req.form.get('language')

    try:        
        table_service = TableService(connection_string=connect_str)
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        for input_file in req.files.values():
            extension = input_file.filename.split('.')[1]
            file_uuid = str(uuid.uuid4())
            filename = file_uuid + "." + extension
            logging.info('Adding file to blob storage...')

            blob_client = blob_service_client.get_blob_client(container=container,blob=filename)
            blob_client.upload_blob(input_file)
            task = {'PartitionKey': extension, 'RowKey': file_uuid, 'email': email_address, 'language': lang, 'translation': '', 'image_text': '', 'data_analysis': ''}
            table_service.insert_entity('Tasks', task)
            logging.info('File added for processing')

        return func.HttpResponse('File added for processing', status_code=201)
    except Exception:
        msg = 'Error has occured'
        logging.warn(msg)
        return func.HttpResponse(msg, status_code=400)
