"""
Stub of confluent_kafka.serialization module for testing.
"""


class StringSerializer:
    def __init__(self, encoding: str = "utf_8", **kwargs):
        self.encoding = encoding

    def __call__(self, value, ctx=None):
        return value


class StringDeserializer:
    def __init__(self, encoding: str = "utf_8", **kwargs):
        self.encoding = encoding

    def __call__(self, value, ctx=None):
        return value
