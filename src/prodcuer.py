import argparse
import uuid
import logging
import time
from confluent_kafka import SerializingProducer
import config

# ─────────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(description="Kafka Order Producer")
    parser.add_argument("--count", type=int, default=3, help="Number of orders to send")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay (seconds) between orders")
    return parser.parse_args()

def create_producer():
    return SerializingProducer({
        'bootstrap.servers': config.BOOTSTRAP_SERVERS,
        'key.serializer': config.get_key_serializer(),
        'value.serializer': config.get_value_serializer(),
    })

def sample_orders():
    return [
        {"user": "alice", "item": "book", "quantity": 1},
        {"user": "bob", "item": "pen", "quantity": 3},
        {"user": "carol", "item": "notebook", "quantity": 2}
    ]

def delivery_report(err, msg):
    if err is not None:
        logging.error(f"❌ Delivery failed for record {msg.key()}: {err}")
    else:
        logging.info(f"✅ Delivered {msg.key()} → {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")

def produce_orders(count: int, delay: float):
    producer = create_producer()
    orders = sample_orders()

    for i in range(count):
        order = orders[i % len(orders)]
        order_id = str(uuid.uuid4())

        payload = {
            "order_id": order_id,
            "user": order["user"],
            "item": order["item"],
            "quantity": order["quantity"],
            "status": "placed"
        }

        logging.info(f"📦 Producing: {payload}")

        producer.produce(
            topic=config.TOPIC,
            key=order_id,
            value=payload,
            on_delivery=delivery_report
        )

        producer.poll(0)
        time.sleep(delay)

    producer.flush()

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    args = parse_args()
    produce_orders(args.count, args.delay)

if __name__ == "__main__":
    main()