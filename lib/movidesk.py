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


def responses(after: str = ''):
    url = f"{URL}/survey/responses?token={TOKEN}&startingAfter={after}"
    response = requests.request("GET", url)
    return response.text
