from src.data.inventory import InventoryStore


def test_inventory_deduct(tmp_path):
    csv_file = tmp_path / "inv.csv"
    csv_file.write_text("item,quantity\npen,5\nbook,2\n")
    store = InventoryStore(path=str(csv_file))
    assert store.has_stock("pen", 5)
    assert store.deduct("pen", 2) is True
    assert store.has_stock("pen", 3)
    assert store.deduct("book", 2)
    assert not store.has_stock("book", 1)
