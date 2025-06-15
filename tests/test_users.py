from src.data.users import UserStore


def test_user_store(tmp_path):
    csv_file = tmp_path / "users.csv"
    csv_file.write_text("user,status\nalice,paid\nbob,unpaid\n")
    store = UserStore(path=str(csv_file))
    assert store.is_paid_user("alice")
    assert not store.is_paid_user("bob")
    assert not store.is_paid_user("carol")
