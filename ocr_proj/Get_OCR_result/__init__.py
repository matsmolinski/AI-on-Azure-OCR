import logging
import azure.functions as func
import os
from azure.cosmosdb.table.tableservice import TableService


def main(req: func.HttpRequest) -> func.HttpResponse:
    connect_str=os.environ["AzureWebJobsStorage"]

    # request validation
    req_keys = req.form.keys()
    token_field_name = "token"
    if token_field_name not in req_keys:
        msg = f'Missing "{token_field_name}" in body'
        logging.warn(msg)
        return func.HttpResponse(msg, status_code=400)
    token = req.form.get(token_field_name)

    # retrive OCR result
    try:        
        table_service = TableService(connection_string=connect_str)
        ocr_results = table_service.query_entities('Tasks', filter=f"RowKey eq '{token}'")
        
        if (len(ocr_results.items) == 0) or (len(ocr_results.items) > 1):
            msg = 'Incorrect token'
            logging.warn(msg)
            return func.HttpResponse(msg, status_code=400) 

        ocr_result = ocr_results.items[0]
        return func.HttpResponse(str(ocr_result), status_code=200)

    except Exception as e:
        msg = 'Error has occured'
        logging.warn(msg)
        logging.error(str(e))
        return func.HttpResponse(msg, status_code=500)
