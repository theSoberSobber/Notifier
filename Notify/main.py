import os
import requests
from codeforces import Codeforces
from notifier import NotifierService
from config import CHANNEL_NAME, HEALTHCHECK_FUNCTION_URL

def ensure_data_directory():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def read_handles(file_name='input.csv'):
    with open(file_name, 'r') as file:
        handles = [line.strip() for line in file.readlines()]
    return handles

def notify_healthcheck_failure(message):
    healthcheck_channel = f"{CHANNEL_NAME}_healthcheck"
    url = f'https://ntfy.sh/{healthcheck_channel}'
    headers = {
        'Title': 'Ntfy Server Health Check Failed'
    }
    payload = message
    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            print("Notification sent successfully.")
        else:
            print(f"Failed to send notification: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"Error sending notification: {e}")

def check_ntfy_health():
    url = HEALTHCHECK_FUNCTION_URL
    try:
        response = requests.get(url, timeout=6)
        if response.status_code == 200 and response.json().get('status') == 200:
            print("Ntfy server is healthy. Proceeding with the script.")
            return True
        else:
            message = f"Health check failed: {response.json().get('message')}"
            print(message)
            notify_healthcheck_failure(message)
            return False
    except requests.RequestException as e:
        message = f"Health check request failed: {str(e)}"
        print(message)
        notify_healthcheck_failure(message)
        return False

def main():
    if not check_ntfy_health():
        print("Ntfy server is not healthy. Exiting the script.")
        return
    
    data_dir = ensure_data_directory()
    handles = read_handles()
    notifier_service = NotifierService()
    for handle in handles:
        cf = Codeforces(handle, data_dir)
        result = cf.process_submissions()
        profile_url = f"https://codeforces.com/profile/{handle}"
        notifier_service.notify(handle, result, profile_url)

if __name__ == "__main__":
    main()