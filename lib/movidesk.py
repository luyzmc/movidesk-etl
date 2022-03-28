import requests
import os
from dotenv import load_dotenv
load_dotenv()

URL = os.getenv('MOVIDESK_URL')
TOKEN = os.getenv('MOVIDESK_TOKEN')


def questions():
    url = f"{URL}/survey/questions?token={TOKEN}"
    response = requests.request("GET", url)
    return response.text


def responses(after: str = '', after_date: str = ''):
    url = f"{URL}/survey/responses?token={TOKEN}&startingAfter={after}&responseDateGreaterThan={after_date}"
    response = requests.request("GET", url)
    return response.text


def status_histories(skip: str = 0):
    url = f"{URL}/survey/tickets?token={TOKEN}&$select=id&$skip={skip}&$expand=statusHistories&$filter=createdDate gt 2022-01-01T00:00:00.00z"
    response = requests.request("GET", url)
    return response.text