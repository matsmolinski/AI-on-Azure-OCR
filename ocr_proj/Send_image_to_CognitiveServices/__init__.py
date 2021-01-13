import os, requests, uuid, json, time, logging
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
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
    # vision_key = os.environ["CognitiveServicesVisionKey"]
    # vision_endpoint = os.environ["CognitiveServicesVisionEndpoint"]
    # sentiment_key = os.environ["CognitiveServicesSentimentKey"]
    # sentiment_enpoint = os.environ["CognitiveServicesSentimentEndpoint"]
    # translation_key = os.environ["CognitiveServicesTranslationKey"]
    # translation_endpoint = os.environ["CognitiveServicesTranslationEndpoint"]
    # translation_loc = "westeurope"
    # connect_str = os.environ["AzureWebJobsStorage"]
    vision_key = "fc0bd2284030410cad911605f2b8bc16"
    vision_endpoint = "https://pogodpol-analycs.cognitiveservices.azure.com/"
    sentiment_key = "f02788a53b2347c389ebf7861d1cad9b"
    sentiment_enpoint = "https://pogodpol-analycs.cognitiveservices.azure.com/"
    translation_key = "9a5e58d5e7e946f88a82ccc973fb8591"
    translation_endpoint = "https://api.cognitive.microsofttranslator.com/"
    translation_loc = "westeurope"
    connect_str = os.environ["AzureWebJobsStorage"]
    

    rowkey = myblob.name.split('.')[0].split('/')[1]
    partkey = myblob.name.split('.')[1]

    #try:        
    table_service = TableService(connection_string=connect_str)
    logging.info(f"row: {rowkey}\n"
                f"part: {partkey}\n")
    task = table_service.get_entity('Tasks', partkey, rowkey)
    del task['etag']
    logging.info(task)
    language = task.language

    #vision stuff here
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
            print(get_read_results.analyze_result.read_results)
            for line in text_result.lines:
                text = text + line.text + '\n'
    text = text.replace("\n", " ")
    #endof vision stuff

    #sentiment stuff here
    textdoc = [text]
    text_sentiment = ""
    sen_credential = AzureKeyCredential(sentiment_key)
    text_analytics_client = TextAnalyticsClient(endpoint=sentiment_enpoint, credential=sen_credential)
    response = text_analytics_client.analyze_sentiment(documents = textdoc)[0]
    text_sentiment = text_sentiment + "Document Sentiment: {}".format(response.sentiment)
    text_sentiment = text_sentiment +"Overall scores: positive={0:.2f}; neutral={1:.2f}; negative={2:.2f} \n".format(
        response.confidence_scores.positive,
        response.confidence_scores.neutral,
        response.confidence_scores.negative,
    )
    for idx, sentence in enumerate(response.sentences):
        text_sentiment = text_sentiment +"Sentence: {}".format(sentence.text)
        text_sentiment = text_sentiment +"Sentence {} sentiment: {}".format(idx+1, sentence.sentiment)
        text_sentiment = text_sentiment +"Sentence score:\nPositive={0:.2f}\nNeutral={1:.2f}\nNegative={2:.2f}\n".format(
                sentence.confidence_scores.positive,
                sentence.confidence_scores.neutral,
                sentence.confidence_scores.negative,
            )
    #endof sentiment stuff


    #translation stuff
    if language is None or len(language)<2:
        translation = ''
    else:
        path = '/translate?api-version=3.0'
        params = '&to={}'.format(language)
        constructed_url = translation_endpoint + path + params
        headers = {
            'Ocp-Apim-Subscription-Key': translation_key,
            'Ocp-Apim-Subscription-Region': translation_loc,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        body = [{
            'text' : text
        }]
        request = requests.post(constructed_url, headers=headers, json=body)
        response = request.json()
        print(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        response = json.dumps(response)
        response = response.split("text")
        response = response[1]
        size = len(response)
        response = response[4:size-5]
        response = response.split(", \"to\":")
        size = len(response)
        translate_lang=response[size-1]
        response.pop()
        translate_text = ""
        for elem in response:
            translate_text = translate_text + elem
        translate_lang = translate_lang.replace("\"","")
        translate_lang = translate_lang.strip()
        translation = "Language: {}, Text: {}".format(translate_lang, translate_text)


    #endof translation


    task['translation'] = translation
    task['image_text'] = text
    task['data_analysis'] = text_sentiment
    table_service.update_entity('Tasks', task)
    logging.info('Table storage updated')
    print(task)

    # url = os.environ["EmailURL"]
    url = "https://prod-145.westeurope.logic.azure.com:443/workflows/ebdbfc4977234440b9a48a98a9fa36af/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=1wlap-WyQ-Qi9WYsFRliBWAdXCSPg9aljr7LupDnHsI"
    content = {
        'email': task.email,
        'code': rowkey
    }
    x = requests.post(url, json=content)
    #except Exception:
    #    msg = 'Error has occured'
    #   logging.warn(msg)

   


