import csv

class InventoryStore:
    def __init__(self, path="storage/inventory.csv"):
        self.path = path
        self._load()

    def _load(self):
        self.items = {}
        with open(self.path) as f:
            for row in csv.DictReader(f):
                self.items[row["item"]] = int(row["quantity"])

    def has_stock(self, item, qty):
        return self.items.get(item, 0) >= qty

    def deduct(self, item, qty):
        if self.has_stock(item, qty):
            self.items[item] -= qty
            self._save()
            return True
        return False

    def _save(self):
        with open(self.path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["item", "quantity"])
            writer.writeheader()
            for item, quantity in self.items.items():
                writer.writerow({"item": item, "quantity": quantity})