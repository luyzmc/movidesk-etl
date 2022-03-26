import requests
import os

URL = os.getenv('MOVIDESK_URL')
TOKEN = os.getenv('MOVIDESK_TOKEN')


def questions():
    url = f"{URL}/survey/questions?token={TOKEN}"
    response = requests.request("GET", url)
    return response.text


def responses(after:str = None):
    url = f"{URL}/survey/questions?token={TOKEN}&startingAfter={after}"
    response = requests.request("GET", url)
    return response.text