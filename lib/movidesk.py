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


def status_histories(skip: int = 0, after_date: str = ''):
    filter = "&$filter=lastUpdate gt {after_date}z" if after_date != '' else ''
    url = f"{URL}/tickets?token={TOKEN}&$select=id,lastUpdate&$skip={skip}&$expand=statusHistories{filter}"
    response = requests.request("GET", url)
    return response.text


def tickets_aguardando_eq_interna(skip: int = 0):
    filter = f"&$filter=status eq 'Aguardando Equipe interna' and serviceSecondLevel eq 'Suporte ZG'"
    expand = f"&$expand=childrenTickets,customFieldValues($filter=customFieldId eq 55366)"
    url = f"{URL}/tickets?token={TOKEN}&$select=id,justification&$skip={skip}{expand}{filter}"
    response = requests.request("GET", url)
    return response.text

