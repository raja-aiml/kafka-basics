from data.inventory import InventoryStore
from data.users import UserStore
import logging

class KafkaOrderProcessor:
    def __init__(self):
        self.inventory = InventoryStore()
        self.users = UserStore()

    def is_valid_order(self, order):
        if not self.users.is_paid_user(order["user"]):
            logging.warning(f"❌ User {order['user']} not paid.")
            return False
        if not self.inventory.has_stock(order["item"], order["quantity"]):
            logging.warning(f"❌ Not enough stock for {order['item']}.")
            return False
        return True

    def process(self, order):
        if self.is_valid_order(order):
            self.inventory.deduct(order["item"], order["quantity"])
            return True
        return False