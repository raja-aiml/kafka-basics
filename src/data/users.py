import csv


class UserStore:
    def __init__(self, path="storage/users.csv"):
        self.path = path
        self._load()

    def _load(self):
        self.users = {}
        with open(self.path) as f:
            for row in csv.DictReader(f):
                self.users[row["user"]] = row["status"].lower() == "paid"

    def is_paid_user(self, username):
        return self.users.get(username, False)
