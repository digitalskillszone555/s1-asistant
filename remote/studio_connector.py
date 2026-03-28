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
        response = requests.post(url, json=payload, timeout=5)

        if response.status_code == 200:
            print("S1 Assistant connected to Studio")
        else:
            print(f"Studio connection failed (Status: {response.status_code})")

    except requests.exceptions.Timeout:
        print("Studio connection timed out. Continuing in offline mode.")
    except requests.exceptions.RequestException as e:
        print(f"Studio connection error: {e}. Continuing in offline mode.")
    except Exception as e:
        print(f"Unexpected connection error: {e}")