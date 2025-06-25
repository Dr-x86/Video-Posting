import requests
import os
from dotenv import load_dotenv

load_dotenv()
CHAT_ID=os.getenv("PERSONAL_CHAT_ID")
TOKEN=os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')

def Me(msg):
    URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"    
    parametros = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    respuesta = requests.post(URL, data=parametros)


def Channel(IMAGE_URL,CAPTION = ''):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    payload = {
        "chat_id": "@WaiFUNotSF",  # Usa '@nombre_del_canal' o 
        "photo": IMAGE_URL,
        "caption": CAPTION
    }
    response = requests.post(url, data=payload)
    return response