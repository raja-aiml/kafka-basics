"""
Stub of confluent_kafka.schema_registry.avro module for testing.
"""


class AvroSerializer:
    def __init__(self, schema_registry_client=None, schema_str=None, **kwargs):
        pass

    def __call__(self, value, ctx=None):
        return value


class AvroDeserializer:
    def __init__(self, schema_registry_client=None, **kwargs):
        pass

    def __call__(self, value, ctx=None):
        return value
