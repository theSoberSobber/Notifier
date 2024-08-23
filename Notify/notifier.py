import time
import os
from config import NTFY_RATE_LIMIT, NOTIFY_NO_NEW_PROBLEMS, MAX_NOTIFICATIONS, CHANNEL_NAME

class NotifierService:
    def __init__(self):
        pass

    def notify(self, handle, submission_info, profile_url):
        if submission_info["rollback"]:
            self.notify_rollback(handle)
        else:
            self.notify_submissions(handle, submission_info["submissions"], profile_url)

    def notify_rollback(self, handle):
        title = f"Rollback detected for {handle}"
        message = "Submissions have decreased. Rollback in progress."
        cmd = f'ntfy publish --title "{title}" --priority high --tags "warning" --message "{message}" {CHANNEL_NAME}'
        os.system(cmd)
        time.sleep(NTFY_RATE_LIMIT)

    def notify_submissions(self, handle, submissions, profile_url):
        if len(submissions) == 0:
            if NOTIFY_NO_NEW_PROBLEMS:
                self.notify_no_new_problems(handle, profile_url)
        else:
            for submission in submissions[:MAX_NOTIFICATIONS]:
                problem_name = submission["problem"]["name"]
                problem_url = f"https://codeforces.com/contest/{submission['problem'].get('contestId') or submission['problem'].get('problemsetName')}/problem/{submission['problem']['index']}"
                submission_url = f"https://codeforces.com/contest/{submission['problem'].get('contestId') or submission['problem'].get('problemsetName')}/submission/{submission['id']}"
                self.send_notification(handle, problem_name, problem_url, submission_url)

            if len(submissions) >= MAX_NOTIFICATIONS:
                self.notify_too_many_problems(handle, profile_url)
                
    def send_403_notification(self, url, timestamp):
        title = "Codeforces API 403 Error"
        message = f"403 error occurred at {timestamp}. URL: {url}"
        cmd = f'ntfy publish --title "{title}" --priority max --tags "error" --message "{message}" --click="{url}" {CHANNEL_NAME}'
        os.system(cmd)
        time.sleep(NTFY_RATE_LIMIT)

    def send_notification(self, handle, problem_name, problem_url, submission_url):
        title = f"New Submission by {handle}"
        message = f"Problem: {problem_name}"
        cmd = f'ntfy publish --title "{title}" --priority high --tags "work,important" --message "{message}"'
        cmd += f' --click="{problem_url}" --actions "view, Open Problem, {problem_url}; view, Open Submission, {submission_url}"'
        cmd += f" {CHANNEL_NAME}"
        os.system(cmd)
        time.sleep(NTFY_RATE_LIMIT)

    def notify_no_new_problems(self, handle, profile_url):
        title = f"No New Submissions by {handle}"
        message = "No new problems attempted."
        cmd = f'ntfy publish --title "{title}" --tags "info" --message "{message}"'
        cmd += f' --click="{profile_url}"'
        cmd += f" {CHANNEL_NAME}"
        os.system(cmd)
        time.sleep(NTFY_RATE_LIMIT)

    def notify_too_many_problems(self, handle, profile_url):
        title = f"Too Many Problems for {handle}"
        message = f"{handle} has too many new problems. Please check their profile."
        cmd = f'ntfy publish --title "{title}" --priority high --tags "important" --message "{message}"'
        cmd += f' --click="{profile_url}"'
        cmd += f" {CHANNEL_NAME}"
        os.system(cmd)
        time.sleep(NTFY_RATE_LIMIT)