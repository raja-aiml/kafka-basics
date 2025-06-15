from src.tool import inventory as inv_tool
from src.tool import user as user_tool


def test_inventory_cli(monkeypatch, tmp_path, capsys):
    path = tmp_path / "inv.csv"
    monkeypatch.setattr(inv_tool, "FILE", str(path))
    inv_tool.add_item("pen", 3)
    inv_tool.update_item("pen", 5)
    inv_tool.show_inventory()
    captured = capsys.readouterr()
    assert "pen" in captured.out
    assert "5" in captured.out


def test_user_cli(monkeypatch, tmp_path, capsys):
    path = tmp_path / "users.csv"
    monkeypatch.setattr(user_tool, "FILE", str(path))
    user_tool.add_user("alice", "paid")
    user_tool.update_user("alice", "unpaid")
    user_tool.show_users()
    captured = capsys.readouterr()
    assert "alice" in captured.out
    assert "unpaid" in captured.out
