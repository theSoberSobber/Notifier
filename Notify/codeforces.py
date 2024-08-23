import requests
import time
import os
from datetime import datetime
from config import CF_RATE_LIMIT, CHANNEL_NAME

class Codeforces:
    def __init__(self, handle, data_dir):
        self.handle = handle
        self.data_dir = data_dir
        self.submissions = self.fetch_submissions()

    def fetch_submissions(self):
        url = f"https://codeforces.com/api/user.status?handle={self.handle}"
        try:
            response = requests.get(url)
            time.sleep(CF_RATE_LIMIT)
            if response.status_code == 403:
                self.handle_403_error(url)
            elif response.status_code == 200:
                return response.json().get('result', [])
        except requests.RequestException as e:
            self.log_failure(f"RequestException: {e}", url)
        return []

    def handle_403_error(self, url):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Codeforces API returned 403 for {url} at {timestamp}"
        self.log_failure(message, url)
        self.send_403_notification(url, timestamp)
        exit(1)

    # need to mangle concerns here because of the nature of exit
    def send_403_notification(self, url, timestamp):
        title = "Codeforces API 403 Error"
        message = f"403 error occurred at {timestamp}. URL: {url}"
        cmd = f'ntfy publish --title "{title}" --priority max --tags "error" --message "{message}" --click="{url}" {CHANNEL_NAME}'
        os.system(cmd)

    def log_failure(self, message, url):
        log_file = os.path.join(self.data_dir, 'failures.log')
        with open(log_file, 'a') as file:
            file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message} - {url}\n")

    def get_submission_file_path(self):
        return os.path.join(self.data_dir, f"number-{self.handle}.txt")

    def read_previous_submission_count(self):
        file_path = self.get_submission_file_path()
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return int(file.read().strip())
        return 0

    def update_submission_count(self, new_count):
        file_path = self.get_submission_file_path()
        with open(file_path, 'w') as file:
            file.write(str(new_count))

    def process_submissions(self):
        previous_count = self.read_previous_submission_count()
        current_count = len(self.submissions)

        to_return = {"rollback": False, "submissions": []}

        if current_count < previous_count:
            print(f"Rollback detected for {self.handle}. Exiting...")
            to_return["rollback"] = True
            return to_return

        seen_problems = set()

        for i in range(current_count-previous_count):
            submission = self.submissions[i]
            problem_id = submission['problem']['contestId'], submission['problem']['index']
            if problem_id in seen_problems:
                continue
            to_return["submissions"].append(submission)
            seen_problems.add(problem_id)

        to_return["submissions"].reverse()

        self.update_submission_count(current_count)
        return to_return