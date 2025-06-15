from src.kafka_utils import offset_reset


class FakePartition:
    def __init__(self, pid):
        self.id = pid


class FakeAdmin:
    def list_topics(self, topic=None, timeout=10):
        return type(
            "meta",
            (),
            {"topics": {topic: type("t", (), {"partitions": {0: FakePartition(0)}})}},
        )


class FakeConsumer:
    def __init__(self):
        self.committed = []

    def get_watermark_offsets(self, tp, timeout=10):
        return (0, 5)

    def commit(self, offsets, asynchronous=False):
        self.committed.extend(offsets)

    def close(self):
        pass


def test_list_partitions():
    admin = FakeAdmin()
    parts = offset_reset.list_partitions(admin, "orders")
    assert parts[0].partition == 0


def test_reset_offsets(monkeypatch):
    monkeypatch.setattr(offset_reset, "AdminClient", lambda conf: FakeAdmin())
    monkeypatch.setattr(offset_reset, "Consumer", lambda conf: FakeConsumer())
    offset_reset.reset_offsets("g", "orders", "localhost:9092", reset_to="latest")
