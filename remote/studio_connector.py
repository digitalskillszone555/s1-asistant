import requests
from config.studio_config import STUDIO_API_URL, ASSISTANT_ID, ASSISTANT_VERSION

def register_assistant():

    url = f"{STUDIO_API_URL}/assistant/register"

    payload = {
        "assistant_id": ASSISTANT_ID,
        "version": ASSISTANT_VERSION,
        "status": "online"
    }

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            print("S1 Assistant connected to Studio")
        else:
            print("Studio connection failed")

    except Exception as e:
        print("Connection error:", e)