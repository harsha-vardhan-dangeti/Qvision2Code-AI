from rich.pretty import pprint

from qgenie import QGenieClient

from dotenv import load_dotenv

import os

load_dotenv()

qgenie_api_key = os.getenv("QGENIE_API_KEY")

print("QGENIE_API_KEY:", qgenie_api_key)

client = QGenieClient(endpoint="https://qgenie-chat.qualcomm.com", api_key=qgenie_api_key)

models_response = client.get_available_models()

pprint(models_response, expand_all=True)

#print(models_response[0].name)