import logging
import os
import time
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import azure.functions as func
from datetime import datetime, timedelta
from azure.storage.blob import ResourceTypes, AccountSasPermissions, generate_account_sas
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity


def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes\n"
                 f"Path to: {myblob.uri}\n")
    vision_key = os.environ["CognitiveServicesVisionKey"]
    vision_endpoint = os.environ["CognitiveServicesVisionEndpoint"]
    connect_str = os.environ["AzureWebJobsStorage"]
    container = os.environ["ContainerName"]
    rowkey = myblob.name.split('.')[0].split('/')[1]
    partkey = myblob.name.split('.')[1]
    #try:        
    table_service = TableService(connection_string=connect_str)
    logging.info(f"row: {rowkey}\n"
                f"part: {partkey}\n")
    task = table_service.get_entity('Tasks', partkey, rowkey)
    del task['etag']
    logging.info(task)


    #cognitive stuff here
    computervision_client = ComputerVisionClient(vision_endpoint, CognitiveServicesCredentials(vision_key))
    read_results = computervision_client.read(myblob.uri,  raw=True)

    operation_location_remote = read_results.headers["Operation-Location"]
    operation_id = operation_location_remote.split("/")[-1]

    while True:
        get_read_results = computervision_client.get_read_result(operation_id)
        if get_read_results.status not in ['notStarted', 'running']:
            break
        time.sleep(1)
    text = ""
    if get_read_results.status == OperationStatusCodes.succeeded:
        for text_result in get_read_results.analyze_result.read_results:
            for line in text_result.lines:
                text = text + line.text + '\n'
    #endof cognitive stuff


    task['translation'] = 'abc'
    task['image_text'] = text
    task['data_analysis'] = 'ghi'
    table_service.update_entity('Tasks', task)
    logging.info('Table storage updated')

    #except Exception:
    #    msg = 'Error has occured'
     #   logging.warn(msg)

    # GENERACJA DOSTĘPU
    #----------------------------------------------------------------------------------------------------
    '''
    sas_token = generate_account_sas(
        blob_service_client.account_name,
        account_key=blob_service_client.credential.account_key,
        resource_types=ResourceTypes(object=True),
        permission=AccountSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    
    # ZAPYTANIE
    #----------------------------------------------------------------------------------------------------

    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

    # Call API with URL and raw response (allows you to get the operation location)
    recognize_handw_results = computervision_client.read(myblob)

    # POBRANIE ODPOWIEDZI
    #----------------------------------------------------------------------------------------------------

    # Get the operation location (URL with an ID at the end) from the response
    operation_location_remote = recognize_handw_results.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = operation_location_remote.split("/")[-1]

    # Call the "GET" API and wait for it to retrieve the results 
    while True:
        get_handw_text_results = computervision_client.get_read_result(operation_id)
        if get_handw_text_results.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # Print the detected text, line by line
    if get_handw_text_results.status == OperationStatusCodes.succeeded:
        for text_result in get_handw_text_results.analyze_result.read_results:
            for line in text_result.lines:
                print(line.text)
                print(line.bounding_box)
    print()
    '''


