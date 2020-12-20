import logging

import azure.functions as func
import os


def main(req: func.HttpRequest, outputblob: func.Out[func.InputStream]) -> func.HttpResponse:
    path_to_file = "kot.jpeg"
    photo = open(path_to_file, "rb")
    outputblob.set(photo.read())
    return func.HttpResponse(f"OK")
