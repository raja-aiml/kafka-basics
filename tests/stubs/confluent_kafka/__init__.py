"""
Stub implementation of confluent_kafka for local testing when the real library is unavailable.
This module provides minimal class definitions used by the application code.
"""


class DeserializingConsumer:
    def __init__(self, conf):
        pass

    def subscribe(self, topics):
        pass

    def poll(self, timeout):
        return None

    def close(self):
        pass


class SerializingProducer:
    def __init__(self, conf):
        pass

    def produce(self, topic, key, value, on_delivery=None):
        pass

    def poll(self, timeout):
        pass

    def flush(self):
        pass


class TopicPartition:
    def __init__(self, topic, partition, offset=None):
        self.topic = topic
        self.partition = partition
        self.offset = offset


class Consumer:
    def __init__(self, conf):
        pass

    def get_watermark_offsets(self, tp, timeout):
        return (0, 0)

    def commit(self, offsets, asynchronous=False):
        pass

    def close(self):
        pass
