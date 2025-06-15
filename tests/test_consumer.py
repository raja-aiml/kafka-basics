from src import consumer


class FakeProcessor:
    def __init__(self, result=True):
        self.result = result
        self.processed = []

    def process(self, order):
        self.processed.append(order)
        return self.result


class FakeMsg:
    def __init__(self, value):
        self._value = value

    def value(self):
        return self._value

    def error(self):
        return None


def test_handle_message_persist(tmp_path):
    msg = FakeMsg({"user": "alice", "item": "pen", "quantity": 1})
    proc = FakeProcessor()
    stats = {"total": 0, "processed": 0, "skipped": 0}
    path = tmp_path / "out.jsonl"
    consumer.handle_message(msg, proc, False, str(path), None, stats)
    assert stats["processed"] == 1
    assert path.read_text().strip() != ""


def test_handle_message_filter(tmp_path):
    msg = FakeMsg({"user": "bob", "item": "pen", "quantity": 1})
    proc = FakeProcessor()
    stats = {"total": 0, "processed": 0, "skipped": 0}
    path = tmp_path / "out.jsonl"
    consumer.handle_message(msg, proc, False, str(path), "alice", stats)
    assert stats["skipped"] == 1
    assert not path.exists()
