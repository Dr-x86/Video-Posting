import requests
import os
from dotenv import load_dotenv

load_dotenv()
CHAT_ID=os.getenv("PERSONAL_CHAT_ID")
TOKEN=os.getenv("BOT_TOKEN")

def Me(msg):
    URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"    
    parametros = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    respuesta = requests.post(URL, data=parametros)