import csv
from datetime import datetime

class Logger:
    def __init__(self):
        self.log_file = open('activity_log.csv', 'a')
        self.writer = csv.writer(self.log_file)

    def log_action(self, action_type, details):
        timestamp = datetime.now().isoformat()
        self.writer.writerow([timestamp, action_type, str(details)])
