import os
from codeforces import Codeforces
from notifier import NotifierService

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

def main():
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