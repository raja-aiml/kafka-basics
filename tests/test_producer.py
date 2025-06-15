from src import prodcuer


class FakeProducer:
    def __init__(self):
        self.sent = []
        self.flushed = False

    def produce(self, topic, key, value, on_delivery):
        self.sent.append((topic, key, value))
        on_delivery(
            None,
            type(
                "msg",
                (),
                {
                    "key": lambda: key,
                    "topic": lambda: topic,
                    "partition": lambda: 0,
                    "offset": lambda: 0,
                },
            ),
        )

    def poll(self, timeout):
        pass

    def flush(self):
        self.flushed = True


def test_sample_orders():
    orders = prodcuer.sample_orders()
    assert len(orders) == 3


def test_produce_orders(monkeypatch):
    producer = FakeProducer()
    monkeypatch.setattr(prodcuer, "SerializingProducer", lambda *_: producer)
    prodcuer.produce_orders(1, 0)
    assert producer.sent
    assert producer.flushed
