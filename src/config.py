from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
from confluent_kafka.serialization import StringSerializer, StringDeserializer

BOOTSTRAP_SERVERS = "localhost:9092"
SCHEMA_REGISTRY_URL = "http://localhost:8081"
TOPIC = "orders"
GROUP_ID = "order-consumer-group"

value_schema_str = """{
  "type": "record",
  "name": "OrderEvent",
  "namespace": "io.company.events",
  "fields": [
    {"name": "order_id", "type": "string"},
    {"name": "user", "type": "string"},
    {"name": "item", "type": "string"},
    {"name": "quantity", "type": "int"},
    {"name": "status", "type": "string"}
  ]
}"""

schema_registry_conf = {"url": SCHEMA_REGISTRY_URL}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

def get_value_serializer():
    return AvroSerializer(schema_registry_client=schema_registry_client, schema_str=value_schema_str)

def get_key_serializer():
    return StringSerializer("utf_8")

def get_value_deserializer():
    return AvroDeserializer(schema_registry_client=schema_registry_client)

def get_key_deserializer():
    return StringDeserializer("utf_8")