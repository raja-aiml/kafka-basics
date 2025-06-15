from src import replay


def test_load_orders_filter(tmp_path):
    path = tmp_path / "orders.jsonl"
    path.write_text('{"order_id":"1","user":"alice","item":"pen","status":"placed"}\n')
    replay.OUTPUT_FILE = str(path)
    orders = list(replay.load_orders(user="alice"))
    assert len(orders) == 1
    assert orders[0]["order_id"] == "1"


class FakeProducer:
    def __init__(self):
        self.sent = []
        self.flush_called = False

    def produce(self, topic, key, value, on_delivery):
        self.sent.append((topic, key, value))
        on_delivery(None, type("msg", (), {"key": lambda: key, "offset": lambda: 0}))

    def poll(self, timeout):
        pass

    def flush(self):
        self.flush_called = True


def test_replay_orders(tmp_path, monkeypatch):
    path = tmp_path / "orders.jsonl"
    path.write_text('{"order_id":"1","user":"alice","item":"pen","status":"placed"}\n')
    replay.OUTPUT_FILE = str(path)

    producer = FakeProducer()
    monkeypatch.setattr(replay, "SerializingProducer", lambda *_: producer)

    replay.replay_orders(0, user="alice", item=None, status=None)
    assert producer.sent[0][1] == "1"
    assert producer.flush_called
