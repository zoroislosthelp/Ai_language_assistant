# import requests
# import os

# def translate(text, to_lang, from_lang="en"):
#     url = f"https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&from={from_lang}&to={to_lang}"
#     headers = {
#         'Ocp-Apim-Subscription-Key': os.getenv("AZURE_TRANSLATOR_KEY"),
#         'Ocp-Apim-Subscription-Region': os.getenv("AZURE_TRANSLATOR_REGION"),
#         'Content-type': 'application/json'
#     }
#     response = requests.post(url, headers=headers, json=[{"text": text}])
#     return response.json()[0]["translations"][0]["text"]

import requests
import os

def translate(text, to_lang, from_lang=None):
    url = f"https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"
    if from_lang:
        url += f"&from={from_lang}"
    url += f"&to={to_lang}"

    headers = {
        'Ocp-Apim-Subscription-Key': os.getenv("AZURE_TRANSLATOR_KEY"),
        'Ocp-Apim-Subscription-Region': os.getenv("AZURE_TRANSLATOR_REGION"),
        'Content-type': 'application/json'
    }
    body = [{"text": text}]
    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception(f"Azure Translator API error: {response.status_code} {response.text}")
    return response.json()[0]["translations"][0]["text"]
