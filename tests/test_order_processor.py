from src.service.order_processor import KafkaOrderProcessor
from src.data.inventory import InventoryStore
from src.data.users import UserStore


def test_order_processor_process(monkeypatch, tmp_path):
    inv_file = tmp_path / "inventory.csv"
    inv_file.write_text("item,quantity\npen,5\n")
    users_file = tmp_path / "users.csv"
    users_file.write_text("user,status\nalice,paid\n")

    def init_stub(self):
        self.inventory = InventoryStore(path=str(inv_file))
        self.users = UserStore(path=str(users_file))

    monkeypatch.setattr(KafkaOrderProcessor, "__init__", init_stub)

    processor = KafkaOrderProcessor()
    order = {"user": "alice", "item": "pen", "quantity": 3}
    assert processor.process(order)
    assert processor.inventory.items["pen"] == 2
